# OpenCode with Ollama and ADIOS MCP Docker Setup

This Docker setup runs OpenCode (an AI coding agent similar to Claude Code) with Ollama for local LLM inference and includes the ADIOS MCP for scientific computing capabilities.

## Prerequisites

- Docker/Podman and Docker Compose/Podman Compose installed
- Sufficient disk space for Ollama models (models can be several GB)
- (Optional) NVIDIA GPU with Docker/Podman GPU support configured

## Features

- **OpenCode**: AI coding agent with terminal interface
- **Ollama**: Local LLM inference with multiple model support
- **GPU Support**: NVIDIA GPU acceleration for faster inference (optional)
- **ADIOS MCP**: Scientific computing capabilities through Model Context Protocol
- **Pre-configured networking**: Services communicate through Docker/Podman network
- **Self-contained**: All configuration is built into the Docker image
- **Model Validation**: Only pre-configured models are allowed to ensure compatibility

## Quick Start

1. Clone or create this directory structure

2. Choose the appropriate compose file:
   ```bash
   # For GPU support (NVIDIA):
   docker-compose up -d
   
   # For CPU-only:
   docker-compose -f docker-compose.cpu.yml up -d
   
   # For Podman with GPU:
   podman-compose up -d
   
   # For Podman CPU-only:
   podman-compose -f docker-compose.cpu.yml up -d
   ```

3. The first run will download and install the default model (llama3.1:8b). This may take several minutes.

4. Access OpenCode:
   ```bash
   # For Docker:
   docker exec -it opencode opencode
   
   # For Podman:
   podman exec -it opencode opencode
   ```

## Configuration

### Changing the Default Model

You can specify a different model when starting the containers. **Only pre-configured models are supported** to ensure they work properly with OpenCode:

```bash
# For Docker:
OLLAMA_MODEL=codellama:latest docker-compose up -d

# For Podman:
OLLAMA_MODEL=codellama:latest podman-compose up -d
```

**Supported models** (these are pre-configured in OpenCode):
- `llama3.1:8b` (default) - Balanced performance
- `llama3.1:70b` - Larger, more capable model
- `codellama:latest` - Optimized for code generation
- `deepseek-coder:latest` - Specialized coding model
- `qwen2.5-coder:latest` - Advanced coding capabilities

If you specify an unsupported model, the container will show an error and list the available options.

### Adding Support for New Models

To add support for additional models:

1. Edit the Dockerfile and add the model to the OpenCode configuration
2. Edit start.sh and add the model to the SUPPORTED_MODELS array
3. Rebuild the image: `docker-compose build` or `podman-compose build`

Note: Simply pulling a model with `ollama pull` is not enough - the model must also be configured in OpenCode.

### Switching Models in OpenCode

Once inside OpenCode, use the `/models` command to switch between available models.

## Directory Structure

```
opencoder-ollama/
├── docker-compose.yml      # Docker/Podman Compose configuration (GPU-enabled)
├── docker-compose.cpu.yml  # CPU-only version
├── Dockerfile             # OpenCode container definition with all configs
├── start.sh               # Ollama startup script with model validation
├── workspace/             # Your project files go here
└── README.md              # This file
```

## Workspace

Place your project files in the `workspace/` directory. This directory is mounted into the OpenCode container and will be the default working directory.

## MCP (Model Context Protocol) Support

This setup includes the ADIOS MCP from the scientific-mcps repository, which provides:
- ADIOS data format support
- Scientific computing utilities
- Integration with OpenCode for enhanced capabilities

The MCP is automatically configured and available when you start OpenCode.

## Networking

The services communicate through an internal Docker/Podman network:
- Ollama is accessible at `http://ollama:11434` from within the OpenCode container
- No ports are exposed to the host by default (for security)
- Services use hostnames for reliable communication

## Troubleshooting

### Ollama Connection Issues

If OpenCode cannot connect to Ollama:
1. Check that Ollama is running: `docker ps` or `podman ps`
2. Check Ollama logs: `docker logs ollama` or `podman logs ollama`
3. Ensure the health check is passing
4. Verify the network connectivity between containers

### Model Download Issues

If model download fails:
1. Check your internet connection
2. Ensure you have sufficient disk space
3. Try pulling the model manually
4. Check Ollama logs for specific errors

### Podman-specific Issues

If using Podman and encountering permission issues:
1. The `:z` flag is already added to volume mounts for SELinux compatibility
2. Ensure your user has proper permissions for the workspace directory
3. Consider using `podman unshare` if needed for rootless operations

## Stopping the Services

```bash
# For Docker:
docker-compose down

# For Podman:
podman-compose down
```

To also remove the downloaded models:
```bash
# For Docker:
docker-compose down -v

# For Podman:
podman-compose down -v
```