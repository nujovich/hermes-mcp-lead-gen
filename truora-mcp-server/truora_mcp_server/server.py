"""Truora MCP Server — 3 tools for background checks & identity verification.

Tools:
  truora_background_check  — Create a background check and poll for results
  truora_get_check         — Get detailed results of a specific check
  truora_list_checks       — List background checks with optional filters
"""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import TruoraClient, TruoraError

logger = logging.getLogger("truora-mcp")
server = FastMCP(
    name="Truora MCP",
    instructions=(
        "Truora MCP Server — background checks & identity verification "
        "for LATAM (Colombia, Mexico, Chile, Brazil, Peru, Costa Rica)."
    ),
)

# Lazy client so TRUORA_API_KEY is read from env on first use
_client: TruoraClient | None = None


def get_client() -> TruoraClient:
    global _client
    if _client is None:
        _client = TruoraClient()
    return _client


# ── Tool 1: Background Check ────────────────────────────────────────


@server.tool(
    description=(
        "Create a background check on a person, vehicle, or company in LATAM "
        "(Colombia, Mexico, Chile, Brazil, Peru, Costa Rica). "
        "Returns the final score (0-1), severity level, and detailed dataset breakdown. "
        "Automatically polls until the check completes."
    ),
)
async def truora_background_check(
    country: str,
    check_type: str,
    national_id: str | None = None,
    tax_id: str | None = None,
    license_plate: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: str | None = None,
    phone_number: str | None = None,
) -> str:
    """Create a background check on a person/vehicle/company.

    Args:
        country: ISO country code (CO, MX, CL, BR, PE, CR, ALL)
        check_type: 'person', 'vehicle', 'company', or a custom type name
        national_id: National ID (required for person/vehicle checks)
        tax_id: Tax ID / RFC (required for company checks, e.g. RFC in MX)
        license_plate: License plate number (for vehicle checks)
        first_name: First name (helps disambiguate homonyms)
        last_name: Last name (helps disambiguate homonyms)
        date_of_birth: Date of birth in YYYY-MM-DD format
        phone_number: Phone number (required by law in some countries)

    Returns:
        Formatted check result with score and severity.
    """
    try:
        client = get_client()
        result = client.create_check_and_wait(
            country=country,
            check_type=check_type,
            national_id=national_id,
            tax_id=tax_id,
            license_plate=license_plate,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number,
        )
        return _format_check_result(result)
    except TruoraError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        logger.exception("Unexpected error in truora_background_check")
        return f"❌ Unexpected error: {e}"


# ── Tool 2: Get Check Result ────────────────────────────────────────


@server.tool(
    description=(
        "Get the full detailed result of a previously created background check "
        "by its check ID. Includes the score, dataset-by-dataset breakdown, "
        "severity level, and individual findings per database queried."
    ),
)
async def truora_get_check(check_id: str) -> str:
    """Get detailed results of a specific background check.

    Args:
        check_id: The check ID (e.g. CHK198e142cdd582a613bb96ff5748f500d)

    Returns:
        Formatted detailed check result with scores and dataset breakdown.
    """
    try:
        client = get_client()
        check_data = client.get_check(check_id)
        check = check_data.get("check", check_data)

        # Try to fetch details too
        details = {}
        try:
            details_data = client.get_check_details(check_id)
            details = details_data.get("details", details_data)
        except TruoraError:
            pass

        result = {
            "check_id": check_id,
            "status": check.get("status"),
            "score": check.get("score"),
            "id_score": check.get("id_score"),
            "homonym_score": check.get("homonym_score"),
            "severity": _severity(check.get("score")),
            "check": check,
            "details": details,
        }
        return _format_check_result(result)
    except TruoraError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        logger.exception("Unexpected error in truora_get_check")
        return f"❌ Unexpected error: {e}"


# ── Tool 3: List Checks ──────────────────────────────────────────────


@server.tool(
    description=(
        "List all background checks in your Truora account. "
        "Optionally filter by report_id. Returns a summary of each check "
        "with score, status, country, type, and severity."
    ),
)
async def truora_list_checks(
    report_id: str | None = None,
    limit: int = 20,
) -> str:
    """List background checks with optional filters.

    Args:
        report_id: Optional — only return checks belonging to this report
        limit: Max number of checks to return (default 20, max 100)

    Returns:
        Formatted table of checks with scores and statuses.
    """
    try:
        client = get_client()
        data = client.list_checks(report_id=report_id, limit=min(limit, 100))

        checks = data.get("checks", data.get("data", [data.get("check", [])]))
        if isinstance(checks, dict):
            checks = [checks]

        if not checks:
            return "No checks found."

        lines = [f"📋 **Checks ({len(checks)})**\n", ""]
        for i, c in enumerate(checks, 1):
            score = c.get("score", "—")
            status = c.get("status", "—")
            country = c.get("country", "—")
            ctype = c.get("type", "—")
            cid = c.get("check_id", "—")
            sev = _severity(score)
            lines.append(
                f"{i}. **{cid}** — {ctype} in {country}"
            )
            lines.append(f"   Score: {score} | Status: {status} | Severity: {sev}")
            lines.append("")

        return "\n".join(lines)
    except TruoraError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        logger.exception("Unexpected error in truora_list_checks")
        return f"❌ Unexpected error: {e}"


# ── Helpers ──────────────────────────────────────────────────────────


def _severity(score: Any) -> str:
    """Human-readable severity from a numeric score."""
    if score is None or score == "—":
        return "unknown"
    try:
        s = float(score)
    except (ValueError, TypeError):
        return "unknown"
    if s < 0:
        return "⏳ pending"
    if s >= 0.8:
        return "✅ low"
    if s >= 0.5:
        return "⚠️ medium"
    return "🔴 high"


def _format_check_result(result: dict[str, Any]) -> str:
    """Format a check result dict into a readable message."""
    cid = result.get("check_id", "—")
    status = result.get("status", "—")
    score = result.get("score", "—")
    severity = result.get("severity", "—")
    id_score = result.get("id_score", "—")
    error = result.get("error")

    lines = [f"🔍 **Check: {cid}**", ""]
    lines.append(f"   **Status:** {status}")
    if error:
        lines.append(f"   **Error:** {error}")
    else:
        lines.append(f"   **Score:** {score}")
        lines.append(f"   **ID Score:** {id_score}")
        lines.append(f"   **Severity:** {severity}")
        lines.append("")

        # Dataset breakdown from details
        details = result.get("details", {})
        if details:
            scores_list = details.get("scores", details.get("data", []))
            if scores_list and isinstance(scores_list, list):
                lines.append("   **📊 Dataset Breakdown:**")
                for ds in scores_list[:10]:  # Show top 10
                    ds_name = ds.get("data_set", "unknown")
                    ds_score = ds.get("score", "—")
                    ds_severity = ds.get("severity", "—")
                    ds_result = ds.get("result", "—")
                    lines.append(
                        f"      • {ds_name}: score={ds_score}, "
                        f"result={ds_result}, severity={ds_severity}"
                    )

    return "\n".join(lines)


# ── Entry point ──────────────────────────────────────────────────────


def main() -> None:
    """Run the Truora MCP server."""
    server.run()


if __name__ == "__main__":
    main()
