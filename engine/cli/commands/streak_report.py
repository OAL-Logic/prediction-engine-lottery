"""
Streak Report Command 🔥
========================
All-pool hot/cold streak overview for the most recent draws.

For every number in the pool, computes its current consecutive run:
  +N = appeared in each of the last N draws (hot streak)
  -N = absent from each of the last N draws (cold streak)

Shows two ranked tables — hottest and coldest — and flags numbers
whose current streak exceeds their historical maximum streak by ≥20%
(statistically unusual, either notably overdue or on an abnormal run).

Complement to `number-timeline` (single-number deep-dive); this command
gives the full-pool snapshot in one view.

Output
------
  Hot streak table    numbers currently on consecutive hit runs
  Cold streak table   numbers currently absent for longest spans
  Extremes panel      pool numbers at historical streak records

Example
-------
  lottery streak-report br/lotofacil
  lottery streak-report br/lotofacil --draws 200 --top 10
  lottery streak-report br/mega-sena --export-md streaks.md
"""

from __future__ import annotations

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


def _current_streak(hits: list[bool]) -> int:
    """Return +N (hot) or -N (cold) from newest end of hits list."""
    if not hits:
        return 0
    streak = 0
    val = hits[-1]
    for h in reversed(hits):
        if h == val:
            streak += 1
        else:
            break
    return streak if val else -streak


def _max_streak(hits: list[bool]) -> tuple[int, int]:
    """Return (max_hot_streak, max_cold_streak) over full history."""
    max_hot = max_cold = 0
    cur_hot = cur_cold = 0
    for h in hits:
        if h:
            cur_hot += 1
            max_hot = max(max_hot, cur_hot)
            cur_cold = 0
        else:
            cur_cold += 1
            max_cold = max(max_cold, cur_cold)
            cur_hot = 0
    return max_hot, max_cold


def _mini_spark(hits: list[bool], width: int = 20) -> str:
    recent = hits[-width:]
    return "".join(_SPARK_ON if h else _SPARK_OFF for h in recent)


