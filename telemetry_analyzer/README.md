# AI Agent Telemetry Analyzer

Unified telemetry analysis for AI agents including Claude Code and Gemini CLI.

## Features

- 📊 **Multi-Agent Support**: Analyzes telemetry from Claude Code and Gemini CLI
- 🔄 **Conversation Flow**: Reconstructs user prompts → agent responses → tool usage
- 📈 **Performance Metrics**: Token usage, costs, response times
- 🛠️ **Tool Analytics**: Tool usage patterns and success rates
- 🎨 **Rich Reports**: Beautiful markdown reports with emojis
- 📤 **Data Export**: JSON export for further analysis

## Installation

```bash
uv sync
```

## Usage

```bash
# Analyze specific agent data
uv run telemetry --data-path ../claude_telemetry/telemetry-data
uv run telemetry --data-path ../gemini_cli_telemetry/telemetry-data

# Analyze all data (auto-detects agent types)
uv run telemetry --data-path ../

# Export detailed data
uv run telemetry --export analysis.json

# Don't display in terminal, just save
uv run telemetry --no-display --output report.md
```

## Report Format

The analyzer generates comprehensive reports showing:

- Summary statistics by agent type
- Top tools used across all agents
- Session details with conversation flows
- Token usage and cost analysis
- Performance metrics

## Supported Agents

- **Claude Code** 🤖: Analyzes claude-telemetry.jsonl files
- **Gemini CLI** ✨: Analyzes OpenTelemetry traces, logs, and metrics files

## File Detection

The analyzer automatically detects agent types based on:
- File names and paths
- File content patterns
- Directory structure

This allows for seamless analysis of mixed telemetry data from multiple agents.