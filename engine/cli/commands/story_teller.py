"""
Story-Teller Command 📖
======================
Generates a natural-language 'Narrative' for a suggested ticket.
Combines multiple analytical signals into a qualitative story.
"""

from __future__ import annotations

import random
from typing import Annotated, Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

def generate_story(lottery: str, ticket: list[int], metadata: dict) -> str:
    """Compose a narrative based on ticket properties."""
    # 1. Identify dominant archetypes
    archs = metadata.get("archetypes", {})
    ticket_archs = [archs.get(n, "CITIZEN") for n in ticket]
    
    # 2. Themes
    if "THE HERO" in ticket_archs:
        theme = "a bold momentum play, led by the 'Hero' numbers of the recent regime."
    elif "THE SHADOW" in ticket_archs:
        theme = "a deep-value retrieval mission, harvesting 'Shadow' numbers from the overdue void."
    else:
        theme = "a balanced structural assembly, seeking harmony in the grid."
        
    # 3. Environment
    moon = metadata.get("moon_phase", "unknown")
    kp = metadata.get("solar_kp", 1.0)
    
    env_str = f"Under the influence of the {moon} moon"
    if kp > 4:
        env_str += " and a chaotic solar storm,"
    else:
        env_str += " and a quiet geomagnetic field,"
        
    # 4. Closing Wisdom
    closings = [
        "The probability field is primed. Trust the resonance.",
        "A win is a collapse of infinite possibilities into one. This is your path.",
        "The numbers do not lie, they only whisper. Listen closely."
    ]
    
    story = (
        f"{env_str} this ticket was formed as {theme}\n\n"
        f"The synergy between {ticket[:3]} suggests a tight-knit family of co-occurrence, "
        f"while the presence of {ticket[-1]} provides the necessary entropy for a solo jackpot.\n\n"
        f"{random.choice(closings)}"
    )
    return story

def story_teller(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to use")] = "archetypes",
) -> None:
    """📖 Tell the 'Story' behind a suggested ticket.

    Runs a prediction and then uses natural-language synthesis to explain 
    the 'Narrative' of the selection. Combines archetypes, lunar cycles, 
    and network synergies into a cohesive predictive myth.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    
    with console.status("[cyan]Reading the numerical scrolls..."):
        strat = get_strategy(strategy)
        res = strat.suggest(df, rules, count=1)
        ticket = res.tickets[0]
        
    story = generate_story(lottery, ticket, res.metadata)
    
    console.rule(f"[bold magenta]📖 THE PREDICTIVE NARRATIVE — {rules.name}[/bold magenta]")
    
    story_panel = (
        f"\n[bold yellow]Ticket:[/] {ticket}\n\n"
        f"[italic white]{story}[/italic white]\n"
    )
    console.print(Panel(story_panel, border_style="magenta", title="📜 Oracle Scroll"))

if __name__ == "__main__":
    story_teller("br/lotofacil")
