"""
Command-line interface for the Claude Telemetry Analyzer.
"""

import argparse
import os
import sys
from typing import Optional

from .analyzer import TelemetryAnalyzer


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze Claude Code telemetry tar files and generate markdown reports',
        prog='claude-telemetry-analyzer'
    )
    parser.add_argument(
        'tar_file', 
        help='Path to telemetry tar.gz file'
    )
    parser.add_argument(
        '-o', '--output', 
        help='Output markdown file (default: <tar_name>_analysis.md)'
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='claude-telemetry-analyzer 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.tar_file):
        print(f"Error: File not found: {args.tar_file}")
        sys.exit(1)
    
    if not args.tar_file.endswith(('.tar.gz', '.tgz')):
        print(f"Warning: File doesn't appear to be a tar.gz file: {args.tar_file}")
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.basename(args.tar_file)
        if base_name.endswith('.tar.gz'):
            base_name = base_name[:-7]  # Remove .tar.gz
        elif base_name.endswith('.tgz'):
            base_name = base_name[:-4]  # Remove .tgz
        output_file = f"{base_name}_analysis.md"
    
    # Analyze
    print(f"🔍 Analyzing {args.tar_file}...")
    analyzer = TelemetryAnalyzer(args.tar_file)
    
    try:
        report = analyzer.analyze()
        
        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Analysis complete!")
        print(f"📄 Report saved to: {output_file}")
        
        # Print summary
        stats = analyzer.calculate_statistics()
        print(f"\n📊 Summary:")
        print(f"  - Sessions: {stats['total_sessions']}")
        print(f"  - Events: {stats['total_events']}")
        print(f"  - Queries: {stats['queries']}")
        print(f"  - MCP Interactions: {stats['mcp_interactions']}")
        print(f"  - Total Cost: ${stats['total_cost']:.4f}")
        
        if stats['total_tokens']['input'] > 0 or stats['total_tokens']['output'] > 0:
            print(f"  - Tokens: {stats['total_tokens']['input']:,} input, {stats['total_tokens']['output']:,} output")
        
        if stats['session_durations']:
            avg_duration = sum(stats['session_durations']) / len(stats['session_durations'])
            print(f"  - Avg Session Duration: {avg_duration:.1f}s")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()