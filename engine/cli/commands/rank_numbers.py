"""
Rank Numbers Command 🔢
=======================
Composite per-number score aggregated across all strategies in a group.

For each strategy, the engine produces a per-number score distribution.
This command aggregates those scores — weighted by calibration lift (if a
calibration cache exists) or statistical composite (stability×discrimination)
otherwise — to produce a ranked list of every number in the pool.

Output columns
--------------
  Rank        Overall composite rank
  Number      Pool number
  Score       Weighted aggregate score (normalised 0–1)
  In N strats How many strategies have this in their top picks
  Freq%       Historical frequency (last 100 draws)
  Trend       7-draw recency bias indicator (↑/↓/→)
  Tier        HOT / WARM / COLD / VERY COLD

Usage
-----
  lottery rank-numbers br/lotofacil
  lottery rank-numbers br/lotofacil --strategies statistical
  lottery rank-numbers br/lotofacil --top 10           # show only top 10
  lottery rank-numbers br/lotofacil --export-md rank.md
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary
from engine.strategies import get_strategy

console = Console()

_STRATEGY_GROUPS: dict[str, list[str]] = {
    "default":     ["weighted", "markov", "bayesian", "monte_carlo", "spectral", "cycle"],
    "fast":        ["bayesian", "weighted", "monte_carlo"],
    "statistical": ["markov", "bayesian", "weighted", "monte_carlo", "pattern",
                    "momentum", "spectral", "streak", "cycle", "harmonic",
                    "stability", "fisher"],
    "esoteric":    ["moon_phase", "solar", "noosphere", "numerology", "fibonacci"],
}

_SPARK = "▁▂▃▄▅▆▇█"
_BARS  = " ░▒▓█"


def _load_cal_weights(lottery: str, names: list[str]) -> dict[str, float] | None:
    try:
        from engine.cli.commands.calibrate import load_calibration_weights
        return load_calibration_weights(lottery, names)
    except Exception:
        return None


def _composite_stat(df, adapter, name: str) -> float:
    """Quick stability×discrimination composite weight."""
    try:
        from engine.cli.commands.forecast import _stability_pct, _stress_delta, _composite_weight
        stab  = _stability_pct(df, adapter, name, 50, 20)
        delta = _stress_delta(df.tail(100), adapter, name, 0.5, 2)
        return _composite_weight(stab, delta)
    except Exception:
        return 0.5


def _bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


def rank_numbers(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Group: default | fast | statistical | esoteric | comma-list")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window for strategy scoring")] = 50,
    top: Annotated[int, typer.Option("--top", "-N",
        help="Show only the top N numbers (0 = all)")] = 0,
    temperature: Annotated[float, typer.Option("--temperature",
        help="Suggestion temperature")] = 0.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append ranking to this .md file")] = None,
) -> None:
    """🔢 Composite per-number ranking across all strategies.

    Aggregates per-number scores from each strategy weighted by calibration
    lift (if calibrate cache exists) or statistical composite otherwise.
    Shows each number's rank, aggregate score, consensus count, frequency
    and trend.

    Example: lottery rank-numbers br/lotofacil
             lottery rank-numbers br/lotofacil --strategies fast --top 10
             lottery rank-numbers br/lotofacil --export-md rank.md
    """
    print_command_summary("rank-numbers", lottery, strategies=strategies, window=window)

    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pool_size = hi - lo + 1
    pick      = rules.pick_count

    if strategies in _STRATEGY_GROUPS:
        names = _STRATEGY_GROUPS[strategies]
    else:
        names = [s.strip() for s in strategies.split(",") if s.strip()]

    win_df = df.tail(window)

    # Load weights: calibration lift if available, else statistical
    cal_weights = _load_cal_weights(lottery, names)
    using_cal   = cal_weights is not None
    weight_source = "calibration" if using_cal else "statistical"

    console.print(f"\n[dim]Weights: {weight_source}  |  {len(names)} strategies[/dim]\n")

    # ── Per-strategy score accumulation ──────────────────────────────────────
    composite = np.zeros(pool_size, dtype=float)
    total_w   = 0.0
    top_sets: list[set[int]] = []    # top picks per strategy (for consensus count)
    n_strategies_used = 0

    with console.status("") as status:
        for name in names:
            status.update(f"[dim]Scoring {name}…[/dim]")
            try:
                if cal_weights and name in cal_weights:
                    w = float(cal_weights[name])
                else:
                    w = _composite_stat(df, adapter, name)

                strat = get_strategy(name)
                res   = strat.suggest(win_df, rules, count=1, temperature=temperature)
                scores_raw = res.scores

                arr = np.zeros(pool_size, dtype=float)
                for num, sc in scores_raw.items():
                    if lo <= num <= hi:
                        arr[num - lo] = max(0.0, float(sc))
                s = arr.sum()
                if s > 0:
                    arr /= s

                composite += arr * w
                total_w   += w
                n_strategies_used += 1

                # Top picks for this strategy
                ranked_idx = sorted(range(pool_size), key=lambda i: arr[i], reverse=True)
                top_sets.append({i + lo for i in ranked_idx[:pick]})

            except Exception:
                pass

    if total_w == 0:
        console.print("[red]No strategies produced scores.[/red]")
        raise typer.Exit(1)

    composite /= total_w

    # ── Historical frequency (last 100 draws) ────────────────────────────────
    recent_100 = df.tail(100)
    freq = Counter()
    for row in recent_100.itertuples():
        for n in row.numbers:
            freq[n] += 1
    max_freq = max(freq.values()) if freq else 1

    # ── 7-draw recency trend ─────────────────────────────────────────────────
    last7_draws = df.tail(7)
    recent_7 = Counter()
    for row in last7_draws.itertuples():
        for n in row.numbers:
            recent_7[n] += 1

    # ── Build ranked table ────────────────────────────────────────────────────
    ranked_pool = sorted(range(pool_size), key=lambda i: composite[i], reverse=True)

    display_count = top if top > 0 else pool_size
    show_idx = ranked_pool[:display_count]

    table = Table(
        title=f"Number Rankings — {rules.name}  ({n_strategies_used} strategies, {weight_source} weights)",
        box=None, padding=(0, 1), header_style="bold",
    )
    table.add_column("Rank",      justify="right",  style="dim")
    table.add_column("Number",    justify="center",  style="bold yellow")
    table.add_column("Score",     justify="right")
    table.add_column("Bar",       justify="left",    style="green")
    table.add_column("Consensus", justify="center")
    table.add_column("Freq%",     justify="right",   style="dim")
    table.add_column("Trend",     justify="center")
    table.add_column("Tier",      justify="center")

    score_max = composite[ranked_pool[0]] if ranked_pool else 1.0

    for rank, idx in enumerate(show_idx, 1):
        num    = idx + lo
        sc     = composite[idx]
        sc_norm = sc / score_max if score_max > 0 else 0.0
        bar_str = _bar(sc_norm, 8)

        # Consensus: how many strategies include num in top picks
        n_agree = sum(1 for s in top_sets if num in s)
        consensus_pct = n_agree / len(top_sets) if top_sets else 0.0
        if consensus_pct >= 0.75:
            cons_fmt = f"[green]{n_agree}/{len(top_sets)}[/green]"
        elif consensus_pct >= 0.50:
            cons_fmt = f"[yellow]{n_agree}/{len(top_sets)}[/yellow]"
        else:
            cons_fmt = f"[dim]{n_agree}/{len(top_sets)}[/dim]"

        # Frequency
        f = freq.get(num, 0)
        freq_pct = f / len(recent_100) * 100 if len(recent_100) > 0 else 0.0

        # Trend: compare recent 7 vs expected
        expected_per_7 = 7 * pick / pool_size
        r7 = recent_7.get(num, 0)
        trend = "↑" if r7 > expected_per_7 * 1.2 else "↓" if r7 < expected_per_7 * 0.5 else "→"
        trend_fmt = (
            f"[green]{trend}[/green]" if trend == "↑"
            else f"[red]{trend}[/red]"   if trend == "↓"
            else f"[dim]{trend}[/dim]"
        )

        # Tier
        if rank <= pick:
            tier = "[bold green]HOT[/bold green]"
        elif rank <= pick * 2:
            tier = "[green]WARM[/green]"
        elif rank >= pool_size - pick + 1:
            tier = "[dim]VERY COLD[/dim]"
        else:
            tier = "[dim]COLD[/dim]"

        table.add_row(
            str(rank),
            str(num),
            f"{sc:.4f}",
            bar_str,
            cons_fmt,
            f"{freq_pct:.1f}%",
            trend_fmt,
            tier,
        )

    console.print(table)

    # Suggested ticket: top pick_count numbers
    ticket = [idx + lo for idx in ranked_pool[:pick]]
    ticket_str = "  ".join(str(n) for n in ticket)
    console.print()
    console.print(Panel(
        f"[bold yellow]{ticket_str}[/bold yellow]\n"
        f"[dim]Top {pick} numbers by composite score  ·  {weight_source} weights  ·  {n_strategies_used} strategies[/dim]",
        title="🔢 Top Numbers → Suggested Ticket",
        border_style="yellow",
    ))

    if export_md:
        _append_md(export_md, lottery, rules.name, _date.today(), ranked_pool,
                   composite, top_sets, freq, recent_100, pool_size, lo, pick,
                   n_strategies_used, weight_source, display_count)
        console.print(f"[green]✔ Number ranking appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    ranked_pool: list[int], composite: np.ndarray, top_sets: list[set],
    freq: Counter, recent_100, pool_size: int, lo: int, pick: int,
    n_strats: int, weight_source: str, display_count: int,
) -> None:
    ticket = [idx + lo for idx in ranked_pool[:pick]]
    score_max = composite[ranked_pool[0]] if ranked_pool else 1.0
    n_draws = len(recent_100)

    rows = ""
    for rank, idx in enumerate(ranked_pool[:display_count], 1):
        num = idx + lo
        sc  = composite[idx]
        f   = freq.get(num, 0)
        fp  = f / n_draws * 100 if n_draws > 0 else 0.0
        n_agree = sum(1 for s in top_sets if num in s)
        tier = "HOT" if rank <= pick else "WARM" if rank <= pick*2 else "COLD"
        rows += f"| {rank} | **{num}** | {sc:.4f} | {n_agree}/{len(top_sets)} | {fp:.1f}% | {tier} |\n"

    content = f"""
---
type: diagnostic
subtype: rank-numbers
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
strategies_used: {n_strats}
weight_source: {weight_source}
top_ticket: {ticket}
---

## Number Rankings: {game_name} ({today.isoformat()})

| Rank | Number | Score | Consensus | Freq% | Tier |
|------|--------|-------|-----------|-------|------|
{rows}
*Ticket: {' '.join(str(n) for n in ticket)}*

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
