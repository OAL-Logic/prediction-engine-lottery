"""
Ticket Backtest Command ⏮️
==========================
"If I had played this exact ticket on every historical draw, how would it
have done?" Replays one fixed ticket against the full cached history and
tallies hits per prize tier. Distinct from `backtest` (which blind-tests a
*strategy* that picks different numbers each draw) and `hitcheck` (which
checks previously-logged tickets against results as they arrive).
"""

from __future__ import annotations

from collections import Counter
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table

console = Console()


def replay_ticket(df, ticket: set[int], prize_tiers: list[int]) -> dict:
    hit_counts = Counter()
    best_ever = 0
    best_draw = None
    for _, row in df.iterrows():
        hits = len(ticket & set(row["numbers"]))
        if hits > best_ever:
            best_ever = hits
            best_draw = (int(row["draw_id"]), str(row["date"])[:10])
        for tier in prize_tiers:
            if hits == tier:
                hit_counts[tier] += 1
    return {"hit_counts": dict(hit_counts), "best_ever": best_ever, "best_draw": best_draw, "total_draws": len(df)}


def ticket_backtest(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    numbers: Annotated[str, typer.Argument(help="Comma-separated ticket numbers")],
) -> None:
    """⏮️ Replay one fixed ticket against every historical draw and tally prize-tier hits."""

    adapter = get_adapter(lottery)
    try:
        ticket_list = sorted({int(x.strip()) for x in numbers.split(",") if x.strip()})
    except ValueError:
        console.print("[red]✗ --numbers must be comma-separated integers.[/red]")
        raise typer.Exit(1)

    if not adapter.validate(ticket_list):
        console.print(f"[red]✗ {ticket_list} is not a valid ticket for {adapter.rules.name}.[/red]")
        raise typer.Exit(1)

    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    result = replay_ticket(df, set(ticket_list), adapter.rules.prize_tiers)

    ui_header("TICKET BACKTEST", f"{adapter.rules.name} · {ticket_list} · {result['total_draws']} draws replayed")

    table = ui_table(columns=["Prize tier (hits)", "Times won", "Historical rate"])
    for tier in sorted(adapter.rules.prize_tiers):
        wins = result["hit_counts"].get(tier, 0)
        rate = wins / result["total_draws"]
        table.add_row(f"{tier}", str(wins), f"1 in {result['total_draws'] / wins:,.0f}" if wins else f"0 / {result['total_draws']}")
    console.print(table)

    if result["best_draw"]:
        draw_id, date = result["best_draw"]
        console.print(
            f"\n[bold]Best-ever match:[/bold] {result['best_ever']}/{len(ticket_list)} numbers, "
            f"on draw {draw_id} ({date})."
        )
    console.print("[dim]This is a replay of one fixed ticket against history it did not change — not evidence it will repeat.[/dim]")
