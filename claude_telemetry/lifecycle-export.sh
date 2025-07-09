#!/bin/bash
# Lifecycle hook script for automatic telemetry export

echo "Container stopping - triggering telemetry export..."

# Get the session ID from the last session
LAST_SESSION=$(ls -t /logs | head -n1)

if [ -n "$LAST_SESSION" ]; then
    echo "Exporting telemetry for session: $LAST_SESSION"
    
    # Set environment variables for export
    export SESSION_ID="$LAST_SESSION"
    export USER_NAME="${USER_NAME:-Unknown User}"
    export USER_EMAIL="${USER_EMAIL:-unknown@example.com}"
    
    # Run the export script
    /usr/local/bin/export-telemetry.sh
    
    echo "Telemetry export completed"
else
    echo "No sessions found to export"
fi

# Allow time for export to complete
sleep 5