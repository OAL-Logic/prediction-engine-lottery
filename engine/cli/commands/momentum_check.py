"""
Momentum Check Command 📊
=========================
Moving-average momentum indicators for pool numbers.

For each number, computes:
  Short MA  — hit rate over last S draws (default 10)
  Long MA   — hit rate over last L draws (default 30)
  Signal    — SHORT > LONG × threshold → RISING momentum
              SHORT < LONG × threshold → FALLING momentum
              Otherwise → NEUTRAL

The signal mimics a simple MACD-style crossover applied to hit rates.
Numbers with RISING momentum are gaining frequency faster than the
long-term trend; numbers with FALLING momentum are slowing.

Useful for:
  • Finding numbers "on the move" vs those in a stable or declining pattern
  • Complementing streak analysis (a streak might end; momentum shows trend)
  • Filtering rank-numbers output to momentum-positive numbers

Output
------
  Momentum table    all pool numbers sorted by signal strength
  Top/Bottom panel  strongest rising and falling momentum numbers

Example
-------
  lottery momentum-check br/lotofacil
  lottery momentum-check br/lotofacil --short 7 --long 21
  lottery momentum-check br/lotofacil --top 10
  lottery momentum-check br/mega-sena --export-md momentum.md
"""

from __future__ import annotations

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

_BAR_FULL  = "█"
_BAR_EMPTY = "░"


def _bar(val: float, max_val: float, width: int = 8) -> str:
    if max_val <= 0:
        return _BAR_EMPTY * width
    filled = round(min(val / max_val, 1.0) * width)
    return _BAR_FULL * filled + _BAR_EMPTY * (width - filled)


