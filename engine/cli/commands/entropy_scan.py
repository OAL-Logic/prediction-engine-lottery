"""
Entropy Scan Command 🔬
=======================
Shannon entropy analysis of the draw distribution over rolling windows.

Measures how "uniform" the number distribution is across recent draws.
Low entropy → some numbers appear far more often than others (potential
structure). High entropy → near-uniform distribution (high noise, random).

Metrics computed per rolling window:
  H(X)          Shannon entropy of number frequency distribution
  H_max         Maximum possible entropy (log2 of pool size)
  Uniformity %  H / H_max × 100 — how close to uniform
  Z-score       how many std devs from baseline (100-draw mean)

A window with Z < -2 (unusually low entropy) may indicate a structural
regime shift worth exploiting. Z > +2 means higher-than-usual uniformity.

Output
------
  Rolling entropy table    one row per window with H, uniformity, Z
  Trend sparkline          entropy across windows oldest→newest
  Summary panel            low/high entropy windows, recommendation

Example
-------
  lottery entropy-scan br/lotofacil
  lottery entropy-scan br/lotofacil --window 20 --windows 10
  lottery entropy-scan br/mega-sena --export-md entropy.md
"""

from __future__ import annotations

import math
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
from engine.modules import filters

console = Console()

_SPARK_CHARS = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if lo == hi:
        return _SPARK_CHARS[4] * len(values)
    return "".join(
        _SPARK_CHARS[round((v - lo) / (hi - lo) * 7)]
        for v in values
    )


def _shannon_entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts if c > 0
    )


