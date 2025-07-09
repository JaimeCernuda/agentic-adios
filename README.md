# AI Coding Agents Docker Setups

This repository contains Docker setups for various AI coding agents with scientific computing capabilities.

## Available Setups

### 1. Claude Code with Telemetry
Located in `claude_telemetry/`. Provides Claude Code with comprehensive telemetry collection and ADIOS MCP integration.

**Features:**
- Claude Code AI assistant with telemetry tracking
- OpenTelemetry-based metrics collection
- ADIOS MCP for scientific data processing
- Session analysis and cost tracking

**Usage:**
```bash
cd claude_telemetry
export USER_NAME="Your Name"
export USER_EMAIL="your.email@company.com"
./run-claude.sh
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
├── USER-INSTRUCTIONS.md            # User instructions documentation
├── complete_implementation_guide.md # Implementation guide
├── claude_telemetry/               # Claude Code with telemetry setup
│   ├── Dockerfile.claude-code      # Docker image
│   ├── docker-compose.yml          # Compose configuration
│   ├── README.md                   # Setup documentation
│   └── ... (telemetry scripts and tools)
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