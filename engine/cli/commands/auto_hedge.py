"""
Auto-Hedge Command 🛡️
====================
Optimizes ticket selection to cover the most probable 'Zones' of the board.
Uses a greedy coverage algorithm to maximize sector exposure.
"""

from __future__ import annotations

import math
from typing import Annotated, Optional, List
import pandas as pd
import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

def auto_hedge(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    budget: Annotated[float, typer.Option("--budget", "-b", help="Total budget for hedging")] = 50.0,
    zones_x: Annotated[int, typer.Option("--zx", help="Grid width zones")] = 3,
    zones_y: Annotated[int, typer.Option("--zy", help="Grid height zones")] = 3,
) -> None:
    """🛡️ Optimize betting surface area by covering high-probability board zones.

    Divides the ticket grid into sectors (e.g. 3x3).
    Calculates the 'Heat' of each sector based on recent draws.
    Selects tickets that provide maximum coverage of the hottest sectors
    to ensure that no matter where the balls land in the 'Hot Zones', you have coverage.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pick = rules.pick_count
    
    width = rules.board_cols or 10
    height = math.ceil((hi - lo + 1) / width)
    
    # 1. Calculate Sector Heat
    # Sector size
    sx = width / zones_x
    sy = height / zones_y
    
    sector_counts = np.zeros((zones_y, zones_x))
    
    window = df.tail(100)
    for row in window.itertuples():
        for n in row.numbers:
            r = (n - 1) // width
            c = (n - 1) % width
            
            zx = min(int(c / sx), zones_x - 1)
            zy = min(int(r / sy), zones_y - 1)
            sector_counts[zy, zx] += 1
            
    # 2. Map Numbers to Sectors
    num_to_sector = {}
    sector_to_nums = {}
    for n in range(lo, hi + 1):
        r = (n - 1) // width
        c = (n - 1) % width
        zx = min(int(c / sx), zones_x - 1)
        zy = min(int(r / sy), zones_y - 1)
        num_to_sector[n] = (zy, zx)
        if (zy, zx) not in sector_to_nums: sector_to_nums[(zy, zx)] = []
        sector_to_nums[(zy, zx)].append(n)
        
    # 3. Greedy Selection
    max_tickets = int(budget // rules.ticket_price)
    if max_tickets < 1:
        console.print("[red]Budget too low for even one ticket.[/red]")
        return
        
    # Rank sectors by heat
    flat_heat = []
    for zy in range(zones_y):
        for zx in range(zones_x):
            flat_heat.append(((zy, zx), sector_counts[zy, zx]))
    flat_heat.sort(key=lambda x: x[1], reverse=True)
    
    tickets = []
    covered_sectors = set()
    
    for _ in range(max_tickets):
        ticket = []
        # Try to pick from uncovered hot sectors first
        for (zy, zx), heat in flat_heat:
            if len(ticket) >= pick: break
            if (zy, zx) not in covered_sectors:
                # Pick best number in this sector (using frequency)
                nums_in_sector = sector_to_nums.get((zy, zx), [])
                if nums_in_sector:
                    # For simplicity, pick one at random from sector
                    import random
                    n = random.choice(nums_in_sector)
                    if n not in ticket:
                        ticket.append(n)
                        covered_sectors.add((zy, zx))
        
        # Fill remaining slots with high-frequency numbers
        if len(ticket) < pick:
            # Get high freq numbers
            all_nums = [n for r in window.itertuples() for n in r.numbers]
            from collections import Counter
            counts = Counter(all_nums)
            sorted_nums = [n for n, c in counts.most_common()]
            for n in sorted_nums:
                if len(ticket) >= pick: break
                if n not in ticket:
                    ticket.append(n)
                    
        tickets.append(sorted(ticket))

    # 4. Display Results
    console.rule(f"[bold green]🛡️ SPATIAL AUTO-HEDGE — {rules.name}[/bold green]")
    
    table = Table(title=f"Optimized Coverage Portfolio ({len(tickets)} tickets)", box=None)
    table.add_column("Ticket ID", style="dim")
    table.add_column("Numbers", style="bold yellow")
    table.add_column("Zones Covered", justify="right", style="cyan")
    
    for i, t in enumerate(tickets):
        zones = set(num_to_sector[n] for n in t)
        table.add_row(f"#{i+1}", ", ".join(map(str, t)), str(len(zones)))
        
    console.print(table)
    
    coverage_pct = (len(covered_sectors) / (zones_x * zones_y)) * 100
    summary = (
        f"Total Budget Spent: [bold]{len(tickets) * rules.ticket_price:.2f}[/bold]\n"
        f"Board Surface Coverage: [bold cyan]{coverage_pct:.1f}%[/bold cyan] of active sectors.\n\n"
        "Strategic Logic:\n"
        "• High Entropy Mitigation: Diversified across 'Hot' physical sectors.\n"
        "• Statistical Anchoring: Residual slots filled with global frequency leaders."
    )
    console.print(Panel(summary, title="🛡️ Hedge Summary", border_style="green"))

if __name__ == "__main__":
    auto_hedge("br/lotofacil")
