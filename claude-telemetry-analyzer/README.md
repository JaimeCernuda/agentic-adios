# Claude Telemetry Analyzer

A tool for analyzing Claude Code telemetry tar files and generating comprehensive markdown reports with conversation flows, usage statistics, and MCP server interaction analysis.

## Features

- **Conversation Reconstruction**: Rebuilds complete user-AI interactions from telemetry data
- **Usage Statistics**: Token consumption, costs, session durations
- **MCP Analysis**: Server interactions, command usage patterns
- **Code Metrics**: Lines of code added/removed/modified
- **Exportable Reports**: Clean markdown format for easy sharing

## Installation

Using `uv` (recommended):

```bash
# Install the package
uv sync

# Or install in development mode
uv pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
uv run claude-telemetry-analyzer telemetry.tar.gz

# Specify output file
uv run claude-telemetry-analyzer telemetry.tar.gz -o my_report.md

# Verbose output for debugging
uv run claude-telemetry-analyzer telemetry.tar.gz -v

# Using alternative command name
uv run analyze-claude-telemetry telemetry.tar.gz
```

### Python API

```python
from claude_telemetry_analyzer import TelemetryAnalyzer

# Analyze a tar file
analyzer = TelemetryAnalyzer("path/to/telemetry.tar.gz")
report = analyzer.analyze()

# Save to file
with open("report.md", "w") as f:
    f.write(report)

# Get statistics
stats = analyzer.calculate_statistics()
print(f"Total cost: ${stats['total_cost']:.4f}")
```

## Report Structure

The generated markdown report includes:

1. **Executive Summary**
   - Session count, total events, queries
   - Cost breakdown and token usage
   - Average session duration

2. **Session Details**
   - Complete conversation flows
   - User queries and AI responses
   - MCP server interactions
   - Session logs (truncated for readability)

3. **MCP Server Analysis**
   - Command usage frequency
   - Server interaction patterns

4. **Raw Telemetry Data**
   - Expandable section with JSONL events
   - Useful for debugging and deep analysis

## Example Output

```markdown
# Claude Code Telemetry Analysis Report

## Executive Summary

- **Total Sessions**: 1
- **Total Events**: 25
- **User Queries**: 3
- **MCP Interactions**: 2
- **Total Cost**: $0.0315

### Session: session-20240108-143000

#### Conversation Flow

- **🧑 User Query**: How can I analyze my Adios data files?
- **🤖 Claude Response**: I'll help you analyze your Adios data files...
- **🔧 MCP Tool Call**: Executing file_analysis with Adios server
- **💰 Cost**: 0.0120 USD
```

## Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/
```

## License

MIT