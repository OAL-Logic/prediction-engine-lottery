"""
Number Timeline Command 📈
==========================
Historical hit pattern for a single number across recent draws.

Shows when the number appeared (and didn't) as a compact sparkline,
computes gap statistics (min/max/mean draws between appearances), and
flags the current cold streak — useful for spotting numbers that are
"overdue" or consistently cold.

Output
------
  Sparkline   hit/miss for the last N draws (newest right)
  Hit table   draws where the number appeared (date, draw_id, numbers)
  Stats panel  count, hit-rate, gaps (min/max/mean/current streak)
  Tier        HOT / WARM / COLD / VERY COLD by recent hit rate

Example
-------
  lottery number-timeline br/lotofacil 7
  lottery number-timeline br/lotofacil 7 --draws 200
  lottery number-timeline br/mega-sena 42 --export-md timeline.md
"""

from __future__ import annotations

import numpy as np
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_SPARK_ON  = "█"
_SPARK_OFF = "░"
_LINE_WIDTH = 60   # sparkline characters per terminal line


def _tier_label(hit_rate: float, baseline: float) -> str:
    if hit_rate >= baseline * 1.5:
        return "[bold green]HOT[/bold green]"
    if hit_rate >= baseline * 1.0:
        return "[green]WARM[/green]"
    if hit_rate >= baseline * 0.5:
        return "[dim]COLD[/dim]"
    return "[dim]VERY COLD[/dim]"


