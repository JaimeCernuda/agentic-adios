#!/usr/bin/env python3
"""
Claude Code Telemetry Analyzer
Analyzes telemetry data from claude-telemetry.jsonl and generates a markdown report.
"""

import json
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

def parse_jsonl(file_path):
    """Parse JSONL file and extract telemetry events."""
    events = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                # Extract log records from OpenTelemetry format
                if 'resourceLogs' in data:
                    for resource_log in data['resourceLogs']:
                        for scope_log in resource_log.get('scopeLogs', []):
                            for log_record in scope_log.get('logRecords', []):
                                events.append(parse_log_record(log_record))
                else:
                    # Direct event format
                    events.append(data)
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {e}")
                continue
    
    return [e for e in events if e]  # Filter out None values

def parse_log_record(log_record):
    """Parse OpenTelemetry log record into event format."""
    if not log_record.get('attributes'):
        return None
    
    # Convert attributes array to dict
    attributes = {}
    for attr in log_record['attributes']:
        key = attr['key']
        value = attr['value']
        # Extract string value from different value types
        if isinstance(value, dict):
            if 'stringValue' in value:
                attributes[key] = value['stringValue']
            elif 'intValue' in value:
                attributes[key] = int(value['intValue'])
            elif 'doubleValue' in value:
                attributes[key] = float(value['doubleValue'])
        else:
            attributes[key] = value
    
    # Get event name from body or attributes
    event_name = log_record.get('body', {}).get('stringValue', '')
    if not event_name and 'event.name' in attributes:
        event_name = attributes['event.name']
    
    return {
        'timestamp': log_record.get('timeUnixNano', log_record.get('observedTimeUnixNano')),
        'event_name': event_name,
        'attributes': attributes
    }

def format_timestamp(timestamp):
    """Format timestamp to readable format."""
    if isinstance(timestamp, str):
        try:
            # Try parsing ISO format first
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return timestamp
    elif isinstance(timestamp, (int, float)):
        # Convert nanoseconds to seconds
        if timestamp > 1e15:  # Nanoseconds
            timestamp = timestamp / 1e9
        elif timestamp > 1e12:  # Microseconds
            timestamp = timestamp / 1e6
        
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    return str(timestamp)

def get_timestamp_for_sorting(event):
    """Get timestamp for sorting, handling mixed string/numeric types."""
    ts = event.get('timestamp', 0)
    if isinstance(ts, str):
        # Try to parse ISO format timestamp to a numeric value
        try:
            from dateutil import parser
            dt = parser.parse(ts)
            return dt.timestamp()
        except:
            return 0
    elif isinstance(ts, (int, float)):
        # If it's already numeric, return as is
        return ts
    return 0

def analyze_events(events):
    """Analyze events and generate statistics."""
    if not events:
        return {}
    
    # Sort events by timestamp (handle mixed types)
    events.sort(key=get_timestamp_for_sorting)
    
    # Group events by type
    event_types = defaultdict(list)
    for event in events:
        event_name = event.get('event_name', 'unknown')
        event_types[event_name].append(event)
    
    # Extract session info
    session_info = {}
    user_info = {}
    
    for event in events:
        attrs = event.get('attributes', {})
        
        # Collect user info
        if 'user.email' in attrs:
            user_info['email'] = attrs['user.email']
        if 'user.id' in attrs:
            user_info['id'] = attrs['user.id']
        if 'user.account_uuid' in attrs:
            user_info['account_uuid'] = attrs['user.account_uuid']
        
        # Collect session info
        if 'session.id' in attrs:
            session_info['session_id'] = attrs['session.id']
        if 'organization.id' in attrs:
            session_info['organization_id'] = attrs['organization.id']
        if 'terminal.type' in attrs:
            session_info['terminal_type'] = attrs['terminal.type']
    
    # Calculate statistics
    stats = {
        'total_events': len(events),
        'event_types': dict(Counter(event.get('event_name', 'unknown') for event in events)),
        'session_info': session_info,
        'user_info': user_info,
        'timespan': {
            'start': format_timestamp(events[0].get('timestamp')) if events else None,
            'end': format_timestamp(events[-1].get('timestamp')) if events else None
        }
    }
    
    # API call statistics
    api_events = event_types.get('claude_code.api_request', [])
    if api_events:
        total_cost = sum(float(e.get('attributes', {}).get('cost_usd', 0)) for e in api_events)
        total_input_tokens = sum(int(e.get('attributes', {}).get('input_tokens', 0)) for e in api_events)
        total_output_tokens = sum(int(e.get('attributes', {}).get('output_tokens', 0)) for e in api_events)
        total_duration = sum(int(e.get('attributes', {}).get('duration_ms', 0)) for e in api_events)
        
        models_used = Counter(e.get('attributes', {}).get('model', 'unknown') for e in api_events)
        
        stats['api_stats'] = {
            'total_calls': len(api_events),
            'total_cost_usd': total_cost,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_duration_ms': total_duration,
            'models_used': dict(models_used)
        }
    
    return stats, event_types

