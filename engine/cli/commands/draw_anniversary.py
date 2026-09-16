"""
Draw Anniversary Command 📅
===========================
"On this day in history": every past draw whose calendar month/day matches
a given date, across all years on record. A seasonal curiosity report.
"""

from __future__ import annotations

from datetime import date as _date
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, Theme

console = Console()


def anniversary_matches(df, month: int, day: int) -> list[tuple]:
    """Return (draw_id, date, numbers) rows whose date falls on month/day, any year."""
    out = []
    for _, row in df.iterrows():
        d = row["date"]
        if d is None:
            continue
        d = d.date() if hasattr(d, "date") else d
        try:
            if d.month == month and d.day == day:
                out.append((row["draw_id"], d, row["numbers"]))
        except AttributeError:
            continue
    out.sort(key=lambda r: r[1])
    return out


def draw_anniversary(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    date: Annotated[Optional[str], typer.Option("--date", help="Anniversary date to check, YYYY-MM-DD (default: today)")] = None,
) -> None:
    """📅 Show every historical draw that fell on this same month/day, across all years."""

    adapter = get_adapter(lottery)
    if date:
        try:
            target = _date.fromisoformat(date)
        except ValueError:
            console.print(f"[red]✗ Invalid --date '{date}'. Expected YYYY-MM-DD.[/red]")
            raise typer.Exit(1)
    else:
        target = _date.today()

    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    matches = anniversary_matches(df, target.month, target.day)
    years_covered = df["date"].dt.year.nunique()

    ui_header("DRAW ANNIVERSARY", f"{adapter.rules.name} · {target.strftime('%B %d')} across {years_covered} years")

    if not matches:
        console.print(f"[yellow]No draw in cached history has ever landed on {target.strftime('%B %d')}.[/yellow]")
        return

    table = ui_table(title=f"{len(matches)} draw(s) on {target.strftime('%B %d')}", columns=["Year", "Draw", "Date", "Numbers"])
    for draw_id, d, numbers in matches:
        table.add_row(str(d.year), str(draw_id), d.isoformat(), str(list(numbers)))
    console.print(table)
    console.print(
        f"\n[dim]{len(matches)} of {len(df)} cached draws ({len(matches) / len(df) * 100:.2f}%) fell on this "
        "calendar day — no calendar day is more or less likely under the rules of the draw.[/dim]"
    )
