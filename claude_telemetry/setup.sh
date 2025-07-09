#!/bin/bash
# Complete setup script for Claude Code sharing environment

set -e

echo "Setting up Claude Code sharing environment with tracing..."

# Create directory structure
mkdir -p user-workspace traces session-logs exported-traces
mkdir -p grafana/dashboards grafana/datasources

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
        ],
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "title": "Token Usage by Type",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(claude_code_token_usage_total[5m])",
            "legendFormat": "{{type}}"
          }
        ],
        "gridPos": {"h": 8, "w": 9, "x": 6, "y": 0}
      },
      {
        "title": "Cost Over Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(claude_code_cost_usage_total[5m])",
            "legendFormat": "USD per minute"
          }
        ],
        "gridPos": {"h": 8, "w": 9, "x": 15, "y": 0}
      },
      {
        "title": "Lines of Code Modified",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(claude_code_lines_of_code_count_total[5m])",
            "legendFormat": "{{type}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "title": "Total Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "claude_code_session_count_total",
            "legendFormat": "Total"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 8}
      },
      {
        "title": "Total Cost",
        "type": "stat",
        "targets": [
          {
            "expr": "claude_code_cost_usage_total",
            "legendFormat": "USD"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s",
    "version": 1
  }
}
EOF

# Create dashboard provisioning config
cat > grafana/dashboards/dashboard.yaml << 'EOF'
apiVersion: 1

providers:
  - name: 'claude-code'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

# Make scripts executable
chmod +x entrypoint.sh session-wrapper.sh export-traces.sh

echo "✅ Directory structure created"
echo "✅ Grafana configuration created"
echo "✅ Scripts made executable"
echo ""
echo "🚀 Quick Start:"
echo "===================================="
echo "1. Start the environment:"
echo "   docker-compose up -d"
echo ""
echo "2. Wait for services to start (about 30 seconds)"
echo ""
echo "3. Claude Code will automatically start with the --dangerous flag"
echo "   The interface will be available in the terminal"
echo ""
echo "4. Access monitoring dashboards:"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo "   - Jaeger: http://localhost:16686"
echo ""
echo "5. To export session data after use:"
echo "   ./export-traces.sh"
echo ""
echo "6. To stop the environment:"
echo "   docker-compose down"
echo ""
echo "📋 Notes:"
echo "- All telemetry is automatically collected"
echo "- Session logs are stored in ./session-logs/"
echo "- Traces are stored in ./traces/"
echo "- Exported data will be in ./exported-traces/"
echo "- The Adios MCP server is pre-configured"