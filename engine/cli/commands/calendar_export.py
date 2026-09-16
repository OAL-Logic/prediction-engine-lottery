"""
Calendar Export Command 🗓️
==========================
Generate a standard .ics (RFC 5545) calendar file with the next N draw
dates for a game, computed from its `draw_days` in the registry — so a
user can import upcoming draws into any calendar app.
"""

from __future__ import annotations

import uuid
from datetime import date as _date, datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.adapters.registry import registry

console = Console()

_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def next_draw_dates(draw_days: list[str], count: int, start: _date | None = None) -> list[_date]:
    """Next `count` dates (starting today) whose weekday name is in draw_days."""
    if not draw_days:
        return []
    wanted = {d.strip().title() for d in draw_days}
    wanted_idx = {_WEEKDAY_NAMES.index(w) for w in wanted if w in _WEEKDAY_NAMES}
    if not wanted_idx:
        return []

    d = start or _date.today()
    out: list[_date] = []
    while len(out) < count:
        if d.weekday() in wanted_idx:
            out.append(d)
        d += timedelta(days=1)
    return out


def build_ics(game_name: str, lottery_id: str, dates: list[_date]) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//lottery-engine//draw-calendar//EN", "CALSCALE:GREGORIAN"]
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for d in dates:
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid5(uuid.NAMESPACE_URL, f'{lottery_id}-{d.isoformat()}')}@lottery-engine",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
            f"SUMMARY:{game_name} draw",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def calendar_export(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    count: Annotated[int, typer.Option("--count", "-n", help="How many upcoming draws to export")] = 8,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Write to this .ics file instead of printing")] = None,
) -> None:
    """🗓️ Export the next N draw dates as a standard .ics calendar file."""

    game = registry.get_game(lottery)
    if not game:
        console.print(f"[red]✗ Unknown lottery '{lottery}'.[/red]")
        raise typer.Exit(1)
    if not game.draw_days:
        console.print(f"[red]✗ {game.name} has no draw_days configured in the registry.[/red]")
        raise typer.Exit(1)

    dates = next_draw_dates(game.draw_days, count)
    ics = build_ics(game.name, lottery, dates)

    if output:
        Path(output).write_text(ics)
        console.print(f"[green]✓[/green] Wrote {len(dates)} upcoming {game.name} draws to [bold]{output}[/bold]")
        console.print(f"  Next draw: {dates[0].isoformat()} ({_WEEKDAY_NAMES[dates[0].weekday()]})")
    else:
        console.print(ics)
