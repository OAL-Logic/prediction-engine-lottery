"""
Party Mode Command 🎊
====================
Simulates a multi-persona brainstorming session to generate radical new project ideas.
"""

from __future__ import annotations

import random
from typing import Annotated, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class Persona:
    def __init__(self, name: str, emoji: str, color: str, focus: str):
        self.name = name
        self.emoji = emoji
        self.color = color
        self.focus = focus

    def speak(self, quote: str):
        content = Text()
        content.append(f"{self.emoji} {self.name.upper()}: ", style=f"bold {self.color}")
        content.append(quote)
        console.print(Panel(content, border_style=self.color))

PERSONAS = {
    "nerd": Persona("The Statistician", "🤓", "cyan", "Real math, p-values, integrity"),
    "chaos": Persona("The Chaos Analyst", "🌪️", "magenta", "Entropy, noise, unpredictable shifts"),
    "mystic": Persona("The Esoteric Expert", "🔮", "yellow", "Numerology, lunar tides, vibrations"),
    "game": Persona("The Game Designer", "🎮", "green", "Fun, absurdity, user engagement"),
}

IDEAS_POOL = [
    "Quantum Entanglement Strategy: Correlate your ticket with the results of a physical double-slit experiment.",
    "The 'Richter' Filter: Only play numbers that hit during high-magnitude seismic events in the last 48 hours.",
    "Blockchain Entropy: Seed the randomness using the hash of the latest Bitcoin block.",
    "Neural Style Transfer for Boards: Treat the board like a painting; use AI to 'paint' the next winning pattern in the style of Van Gogh.",
    "Kelly Criterion 2.0: Automatically calculate the 'Probability of Ruin' for your current betting strategy.",
    "The 'Void' Predator: A strategy that specifically targets numbers that have NEVER appeared together in 30 years.",
    "Atmospheric Muon Collision Sim: Model the path of subatomic particles hitting the draw machine's housing.",
    "Crowd-Sourced Chaos: Use real-time sentiment analysis from Twitter to find 'unpopular' numbers.",
    "Planetary Angularity Filter: Reject any ticket where the numbers form a 'Square' or 'Opposition' in the current zodiac house.",
]

def party(
    lottery: Annotated[str, typer.Argument(help="Lottery name to generate a ticket for")] = "br/mega-sena",
) -> None:
    """🥳 Launch 'Party Mode' to brainstorm and generate a chaotic/math hybrid ticket."""
    from engine.cli.utils import get_adapter
    from engine.strategies import get_strategy

    console.rule("[bold magenta]🎊 WELCOME TO THE PARTY MODE 🎊[/bold magenta]")
    console.print("\n[dim]Topic: Bridging Real Math, Chaos, and Esoteric Absurdity to find the next winning strategy.[/dim]\n")

    # Round 1: The Mathematician's Skepticism
    PERSONAS["nerd"].speak(
        "Look, we can add all the chaos we want, but if the Chi-Squared gate doesn't trip, we're just painting noise. "
        "I'm forcing a 'weighted' frequency baseline."
    )

    # Round 2: The Chaos Response
    PERSONAS["chaos"].speak(
        "Rigorous statistics only work in stable regimes, Nerd! The world is high-entropy right now. "
        "I'm injecting 'seismic' and 'noosphere' jitter into the mix."
    )

    # Round 3: The Mystic's Intervention
    PERSONAS["mystic"].speak(
        "You both miss the point. The machines are physical, yes, but they are entrained to the synodic month. "
        "We need 'moon_phase' to align the ticket with today's tide."
    )

    # Round 4: The Game Designer's Vision
    PERSONAS["game"].speak(
        "Guys, let's keep it fun! I'll put all of this into a 'Hybrid Ensemble' and see what the machine spits out!"
    )

    # Brainstorming Results
    console.print("\n" + "─" * 40 + "\n")
    console.print("[bold yellow]🚀 PARTY TICKETS GENERATED:[/bold yellow]")
    
    with console.status(f"[bold green]The Personas are arguing over {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()
        
        try:
            from engine.strategies.ml.ensemble import HybridEnsemble
            # The personas' chosen strategies
            members = ["weighted", "seismic", "noosphere", "moon_phase"]
            party_strat = HybridEnsemble(members=members)
            
            # They use high temperature because it's a party
            res = party_strat.suggest(df, adapter.rules, count=3, temperature=1.5)
            
            for i, ticket in enumerate(res.tickets):
                console.print(f"  [bold magenta]Party Ticket {i+1}:[/bold magenta] [bold green]{ticket}[/bold green] (sum={sum(ticket)})")
                
            console.print(f"\n  [dim]Consensus built from: {', '.join(members)} (Conf: {res.confidence:.2f})[/dim]")
        except Exception as e:
            console.print(f"  [red]The party crashed! Too much entropy. ({e})[/red]")

    console.print("\n[dim]Party Mode finished. The hangover begins.[/dim]")
