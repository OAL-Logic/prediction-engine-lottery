"""
Gap Forecast Command 🔮
=======================
Poisson-based overdue analysis for all pool numbers.

For each number, models the gap since last appearance against a Poisson
arrival process (expected gap = pool / pick). Numbers with an unusually
long absence — relative to their historical mean gap — are flagged as
overdue with a probability estimate.

Model
-----
  Expected gap      = pool_size / pick_count  (random baseline)
  Historical mean   = average gap over all appearances
  Adjusted expected = blend of baseline and historical mean
  Overdue score     = current_gap / adjusted_expected
  P(overdue)        = 1 - exp(−overdue_score)  [Poisson CDF]

The Poisson interpretation: if arrivals are memoryless at rate λ = 1/E[gap],
P(overdue) is the probability that a number would have appeared by now if the
process were still active. Values above ~85% indicate genuine rarity.

Useful for:
  • Finding numbers whose absence is statistically unusual
  • Complementing momentum (falling momentum + high overdue → caution)
  • Filtering rank-numbers for "due for a comeback" scenarios

Output
------
  Ranked table      all pool numbers by overdue score (most overdue first)
  Summary panel     top 5 overdue, top 5 fresh, baseline stats

Example
-------
  lottery gap-forecast br/lotofacil
  lottery gap-forecast br/lotofacil --top 10
  lottery gap-forecast br/mega-sena --export-md gap.md
"""

from __future__ import annotations

import math
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_BAR_FULL  = "█"
_BAR_EMPTY = "░"


def _bar(val: float, width: int = 8) -> str:
    filled = round(min(max(val, 0.0), 1.0) * width)
    return _BAR_FULL * filled + _BAR_EMPTY * (width - filled)


def _poisson_cdf(rate: float, current: float) -> float:
    """P(X <= current) for Poisson with mean=rate — uses exponential approximation."""
    if rate <= 0:
        return 0.0
    return 1.0 - math.exp(-current / rate)


