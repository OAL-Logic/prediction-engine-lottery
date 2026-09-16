"""
Pattern Search Command 🔎
=========================
SamLotto's "nsSearch" equivalent: given a set of numbers (a full ticket or
just a handful of numbers you care about), rank every historical draw by how
much it overlaps with that set. Answers "has anything like this ever come
up before, and when?" — a direct historical lookup, not a forecast.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, Theme

console = Console()


def _parse_numbers(raw: str) -> list[int]:
    return sorted({int(x.strip()) for x in raw.split(",") if x.strip()})


def pattern_search(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    numbers: Annotated[str, typer.Option("--numbers", "-n", help="Comma-separated numbers to search for, e.g. 3,7,12,24")],
    top: Annotated[int, typer.Option("--top", help="How many best matches to show")] = 10,
    min_overlap: Annotated[int, typer.Option("--min-overlap", help="Only show draws matching at least this many numbers")] = 2,
) -> None:
    """🔎 Rank historical draws by overlap with a given set of numbers."""

    adapter = get_adapter(lottery)
    lo, hi = adapter.rules.number_range
    query = _parse_numbers(numbers)

    if not query:
        console.print("[red]✗ --numbers must contain at least one integer.[/red]")
        raise typer.Exit(1)
    if any(not (lo <= n <= hi) for n in query):
        console.print(f"[red]✗ All numbers must be within {adapter.rules.number_range} for {adapter.rules.name}.[/red]")
        raise typer.Exit(1)

    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    query_set = set(query)
    matches = []
    for _, row in df.iterrows():
        drawn = set(row["numbers"])
        overlap = query_set & drawn
        if len(overlap) >= min_overlap:
            matches.append((row["draw_id"], row["date"], row["numbers"], overlap))

    ui_header("PATTERN SEARCH", f"{adapter.rules.name} · query={sorted(query_set)} · {len(df)} draws scanned")

    if not matches:
        console.print(f"[yellow]No historical draw matched at least {min_overlap} of {sorted(query_set)}.[/yellow]")
        return

    matches.sort(key=lambda m: (len(m[3]), m[0]), reverse=True)
    best_overlap = len(matches[0][3])

    table = ui_table(
        title=f"Top {min(top, len(matches))} matches (of {len(matches)} draws with >= {min_overlap} overlap)",
        columns=["Draw", "Date", "Numbers", "Overlap", "Matched"],
    )
    for draw_id, date, drawn_numbers, overlap in matches[:top]:
        date_str = str(date)[:10] if date is not None else "—"
        overlap_str = f"[bold {Theme.SUCCESS}]{len(overlap)}/{len(query_set)}[/bold {Theme.SUCCESS}]" if len(overlap) == best_overlap else str(len(overlap))
        table.add_row(str(draw_id), date_str, str(list(drawn_numbers)), overlap_str, str(sorted(overlap)))

    console.print(table)
    console.print(
        f"\n[dim]Best historical overlap: {best_overlap}/{len(query_set)}. "
        f"Past overlap has no bearing on future draws — this is a lookup, not a forecast.[/dim]"
    )
