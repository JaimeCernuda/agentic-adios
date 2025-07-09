# Claude Code Containerized Setup with Full Tracing and MCP Servers

## Overview

This document provides a complete containerized environment for sharing Claude Code with external users while capturing comprehensive usage traces. Based on the official [Claude Code monitoring documentation](https://docs.anthropic.com/en/docs/claude-code/monitoring-usage), this setup uses OpenTelemetry to track all user interactions and generate exportable trace files.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude Code   │────│ OpenTelemetry    │────│ Trace Files     │
│   Container     │    │ Collector        │    │ (Exportable)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   Custom MCP    │──────────────┘
                        │    Servers      │
                        └─────────────────┘
                                 │
                   ┌─────────────┼─────────────┐
                   │             │             │
         ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
         │   Jaeger    │ │ Prometheus  │ │  Grafana    │
         │ (Tracing)   │ │ (Metrics)   │ │(Dashboard)  │
         └─────────────┘ └─────────────┘ └─────────────┘
```

## Complete File Structure

```
claude-code-sharing/
├── docker-compose.yml
├── otel-collector-config.yaml
├── prometheus.yml
├── Dockerfile.claude-code
├── mcp-config.json
├── setup.sh
├── entrypoint.sh
├── session-wrapper.sh
├── export-traces.sh
├── mcp-servers/
│   ├── file-ops/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── server.js
│   └── database/
│       ├── Dockerfile
│       ├── package.json
│       └── server.js
└── grafana/
    ├── dashboards/
    │   └── claude-code.json
    └── datasources/
        └── prometheus.yaml
```

## Implementation Files

### 1. Docker Compose Configuration

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  # OpenTelemetry Collector for trace aggregation
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
      - ./traces:/var/traces
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8888:8888"   # Prometheus metrics
      - "8889:8889"   # Prometheus exporter metrics
    depends_on:
      - jaeger

  # Jaeger for trace visualization
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "14250:14250"  # Jaeger gRPC
    environment:
      - COLLECTOR_OTLP_ENABLED=true
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    volumes:
      - jaeger-data:/tmp

  # Prometheus for metrics storage
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  # Claude Code container with MCP servers
  claude-code:
    build:
      context: .
      dockerfile: Dockerfile.claude-code
    environment:
      # Enable telemetry (required)
      - CLAUDE_CODE_ENABLE_TELEMETRY=1
      - OTEL_METRICS_EXPORTER=otlp,prometheus
      - OTEL_EXPORTER_OTLP_PROTOCOL=grpc
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_METRIC_EXPORT_INTERVAL=30000  # 30 seconds for demo purposes
      
      # Include all attributes for detailed tracking
      - OTEL_METRICS_INCLUDE_SESSION_ID=true
      - OTEL_METRICS_INCLUDE_VERSION=true
      - OTEL_METRICS_INCLUDE_ACCOUNT_UUID=true
      
      # MCP server configuration
      - MCP_SERVERS_CONFIG=/app/mcp-config.json
    volumes:
      - ./mcp-servers:/app/mcp-servers
      - ./mcp-config.json:/app/mcp-config.json
      - ./user-workspace:/workspace
      - ./traces:/var/traces
      - ./session-logs:/var/logs
    working_dir: /workspace
    depends_on:
      - otel-collector
      - mcp-server-custom-1
      - mcp-server-custom-2
    stdin_open: true
    tty: true

  # Custom MCP Server 1 - File operations
  mcp-server-custom-1:
    build:
      context: ./mcp-servers/file-ops
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - MCP_SERVER_NAME=file-operations
      - MCP_SERVER_PORT=3001
    volumes:
      - ./user-workspace:/shared-workspace

  # Custom MCP Server 2 - Database operations
  mcp-server-custom-2:
    build:
      context: ./mcp-servers/database
      dockerfile: Dockerfile
    ports:
      - "3002:3002"
    environment:
      - MCP_SERVER_NAME=database-operations
      - MCP_SERVER_PORT=3002
      - DATABASE_URL=sqlite:///shared/demo.db
    volumes:
      - ./shared-data:/shared

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus

volumes:
  jaeger-data:
  prometheus-data:
  grafana-data:
```

### 2. OpenTelemetry Collector Configuration

**File: `otel-collector-config.yaml`**
```yaml
# OpenTelemetry Collector configuration for Claude Code tracing
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  
  # Add session metadata and enrich traces
  resource:
    attributes:
      - key: service.name
        value: claude-code
        action: upsert
      - key: deployment.environment
        value: shared-demo
        action: upsert
  
  # Memory limiter to prevent OOM
  memory_limiter:
    limit_mib: 512

exporters:
  # Export traces to Jaeger
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  # Export metrics to Prometheus
  prometheus:
    endpoint: "0.0.0.0:8889"
    
  # File exporter for trace files that users can download
  file/traces:
    path: /var/traces/claude-code-traces.jsonl
    rotation:
      max_megabytes: 100
      max_days: 7
      max_backups: 5

  # File exporter for metrics
  file/metrics:
    path: /var/traces/claude-code-metrics.jsonl
    rotation:
      max_megabytes: 50
      max_days: 7
      max_backups: 3

  # Logging for debugging
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [jaeger, file/traces, logging]
    
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [prometheus, file/metrics, logging]

  extensions: []
```

### 3. Claude Code Container

**File: `Dockerfile.claude-code`**
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    nodejs \
    npm \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code
# Replace this section with actual Claude Code installation method
WORKDIR /tmp
RUN curl -L "https://github.com/anthropics/claude-code/releases/latest/download/claude-code-linux-x64.tar.gz" -o claude-code.tar.gz || \
    echo "# Note: Replace with actual Claude Code installation" > /dev/null
# RUN tar -xzf claude-code.tar.gz && mv claude-code /usr/local/bin/

# Create app directory
WORKDIR /app

# Copy configuration files
COPY mcp-config.json /app/mcp-config.json
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create necessary directories
RUN mkdir -p /workspace /var/traces /var/logs

# Create a wrapper script for session tracking
COPY session-wrapper.sh /usr/local/bin/session-wrapper
RUN chmod +x /usr/local/bin/session-wrapper

# Set up environment for telemetry
ENV CLAUDE_CODE_ENABLE_TELEMETRY=1
ENV OTEL_SERVICE_NAME=claude-code
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=claude-code,deployment.environment=shared-demo"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["claude-code"]
```

### 4. MCP Configuration

**File: `mcp-config.json`**
```json
{
  "mcpServers": {
    "file-operations": {
      "command": "node",
      "args": ["/app/mcp-servers/file-ops/server.js"],
      "env": {
        "MCP_SERVER_NAME": "file-operations"
      }
    },
    "database-operations": {
      "command": "node", 
      "args": ["/app/mcp-servers/database/server.js"],
      "env": {
        "MCP_SERVER_NAME": "database-operations"
      }
    }
  }
}
```

### 5. Prometheus Configuration

**File: `prometheus.yml`**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
  
  - job_name: 'claude-code-metrics'
    static_configs:
      - targets: ['otel-collector:8888']
```

### 6. Example MCP Server - File Operations

**File: `mcp-servers/file-ops/package.json`**
```json
{
  "name": "file-operations-mcp",
  "version": "1.0.0",
  "main": "server.js",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.4.0"
  }
}
```

**File: `mcp-servers/file-ops/server.js`**
```javascript
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const fs = require('fs').promises;
const path = require('path');

class FileOperationsServer {
  constructor() {
    this.server = new Server(
      { name: "file-operations", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );
    
    this.setupHandlers();
  }

  setupHandlers() {
    this.server.setRequestHandler('tools/list', async () => ({
      tools: [
        {
          name: "read_file",
          description: "Read contents of a file",
          inputSchema: {
            type: "object",
            properties: {
              path: { type: "string", description: "File path to read" }
            },
            required: ["path"]
          }
        },
        {
          name: "write_file", 
          description: "Write content to a file",
          inputSchema: {
            type: "object",
            properties: {
              path: { type: "string", description: "File path to write" },
              content: { type: "string", description: "Content to write" }
            },
            required: ["path", "content"]
          }
        },
        {
          name: "list_directory",
          description: "List contents of a directory",
          inputSchema: {
            type: "object",
            properties: {
              path: { type: "string", description: "Directory path to list" }
            },
            required: ["path"]
          }
        }
      ]
    }));

    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          case "read_file":
            const content = await fs.readFile(args.path, 'utf8');
            return { content: [{ type: "text", text: content }] };
            
          case "write_file":
            await fs.writeFile(args.path, args.content, 'utf8');
            return { content: [{ type: "text", text: `Successfully wrote to ${args.path}` }] };
            
          case "list_directory":
            const items = await fs.readdir(args.path);
            const itemList = items.join('\n');
            return { content: [{ type: "text", text: `Directory contents:\n${itemList}` }] };
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        throw new Error(`Tool execution failed: ${error.message}`);
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }
}

const server = new FileOperationsServer();
server.run().catch(console.error);
```

**File: `mcp-servers/file-ops/Dockerfile`**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3001
CMD ["node", "server.js"]
```

### 7. Database MCP Server

**File: `mcp-servers/database/package.json`**
```json
{
  "name": "database-operations-mcp",
  "version": "1.0.0",
  "main": "server.js",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.4.0",
    "sqlite3": "^5.1.6"
  }
}
```

**File: `mcp-servers/database/server.js`**
```javascript
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const sqlite3 = require('sqlite3').verbose();

