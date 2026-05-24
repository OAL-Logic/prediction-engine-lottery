"""
Odds Command ⚖️
==============
Displays mathematical odds for a specific lottery or compares every registered game.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from engine.cli.utils import get_adapter
from engine.adapters.registry import registry
from engine.odds.comparator import compare_lotteries

console = Console()

def odds(
    lottery: Annotated[Optional[str], typer.Argument(help="Lottery name (e.g. br/lotofacil)")] = None,
    compare: Annotated[bool, typer.Option("--compare", "-c", help="Compare all registered lotteries")] = False,
) -> None:
    """⚖️ View jackpot odds and compare game efficiency."""
    
    if compare:
        _run_comparison()
        return

    if not lottery:
        console.print("[red]✗ Lottery name is required unless using --compare.[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    rules = adapter.rules
    
    console.rule(f"[bold cyan]Odds Analysis: {rules.name}[/bold cyan]")
    
    table = Table(box=None)
    table.add_column("Tier (Match)", style="bold yellow")
    table.add_column("Exact Probability", justify="right")
    table.add_column("1 in X Odds", justify="right", style="bold green")
    
    from math import comb
    def _hyp_prob(pool, pick, match):
        denom = comb(pool, pick)
        if denom == 0: return 0.0
        return (comb(pick, match) * comb(pool - pick, pick - match)) / denom

    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    
    for t in sorted(rules.prize_tiers, reverse=True):
        p = _hyp_prob(pool_size, rules.pick_count, t)
        odds_val = 1.0 / p if p > 0 else 0
        table.add_row(
            str(t),
            f"{p:.8f}",
            f"{odds_val:,.0f}" if odds_val > 0 else "—"
        )
        
    console.print(table)
    console.print(f"\n  [dim]Ticket Price: {rules.currency} {rules.ticket_price:.2f}[/dim]")


def _run_comparison() -> None:
    """Compare all registered games."""
    all_games = registry.list_games()
    all_rules = [g.to_rules() for g in all_games]
    
    results = compare_lotteries(all_rules)
    
    table = Table(title="Global Odds Comparison (Ranked by Jackpot Odds)", box=None)
    table.add_column("Rank", justify="right", style="dim")
    table.add_column("Lottery", style="bold cyan")
    table.add_column("Jackpot Odds", justify="right", style="bold green")
    table.add_column("Price", justify="right")
    table.add_column("Efficiency*", justify="right", style="dim")
    
    for i, res in enumerate(results):
        table.add_row(
            str(i + 1),
            res.name,
            f"1 in {res.jackpot_odds:,}",
            f"{res.currency} {res.ticket_price:.2f}",
            f"{res.efficiency_score:.2f}"
        )
        
    console.print(table)
    console.print("\n[dim]* Efficiency = log10(odds) / price. Lower is better (more probability per currency unit).[/dim]")
