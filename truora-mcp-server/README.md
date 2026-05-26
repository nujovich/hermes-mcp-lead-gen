# Truora MCP Server

MCP (Model Context Protocol) server for [Truora](https://truora.com/) — background checks & identity verification for LATAM.

No Python/Node.js SDKs exist for Truora. This MCP server fills that gap, letting any AI agent run KYC/KYB checks, verify identities, and query results via natural language.

## Tools

### 1. `truora_background_check`
Create a background check on a person, vehicle, or company in LATAM. Automatically polls until the check completes.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `country` | ✅ | ISO code: `CO`, `MX`, `CL`, `BR`, `PE`, `CR`, `ALL` |
| `check_type` | ✅ | `person`, `vehicle`, `company`, or custom type |
| `national_id` | ❌ | National ID (required for person/vehicle) |
| `tax_id` | ❌ | Tax ID / RFC (required for company) |
| `license_plate` | ❌ | License plate (for vehicle checks) |
| `first_name` | ❌ | First name (helps disambiguate homonyms) |
| `last_name` | ❌ | Last name |
| `date_of_birth` | ❌ | YYYY-MM-DD |
| `phone_number` | ❌ | Phone (required by law in some countries) |

**Returns:** Score (0-1), severity, dataset-by-dataset breakdown.

### 2. `truora_get_check`
Get full detailed results of a specific check by its check ID.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `check_id` | ✅ | The check ID (e.g. `CHK198e142cdd...`) |

**Returns:** Score, ID score, severity, and per-dataset results.

### 3. `truora_list_checks`
List all background checks with optional filters.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `report_id` | ❌ | Filter by report |
| `limit` | ❌ | Max results (default 20, max 100) |

**Returns:** Formatted table of checks with scores, statuses, and severities.

## Quick Start

```bash
# 1. Install
pip install -e .

# 2. Set your API key
export TRUORA_API_KEY=your_key_here

# 3. Run (stdio mode — for Claude Desktop, Hermes Agent, etc.)
uv run truora-mcp
```

### Configure with Hermes Agent

In `~/.hermes/config.yaml`:

```yaml
tools:
  mcp_servers:
    truora:
      command: uv
      args:
        - run
        - --directory
        - /home/nujovich/hermes-mcp-lead-gen/truora-mcp-server
        - python
        - -m
        - truora_mcp_server
      env:
        TRUORA_API_KEY: "your_key_here"
```

### Configure with Claude Desktop

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "truora": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/truora-mcp-server",
        "python", "-m", "truora_mcp_server"
      ],
      "env": {
        "TRUORA_API_KEY": "your_key_here"
      }
    }
  }
}
```

## API Coverage

| API Family | Endpoints | Status |
|------------|-----------|--------|
| Checks | `POST /v1/checks`, `GET /v1/checks/{id}`, `GET /v1/checks/{id}/details`, `GET /v1/checks` | ✅ Full |
| Digital Identity | DI Processes | 🚧 Coming soon |
| Shared Accounts | Rules, Variables, Actions | 🚧 Coming soon |
| Validator Suite | Accounts, Enrollments, Validations | 🚧 Coming soon |

## Tech Stack

- **Python 3.10+** with **FastMCP** (MCP SDK v1.27.1)
- **httpx** for async HTTP
- Auth via `Truora-API-Key` header

## License

MIT — part of the [Hermes Agent Challenge](https://dev.to/nujovich/building-an-autonomous-mcp-lead-generation-system-with-hermes-agent-gf4) submission.