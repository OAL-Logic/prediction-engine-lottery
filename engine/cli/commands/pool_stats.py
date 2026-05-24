"""
Pool Stats Command 📊
=====================
Distributional statistics for draw outcomes across recent history.

Analyses the aggregate properties of draws (not individual numbers):
  • Sum distribution (min/mean/max, percentile bands)
  • Even/Odd ratio distribution
  • Consecutive pairs count (e.g. 3–4, 15–16)
  • Number spread (max – min of drawn numbers)
  • Decade/range distribution
  • Repeat rate (numbers from the previous draw that reappear)

Displays percentile bands so you can validate whether any given ticket
is "within the typical draw envelope" before playing.

Useful for:
  • Understanding what a "typical" draw looks like
  • Checking if your ticket matches historical patterns
  • Spotting outlier draws

Example
-------
  lottery pool-stats br/lotofacil
  lottery pool-stats br/lotofacil --draws 200
  lottery pool-stats br/lotofacil --check 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25
  lottery pool-stats br/lotofacil --export-md stats.md
"""

from __future__ import annotations

import numpy as np
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

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values: list[float]) -> str:
    if not values:
        return ""
    mn, mx = min(values), max(values)
    if mn == mx:
        return _SPARK[4] * len(values)
    return "".join(_SPARK[round((v - mn) / (mx - mn) * 7)] for v in values)


def _pct(values: list[float], p: float) -> float:
    """p-th percentile (0–100)."""
    if not values:
        return 0.0
    sv = sorted(values)
    idx = (len(sv) - 1) * p / 100
    lo, hi = int(idx), min(int(idx) + 1, len(sv) - 1)
    return sv[lo] + (sv[hi] - sv[lo]) * (idx - lo)


def _ticket_props(nums: list[int]) -> dict:
    t = sorted(int(n) for n in nums)
    total_sum = sum(t)
    n_even    = sum(1 for n in t if n % 2 == 0)
    n_cons    = sum(1 for a, b in zip(t, t[1:]) if b == a + 1)
    spread    = (t[-1] - t[0]) if len(t) >= 2 else 0
    return {"sum": float(total_sum), "n_even": float(n_even), "n_cons": float(n_cons), "spread": float(spread)}


