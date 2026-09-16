"""
Record Command 📝
=================
Manually record (or correct) a single draw result — the "DrawingsUpdate"
equivalent for when a result isn't available yet from any automated `fetch`
source, or a previously-stored draw needs a correction.
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from engine.cli.utils import get_adapter, Theme
from engine.modules.storage import LotteryStorage

console = Console()


def _parse_int_list(raw: str) -> list[int]:
    raw = raw.strip()
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def record(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draw_id: Annotated[int, typer.Option("--draw-id", help="Sequential draw number (contest/concurso id)")],
    date: Annotated[str, typer.Option("--date", help="Draw date, ISO format (YYYY-MM-DD)")],
    numbers: Annotated[str, typer.Option("--numbers", help="Comma-separated main numbers, e.g. 3,7,12,24,31,45")],
    bonus: Annotated[str, typer.Option("--bonus", help="Comma-separated bonus/powerball numbers")] = "",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Validate and preview only — do not write to storage")] = False,
    db_path: Annotated[Optional[Path], typer.Option("--db-path", hidden=True, help="Override storage DB path (testing)")] = None,
) -> None:
    """📝 Manually record or correct a single historical draw result."""

    adapter = get_adapter(lottery)

    try:
        parsed_date = _date.fromisoformat(date)
    except ValueError:
        console.print(f"[red]✗ Invalid --date '{date}'. Expected YYYY-MM-DD.[/red]")
        raise typer.Exit(1)

    try:
        num_list = sorted(_parse_int_list(numbers))
        bonus_list = sorted(_parse_int_list(bonus))
    except ValueError:
        console.print("[red]✗ --numbers/--bonus must be comma-separated integers.[/red]")
        raise typer.Exit(1)

    if not adapter.validate(num_list, bonus_list or None):
        console.print(
            f"[red]✗ {num_list} (bonus={bonus_list}) is not a valid ticket for "
            f"{adapter.rules.name} (pick {adapter.rules.pick_count} from "
            f"{adapter.rules.number_range[0]}-{adapter.rules.number_range[1]}"
            + (f", bonus {adapter.rules.bonus_count} from {adapter.rules.bonus_range}" if adapter.rules.bonus_count else "")
            + ").[/red]"
        )
        raise typer.Exit(1)

    summary = (
        f"[bold]Lottery:[/bold]  {adapter.rules.name} ({lottery})\n"
        f"[bold]Draw ID:[/bold]  {draw_id}\n"
        f"[bold]Date:[/bold]     {parsed_date.isoformat()}\n"
        f"[bold]Numbers:[/bold]  {num_list}\n"
        f"[bold]Bonus:[/bold]    {bonus_list or '—'}"
    )

    if dry_run:
        console.print(Panel(summary, title="[bold]DRY RUN — nothing written[/bold]", border_style=Theme.WARNING))
        return

    storage = LotteryStorage(db_path=db_path) if db_path is not None else LotteryStorage()
    storage.save_draws(lottery, [{
        "draw_id": draw_id,
        "draw_date": parsed_date.isoformat(),
        "numbers": num_list,
        "bonus": bonus_list,
    }])

    console.print(Panel(summary, title="[bold green]✓ Draw recorded[/bold green]", border_style=Theme.SUCCESS))
    console.print("[dim]Manually-recorded draws are merged like any fetched draw — re-run `analyze`/`suggest` to pick it up.[/dim]")