def momentum_check(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    short:   Annotated[int, typer.Option("--short", "-s",
        help="Short moving-average window (draws)")] = 10,
    long:    Annotated[int, typer.Option("--long", "-l",
        help="Long moving-average window (draws)")] = 30,
    top:     Annotated[int, typer.Option("--top", "-N",
        help="Show only top-N rising and bottom-N falling (0 = all)")] = 8,
    threshold: Annotated[float, typer.Option("--threshold",
        help="Signal threshold: SHORT must be > LONG × (1 + threshold)")] = 0.15,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append momentum report to this .md file")] = None,
) -> None:
    """📊 Moving-average momentum indicators for all pool numbers.

    Numbers where short-term hit rate crosses above long-term rate are
    'RISING'; those falling below are 'FALLING'. Neutral = in-band.

    Example: lottery momentum-check br/lotofacil
             lottery momentum-check br/lotofacil --short 7 --long 21 --top 10
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = list(range(lo, hi + 1))
    pool_size = hi - lo + 1

    min_draws = long + 5
    if len(df) < min_draws:
        console.print(f"[dim]Need at least {min_draws} draws; only have {len(df)}.[/dim]")
        raise typer.Exit(0)

    window_l = df.tail(long)
    window_s = df.tail(short)

    # ── Compute hit rates ─────────────────────────────────────────────────────
    def hit_rate(sub, num: int) -> float:
        n = len(sub)
        if n == 0:
            return 0.0
        hits = sum(1 for row in sub.itertuples() if num in row.numbers)
        return hits / n

    baseline = pick / pool_size  # expected hit rate per draw

    # Build momentum data
    data: list[dict] = []
    
    # Calculate historical average skip for every number
    avg_skips: dict[int, float] = {}
    current_skips: dict[int, int] = {}
    
    for n in pool:
        hits = df[df["numbers"].apply(lambda x: n in x)].index.tolist()
        if len(hits) >= 2:
            skips = [hits[i] - hits[i-1] - 1 for i in range(1, len(hits))]
            avg_skips[n] = float(np.mean(skips))
        else:
            avg_skips[n] = (pool_size / pick) - 1.0 # theoretical average
            
        if hits:
            current_skips[n] = (len(df) - 1) - hits[-1]
        else:
            current_skips[n] = len(df)

    for n in pool:
        sr = hit_rate(window_s, n)
        lr = hit_rate(window_l, n)
        # Momentum signal
        if lr > 0:
            ratio = sr / lr
        else:
            ratio = sr / (baseline + 1e-9)

        if ratio >= 1.0 + threshold:
            signal = "RISING"
            signal_strength = ratio - 1.0
        elif ratio <= 1.0 - threshold:
            signal = "FALLING"
            signal_strength = 1.0 - ratio
        else:
            signal = "NEUTRAL"
            signal_strength = 0.0

        data.append({
            "num":      n,
            "short_r":  sr,
            "long_r":   lr,
            "ratio":    ratio,
            "signal":   signal,
            "strength": signal_strength,
            "skip":     current_skips[n],
            "avg_skip": avg_skips[n],
        })

    # Sort by ratio (highest first)
    rising  = sorted([d for d in data if d["signal"] == "RISING"],
                     key=lambda d: -d["strength"])
    falling = sorted([d for d in data if d["signal"] == "FALLING"],
                     key=lambda d: -d["strength"])
    neutral = [d for d in data if d["signal"] == "NEUTRAL"]

    max_ratio = max(d["ratio"] for d in data) if data else 2.0
    min_ratio = min(d["ratio"] for d in data) if data else 0.0

    n_top = top if top > 0 else len(pool)

    # ── Momentum table ────────────────────────────────────────────────────────
    mom_table = Table(
        title=f"📊 Momentum & Skips — {rules.name}  "
              f"(short={short}, long={long}, threshold=±{threshold:.0%})",
        box=None, padding=(0, 1), header_style="bold",
    )
    mom_table.add_column("Number",    justify="center", style="bold yellow")
    mom_table.add_column("Short%",    justify="right")
    mom_table.add_column("Long%",     justify="right",  style="dim")
    mom_table.add_column("Ratio",     justify="right")
    mom_table.add_column("Skip",      justify="right")
    mom_table.add_column("Signal",    justify="center")
    mom_table.add_column("Bar",       justify="left")

    # Show top rising + top falling
    display = rising[:n_top] + falling[:n_top]
    if top == 0:
        display = sorted(data, key=lambda d: -d["ratio"])

    for d in display:
        sig = d["signal"]
        if sig == "RISING":
            sig_fmt = "[bold green]▲ RISING[/bold green]"
            bar_col = "green"
        elif sig == "FALLING":
            sig_fmt = "[red]▼ FALLING[/red]"
            bar_col = "red"
        else:
            sig_fmt = "[dim]→ NEUTRAL[/dim]"
            bar_col = "dim"

        bar_val = d["ratio"] / max_ratio if max_ratio > 0 else 0.5
        bar_str = _bar(bar_val, 1.0)
        
        skip = d["skip"]
        avg_s = d["avg_skip"]
        # Overdue logic: current skip > 2x average skip
        if skip > avg_s * 2.0:
            skip_fmt = f"[bold red]{skip}[/bold red]"
        elif skip > avg_s:
            skip_fmt = f"[yellow]{skip}[/yellow]"
        else:
            skip_fmt = f"[dim]{skip}[/dim]"

        mom_table.add_row(
            str(d["num"]),
            f"{d['short_r']:.0%}",
            f"{d['long_r']:.0%}",
            f"{d['ratio']:.2f}×",
            skip_fmt,
            sig_fmt,
            f"[{bar_col}]{bar_str}[/{bar_col}]",
        )

    console.print()
    console.print(mom_table)

    # ── Summary panel ─────────────────────────────────────────────────────────
    top_rising  = rising[:3]
    top_falling = falling[:3]

    rising_str  = "  ".join(f"#{d['num']} ({d['ratio']:.2f}×)" for d in top_rising)  or "none"
    falling_str = "  ".join(f"#{d['num']} ({d['ratio']:.2f}×)" for d in top_falling) or "none"

    console.print()
    console.print(Panel(
        f"[bold green]Rising:[/bold green]   {rising_str}\n"
        f"[bold red]Falling:[/bold red]  {falling_str}\n"
        f"[dim]Neutral: {len(neutral)}  ·  Rising: {len(rising)}  ·  Falling: {len(falling)}  ·  "
        f"Baseline rate: {baseline:.1%}  ·  Window: short={short} long={long}[/dim]",
        title="📊 Momentum Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            short, long, threshold, rising, falling, neutral, baseline,
        )
        console.print(f"\n[green]✔ Momentum report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    short: int, long: int, threshold: float,
    rising: list, falling: list, neutral: list,
    baseline: float,
) -> None:
    top_r = "  ".join(f"#{d['num']} ({d['ratio']:.2f}×)" for d in rising[:5])
    top_f = "  ".join(f"#{d['num']} ({d['ratio']:.2f}×)" for d in falling[:5])

    rows = ""
    for d in (rising[:10] + falling[:10]):
        rows += (f"| **{d['num']}** | {d['short_r']:.0%} | {d['long_r']:.0%} | "
                 f"{d['ratio']:.2f}× | {d['signal']} |\n")

    content = f"""
---
type: diagnostic
subtype: momentum-check
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
short_window: {short}
long_window: {long}
threshold: {threshold}
rising_count: {len(rising)}
falling_count: {len(falling)}
neutral_count: {len(neutral)}
baseline_rate: {baseline:.4f}
---

## Momentum Check: {game_name} ({today.isoformat()})

**Short:** {short} draws  ·  **Long:** {long} draws  ·  **Threshold:** ±{threshold:.0%}
**Rising:** {len(rising)}  ·  **Falling:** {len(falling)}  ·  **Neutral:** {len(neutral)}

**Top rising:** {top_r}
**Top falling:** {top_f}

| Number | Short% | Long% | Ratio | Signal |
|--------|--------|-------|-------|--------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
