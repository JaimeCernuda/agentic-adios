# Agent Telemetry Collection Setup - Replication Prompt

Use this prompt to set up comprehensive telemetry collection for any AI agent system (Google Gemini CLI, OpenAI CLI, etc.).

## Primary Objective

Create a complete Docker-based telemetry collection system for [AGENT_NAME] that captures detailed conversation flow, API usage, tool interactions, and costs with the ADIOS MCP integration.

## Requirements

### 1. Docker Environment Setup
- Create a Docker container with the target agent system
- Include Node.js 18+ environment
- Set up a non-root user with sudo privileges
- Install uv (Python package manager)
- Configure workspace directory for agent operations

### 2. ADIOS MCP Integration
- Clone and install ADIOS MCP from https://github.com/iowarp/scientific-mcps
- Build the ADIOS MCP using `uv sync` in the Adios directory
- Configure the agent to use ADIOS MCP with proper connection string
- Ensure ADIOS tools are available for scientific data analysis

### 3. Telemetry Collection Infrastructure
- Set up OpenTelemetry collector with both gRPC (4317) and HTTP (4318) endpoints
- Configure telemetry data export to JSONL format
- Enable comprehensive logging with maximum verbosity
- Set up Docker Compose orchestration for agent + collector

### 4. Agent Configuration
Research and enable ALL available telemetry/logging options for the target agent:
- Full conversation logging (equivalent to `OTEL_LOG_USER_PROMPTS=1`)
- Tool usage tracking with inputs/outputs if available
- API request/response logging with maximum detail
- Cost and token usage tracking
- Session and user information capture
- Error and debug logging
- Any verbose or development mode settings

### 5. Python Analysis Package
Create a uv-managed Python package with entry point that:
- Parses the telemetry JSONL format
- Generates chronological conversation flow reports
- Shows user prompts → agent responses → tool usage → tool results
- Calculates costs, tokens, and performance metrics
- Provides detailed markdown reports with emojis for readability

### 6. File Structure
```
[agent_name]_telemetry/
├── Dockerfile                    # Agent + ADIOS MCP container
├── docker-compose.yml            # Full orchestration
├── otel-config.yaml             # OpenTelemetry configuration  
├── export-telemetry-manual.sh   # Manual export script
├── telemetry_analyzer/          # Python analysis package
│   ├── __init__.py
│   ├── analyzer.py              # Core analysis logic
│   └── cli.py                   # CLI entry point
├── telemetry-data/              # Generated telemetry files
├── workspace/                   # Agent workspace
├── pyproject.toml               # Python package config
├── README.md                    # Basic usage instructions
└── USAGE-GUIDE.md              # Comprehensive guide

```

### 7. Usage Pattern
```bash
# Start telemetry collector
docker-compose up -d otel-collector

# Run agent with full telemetry
export USER_NAME="Your Name"
export USER_EMAIL="your.email@example.com"
docker-compose run --rm [agent-name]

# Generate conversation flow report
uv run telemetry

# Export timestamped archives
./export-telemetry-manual.sh
```

### 8. Research Tasks
For the target agent system, research and implement:

#### Authentication & Setup
- How to authenticate and configure the agent
- Required API keys and environment variables
- Installation and setup procedures

#### Telemetry Configuration
- ALL available logging/telemetry environment variables
- Debug modes and verbose logging options
- Development settings that increase logging detail
- Configuration files or settings for maximum observability

#### Tool Integration
- How to install and configure MCP servers
- Tool usage tracking capabilities
- Custom tool integration methods

#### API Monitoring
- Request/response logging options
- Cost tracking and token usage monitoring
- Rate limiting and error handling

### 9. Key Environment Variables to Research
Look for equivalents to:
- `ENABLE_TELEMETRY=1`
- `LOG_USER_PROMPTS=1`
- `VERBOSE=1`
- `DEBUG=1`
- `DEVELOPMENT_MODE=1`
- `LOG_LEVEL=debug`
- `TRACE_ENABLED=1`
- `CAPTURE_TOOL_IO=1`
- `EXPORT_CONVERSATIONS=1`

### 10. Analysis Features
The telemetry analyzer should provide:
- **Conversation Flow**: Chronological user prompt → agent response → tool usage
- **Cost Analysis**: Token usage, API costs, model usage patterns
- **Tool Monitoring**: Which tools used, success/failure rates, performance
- **Session Analytics**: User activity, session duration, error rates
- **Performance Metrics**: Response times, throughput, bottlenecks

### 11. Documentation Requirements
Create comprehensive documentation including:
- Setup and installation instructions
- Environment variable configuration
- Troubleshooting guide
- Example reports and analysis
- Comparison with other agent systems

## Expected Deliverables

1. **Working Docker setup** with agent + ADIOS MCP + telemetry
2. **Comprehensive telemetry collection** with maximum available detail
3. **Python analysis package** with `uv run telemetry` command
4. **Conversation flow reports** showing complete interaction timeline
5. **Usage documentation** for replication and operation
6. **Cost and performance analytics** for optimization

## Success Criteria

- ✅ Agent runs in Docker with ADIOS MCP integration
- ✅ Full conversation content captured (if available)
- ✅ Tool usage tracked with maximum detail
- ✅ API costs and performance monitored
- ✅ Chronological conversation flow reports generated
- ✅ Easy deployment with 2-3 commands maximum
- ✅ Comprehensive documentation for replication

## Notes

- Focus on capturing the maximum amount of detail available from the target agent system
- Some agents may have more or less telemetry capability than others
- Document any limitations or missing features compared to other systems
- Ensure the setup is production-ready for research and development use
- Make the system easily adaptable for different agent platforms

This setup should provide comprehensive observability into AI agent interactions while maintaining security and privacy best practices.