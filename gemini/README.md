# Gemini CLI with ADIOS MCP Docker Setup

This Docker setup runs Google's Gemini CLI with ADIOS MCP for scientific computing capabilities.

## Prerequisites

- Docker/Podman and Docker Compose/Podman Compose installed
- Google Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/))

## Features

- **Gemini CLI**: Google's official command-line interface for Gemini models
- **ADIOS MCP**: Scientific computing capabilities through Model Context Protocol
- **Self-contained**: All configuration is built into the Docker image
- **API Integration**: Uses Google's Gemini API directly (no local inference)

## Quick Start

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/)

2. Run the container:
   ```bash
   # For Docker:
   GEMINI_API_KEY=your-api-key-here docker-compose up -d
   
   # For Podman:
   GEMINI_API_KEY=your-api-key-here podman-compose up -d
   ```

3. Access Gemini CLI:
   ```bash
   # For Docker:
   docker exec -it gemini-cli /usr/local/bin/start-gemini.sh
   
   # For Podman:
   podman exec -it gemini-cli /usr/local/bin/start-gemini.sh
   ```

## Directory Structure

```
gemini/
├── docker-compose.yml    # Docker/Podman Compose configuration
├── Dockerfile           # Gemini CLI container definition with all configs
├── workspace/           # Your project files go here
└── README.md           # This file
```

## Workspace

Place your project files in the `workspace/` directory. This directory is mounted into the Gemini container and will be the default working directory.

## MCP (Model Context Protocol) Support

This setup includes the ADIOS MCP from the scientific-mcps repository, which provides:
- ADIOS data format support
- Scientific computing utilities
- Integration with Gemini CLI for enhanced capabilities

## API Limits

With a personal Google account:
- Up to 60 model requests per minute
- 1,000 model requests per day

For higher limits, consider upgrading to a paid Google Cloud account.

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Troubleshooting

### API Key Issues

If you get authentication errors:
1. Verify your API key is correct
2. Check that the API key has the necessary permissions
3. Ensure you haven't exceeded your rate limits

### Container Issues

If the container fails to start:
1. Check that the GEMINI_API_KEY environment variable is set
2. Verify Docker/Podman is running properly
3. Check container logs: `docker logs gemini-cli` or `podman logs gemini-cli`

## Stopping the Service

```bash
# For Docker:
docker-compose down

# For Podman:
podman-compose down
```

## Commands

Once inside the Gemini CLI, you can:
- Ask questions and get responses from Gemini models
- Upload and analyze files
- Use the built-in Google Search tool
- Access scientific computing capabilities through the ADIOS MCP