def entropy_scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Draws per rolling window")] = 30,
    windows: Annotated[int, typer.Option("--windows", "-k",
        help="Number of windows to compute (0 = all)")] = 12,
    baseline_draws: Annotated[int, typer.Option("--baseline",
        help="Draws used to compute baseline entropy mean/std")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append entropy scan report to this .md file")] = None,
) -> None:
    """🔬 Shannon entropy analysis of draw distribution over rolling windows.

    Low uniformity windows may signal exploitable structure; high
    uniformity signals a near-random regime.

    Example: lottery entropy-scan br/lotofacil
             lottery entropy-scan br/lotofacil --window 20 --windows 10
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pool     = list(range(lo, hi + 1))
    pool_size = hi - lo + 1

    all_rows = list(df.itertuples())
    n_total  = len(all_rows)

    if n_total < window + 5:
        console.print(f"[dim]Need at least {window + 5} draws; have {n_total}.[/dim]")
        raise typer.Exit(0)

    h_max = math.log2(pool_size)  # maximum possible entropy

    # ── Baseline entropy (long window) ─────────────────────────────────────
    baseline_rows = all_rows[-min(baseline_draws, n_total):]
    base_freq = Counter()
    for row in baseline_rows:
        for n in row.numbers:
            base_freq[n] += 1
    base_counts = [base_freq.get(n, 0) for n in pool]
    h_baseline  = _shannon_entropy(base_counts)
    u_baseline  = h_baseline / h_max * 100

    # ── Rolling entropy windows ─────────────────────────────────────────────
    max_windows = n_total // window
    k = min(windows if windows > 0 else max_windows, max_windows)

    window_data: list[dict] = []
    for i in range(k):
        # Work backwards from most recent
        end   = n_total - i * window
        start = end - window
        if start < 0:
            break
        sub   = all_rows[start:end]
        freq  = Counter()
        for row in sub:
            for n in row.numbers:
                freq[n] += 1
        counts = [freq.get(n, 0) for n in pool]
        h      = _shannon_entropy(counts)
        unif   = h / h_max * 100
        window_data.append({
            "idx":         k - i,      # 1 = oldest shown, k = most recent
            "start_draw":  start,
            "end_draw":    end,
            "h":           h,
            "uniformity":  unif,
        })

    # Reverse so oldest first
    window_data = list(reversed(window_data))

    # Compute Z-scores
    h_values = [d["h"] for d in window_data]
    if len(h_values) >= 2:
        h_mean = np.mean(h_values)
        h_std  = np.std(h_values, ddof=1) or 1e-9
    else:
        h_mean = h_baseline
        h_std  = 1e-9

    for d in window_data:
        d["z"] = (d["h"] - h_mean) / h_std

    # ── AC Value Analysis (Historical Distribution) ────────────────────────
    ac_values = [filters.get_ac_value(row.numbers) for row in all_rows]
    ac_counts = Counter(ac_values)
    total_ac  = len(ac_values)
    
    # Sort by frequency to find the "Golden Range" (containing >90% of draws)
    sorted_ac = sorted(ac_counts.items(), key=lambda x: x[1], reverse=True)
    cumulative = 0
    golden_range = []
    for ac, count in sorted_ac:
        golden_range.append(ac)
        cumulative += count
        if cumulative / total_ac >= 0.90:
            break
    golden_range = sorted(golden_range) if golden_range else [0]

    # ── Table ───────────────────────────────────────────────────────────────
    tbl = Table(
        title=f"🔬 Entropy Scan — {rules.name}  "
              f"(window={window} draws, {k} windows)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Window",     justify="right",  style="dim")
    tbl.add_column("Draws",      justify="center", style="dim")
    tbl.add_column("H(X)",       justify="right")
    tbl.add_column("Uniform%",   justify="right")
    tbl.add_column("Z",          justify="right")
    tbl.add_column("Signal",     justify="center")

    low_entropy_windows  = []
    high_entropy_windows = []

    for d in window_data:
        z = d["z"]
        u = d["uniformity"]
        w = d["idx"]

        if z <= -2.0:
            signal = "[bold red]LOW-H[/bold red]"
            low_entropy_windows.append(d)
        elif z >= 2.0:
            signal = "[bold green]HIGH-H[/bold green]"
            high_entropy_windows.append(d)
        elif z <= -1.0:
            signal = "[yellow]low-h[/yellow]"
        elif z >= 1.0:
            signal = "[cyan]high-h[/cyan]"
        else:
            signal = "[dim]normal[/dim]"

        draw_range = f"{d['start_draw'] + 1}–{d['end_draw']}"
        tbl.add_row(
            f"W{w}",
            draw_range,
            f"{d['h']:.3f}",
            f"{u:.1f}%",
            f"{z:+.2f}",
            signal,
        )

    console.print()
    console.print(tbl)

    # ── Sparkline trend ─────────────────────────────────────────────────────
    spark = _sparkline([d["uniformity"] for d in window_data])
    latest_z = window_data[-1]["z"] if window_data else 0.0
    trend_arrow = "↑" if latest_z > 0.5 else "↓" if latest_z < -0.5 else "→"
    console.print(
        f"\n  [dim]Uniformity trend (oldest → newest):[/dim] "
        f"[cyan]{spark}[/cyan] {trend_arrow}"
    )
    console.print(
        f"  [dim]Baseline (last {len(baseline_rows)} draws): "
        f"H={h_baseline:.3f}  Uniform={u_baseline:.1f}%  H_max={h_max:.3f}[/dim]"
    )

    # ── Summary panel ───────────────────────────────────────────────────────
    if low_entropy_windows:
        verdict  = "STRUCTURED — low-entropy windows detected; patterns may be exploitable"
        colour   = "bold red"
        action   = "Run rank-numbers or momentum-check for numbers driving the concentration"
    elif high_entropy_windows:
        verdict  = "NOISY — high-entropy windows; near-uniform distribution"
        colour   = "bold green"
        action   = "Distribution is highly uniform; pattern strategies may underperform"
    else:
        verdict  = "NORMAL — entropy within expected range across all windows"
        colour   = "yellow"
        action   = "No unusual entropy regime detected; standard strategy applicable"

    low_str  = ", ".join(f"W{d['idx']}" for d in low_entropy_windows)  or "none"
    high_str = ", ".join(f"W{d['idx']}" for d in high_entropy_windows) or "none"

    console.print()
    console.print(Panel(
        f"[{colour}]{verdict}[/{colour}]\n\n"
        f"[dim]Low-H windows (Z≤-2): {low_str}\n"
        f"High-H windows (Z≥+2): {high_str}\n"
        f"AC Golden Range (>90%): {golden_range[0]}–{golden_range[-1]} "
        f"(Mode: {ac_counts.most_common(1)[0][0]})\n"
        f"Recommendation: {action}[/dim]",
        title="🔬 Entropy & Complexity Summary",
        border_style="yellow",
    ))

    if export_md:
        ac_range_str = f"{golden_range[0]}–{golden_range[-1]}"
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            window, k, h_baseline, u_baseline, h_max,
            len(low_entropy_windows), len(high_entropy_windows), verdict,
            ac_range_str
        )
        console.print(f"\n[green]✔ Entropy scan appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    window_size: int, n_windows: int,
    h_baseline: float, u_baseline: float, h_max: float,
    low_count: int, high_count: int, verdict: str,
    ac_golden_range: str = "N/A"
) -> None:
    content = f"""
---
type: diagnostic
subtype: entropy-scan
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
window_size: {window_size}
windows_computed: {n_windows}
h_baseline: {h_baseline:.4f}
uniformity_baseline: {u_baseline:.2f}
h_max: {h_max:.4f}
low_entropy_windows: {low_count}
high_entropy_windows: {high_count}
ac_golden_range: {ac_golden_range}
verdict: {verdict.split('—')[0].strip()}
---

## Entropy Scan: {game_name} ({today.isoformat()})

**Window:** {window_size} draws  ·  **Windows computed:** {n_windows}
**Baseline:** H={h_baseline:.4f}  Uniform={u_baseline:.1f}%  H_max={h_max:.4f}
**Low-H windows:** {low_count}  ·  **High-H windows:** {high_count}
**AC Golden Range:** {ac_golden_range}

**Verdict:** {verdict}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
