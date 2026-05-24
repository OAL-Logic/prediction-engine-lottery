"""
Bonus Ball Command 🎱
=====================
Isolated analytics for the special-pool ball in games like Powerball,
Mega Millions, and EuroMillions.

Unlike the main pool, the bonus ball is drawn from a separate, smaller
pool. This command analyses only the bonus ball numbers so you can see
which special balls are overdue, hot, or structurally biased — without
contaminating the analysis with main-pool statistics.

Metrics
-------
  Frequency   — how often each bonus number has been drawn
  Hot/Cold    — last-seen gap and colour-coded temperature
  Mean gap    — average draws between appearances
  Overdue     — numbers whose current gap exceeds their mean gap

Output
------
  Frequency / hot-cold table (all bonus numbers)
  Overdue panel (numbers beyond their average gap)
  Optional --export-md for Obsidian DataviewJS

Exit codes
----------
  0  — analysis complete
  1  — game has no bonus ball

Example
-------
  lottery bonus-ball us/powerball
  lottery bonus-ball us/mega-millions --draws 200
  lottery bonus-ball eu/euro-millions --top 5
  lottery bonus-ball us/powerball --export-md bonus.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()


def _gap_stats(bonus_col: list[list[int]], ball_idx: int = 0) -> dict[int, dict]:
    """Return {ball: {appearances, last_seen_draws_ago, mean_gap, overdue}} for each bonus number."""
    flat: list[int] = []
    for row in bonus_col:
        if isinstance(row, list) and len(row) > ball_idx:
            flat.append(int(row[ball_idx]))
        elif isinstance(row, (int, float)):
            flat.append(int(row))

    n_draws = len(flat)
    freq: Counter[int] = Counter(flat)

    stats: dict[int, dict] = {}
    for num, count in freq.items():
        positions = [i for i, v in enumerate(flat) if v == num]
        gaps = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
        mean_gap = sum(gaps) / len(gaps) if gaps else float(n_draws)
        last_seen = n_draws - 1 - positions[-1]  # draws since last appearance
        stats[num] = {
            "appearances": count,
            "last_seen": last_seen,
            "mean_gap": mean_gap,
            "overdue": last_seen > mean_gap,
            "freq_pct": count / n_draws * 100 if n_draws else 0.0,
        }

    return stats


def bonus_ball(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. us/powerball)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to analyse")] = 300,
    top: Annotated[int, typer.Option("--top",
        help="Show only the top N most-frequent bonus numbers")] = 0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append bonus-ball report to this .md file")] = None,
) -> None:
    """🎱 Isolated frequency and gap analysis for the bonus/special-pool ball.

    Works with games that have a separate bonus draw pool: Powerball,
    Mega Millions, EuroMillions. Exits with code 1 for main-pool-only games.

    Example: lottery bonus-ball us/powerball
             lottery bonus-ball us/mega-millions --draws 200
             lottery bonus-ball us/powerball --export-md bonus.md
    """
    adapter = get_adapter(lottery)
    rules = adapter.rules

    if not rules.bonus_count or not rules.bonus_range:
        console.print(
            f"[yellow]{rules.name} has no separate bonus ball.[/yellow] "
            "This command is for Powerball, Mega Millions, EuroMillions, etc."
        )
        raise typer.Exit(1)

    blo, bhi = rules.bonus_range
    pool_size = bhi - blo + 1
    n_bonus = rules.bonus_count

    df = adapter.fetch()
    win_df = df.tail(draws)
    bonus_col: list = win_df["bonus"].tolist()

    console.rule(f"[bold cyan]Bonus Ball Analysis: {rules.name}[/bold cyan]")
    console.print(
        f"[dim]Pool: 1–{bhi}  ·  Draws analysed: {len(win_df)}  ·  "
        f"Bonus count per draw: {n_bonus}[/dim]\n"
    )

    # Build stats for ball index 0 (primary bonus / Powerball number)
    stats = _gap_stats(bonus_col, ball_idx=0)

    # All bonus numbers in pool (even if never drawn)
    all_nums = list(range(blo, bhi + 1))
    for n in all_nums:
        if n not in stats:
            stats[n] = {
                "appearances": 0,
                "last_seen": len(win_df),
                "mean_gap": float(len(win_df)),
                "overdue": True,
                "freq_pct": 0.0,
            }

    sorted_nums = sorted(all_nums, key=lambda n: stats[n]["appearances"], reverse=True)
    if top > 0:
        sorted_nums = sorted_nums[:top]

    max_app = max(stats[n]["appearances"] for n in sorted_nums) or 1

    table = Table(
        title=f"Bonus Ball Frequency — {rules.name}",
        box=None, padding=(0, 1), header_style="bold",
    )
    table.add_column("Ball",        justify="center", style="bold yellow")
    table.add_column("Count",       justify="right")
    table.add_column("Freq%",       justify="right", style="dim")
    table.add_column("Last seen",   justify="right", style="dim")
    table.add_column("Mean gap",    justify="right", style="dim")
    table.add_column("Status",      justify="center")

    _BAR = "█"
    _DIM = "░"

    for num in sorted_nums:
        s = stats[num]
        bar_filled = round(s["appearances"] / max_app * 10)
        bar = f"[green]{_BAR * bar_filled}[/green][dim]{_DIM * (10 - bar_filled)}[/dim]"

        if s["appearances"] == 0:
            status = "[dim]NEVER[/dim]"
        elif s["overdue"]:
            status = "[red]OVERDUE[/red]"
        elif s["last_seen"] <= 5:
            status = "[yellow]HOT[/yellow]"
        elif s["last_seen"] > s["mean_gap"] * 0.8:
            status = "[blue]WARMING[/blue]"
        else:
            status = "[dim]NEUTRAL[/dim]"

        table.add_row(
            str(num),
            str(s["appearances"]),
            f"{s['freq_pct']:.1f}%",
            f"{s['last_seen']} ago",
            f"{s['mean_gap']:.1f}",
            status,
        )

    console.print(table)

    # Overdue panel
    overdue = [n for n in all_nums if stats[n]["overdue"] and stats[n]["appearances"] > 0]
    if overdue:
        overdue.sort(key=lambda n: stats[n]["last_seen"] - stats[n]["mean_gap"], reverse=True)
        overdue_str = "  ".join(str(n) for n in overdue[:10])
        console.print()
        console.print(Panel(
            f"[bold yellow]{overdue_str}[/bold yellow]\n"
            f"[dim]{len(overdue)} numbers are overdue (gap > mean gap). "
            "These are not predictions — just structural observations.[/dim]",
            title="📊 Most Overdue Bonus Balls",
            border_style="yellow",
        ))
    else:
        console.print("\n[dim]No bonus numbers currently overdue.[/dim]")

    # Expected frequency for uniform distribution
    expected_pct = 100.0 / pool_size
    hottest = sorted_nums[0]
    coldest = sorted(all_nums, key=lambda n: stats[n]["appearances"])[0]

    console.print(
        f"\n[dim]Expected frequency (uniform): {expected_pct:.1f}%  ·  "
        f"Hottest: {hottest} ({stats[hottest]['freq_pct']:.1f}%)  ·  "
        f"Coldest: {coldest} ({stats[coldest]['freq_pct']:.1f}%)[/dim]"
    )

    if export_md:
        _append_md(export_md, lottery, rules.name, draws, len(win_df),
                   bhi, pool_size, stats, sorted_nums[:10], overdue[:10])
        console.print(f"\n[green]✔ Bonus ball report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str,
    draws: int, n_draws: int, bhi: int, pool_size: int,
    stats: dict, top10: list[int], overdue: list[int],
) -> None:
    today = _date.today().isoformat()
    top_rows = "".join(
        f"| {n} | {stats[n]['appearances']} | {stats[n]['freq_pct']:.1f}% | "
        f"{stats[n]['last_seen']} | {stats[n]['mean_gap']:.1f} |\n"
        for n in top10
    )
    overdue_str = ", ".join(str(n) for n in overdue) if overdue else "none"

    content = f"""
---
type: diagnostic
subtype: bonus-ball
date: {today}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
bonus_pool: {pool_size}
overdue_count: {len(overdue)}
overdue_numbers: [{overdue_str}]
tags: [prediction-engine, bonus-ball, special-pool, pattern-log]
---

## Bonus Ball Analysis: {game_name} ({today})

**Draws analysed:** {n_draws}  ·  **Bonus pool:** 1–{bhi} ({pool_size} numbers)

### Top 10 by Frequency

| Ball | Count | Freq% | Last seen | Mean gap |
|------|-------|-------|-----------|----------|
{top_rows}
**Overdue numbers:** {overdue_str}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
