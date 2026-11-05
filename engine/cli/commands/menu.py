"""
TUI Main Menu Command 🧭
========================
Provides an interactive menu to navigate the primary features
available in the Prediction Engine.
"""

from __future__ import annotations

import os
import sys
from typing import Annotated
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

console = Console()


def menu() -> None:
    """🧭 Interactive CLI Command Center for navigating the Prediction Engine."""
    console.print()
    header = (
        "[bold cyan]🎯 P4LOTTERY: UNIFIED COMMAND CENTER[/bold cyan]\n"
        "[dim]High-precision probabilistic forecasting, combinatorial wheeling, and physical phase space models.[/dim]"
    )
    console.print(Panel(header, border_style="bright_blue"))

    menu_table = Table(box=None, padding=(0, 2))
    menu_table.add_column("Key", style="bold cyan", justify="right")
    menu_table.add_column("Command", style="bold white")
    menu_table.add_column("Description", style="dim")

    options = {
        "1": ("wizard", "Interactive guided analysis, strategy selection, and ticket generation"),
        "2": ("suggest", "Instant ticket generation for a specific game and strategy"),
        "3": ("analyze", "Unified statistical dashboard, frequencies, and regime detection"),
        "4": ("fringe-swarm", "Autonomous fringe telemetry, consensus disagreement & counter-hedging"),
        "5": ("lab", "Offline Web Synthesis Lab, 3D Lorenz attractor, and PWA edge cockpit"),
        "6": ("auto-hedge", "Grid sector auto-hedging to maximize board surface coverage"),
        "7": ("wheel", "Combinatorial covering designs and budget reduction wheels"),
        "8": ("docs", "Mathematical specifications, filter diagrams, and formula catalog"),
        "9": ("help", "Display full multi-panel categorised command reference"),
        "q": ("Quit", "Exit the menu"),
    }

    for key, (cmd_name, desc) in options.items():
        if key == "q":
            menu_table.add_row(f"[bold red]{key}[/bold red]", f"[red]{cmd_name}[/red]", desc)
        else:
            menu_table.add_row(f"[bold cyan]{key}[/bold cyan]", f"[bold green]{cmd_name}[/bold green]", desc)

    console.print(menu_table)
    choice = Prompt.ask("\n[bold yellow]Select Option[/bold yellow]", choices=list(options.keys()), default="1")

    if choice == "q":
        console.print("[dim]Exiting command center.[/dim]")
        return

    cmd = options[choice][0]
    console.print(f"\n[bold green]Launching:[/] [cyan]./p4lottery {cmd}[/cyan]\n")

    # Delegate directly to CLI command in-process
    from typer.main import get_command
    from engine.cli.main import app as root_app

    click_cmd = get_command(root_app)
    try:
        click_cmd.main(args=[cmd], prog_name="p4lottery", standalone_mode=False)
    except Exception as exc:
        # Fallback to sys.argv re-entry
        os.system(f"{sys.executable} -m engine.cli.main {cmd}")


if __name__ == "__main__":
    menu()
