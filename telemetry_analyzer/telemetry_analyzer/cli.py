#!/usr/bin/env python3
"""CLI entry point for AI Agent Telemetry Analyzer"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from .unified_analyzer import UnifiedTelemetryAnalyzer

console = Console()

@click.command()
@click.option(
    "--data-path",
    "-d",
    default="./telemetry-data",
    help="Path to telemetry data directory",
    type=click.Path(file_okay=False, dir_okay=True)
)
@click.option(
    "--output",
    "-o",
    default="telemetry-report.md",
    help="Output file for the report",
    type=click.Path(file_okay=True, dir_okay=False)
)
@click.option(
    "--export",
    "-e",
    help="Export analyzed data to JSON file",
    type=click.Path(file_okay=True, dir_okay=False)
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--no-display",
    is_flag=True,
    help="Don't display report in terminal, just save to file"
)
def main(data_path: str, output: str, export: str, verbose: bool, no_display: bool):
    """
    🔍 Analyze AI agent telemetry data and generate conversation flow reports.
    
    This tool processes telemetry data from AI agents (Claude Code, Gemini CLI) and generates
    comprehensive reports showing conversation flows, tool usage, costs, and performance metrics.
    """
    console.print("🚀 [bold blue]AI Agent Telemetry Analyzer[/bold blue]")
    console.print()
    
    # Initialize analyzer
    analyzer = UnifiedTelemetryAnalyzer(data_path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        # Load telemetry data
        task1 = progress.add_task("Loading telemetry data...", total=None)
        try:
            analyzer.load_telemetry_data()
            progress.update(task1, description="✅ Telemetry data loaded")
        except Exception as e:
            console.print(f"❌ [red]Error loading telemetry data: {e}[/red]")
            return
            
        # Analyze conversation flow
        task2 = progress.add_task("Analyzing conversation flow...", total=None)
        try:
            analyzer.analyze_conversation_flow()
            progress.update(task2, description="✅ Conversation flow analyzed")
        except Exception as e:
            console.print(f"❌ [red]Error analyzing conversation flow: {e}[/red]")
            return
            
        # Generate report
        task3 = progress.add_task("Generating report...", total=None)
        try:
            report = analyzer.generate_report()
            progress.update(task3, description="✅ Report generated")
        except Exception as e:
            console.print(f"❌ [red]Error generating report: {e}[/red]")
            return
    
    # Display report statistics
    console.print(f"📊 [bold green]Analysis Complete![/bold green]")
    console.print(f"   • Events processed: {len(analyzer.events)}")
    console.print(f"   • Conversation sessions: {len(analyzer.conversation_flows)}")
    console.print(f"   • Total turns: {sum(len(flow.turns) for flow in analyzer.conversation_flows)}")
    
    # Show agent breakdown
    agent_counts = {}
    for flow in analyzer.conversation_flows:
        agent_counts[flow.agent_type] = agent_counts.get(flow.agent_type, 0) + 1
    
    if agent_counts:
        console.print("   • Agent breakdown:")
        for agent_type, count in agent_counts.items():
            agent_icon = "🤖" if agent_type == "claude-code" else "✨" if agent_type == "gemini-cli" else "🔧"
            console.print(f"     {agent_icon} {agent_type}: {count} sessions")
    
    console.print()
    
    # Save report to file
    try:
        with open(output, 'w') as f:
            f.write(report)
        console.print(f"💾 Report saved to: [bold cyan]{output}[/bold cyan]")
    except Exception as e:
        console.print(f"❌ [red]Error saving report: {e}[/red]")
        return
    
    # Export data if requested
    if export:
        try:
            analyzer.export_data(export)
            console.print(f"📤 Data exported to: [bold cyan]{export}[/bold cyan]")
        except Exception as e:
            console.print(f"❌ [red]Error exporting data: {e}[/red]")
    
    # Display report in terminal (unless disabled)
    if not no_display:
        console.print()
        console.print("📋 [bold magenta]Report Preview:[/bold magenta]")
        console.print()
        
        # Render markdown report
        try:
            markdown = Markdown(report)
            console.print(markdown)
        except Exception as e:
            console.print(f"❌ [red]Error displaying report: {e}[/red]")
            console.print()
            console.print("Raw report:")
            console.print(report)
    
    console.print()
    console.print("🎉 [bold green]Analysis complete![/bold green]")
    console.print(f"   📁 Report: {output}")
    if export:
        console.print(f"   📄 Data export: {export}")


if __name__ == "__main__":
    main()