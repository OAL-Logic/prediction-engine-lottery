"""
Oracle Command 🔮
================
Generates natural-language advice using simulated high-intelligence personas.
"""

from __future__ import annotations

import random
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from engine.cli.utils import get_adapter
from engine.modules import frequency, deviation, insights as insight_mod

console = Console()

PERSONAS = {
    "quant": {
        "name": "The Quantitative Strategist",
        "emoji": "🧐",
        "style": "cyan",
        "intro": "Statistical significance is the only truth. Here is the mathematical reality of your current window:",
    },
    "mystic": {
        "name": "The Esoteric Sage",
        "emoji": "🧙‍♂️",
        "style": "yellow",
        "intro": "The machines are but mirrors of the universe's breath. Listen to the vibrations of the current cycle:",
    },
    "degen": {
        "name": "The High-Roller Analyst",
        "emoji": "🎲",
        "style": "magenta",
        "intro": "Calculated risk is the path to the jackpot. Here's where the heat is concentrating:",
    }
}

def oracle(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    persona: Annotated[str, typer.Option("--persona", "-p", help="quant | mystic | degen")] = "quant",
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Analysis window")] = 100,
) -> None:
    """🔮 Generate natural-language betting advice based on hard data."""
    if persona not in PERSONAS:
        console.print(f"[red]Unknown persona '{persona}'. Choose: {', '.join(PERSONAS.keys())}[/red]")
        raise typer.Exit(1)
        
    p_data = PERSONAS[persona]
    
    with console.status(f"[bold {p_data['style']}]Consulting {p_data['name']}…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()
        insights = insight_mod.get_automated_insights(df, adapter.rules, limit=limit)
        
    console.rule(f"[bold {p_data['style']}]ORACLE CONSULTATION: {p_data['name']}[/bold {p_data['style']}]")
    console.print(f"\n{p_data['emoji']} [italic]\"{p_data['intro']}\"[/italic]\n")
    
    # Transform insights into persona-specific language
    for i in insights:
        text = i.replace("[red]●[/red]", "•").replace("[green]●[/green]", "•").replace("[yellow]●[/yellow]", "•").replace("[cyan]●[/cyan]", "•").replace("[blue]●[/blue]", "•").replace("[magenta]●[/magenta]", "•")
        
        if persona == "mystic":
            text = text.replace("distribution", "cosmic flow").replace("Statistical", "Vibrational").replace("Number", "Arcano")
            text += " [dim](The stars align).[/dim]"
        elif persona == "quant":
            text = text.replace("Hotspot", "Local Maximum").replace("Overdue", "Mean Reversion Candidate")
        
        console.print(f"  {text}")
        
    # Closing wisdom
    closing = [
        "Fortune favors the prepared mind.",
        "The house always wins, unless the math breaks.",
        "Luck is what happens when preparation meets opportunity.",
        "The machine remembers nothing; the data remembers everything."
    ]
    console.print(f"\n[dim]\"{random.choice(closing)}\"[/dim]")
