"""HTTP client for Truora API (Checks + Digital Identity)."""

import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL_CHECKS = "https://api.checks.truora.com"
BASE_URL_DI = "https://api.digitalidentity.truora.com"

CHECK_TIMEOUT = 120  # Max seconds to wait for a check to complete
POLL_INTERVAL = 3    # Seconds between poll attempts


class TruoraError(Exception):
    """Base error for Truora API failures."""


@dataclass
class TruoraConfig:
    api_key: str
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "TruoraConfig":
        key = os.environ.get("TRUORA_API_KEY", "")
        if not key:
            raise TruoraError(
                "TRUORA_API_KEY environment variable is not set. "
                "Get your key at https://dev.truora.com/"
            )
        return cls(api_key=key)


class TruoraClient:
    """Thin wrapper around Truora's REST APIs."""

    def __init__(self, config: TruoraConfig | None = None):
        self.config = config or TruoraConfig.from_env()
        self._headers = {"Truora-API-Key": self.config.api_key}

    # ── Checks API ──────────────────────────────────────────────────

    def _checks_request(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any]:
        url = f"{BASE_URL_CHECKS}{path}"
        return self._request(method, url, **kwargs)

    def _di_request(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any]:
        url = f"{BASE_URL_DI}{path}"
        return self._request(method, url, **kwargs)

    def _request(
        self, method: str, url: str, **kwargs: Any
    ) -> dict[str, Any]:
        kwargs.setdefault("headers", {}).update(self._headers)
        kwargs.setdefault("timeout", self.config.timeout)
        resp = httpx.request(method, url, **kwargs)
        if resp.status_code >= 400:
            raise TruoraError(
                f"Truora API error {resp.status_code}: {resp.text[:500]}"
            )
        return resp.json()

    def create_check(
        self,
        country: str,
        check_type: str,
        *,
        national_id: str | None = None,
        tax_id: str | None = None,
        license_plate: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: str | None = None,
        phone_number: str | None = None,
        user_authorized: bool = True,
        **extra: Any,
    ) -> dict[str, Any]:
        """Create a background check.

        Args:
            country: ISO code (CO, MX, CL, BR, PE, CR, ALL)
            check_type: 'person', 'vehicle', 'company', or custom_type_name
            national_id: National ID number (for person/vehicle checks)
            tax_id: Tax ID (for company checks)
            license_plate: License plate (for vehicle checks)
            first_name: Person's first name
            last_name: Person's last name
            date_of_birth: YYYY-MM-DD format
            phone_number: Contact phone (required by law in some countries)
            user_authorized: Must be True for API key V1+
            **extra: Additional optional fields (issue_date, gender, etc.)
        """
        payload: dict[str, Any] = {
            "country": country,
            "type": check_type,
            "user_authorized": str(user_authorized).lower(),
        }
        # Map common fields
        for key, value in [
            ("national_id", national_id),
            ("tax_id", tax_id),
            ("license_plate", license_plate),
            ("first_name", first_name),
            ("last_name", last_name),
            ("date_of_birth", date_of_birth),
            ("phone_number", phone_number),
        ]:
            if value is not None:
                payload[key] = value

        payload.update(extra)
        return self._checks_request("POST", "/v1/checks", data=payload)

    def get_check(self, check_id: str) -> dict[str, Any]:
        """Get a background check by its ID."""
        return self._checks_request("GET", f"/v1/checks/{check_id}")

    def get_check_details(self, check_id: str) -> dict[str, Any]:
        """Get detailed breakdown by dataset for a check."""
        return self._checks_request(
            "GET", f"/v1/checks/{check_id}/details"
        )

    def list_checks(
        self,
        *,
        report_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List background checks.

        Args:
            report_id: Optional report ID to filter by
            limit: Max results (default 50)
            offset: Pagination offset
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if report_id:
            params["report_id"] = report_id
        return self._checks_request(
            "GET", "/v1/checks", params=params
        )

    def create_check_and_wait(
        self,
        country: str,
        check_type: str,
        *,
        timeout: int = CHECK_TIMEOUT,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a background check and poll until complete.

        Returns the check result with the final score and status.
        Raises TruoraError if the check doesn't complete in time.
        """
        created = self.create_check(country, check_type, **kwargs)
        check = created.get("check", created)
        check_id = check.get("check_id")
        if not check_id:
            raise TruoraError(f"No check_id in response: {created}")

        deadline = time.time() + timeout
        while time.time() < deadline:
            result = self.get_check(check_id)
            check_data = result.get("check", result)
            status = check_data.get("status", "unknown")

            if status == "ready":
                # Fetch details too
                try:
                    details = self.get_check_details(check_id)
                except TruoraError:
                    details = {}
                return {
                    "check_id": check_id,
                    "status": status,
                    "score": check_data.get("score"),
                    "id_score": check_data.get("id_score"),
                    "homonym_score": check_data.get("homonym_score"),
                    "severity": _infer_severity(check_data),
                    "check": check_data,
                    "details": details,
                }

            if status in ("error", "cancelled", "failed"):
                return {
                    "check_id": check_id,
                    "status": status,
                    "error": check_data.get("error_message", "Unknown error"),
                    "check": check_data,
                }

            time.sleep(POLL_INTERVAL)

        raise TruoraError(
            f"Check {check_id} did not complete within {timeout}s "
            f"(last status: {check_data.get('status', 'unknown')})"
        )


def _infer_severity(check: dict[str, Any]) -> str:
    """Infer overall severity from scores."""
    score = check.get("score")
    if score is None:
        return "unknown"
    if score < 0:
        return "pending"
    if score >= 0.8:
        return "low"
    if score >= 0.5:
        return "medium"
    return "high"