def generate_markdown_report(stats, event_types, output_file):
    """Generate comprehensive markdown report."""
    
    report = []
    report.append("# Claude Code Telemetry Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")
    
    # Generate conversation flow first
    report.append("## Conversation Flow")
    report.append("")
    report.append("This section shows the chronological flow of the conversation.")
    report.append("")
    
    # Collect all events with timestamps
    all_events = []
    for event_type, events in event_types.items():
        for event in events:
            event['_type'] = event_type
            all_events.append(event)
    
    # Sort by timestamp
    all_events.sort(key=get_timestamp_for_sorting)
    
    # Generate flow
    for event in all_events:
        event_type = event.get('_type', 'unknown')
        attrs = event.get('attributes', {})
        timestamp = format_timestamp(event.get('timestamp'))
        
        if 'user_prompt' in event_type:
            prompt = attrs.get('prompt', '<REDACTED>')
            prompt_length = attrs.get('prompt_length', 'unknown')
            report.append(f"### 🧑 User Prompt [{timestamp}]")
            report.append(f"**Length:** {prompt_length} characters")
            if prompt and prompt != '<REDACTED>' and len(prompt.strip()) > 0:
                report.append(f"**Content:**")
                report.append(f"```")
                report.append(prompt)
                report.append(f"```")
            else:
                report.append("*Content redacted for privacy (set OTEL_LOG_USER_PROMPTS=1 to show)*")
            report.append("")
            
        elif 'api_request' in event_type:
            model = attrs.get('model', 'unknown')
            input_tokens = attrs.get('input_tokens', 0)
            output_tokens = attrs.get('output_tokens', 0)
            cost = attrs.get('cost_usd', 0)
            duration = attrs.get('duration_ms', 0)
            
            report.append(f"### 🤖 Claude Response [{timestamp}]")
            report.append(f"**Model:** {model}")
            report.append(f"**Tokens:** {input_tokens} in / {output_tokens} out")
            report.append(f"**Cost:** ${cost} | **Duration:** {duration}ms")
            report.append("")
            
        elif 'tool_decision' in event_type:
            tool_name = attrs.get('tool_name', attrs.get('tool.name', 'unknown'))
            decision = attrs.get('decision', 'unknown')
            source = attrs.get('source', 'unknown')
            report.append(f"### 🔧 Tool Decision: {tool_name} [{timestamp}]")
            report.append(f"**Decision:** {decision}")
            report.append(f"**Source:** {source}")
            report.append("")
            
        elif 'tool_use' in event_type:
            tool_name = attrs.get('tool_name', attrs.get('tool.name', 'unknown'))
            tool_input = attrs.get('tool_input', attrs.get('tool.input', 'N/A'))
            tool_status = attrs.get('tool_status', attrs.get('tool.status', 'N/A'))
            
            report.append(f"### 🔨 Tool Use: {tool_name} [{timestamp}]")
            report.append(f"**Status:** {tool_status}")
            if tool_input != 'N/A' and len(str(tool_input)) > 0:
                report.append(f"**Input:**")
                report.append(f"```json")
                # Try to pretty print JSON if possible
                try:
                    import json
                    if isinstance(tool_input, str):
                        tool_input_json = json.loads(tool_input)
                        report.append(json.dumps(tool_input_json, indent=2))
                    else:
                        report.append(str(tool_input))
                except:
                    report.append(str(tool_input))
                report.append(f"```")
            report.append("")
            
        elif 'tool_result' in event_type:
            tool_name = attrs.get('tool_name', attrs.get('tool.name', 'unknown'))
            tool_result = attrs.get('tool_result', attrs.get('tool.result', 'N/A'))
            tool_error = attrs.get('tool_error', attrs.get('tool.error', None))
            
            report.append(f"### 📤 Tool Result: {tool_name} [{timestamp}]")
            if tool_error:
                report.append(f"**Error:** {tool_error}")
            if tool_result != 'N/A' and len(str(tool_result)) > 0:
                report.append(f"**Result:**")
                report.append(f"```")
                # Truncate very long results
                result_str = str(tool_result)
                if len(result_str) > 1000:
                    report.append(result_str[:1000] + "\n... [truncated]")
                else:
                    report.append(result_str)
                report.append(f"```")
            report.append("")
            
        elif 'mcp_server' in event_type:
            server_name = attrs.get('mcp_server_name', attrs.get('mcp.server_name', 'unknown'))
            method = attrs.get('mcp_method', attrs.get('mcp.method', 'unknown'))
            status = attrs.get('mcp_status', attrs.get('mcp.status', 'unknown'))
            
            report.append(f"### 🔌 MCP Server: {server_name} [{timestamp}]")
            report.append(f"**Method:** {method}")
            report.append(f"**Status:** {status}")
            report.append("")
    
    report.append("---")
    report.append("")
    
    # Session Overview
    report.append("## Session Overview")
    report.append("")
    
    if stats.get('session_info'):
        si = stats['session_info']
        report.append(f"- **Session ID:** `{si.get('session_id', 'N/A')}`")
        report.append(f"- **Organization ID:** `{si.get('organization_id', 'N/A')}`")
        report.append(f"- **Terminal Type:** `{si.get('terminal_type', 'N/A')}`")
        report.append("")
    
    if stats.get('user_info'):
        ui = stats['user_info']
        report.append(f"- **User Email:** `{ui.get('email', 'N/A')}`")
        report.append(f"- **User ID:** `{ui.get('id', 'N/A')}`")
        report.append(f"- **Account UUID:** `{ui.get('account_uuid', 'N/A')}`")
        report.append("")
    
    if stats.get('timespan'):
        ts = stats['timespan']
        report.append(f"- **Session Start:** {ts.get('start', 'N/A')}")
        report.append(f"- **Session End:** {ts.get('end', 'N/A')}")
        report.append("")
    
    # Statistics Summary
    report.append("## Statistics Summary")
    report.append("")
    report.append(f"- **Total Events:** {stats.get('total_events', 0)}")
    report.append("")
    
    # Event Types
    report.append("### Event Types")
    report.append("")
    for event_type, count in stats.get('event_types', {}).items():
        report.append(f"- **{event_type}:** {count}")
    report.append("")
    
    # API Call Statistics
    if 'api_stats' in stats:
        api_stats = stats['api_stats']
        report.append("### API Call Statistics")
        report.append("")
        report.append(f"- **Total API Calls:** {api_stats.get('total_calls', 0)}")
        report.append(f"- **Total Cost:** ${api_stats.get('total_cost_usd', 0):.6f}")
        report.append(f"- **Total Input Tokens:** {api_stats.get('total_input_tokens', 0):,}")
        report.append(f"- **Total Output Tokens:** {api_stats.get('total_output_tokens', 0):,}")
        report.append(f"- **Total Duration:** {api_stats.get('total_duration_ms', 0):,} ms")
        report.append("")
        
        if api_stats.get('models_used'):
            report.append("**Models Used:**")
            for model, count in api_stats['models_used'].items():
                report.append(f"- {model}: {count} calls")
            report.append("")
    
    # Detailed Event Analysis
    report.append("## Detailed Event Analysis")
    report.append("")
    
    # Process each event type
    for event_type, events in event_types.items():
        if not events:
            continue
            
        report.append(f"### {event_type} ({len(events)} events)")
        report.append("")
        
        if event_type == 'claude_code.api_request':
            report.append("| Time | Model | Input Tokens | Output Tokens | Cost | Duration |")
            report.append("|------|-------|--------------|---------------|------|----------|")
            
            for event in events:
                attrs = event.get('attributes', {})
                timestamp = format_timestamp(event.get('timestamp'))
                model = attrs.get('model', 'N/A')
                input_tokens = attrs.get('input_tokens', 0)
                output_tokens = attrs.get('output_tokens', 0)
                cost = attrs.get('cost_usd', 0)
                duration = attrs.get('duration_ms', 0)
                
                report.append(f"| {timestamp} | {model} | {input_tokens} | {output_tokens} | ${cost} | {duration}ms |")
        
        elif event_type == 'claude_code.tool_use':
            report.append("| Time | Tool | Input | Status |")
            report.append("|------|------|-------|--------|")
            
            for event in events:
                attrs = event.get('attributes', {})
                timestamp = format_timestamp(event.get('timestamp'))
                tool_name = attrs.get('tool.name', 'N/A')
                tool_input = attrs.get('tool.input', 'N/A')
                status = attrs.get('tool.status', 'N/A')
                
                # Truncate long inputs
                if len(str(tool_input)) > 100:
                    tool_input = str(tool_input)[:100] + "..."
                
                report.append(f"| {timestamp} | {tool_name} | {tool_input} | {status} |")
        
        elif event_type == 'claude_code.mcp_server_interaction':
            report.append("| Time | Server | Method | Status |")
            report.append("|------|--------|--------|--------|")
            
            for event in events:
                attrs = event.get('attributes', {})
                timestamp = format_timestamp(event.get('timestamp'))
                server_name = attrs.get('mcp.server_name', 'N/A')
                method = attrs.get('mcp.method', 'N/A')
                status = attrs.get('mcp.status', 'N/A')
                
                report.append(f"| {timestamp} | {server_name} | {method} | {status} |")
        
        else:
            # Generic event table
            report.append("| Time | Event Details |")
            report.append("|------|---------------|")
            
            for event in events:
                timestamp = format_timestamp(event.get('timestamp'))
                attrs = event.get('attributes', {})
                
                # Create summary of key attributes
                key_attrs = []
                for key, value in attrs.items():
                    if key not in ['user.id', 'session.id', 'organization.id', 'user.email', 'user.account_uuid']:
                        key_attrs.append(f"{key}: {value}")
                
                details = ", ".join(key_attrs[:3])  # Limit to first 3 attributes
                if len(key_attrs) > 3:
                    details += "..."
                
                report.append(f"| {timestamp} | {details} |")
        
        report.append("")
    
    # Write report to file
    with open(output_file, 'w') as f:
        f.write("\n".join(report))
    
    return "\n".join(report)

def process_telemetry(input_file):
    """Process telemetry file and generate report."""
    if not Path(input_file).exists():
        print(f"Error: File {input_file} does not exist")
        return False
    
    # Parse events
    print(f"Parsing telemetry data from {input_file}...")
    events = parse_jsonl(input_file)
    
    if not events:
        print("No events found in telemetry file")
        return False
    
    print(f"Found {len(events)} events")
    
    # Analyze events
    stats, event_types = analyze_events(events)
    
    # Generate report
    output_file = input_file.replace('.jsonl', '_report.md')
    report = generate_markdown_report(stats, event_types, output_file)
    
    print(f"Report generated: {output_file}")
    print("\nNote: User prompts are redacted by Claude Code for privacy.")
    print("To see full conversation content, check Claude Code's own logs.")
    
    return True