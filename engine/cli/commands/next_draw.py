"""
Next Command ⚡
===============
One-liner executive summary: should I play today, and if so, what ticket?

Internally runs:
  1. Scan (6-layer GO/NO-GO) — fast mode (3 stress trials)
  2. If GO: Forecast (fast strategy group) → consensus ticket
  3. Compact output: verdict + ticket + key signals

This is the "morning coffee" command — run it once, get an answer.

Example
-------
  lottery next br/lotofacil
  lottery next br/lotofacil --force       (generate ticket even if not GO)
  lottery next br/lotofacil --quiet       (just the ticket, no decoration)
"""

from __future__ import annotations

import json
from datetime import date as _date
from pathlib import Path
from typing import Annotated

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel

from engine.cli.utils import get_adapter, print_command_summary
from engine.strategies import get_strategy
from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name
from engine.modules import frequency

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _quick_scan(df, adapter, strategy: str) -> tuple[str, int, int, dict]:
    """Lightweight 6-layer scan. Returns (verdict, score, max, details)."""
    from engine.cli.commands.scan import (
        _rolling_stable_pct, _stress_delta, _solar_kp, _regime_js,
    )

    rules  = adapter.rules
    today  = _date.today()
    scores = {}
    details = {}

    # L1 fairness
    try:
        f_res = frequency.analyze(df.tail(100), rules, top_n=1)
        p = f_res.chi2_p_value
        if p < 0.05:
            scores["fairness"] = 0
        elif p > 0.5:
            scores["fairness"] = 2
        else:
            scores["fairness"] = 1
        details["fairness"] = f"chi²p={p:.4f}"
    except Exception:
        scores["fairness"] = 1
        details["fairness"] = "n/a"

    # L2 stability
    stab = _rolling_stable_pct(df, adapter, strategy, 50, n_windows=4)
    if stab is None:
        scores["stability"] = 1
        details["stability"] = "n/a"
    elif stab >= 0.5:
        scores["stability"] = 2
        details["stability"] = f"stable={stab:.0%}"
    elif stab >= 0.25:
        scores["stability"] = 1
        details["stability"] = f"mixed={stab:.0%}"
    else:
        scores["stability"] = 0
        details["stability"] = f"noisy={stab:.0%}"

    # L3 cluster (always 1 — informational only)
    scores["cluster"] = 1
    details["cluster"] = "n/a"

    # L4 esoteric
    moon_ratio_val = moon_phase_ratio(today)
    moon_name = phase_name(today)
    kp = _solar_kp()
    esoteric_score = 1
    if moon_name in ("New Moon", "Full Moon"):
        esoteric_score = 2
    if kp is not None:
        if kp >= 5:
            esoteric_score = max(0, esoteric_score - 1)
        elif kp < 3:
            esoteric_score = min(2, esoteric_score + 1)
    scores["esoteric"] = esoteric_score
    details["esoteric"] = f"{moon_name}  kp={kp or '?'}"

    # L5 discrimination
    delta = _stress_delta(df, adapter, strategy, inject_ratio=0.5, trials=3)
    if delta is None:
        scores["discrimination"] = 1
        details["discrimination"] = "n/a"
    elif delta > 0.02:
        scores["discrimination"] = 2
        details["discrimination"] = f"Δ={delta:+.4f}"
    elif delta < -0.005:
        scores["discrimination"] = 0
        details["discrimination"] = f"Δ={delta:+.4f} (inverted)"
    else:
        scores["discrimination"] = 1
        details["discrimination"] = f"Δ={delta:+.4f}"

    # L6 regime
    lo, hi = rules.number_range
    js_val, regime = _regime_js(df, lo, hi - lo + 1, recent=50)
    if regime == "STABLE":
        scores["regime"] = 2
    elif regime == "DRIFT":
        scores["regime"] = 1
    else:
        scores["regime"] = 0
    details["regime"] = f"JS={js_val:.5f} ({regime})"

    total = sum(scores.values())
    max_score = len(scores) * 2  # 12
    pct = total / max_score
    if pct >= 0.70:
        verdict = "GO"
    elif pct >= 0.40:
        verdict = "CAUTION"
    else:
        verdict = "NO-GO"

    return verdict, total, max_score, details


