"""
Number Heat Command 🌡️
=====================
Compact heatmap of all pool numbers × recent draws.

Renders a grid where each row is a pool number and each column is a
recent draw, showing exactly when each number appeared. Rows are colour-
coded by overall frequency tier (HOT/WARM/COLD) and sorted by current
frequency (most frequent at top).

Useful for:
  • At-a-glance view of the entire pool in one terminal screen
  • Spotting visual patterns: clusters of hits, cold deserts
  • Quickly identifying which numbers are currently active

Output
------
  Grid       N numbers × M draws (newest draws on the right)
             █ = appeared   ░ = not drawn
  Summary    frequency tiers + current hot/cold zones

Example
-------
  lottery number-heat br/lotofacil
  lottery number-heat br/lotofacil --draws 30
  lottery number-heat br/lotofacil --sort-by streak
  lottery number-heat br/mega-sena --export-md heat.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from engine.cli.utils import get_adapter

console = Console()

_HIT  = "█"
_MISS = "░"


def number_heat(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="How many recent draws to show in the grid")] = 30,
    sort_by: Annotated[str, typer.Option("--sort-by",
        help="Sort rows by: freq | streak | number")] = "freq",
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append heatmap to this .md file")] = None,
) -> None:
    """🌡️ Compact heatmap of all pool numbers × recent draws.

    Each row = one pool number; each column = one recent draw.
    █ = appeared, ░ = not drawn. Rows sorted by frequency by default.

    Example: lottery number-heat br/lotofacil
             lottery number-heat br/lotofacil --draws 30
             lottery number-heat br/lotofacil --sort-by streak
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = list(range(lo, hi + 1))
    pool_size = hi - lo + 1

    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # Build hit matrix: pool_num → list[bool] (oldest first)
    hits: dict[int, list[bool]] = {n: [] for n in pool}
    for row in window.itertuples():
        nums_in_draw = set(row.numbers)
        for n in pool:
            hits[n].append(n in nums_in_draw)

    # ── Frequency & streak per number ─────────────────────────────────────────
    freq: dict[int, int] = {n: sum(hits[n]) for n in pool}
    baseline = pick / pool_size

    def _current_streak(n: int) -> int:
        h = hits[n]
        if not h:
            return 0
        streak = 0
        val = h[-1]
        for v in reversed(h):
            if v == val:
                streak += 1
            else:
                break
        return streak if val else -streak

    streaks: dict[int, int] = {n: _current_streak(n) for n in pool}

    # ── Sort order ────────────────────────────────────────────────────────────
    if sort_by == "streak":
        sorted_pool = sorted(pool, key=lambda n: -streaks[n])
    elif sort_by == "number":
        sorted_pool = sorted(pool)
    else:  # "freq" (default)
        sorted_pool = sorted(pool, key=lambda n: -freq[n])

    # ── Render grid ───────────────────────────────────────────────────────────
    expected_per_window = baseline * n_draws

    # Column header (draw index, newest=right): just show tick marks every 5
    header = ""
    for i in range(n_draws):
        if (i + 1) % 5 == 0:
            header += "|"
        else:
            header += " "

    console.print()
    console.print(
        f"[bold]{rules.name}[/bold]  [dim](last {n_draws} draws, oldest → newest)[/dim]"
    )
    console.print(f"  [dim]{'':3}  {header}  freq  streak[/dim]")

    for n in sorted_pool:
        h     = hits[n]
        f     = freq[n]
        stk   = streaks[n]
        ratio = f / expected_per_window if expected_per_window > 0 else 0.5

        # Colour tier
        if ratio >= 1.4:
            colour = "bold green"
            tier   = "H"
        elif ratio >= 0.8:
            colour = "green"
            tier   = "W"
        elif ratio >= 0.4:
            colour = "dim"
            tier   = "C"
        else:
            colour = "dim"
            tier   = "V"

        # Build the hit row
        row_text = Text()
        row_text.append(f"  {n:3}  ", style=colour)
        for hit in h:
            row_text.append(_HIT if hit else _MISS, style="green" if hit else "dim")
        # Freq bar (4 chars)
        bar_filled = round(min(f / n_draws, 1.0) * 4)
        bar_str = "█" * bar_filled + "░" * (4 - bar_filled)
        row_text.append(f"  {f:3}  ", style="dim")
        row_text.append(bar_str, style=colour)

        # Streak indicator
        if stk > 0:
            row_text.append(f"  +{stk}", style="bold green")
        elif stk < 0:
            row_text.append(f"  {stk}", style="cyan")
        else:
            row_text.append("   0", style="dim")

        console.print(row_text)

    # ── Summary panel ─────────────────────────────────────────────────────────
    n_hot  = sum(1 for n in pool if freq[n] / expected_per_window >= 1.4)
    n_warm = sum(1 for n in pool if 0.8 <= freq[n] / expected_per_window < 1.4)
    n_cold = sum(1 for n in pool if freq[n] / expected_per_window < 0.8)

    hottest_n  = max(pool, key=lambda n: freq[n])
    coldest_n  = min(pool, key=lambda n: freq[n])
    lon_hot_stk = max(pool, key=lambda n: streaks[n])
    lon_cold_stk = min(pool, key=lambda n: streaks[n])

    console.print()
    console.print(Panel(
        f"[dim]Pool:[/dim] {pool_size}  ·  "
        f"[bold green]HOT:[/bold green] {n_hot}  "
        f"[green]WARM:[/green] {n_warm}  "
        f"[dim]COLD:[/dim] {n_cold}\n"
        f"[dim]Hottest:[/dim] #{hottest_n} ({freq[hottest_n]} hits)  ·  "
        f"[dim]Coldest:[/dim] #{coldest_n} ({freq[coldest_n]} hits)\n"
        f"[dim]Longest hot run:[/dim] #{lon_hot_stk} (+{streaks[lon_hot_stk]})  ·  "
        f"[dim]Longest cold run:[/dim] #{lon_cold_stk} ({streaks[lon_cold_stk]})",
        title="🌡️ Pool Heatmap Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, pool, hits, freq, streaks, n_hot, n_warm, n_cold,
            hottest_n, coldest_n,
        )
        console.print(f"\n[green]✔ Heatmap appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, pool: list[int], hits: dict, freq: dict, streaks: dict,
    n_hot: int, n_warm: int, n_cold: int,
    hottest: int, coldest: int,
) -> None:
    # Build compact ASCII grid (numbers sorted by freq)
    sorted_pool = sorted(pool, key=lambda n: -freq[n])
    grid_lines = ""
    for n in sorted_pool:
        row = "".join("█" if h else "░" for h in hits[n])
        grid_lines += f"{n:3}: {row}  {freq[n]:3}\n"

    content = f"""
---
type: diagnostic
subtype: number-heat
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_shown: {n_draws}
hot_count: {n_hot}
warm_count: {n_warm}
cold_count: {n_cold}
hottest_number: {hottest}
coldest_number: {coldest}
---

## Number Heatmap: {game_name} ({today.isoformat()})

Last {n_draws} draws (oldest → newest). █=hit ░=miss. Sorted by frequency.

```
{game_name} — last {n_draws} draws
{grid_lines}```

**HOT:** {n_hot}  ·  **WARM:** {n_warm}  ·  **COLD:** {n_cold}
**Hottest:** #{hottest} ({freq[hottest]} hits)  ·  **Coldest:** #{coldest} ({freq[coldest]} hits)

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
