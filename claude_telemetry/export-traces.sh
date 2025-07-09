#!/bin/bash
# Script to export traces and session data for sharing

SESSION_ID=${1:-$(date +%Y%m%d-%H%M%S)}
EXPORT_DIR="./exported-traces/${SESSION_ID}"

mkdir -p "${EXPORT_DIR}"

echo "Exporting Claude Code session data..."
echo "Session ID: ${SESSION_ID}"

# Copy trace files from container
echo "Copying trace files..."
docker cp claude-code:/var/traces/. "${EXPORT_DIR}/" 2>/dev/null || echo "No trace files found"

# Copy session logs from container
echo "Copying session logs..."
docker cp claude-code:/var/logs/. "${EXPORT_DIR}/" 2>/dev/null || echo "No session logs found"

# Export metrics from Prometheus (if available)
if command -v curl &> /dev/null; then
    echo "Exporting metrics from Prometheus..."
    curl -s "http://localhost:9090/api/v1/query_range?query=claude_code_session_count_total&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=60" > "${EXPORT_DIR}/session-metrics.json" 2>/dev/null || echo "Could not export Prometheus metrics"
fi

# Export Jaeger traces
echo "Exporting Jaeger traces..."
SERVICES=$(curl -s "http://localhost:16686/api/services" | jq -r '.data[]' 2>/dev/null)
if [ ! -z "$SERVICES" ]; then
    for service in $SERVICES; do
        curl -s "http://localhost:16686/api/traces?service=${service}&limit=1000" > "${EXPORT_DIR}/jaeger-traces-${service}.json" 2>/dev/null
    done
fi

# Create comprehensive summary report
cat > "${EXPORT_DIR}/session-summary.txt" << SUMMARY
Claude Code Session Export
==========================
Export Date: $(date)
Session ID: ${SESSION_ID}
Export Directory: ${EXPORT_DIR}

Files Included:
$(find "${EXPORT_DIR}" -type f -exec ls -lh {} \; | awk '{print $9 " (" $5 ")"}')

Data Types:
- claude-code-traces.jsonl: OpenTelemetry trace data in JSON Lines format
- claude-code-metrics.jsonl: OpenTelemetry metrics data  
- session-*.log: Complete session command history and outputs
- session-metrics.json: Prometheus metrics export (if available)
- jaeger-traces-*.json: Jaeger trace exports

Analysis Instructions:
1. Import traces into Jaeger or any OpenTelemetry-compatible tool
2. Review session logs for complete command history
3. Analyze metrics for usage patterns and performance

Trace Data Schema:
Each trace line contains:
- timestamp: ISO 8601 timestamp
- session_id: Unique session identifier  
- metric_name: Type of metric (session.count, token.usage, etc.)
- value: Numeric value
- attributes: Additional metadata (model, type, etc.)

Key Metrics to Analyze:
- claude_code.token.usage: Token consumption by type (input/output)
- claude_code.cost.usage: Estimated costs
- claude_code.lines_of_code.count: Code modifications
- claude_code.session.count: Session activity

For questions about this data, refer to:
https://docs.anthropic.com/en/docs/claude-code/monitoring-usage

SUMMARY

# Create compressed archive
tar -czf "claude-code-session-${SESSION_ID}.tar.gz" -C ./exported-traces "${SESSION_ID}"

echo ""
echo "✅ Export complete!"
echo "📁 Archive: claude-code-session-${SESSION_ID}.tar.gz"
echo "📊 Contains: traces, metrics, and session logs"
echo "🔗 Share this file for detailed usage analysis"
echo ""
echo "Quick stats:"
echo "- Archive size: $(du -h claude-code-session-${SESSION_ID}.tar.gz | cut -f1)"
echo "- Files exported: $(find "${EXPORT_DIR}" -type f | wc -l)"
echo "- Session logs: $(find "${EXPORT_DIR}" -name "session-*.log" | wc -l)"