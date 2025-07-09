# Claude Code Telemetry Analysis Report

**Generated**: 2025-07-08 15:13:06
**Source**: `claude-telemetry-TestUser-20250708-151259.tar.gz`

---

## Executive Summary

- **Total Sessions**: 1
- **Total Events**: 25
- **User Queries**: 3
- **MCP Interactions**: 2
- **Total Cost**: $0.0315

### Token Usage

| Type | Tokens |
|------|--------|
| Input | 430 |
| Output | 370 |

**Average Session Duration**: 300.0 seconds

---

## Session Details

### Session: session-20240108-143000

- **User**: Test User (test@company.com)
- **Start Time**: 2024-01-08T14:30:00Z
- **End Time**: 2024-01-08T14:35:00Z
- **MCP Servers**: adios

#### Conversation Flow

- **📌 claude_code.session.count**: 1
- **🚀 Session Started**: Test User (test@company.com)
- **📊 Token Usage**: 250 input tokens
- **🧑 User Query**: How can I analyze my Adios data files?
- **📊 Token Usage**: 150 output tokens
- **🤖 Claude Response**: I'll help you analyze your Adios data files. Let me first examine what files you have available.
- **💰 Cost**: 0.0120 USD
- **🔧 MCP Interaction**: `file_analysis` on adios server
- **🔧 MCP Tool Call**: Executing file_analysis with Adios server
- **🔧 MCP Tool Call**: Response from Adios server - Found 3 data files: data1.adios, data2.adios, config.xml
- **🤖 Claude Response**: I found 3 Adios files in your workspace. Would you like me to examine their structure?
- **📊 Token Usage**: 180 input tokens
- **🧑 User Query**: Yes, please show me the structure of data1.adios
- **📊 Token Usage**: 220 output tokens
- **🤖 Claude Response**: I'll examine the structure of data1.adios for you.
- **💰 Cost**: 0.0195 USD
- **🔧 MCP Interaction**: `list_files` on adios server
- **🔧 MCP Tool Call**: Executing list_files with Adios server
- **🔧 MCP Tool Call**: Response from Adios server - data1.adios contains: variables=[temperature, pressure], dimensions=[x:100, y:100, time:50]
- **🤖 Claude Response**: The file contains temperature and pressure data on a 100x100 grid over 50 time steps. I can help you visualize or extract specific data.
- **📌 claude_code.lines_of_code.count**: 45
- **📋 AI Activity**: Tool use: Created analysis script analyze_data.py
- **📌 claude_code.lines_of_code.count**: 12
- **🧑 User Query**: exit
- **🏁 Session Ended**: Exit code 0

#### Session Log Excerpt

```
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
... [truncated] ...
```

claude> exit
Goodbye!

=== Claude Code Session Ended ===
Timestamp: 2024-01-08T14:35:00Z
Session duration: 300 seconds
Exit code: 0

```

---

## MCP Server Analysis

### Command Usage

| Command | Count |
|---------|-------|
| `file_analysis` | 1 |
| `list_files` | 1 |

## Raw Telemetry Events

<details>
<summary>Click to expand raw telemetry data</summary>

```json
{
  "timestamp": "2024-01-08T14:30:00Z",
  "metric": "claude_code.session.count",
  "value": 1,
  "attributes": {
    "user": "Test User",
    "email": "test@company.com",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:30:15Z",
  "metric": "claude_code.token.usage",
  "value": 250,
  "attributes": {
    "type": "input",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:30:16Z",
  "metric": "claude_code.token.usage",
  "value": 150,
  "attributes": {
    "type": "output",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:30:17Z",
  "metric": "claude_code.cost.usage",
  "value": 0.012,
  "attributes": {
    "currency": "USD",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:30:20Z",
  "metric": "mcp.interaction",
  "value": 1,
  "attributes": {
    "server": "adios",
    "command": "file_analysis",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:31:30Z",
  "metric": "claude_code.token.usage",
  "value": 180,
  "attributes": {
    "type": "input",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:31:31Z",
  "metric": "claude_code.token.usage",
  "value": 220,
  "attributes": {
    "type": "output",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:31:32Z",
  "metric": "claude_code.cost.usage",
  "value": 0.0195,
  "attributes": {
    "currency": "USD",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:32:00Z",
  "metric": "mcp.interaction",
  "value": 1,
  "attributes": {
    "server": "adios",
    "command": "list_files",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:33:00Z",
  "metric": "claude_code.lines_of_code.count",
  "value": 45,
  "attributes": {
    "type": "added",
    "session_id": "session-20240108-143000"
  }
}
{
  "timestamp": "2024-01-08T14:33:01Z",
  "metric": "claude_code.lines_of_code.count",
  "value": 12,
  "attributes": {
    "type": "removed",
    "session_id": "session-20240108-143000"
  }
}
```

</details>