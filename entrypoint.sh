#!/bin/bash
# User-friendly entrypoint for Claude Code with telemetry

# Set up shutdown hook for automatic export
trap '/app/shutdown-export.sh' SIGTERM SIGINT EXIT

# Generate unique session ID
export SESSION_ID="session-$(date +%Y%m%d-%H%M%S)-$(hostname)"
export OTEL_RESOURCE_ATTRIBUTES="${OTEL_RESOURCE_ATTRIBUTES},session.id=${SESSION_ID},user.email=${USER_EMAIL},user.name=${USER_NAME}"

# Create session directory
mkdir -p /logs/${SESSION_ID}
export SESSION_LOG="/logs/${SESSION_ID}/session.log"

# Start logging
exec > >(tee -a ${SESSION_LOG}) 2>&1

clear
echo "============================================="
echo "  Welcome to Claude Code with Adios MCP"
echo "============================================="
echo ""
echo "User: ${USER_NAME} (${USER_EMAIL})"
echo "Session: ${SESSION_ID}"
echo "Workspace: /workspace"
echo ""
echo "The Adios MCP server is pre-configured and ready to use."
echo "All your interactions are being recorded for analysis."
echo ""
echo "When you're done, type 'exit' to close the session."
echo "Your telemetry data will be automatically saved."
echo ""
echo "Starting Claude Code..."
echo "============================================="
echo ""

# Record session start
cat > /logs/${SESSION_ID}/session-info.json << EOF
{
  "session_id": "${SESSION_ID}",
  "user_name": "${USER_NAME}",
  "user_email": "${USER_EMAIL}",
  "start_time": "$(date -Iseconds)",
  "workspace": "/workspace",
  "mcp_servers": ["adios"]
}
EOF

# Run Claude Code with telemetry wrapper
/usr/local/bin/telemetry-wrapper "$@"
EXIT_CODE=$?

# Record session end
END_TIME=$(date -Iseconds)
jq --arg end "$END_TIME" --arg code "$EXIT_CODE" \
  '. + {end_time: $end, exit_code: ($code | tonumber)}' \
  /logs/${SESSION_ID}/session-info.json > /logs/${SESSION_ID}/session-info.tmp && \
  mv /logs/${SESSION_ID}/session-info.tmp /logs/${SESSION_ID}/session-info.json

echo ""
echo "============================================="
echo "  Session Complete"
echo "============================================="
echo ""
echo "Session ended at: $(date)"
echo "Exit code: $EXIT_CODE"
echo ""
echo "Your telemetry data has been saved."
echo "To export your data, run:"
echo "  docker run --rm -v claude-telemetry:/data alpine tar -czf - -C /data . > telemetry-export.tar.gz"
echo ""
echo "Thank you for using Claude Code!"
echo "============================================="

exit $EXIT_CODE