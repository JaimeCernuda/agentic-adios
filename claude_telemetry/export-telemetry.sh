#!/bin/bash

echo "Exporting telemetry data..."

# Create export directory
mkdir -p /telemetry/exports

# Create timestamped export
EXPORT_NAME="claude-telemetry-$(date +%Y%m%d-%H%M%S)"

# Check if telemetry data exists
if [ -f "/telemetry/claude-telemetry.jsonl" ]; then
    # Copy telemetry data
    cp /telemetry/claude-telemetry.jsonl "/telemetry/exports/${EXPORT_NAME}.jsonl"
    
    echo "Telemetry exported to: /telemetry/exports/${EXPORT_NAME}.jsonl"
else
    echo "No telemetry data found at /telemetry/claude-telemetry.jsonl"
fi

# Also check for any other telemetry files
if [ -n "$(find /telemetry -name '*.jsonl' -type f 2>/dev/null)" ]; then
    echo "Other telemetry files found:"
    find /telemetry -name '*.jsonl' -type f 2>/dev/null
fi