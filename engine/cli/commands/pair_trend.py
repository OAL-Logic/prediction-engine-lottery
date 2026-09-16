"""
Pair Trend Command 📈
=====================
`pair-analysis` reports a single static co-occurrence lift over a lookback
window. `pair-trend` instead tracks how a specific pair's co-occurrence
RATE has moved over successive rolling windows across history — is this
pair's affinity rising, falling, or flat?
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, sparkline, Theme

console = Console()


def rolling_cooccurrence(df, a: int, b: int, window: int, step: int) -> list[tuple[int, int, float]]:
    """
    Returns a list of (window_start_draw_id, window_end_draw_id, rate) across
    successive (non-overlapping, `step`-advanced) windows of `window` draws.
    """
    n = len(df)
    out = []
    start = 0
    while start + window <= n:
        chunk = df.iloc[start:start + window]
        hits = sum(1 for nums in chunk["numbers"] if a in nums and b in nums)
        rate = hits / window
        out.append((int(chunk.iloc[0]["draw_id"]), int(chunk.iloc[-1]["draw_id"]), rate))
        start += step
    return out


def pair_trend(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    a: Annotated[int, typer.Argument(help="First number")],
    b: Annotated[int, typer.Argument(help="Second number")],
    window: Annotated[int, typer.Option("--window", "-w", help="Draws per rolling window")] = 100,
    step: Annotated[int, typer.Option("--step", "-s", help="Draws to advance between windows")] = 20,
) -> None:
    """📈 Track how a number pair's co-occurrence rate has trended over rolling windows."""

    adapter = get_adapter(lottery)
    lo, hi = adapter.rules.number_range
    if a == b:
        console.print("[red]✗ a and b must be different numbers.[/red]")
        raise typer.Exit(1)
    if not (lo <= a <= hi and lo <= b <= hi):
        console.print(f"[red]✗ Both numbers must be within {adapter.rules.number_range}.[/red]")
        raise typer.Exit(1)

    df = adapter.fetch()
    if len(df) < window:
        console.print(f"[red]✗ Only {len(df)} cached draws, need at least --window={window}.[/red]")
        raise typer.Exit(1)

    points = rolling_cooccurrence(df, a, b, window, step)
    rates = [r for _, _, r in points]

    ui_header("PAIR TREND", f"{adapter.rules.name} · pair ({a}, {b}) · window={window}, step={step}")

    table = ui_table(columns=["Window (draw ids)", "Co-occur rate"])
    for start_id, end_id, rate in points:
        table.add_row(f"{start_id}–{end_id}", f"{rate*100:.1f}%")
    console.print(table)

    console.print(f"\n[bold]Trend:[/bold] {sparkline(rates)}")

    first_half = rates[: len(rates) // 2] or rates
    second_half = rates[len(rates) // 2:] or rates
    delta = (sum(second_half) / len(second_half)) - (sum(first_half) / len(first_half))
    direction = "rising" if delta > 0.005 else "falling" if delta < -0.005 else "flat"
    color = Theme.SUCCESS if direction == "rising" else Theme.DANGER if direction == "falling" else Theme.MUTED
    console.print(f"[{color}]Recent vs. earlier windows: {direction} ({delta*100:+.2f} pts)[/{color}]")
    console.print("[dim]A historical trend in a fixed dataset does not predict the next draw.[/dim]")
