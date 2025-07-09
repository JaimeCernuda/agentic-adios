#!/bin/bash
# Easy wrapper to run Claude with telemetry

# Check if USER_NAME and USER_EMAIL are provided
if [ -z "$USER_NAME" ] || [ -z "$USER_EMAIL" ]; then
    echo "Please provide your name and email:"
    echo "export USER_NAME=\"Your Name\""
    echo "export USER_EMAIL=\"your.email@company.com\""
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "Starting Claude Code with telemetry for $USER_NAME ($USER_EMAIL)"
echo ""

# Export variables for docker-compose
export USER_NAME
export USER_EMAIL
export SESSION_ID="session-$(date +%Y%m%d-%H%M%S)"

# Change to script directory
cd "$(dirname "$0")"

# Clean up any existing containers
echo "Cleaning up existing containers..."
docker-compose down 2>/dev/null || true
docker container rm -f claude-code-adios 2>/dev/null || true

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d

# Wait for containers to be ready
echo "Waiting for services to start..."
sleep 5

# Connect to Claude - it should start automatically
echo "Connecting to Claude Code..."
echo "Claude will start automatically in dangerous mode."
echo "Type 'exit' when done to automatically export telemetry data."
echo ""
docker exec -it claude-code-adios /bin/bash

# Export telemetry after exit
echo ""
echo "Exporting telemetry data..."
docker exec claude-code-adios /usr/local/bin/lifecycle-export.sh 2>/dev/null || echo "Export may have already completed"

# Clean up
echo "Cleaning up containers..."
docker-compose down

# Show export location
echo ""
echo "Telemetry data exported to: ./exported-data/"
echo "To analyze: cd claude-telemetry-analyzer && uv run claude-telemetry-analyzer analyze ../exported-data/claude-telemetry-*.tar.gz"