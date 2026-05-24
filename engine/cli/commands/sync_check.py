"""
Sync Check Command 📡
====================
Detects 'Numerical Synchronicity' across multiple lottery games.
Identifies numbers that appeared in different lotteries on the same date or week.
"""

from __future__ import annotations

from typing import Annotated, Optional, Dict
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.adapters.registry import registry
from engine.cli.utils import get_adapter

console = Console()

def sync_check(
    days: Annotated[int, typer.Option("--days", "-d", help="Window for cross-game sync check")] = 7,
) -> None:
    """📡 Search for cross-game synchronicity (shared numbers across different lotteries).

    Fetches the latest draws for ALL supported games and identifies numbers 
    that appeared in more than one lottery within the given window. 
    Theory: Global environmental factors might create 'Resonance Peaks' 
    across independent random processes.
    """
    games = registry.list_games()
    
    # 1. Fetch recent draws for all games
    global_hits: Dict[int, list[str]] = {}
    
    with console.status("[cyan]Scanning global lottery network..."):
        for game in games:
            try:
                adapter = get_adapter(game.id)
                df = adapter.fetch(limit=10) # Get a few recent ones
                if df.empty: continue
                
                # Check draws within the last N days
                now = datetime.now()
                cutoff = now - timedelta(days=days)
                
                recent = df[df['date'] >= cutoff.date()] if 'date' in df.columns else df.tail(3)
                
                for row in recent.itertuples():
                    for n in row.numbers:
                        if n not in global_hits:
                            global_hits[n] = []
                        if game.name not in global_hits[n]:
                            global_hits[n].append(game.name)
            except Exception:
                continue

    # 2. Identify sync peaks
    sync_peaks = {n: games for n, games in global_hits.items() if len(games) > 1}
    
    # 3. Results
    console.rule(f"[bold magenta]📡 GLOBAL SYNCHRONICITY REPORT (Window: {days} days)[/bold magenta]")
    
    if not sync_peaks:
        console.print("[dim]No significant cross-game sync peaks detected.[/dim]")
        return
        
    table = Table(title="Sync Peaks (Numbers appearing in multiple games)", box=None)
    table.add_column("Number", style="bold yellow")
    table.add_column("Game Count", justify="right")
    table.add_column("Participating Lotteries", style="cyan")
    
    # Sort by game count
    sorted_peaks = sorted(sync_peaks.items(), key=lambda x: len(x[1]), reverse=True)
    
    for n, participating in sorted_peaks:
        table.add_row(
            str(n),
            str(len(participating)),
            ", ".join(participating)
        )
        
    console.print(table)
    
    # Consensus
    all_sync_nums = [n for n, p in sorted_peaks]
    summary = (
        f"Detected [bold yellow]{len(sync_peaks)}[/bold yellow] synchronized numbers.\n\n"
        f"These numbers reached 'Global Resonance' recently across the network.\n"
        f"Sync Pool: [cyan]{all_sync_nums[:10]}[/cyan]..."
    )
    console.print(Panel(summary, border_style="magenta", title="📡 Global Coincidence Cluster"))

if __name__ == "__main__":
    sync_check()