def _quick_forecast(df, adapter, window: int = 50) -> list[int]:
    """Run a 3-strategy weighted forecast. Returns ticket as list of ints."""
    from engine.cli.commands.forecast import _stability_pct, _stress_delta, _composite_weight

    strategy_names = ["bayesian", "weighted", "markov"]
    lo, hi = adapter.rules.number_range
    pool_size = hi - lo + 1
    win_df = df.tail(window)
    stress_df = df.tail(100)

    consensus = np.zeros(pool_size, dtype=float)
    total_weight = 0.0

    for name in strategy_names:
        stab  = _stability_pct(df, adapter, name, window, step=20)
        delta = _stress_delta(stress_df, adapter, name, inject_ratio=0.5, trials=2)
        weight = _composite_weight(stab, delta)
        try:
            strat = get_strategy(name)
            res = strat.suggest(win_df, adapter.rules, count=1, temperature=1.0)
            arr = np.zeros(pool_size, dtype=float)
            for num, sc in res.scores.items():
                if lo <= num <= hi:
                    arr[num - lo] = max(0.0, sc)
            s = arr.sum()
            if s > 0:
                arr /= s
            consensus += arr * weight
            total_weight += weight
        except Exception:
            continue

    if total_weight > 0:
        consensus /= total_weight

    pick = adapter.rules.pick_count
    ranked = sorted(range(pool_size), key=lambda i: consensus[i], reverse=True)
    return sorted([i + lo for i in ranked[:pick]])


def next_draw(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategy: Annotated[str, typer.Option("--strategy", "-s",
        help="Strategy for scan layers")] = "bayesian",
    force: Annotated[bool, typer.Option("--force/--no-force",
        help="Generate ticket even if verdict is not GO")] = False,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet",
        help="Print only the ticket numbers (no decoration)")] = False,
) -> None:
    """⚡ One-liner: scan conditions + generate consensus ticket if GO.

    Combines the 6-layer scan with a fast 3-strategy weighted forecast
    into a single command. The definitive "should I play today?" answer.

    Example: lottery next br/lotofacil
             lottery next br/lotofacil --force
             lottery next br/lotofacil --quiet
    """

    if not quiet:
        print_command_summary("next", lottery, strategy=strategy)

    with console.status(f"[bold green]Loading {lottery}…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    if not quiet:
        console.print("[dim]Running 6-layer scan…[/dim]")

    verdict, score, max_score, details = _quick_scan(df, adapter, strategy)

    if quiet:
        if verdict == "GO" or force:
            ticket = _quick_forecast(df, adapter)
            console.print(" ".join(str(n) for n in ticket))
        return

    # ── Verbose output ────────────────────────────────────────────────────────
    # Verdict panel
    if verdict == "GO":
        verdict_str   = "[bold green]✔ GO[/bold green]"
        border        = "green"
    elif verdict == "CAUTION":
        verdict_str   = "[bold yellow]⚠ CAUTION[/bold yellow]"
        border        = "yellow"
    else:
        verdict_str   = "[bold red]✘ NO-GO[/bold red]"
        border        = "red"

    signal_lines = "\n".join(
        f"  [dim]{k.capitalize():16s}[/dim] {v}"
        for k, v in details.items()
    )

    console.print()
    console.print(Panel(
        f"{verdict_str}  ({score}/{max_score})\n\n{signal_lines}",
        title=f"⚡ {adapter.rules.name} — Today's Conditions",
        border_style=border,
    ))

    # Ticket
    if verdict == "GO" or force:
        if verdict != "GO":
            console.print("[yellow]Generating ticket anyway (--force)[/yellow]")

        console.print("[dim]Running fast 3-strategy forecast…[/dim]")
        ticket = _quick_forecast(df, adapter)
        ticket_str = "  ".join(str(n) for n in ticket)
        console.print()
        console.print(Panel(
            f"[bold yellow]{ticket_str}[/bold yellow]",
            title="🔮 Consensus Ticket",
            border_style="yellow",
        ))
    else:
        console.print(
            f"\n[yellow]Ticket not generated (verdict: {verdict}). "
            "Use --force to override.[/yellow]"
        )
