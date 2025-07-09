#!/bin/bash
# Session wrapper script for detailed logging

# Log all commands and outputs to session file
exec > >(tee -a /var/logs/session-${SESSION_ID}.log) 2>&1

echo "=== Claude Code Session Started ==="
echo "Session ID: ${SESSION_ID}"
echo "Timestamp: $(date)"
echo "Available MCP Servers:"
echo "  - Adios AI - Advanced AI-powered assistance"
echo ""
echo "Telemetry Configuration:"
echo "  - Traces: Enabled → /var/traces/"
echo "  - Metrics: Enabled → OpenTelemetry Collector"
echo "  - Session logs: /var/logs/session-${SESSION_ID}.log"
echo ""
echo "Monitoring Dashboards:"
echo "  - Grafana: http://localhost:3000"
echo "  - Jaeger: http://localhost:16686"
echo ""

# Execute the actual command
"$@"
EXIT_CODE=$?

# Log session end
echo ""
echo "=== Claude Code Session Ended ==="
echo "Timestamp: $(date)"
echo "Session duration: $(($(date +%s) - $(echo $SESSION_ID | cut -d'-' -f1))) seconds"
echo "Exit code: $EXIT_CODE"

# Create a session summary file
cat > /var/logs/session-${SESSION_ID}-summary.json << EOF
{
  "session_id": "${SESSION_ID}",
  "start_time": "$(echo $SESSION_ID | cut -d'-' -f1)",
  "end_time": "$(date +%s)",
  "duration_seconds": $(($(date +%s) - $(echo $SESSION_ID | cut -d'-' -f1))),
  "hostname": "$(hostname)",
  "exit_code": $EXIT_CODE,
  "telemetry_enabled": true,
  "mcp_servers": ["adios"]
}
EOF

exit $EXIT_CODE