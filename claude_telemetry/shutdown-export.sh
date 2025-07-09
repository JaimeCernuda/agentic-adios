#!/bin/bash
# Automatic telemetry export on container shutdown

echo "Container shutting down - automatically exporting telemetry data..."

# Set default values if not provided
USER_NAME=${USER_NAME:-"unknown-user"}
USER_EMAIL=${USER_EMAIL:-"unknown@company.com"}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
EXPORT_NAME="claude-telemetry-${USER_NAME}-${TIMESTAMP}"
EXPORT_DIR="/tmp/${EXPORT_NAME}"

# Create export directory
mkdir -p "${EXPORT_DIR}"

# Copy telemetry data
echo "Copying telemetry data..."
cp -r /telemetry/* "${EXPORT_DIR}/" 2>/dev/null || mkdir -p "${EXPORT_DIR}/telemetry"

# Copy session logs
echo "Copying session logs..."
cp -r /logs/* "${EXPORT_DIR}/sessions/" 2>/dev/null || mkdir -p "${EXPORT_DIR}/sessions"

# Create analysis summary
cat > "${EXPORT_DIR}/AUTO-EXPORT-README.txt" << 'EOF'
AUTOMATIC TELEMETRY EXPORT
===========================

This export was automatically generated when the Claude Code container was shut down.

Contents:
- telemetry/: OpenTelemetry data files
- sessions/: Session-specific logs and interactions
- This README file

To analyze this data:
1. Extract the tar.gz file
2. Review sessions/ for user interactions
3. Analyze telemetry/ for usage metrics
4. Check session-info.json files for metadata

This data can be used to improve the Adios MCP server and understand user interaction patterns.
EOF

# Generate summary statistics
SESSION_COUNT=$(find "${EXPORT_DIR}/sessions" -name "session-info.json" 2>/dev/null | wc -l)
TELEMETRY_SIZE=$(du -sh "${EXPORT_DIR}" 2>/dev/null | cut -f1 || echo "0")

# Create summary JSON
cat > "${EXPORT_DIR}/auto-export-summary.json" << EOF
{
  "export_type": "automatic_shutdown",
  "export_timestamp": "$(date -Iseconds)",
  "user_name": "${USER_NAME}",
  "user_email": "${USER_EMAIL}",
  "session_count": ${SESSION_COUNT},
  "total_size": "${TELEMETRY_SIZE}",
  "container_shutdown": true
}
EOF

# Create exported-data directory if it doesn't exist
mkdir -p /workspace/exported-data

# Create compressed archive in shared volume
cd /tmp
tar -czf "/workspace/exported-data/${EXPORT_NAME}.tar.gz" "${EXPORT_NAME}"

echo "✅ Automatic export complete: ${EXPORT_NAME}.tar.gz"
echo "📁 Location: ./exported-data/${EXPORT_NAME}.tar.gz"
echo "📊 Sessions exported: ${SESSION_COUNT}"
echo "💾 Total size: ${TELEMETRY_SIZE}"

# Clean up temp directory
rm -rf "${EXPORT_DIR}"