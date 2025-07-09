"""Unified telemetry analysis for AI agents (Claude Code, Gemini CLI)"""

import json
import orjson
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re

@dataclass
class TelemetryEvent:
    """Represents a single telemetry event"""
    timestamp: datetime
    event_type: str
    agent_type: str  # "claude-code" or "gemini-cli"
    span_id: Optional[str] = None
    trace_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    service_name: str = "unknown"
    operation_name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationTurn:
    """Represents a single conversation turn (prompt -> response -> tools)"""
    turn_id: int
    agent_type: str
    user_prompt: Optional[str] = None
    assistant_response: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None
    token_usage: Dict[str, int] = field(default_factory=dict)
    cost_estimate: Optional[float] = None
    errors: List[str] = field(default_factory=list)

@dataclass
class ConversationFlow:
    """Represents the complete conversation flow"""
    session_id: str
    agent_type: str
    user_name: str
    user_email: str
    start_time: datetime
    end_time: Optional[datetime] = None
    turns: List[ConversationTurn] = field(default_factory=list)
    total_tokens: Dict[str, int] = field(default_factory=dict)
    total_cost: float = 0.0
    tools_used: Dict[str, int] = field(default_factory=dict)
    error_count: int = 0

class UnifiedTelemetryAnalyzer:
    """Unified analyzer for both Claude Code and Gemini CLI telemetry"""
    
    def __init__(self, data_path: str = "./telemetry-data"):
        self.data_path = Path(data_path)
        self.events: List[TelemetryEvent] = []
        self.conversation_flows: List[ConversationFlow] = []
        
    def detect_agent_type(self, file_path: Path) -> str:
        """Detect the agent type from file name or path"""
        name = file_path.name.lower()
        parent = file_path.parent.name.lower()
        
        if "claude" in name or "claude" in parent:
            return "claude-code"
        elif "gemini" in name or "gemini" in parent:
            return "gemini-cli"
        else:
            # Try to detect from content
            try:
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    if "claude" in first_line.lower():
                        return "claude-code"
                    elif "gemini" in first_line.lower():
                        return "gemini-cli"
            except:
                pass
        
        return "unknown"
        
    def load_telemetry_data(self) -> None:
        """Load telemetry data from various formats"""
        print("🔍 Loading telemetry data...")
        
        # Look for different file patterns
        patterns = [
            "*.jsonl",
            "claude-telemetry.jsonl", 
            "traces.jsonl",
            "logs.jsonl", 
            "metrics.jsonl"
        ]
        
        files_loaded = 0
        for pattern in patterns:
            for file_path in self.data_path.glob(pattern):
                if file_path.is_file():
                    agent_type = self.detect_agent_type(file_path)
                    self._load_file(file_path, agent_type)
                    files_loaded += 1
        
        if files_loaded == 0:
            print("⚠️  No telemetry files found")
        else:
            print(f"✅ Loaded {len(self.events)} telemetry events from {files_loaded} files")
            
    def _load_file(self, file_path: Path, agent_type: str) -> None:
        """Load events from a single file"""
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            data = orjson.loads(line)
                            event = self._parse_event(data, agent_type, file_path.name)
                            if event:
                                self.events.append(event)
                        except Exception as e:
                            print(f"⚠️  Warning: Failed to parse line {line_num} in {file_path}: {e}")
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            
    def _parse_event(self, data: Dict[str, Any], agent_type: str, file_type: str) -> Optional[TelemetryEvent]:
        """Parse raw data into a TelemetryEvent"""
        try:
            # Extract timestamp
            timestamp = self._extract_timestamp(data)
            
            # Extract basic event info
            event_type = self._determine_event_type(data, file_type)
            span_id = data.get('spanId')
            trace_id = data.get('traceId')
            parent_span_id = data.get('parentSpanId')
            
            # Extract service name
            service_name = self._extract_service_name(data, agent_type)
            
            # Extract operation name
            operation_name = data.get('operationName', data.get('name'))
            
            # Extract attributes
            attributes = self._extract_attributes(data)
            
            # Extract logs
            logs = data.get('logs', [])
            
            return TelemetryEvent(
                timestamp=timestamp,
                event_type=event_type,
                agent_type=agent_type,
                span_id=span_id,
                trace_id=trace_id,
                parent_span_id=parent_span_id,
                service_name=service_name,
                operation_name=operation_name,
                attributes=attributes,
                logs=logs,
                raw_data=data
            )
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to parse event: {e}")
            return None
            
    def _extract_timestamp(self, data: Dict[str, Any]) -> datetime:
        """Extract timestamp from various formats"""
        timestamp_str = data.get('timestamp', data.get('timeUnixNano'))
        
        if isinstance(timestamp_str, str):
            try:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                # Try parsing common formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ']:
                    try:
                        return datetime.strptime(timestamp_str, fmt).replace(tzinfo=timezone.utc)
                    except:
                        continue
        elif isinstance(timestamp_str, (int, float)):
            return datetime.fromtimestamp(timestamp_str / 1e9, tz=timezone.utc)
            
        return datetime.now(timezone.utc)
        
    def _determine_event_type(self, data: Dict[str, Any], file_type: str) -> str:
        """Determine the event type from data and file type"""
        if 'traces' in file_type:
            return 'trace'
        elif 'logs' in file_type:
            return 'log'
        elif 'metrics' in file_type:
            return 'metric'
        else:
            return data.get('type', 'unknown')
            
    def _extract_service_name(self, data: Dict[str, Any], agent_type: str) -> str:
        """Extract service name from data"""
        # Check various places for service name
        service_name = data.get('serviceName')
        if service_name:
            return service_name
            
        # Check resource attributes
        resource = data.get('resource', {})
        if resource:
            attrs = resource.get('attributes', {})
            if 'service.name' in attrs:
                return attrs['service.name']
                
        # Default based on agent type
        if agent_type == "claude-code":
            return "claude-code"
        elif agent_type == "gemini-cli":
            return "gemini-cli"
        else:
            return "unknown"
            
    def _extract_attributes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract attributes from various data formats"""
        attributes = {}
        
        # Direct attributes
        if 'attributes' in data:
            attrs = data['attributes']
            if isinstance(attrs, dict):
                attributes.update(attrs)
            elif isinstance(attrs, list):
                for attr in attrs:
                    if isinstance(attr, dict) and 'key' in attr and 'value' in attr:
                        key = attr['key']
                        value = attr['value']
                        if isinstance(value, dict):
                            # Handle OpenTelemetry attribute format
                            if 'stringValue' in value:
                                attributes[key] = value['stringValue']
                            elif 'intValue' in value:
                                attributes[key] = value['intValue']
                            elif 'boolValue' in value:
                                attributes[key] = value['boolValue']
                        else:
                            attributes[key] = value
        
        # Resource attributes
        resource = data.get('resource', {})
        if resource:
            res_attrs = resource.get('attributes', {})
            if isinstance(res_attrs, dict):
                attributes.update(res_attrs)
                
        return attributes
        
    def analyze_conversation_flow(self) -> None:
        """Analyze events to reconstruct conversation flows"""
        print("🔄 Analyzing conversation flow...")
        
        # Group events by agent type and trace/session
        agent_sessions = defaultdict(lambda: defaultdict(list))
        
        for event in self.events:
            session_key = event.trace_id or event.service_name
            agent_sessions[event.agent_type][session_key].append(event)
            
        # Process each agent type and session
        for agent_type, sessions in agent_sessions.items():
            for session_id, session_events in sessions.items():
                session_events.sort(key=lambda x: x.timestamp)
                
                if not session_events:
                    continue
                    
                # Create conversation flow
                flow = ConversationFlow(
                    session_id=session_id,
                    agent_type=agent_type,
                    user_name=self._extract_user_name(session_events),
                    user_email=self._extract_user_email(session_events),
                    start_time=session_events[0].timestamp,
                    end_time=session_events[-1].timestamp
                )
                
                # Group events into conversation turns
                self._process_conversation_turns(flow, session_events)
                
                # Calculate flow statistics
                self._calculate_flow_statistics(flow)
                self.conversation_flows.append(flow)
                
        print(f"✅ Analyzed {len(self.conversation_flows)} conversation sessions")
        
    def _extract_user_name(self, events: List[TelemetryEvent]) -> str:
        """Extract user name from events"""
        for event in events:
            if 'user.name' in event.attributes:
                return event.attributes['user.name']
            if 'user_name' in event.attributes:
                return event.attributes['user_name']
        return "Unknown User"
        
    def _extract_user_email(self, events: List[TelemetryEvent]) -> str:
        """Extract user email from events"""
        for event in events:
            if 'user.email' in event.attributes:
                return event.attributes['user.email']
            if 'user_email' in event.attributes:
                return event.attributes['user_email']
        return "unknown@example.com"
        
    def _process_conversation_turns(self, flow: ConversationFlow, events: List[TelemetryEvent]) -> None:
        """Process events into conversation turns"""
        current_turn = None
        turn_counter = 0
        
        for event in events:
            if self._is_user_prompt(event):
                if current_turn:
                    flow.turns.append(current_turn)
                turn_counter += 1
                current_turn = ConversationTurn(
                    turn_id=turn_counter,
                    agent_type=flow.agent_type,
                    user_prompt=self._extract_user_prompt(event),
                    timestamp=event.timestamp
                )
                
            elif self._is_assistant_response(event) and current_turn:
                current_turn.assistant_response = self._extract_assistant_response(event)
                
            elif self._is_tool_call(event) and current_turn:
                tool_call = self._extract_tool_call(event)
                if tool_call:
                    current_turn.tool_calls.append(tool_call)
                    
            elif self._is_tool_result(event) and current_turn:
                tool_result = self._extract_tool_result(event)
                if tool_result:
                    current_turn.tool_results.append(tool_result)
                    
            # Extract token usage and costs
            if current_turn:
                self._update_token_usage(current_turn, event)
                
        # Add final turn
        if current_turn:
            flow.turns.append(current_turn)
            
    def _is_user_prompt(self, event: TelemetryEvent) -> bool:
        """Check if event represents a user prompt"""
        return (
            'user.prompt' in event.attributes or
            'prompt' in event.attributes or
            event.operation_name == 'user_prompt' or
            any('prompt' in log.get('message', '').lower() for log in event.logs)
        )
        
    def _is_assistant_response(self, event: TelemetryEvent) -> bool:
        """Check if event represents an assistant response"""
        return (
            'assistant.response' in event.attributes or
            'response' in event.attributes or
            event.operation_name == 'assistant_response' or
            any('response' in log.get('message', '').lower() for log in event.logs)
        )
        
    def _is_tool_call(self, event: TelemetryEvent) -> bool:
        """Check if event represents a tool call"""
        return (
            'tool.name' in event.attributes or
            event.operation_name == 'tool_call' or
            any('tool' in log.get('message', '').lower() for log in event.logs)
        )
        
    def _is_tool_result(self, event: TelemetryEvent) -> bool:
        """Check if event represents a tool result"""
        return (
            'tool.result' in event.attributes or
            event.operation_name == 'tool_result' or
            any('result' in log.get('message', '').lower() for log in event.logs)
        )
        
    def _extract_user_prompt(self, event: TelemetryEvent) -> Optional[str]:
        """Extract user prompt from event"""
        if 'user.prompt' in event.attributes:
            return event.attributes['user.prompt']
        elif 'prompt' in event.attributes:
            return event.attributes['prompt']
        
        # Check logs for prompt content
        for log in event.logs:
            message = log.get('message', '')
            if 'prompt' in message.lower():
                return message
                
        return None
        
    def _extract_assistant_response(self, event: TelemetryEvent) -> Optional[str]:
        """Extract assistant response from event"""
        if 'assistant.response' in event.attributes:
            return event.attributes['assistant.response']
        elif 'response' in event.attributes:
            return event.attributes['response']
            
        # Check logs for response content
        for log in event.logs:
            message = log.get('message', '')
            if 'response' in message.lower():
                return message
                
        return None
        
    def _extract_tool_call(self, event: TelemetryEvent) -> Optional[Dict[str, Any]]:
        """Extract tool call information from event"""
        tool_call = {
            'name': event.attributes.get('tool.name', 'unknown'),
            'inputs': event.attributes.get('tool.inputs', {}),
            'timestamp': event.timestamp
        }
        
        # Check logs for tool call details
        for log in event.logs:
            message = log.get('message', '')
            if 'tool' in message.lower():
                tool_call['log_message'] = message
                
        return tool_call
        
    def _extract_tool_result(self, event: TelemetryEvent) -> Optional[Dict[str, Any]]:
        """Extract tool result information from event"""
        tool_result = {
            'result': event.attributes.get('tool.result', 'unknown'),
            'success': event.attributes.get('tool.success', True),
            'timestamp': event.timestamp
        }
        
        # Check logs for tool result details
        for log in event.logs:
            message = log.get('message', '')
            if 'result' in message.lower():
                tool_result['log_message'] = message
                
        return tool_result
        
    def _update_token_usage(self, turn: ConversationTurn, event: TelemetryEvent) -> None:
        """Update token usage information for a turn"""
        if 'tokens.input' in event.attributes:
            turn.token_usage['input'] = event.attributes['tokens.input']
        if 'tokens.output' in event.attributes:
            turn.token_usage['output'] = event.attributes['tokens.output']
        if 'tokens.total' in event.attributes:
            turn.token_usage['total'] = event.attributes['tokens.total']
            
    def _calculate_flow_statistics(self, flow: ConversationFlow) -> None:
        """Calculate statistics for a conversation flow"""
        flow.total_tokens = defaultdict(int)
        flow.total_cost = 0.0
        flow.tools_used = defaultdict(int)
        flow.error_count = 0
        
        for turn in flow.turns:
            # Aggregate token usage
            for key, value in turn.token_usage.items():
                flow.total_tokens[key] += value
                
            # Count tool usage
            for tool_call in turn.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                flow.tools_used[tool_name] += 1
                
            # Count errors
            flow.error_count += len(turn.errors)
            
            # Estimate costs (simplified)
            if turn.token_usage.get('input'):
                flow.total_cost += turn.token_usage['input'] * 0.00001  # $0.01 per 1k tokens
            if turn.token_usage.get('output'):
                flow.total_cost += turn.token_usage['output'] * 0.00003  # $0.03 per 1k tokens
                
    def generate_report(self) -> str:
        """Generate a comprehensive unified markdown report"""
        if not self.conversation_flows:
            return "❌ No conversation flows found. Please run analyze_conversation_flow() first."
            
        report = []
        report.append("# 📊 AI Agent Telemetry Analysis Report")
        report.append("")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics by agent type
        agent_stats = defaultdict(lambda: {
            'sessions': 0, 'turns': 0, 'tokens': 0, 'cost': 0.0, 'tools': defaultdict(int)
        })
        
        for flow in self.conversation_flows:
            stats = agent_stats[flow.agent_type]
            stats['sessions'] += 1
            stats['turns'] += len(flow.turns)
            stats['tokens'] += flow.total_tokens.get('total', 0)
            stats['cost'] += flow.total_cost
            for tool, count in flow.tools_used.items():
                stats['tools'][tool] += count
        
        report.append("## 📈 Summary Statistics")
        report.append("")
        
        for agent_type, stats in agent_stats.items():
            agent_icon = "🤖" if agent_type == "claude-code" else "✨" if agent_type == "gemini-cli" else "🔧"
            report.append(f"### {agent_icon} {agent_type.title().replace('-', ' ')}")
            report.append(f"- **Sessions**: {stats['sessions']}")
            report.append(f"- **Conversation Turns**: {stats['turns']}")
            report.append(f"- **Total Tokens**: {stats['tokens']:,}")
            report.append(f"- **Estimated Cost**: ${stats['cost']:.4f}")
            report.append("")
        
        # Combined top tools
        all_tools = defaultdict(int)
        for stats in agent_stats.values():
            for tool, count in stats['tools'].items():
                all_tools[tool] += count
                
        if all_tools:
            report.append("## 🛠️ Top Tools Used (All Agents)")
            report.append("")
            for tool, count in sorted(all_tools.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"- **{tool}**: {count} calls")
            report.append("")
        
        # Session details by agent type
        report.append("## 💬 Session Details")
        report.append("")
        
        flows_by_agent = defaultdict(list)
        for flow in self.conversation_flows:
            flows_by_agent[flow.agent_type].append(flow)
        
        for agent_type, flows in flows_by_agent.items():
            agent_icon = "🤖" if agent_type == "claude-code" else "✨" if agent_type == "gemini-cli" else "🔧"
            report.append(f"### {agent_icon} {agent_type.title().replace('-', ' ')} Sessions")
            report.append("")
            
            for i, flow in enumerate(flows, 1):
                report.append(f"#### Session {i}: {flow.user_name}")
                report.append("")
                report.append(f"- **Session ID**: `{flow.session_id[:8]}...`")
                report.append(f"- **User**: {flow.user_name} ({flow.user_email})")
                report.append(f"- **Duration**: {flow.start_time.strftime('%H:%M:%S')} - {flow.end_time.strftime('%H:%M:%S') if flow.end_time else 'Ongoing'}")
                report.append(f"- **Turns**: {len(flow.turns)}")
                report.append(f"- **Tokens**: {flow.total_tokens.get('total', 0):,}")
                report.append(f"- **Cost**: ${flow.total_cost:.4f}")
                report.append(f"- **Tools Used**: {', '.join(flow.tools_used.keys()) if flow.tools_used else 'None'}")
                report.append("")
                
                # Show conversation flow for first few turns
                if flow.turns:
                    report.append("##### 🔄 Conversation Flow")
                    report.append("")
                    for turn in flow.turns[:3]:  # Show first 3 turns
                        report.append(f"**Turn {turn.turn_id}** ({turn.timestamp.strftime('%H:%M:%S')})")
                        
                        if turn.user_prompt:
                            prompt_preview = turn.user_prompt[:100] + "..." if len(turn.user_prompt) > 100 else turn.user_prompt
                            report.append(f"- 👤 **User**: {prompt_preview}")
                            
                        if turn.assistant_response:
                            response_preview = turn.assistant_response[:100] + "..." if len(turn.assistant_response) > 100 else turn.assistant_response
                            report.append(f"- 🤖 **Assistant**: {response_preview}")
                            
                        if turn.tool_calls:
                            report.append(f"- 🛠️ **Tools**: {', '.join(tc['name'] for tc in turn.tool_calls)}")
                            
                        if turn.token_usage:
                            report.append(f"- 📊 **Tokens**: {turn.token_usage}")
                            
                        report.append("")
                        
                    if len(flow.turns) > 3:
                        report.append(f"*... and {len(flow.turns) - 3} more turns*")
                        report.append("")
                        
                report.append("---")
                report.append("")
                
        return "\n".join(report)
        
    def export_data(self, output_file: str) -> None:
        """Export analyzed data to JSON file"""
        export_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_events': len(self.events),
            'conversation_flows': []
        }
        
        for flow in self.conversation_flows:
            flow_data = {
                'session_id': flow.session_id,
                'agent_type': flow.agent_type,
                'user_name': flow.user_name,
                'user_email': flow.user_email,
                'start_time': flow.start_time.isoformat(),
                'end_time': flow.end_time.isoformat() if flow.end_time else None,
                'total_tokens': dict(flow.total_tokens),
                'total_cost': flow.total_cost,
                'tools_used': dict(flow.tools_used),
                'error_count': flow.error_count,
                'turns': []
            }
            
            for turn in flow.turns:
                turn_data = {
                    'turn_id': turn.turn_id,
                    'agent_type': turn.agent_type,
                    'user_prompt': turn.user_prompt,
                    'assistant_response': turn.assistant_response,
                    'tool_calls': turn.tool_calls,
                    'tool_results': turn.tool_results,
                    'timestamp': turn.timestamp.isoformat() if turn.timestamp else None,
                    'duration_ms': turn.duration_ms,
                    'token_usage': turn.token_usage,
                    'cost_estimate': turn.cost_estimate,
                    'errors': turn.errors
                }
                flow_data['turns'].append(turn_data)
                
            export_data['conversation_flows'].append(flow_data)
            
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
            
        print(f"✅ Exported analysis data to {output_file}")