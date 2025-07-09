# Agentic Setup with ADIOS

Telemetry collection for AI agents with ADIOS MCP integration.

**Supports:** Claude Code, Gemini CLI

## Claude Code

### Run
```bash
cd claude_telemetry
export USER_NAME="Your Name" && export USER_EMAIL="your.email@example.com" & docker-compose run --rm claude-code
```

## Gemini CLI

### Run
Generate your gemini API key, visit: https://aistudio.google.com/apikey. Log-in with your google account, and press "+ Create API key" (in blue).
You might be asked to select a google cloud project, select "Gemini API" and press "Create API in existing project"
Copy the key to a safe space

```bash
cd gemini_cli_telemetry
export USER_NAME="Your Name" && export USER_EMAIL="your.email@example.com" && export  GEMINI_API_KEY="xxxxxxxxxxxxx" & docker-compose run --rm gemini-cli > telemetry-startup.log
```

## Analysis

The telemetry analyzer can analyze data from both agents:

```bash
# Analyze specific agent data
uv run telemetry --data-path claude_telemetry/telemetry-data
uv run telemetry --data-path gemini_cli_telemetry/telemetry-data
```

