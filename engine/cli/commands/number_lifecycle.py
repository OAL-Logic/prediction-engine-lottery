"""
Number Lifecycle Command 🧬
===========================
A consolidated historical "dossier" for a single number: first/last
appearance, total hits, hit rate, current gap, average gap, and the
longest gap/streak it has ever had. Distinct from `gap-forecast` (which is
forward-looking) — this is a pure historical summary.
"""

from __future__ import annotations

from typing import Annotated, Any

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_panel, Theme

console = Console()


def compute_lifecycle(df, number: int) -> dict[str, Any]:
    """
    df must be sorted ascending by draw_id (as adapter.fetch() returns it).
    Returns a dict of lifecycle stats for `number`.
    """
    hits = [number in row for row in df["numbers"]]
    total_draws = len(hits)
    total_hits = sum(hits)

    hit_indices = [i for i, h in enumerate(hits) if h]

    result: dict[str, Any] = {
        "total_draws": total_draws,
        "total_hits": total_hits,
        "hit_rate": (total_hits / total_draws) if total_draws else 0.0,
        "first_draw": None,
        "first_date": None,
        "last_draw": None,
        "last_date": None,
        "current_gap": total_draws,
        "avg_gap": None,
        "longest_gap": None,
        "longest_streak": 0,
    }

    if not hit_indices:
        return result

    result["first_draw"] = int(df.iloc[hit_indices[0]]["draw_id"])
    result["first_date"] = str(df.iloc[hit_indices[0]]["date"])[:10]
    result["last_draw"] = int(df.iloc[hit_indices[-1]]["draw_id"])
    result["last_date"] = str(df.iloc[hit_indices[-1]]["date"])[:10]
    result["current_gap"] = total_draws - 1 - hit_indices[-1]

    gaps = [hit_indices[0]]  # draws before the first hit count as a leading gap
    for a, b in zip(hit_indices, hit_indices[1:]):
        gaps.append(b - a - 1)
    result["avg_gap"] = sum(gaps) / len(gaps) if gaps else None
    result["longest_gap"] = max(gaps) if gaps else None

    longest_streak = streak = 0
    prev = None
    for i in hit_indices:
        if prev is not None and i == prev + 1:
            streak += 1
        else:
            streak = 1
        longest_streak = max(longest_streak, streak)
        prev = i
    result["longest_streak"] = longest_streak

    return result


def number_lifecycle(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    number: Annotated[int, typer.Argument(help="Number to profile")],
) -> None:
    """🧬 Full historical dossier for a single number: hits, gaps, streaks."""

    adapter = get_adapter(lottery)
    lo, hi = adapter.rules.number_range
    if not (lo <= number <= hi):
        console.print(f"[red]✗ {number} is outside {adapter.rules.name}'s range {adapter.rules.number_range}.[/red]")
        raise typer.Exit(1)

    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    stats = compute_lifecycle(df, number)

    ui_header("NUMBER LIFECYCLE", f"{adapter.rules.name} · number {number}")

    if stats["total_hits"] == 0:
        console.print(f"[yellow]{number} has never been drawn in {stats['total_draws']} cached draws.[/yellow]")
        return

    body = (
        f"[bold]Total hits:[/bold]      {stats['total_hits']} / {stats['total_draws']} draws ({stats['hit_rate']*100:.2f}%)\n"
        f"[bold]First seen:[/bold]      draw {stats['first_draw']} ({stats['first_date']})\n"
        f"[bold]Last seen:[/bold]       draw {stats['last_draw']} ({stats['last_date']})\n"
        f"[bold]Current gap:[/bold]     {stats['current_gap']} draws since last hit\n"
        f"[bold]Average gap:[/bold]     {stats['avg_gap']:.2f} draws\n"
        f"[bold]Longest gap ever:[/bold] {stats['longest_gap']} draws\n"
        f"[bold]Longest streak:[/bold]  {stats['longest_streak']} consecutive draws"
    )
    overdue = stats["current_gap"] > stats["avg_gap"]
    style = Theme.WARNING if overdue else Theme.SUCCESS
    console.print(ui_panel(body, title=f"Number {number}", style=style))
    console.print(f"\n[dim]Overdue relative to its own average gap: {'yes' if overdue else 'no'}. Past gaps do not change future draw probabilities.[/dim]")
