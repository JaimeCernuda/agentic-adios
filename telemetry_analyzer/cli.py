#!/usr/bin/env python3
"""CLI entry point for Claude Code Telemetry Analyzer"""

import sys
import argparse
from pathlib import Path
from .analyzer import process_telemetry


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Claude Code telemetry data and generate markdown reports"
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        default="telemetry-data/claude-telemetry.jsonl",
        help="Path to telemetry JSONL file (default: telemetry-data/claude-telemetry.jsonl)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Process telemetry
    success = process_telemetry(args.file)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()