#!/bin/bash
# Wrapper to capture all Claude Code interactions

# Create a detailed interaction log
INTERACTION_LOG="/logs/${SESSION_ID}/interactions.jsonl"
touch ${INTERACTION_LOG}

# Function to log interactions
log_interaction() {
    local event_type=$1
    local data=$2
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"session_id\":\"${SESSION_ID}\",\"event\":\"${event_type}\",\"data\":${data}}" >> ${INTERACTION_LOG}
}

# Log session start
log_interaction "session_start" "{\"user\":\"${USER_NAME}\",\"email\":\"${USER_EMAIL}\"}"

# Set up command logging
export HISTFILE="/logs/${SESSION_ID}/command_history.txt"
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S "

# Run Claude Code with all arguments
"$@" 2>&1 | while IFS= read -r line; do
    echo "$line"
    # Capture specific patterns for analysis
    if [[ "$line" =~ "Tool use:" ]] || [[ "$line" =~ "Model:" ]] || [[ "$line" =~ "MCP:" ]]; then
        log_interaction "ai_activity" "\"${line//\"/\\\"}\""
    fi
done

EXIT_CODE=${PIPESTATUS[0]}

# Log session end
log_interaction "session_end" "{\"exit_code\":${EXIT_CODE}}"

exit $EXIT_CODE