"""
Core telemetry analysis functionality.
"""

import json
import tarfile
import os
import tempfile
import shutil
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional


class TelemetryAnalyzer:
    """Analyzes Claude Code telemetry tar files and generates reports."""
    
    def __init__(self, tar_path: str):
        self.tar_path = tar_path
        self.temp_dir: Optional[str] = None
        self.sessions: Dict[str, Dict] = {}
        self.telemetry_events: List[Dict] = []
        self.interactions: List[Dict] = []
        self.session_logs: Dict[str, str] = {}
        
    def extract_tar(self) -> str:
        """Extract tar file to temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        print(f"Extracting {self.tar_path}...")
        
        with tarfile.open(self.tar_path, 'r:gz') as tar:
            tar.extractall(self.temp_dir)
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir(self.temp_dir) 
                         if os.path.isdir(os.path.join(self.temp_dir, d))]
        if not extracted_dirs:
            raise ValueError("No directory found in tar file")
        
        return os.path.join(self.temp_dir, extracted_dirs[0])
    
    def parse_jsonl(self, file_path: str) -> List[Dict]:
        """Parse JSONL file and return list of objects."""
        events = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(f"Warning: Failed to parse line in {file_path}: {e}")
        return events
    
    def load_data(self, base_dir: str) -> None:
        """Load all telemetry data from extracted directory."""
        print("Loading telemetry data...")
        
        # Load main telemetry events
        telemetry_file = os.path.join(base_dir, 'claude-telemetry.jsonl')
        if os.path.exists(telemetry_file):
            self.telemetry_events = self.parse_jsonl(telemetry_file)
        
        # Load metrics
        metrics_file = os.path.join(base_dir, 'claude-metrics.jsonl')
        if os.path.exists(metrics_file):
            self.telemetry_events.extend(self.parse_jsonl(metrics_file))
        
        # Load traces
        traces_file = os.path.join(base_dir, 'claude-traces.jsonl')
        if os.path.exists(traces_file):
            self.telemetry_events.extend(self.parse_jsonl(traces_file))
        
        # Load session data
        sessions_dir = os.path.join(base_dir, 'sessions')
        if os.path.exists(sessions_dir):
            for session_dir in os.listdir(sessions_dir):
                session_path = os.path.join(sessions_dir, session_dir)
                if os.path.isdir(session_path):
                    self.load_session_data(session_path, session_dir)
    
    def load_session_data(self, session_path: str, session_id: str) -> None:
        """Load data for a specific session."""
        # Load session info
        info_file = os.path.join(session_path, 'session-info.json')
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                self.sessions[session_id] = json.load(f)
        
        # Load interactions
        interactions_file = os.path.join(session_path, 'interactions.jsonl')
        if os.path.exists(interactions_file):
            interactions = self.parse_jsonl(interactions_file)
            for interaction in interactions:
                interaction['session_id'] = session_id
                self.interactions.append(interaction)
        
        # Load session log
        log_file = os.path.join(session_path, 'session.log')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                self.session_logs[session_id] = f.read()
    
    def analyze_conversations(self) -> Dict[str, List[Dict]]:
        """Analyze and reconstruct conversations from telemetry data."""
        conversations = defaultdict(list)
        
        # Group events by session
        for event in self.telemetry_events:
            session_id = event.get('attributes', {}).get('session_id', 'unknown')
            conversations[session_id].append(event)
        
        # Add interactions
        for interaction in self.interactions:
            session_id = interaction.get('session_id', 'unknown')
            conversations[session_id].append(interaction)
        
        # Sort events by timestamp
        for session_id in conversations:
            conversations[session_id].sort(key=lambda x: x.get('timestamp', ''))
        
        return conversations
    
    def format_event(self, event: Dict) -> str:
        """Format a single event for markdown output."""
        event_type = event.get('event', event.get('metric', 'unknown'))
        
        if event_type == 'ai_activity':
            data = event.get('data', '')
            if 'Processing query:' in str(data):
                query = str(data).replace('Processing query: ', '')
                return f"**🧑 User Query**: {query}"
            elif 'Claude:' in str(data):
                response = str(data).replace('Claude: ', '')
                return f"**🤖 Claude Response**: {response}"
            elif 'MCP:' in str(data):
                mcp_action = str(data).replace('MCP: ', '')
                return f"**🔧 MCP Tool Call**: {mcp_action}"
            elif 'Tool use:' in str(data):
                tool_action = str(data).replace('Tool use: ', '')
                return f"**🛠️ Tool Usage**: {tool_action}"
            else:
                return f"**📋 AI Activity**: {data}"
        
        elif event_type == 'claude_code.token.usage':
            token_type = event.get('attributes', {}).get('type', 'unknown')
            value = event.get('value', 0)
            return f"**📊 Token Usage**: {value} {token_type} tokens"
        
        elif event_type == 'claude_code.cost.usage':
            value = event.get('value', 0)
            currency = event.get('attributes', {}).get('currency', 'USD')
            return f"**💰 Cost**: {value:.4f} {currency}"
        
        elif event_type == 'claude_code.lines_of_code.count':
            code_type = event.get('attributes', {}).get('type', 'unknown')
            value = event.get('value', 0)
            return f"**📝 Code Lines**: {value} lines {code_type}"
        
        elif event_type == 'mcp.interaction':
            server = event.get('attributes', {}).get('server', 'unknown')
            command = event.get('attributes', {}).get('command', 'unknown')
            return f"**🔧 MCP Interaction**: `{command}` on {server} server"
        
        elif event_type == 'session_start':
            user = event.get('data', {}).get('user', 'Unknown')
            email = event.get('data', {}).get('email', '')
            return f"**🚀 Session Started**: {user} ({email})"
        
        elif event_type == 'session_end':
            exit_code = event.get('data', {}).get('exit_code', 0)
            return f"**🏁 Session Ended**: Exit code {exit_code}"
        
        else:
            value = event.get('data', event.get('value', ''))
            return f"**📌 {event_type}**: {json.dumps(value) if not isinstance(value, str) else value}"
    
    def calculate_statistics(self) -> Dict:
        """Calculate statistics from telemetry data."""
        stats = {
            'total_sessions': len(self.sessions),
            'total_events': len(self.telemetry_events) + len(self.interactions),
            'total_tokens': {'input': 0, 'output': 0, 'cache': 0},
            'total_cost': 0.0,
            'mcp_interactions': 0,
            'queries': 0,
            'code_lines': {'added': 0, 'removed': 0, 'modified': 0},
            'session_durations': []
        }
        
        # Calculate token usage and costs
        for event in self.telemetry_events:
            if event.get('metric') == 'claude_code.token.usage':
                token_type = event.get('attributes', {}).get('type', 'unknown')
                value = event.get('value', 0)
                if token_type in stats['total_tokens']:
                    stats['total_tokens'][token_type] += value
            
            elif event.get('metric') == 'claude_code.cost.usage':
                stats['total_cost'] += event.get('value', 0)
            
            elif event.get('metric') == 'mcp.interaction':
                stats['mcp_interactions'] += 1
            
            elif event.get('metric') == 'claude_code.lines_of_code.count':
                code_type = event.get('attributes', {}).get('type', 'unknown')
                value = event.get('value', 0)
                if code_type in stats['code_lines']:
                    stats['code_lines'][code_type] += value
        
        # Count queries
        for interaction in self.interactions:
            if 'Processing query:' in str(interaction.get('data', '')):
                stats['queries'] += 1
        
        # Calculate session durations
        for session_id, session_info in self.sessions.items():
            start_time = session_info.get('start_time')
            end_time = session_info.get('end_time')
            if start_time and end_time:
                try:
                    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()
                    stats['session_durations'].append(duration)
                except Exception as e:
                    print(f"Warning: Failed to parse session duration: {e}")
        
        return stats
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report."""
        report = []
        
        # Header
        report.append("# Claude Code Telemetry Analysis Report")
        report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Source**: `{os.path.basename(self.tar_path)}`")
        report.append("\n---\n")
        
        # Executive Summary
        stats = self.calculate_statistics()
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total Sessions**: {stats['total_sessions']}")
        report.append(f"- **Total Events**: {stats['total_events']}")
        report.append(f"- **User Queries**: {stats['queries']}")
        report.append(f"- **MCP Interactions**: {stats['mcp_interactions']}")
        report.append(f"- **Total Cost**: ${stats['total_cost']:.4f}")
        report.append("")
        
        # Token Usage
        report.append("### Token Usage")
        report.append("")
        report.append("| Type | Tokens |")
        report.append("|------|--------|")
        for token_type, count in stats['total_tokens'].items():
            if count > 0:
                report.append(f"| {token_type.capitalize()} | {count:,} |")
        report.append("")
        
        # Code Statistics
        if any(stats['code_lines'].values()):
            report.append("### Code Modifications")
            report.append("")
            report.append("| Type | Lines |")
            report.append("|------|-------|")
            for code_type, count in stats['code_lines'].items():
                if count > 0:
                    report.append(f"| {code_type.capitalize()} | {count} |")
            report.append("")
        
        # Session Durations
        if stats['session_durations']:
            avg_duration = sum(stats['session_durations']) / len(stats['session_durations'])
            max_duration = max(stats['session_durations'])
            min_duration = min(stats['session_durations'])
            report.append(f"**Average Session Duration**: {avg_duration:.1f} seconds")
            report.append(f"**Longest Session**: {max_duration:.1f} seconds")
            report.append(f"**Shortest Session**: {min_duration:.1f} seconds")
            report.append("")
        
        report.append("---\n")
        
        # Session Details
        report.append("## Session Details")
        report.append("")
        
        conversations = self.analyze_conversations()
        
        for session_id, session_info in self.sessions.items():
            report.append(f"### Session: {session_id}")
            report.append("")
            report.append(f"- **User**: {session_info.get('user_name', 'Unknown')} ({session_info.get('user_email', '')})")
            report.append(f"- **Start Time**: {session_info.get('start_time', 'Unknown')}")
            report.append(f"- **End Time**: {session_info.get('end_time', 'Unknown')}")
            report.append(f"- **MCP Servers**: {', '.join(session_info.get('mcp_servers', []))}")
            report.append("")
            
            # Conversation Flow
            report.append("#### Conversation Flow")
            report.append("")
            
            session_events = conversations.get(session_id, [])
            if session_events:
                for event in session_events:
                    formatted = self.format_event(event)
                    if formatted:
                        report.append(f"- {formatted}")
                report.append("")
            
            # Session Log Excerpt
            if session_id in self.session_logs:
                report.append("#### Session Log Excerpt")
                report.append("")
                report.append("```")
                log_lines = self.session_logs[session_id].split('\n')
                # Show first 20 and last 10 lines for long logs
                if len(log_lines) > 30:
                    for line in log_lines[:20]:
                        report.append(line)
                    report.append("... [truncated] ...")
                    for line in log_lines[-10:]:
                        report.append(line)
                else:
                    report.append(self.session_logs[session_id])
                report.append("```")
                report.append("")
            
            report.append("---\n")
        
        # MCP Server Analysis
        report.append("## MCP Server Analysis")
        report.append("")
        
        mcp_commands = defaultdict(int)
        mcp_servers = defaultdict(int)
        
        for event in self.telemetry_events:
            if event.get('metric') == 'mcp.interaction':
                command = event.get('attributes', {}).get('command', 'unknown')
                server = event.get('attributes', {}).get('server', 'unknown')
                mcp_commands[command] += 1
                mcp_servers[server] += 1
        
        if mcp_commands:
            report.append("### Command Usage")
            report.append("")
            report.append("| Command | Count |")
            report.append("|---------|-------|")
            for command, count in sorted(mcp_commands.items(), key=lambda x: x[1], reverse=True):
                report.append(f"| `{command}` | {count} |")
            report.append("")
        
        if mcp_servers:
            report.append("### Server Usage")
            report.append("")
            report.append("| Server | Interactions |")
            report.append("|--------|--------------|")
            for server, count in sorted(mcp_servers.items(), key=lambda x: x[1], reverse=True):
                report.append(f"| {server} | {count} |")
            report.append("")
        
        # Raw Telemetry Events
        report.append("## Raw Telemetry Events")
        report.append("")
        report.append("<details>")
        report.append("<summary>Click to expand raw telemetry data</summary>")
        report.append("")
        report.append("```json")
        for event in self.telemetry_events[:20]:  # Show first 20 events
            report.append(json.dumps(event, indent=2))
        if len(self.telemetry_events) > 20:
            report.append(f"... and {len(self.telemetry_events) - 20} more events")
        report.append("```")
        report.append("")
        report.append("</details>")
        
        return '\n'.join(report)
    
    def cleanup(self) -> None:
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def analyze(self) -> str:
        """Main analysis method."""
        try:
            # Extract tar file
            base_dir = self.extract_tar()
            
            # Load all data
            self.load_data(base_dir)
            
            # Generate report
            report = self.generate_markdown_report()
            
            return report
        finally:
            self.cleanup()