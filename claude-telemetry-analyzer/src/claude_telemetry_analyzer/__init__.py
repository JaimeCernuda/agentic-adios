"""
Claude Telemetry Analyzer

A tool for analyzing Claude Code telemetry tar files and generating 
comprehensive markdown reports with conversation flows, usage statistics,
and MCP server interaction analysis.
"""

from .analyzer import TelemetryAnalyzer
from .cli import main

__version__ = "0.1.0"
__all__ = ["TelemetryAnalyzer", "main"]