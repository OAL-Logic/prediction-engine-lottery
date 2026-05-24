"""
Variance Report Command 📉
==========================
Analyses the volatility regime of a lottery's draw process.

Measures how much variance there is in:
  1. Number frequency distribution (are some numbers drawn far more often?)
  2. Draw sum variance (are sums clustered or spread out?)
  3. Parity variance (how much does even/odd mix fluctuate?)
  4. Consecutive run variance (do consecutive number runs spike?)
  5. Confidence score volatility (strategy confidence standard deviation)

A low-variance regime means the draw process is highly uniform — strategies
based on historical patterns are likely to be unstable. A high-variance
regime means certain numbers/patterns are genuinely over/under-represented.

Output
------
  Variance table    per-dimension variance metric + tier (HIGH/MED/LOW)
  Trend sparkline   rolling 20-draw variance (is volatility changing?)
  Summary panel     overall volatility verdict + actionability score

Example
-------
  lottery variance-report br/lotofacil
  lottery variance-report br/lotofacil --draws 200
  lottery variance-report br/mega-sena --export-md variance.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
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


def variance_report(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to analyse")] = 100,
    rolling: Annotated[int, typer.Option("--rolling", "-r",
        help="Window size for rolling variance trend")] = 20,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append variance report to this .md file")] = None,
) -> None:
    """📉 Volatility regime analysis — how predictable is the draw process?

    Measures variance across 5 dimensions: frequency distribution,
    sum variance, parity variance, consecutive runs, and strategy
    confidence volatility.

    Example: lottery variance-report br/lotofacil
             lottery variance-report br/lotofacil --draws 200
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = hi - lo + 1

    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # ── Per-draw properties ───────────────────────────────────────────────────
    sums:    list[float] = []
    evens:   list[float] = []
    consec:  list[float] = []
    freq_cv_per_window: list[float] = []   # for rolling trend

    for row in window.itertuples():
        nums = sorted(int(x) for x in row.numbers)
        sums.append(float(sum(nums)))
        evens.append(float(sum(1 for n in nums if n % 2 == 0)))
        consec.append(float(sum(1 for a, b in zip(nums, nums[1:]) if b == a + 1)))

    # ── Dimension 1: Frequency distribution variance ──────────────────────────
    freq_counts: Counter[int] = Counter()
    for row in window.itertuples():
        for n in row.numbers:
            freq_counts[int(n)] += 1
    all_freqs = [float(freq_counts.get(n, 0)) for n in range(lo, hi + 1)]
    expected_freq = n_draws * pick / pool
    # Coefficient of variation: std / mean
    freq_cv = np.std(all_freqs, ddof=1) / (expected_freq + 1e-9)

    # ── Dimension 2: Sum variance (CV of draw sums) ───────────────────────────
    sum_cv = np.std(sums, ddof=1) / (np.mean(sums) + 1e-9) if len(sums) >= 2 else 0.0

    # ── Dimension 3: Parity variance ──────────────────────────────────────────
    parity_cv = np.std(evens, ddof=1) / (np.mean(evens) + 1e-9) if len(evens) >= 2 else 0.0

    # ── Dimension 4: Consecutive run variance ─────────────────────────────────
    consec_cv = np.std(consec, ddof=1) / (np.mean(consec) + 0.1 + 1e-9) if len(consec) >= 2 else 0.0

    # ── Dimension 5: Strategy confidence volatility ───────────────────────────
    conf_cv = 0.5  # default neutral
    try:
        from engine.strategies import get_strategy
        strat = get_strategy("bayesian")
        step = max(1, n_draws // 10)
        confs = []
        for i in range(0, n_draws, step):
            sub = window.iloc[max(0, i):i + step + 20]
            if len(sub) < 20:
                continue
            try:
                res = strat.suggest(sub, rules, count=1, temperature=0.0)
                confs.append(res.confidence)
            except Exception:
                pass
        if len(confs) >= 2:
            conf_cv = np.std(confs, ddof=1) / (np.mean(confs) + 1e-9)
    except Exception:
        pass

    # ── Rolling variance trend (freq_cv over rolling windows) ────────────────
    n_windows = max(1, n_draws // rolling)
    rolling_cv: list[float] = []
    all_rows = list(window.itertuples())
    for i in range(n_windows):
        start = i * rolling
        end   = min(start + rolling, len(all_rows))
        if end - start < 5:
            break
        sub_freq = Counter()
        for row in all_rows[start:end]:
            for n in row.numbers:
                sub_freq[n] += 1
        sub_freqs = [sub_freq.get(n, 0) for n in range(lo, hi + 1)]
        sub_exp = (end - start) * pick / pool
        cv = np.std(sub_freqs, ddof=1) / (sub_exp + 1e-9)
        rolling_cv.append(cv)

    # ── Tier classification ───────────────────────────────────────────────────
    def tier(cv: float, thresholds: tuple[float, float]) -> tuple[str, str]:
        low, high = thresholds
        if cv >= high:
            return "HIGH", "bold green"
        if cv >= low:
            return "MED", "yellow"
        return "LOW", "dim"

    # HIGH variance = more signal; LOW = near-random
    dimensions = [
        ("Frequency dist.",  freq_cv,   (0.10, 0.20), "How unequal are number hit rates?"),
        ("Draw sum",         sum_cv,    (0.08, 0.15), "How much does the total fluctuate?"),
        ("Parity (even/odd)",parity_cv, (0.15, 0.25), "How volatile is the even/odd split?"),
        ("Consecutive runs", consec_cv, (0.30, 0.60), "How much do consecutive numbers spike?"),
        ("Strategy conf.",   conf_cv,   (0.04, 0.10), "How unstable is strategy confidence?"),
    ]

    var_table = Table(
        title=f"📉 Variance Report — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    var_table.add_column("Dimension",   justify="left")
    var_table.add_column("CV",          justify="right")
    var_table.add_column("Tier",        justify="center")
    var_table.add_column("Description", justify="left", style="dim")

    tier_scores = []
    for name, cv, thresh, desc in dimensions:
        t, colour = tier(cv, thresh)
        tier_scores.append(t)
        t_fmt = f"[{colour}]{t}[/{colour}]"
        var_table.add_row(name, f"{cv:.3f}", t_fmt, desc)

    console.print()
    console.print(var_table)

    # ── Rolling trend sparkline ───────────────────────────────────────────────
    if rolling_cv:
        spark_str = _spark(rolling_cv)
        trend_dir = "→"
        if len(rolling_cv) >= 3:
            recent_avg = np.mean(rolling_cv[-3:])
            older_avg  = np.mean(rolling_cv[:-3]) if len(rolling_cv) > 3 else rolling_cv[0]
            trend_dir = "↑" if recent_avg > older_avg * 1.1 else "↓" if recent_avg < older_avg * 0.9 else "→"
        console.print(
            f"\n  [dim]Frequency variance trend ({rolling}-draw windows):[/dim] "
            f"[green]{spark_str}[/green] {trend_dir}"
        )


    # ── Summary panel ─────────────────────────────────────────────────────────
    n_high = tier_scores.count("HIGH")
    n_med  = tier_scores.count("MED")
    n_low  = tier_scores.count("LOW")

    # Actionability: HIGH variance = strategies might find signal
    if n_high >= 3:
        verdict  = "HIGH VARIANCE — good conditions for pattern-based strategies"
        colour   = "bold green"
        action   = "High cross-dimension variance suggests genuine signal; strategies may be effective"
    elif n_high + n_med >= 3:
        verdict  = "MODERATE VARIANCE — typical operating conditions"
        colour   = "yellow"
        action   = "Mixed signal; standard strategies applicable; use calibrated weights"
    else:
        verdict  = "LOW VARIANCE — near-random draw process"
        colour   = "red"
        action   = "Low variance implies high entropy; pattern strategies may underperform; use --strategies statistical"

    console.print()
    console.print(Panel(
        f"[{colour}]{verdict}[/{colour}]\n\n"
        f"[dim]HIGH: {n_high}  MED: {n_med}  LOW: {n_low}  "
        f"·  Freq CV: {freq_cv:.3f}  ·  Sum CV: {sum_cv:.3f}\n"
        f"Recommendation: {action}[/dim]",
        title="📉 Variance Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, freq_cv, sum_cv, parity_cv, consec_cv, conf_cv,
            n_high, n_med, n_low, verdict,
        )
        console.print(f"\n[green]✔ Variance report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, freq_cv: float, sum_cv: float, parity_cv: float,
    consec_cv: float, conf_cv: float,
    n_high: int, n_med: int, n_low: int, verdict: str,
) -> None:
    content = f"""
---
type: diagnostic
subtype: variance-report
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
freq_cv: {freq_cv:.4f}
sum_cv: {sum_cv:.4f}
parity_cv: {parity_cv:.4f}
consec_cv: {consec_cv:.4f}
conf_cv: {conf_cv:.4f}
high_dims: {n_high}
med_dims: {n_med}
low_dims: {n_low}
verdict: {verdict.split('—')[0].strip()}
---

## Variance Report: {game_name} ({today.isoformat()})

**Verdict:** {verdict}

| Dimension | CV | Tier |
|-----------|----|------|
| Frequency dist. | {freq_cv:.4f} | {"HIGH" if freq_cv>=0.20 else "MED" if freq_cv>=0.10 else "LOW"} |
| Draw sum | {sum_cv:.4f} | {"HIGH" if sum_cv>=0.15 else "MED" if sum_cv>=0.08 else "LOW"} |
| Parity | {parity_cv:.4f} | {"HIGH" if parity_cv>=0.25 else "MED" if parity_cv>=0.15 else "LOW"} |
| Consecutive | {consec_cv:.4f} | {"HIGH" if consec_cv>=0.60 else "MED" if consec_cv>=0.30 else "LOW"} |
| Strategy conf. | {conf_cv:.4f} | {"HIGH" if conf_cv>=0.10 else "MED" if conf_cv>=0.04 else "LOW"} |

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
