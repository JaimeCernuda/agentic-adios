#!/bin/bash
# Create a comprehensive test tar file with proper structure

set -e

echo "Creating comprehensive test telemetry archive..."

# Set up test environment
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
EXPORT_NAME="claude-telemetry-TestUser-${TIMESTAMP}"
EXPORT_DIR="./${EXPORT_NAME}"

# Create directories
mkdir -p "${EXPORT_DIR}/sessions/session-20240108-143000"

# Create telemetry data with more events
cat > "${EXPORT_DIR}/claude-telemetry.jsonl" << 'EOF'
{"timestamp":"2024-01-08T14:30:00Z","metric":"claude_code.session.count","value":1,"attributes":{"user":"Test User","email":"test@company.com","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:30:15Z","metric":"claude_code.token.usage","value":250,"attributes":{"type":"input","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:30:16Z","metric":"claude_code.token.usage","value":150,"attributes":{"type":"output","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:30:17Z","metric":"claude_code.cost.usage","value":0.012,"attributes":{"currency":"USD","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:30:20Z","metric":"mcp.interaction","value":1,"attributes":{"server":"adios","command":"file_analysis","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:31:30Z","metric":"claude_code.token.usage","value":180,"attributes":{"type":"input","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:31:31Z","metric":"claude_code.token.usage","value":220,"attributes":{"type":"output","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:31:32Z","metric":"claude_code.cost.usage","value":0.0195,"attributes":{"currency":"USD","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:32:00Z","metric":"mcp.interaction","value":1,"attributes":{"server":"adios","command":"list_files","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:33:00Z","metric":"claude_code.lines_of_code.count","value":45,"attributes":{"type":"added","session_id":"session-20240108-143000"}}
{"timestamp":"2024-01-08T14:33:01Z","metric":"claude_code.lines_of_code.count","value":12,"attributes":{"type":"removed","session_id":"session-20240108-143000"}}
EOF

# Create session info
cat > "${EXPORT_DIR}/sessions/session-20240108-143000/session-info.json" << 'EOF'
{
  "session_id": "session-20240108-143000",
  "user_name": "Test User",
  "user_email": "test@company.com",
  "start_time": "2024-01-08T14:30:00Z",
  "end_time": "2024-01-08T14:35:00Z",
  "workspace": "/workspace",
  "mcp_servers": ["adios"],
  "exit_code": 0
}
EOF

# Create interactions with realistic conversation flow
cat > "${EXPORT_DIR}/sessions/session-20240108-143000/interactions.jsonl" << 'EOF'
{"timestamp":"2024-01-08T14:30:00Z","session_id":"session-20240108-143000","event":"session_start","data":{"user":"Test User","email":"test@company.com"}}
{"timestamp":"2024-01-08T14:30:15Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Processing query: How can I analyze my Adios data files?"}
{"timestamp":"2024-01-08T14:30:16Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Claude: I'll help you analyze your Adios data files. Let me first examine what files you have available."}
{"timestamp":"2024-01-08T14:30:20Z","session_id":"session-20240108-143000","event":"ai_activity","data":"MCP: Executing file_analysis with Adios server"}
{"timestamp":"2024-01-08T14:30:22Z","session_id":"session-20240108-143000","event":"ai_activity","data":"MCP: Response from Adios server - Found 3 data files: data1.adios, data2.adios, config.xml"}
{"timestamp":"2024-01-08T14:30:25Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Claude: I found 3 Adios files in your workspace. Would you like me to examine their structure?"}
{"timestamp":"2024-01-08T14:31:30Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Processing query: Yes, please show me the structure of data1.adios"}
{"timestamp":"2024-01-08T14:31:31Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Claude: I'll examine the structure of data1.adios for you."}
{"timestamp":"2024-01-08T14:32:00Z","session_id":"session-20240108-143000","event":"ai_activity","data":"MCP: Executing list_files with Adios server"}
{"timestamp":"2024-01-08T14:32:02Z","session_id":"session-20240108-143000","event":"ai_activity","data":"MCP: Response from Adios server - data1.adios contains: variables=[temperature, pressure], dimensions=[x:100, y:100, time:50]"}
{"timestamp":"2024-01-08T14:32:05Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Claude: The file contains temperature and pressure data on a 100x100 grid over 50 time steps. I can help you visualize or extract specific data."}
{"timestamp":"2024-01-08T14:33:00Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Tool use: Created analysis script analyze_data.py"}
{"timestamp":"2024-01-08T14:33:30Z","session_id":"session-20240108-143000","event":"ai_activity","data":"Processing query: exit"}
{"timestamp":"2024-01-08T14:35:00Z","session_id":"session-20240108-143000","event":"session_end","data":{"exit_code":0}}
EOF

# Create detailed session log
cat > "${EXPORT_DIR}/sessions/session-20240108-143000/session.log" << 'EOF'
=============================================
  Welcome to Claude Code with Adios MCP
=============================================

User: Test User (test@company.com)
Session: session-20240108-143000
Workspace: /workspace

The Adios MCP server is pre-configured and ready to use.
All your interactions are being recorded for analysis.

When you're done, type 'exit' to close the session.
Your telemetry data will be automatically saved.

Starting Claude Code...
=============================================

claude> How can I analyze my Adios data files?
Processing query: How can I analyze my Adios data files?
Claude: I'll help you analyze your Adios data files. Let me first examine what files you have available.
MCP: Executing file_analysis with Adios server
MCP: Response from Adios server - Found 3 data files: data1.adios, data2.adios, config.xml
Claude: I found 3 Adios files in your workspace. Would you like me to examine their structure?

claude> Yes, please show me the structure of data1.adios
Processing query: Yes, please show me the structure of data1.adios
Claude: I'll examine the structure of data1.adios for you.
MCP: Executing list_files with Adios server
MCP: Response from Adios server - data1.adios contains: variables=[temperature, pressure], dimensions=[x:100, y:100, time:50]
Claude: The file contains temperature and pressure data on a 100x100 grid over 50 time steps. I can help you visualize or extract specific data.

Tool use: Created analysis script analyze_data.py

File created: analyze_data.py
```python
import adios2
import numpy as np
import matplotlib.pyplot as plt

# Open the ADIOS file
with adios2.open("data1.adios", "r") as fh:
    # Read temperature data
    temperature = fh.read("temperature")
    pressure = fh.read("pressure")
    
    # Plot the first timestep
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(temperature[0, :, :], cmap='hot')
    plt.colorbar(label='Temperature')
    plt.title('Temperature at t=0')
    
    plt.subplot(1, 2, 2)
    plt.imshow(pressure[0, :, :], cmap='viridis')
    plt.colorbar(label='Pressure')
    plt.title('Pressure at t=0')
    
    plt.tight_layout()
    plt.show()
```

claude> exit
Goodbye!

=== Claude Code Session Ended ===
Timestamp: 2024-01-08T14:35:00Z
Session duration: 300 seconds
Exit code: 0
EOF

# Create README
cat > "${EXPORT_DIR}/README.txt" << 'EOF'
Claude Code Telemetry Export
============================

This archive contains telemetry data from a Claude Code session with Adios MCP integration.

Test Session Details:
- User performed 3 queries
- Used Adios MCP server for file analysis
- Created an analysis script
- Total cost: $0.0315
- Duration: 5 minutes

This is test data for the telemetry analysis tool.
EOF

# Create tar archive
tar -czf "${EXPORT_NAME}.tar.gz" "${EXPORT_NAME}"
rm -rf "${EXPORT_DIR}"

echo "✅ Created comprehensive test archive: ${EXPORT_NAME}.tar.gz"
echo "📊 This archive contains:"
echo "   - Complete session data with conversation flow"
echo "   - Telemetry metrics (tokens, costs, MCP interactions)"
echo "   - Session logs with code generation"
echo "   - Proper directory structure"