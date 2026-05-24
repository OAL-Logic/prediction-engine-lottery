"""
Fetch Command 📡
===============
Fetches and caches historical draw data for a lottery.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter

console = Console()

def fetch(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    limit: Annotated[Optional[int], typer.Option("--limit", "-L", help="Only fetch N most recent draws")] = None,
) -> None:
    """📡 Fetch and cache historical draw data for a lottery."""

    with console.status(f"[bold green]Fetching {lottery} draws…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch(limit=limit)

    if df.empty:
        console.print(f"[red]✗ 0 draws loaded for {adapter.rules.name}.[/red]")
        console.print("  All sources failed or returned unparseable data.")
        console.print("  Re-run with debug logging: PYTHONLOGGING=DEBUG lottery fetch …")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] {len(df)} draws loaded for [bold]{adapter.rules.name}[/bold]")
    console.print(f"  Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    console.print(f"  Storage:    data/lottery.db (analytical)")
    console.print(f"  Inspection: data/inspections/{lottery.replace('/', '_')}/ (partitioned JSON)")