def streak_report(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="How many recent draws to analyse")] = 100,
    top: Annotated[int, typer.Option("--top", "-t",
        help="How many numbers to show in each table")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append streak report to this .md file")] = None,
) -> None:
    """🔥 All-pool hot/cold streak overview.

    Shows which numbers are on the longest consecutive hit/miss runs
    and flags any that are at or near their historical record streaks.

    Example: lottery streak-report br/lotofacil
             lottery streak-report br/lotofacil --draws 200 --top 10
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pool    = list(range(lo, hi + 1))
    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # Build hit sequences for every pool number
    hit_seq: dict[int, list[bool]] = {n: [] for n in pool}
    for row in window.itertuples():
        nums_in_draw = set(row.numbers)
        for n in pool:
            hit_seq[n].append(n in nums_in_draw)

    # Compute streaks and record extremes
    data: list[dict] = []
    for n in pool:
        h = hit_seq[n]
        cur   = _current_streak(h)
        mxh, mxc = _max_streak(h)
        data.append({
            "num":      n,
            "streak":   cur,
            "max_hot":  mxh,
            "max_cold": mxc,
            "hits":     h,
            "at_record": (
                cur > 0 and mxh > 0 and cur >= mxh * 0.8
                or cur < 0 and mxc > 0 and abs(cur) >= mxc * 0.8
            ),
        })

    hot_sorted  = sorted([d for d in data if d["streak"] > 0],
                         key=lambda d: d["streak"], reverse=True)
    cold_sorted = sorted([d for d in data if d["streak"] < 0],
                         key=lambda d: d["streak"])

    n_top = min(top, len(hot_sorted), len(cold_sorted)) if top > 0 else len(data)
    n_top = max(n_top, 1)

    # ── Hot streak table ──────────────────────────────────────────────────────
    hot_table = Table(
        title=f"🔥 Hottest Numbers — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    hot_table.add_column("Number",  justify="center", style="bold yellow")
    hot_table.add_column("Streak",  justify="right",  style="bold green")
    hot_table.add_column("Max Hot", justify="right",  style="dim")
    hot_table.add_column("Record?", justify="center")
    hot_table.add_column("Recent 20", justify="left",  style="green")

    for d in hot_sorted[:n_top]:
        rec_flag = "[bold red]★[/bold red]" if d["at_record"] else "[dim]·[/dim]"
        hot_table.add_row(
            str(d["num"]),
            f"+{d['streak']}",
            str(d["max_hot"]),
            rec_flag,
            _mini_spark(d["hits"]),
        )

    console.print()
    console.print(hot_table)

    # ── Cold streak table ─────────────────────────────────────────────────────
    cold_table = Table(
        title=f"❄️  Coldest Numbers — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    cold_table.add_column("Number",   justify="center", style="bold yellow")
    cold_table.add_column("Streak",   justify="right",  style="bold cyan")
    cold_table.add_column("Max Cold", justify="right",  style="dim")
    cold_table.add_column("Record?",  justify="center")
    cold_table.add_column("Recent 20", justify="left",  style="dim")

    for d in cold_sorted[:n_top]:
        rec_flag = "[bold red]★[/bold red]" if d["at_record"] else "[dim]·[/dim]"
        cold_table.add_row(
            str(d["num"]),
            str(d["streak"]),
            str(d["max_cold"]),
            rec_flag,
            _mini_spark(d["hits"]),
        )

    console.print()
    console.print(cold_table)

    # ── Extremes panel ────────────────────────────────────────────────────────
    at_record = [d for d in data if d["at_record"]]
    hottest_num  = max(data, key=lambda d: d["streak"])
    coldest_num  = min(data, key=lambda d: d["streak"])
    avg_hot  = (sum(d["streak"] for d in data if d["streak"] > 0)
                / max(1, sum(1 for d in data if d["streak"] > 0)))
    avg_cold = (sum(abs(d["streak"]) for d in data if d["streak"] < 0)
                / max(1, sum(1 for d in data if d["streak"] < 0)))
    n_neutral = sum(1 for d in data if d["streak"] == 0)

    record_nums = ", ".join(str(d["num"]) for d in at_record) if at_record else "none"

    console.print()
    console.print(Panel(
        f"[bold green]Hottest:[/bold green] #{hottest_num['num']} (+{hottest_num['streak']} draws)   "
        f"[bold cyan]Coldest:[/bold cyan] #{coldest_num['num']} ({coldest_num['streak']} draws)\n"
        f"[dim]Avg hot streak: {avg_hot:.1f}  ·  Avg cold streak: {avg_cold:.1f}  ·  "
        f"Neutral (appeared last draw then missed or vice versa): {n_neutral}\n"
        f"At/near historical record: {record_nums}[/dim]",
        title="🔥❄️  Streak Extremes",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, hot_sorted[:n_top], cold_sorted[:n_top],
            hottest_num, coldest_num, at_record,
        )
        console.print(f"\n[green]✔ Streak report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, hot_top: list[dict], cold_top: list[dict],
    hottest: dict, coldest: dict, at_record: list[dict],
) -> None:
    hottest_num  = hottest["num"]
    hottest_str  = hottest["streak"]
    coldest_num  = coldest["num"]
    coldest_str  = coldest["streak"]
    record_nums  = ", ".join(str(d["num"]) for d in at_record) if at_record else "none"

    hot_rows = "".join(
        f"| **{d['num']}** | +{d['streak']} | {d['max_hot']} | "
        f"{'★' if d['at_record'] else ''} |\n"
        for d in hot_top
    )
    cold_rows = "".join(
        f"| **{d['num']}** | {d['streak']} | {d['max_cold']} | "
        f"{'★' if d['at_record'] else ''} |\n"
        for d in cold_top
    )

    content = f"""
---
type: diagnostic
subtype: streak-report
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
hottest_number: {hottest_num}
hottest_streak: {hottest_str}
coldest_number: {coldest_num}
coldest_streak: {coldest_str}
at_record_numbers: [{record_nums}]
---

## Streak Report: {game_name} ({today.isoformat()})

**Hottest:** #{hottest_num} (+{hottest_str})  ·  **Coldest:** #{coldest_num} ({coldest_str})
**At/near record:** {record_nums}

### Hot Streaks

| Number | Current | Max Hot | Record |
|--------|---------|---------|--------|
{hot_rows}
### Cold Streaks

| Number | Current | Max Cold | Record |
|--------|---------|----------|--------|
{cold_rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
