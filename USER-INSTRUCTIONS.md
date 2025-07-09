# Claude Code with Adios MCP - Telemetry Collection

This Docker setup provides Claude Code with the Adios MCP server pre-configured for exploring your files, while collecting comprehensive telemetry data for analysis.

## Quick Start for Users

### 1. Setup (First Time Only)

```bash
# Set your user information
export USER_NAME="Your Name"
export USER_EMAIL="your.email@company.com"

# Optional: Set custom workspace directory
export WORKSPACE_DIR="/path/to/your/adios/files"

# Start the environment
docker-compose up -d
```

### 2. Use Claude Code

The Claude Code interface will start automatically with:
- **Adios MCP server** pre-configured for file exploration
- **Telemetry collection** running in the background
- **User-friendly interface** with welcome message

Simply interact with Claude Code as normal. The Adios MCP server will help you explore and analyze your files.

### 3. Export Your Data

**Option A: Automatic Export (Recommended)**
- Simply stop the container with `docker-compose down`
- Telemetry data is automatically exported to `./exported-data/`
- Look for files like `claude-telemetry-yourname-20240108-143022.tar.gz`

**Option B: Manual Export**
```bash
./export-telemetry.sh
```

### 4. Cleanup

```bash
docker-compose down
```

## What Gets Collected

### Telemetry Data
- **Token usage**: Input, output, and cache token consumption
- **Cost estimates**: API usage costs
- **Code metrics**: Lines of code modified, files touched
- **Session data**: Start/end times, duration, user info
- **Tool interactions**: MCP server usage patterns

### Session Logs
- **Complete terminal output**: Everything you see in Claude Code
- **Command history**: All commands executed
- **AI interactions**: Detailed interaction patterns
- **MCP events**: Adios server communication

### File Structure in Export
```
claude-telemetry-user-timestamp/
├── telemetry/
│   ├── claude-telemetry.jsonl    # All telemetry events
│   ├── claude-traces.jsonl       # Detailed traces
│   └── claude-metrics.jsonl      # Metrics data
├── sessions/
│   └── session-*/
│       ├── session.log           # Terminal output
│       ├── session-info.json     # Session metadata
│       ├── interactions.jsonl    # AI activity
│       └── command_history.txt   # Commands
├── container.log                 # Docker logs
├── summary.json                  # Export statistics
└── README.txt                    # Analysis guide
```

## For Developers/Analysts

### Environment Variables
```bash
USER_NAME="John Doe"              # Required: User's full name
USER_EMAIL="john@company.com"     # Required: User's email
WORKSPACE_DIR="./my-files"        # Optional: Custom workspace
```

### Key Files to Analyze
1. **sessions/*/interactions.jsonl** - AI interaction patterns
2. **telemetry/claude-metrics.jsonl** - Usage metrics
3. **sessions/*/session.log** - Complete user sessions

### Common Analysis Patterns
```bash
# Count total sessions
jq 'select(.event=="session_start")' */sessions/*/interactions.jsonl | wc -l

# Extract token usage
jq 'select(.metric_name=="claude_code.token.usage")' */telemetry/claude-metrics.jsonl

# Find MCP interactions
grep -r "MCP:" */sessions/*/interactions.jsonl
```

## Architecture

```
User → Claude Code → Adios MCP → OpenTelemetry → File Export
                  ↓
              Telemetry Data
```

- **Claude Code**: AI interface with `--dangerous` flag for immediate use
- **Adios MCP**: Pre-configured for file exploration
- **OpenTelemetry**: Collects all interaction data
- **File Export**: Creates shareable telemetry archives

## Troubleshooting

### Container Won't Start
```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs claude-code
```

### No Telemetry Data
- Ensure `USER_NAME` and `USER_EMAIL` are set
- Check container logs for OpenTelemetry errors
- Verify telemetry is enabled in the welcome message

### Export Script Fails
```bash
# Check container is running
docker-compose ps

# Run export with debug
bash -x ./export-telemetry.sh
```

## Privacy & Security

- ✅ All data stays on your local machine
- ✅ No external services or uploads
- ✅ User controls what gets exported
- ✅ No API keys or credentials in telemetry
- ✅ Can be run completely offline

## Support

This setup is designed for internal company use to analyze Claude Code + Adios MCP interactions. The exported telemetry files can be shared with AI teams for improving MCP server performance and user experience.