"""
Calendar Effect Command 📆
==========================
Weekday and month-of-year bias detector for draw properties.

Some lotteries draw multiple times per week (e.g. Monday, Wednesday,
Saturday). This command tests whether the weekday or month of a draw
correlates with structural properties (sum, parity, consecutive count).

The honest answer is usually "no significant effect" — truly random
draws are independent of the calendar. But this command makes that
finding *rigorous* rather than assumed, which is useful for:
  • Ruling out weekday-based betting strategies definitively
  • Identifying true anomalies if a game changed mechanics on a date
  • Confirming that holiday draws (mega-virada, special editions) are
    structurally different from regular draws

Algorithm
---------
For each calendar dimension (weekday, month), group draws.
For each property (sum, parity, consecutive), compute per-group mean
and std, then the overall grand mean.

Effect size (Cohen's d proxy):
  d = (group_mean − grand_mean) / grand_std

Groups with |d| ≥ 0.5 are notable; ≥ 0.8 are substantial.
A chi-squared-style flag is raised if max |d| ≥ 0.5.

Output
------
  Weekday table    mean sum/parity/consec per weekday (if multi-draw week)
  Month table      mean sum/parity/consec per month
  Summary panel    strongest effect, verdict

Example
-------
  lottery calendar-effect br/lotofacil
  lottery calendar-effect br/mega-sena --draws 500
  lottery calendar-effect br/lotofacil --export-md calendar.md
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS   = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _stats(values: list[float]) -> tuple[float, float]:
    """Return (mean, std) for a list."""
    if not values:
        return 0.0, 0.0
    n   = len(values)
    mu  = sum(values) / n
    std = (sum((v - mu) ** 2 for v in values) / n) ** 0.5
    return mu, std


def _row_features(nums: list[int]) -> dict[str, float]:
    s = sorted(nums)
    return {
        "sum":    float(sum(s)),
        "parity": sum(1 for n in s if n % 2 == 0) / len(s),
        "consec": float(sum(1 for a, b in zip(s, s[1:]) if b == a + 1)),
    }


PROP_NAMES = ["sum", "parity", "consec"]
PROP_FMT   = [".1f", ".3f", ".2f"]


def calendar_effect(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws to analyse")] = 400,
    effect_threshold: Annotated[float, typer.Option("--effect", "-e",
        help="Cohen's d threshold to flag a notable effect")] = 0.5,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append calendar effect report to this .md file")] = None,
) -> None:
    """📆 Weekday and month-of-year bias detector for draw properties.

    Tests whether the calendar day or month of a draw correlates with
    structural properties. Typically shows no effect (confirming independence);
    flags genuine anomalies when found.

    Example: lottery calendar-effect br/lotofacil
             lottery calendar-effect br/mega-sena --draws 500
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    n_draws  = min(draws, len(df))
    window   = df.tail(n_draws)

    # ── Parse rows into calendar buckets ──────────────────────────────────
    wd_buckets: dict[int, list[dict]] = defaultdict(list)  # 0=Mon
    mo_buckets: dict[int, list[dict]] = defaultdict(list)  # 1=Jan

    valid = 0
    for row in window.itertuples():
        if row.numbers is None or len(row.numbers) == 0:
            continue
        if row.date is None:
            continue
        try:
            dt = row.date
            if hasattr(dt, "date"):
                dt = dt.date()
            wd = dt.weekday()  # 0=Monday
            mo = dt.month      # 1=January
        except (AttributeError, TypeError):
            continue
        feats = _row_features(list(row.numbers))
        wd_buckets[wd].append(feats)
        mo_buckets[mo].append(feats)
        valid += 1

    if valid < 20:
        console.print("[dim]Not enough dated draws for calendar analysis.[/dim]")
        raise typer.Exit(0)

    # ── Grand stats ────────────────────────────────────────────────────────
    all_feats = [f for feats in wd_buckets.values() for f in feats]
    grand: dict[str, tuple[float, float]] = {
        p: _stats([f[p] for f in all_feats]) for p in PROP_NAMES
    }

    # ── Build comparison tables ────────────────────────────────────────────
    def _effect_d(group_mean: float, prop: str) -> float:
        mu, std = grand[prop]
        if std == 0:
            return 0.0
        return (group_mean - mu) / std

    def _make_table(title: str, buckets: dict, label_map: list[str]) -> tuple[Table, float]:
        tbl = Table(title=title, box=None, padding=(0, 1), header_style="bold")
        tbl.add_column("Group",  justify="center", style="bold yellow")
        tbl.add_column("n",      justify="right",  style="dim")
        for p, fmt in zip(PROP_NAMES, PROP_FMT):
            tbl.add_column(p.capitalize(), justify="right")
            tbl.add_column("d",            justify="right", style="dim")

        max_d = 0.0
        for idx in sorted(buckets.keys()):
            feats = buckets[idx]
            if not feats:
                continue
            label = label_map[idx] if idx < len(label_map) else str(idx)
            n     = len(feats)
            cells: list[str] = [label, str(n)]
            for p, fmt in zip(PROP_NAMES, PROP_FMT):
                mu, _ = _stats([f[p] for f in feats])
                d     = _effect_d(mu, p)
                max_d = max(max_d, abs(d))
                d_col = "red" if abs(d) >= 0.8 else "yellow" if abs(d) >= 0.5 else "dim"
                cells += [format(mu, fmt), f"[{d_col}]{d:+.2f}[/{d_col}]"]
            tbl.add_row(*cells)

        return tbl, max_d

    wd_tbl, wd_max_d = _make_table(
        f"📆 Weekday Effect — {rules.name}  (n={valid})",
        wd_buckets,
        _WEEKDAYS,
    )
    mo_tbl, mo_max_d = _make_table(
        f"📆 Month Effect — {rules.name}  (n={valid})",
        mo_buckets,
        [""] + _MONTHS,  # 1-indexed months
    )

    # ── Grand stats row ────────────────────────────────────────────────────
    console.print()
    console.print(wd_tbl)
    console.print()
    console.print(mo_tbl)

    # ── Summary ────────────────────────────────────────────────────────────
    overall_max_d = max(wd_max_d, mo_max_d)
    if overall_max_d >= 0.8:
        verdict = f"[red]SUBSTANTIAL effect found (max |d|={overall_max_d:.2f}) — investigate further[/red]"
    elif overall_max_d >= effect_threshold:
        verdict = f"[yellow]NOTABLE effect found (max |d|={overall_max_d:.2f}) — possibly coincidental with n={valid}[/yellow]"
    else:
        verdict = f"[green]NO significant effect (max |d|={overall_max_d:.2f}) — draw properties are calendar-independent[/green]"

    grand_sum_mu, grand_sum_std = grand["sum"]
    grand_par_mu, _ = grand["parity"]

    console.print()
    console.print(Panel(
        f"{verdict}\n\n"
        f"[dim]Grand mean: sum={grand_sum_mu:.1f} (±{grand_sum_std:.1f})  "
        f"parity={grand_par_mu:.3f}\n"
        f"Weekday max |d|: {wd_max_d:.2f}  ·  Month max |d|: {mo_max_d:.2f}\n"
        f"Effect threshold: ±{effect_threshold}  ·  Draws analysed: {valid}[/dim]",
        title="📆 Calendar Effect Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            valid, effect_threshold, wd_max_d, mo_max_d, overall_max_d,
            grand_sum_mu, grand_sum_std,
        )
        console.print(f"\n[green]✔ Calendar effect report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n: int, threshold: float, wd_max_d: float, mo_max_d: float,
    overall_max_d: float, grand_sum_mu: float, grand_sum_std: float,
) -> None:
    verdict = (
        "SUBSTANTIAL" if overall_max_d >= 0.8
        else "NOTABLE" if overall_max_d >= threshold
        else "NONE"
    )
    content = f"""
---
type: diagnostic
subtype: calendar-effect
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n}
effect_threshold: {threshold}
weekday_max_d: {wd_max_d:.4f}
month_max_d: {mo_max_d:.4f}
overall_max_d: {overall_max_d:.4f}
verdict: {verdict}
grand_sum_mean: {grand_sum_mu:.2f}
grand_sum_std: {grand_sum_std:.2f}
---

## Calendar Effect: {game_name} ({today.isoformat()})

**Draws analysed:** {n}  ·  **Effect threshold:** {threshold}
**Weekday max |d|:** {wd_max_d:.2f}  ·  **Month max |d|:** {mo_max_d:.2f}
**Verdict:** {verdict}

Grand mean sum: {grand_sum_mu:.1f} ± {grand_sum_std:.1f}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