def gap_forecast(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    top: Annotated[int, typer.Option("--top", "-N",
        help="Show only top-N most overdue (0 = all)")] = 10,
    min_draws: Annotated[int, typer.Option("--min-draws",
        help="Minimum draws required to compute gaps")] = 30,
    threshold: Annotated[float, typer.Option("--threshold",
        help="P(overdue) threshold to flag a number")] = 0.75,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append gap forecast report to this .md file")] = None,
) -> None:
    """🔮 Poisson-based overdue analysis for all pool numbers.

    Numbers absent far longer than their historical average are flagged
    as overdue with a probability estimate. Sorted by overdue score.

    Example: lottery gap-forecast br/lotofacil
             lottery gap-forecast br/lotofacil --top 15
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = list(range(lo, hi + 1))
    pool_size = hi - lo + 1

    if len(df) < min_draws:
        console.print(f"[dim]Need at least {min_draws} draws; only have {len(df)}.[/dim]")
        raise typer.Exit(0)

    draws = list(df.itertuples())
    n_draws = len(draws)
    baseline_gap = pool_size / pick  # expected gap under random model

    # ── Build per-number gap history ──────────────────────────────────────────
    data: list[dict] = []

    for num in pool:
        # Find all draw indices where this number appeared (0 = oldest)
        appearances = [i for i, row in enumerate(draws) if num in row.numbers]

        if not appearances:
            # Never appeared — treat current gap as full history
            mean_gap   = baseline_gap
            current_gap = float(n_draws)
            last_seen  = n_draws  # draws ago
            n_appear   = 0
        else:
            # Compute gaps between consecutive appearances
            gaps = []
            prev = 0
            for idx in appearances:
                gaps.append(idx - prev)
                prev = idx
            # Gap from last appearance to now
            current_gap = float(n_draws - appearances[-1] - 1)
            last_seen   = n_draws - appearances[-1] - 1
            n_appear    = len(appearances)

            # Use actual mean gap if we have enough data, else blend with baseline
            hist_mean = sum(gaps) / len(gaps) if gaps else baseline_gap
            # Blend: weight toward baseline for sparse histories
            weight = min(n_appear / 10.0, 1.0)
            mean_gap = weight * hist_mean + (1 - weight) * baseline_gap

        overdue_score = current_gap / mean_gap if mean_gap > 0 else 0.0
        p_overdue     = _poisson_cdf(mean_gap, current_gap)

        data.append({
            "num":           num,
            "last_seen":     last_seen,
            "current_gap":   current_gap,
            "mean_gap":      mean_gap,
            "baseline_gap":  baseline_gap,
            "overdue_score": overdue_score,
            "p_overdue":     p_overdue,
            "n_appear":      n_appear,
        })

    # Sort by overdue score descending
    data_sorted = sorted(data, key=lambda d: -d["overdue_score"])

    n_show = top if top > 0 else len(pool)
    display = data_sorted[:n_show]

    # ── Table ─────────────────────────────────────────────────────────────────
    tbl = Table(
        title=f"🔮 Gap Forecast — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Number",       justify="center", style="bold yellow")
    tbl.add_column("Gap",          justify="right")
    tbl.add_column("Mean Gap",     justify="right",  style="dim")
    tbl.add_column("Overdue ×",    justify="right")
    tbl.add_column("P(overdue)",   justify="right")
    tbl.add_column("Status",       justify="center")
    tbl.add_column("Bar",          justify="left")

    for d in display:
        p = d["p_overdue"]
        if p >= threshold:
            status = "[bold red]OVERDUE[/bold red]"
            bar_colour = "red"
        elif p >= 0.50:
            status = "[yellow]WATCH[/yellow]"
            bar_colour = "yellow"
        else:
            status = "[dim]FRESH[/dim]"
            bar_colour = "dim"

        tbl.add_row(
            str(d["num"]),
            str(int(d["current_gap"])),
            f"{d['mean_gap']:.1f}",
            f"{d['overdue_score']:.2f}×",
            f"{p:.1%}",
            status,
            f"[{bar_colour}]{_bar(p)}[/{bar_colour}]",
        )

    console.print()
    console.print(tbl)

    # ── Summary panel ─────────────────────────────────────────────────────────
    overdue_nums = [d for d in data_sorted if d["p_overdue"] >= threshold]
    fresh_nums   = sorted(data, key=lambda d: d["overdue_score"])[:5]

    overdue_str = "  ".join(
        f"#{d['num']} ({d['p_overdue']:.0%})" for d in overdue_nums[:5]
    ) or "none"
    fresh_str = "  ".join(
        f"#{d['num']} ({d['p_overdue']:.0%})" for d in fresh_nums[:5]
    ) or "none"

    console.print()
    console.print(Panel(
        f"[bold red]Overdue (≥{threshold:.0%}):[/bold red]  {overdue_str}\n"
        f"[dim]Fresh (most recent):[/dim]  {fresh_str}\n"
        f"[dim]Baseline gap: {baseline_gap:.1f} draws  ·  "
        f"Overdue count: {len(overdue_nums)}/{pool_size}  ·  "
        f"Threshold: {threshold:.0%}[/dim]",
        title="🔮 Gap Forecast Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, baseline_gap, threshold, overdue_nums, fresh_nums, pool_size,
        )
        console.print(f"\n[green]✔ Gap forecast appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, baseline_gap: float, threshold: float,
    overdue: list, fresh: list, pool_size: int,
) -> None:
    top_o = "  ".join(f"#{d['num']} ({d['p_overdue']:.0%})" for d in overdue[:5])
    top_f = "  ".join(f"#{d['num']} ({d['p_overdue']:.0%})" for d in fresh[:5])

    rows = ""
    for d in overdue[:10]:
        rows += (f"| **{d['num']}** | {int(d['current_gap'])} | "
                 f"{d['mean_gap']:.1f} | {d['overdue_score']:.2f}× | "
                 f"{d['p_overdue']:.1%} | OVERDUE |\n")

    content = f"""
---
type: diagnostic
subtype: gap-forecast
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
baseline_gap: {baseline_gap:.2f}
threshold: {threshold}
overdue_count: {len(overdue)}
pool_size: {pool_size}
---

## Gap Forecast: {game_name} ({today.isoformat()})

**Draws analysed:** {n_draws}  ·  **Baseline gap:** {baseline_gap:.1f}  ·  **Threshold:** {threshold:.0%}
**Overdue numbers:** {len(overdue)}/{pool_size}

**Top overdue:** {top_o}
**Most fresh:** {top_f}

| Number | Gap | Mean Gap | Overdue × | P(overdue) | Status |
|--------|-----|----------|-----------|------------|--------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
