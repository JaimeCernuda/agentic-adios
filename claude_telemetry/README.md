# Claude Code with Telemetry

This directory contains a Docker setup for Claude Code with comprehensive telemetry collection and analysis capabilities.

## Features

- Claude Code AI assistant with ADIOS MCP integration
- OpenTelemetry-based metrics collection
- Session tracking and analysis
- Token usage and cost monitoring
- MCP interaction tracking
- Automated telemetry export and analysis

## Quick Start

```bash
# Build and start the container
docker-compose up -d

# Connect to Claude
docker exec -it claude-code-adios claude --dangerously-skip-permissions

# Run telemetry tests
docker exec -it claude-code-adios bash -c "cd /app && ./test-telemetry.sh"

# Export telemetry data
docker exec claude-code-adios /app/export-telemetry.sh

# Analyze telemetry
cd claude-telemetry-analyzer
uv sync
uv run claude-telemetry-analyzer analyze ../exported-data/claude-telemetry-*.tar.gz
```

## Directory Structure

```
claude_telemetry/
├── Dockerfile.claude-code          # Main Docker image
├── docker-compose.yml              # Compose configuration with telemetry
├── otel-collector-config.yaml      # OpenTelemetry collector config
├── prometheus.yml                  # Prometheus configuration
├── entrypoint.sh                  # Container entrypoint
├── session-wrapper.sh             # Session management wrapper
├── telemetry-wrapper.sh           # Telemetry collection wrapper
├── export-telemetry.sh            # Export collected telemetry
├── test-telemetry.sh              # Test telemetry system
├── mock-claude.sh                 # Mock Claude for testing
├── setup.sh                       # Initial setup script
├── shutdown-export.sh             # Shutdown and export script
├── create-full-test-tar.sh        # Create test archives
├── analyze-telemetry.py           # Telemetry analysis script
├── claude-telemetry-analyzer/     # Python analyzer package
├── telemetry-data/                # Runtime telemetry storage
├── session-logs/                  # Session logs
├── exported-data/                 # Exported telemetry archives
└── telemetry_examples/            # Example telemetry data
```

## Environment Variables

- `USER_EMAIL`: User email for tracking (default: user@company.com)
- `USER_NAME`: User name for tracking (default: Company User)
- `WORKSPACE_DIR`: Directory to mount as workspace (default: ./workspace)

## Telemetry Metrics

The system collects:
- Session start/end events
- Token usage (input/output)
- Cost tracking
- MCP server interactions
- Lines of code added/removed
- AI activity events

## Analysis

The telemetry analyzer provides:
- Session timeline visualization
- Token usage and cost summaries
- MCP interaction analysis
- Detailed event breakdowns
- Markdown report generation