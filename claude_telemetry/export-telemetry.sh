#!/bin/bash
# Export telemetry data for sharing

set -e

echo "======================================"
echo "  Claude Code Telemetry Export"
echo "======================================"
echo ""

# Check if docker compose is running
if ! docker-compose ps | grep -q "claude-code-adios"; then
    echo "⚠️  Claude Code container is not running."
    echo "Please ensure you've run: docker-compose up -d"
    exit 1
fi

# Get container name
CONTAINER_NAME="claude-code-adios"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
EXPORT_NAME="claude-telemetry-${USER:-unknown}-${TIMESTAMP}"
EXPORT_DIR="./${EXPORT_NAME}"

echo "Creating export directory: ${EXPORT_DIR}"
mkdir -p "${EXPORT_DIR}"

# Copy telemetry data from container
echo "Exporting telemetry data..."
docker cp ${CONTAINER_NAME}:/telemetry/. "${EXPORT_DIR}/telemetry/" 2>/dev/null || echo "No telemetry data found"

# Copy session logs
echo "Exporting session logs..."
docker cp ${CONTAINER_NAME}:/logs/. "${EXPORT_DIR}/sessions/" 2>/dev/null || echo "No session logs found"

# Get container logs
echo "Exporting container logs..."
docker-compose logs claude-code > "${EXPORT_DIR}/container.log" 2>&1

# Create analysis summary
echo "Creating analysis summary..."
cat > "${EXPORT_DIR}/README.txt" << 'EOF'
Claude Code Telemetry Export
============================

This archive contains all telemetry data from your Claude Code session(s).

Contents:
---------
- telemetry/         : OpenTelemetry data files
  - claude-telemetry.jsonl : All telemetry events
  - claude-traces.jsonl    : Detailed trace data
  - claude-metrics.jsonl   : Metrics data

- sessions/          : Session-specific data
  - session-*/       : Individual session folders
    - session.log    : Complete terminal output
    - session-info.json : Session metadata
    - interactions.jsonl : AI interaction events
    - command_history.txt : Command history

- container.log      : Docker container logs
- summary.json       : Export summary and statistics

Data Analysis Guide:
-------------------
1. Session Information:
   - Check sessions/*/session-info.json for user and timing data
   - Review sessions/*/session.log for complete interaction history

2. AI Interactions:
   - Parse sessions/*/interactions.jsonl for AI activity patterns
   - Look for "Tool use:", "Model:", and "MCP:" events

3. Telemetry Metrics:
   - telemetry/claude-metrics.jsonl contains:
     * Token usage (input/output/cache)
     * Cost estimates
     * Lines of code modified
     * Session counts

4. Trace Analysis:
   - telemetry/claude-traces.jsonl provides detailed execution traces
   - Useful for understanding performance and tool usage patterns

Key Metrics to Analyze:
----------------------
- claude_code.token.usage: Token consumption breakdown
- claude_code.cost.usage: Estimated API costs
- claude_code.lines_of_code.count: Code modification metrics
- claude_code.session.count: Session activity
- MCP server interactions: Adios tool usage patterns

For questions about the telemetry format, see:
https://docs.anthropic.com/en/docs/claude-code/monitoring-usage
EOF

# Generate summary statistics
echo "Generating summary statistics..."
SUMMARY_FILE="${EXPORT_DIR}/summary.json"

# Count sessions
SESSION_COUNT=$(find "${EXPORT_DIR}/sessions" -name "session-info.json" 2>/dev/null | wc -l)

# Get file sizes
TELEMETRY_SIZE=$(du -sh "${EXPORT_DIR}/telemetry" 2>/dev/null | cut -f1 || echo "0")
SESSIONS_SIZE=$(du -sh "${EXPORT_DIR}/sessions" 2>/dev/null | cut -f1 || echo "0")
TOTAL_SIZE=$(du -sh "${EXPORT_DIR}" 2>/dev/null | cut -f1 || echo "0")

# Create summary JSON
cat > "${SUMMARY_FILE}" << EOF
{
  "export_timestamp": "$(date -Iseconds)",
  "export_name": "${EXPORT_NAME}",
  "statistics": {
    "session_count": ${SESSION_COUNT},
    "telemetry_size": "${TELEMETRY_SIZE}",
    "sessions_size": "${SESSIONS_SIZE}",
    "total_size": "${TOTAL_SIZE}"
  },
  "files": {
    "telemetry_files": $(ls -1 "${EXPORT_DIR}/telemetry" 2>/dev/null | wc -l || echo 0),
    "session_folders": ${SESSION_COUNT}
  }
}
EOF

# Create compressed archive
echo "Creating compressed archive..."
tar -czf "${EXPORT_NAME}.tar.gz" -C . "${EXPORT_NAME}"

# Clean up directory
rm -rf "${EXPORT_DIR}"

echo ""
echo "✅ Export complete!"
echo ""
echo "📦 Archive created: ${EXPORT_NAME}.tar.gz"
echo "📊 Size: $(du -h ${EXPORT_NAME}.tar.gz | cut -f1)"
echo "📁 Sessions exported: ${SESSION_COUNT}"
echo ""
echo "🔗 Share this file for telemetry analysis"
echo ""
echo "To extract the archive:"
echo "  tar -xzf ${EXPORT_NAME}.tar.gz"
echo ""