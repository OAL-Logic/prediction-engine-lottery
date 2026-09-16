"""
Data Status Command 📡📋
========================
`games` lists the static registry (id, format, price). This reports
operational freshness instead: how many draws are actually cached for
each game, when the last one landed, and when the next one is due —
a one-glance "is my data fresh?" fleet overview.
"""

from __future__ import annotations

from datetime import date as _date
from typing import Annotated

import typer
from rich.console import Console

from engine.adapters.registry import registry
from engine.cli.commands.calendar_export import next_draw_dates
from engine.cli.utils import ui_header, ui_table, Theme
from engine.modules.storage import LotteryStorage

console = Console()


def data_status(
    all_games: Annotated[bool, typer.Option("--all", help="Include games with no data adapter yet")] = False,
) -> None:
    """📡📋 Cached-data freshness overview across every registered game."""

    games = registry.list_games(only_available=not all_games)
    storage = LotteryStorage()
    today = _date.today()

    ui_header("DATA STATUS", f"{len(games)} games")

    table = ui_table(columns=["ID", "Name", "Cached draws", "Last draw", "Days since", "Next draw"])
    for g in games:
        if not g.data_available:
            table.add_row(g.id, g.name, "[dim]—[/dim]", "[dim]no adapter yet[/dim]", "—", "—")
            continue

        df = storage.load_draws(g.id)
        if df.empty:
            table.add_row(g.id, g.name, "0", "[yellow]never fetched[/yellow]", "—", "—")
            continue

        last_date = df["draw_date"].max()
        if hasattr(last_date, "date"):
            last_date = last_date.date()
        elif isinstance(last_date, str):
            last_date = _date.fromisoformat(last_date[:10])
        days_since = (today - last_date).days

        next_dates = next_draw_dates(g.draw_days, count=1, start=today) if g.draw_days else []
        next_str = next_dates[0].isoformat() if next_dates else "[dim]unknown[/dim]"

        style = Theme.WARNING if days_since > 14 else ""
        days_str = f"[{style}]{days_since}[/{style}]" if style else str(days_since)
        table.add_row(g.id, g.name, str(len(df)), last_date.isoformat(), days_str, next_str)

    console.print(table)
