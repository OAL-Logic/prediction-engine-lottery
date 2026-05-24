"""
Draw Clock Command ⏰
====================
Draws-until-next-expected-hit countdown for every pool number.

Uses each number's empirical hit rate to estimate how many more draws
are expected before its next appearance. Combines:
  • Hit rate   — fraction of draws where this number appeared
  • Current gap — draws since last appearance
  • Expected next — 1/hit_rate draws per cycle; "draws remaining" =
                    max(0, expected_next − current_gap)

Numbers with draws_remaining = 0 are "DUE NOW"; negative means overdue.
Numbers with draws_remaining > 2× expected are cooling off fast.

Useful for:
  • Quick "who's due next draw" scan without full Poisson math
  • Cron alert: which numbers are expected this draw vs next week
  • Complementing gap-forecast (probability) with a concrete draw count

Output
------
  Clock table   all pool numbers sorted by draws_remaining (ascending)
  Due-now panel numbers expected this draw or already overdue
  Summary       earliest expected, mean gap stats

Example
-------
  lottery draw-clock br/lotofacil
  lottery draw-clock br/lotofacil --top 15
  lottery draw-clock br/mega-sena --export-md clock.md
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

_SPARK = "▁▂▃▄▅▆▇█"


def _spark_bar(val: float, width: int = 8) -> str:
    """Horizontal bar 0→width."""
    filled = round(min(max(val, 0.0), 1.0) * width)
    return "█" * filled + "░" * (width - filled)


def draw_clock(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    top: Annotated[int, typer.Option("--top", "-N",
        help="Show only top-N most-due numbers (0 = all)")] = 15,
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Draws to use for hit-rate estimation")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append draw clock report to this .md file")] = None,
) -> None:
    """⏰ Draws-until-next-hit countdown for every pool number.

    Estimates how many more draws before each number is statistically
    expected to appear, based on its empirical hit rate.

    Example: lottery draw-clock br/lotofacil
             lottery draw-clock br/lotofacil --top 20
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pool     = list(range(lo, hi + 1))
    pool_size = hi - lo + 1
    pick     = rules.pick_count

    n_draws  = min(window, len(df))
    if n_draws < 10:
        console.print(f"[dim]Need at least 10 draws; only have {len(df)}.[/dim]")
        raise typer.Exit(0)

    rate_window = df.tail(n_draws)
    all_rows    = list(df.itertuples())
    total_rows  = len(all_rows)

    baseline_rate = pick / pool_size

    data: list[dict] = []
    for num in pool:
        # Hit rate over estimation window
        hits_in_window = sum(1 for row in rate_window.itertuples() if num in row.numbers)
        hit_rate = hits_in_window / n_draws if n_draws > 0 else baseline_rate

        # Avoid division-by-zero for numbers that never appeared in window
        if hit_rate == 0:
            hit_rate = baseline_rate

        expected_gap = 1.0 / hit_rate  # average draws per appearance

        # Current gap: draws since last appearance in full history
        last_idx = None
        for i in range(total_rows - 1, -1, -1):
            if num in all_rows[i].numbers:
                last_idx = i
                break

        if last_idx is None:
            current_gap = float(total_rows)
        else:
            current_gap = float(total_rows - last_idx - 1)

        draws_remaining = max(0.0, expected_gap - current_gap)
        overdue_by      = max(0.0, current_gap - expected_gap)

        data.append({
            "num":             num,
            "hit_rate":        hit_rate,
            "expected_gap":    expected_gap,
            "current_gap":     current_gap,
            "draws_remaining": draws_remaining,
            "overdue_by":      overdue_by,
            "due_now":         draws_remaining == 0,
        })

    # Sort by draws_remaining ascending (most due first)
    data_sorted = sorted(data, key=lambda d: d["draws_remaining"])

    n_show  = top if top > 0 else len(pool)
    display = data_sorted[:n_show]

    max_remaining = max(d["draws_remaining"] for d in data) if data else 1.0

    # ── Clock table ────────────────────────────────────────────────────────
    tbl = Table(
        title=f"⏰ Draw Clock — {rules.name}  (rate window: {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Number",    justify="center", style="bold yellow")
    tbl.add_column("Rate%",     justify="right")
    tbl.add_column("Exp. Gap",  justify="right",  style="dim")
    tbl.add_column("Gap Now",   justify="right")
    tbl.add_column("Due In",    justify="right")
    tbl.add_column("Status",    justify="center")
    tbl.add_column("Urgency",   justify="left")

    for d in display:
        dr = d["draws_remaining"]
        if dr == 0:
            status = "[bold red]DUE NOW[/bold red]"
            urgency_val = 1.0
            col = "red"
        elif dr <= 1:
            status = "[red]SOON[/red]"
            urgency_val = 0.85
            col = "red"
        elif dr <= d["expected_gap"] * 0.5:
            status = "[yellow]NEAR[/yellow]"
            urgency_val = 0.5
            col = "yellow"
        else:
            status = "[dim]WAIT[/dim]"
            urgency_val = max(0.0, 1.0 - dr / (max_remaining + 1))
            col = "dim"

        tbl.add_row(
            str(d["num"]),
            f"{d['hit_rate']:.1%}",
            f"{d['expected_gap']:.1f}",
            str(int(d["current_gap"])),
            str(int(dr)) if dr > 0 else "0 (overdue)",
            status,
            f"[{col}]{_spark_bar(urgency_val)}[/{col}]",
        )

    console.print()
    console.print(tbl)

    # ── Due-now panel ──────────────────────────────────────────────────────
    due_now   = [d for d in data_sorted if d["due_now"]]
    due_soon  = [d for d in data_sorted if not d["due_now"] and d["draws_remaining"] <= 2]

    due_str  = "  ".join(f"#{d['num']}" for d in due_now[:10])  or "none"
    soon_str = "  ".join(
        f"#{d['num']} ({int(d['draws_remaining'])})" for d in due_soon[:5]
    ) or "none"

    mean_gap = sum(d["expected_gap"] for d in data) / len(data) if data else 0

    console.print()
    console.print(Panel(
        f"[bold red]Due now:[/bold red]   {due_str}\n"
        f"[yellow]Due in 1–2:[/yellow]  {soon_str}\n"
        f"[dim]Mean expected gap: {mean_gap:.1f} draws  ·  "
        f"Baseline: {baseline_rate:.1%}/draw  ·  "
        f"Rate window: {n_draws} draws[/dim]",
        title="⏰ Draw Clock Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, baseline_rate, due_now, due_soon, data_sorted[:10],
        )
        console.print(f"\n[green]✔ Draw clock appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, baseline_rate: float,
    due_now: list, due_soon: list, top10: list,
) -> None:
    due_str  = ", ".join(f"#{d['num']}" for d in due_now[:10]) or "none"
    soon_str = ", ".join(f"#{d['num']} ({int(d['draws_remaining'])})" for d in due_soon[:5]) or "none"

    rows = ""
    for d in top10:
        rows += (f"| **{d['num']}** | {d['hit_rate']:.1%} | "
                 f"{d['expected_gap']:.1f} | {int(d['current_gap'])} | "
                 f"{int(d['draws_remaining'])} |\n")

    content = f"""
---
type: diagnostic
subtype: draw-clock
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
rate_window: {n_draws}
baseline_rate: {baseline_rate:.4f}
due_now_count: {len(due_now)}
due_soon_count: {len(due_soon)}
---

## Draw Clock: {game_name} ({today.isoformat()})

**Rate window:** {n_draws} draws  ·  **Baseline:** {baseline_rate:.1%}/draw
**Due now:** {due_str}
**Due in 1–2 draws:** {soon_str}

| Number | Rate% | Exp. Gap | Gap Now | Due In |
|--------|-------|----------|---------|--------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
