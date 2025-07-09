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

### Method 1: Using the wrapper script (Recommended)

```bash
# Set your user information
export USER_NAME="Your Name"
export USER_EMAIL="your.email@company.com"

# Run Claude with automatic telemetry
./run-claude.sh

# Claude will start immediately in dangerous mode
# Type 'exit' when done - telemetry will be exported automatically
```

### Method 2: Manual Docker commands

```bash
# Set required environment variables
export USER_NAME="Your Name"
export USER_EMAIL="your.email@company.com"

# Build and start the container
docker-compose up -d

# Claude starts automatically - just connect
docker exec -it claude-code-adios /bin/bash

# When done, export telemetry
docker exec claude-code-adios /usr/local/bin/lifecycle-export.sh

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
├── run-claude.sh                  # Easy wrapper script for running Claude
├── lifecycle-export.sh            # Automatic export on container stop
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

**Required:**
- `USER_NAME`: Your name for tracking (e.g., "John Doe")
- `USER_EMAIL`: Your email for tracking (e.g., "john.doe@company.com")

**Optional:**
- `WORKSPACE_DIR`: Directory to mount as workspace (default: ./workspace)
- `SESSION_ID`: Custom session ID (default: auto-generated)

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