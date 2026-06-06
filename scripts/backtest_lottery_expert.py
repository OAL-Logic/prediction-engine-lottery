#!/usr/bin/env python3
"""
🚀 Lottery Engine Expert Backtest Runner
========================================
Wrapper script to run the advanced out-of-sample strategy sweep,
portfolio simulation, and budget-aware wheel ticket generation.
"""

import sys
import os
import argparse

# Add the project root to the python path so imports resolve correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    from engine.cli.commands.expert_suggest import expert_suggest
    from rich.console import Console
    from rich.panel import Panel
except ImportError:
    # If the user ran with system python instead of the venv, automatically relaunch in venv
    venv_python = os.path.join(PROJECT_ROOT, ".venv", "bin", "python3")
    if os.path.exists(venv_python) and sys.executable != venv_python:
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print("Error: Could not import prediction engine modules.")
        print("Please ensure you are in the active virtual environment or run ./lottery first.")
        sys.exit(1)

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Run the Lottery Engine Expert Backtest Recommender & Simulator.")
    parser.add_argument("lottery", nargs="?", default="br/lotofacil", help="Lottery name (e.g., br/lotofacil, br/mega-sena)")
    parser.add_argument("-b", "--budget", type=float, default=100.0, help="Allocated BRL budget (default: 100.0)")
    parser.add_argument("-n", "--draws", type=int, default=40, help="Number of history draws to backtest/simulate (default: 40)")
    parser.add_argument("-B", "--bankroll", type=float, default=None, help="Starting bankroll for portfolio simulation")
    parser.add_argument("-e", "--export-md", type=str, default=None, help="Append report to this .md file")
    
    args = parser.parse_args()

    try:
        expert_suggest(
            lottery=args.lottery,
            budget=args.budget,
            draws=args.draws,
            start_bankroll=args.bankroll,
            export_md=args.export_md
        )
    except Exception as e:
        console.print(Panel(f"[bold red]Error running backtest expert simulation:[/bold red]\n[white]{e}[/white]", border_style="red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
