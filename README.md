# AI Coding Agents Docker Setups

This repository contains Docker setups for various AI coding agents with scientific computing capabilities.

## Available Setups

### 1. Claude Code with ADIOS MCP
Located in the root directory. Provides Claude Code with the ADIOS MCP for scientific computing.

**Features:**
- Claude Code AI assistant
- ADIOS MCP for scientific data processing
- Python environment with uv package management

**Usage:**
```bash
docker-compose up -d
docker exec -it claude_code claude
```

### 2. OpenCode with Ollama
Located in `opencoder-ollama/`. Provides OpenCode (SST's AI coding agent) with local Ollama inference.

**Features:**
- OpenCode AI coding agent (similar to Claude Code)
- Local LLM inference with Ollama
- GPU acceleration support
- Multiple pre-configured models (Llama 3.1, Code Llama, DeepSeek Coder, etc.)
- ADIOS MCP integration
- Model validation and selection

**Usage:**
```bash
cd opencoder-ollama
# With GPU support:
OLLAMA_MODEL=codellama:latest docker-compose up -d
# CPU only:
OLLAMA_MODEL=codellama:latest docker-compose -f docker-compose.cpu.yml up -d

docker exec -it opencode opencode
```

### 3. Gemini CLI
Located in `gemini/`. Provides Google's Gemini CLI with ADIOS MCP integration.

**Features:**
- Google Gemini CLI
- Direct API integration (no local inference)
- ADIOS MCP for scientific computing
- Built-in Google Search capabilities

**Usage:**
```bash
cd gemini
GEMINI_API_KEY=your-api-key docker-compose up -d
docker exec -it gemini-cli /usr/local/bin/start-gemini.sh
```

## Common Features

All setups include:
- **ADIOS MCP**: Scientific computing capabilities through Model Context Protocol
- **Workspace mounting**: Your project files are accessible in `/workspace`
- **Docker/Podman compatibility**: Works with both container runtimes
- **Self-contained**: All configurations built into images for easy sharing

## Prerequisites

- Docker or Podman with Compose
- Sufficient disk space (especially for Ollama models)
- API keys (for Claude Code and Gemini setups)
- NVIDIA GPU support (optional, for Ollama GPU acceleration)

## Directory Structure

```
.
├── README.md                        # This file
├── Dockerfile.claude-code           # Claude Code Docker setup
├── docker-compose.yml               # Main compose file with telemetry
├── otel-collector-config.yaml       # OpenTelemetry collector configuration
├── prometheus.yml                   # Prometheus configuration
├── entrypoint.sh                   # Container entrypoint script
├── mock-claude.sh                  # Mock Claude CLI for testing
├── session-wrapper.sh              # Session management wrapper
├── setup.sh                        # Initial setup script
├── shutdown-export.sh              # Shutdown and export script
├── create-full-test-tar.sh         # Test archive creation script
├── USER-INSTRUCTIONS.md            # User instructions documentation
├── complete_implementation_guide.md # Implementation guide
├── claude_telemetry/               # All telemetry-related files
│   ├── analyze-telemetry.py        # Telemetry analysis script
│   ├── export-telemetry.sh         # Export telemetry data
│   ├── export-traces.sh            # Export traces
│   ├── telemetry-wrapper.sh        # Telemetry wrapper script
│   ├── test-telemetry.sh           # Test telemetry system
│   ├── telemetry-data/             # Telemetry data storage
│   ├── session-logs/               # Session logs storage
│   ├── exported-data/              # Exported data storage
│   ├── claude-telemetry-*.tar.gz   # Telemetry archives
│   ├── *_analysis.md               # Analysis reports
│   ├── claude-telemetry-analyzer/  # Python telemetry analyzer package
│   │   ├── src/                    # Source code
│   │   ├── pyproject.toml          # Python project configuration
│   │   └── README.md               # Analyzer documentation
│   └── telemetry_examples/         # Example telemetry data
│       └── claude-telemetry-Test-User-20250708-150316/
├── claude/                         # Claude-specific files
│   └── Dockerfile.dangerous        # Dangerous Dockerfile example
├── opencoder-ollama/               # OpenCode + Ollama setup
│   ├── Dockerfile
│   ├── docker-compose.yml          # GPU-enabled version
│   ├── docker-compose.cpu.yml      # CPU-only version
│   ├── start.sh                    # Model validation script
│   └── README.md
├── gemini/                         # Gemini CLI setup
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
└── workspace/                      # Shared workspace directory
```

## Getting Started

1. Choose the AI coding agent you want to use
2. Navigate to the appropriate directory
3. Follow the specific README instructions for that setup
4. Set required environment variables (API keys, model selection)
5. Run `docker-compose up -d`
6. Access the AI agent using the provided commands

## Contributing

Feel free to submit issues and pull requests to improve these setups.

## License

This project is open source and available under the MIT License.