# Claude Code Telemetry Analysis Report

**Generated**: 2025-07-08 15:11:54
**Source**: `claude-telemetry-Test-User-20250708-150316.tar.gz`

---

## Executive Summary

- **Total Sessions**: 0
- **Total Events**: 5
- **User Queries**: 0
- **MCP Interactions**: 1
- **Total Cost**: $0.0120

### Token Usage

| Type | Tokens |
|------|--------|
| Input | 250 |
| Output | 150 |

---

## Session Details

## MCP Server Analysis

### Command Usage

| Command | Count |
|---------|-------|
| `file_analysis` | 1 |

## Raw Telemetry Events

<details>
<summary>Click to expand raw telemetry data</summary>

```json
{
  "timestamp": "2024-01-08T14:30:00Z",
  "metric": "claude_code.session.count",
  "value": 1,
  "attributes": {
    "user": "Test User",
    "email": "test@company.com"
  }
}
{
  "timestamp": "2024-01-08T14:30:15Z",
  "metric": "claude_code.token.usage",
  "value": 250,
  "attributes": {
    "type": "input"
  }
}
{
  "timestamp": "2024-01-08T14:30:16Z",
  "metric": "claude_code.token.usage",
  "value": 150,
  "attributes": {
    "type": "output"
  }
}
{
  "timestamp": "2024-01-08T14:30:17Z",
  "metric": "claude_code.cost.usage",
  "value": 0.012,
  "attributes": {
    "currency": "USD"
  }
}
{
  "timestamp": "2024-01-08T14:30:20Z",
  "metric": "mcp.interaction",
  "value": 1,
  "attributes": {
    "server": "adios",
    "command": "file_analysis"
  }
}
```

</details>