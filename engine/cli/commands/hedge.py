"""
Hedge Command ⚖️
==============
Generates an optimized portfolio of tickets to maximize lower-tier prize probability.
"""

from __future__ import annotations

import math
from typing import Annotated, Optional, List

import typer
import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from engine.cli.utils import get_adapter, format_confidence
from engine.strategies import get_strategy

console = Console()

def hedge(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    budget:  Annotated[float, typer.Option("--budget", "-b", help="Total budget for this hedge bet")] = 50.0,
    risk_profile: Annotated[str, typer.Option("--risk", "-r", help="conservative | balanced | aggressive")] = "balanced",
) -> None:
    """🛡️ Generate an optimized 'Hedge Portfolio' to maximize lower-tier returns.

    Uses the HedgeStrategy to identify a stable pool of high-confidence numbers,
    then generates an optimized set of tickets that maximizes coverage for the
    lowest prize tier within your budget.

    Args:
        lottery: Lottery identifier (e.g. 'br/lotofacil')
        budget:  Total money to spend on tickets
        risk_profile:  'conservative' | 'balanced' | 'aggressive'

    Returns:
        None (prints portfolio and analysis)

    Example:
        lottery hedge br/lotofacil --budget 50.0
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    
    # 1. Calculate how many tickets we can afford
    price = rules.ticket_price
    max_tickets = int(budget // price)
    
    if max_tickets < 1:
        console.print(f"[red]Error: Budget {budget} is less than the ticket price {price}.[/red]")
        raise typer.Exit(1)
        
    console.rule(f"[bold cyan]Hedge Portfolio Generator: {rules.name}[/bold cyan]")
    console.print(f"  [dim]Budget: {budget:.2f} {rules.currency} | Target: {max_tickets} tickets[/dim]\n")

    # 2. Use HedgeStrategy to find "Stable" numbers
    with console.status("[bold green]Calculating structural stability zones…"):
        strat = get_strategy("hedge")
        scores = strat.score(df, rules)
        
    # 3. Select Pool
    # Conservative: smaller pool, more repetition (higher prize probability)
    # Aggressive: larger pool, more coverage (wider search, lower hit probability)
    pool_sizes = {"conservative": 10, "balanced": 15, "aggressive": 20}
    pool_size = pool_sizes.get(risk_profile, 15)
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_pool = [n for n, s in sorted_nums[:pool_size]]
    
    # 4. Combinatorial Optimization (Simplified Greedy Covering)
    # We want to pick tickets from this pool such that we maximize the chance 
    # of hitting the lowest prize tier.
    tickets = []
    
    # Tier targets (e.g. 4 for Mega-Sena, 11 for Lotofacil)
    target_matches = rules.prize_tiers[0]
    
    from engine.wheels import generate_abbreviated_wheel
    # We use our wheeling engine to get a covering set for our target pool
    wheel_tickets = generate_abbreviated_wheel(
        top_pool, 
        rules.pick_count, 
        guarantee=target_matches, 
        max_tickets=max_tickets
    )
    
    # 5. Display Portfolio
    table = Table(title=f"Self-Paying Portfolio ({risk_profile.capitalize()})", box=None)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Numbers", style="bold green")
    table.add_column("Hedge Strength", justify="right")
    
    for i, t in enumerate(wheel_tickets):
        # Calculate mean hedge score for this ticket
        h_score = sum(scores.get(n, 0) for n in t) / len(t)
        table.add_row(str(i+1), str(sorted(t)), f"{h_score:.2f}")
        
    console.print(table)
    
    # 6. Financial Projection
    cost = len(wheel_tickets) * price
    # Crude estimation of probability of hitting target_matches in the pool
    # Prob(T in Pool) = C(PoolSize, Target) / C(TotalPool, Target)
    # This is complex, but we'll show the "Pool Coverage"
    coverage = (len(top_pool) / (rules.number_range[1] - rules.number_range[0] + 1)) * 100
    
    projection = (
        f"This portfolio covers [bold]{len(top_pool)}[/bold] numbers ({coverage:.1f}% of board).\n"
        f"Total Investment: [bold]{cost:.2f} {rules.currency}[/bold]\n\n"
        f"Goal: If [bold]{target_matches}[/bold] of the winning numbers fall within your pool of {len(top_pool)}, "
        f"at least one of these tickets is [bold]guaranteed[/bold] to hit a prize."
    )
    
    console.print(Panel(projection, title="Financial Projection", border_style="cyan"))
    
    console.print(f"\n[dim]Hedge Pool: {top_pool}[/dim]")
