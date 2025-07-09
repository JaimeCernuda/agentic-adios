#!/bin/bash
# Mock Claude Code for testing telemetry collection

echo "Mock Claude Code started for telemetry testing"
echo "This simulates Claude Code interactions with Adios MCP"
echo ""
echo "Available commands:"
echo "  - help: Show this help"
echo "  - query <text>: Simulate a query to Claude"
echo "  - mcp <command>: Simulate MCP server interaction"
echo "  - exit: Exit the session"
echo ""

# Function to simulate OpenTelemetry metrics
send_telemetry() {
    local metric_name=$1
    local value=$2
    local attributes=$3
    
    # Simulate telemetry data
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"metric\":\"${metric_name}\",\"value\":${value},\"attributes\":${attributes}}" >> /telemetry/claude-telemetry.jsonl
}

# Function to simulate MCP interaction
simulate_mcp() {
    local command=$1
    echo "MCP: Executing ${command} with Adios server"
    send_telemetry "mcp.interaction" 1 "{\"server\":\"adios\",\"command\":\"${command}\"}"
    echo "MCP: Response from Adios server for ${command}"
}

# Function to simulate query
simulate_query() {
    local query=$1
    echo "Processing query: ${query}"
    
    # Simulate token usage
    local input_tokens=$((100 + RANDOM % 500))
    local output_tokens=$((50 + RANDOM % 200))
    
    send_telemetry "claude_code.token.usage" ${input_tokens} "{\"type\":\"input\"}"
    send_telemetry "claude_code.token.usage" ${output_tokens} "{\"type\":\"output\"}"
    
    # Simulate cost
    local cost=$(echo "scale=4; ($input_tokens * 0.000015) + ($output_tokens * 0.000075)" | bc -l)
    send_telemetry "claude_code.cost.usage" ${cost} "{\"currency\":\"USD\"}"
    
    echo "Claude: Here's my response to '${query}'"
    echo "This is a simulated response that would help with your Adios files."
    
    # Simulate occasional MCP usage
    if [ $((RANDOM % 3)) -eq 0 ]; then
        simulate_mcp "file_analysis"
    fi
}

# Main interaction loop
echo "Starting interactive session..."
send_telemetry "claude_code.session.count" 1 "{\"user\":\"${USER_NAME}\",\"email\":\"${USER_EMAIL}\"}"

while true; do
    echo -n "claude> "
    read -r input
    
    if [[ "$input" == "exit" ]]; then
        echo "Goodbye!"
        break
    elif [[ "$input" == "help" ]]; then
        echo "Available commands:"
        echo "  - help: Show this help"
        echo "  - query <text>: Simulate a query to Claude"
        echo "  - mcp <command>: Simulate MCP server interaction"
        echo "  - exit: Exit the session"
    elif [[ "$input" =~ ^query ]]; then
        query_text="${input#query }"
        simulate_query "$query_text"
    elif [[ "$input" =~ ^mcp ]]; then
        mcp_command="${input#mcp }"
        simulate_mcp "$mcp_command"
    else
        echo "Unknown command. Type 'help' for available commands."
    fi
done