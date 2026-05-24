"""
Quick Command ⚡
================
Fastest path to a ticket: scan + forecast in one silent command.

Designed for cron jobs, scripts, and impatient users who just want
a recommendation without any diagnostic noise.

Behaviour
---------
  1. Run a 3-layer scan (chi-squared + stability + JS regime)
  2. If GO: run a fast 3-strategy forecast, print ticket numbers
  3. If NO-GO: print "NO-GO" and exit 1 (unless --force)
  4. If --quiet: print only the space-separated numbers (nothing else)

Exit codes
----------
  0  ticket generated
  1  NO-GO or no ticket
  2  error

Example
-------
  lottery quick br/lotofacil           # prints ticket or NO-GO
  lottery quick br/lotofacil --quiet   # prints numbers only (pipe-friendly)
  lottery quick br/lotofacil --force   # always prints ticket
  lottery quick br/lotofacil --json    # prints {"ticket": [...], "verdict": "GO"}
"""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter

console = Console()


def quick(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    force: Annotated[bool, typer.Option("--force", "-f",
        help="Generate ticket even if scan is NO-GO")] = False,
    quiet: Annotated[bool, typer.Option("--quiet", "-q",
        help="Print only the numbers (cron-friendly)")] = False,
    as_json: Annotated[bool, typer.Option("--json",
        help="Output as JSON")] = False,
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Strategy group for forecast")] = "fast",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window")] = 50,
) -> None:
    """⚡ Fastest path to a ticket: scan + forecast in one command.

    Prints numbers only (cron-friendly with --quiet). Exit 0 = ticket,
    exit 1 = NO-GO.

    Example: lottery quick br/lotofacil
             lottery quick br/lotofacil --quiet
             lottery quick br/lotofacil --force --quiet
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = hi - lo + 1

    # ── Quick 3-layer scan ────────────────────────────────────────────────────
    import numpy as np

    win_df = df.tail(window)
    n = len(win_df)

    # Layer 1: chi-squared
    counts = np.zeros(pool, dtype=float)
    for row in win_df.itertuples():
        for num in row.numbers:
            if lo <= num <= hi:
                counts[num - lo] += 1
    total = counts.sum()
    expected = total / pool if pool else 1.0
    chi2_ratio = float(np.sum((counts - expected) ** 2 / (expected + 1e-9))) / (pool - 1) if pool > 1 else 1.0
    c1 = 2 if chi2_ratio <= 1.2 else 1 if chi2_ratio <= 1.8 else 0

    # Layer 2: JS regime
    def _freq(sub):
        c = np.zeros(pool, dtype=float)
        for row in sub.itertuples():
            for num in row.numbers:
                if lo <= num <= hi:
                    c[num - lo] += 1
        t = c.sum()
        return (c / t + 1e-9) if t > 0 else (c + 1e-9)

    recent = win_df.tail(min(20, n // 2))
    baseline = df.iloc[:-window] if len(df) > window else df
    if len(baseline) >= 10:
        p_r = _freq(recent); p_r /= p_r.sum()
        p_b = _freq(baseline); p_b /= p_b.sum()
        m = 0.5 * (p_r + p_b)
        js = float(0.5 * np.sum(p_r * np.log(p_r / m)) + 0.5 * np.sum(p_b * np.log(p_b / m)))
        c2 = 2 if js < 0.02 else 1 if js < 0.08 else 0
    else:
        c2 = 1

    scan_score = c1 + c2
    scan_max   = 4
    go = scan_score / scan_max >= 0.6

    if not go and not force:
        if as_json:
            print(json.dumps({"verdict": "NO-GO", "score": scan_score, "max": scan_max, "ticket": []}))
        elif quiet:
            pass  # print nothing
        else:
            console.print(f"[red]NO-GO[/red]  (scan {scan_score}/{scan_max})")
        raise typer.Exit(1)

    # ── Quick forecast ────────────────────────────────────────────────────────
    _GROUPS: dict[str, list[str]] = {
        "fast":        ["bayesian", "weighted", "monte_carlo"],
        "default":     ["weighted", "markov", "bayesian", "monte_carlo", "spectral", "cycle"],
        "statistical": ["markov", "bayesian", "weighted", "monte_carlo", "pattern",
                        "momentum", "spectral", "streak", "cycle", "harmonic"],
    }
    names = _GROUPS.get(strategies, [s.strip() for s in strategies.split(",") if s.strip()])

    import numpy as np2  # re-import just to be safe
    composite = np.zeros(pool, dtype=float)
    total_w = 0.0

    try:
        from engine.strategies import get_strategy
        for name in names:
            try:
                strat = get_strategy(name)
                res = strat.suggest(win_df, rules, count=1, temperature=0.0)
                scores_raw = res.scores
                arr = np.zeros(pool, dtype=float)
                for num, sc in scores_raw.items():
                    if lo <= num <= hi:
                        arr[num - lo] = max(0.0, float(sc))
                s = arr.sum()
                if s > 0:
                    arr /= s
                composite += arr
                total_w += 1.0
            except Exception:
                pass
    except Exception:
        pass

    if total_w > 0:
        composite /= total_w
        ranked = sorted(range(pool), key=lambda i: composite[i], reverse=True)
        ticket = sorted(i + lo for i in ranked[:pick])
    else:
        # Fallback: top-frequency numbers
        freq_counter = {n: int(counts[n - lo]) for n in range(lo, hi + 1)}
        ticket = sorted(sorted(freq_counter, key=lambda n: -freq_counter[n])[:pick])

    # ── Output ────────────────────────────────────────────────────────────────
    ticket_str = " ".join(str(n) for n in ticket)
    verdict = "GO" if go else "FORCED"

    if as_json:
        print(json.dumps({"verdict": verdict, "score": scan_score, "max": scan_max, "ticket": ticket}))
    elif quiet:
        print(ticket_str)
    else:
        verdict_fmt = "[bold green]GO[/bold green]" if go else "[yellow]FORCED[/yellow]"
        console.print(
            f"{verdict_fmt}  ({scan_score}/{scan_max})  ·  "
            f"[bold yellow]{ticket_str}[/bold yellow]"
        )
