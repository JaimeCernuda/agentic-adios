# Agentic Setup with ADIOS

Telemetry collection for AI agents with ADIOS MCP integration.

**Supports:** Claude Code (more to be added)

## Claude Code

### Run
```bash
cd claude_telemetry
export USER_NAME="Your Name" && export USER_EMAIL="your.email@example.com"
docker-compose run --rm claude-code
```

### Analyze
```bash
uv run telemetry
```

Output: `telemetry-data/claude-telemetry_report.md`