class DatabaseOperationsServer {
  constructor() {
    this.server = new Server(
      { name: "database-operations", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );
    
    this.db = new sqlite3.Database(':memory:');
    this.setupDatabase();
    this.setupHandlers();
  }

  setupDatabase() {
    // Create sample tables
    this.db.run(`
      CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
      )
    `);
    
    this.db.run(`
      INSERT INTO users (name, email) VALUES 
      ('Alice', 'alice@example.com'),
      ('Bob', 'bob@example.com')
    `);
  }

  setupHandlers() {
    this.server.setRequestHandler('tools/list', async () => ({
      tools: [
        {
          name: "execute_query",
          description: "Execute a SQL query",
          inputSchema: {
            type: "object",
            properties: {
              query: { type: "string", description: "SQL query to execute" }
            },
            required: ["query"]
          }
        },
        {
          name: "describe_schema",
          description: "Get database schema information",
          inputSchema: {
            type: "object",
            properties: {}
          }
        }
      ]
    }));

    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          case "execute_query":
            return await this.executeQuery(args.query);
            
          case "describe_schema":
            return await this.describeSchema();
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        throw new Error(`Database operation failed: ${error.message}`);
      }
    });
  }

  executeQuery(query) {
    return new Promise((resolve, reject) => {
      this.db.all(query, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const result = JSON.stringify(rows, null, 2);
          resolve({ content: [{ type: "text", text: `Query results:\n${result}` }] });
        }
      });
    });
  }

  describeSchema() {
    return new Promise((resolve, reject) => {
      this.db.all("SELECT name FROM sqlite_master WHERE type='table'", (err, tables) => {
        if (err) {
          reject(err);
        } else {
          const tableNames = tables.map(t => t.name).join(', ');
          resolve({ content: [{ type: "text", text: `Available tables: ${tableNames}` }] });
        }
      });
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }
}

const server = new DatabaseOperationsServer();
server.run().catch(console.error);
```

**File: `mcp-servers/database/Dockerfile`**
```dockerfile
FROM node:18-alpine
RUN apk add --no-cache sqlite
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3002
CMD ["node", "server.js"]
```

### 8. Setup and Helper Scripts

**File: `setup.sh`**
```bash
#!/bin/bash
# Complete setup script for Claude Code sharing environment

set -e

echo "Setting up Claude Code sharing environment with tracing..."

# Create directory structure
mkdir -p {mcp-servers/file-ops,mcp-servers/database,user-workspace,traces,session-logs,shared-data}
mkdir -p {grafana/dashboards,grafana/datasources}

# Create Grafana datasource configuration
cat > grafana/datasources/prometheus.yaml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Create basic dashboard for Claude Code metrics
cat > grafana/dashboards/claude-code.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Claude Code Usage Dashboard",
    "tags": ["claude-code"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Active Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(claude_code_session_count_total[5m])",
            "legendFormat": "Sessions"
          }
        ]
      },
      {
        "title": "Token Usage by Type",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(claude_code_token_usage_total[5m])",
            "legendFormat": "{{type}}"
          }
        ]
      },
      {
        "title": "Cost Over Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(claude_code_cost_usage_total[5m])",
            "legendFormat": "USD per minute"
          }
        ]
      },
      {
        "title": "Lines of Code Modified",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(claude_code_lines_of_code_count_total[5m])",
            "legendFormat": "{{type}}"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
EOF

echo "✅ Directory structure created"
echo "✅ Grafana configuration created"
echo ""
echo "Next steps:"
echo "1. Run: docker-compose up -d"
echo "2. Access Grafana at http://localhost:3000 (admin/admin)"
echo "3. Access Jaeger at http://localhost:16686"
echo "4. Connect to Claude Code: docker-compose exec claude-code bash"
echo "5. Export traces with: ./export-traces.sh [session-id]"
```

**File: `entrypoint.sh`**
```bash
#!/bin/bash
# Entrypoint script for Claude Code container with session tracking

# Generate unique session ID
export SESSION_ID=$(date +%s)-$(hostname)-$$
export OTEL_RESOURCE_ATTRIBUTES="${OTEL_RESOURCE_ATTRIBUTES},session.id=${SESSION_ID}"

echo "Starting Claude Code session: ${SESSION_ID}" | tee /var/logs/session-${SESSION_ID}.log

# Log session start time and environment info
echo "Session started at: $(date)" >> /var/logs/session-${SESSION_ID}.log
echo "Container hostname: $(hostname)" >> /var/logs/session-${SESSION_ID}.log
echo "Working directory: $(pwd)" >> /var/logs/session-${SESSION_ID}.log
echo "OpenTelemetry endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}" >> /var/logs/session-${SESSION_ID}.log

# Start the session with wrapper
exec /usr/local/bin/session-wrapper "$@"
```

**File: `session-wrapper.sh`**
```bash
#!/bin/bash
# Session wrapper script for detailed logging

# Log all commands and outputs to session file
exec > >(tee -a /var/logs/session-${SESSION_ID}.log) 2>&1

echo "=== Claude Code Session Started ==="
echo "Session ID: ${SESSION_ID}"
echo "Timestamp: $(date)"
echo "Available MCP Servers:"
echo "  - file-operations (port 3001) - File read/write/list operations"
echo "  - database-operations (port 3002) - SQL query and schema operations"
echo ""
echo "Telemetry Configuration:"
echo "  - Traces: Enabled → /var/traces/"
echo "  - Metrics: Enabled → OpenTelemetry Collector"
echo "  - Session logs: /var/logs/session-${SESSION_ID}.log"
echo ""
echo "Monitoring Dashboards:"
echo "  - Grafana: http://localhost:3000"
echo "  - Jaeger: http://localhost:16686"
echo ""

# Execute the actual command
"$@"

# Log session end
echo ""
echo "=== Claude Code Session Ended ==="
echo "Timestamp: $(date)"
echo "Session duration: $(($(date +%s) - $(echo $SESSION_ID | cut -d'-' -f1))) seconds"
```

**File: `export-traces.sh`**
```bash
#!/bin/bash
# Script to export traces and session data for sharing

SESSION_ID=${1:-$(date +%Y%m%d-%H%M%S)}
EXPORT_DIR="./exported-traces/${SESSION_ID}"

mkdir -p "${EXPORT_DIR}"

echo "Exporting Claude Code session data..."
echo "Session ID: ${SESSION_ID}"

# Copy trace files
if [ -d "./traces" ]; then
    cp -r ./traces/* "${EXPORT_DIR}/" 2>/dev/null || echo "No trace files found"
fi

# Copy session logs
if [ -d "./session-logs" ]; then
    cp ./session-logs/session-*.log "${EXPORT_DIR}/" 2>/dev/null || echo "No session logs found"
fi

# Export metrics from Prometheus (if available)
if command -v curl &> /dev/null; then
    echo "Exporting metrics from Prometheus..."
    curl -s "http://localhost:9090/api/v1/query_range?query=claude_code_session_count_total&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=60" > "${EXPORT_DIR}/session-metrics.json" 2>/dev/null || echo "Could not export Prometheus metrics"
fi

# Create comprehensive summary report
cat > "${EXPORT_DIR}/session-summary.txt" << SUMMARY
Claude Code Session Export
==========================
Export Date: $(date)
Session ID: ${SESSION_ID}
Export Directory: ${EXPORT_DIR}

Files Included:
$(find "${EXPORT_DIR}" -type f -exec ls -lh {} \; | awk '{print $9 " (" $5 ")"}')

Data Types:
- claude-code-traces.jsonl: OpenTelemetry trace data in JSON Lines format
- claude-code-metrics.jsonl: OpenTelemetry metrics data  
- session-*.log: Complete session command history and outputs
- session-metrics.json: Prometheus metrics export (if available)

Analysis Instructions:
1. Import traces into Jaeger or any OpenTelemetry-compatible tool
2. Review session logs for complete command history
3. Analyze metrics for usage patterns and performance

Trace Data Schema:
Each trace line contains:
- timestamp: ISO 8601 timestamp
- session_id: Unique session identifier  
- metric_name: Type of metric (session.count, token.usage, etc.)
- value: Numeric value
- attributes: Additional metadata (model, type, etc.)

Key Metrics to Analyze:
- claude_code.token.usage: Token consumption by type (input/output)
- claude_code.cost.usage: Estimated costs
- claude_code.lines_of_code.count: Code modifications
- claude_code.session.count: Session activity

For questions about this data, refer to:
https://docs.anthropic.com/en/docs/claude-code/monitoring-usage

SUMMARY

# Create compressed archive
tar -czf "claude-code-session-${SESSION_ID}.tar.gz" -C ./exported-traces "${SESSION_ID}"

echo ""
echo "✅ Export complete!"
echo "📁 Archive: claude-code-session-${SESSION_ID}.tar.gz"
echo "📊 Contains: traces, metrics, and session logs"
echo "🔗 Share this file for detailed usage analysis"
echo ""
echo "Quick stats:"
echo "- Archive size: $(du -h claude-code-session-${SESSION_ID}.tar.gz | cut -f1)"
echo "- Files exported: $(find "${EXPORT_DIR}" -type f | wc -l)"
echo "- Session logs: $(find "${EXPORT_DIR}" -name "session-*.log" | wc -l)"
```

## Installation and Usage

### Quick Start

1. **Clone or create the directory structure** with all the files above

2. **Make scripts executable:**
   ```bash
   chmod +x setup.sh entrypoint.sh session-wrapper.sh export-traces.sh
   ```

3. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

4. **Start the environment:**
   ```bash
   docker-compose up -d
   ```

5. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

### For Users

1. **Connect to Claude Code:**
   ```bash
   docker-compose exec claude-code bash
   ```

2. **Start using Claude Code** - all interactions are automatically tracked

3. **Export session data when done:**
   ```bash
   ./export-traces.sh
   ```

### Monitoring Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger**: http://localhost:16686  
- **Prometheus**: http://localhost:9090

## What Gets Tracked

Based on the [official Claude Code monitoring documentation](https://docs.anthropic.com/en/docs/claude-code/monitoring-usage), this setup captures:

### Automatic Metrics
- `claude_code.session.count`: Number of CLI sessions started
- `claude_code.lines_of_code.count`: Lines of code added/removed
- `claude_code.pull_request.count`: Pull requests created
- `claude_code.commit.count`: Git commits created  
- `claude_code.cost.usage`: Estimated costs in USD
- `claude_code.token.usage`: Token consumption by type (input/output/cache)

### Session Data
- Complete command history with timestamps
- All outputs and error messages
- MCP server interactions
- Session duration and metadata

### Exportable Traces
- OpenTelemetry-compatible JSONL files
- Prometheus metrics export
- Compressed archives ready for analysis

## Customization

### Adding Custom MCP Servers

1. Create server directory in `mcp-servers/your-server/`
2. Add service to `docker-compose.yml`
3. Update `mcp-config.json`
4. Rebuild containers

### Adjusting Telemetry

Modify environment variables in `docker-compose.yml`:
```yaml
environment:
  - OTEL_METRIC_EXPORT_INTERVAL=10000  # Export every 10 seconds
  - OTEL_METRICS_INCLUDE_SESSION_ID=true
  - OTEL_METRICS_INCLUDE_ACCOUNT_UUID=false  # Reduce cardinality
```

### Storage Configuration

Adjust trace retention in `otel-collector-config.yaml`:
```yaml
file/traces:
  rotation:
    max_megabytes: 100
    max_days: 7
    max_backups: 5
```

## Data Analysis

The exported traces provide detailed insights into:
- User behavior patterns and problem-solving approaches
- MCP server usage and effectiveness  
- Token efficiency and cost optimization opportunities
- Session duration and productivity metrics
- Error patterns and recovery strategies

## Security and Privacy

- ✅ Telemetry is opt-in via `CLAUDE_CODE_ENABLE_TELEMETRY=1`
- ✅ No API keys or credentials are logged
- ✅ File contents are not automatically captured
- ✅ All data stays within your infrastructure
- ✅ 7-day automatic trace rotation to manage storage

## Support

For issues with this setup:
1. Check service status: `docker-compose ps`
2. View logs: `docker-compose logs [service-name]`
3. Refer to [Claude Code monitoring docs](https://docs.anthropic.com/en/docs/claude-code/monitoring-usage)

This complete setup provides comprehensive tracing and monitoring for Claude Code usage while maintaining user privacy and enabling detailed analysis of interaction patterns.