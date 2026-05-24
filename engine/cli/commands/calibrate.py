"""
Calibrate Command 🎯
====================
Empirical strategy calibration — ranks strategies by real hit rates against
historical draws rather than statistical proxies.

Algorithm (strict out-of-sample)
---------------------------------
For each target draw d in the last N draws:
  1. Training data = all draws BEFORE d (no lookahead)
  2. Run strategy.suggest() on training data → top pick_count numbers
  3. Count hits = |predicted ∩ actual|

Aggregate across all target draws:
  • mean_hits  — average match count
  • hit_rate   — mean_hits / pick_count  (fraction of picks that matched)
  • baseline   — expected random hit rate = pick_count / pool_size
  • lift       — hit_rate / baseline  (> 1 = above random)
  • lift_pct   — (lift − 1) × 100

Comparison
----------
  Leaderboard:  statistical proxies (stability × discrimination)
  Calibrate:    real outcomes (did the strategy's picks appear?)

These are complementary — a strategy can score well on one but not the other.
High lift with low leaderboard score = overfitted. High leaderboard score with
lift ≈ 1 = statistically clean but not predictive.

Example
-------
  lottery calibrate br/lotofacil
  lottery calibrate br/lotofacil --draws 30
  lottery calibrate br/lotofacil --strategies statistical --draws 20
  lottery calibrate br/lotofacil --export-md calibration.md
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary
from engine.strategies import get_strategy, STRATEGY_PRESETS, list_strategies

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_CAL_CACHE = _DATA_DIR / "calibration_cache.json"


def calibrate(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to test against (more = slower)")] = 15,
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Group: default | fast | statistical | esoteric | comma-list")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Training window size (draws before each target)")] = 50,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append calibration report to this .md file")] = None,
    min_training: Annotated[int, typer.Option("--min-training",
        help="Minimum training draws required; skip earlier targets")] = 30,
) -> None:
    """🎯 Empirical strategy calibration — rank by actual out-of-sample hit rates.

    Tests each strategy in strict out-of-sample fashion: train on draws before
    target, predict, count matches with actual draw. Ranks all strategies by
    mean hit count and lift over random baseline.

    Example: lottery calibrate br/lotofacil
             lottery calibrate br/lotofacil --draws 30
             lottery calibrate br/lotofacil --strategies statistical --draws 20
    """
    print_command_summary("calibrate", lottery, strategies=strategies, draws=draws, window=window)

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    pick_count = rules.pick_count

    # Resolve strategy list (Smart Expansion)
    raw_names = [s.strip() for s in strategies.split(",") if s.strip()]
    strat_names = []
    
    for name in raw_names:
        if name == "all":
            strat_names.extend([s["name"] for s in list_strategies()])
        elif name in STRATEGY_PRESETS:
            strat_names.extend(STRATEGY_PRESETS[name])
        elif name == "default":
            # Calibrate specific default group
            strat_names.extend(["weighted", "markov", "bayesian", "monte_carlo", "spectral", "cycle"])
        else:
            strat_names.append(name)
            
    # Deduplicate while preserving order
    strat_names = list(dict.fromkeys(strat_names))

    # Validate strategies up front
    valid: list[str] = []
    for name in strat_names:
        try:
            get_strategy(name)
            valid.append(name)
        except Exception:
            console.print(f"  [dim]skip {name} (not available)[/dim]")
    strat_names = valid

    if not strat_names:
        console.print("[red]No valid strategies.[/red]")
        raise typer.Exit(1)

    # Select target draws (last N, with enough training history before each)
    all_rows = df.reset_index(drop=True)
    n_total  = len(all_rows)
    target_indices: list[int] = []
    for i in range(n_total - draws, n_total):
        if i < min_training:
            continue
        target_indices.append(i)

    if not target_indices:
        console.print(f"[red]Not enough draws. Need ≥{draws + min_training}, have {n_total}.[/red]")
        raise typer.Exit(1)

    n_targets = len(target_indices)
    console.print(
        f"\n[dim]Testing {len(strat_names)} strategies over {n_targets} target draws "
        f"(training window ≤ {window} draws each)...[/dim]\n"
    )

    # Random baseline: expected hits when randomly picking pick_count from pool
    baseline = pick_count * pick_count / pool_size  # E[hits] if strategy == random

    # ── Main calibration loop ─────────────────────────────────────────────────
    results: dict[str, list[int]] = defaultdict(list)

    with console.status("") as status:
        for t_idx, target_pos in enumerate(target_indices):
            target_row   = all_rows.iloc[target_pos]
            actual_nums  = set(target_row["numbers"])
            # Training: draws strictly before target_pos, capped at window
            train_start  = max(0, target_pos - window)
            train_df     = all_rows.iloc[train_start:target_pos]

            if len(train_df) < min_training:
                continue

            for name in strat_names:
                status.update(
                    f"[dim]draw {t_idx+1}/{n_targets}  strategy {name}…[/dim]"
                )
                try:
                    strat  = get_strategy(name)
                    res    = strat.suggest(train_df, rules, count=1, temperature=0.0)
                    ticket = sorted(res.tickets[0]) if res.tickets else []
                    hits   = len(set(ticket) & actual_nums)
                    results[name].append(hits)
                except Exception:
                    pass

    if not results:
        console.print("[red]No results produced.[/red]")
        raise typer.Exit(1)

    # ── Build ranked table ────────────────────────────────────────────────────
    rows: list[dict] = []
    for name, hit_list in results.items():
        if not hit_list:
            continue
        mean_h  = float(np.mean(hit_list))
        std_h   = float(np.std(hit_list))
        hr      = mean_h / pick_count
        lift    = hr / (baseline / pick_count) if baseline > 0 else 1.0
        lift_pct = (lift - 1.0) * 100.0
        best    = max(hit_list)
        n       = len(hit_list)
        rows.append({
            "name":      name,
            "mean_hits": mean_h,
            "std":       std_h,
            "hit_rate":  hr,
            "lift":      lift,
            "lift_pct":  lift_pct,
            "best":      best,
            "n":         n,
        })

    rows.sort(key=lambda r: r["lift"], reverse=True)

    table = Table(
        title=f"Strategy Calibration — {rules.name}  ({n_targets} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    table.add_column("#",         justify="right",  style="dim")
    table.add_column("Strategy",  style="cyan")
    table.add_column("Mean hits", justify="right")
    table.add_column("±σ",        justify="right",  style="dim")
    table.add_column("Hit rate",  justify="right")
    table.add_column("Lift",      justify="right")
    table.add_column("Lift %",    justify="right")
    table.add_column("Best",      justify="right",  style="dim")
    table.add_column("N",         justify="right",  style="dim")

    for rank, r in enumerate(rows, 1):
        lift_str  = f"{r['lift']:.3f}"
        lift_fmt  = (
            f"[bold green]{lift_str}[/bold green]" if r["lift"] >= 1.05
            else f"[green]{lift_str}[/green]" if r["lift"] >= 1.01
            else f"[red]{lift_str}[/red]" if r["lift"] < 0.97
            else f"[dim]{lift_str}[/dim]"
        )
        lp        = r["lift_pct"]
        lp_str    = f"{'+'if lp >= 0 else ''}{lp:.1f}%"
        lp_fmt    = (
            f"[green]{lp_str}[/green]" if lp >= 1
            else f"[red]{lp_str}[/red]" if lp < -1
            else f"[dim]{lp_str}[/dim]"
        )
        table.add_row(
            str(rank),
            r["name"],
            f"{r['mean_hits']:.3f}",
            f"±{r['std']:.3f}",
            f"{r['hit_rate']:.4f}",
            lift_fmt,
            lp_fmt,
            str(r["best"]),
            str(r["n"]),
        )

    console.print()
    console.print(table)

    # Baseline row
    bl_hits = baseline
    console.print(
        f"\n[dim]Random baseline: {bl_hits:.3f} expected hits/draw  "
        f"(pick {pick_count} from {pool_size})  |  "
        f"Lift > 1.0 = above random[/dim]"
    )

    # Best strategy summary
    if rows:
        top = rows[0]
        verdict = "above" if top["lift"] > 1.0 else "at or below"
        console.print()
        console.print(Panel(
            f"Best: [bold cyan]{top['name']}[/bold cyan]  "
            f"mean hits={top['mean_hits']:.3f}  lift={top['lift']:.3f}  "
            f"({verdict} random baseline)\n"
            f"[dim]Tested {n_targets} draws  ·  training window ≤ {window}[/dim]",
            title="🎯 Calibration Summary",
            border_style="cyan",
        ))

    # Save to cache (used by forecast --use-calibration)
    _save_cache(lottery, rows)
    console.print(f"[dim]✔ Calibration cached to {_CAL_CACHE.name}[/dim]")

    if export_md:
        _append_md(export_md, lottery, rules.name, _date.today(), rows,
                   n_targets, window, baseline, pick_count, pool_size)
        console.print(f"[green]✔ Calibration report appended to {export_md}[/green]")


def _save_cache(lottery: str, rows: list[dict]) -> None:
    """Persist calibration lift scores to data/calibration_cache.json."""
    try:
        existing: dict = {}
        if _CAL_CACHE.exists():
            existing = json.loads(_CAL_CACHE.read_text())
        existing[lottery] = {
            "date": _date.today().isoformat(),
            "strategies": {r["name"]: r["lift"] for r in rows},
        }
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        _CAL_CACHE.write_text(json.dumps(existing, indent=2))
    except Exception:
        pass


def load_calibration_weights(lottery: str, strat_names: list[str]) -> dict[str, float] | None:
    """Return lift-based weights for the given strategies, or None if no cache."""
    if not _CAL_CACHE.exists():
        return None
    try:
        cache = json.loads(_CAL_CACHE.read_text())
        entry = cache.get(lottery)
        if not entry:
            return None
        strat_lifts = entry.get("strategies", {})
        # Only return if we have lift data for at least one of the requested strategies
        weights = {name: max(0.01, strat_lifts.get(name, 1.0)) for name in strat_names}
        if all(w == 1.0 for w in weights.values()):
            return None  # No calibration data available for these strategies
        return weights
    except Exception:
        return None


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    rows: list[dict], n_targets: int, window: int,
    baseline: float, pick_count: int, pool_size: int,
) -> None:
    top = rows[0]["name"] if rows else "—"
    top_lift = f"{rows[0]['lift']:.3f}" if rows else "—"

    header = f"""
---
type: diagnostic
subtype: calibration
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_tested: {n_targets}
training_window: {window}
baseline_hits: {baseline:.3f}
top_strategy: {top}
top_lift: {top_lift}
---

## Calibration: {game_name} ({today.isoformat()})

| # | Strategy | Mean Hits | Hit Rate | Lift | Lift % | Best | N |
|---|----------|-----------|----------|------|--------|------|---|
"""
    table_rows = ""
    for rank, r in enumerate(rows, 1):
        lp = f"+{r['lift_pct']:.1f}%" if r["lift_pct"] >= 0 else f"{r['lift_pct']:.1f}%"
        table_rows += (
            f"| {rank} | {r['name']} | {r['mean_hits']:.3f} | {r['hit_rate']:.4f} "
            f"| {r['lift']:.3f} | {lp} | {r['best']} | {r['n']} |\n"
        )

    footer = f"\n*Random baseline: {baseline:.3f} hits/draw  ·  pick {pick_count} from {pool_size}*\n"

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(header + table_rows + footer)
