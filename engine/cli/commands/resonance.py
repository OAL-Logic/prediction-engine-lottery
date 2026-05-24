"""
Resonance Command 💎
===================
Analyzes the 'constructive interference' between multiple strategies.
Treats each strategy's score for a number as a wave amplitude.
Identifies numbers where the 'Phase Lock' is strongest.
"""

from __future__ import annotations

import numpy as np
from typing import Annotated, Optional, List

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

def resonance(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", 
        help="Comma-separated strategies to analyze")] = "weighted,markov,bayesian,hurst_memory,graph_influence",
    limit: Annotated[int, typer.Option("--limit", "-L", help="Analysis window")] = 100,
) -> None:
    """💎 Detect multi-strategy resonance and wave interference.

    Calculates the 'Probability Waveform' of the lottery by summing normalized 
    scores from multiple strategies. Identifies 'Resonance Peaks' where 
    different mathematical models constructively interfere.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    all_numbers = list(range(lo, hi + 1))
    
    strat_list = [s.strip() for s in strategies.split(",") if s.strip()]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Calculating interference pattern...", total=len(strat_list))
        
        all_scores = {}
        for name in strat_list:
            try:
                strat = get_strategy(name)
                # We use score() directly to get the raw probability field
                scores = strat.score(df.tail(limit), rules)
                all_scores[name] = scores
            except Exception as e:
                console.print(f"[dim red]Skipped {name}: {e}[/dim red]")
            progress.advance(task)

    if not all_scores:
        console.print("[bold red]No signals detected. Resonance failed.[/bold red]")
        return

    # --- 1. Calculate Aggregate Interference ---
    # Global Waveform = sum of all normalized scores
    waveform = {n: 0.0 for n in all_numbers}
    n_strats = len(all_scores)
    
    for name, scores in all_scores.items():
        for n, s in scores.items():
            waveform[n] += s / n_strats

    # --- 2. Calculate Coherence (Phase Lock) ---
    # Coherence = inverse of variance across strategies for each number
    coherence = {}
    for n in all_numbers:
        vals = [all_scores[name].get(n, 0.0) for name in all_scores]
        variance = np.var(vals)
        # Coherence is high if variance is low (and score is high)
        coherence[n] = (waveform[n] * (1.0 - np.sqrt(variance)))

    # --- 3. Visualization ---
    console.rule(f"[bold yellow]💎 HARMONIC RESONANCE SPECTRUM — {rules.name}[/bold yellow]")
    
    # Sort numbers by resonance (waveform * coherence)
    resonant_nums = sorted(all_numbers, key=lambda n: coherence[n], reverse=True)
    
    table = Table(title="Resonance Peaks (Constructive Interference)", box=None, padding=(0, 2))
    table.add_column("Number", justify="center", style="bold cyan")
    table.add_column("Amplitude (Σ)", justify="right", style="green")
    table.add_column("Coherence (Φ)", justify="right", style="magenta")
    table.add_column("Spectrum", justify="left", width=25)
    
    max_amp = max(waveform.values()) if waveform else 1.0
    
    for n in resonant_nums[:15]:
        amp = waveform[n]
        coh = coherence[n]
        
        # Visual spectrum bar
        bar_len = int(amp * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        table.add_row(
            str(n),
            f"{amp:.3f}",
            f"{coh:.3f}",
            f"[yellow]{bar}[/yellow]"
        )
        
    console.print(table)
    
    # Consensus Panel
    top_ticket = sorted(resonant_nums[:rules.pick_count])
    consensus = Text.from_markup(
        f"\n[bold yellow]✨ RESONANCE TICKET: {top_ticket}[/bold yellow]\n\n"
        f"[dim]This ticket represents the point of maximum coherence across {n_strats} mathematical models.[/dim]"
    )
    console.print(Panel(consensus, border_style="yellow", title="💎 Final Synthesis"))

if __name__ == "__main__":
    resonance("br/lotofacil")
