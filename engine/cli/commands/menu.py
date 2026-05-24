"""
TUI Main Menu Command 🧭
========================
Provides an interactive menu to navigate the dozens of commands
available in the Prediction Engine.
"""

from __future__ import annotations

import os
from typing import Annotated
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def menu() -> None:
    """🧭 Interactive TUI Main Menu for navigating the Prediction Engine."""
    console.clear()
    
    header = (
        "[bold yellow]🏛️  PREDICTION ENGINE: MAIN HUB[/bold yellow]\n\n"
        "Welcome to the high-fidelity probability laboratory.\n"
        "Select an operational sector:"
    )
    console.print(Panel(header, border_style="yellow"))
    
    options = {
        "1": ("⭐ Primary Golden Path", "Quick forecasting, wizard, and backtesting."),
        "2": ("🔬 Analytics & Diagnostics", "Deep-dives into patterns, entropy, and history."),
        "3": ("🎟️ Betting & Tactical Tools", "Portfolio generation, hedging, and combinatorial wheels."),
        "4": ("📓 Monitoring & Logs", "Watchlists, daily digests, and regime history."),
        "5": ("⚙️ System & Optimization", "AutoML tuning, data auditing, and API sidecar."),
        "6": ("✅ Verification & Tools", "Property tests, ticket grading, and structural checks."),
        "q": ("Quit", "Exit the system.")
    }
    
    for key, (name, desc) in options.items():
        console.print(f"  [bold cyan]{key}[/bold cyan] : [bold white]{name}[/bold white] - [dim]{desc}[/dim]")
        
    choice = Prompt.ask("\nSelect Sector", choices=list(options.keys()), default="q")
    
    if choice == "q":
        console.print("[dim]Exiting...[/dim]")
        return
        
    # We will just map sectors to help commands for now, as a full TUI requires `textual` or similar
    # but an interactive Typer prompt is sufficient for a CLI hub.
    
    panels = {
        "1": "help",
        "2": "help", 
        "3": "help",
        "4": "help",
        "5": "help",
        "6": "help"
    }
    
    console.print(f"\n[bold green]Entering Sector:[/] {options[choice][0]}\n")
    console.print("[dim]Use the 'help' command to view detailed lists of commands in this sector.[/dim]\n")
    
    # Run the equivalent help command
    os.system("./lottery help")

if __name__ == "__main__":
    menu()