def pool_stats(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws:   Annotated[int, typer.Option("--draws", "-n",
        help="How many recent draws to analyse")] = 100,
    check:   Annotated[Optional[list[int]], typer.Option("--check", "-c",
        help="Validate a specific ticket against the distribution")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append stats report to this .md file")] = None,
) -> None:
    """📊 Distributional statistics for draw outcomes.

    Shows sum, even/odd, consecutive, and spread distributions so you
    can tell whether a ticket is 'within the historical envelope'.

    Example: lottery pool-stats br/lotofacil
             lottery pool-stats br/lotofacil --draws 200
             lottery pool-stats br/lotofacil --check 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count

    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # Collect per-draw properties
    sums:    list[float] = []
    evens:   list[float] = []
    consec:  list[float] = []
    spreads: list[float] = []
    repeats: list[float] = []

    prev_set: set[int] = set()
    for row in window.itertuples():
        props = _ticket_props(list(row.numbers))
        sums.append(props["sum"])
        evens.append(props["n_even"])
        consec.append(props["n_cons"])
        spreads.append(props["spread"])
        if prev_set:
            rep = len(set(int(n) for n in row.numbers) & prev_set)
            repeats.append(float(rep))
        prev_set = set(int(n) for n in row.numbers)

    if not sums:
        console.print("[red]No draw data available.[/red]")
        raise typer.Exit(1)

    # ── Stats table ───────────────────────────────────────────────────────────
    def stat_row(name: str, values: list[float], unit: str = "") -> list:
        mn  = min(values)
        mx  = max(values)
        avg = np.mean(values)
        med = np.median(values)
        sd  = np.std(values, ddof=1) if len(values) >= 2 else 0.0
        p10 = _pct(values, 10)
        p90 = _pct(values, 90)
        return [
            name,
            f"{mn:.1f}{unit}",
            f"{p10:.1f}{unit}",
            f"{avg:.1f}{unit}",
            f"{med:.1f}{unit}",
            f"{p90:.1f}{unit}",
            f"{mx:.1f}{unit}",
            f"±{sd:.1f}",
        ]

    stats_table = Table(
        title=f"📊 Draw Property Distributions — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    for col in ["Property", "Min", "P10", "Mean", "Median", "P90", "Max", "StdDev"]:
        stats_table.add_column(col, justify="right" if col != "Property" else "left")

    stats_table.add_row(*stat_row("Sum", sums))
    stats_table.add_row(*stat_row("Even count", evens))
    stats_table.add_row(*stat_row("Odd count",  [pick - e for e in evens]))
    stats_table.add_row(*stat_row("Consecutive pairs", consec))
    stats_table.add_row(*stat_row("Spread (max−min)", spreads))
    if repeats:
        stats_table.add_row(*stat_row("Repeat from prev draw", repeats))

    console.print()
    console.print(stats_table)

    # ── Decade distribution ───────────────────────────────────────────────────
    decade_starts = list(range(lo, hi + 1, 10))
    decade_counts: Counter[int] = Counter()
    for row in window.itertuples():
        for n in row.numbers:
            dec = ((n - lo) // 10) * 10 + lo
            decade_counts[dec] += 1
    total_appearances = sum(decade_counts.values())

    dec_table = Table(
        title="Decade Distribution (avg appearances per draw)",
        box=None, padding=(0, 1), header_style="bold",
    )
    dec_table.add_column("Range", justify="center", style="bold")
    dec_table.add_column("Avg / draw", justify="right")
    dec_table.add_column("Expected",   justify="right", style="dim")
    dec_table.add_column("Δ",          justify="right")

    decade_size = 10
    for ds in decade_starts:
        de = min(ds + decade_size - 1, hi)
        size_in_pool = de - ds + 1
        expected_per_draw = pick * size_in_pool / (hi - lo + 1)
        avg_per_draw = decade_counts.get(ds, 0) / n_draws
        delta = avg_per_draw - expected_per_draw
        delta_fmt = (
            f"[green]+{delta:.2f}[/green]" if delta > 0.2
            else f"[red]{delta:.2f}[/red]" if delta < -0.2
            else f"[dim]{delta:+.2f}[/dim]"
        )
        dec_table.add_row(
            f"{ds}–{de}",
            f"{avg_per_draw:.2f}",
            f"{expected_per_draw:.2f}",
            delta_fmt,
        )

    console.print()
    console.print(dec_table)

    # ── Optional: check a user ticket ─────────────────────────────────────────
    check_result: dict = {}
    if check:
        ticket = sorted(check)
        tp = _ticket_props(ticket)
        t_sum    = tp["sum"]
        t_even   = tp["n_even"]
        t_cons   = tp["n_cons"]
        t_spread = tp["spread"]

        def within_band(val: float, values: list[float]) -> tuple[bool, float]:
            p10 = _pct(values, 10)
            p90 = _pct(values, 90)
            in_band = p10 <= val <= p90
            pctile = sum(1 for v in values if v <= val) / len(values) * 100
            return in_band, pctile

        checks = [
            ("Sum",         t_sum,    sums,    ""),
            ("Even count",  t_even,   evens,   ""),
            ("Consecutive", t_cons,   consec,  ""),
            ("Spread",      t_spread, spreads, ""),
        ]

        chk_table = Table(
            title=f"Ticket Check: {' '.join(str(n) for n in ticket)}",
            box=None, padding=(0, 1), header_style="bold",
        )
        chk_table.add_column("Property",   justify="left")
        chk_table.add_column("Ticket",     justify="right", style="bold yellow")
        chk_table.add_column("Mean",       justify="right", style="dim")
        chk_table.add_column("P10–P90",    justify="center", style="dim")
        chk_table.add_column("In band?",   justify="center")
        chk_table.add_column("Percentile", justify="right")

        n_in_band = 0
        for name, val, vals, unit in checks:
            in_band, pctile = within_band(val, vals)
            if in_band:
                n_in_band += 1
            band_str = f"{_pct(vals,10):.1f}–{_pct(vals,90):.1f}"
            band_flag = "[green]✔[/green]" if in_band else "[yellow]⚠[/yellow]"
            chk_table.add_row(
                name,
                f"{val:.0f}",
                f"{np.mean(vals):.1f}",
                band_str,
                band_flag,
                f"{pctile:.0f}th",
            )

        console.print()
        console.print(chk_table)

        fit_score = n_in_band / len(checks) * 100
        fit_grade = "WITHIN ENVELOPE" if fit_score >= 75 else "BORDERLINE" if fit_score >= 50 else "UNUSUAL"
        fit_colour = "green" if fit_score >= 75 else "yellow" if fit_score >= 50 else "red"

        console.print()
        console.print(Panel(
            f"[{fit_colour}]{n_in_band}/{len(checks)} properties within P10–P90 band[/{fit_colour}]  "
            f"→  [{fit_colour}]{fit_grade}[/{fit_colour}]",
            title="Ticket Fit Assessment",
            border_style=fit_colour,
        ))
        check_result = {"n_in_band": n_in_band, "total": len(checks), "verdict": fit_grade}

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, sums, evens, consec, spreads,
            check if check else [], check_result,
        )
        console.print(f"\n[green]✔ Pool stats appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, sums: list, evens: list, consec: list, spreads: list,
    ticket: list, check_result: dict,
) -> None:
    def fmt_dist(vals: list) -> str:
        if not vals:
            return "N/A"
        return (f"min={min(vals):.1f} mean={np.mean(vals):.1f} "
                f"max={max(vals):.1f} sd={np.std(vals, ddof=1) if len(vals)>1 else 0:.1f}")

    ticket_str = ", ".join(str(n) for n in ticket) if ticket else ""
    verdict = check_result.get("verdict", "")

    content = f"""
---
type: diagnostic
subtype: pool-stats
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
sum_mean: {np.mean(sums):.1f}
sum_p10: {_pct(sums, 10):.1f}
sum_p90: {_pct(sums, 90):.1f}
even_mean: {np.mean(evens):.1f}
checked_ticket: [{ticket_str}]
check_verdict: {verdict}
---

## Pool Stats: {game_name} ({today.isoformat()})

| Property | Min | Mean | Max | P10–P90 |
|----------|-----|------|-----|---------|
| Sum | {min(sums):.1f} | {np.mean(sums):.1f} | {max(sums):.1f} | {_pct(sums,10):.1f}–{_pct(sums,90):.1f} |
| Even count | {min(evens):.1f} | {np.mean(evens):.1f} | {max(evens):.1f} | {_pct(evens,10):.1f}–{_pct(evens,90):.1f} |
| Consecutive | {min(consec):.1f} | {np.mean(consec):.1f} | {max(consec):.1f} | {_pct(consec,10):.1f}–{_pct(consec,90):.1f} |
| Spread | {min(spreads):.1f} | {np.mean(spreads):.1f} | {max(spreads):.1f} | {_pct(spreads,10):.1f}–{_pct(spreads,90):.1f} |

{f"**Checked ticket:** {ticket_str}  →  **{verdict}**" if ticket else ""}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