def number_timeline(
    lottery:  Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    number:   Annotated[int, typer.Argument(help="The pool number to inspect")],
    draws:    Annotated[int,  typer.Option("--draws", "-n",
        help="How many recent draws to analyse")] = 100,
    show_all: Annotated[bool, typer.Option("--all", "-a",
        help="Print every draw in the hit table, not just hits")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append timeline report to this .md file")] = None,
) -> None:
    """📈 Historical hit pattern for a single pool number.

    Shows a sparkline (newest-right), gap statistics, and current
    cold-streak length for any number in the pool.

    Example: lottery number-timeline br/lotofacil 7
             lottery number-timeline br/lotofacil 7 --draws 200
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range

    if not (lo <= number <= hi):
        console.print(f"[red]Number {number} is outside pool range [{lo}–{hi}][/red]")
        raise typer.Exit(1)

    window = df.tail(draws)
    n_draws = len(window)

    # Build hit/miss sequence (oldest → newest, index 0 = oldest)
    hits: list[bool] = []
    rows_data: list[dict] = []
    for row in window.itertuples():
        hit = number in row.numbers
        hits.append(hit)
        rows_data.append({
            "date":    str(getattr(row, "date", "?")),
            "draw_id": str(getattr(row, "draw_id", "?")),
            "numbers": sorted(row.numbers),
            "hit":     hit,
        })

    # ── Sparkline (newest on right) ──────────────────────────────────────────
    spark = "".join(_SPARK_ON if h else _SPARK_OFF for h in hits)
    # Wrap into lines of _LINE_WIDTH
    lines = [spark[i:i+_LINE_WIDTH] for i in range(0, len(spark), _LINE_WIDTH)]

    console.print(f"\n[bold]Number [yellow]{number}[/yellow] — {rules.name}[/bold]  "
                  f"[dim](last {n_draws} draws, oldest → newest)[/dim]\n")
    for line in lines:
        # colour hits green
        coloured = line.replace(_SPARK_ON, "[green]█[/green]")
        console.print("  " + coloured)
    console.print()

    # ── Gap statistics ────────────────────────────────────────────────────────
    gap_start: Optional[int] = None
    gaps: list[int] = []
    current_cold = 0   # draws since last hit (0 = hit in most recent draw)
    for i, h in enumerate(hits):
        if h:
            if gap_start is not None:
                gaps.append(i - gap_start)
            gap_start = i
    # Cold streak: draws since last hit (counting from end)
    for h in reversed(hits):
        if h:
            break
        current_cold += 1

    hit_count = sum(hits)
    hit_rate  = hit_count / n_draws if n_draws else 0.0
    baseline  = rules.pick_count / (hi - lo + 1)
    tier      = _tier_label(hit_rate, baseline)

    mean_gap = np.mean(gaps) if gaps else float("inf")
    min_gap  = min(gaps) if gaps else 0
    max_gap  = max(gaps) if gaps else 0
    med_gap  = np.median(gaps) if gaps else 0

    # "Overdue" flag: current cold streak vs mean gap
    overdue_flag = ""
    if gaps and current_cold > mean_gap * 1.5:
        overdue_flag = "  [yellow]⚠ OVERDUE[/yellow]"
    elif gaps and current_cold > mean_gap * 2.0:
        overdue_flag = "  [red]⚠ VERY OVERDUE[/red]"

    console.print(Panel(
        f"[bold yellow]{number}[/bold yellow]   {tier}{overdue_flag}\n\n"
        f"[dim]Draws analysed :[/dim] {n_draws}   "
        f"[dim]Hits:[/dim] {hit_count}   "
        f"[dim]Rate:[/dim] {hit_rate:.1%}   "
        f"[dim]Baseline:[/dim] {baseline:.1%}\n"
        f"[dim]Gap (min/mean/median/max):[/dim] "
        f"{min_gap} / {mean_gap:.1f} / {med_gap:.0f} / {max_gap}\n"
        f"[dim]Current cold streak:[/dim] {current_cold} draws",
        title=f"📈 Timeline — #{number}",
        border_style="yellow",
    ))

    # ── Hit table ─────────────────────────────────────────────────────────────
    table = Table(
        title=f"{'All draws' if show_all else 'Draws where #{number} appeared'}",
        box=None, padding=(0, 1), header_style="bold",
    )
    table.add_column("Draw", justify="right", style="dim")
    table.add_column("Date", justify="left")
    table.add_column("Numbers", justify="left", style="dim")
    table.add_column("Hit", justify="center")

    display_rows = rows_data if show_all else [r for r in rows_data if r["hit"]]
    # newest first
    for row in reversed(display_rows[-50:]):
        nums_str = " ".join(
            f"[bold yellow]{n}[/bold yellow]" if n == number else str(n)
            for n in row["numbers"]
        )
        hit_sym = "[green]✔[/green]" if row["hit"] else "[dim]·[/dim]"
        table.add_row(row["draw_id"], row["date"], nums_str, hit_sym)

    if display_rows:
        console.print(table)
    else:
        console.print(f"[dim]  #{number} did not appear in the last {n_draws} draws.[/dim]")

    if export_md:
        _append_md(
            export_md, lottery, rules.name, number, _date.today(),
            n_draws, hit_count, hit_rate, baseline, current_cold,
            mean_gap, min_gap, max_gap, med_gap, spark,
        )
        console.print(f"\n[green]✔ Timeline appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, number: int, today: _date,
    n_draws: int, hit_count: int, hit_rate: float, baseline: float,
    current_cold: int, mean_gap: float, min_gap: int, max_gap: int,
    med_gap: float, spark: str,
) -> None:
    tier_str = (
        "HOT"       if hit_rate >= baseline * 1.5 else
        "WARM"      if hit_rate >= baseline else
        "COLD"      if hit_rate >= baseline * 0.5 else
        "VERY COLD"
    )
    content = f"""
---
type: diagnostic
subtype: number-timeline
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
number: {number}
draws_analysed: {n_draws}
hits: {hit_count}
hit_rate: {hit_rate:.4f}
baseline: {baseline:.4f}
current_cold_streak: {current_cold}
mean_gap: {mean_gap:.1f}
tier: {tier_str}
---

## Number Timeline: #{number} — {game_name} ({today.isoformat()})

**Tier:** {tier_str}  ·  **Hits:** {hit_count}/{n_draws} ({hit_rate:.1%})  ·  **Baseline:** {baseline:.1%}
**Current cold streak:** {current_cold} draws  ·  **Gap (min/mean/max):** {min_gap}/{mean_gap:.1f}/{max_gap}

```
{spark}
```
*(oldest → newest; █ = appeared, ░ = not drawn)*

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
