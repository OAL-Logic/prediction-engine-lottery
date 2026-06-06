"""
Tune Command  tune
=================
Grid search optimizer for strategy parameters and filter combinations.
Finds the best configuration for a specific lottery based on historical out-of-sample performance.
"""

from __future__ import annotations

import itertools
import json
import pathlib
from datetime import date as _date
from collections import defaultdict
from typing import Annotated, Any, Optional

import numpy as np
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from engine.cli.utils import get_adapter, load_local_config, print_command_summary
from engine.strategies import  get_strategy, STRATEGY_PRESETS, list_strategies

console = Console()

# --- Parameter Grids ---
PARAM_GRIDS = {
    "bayesian": {
        "alpha0": [0.5, 1.0, 2.0],
        "decay": [0.99, 0.998, 0.999]
    },
    "monte_carlo": {
        "n_simulations": [5000, 10000],
        "sim_temperature": [1.0, 1.2, 1.5]
    },
    "pattern": {
        "sum_coverage": [0.6, 0.7, 0.8]
    },
    "spectral": {
        "minimum_magnitude": [1.5, 2.0, 2.5]
    },
    "void": {
        "w_quadrant": [0.5, 1.0, 1.5],
        "w_row": [0.25, 0.5, 1.0]
    },
    "copairs": {
        "history_limit": [100, 200, 400]
    }
}

# --- Filter Grids ---
FILTER_GRIDS = [
    [],
    ['sum_range'],
    ['parity'],
    ['sum_range', 'parity'],
    ['sum_range', 'parity', 'breadth']
]

# --- Typical Prizes and Payout Helpers ---
_TYPICAL_LOWER: dict[str, dict[int, float]] = {
    "br/mega-sena":  {4: 1_400.0,  5: 36_000.0, 6: 10_000_000.0},
    "br/lotofacil":  {11: 6.0, 12: 25.0, 13: 120.0, 14: 1_200.0, 15: 1_500_000.0},
    "us/powerball":  {3: 7.0,    4: 100.0, 5: 1_000_000.0, 6: 40_000_000.0},
    "us/megamillions": {3: 10.0, 4: 150.0, 5: 1_000_000.0, 6: 40_000_000.0},
}

def _hyp_prob(pool: int, pick: int, match: int) -> float:
    from math import comb
    denom = comb(pool, pick)
    if denom == 0:
        return 0.0
    numer = comb(pick, match) * comb(pool - pick, pick - match)
    return numer / denom

def calculate_simulated_prize(game_id: str, hits: int, rules: Any) -> float:
    prizes = _TYPICAL_LOWER.get(game_id, {})
    if hits in prizes:
        return prizes[hits]
    if hits in rules.prize_tiers:
        lo, hi = rules.number_range
        pool = hi - lo + 1
        pick = rules.pick_count
        prob = _hyp_prob(pool, pick, hits)
        if prob > 0:
            return min(10_000_000.0, rules.ticket_price * 0.5 / prob)
    return 0.0

def tune(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent target draws to test against")] = 30,
    limit: Annotated[int, typer.Option("--limit", "-L",
        help="Training window size (draws before each target)")] = 50,
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Strategies to evaluate: preset (statistical|fast|default) or comma list")] = "statistical",
    no_grid: Annotated[bool, typer.Option("--no-grid",
        help="Skip parameter grids — run each strategy once with defaults (faster)")] = False,
    stacking: Annotated[bool, typer.Option("--stacking",
        help="Train the Stacking AI meta-learner for this lottery")] = False,
    metric: Annotated[str, typer.Option("--metric",
        help="Ranking metric: lift | hits | capture | profit | roi | precision")] = "lift",
    top: Annotated[int, typer.Option("--top",
        help="How many winners to write to the YAML")] = 1,
    fmt: Annotated[str, typer.Option("--format",
        help="YAML output format: flat (backtest/forecast) | report (lottery report)")] = "flat",
    output: Annotated[Optional[str], typer.Option("--output", "-o",
        help="Output YAML path (default: tuned/<lottery>.yaml)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append tune report to this .md file")] = None,
    min_training: Annotated[int, typer.Option("--min-training",
        help="Minimum training draws required; skip earlier targets")] = 30,
) -> None:
    """🧪 Optimize strategy parameters and filters via grid search.

    Evaluates thousands of combinations of (strategy, parameters, filters) against
    historical draws to find the most predictive configuration. Outputs to YAML.
    """
    personal_data = load_local_config()
    
    print_command_summary("tune", lottery, draws=draws, limit=limit, metric=metric, strategies=strategies)

    adapter = get_adapter(lottery)

    # STORY 7.3: Specialized Stacking Mode
    if stacking:
        console.print("[bold cyan]🧠 Stacking AI Mode:[/bold cyan] Training meta-learner to optimize voting weights...")
        from engine.strategies.ml.stacking_ai import StackingAIStrategy
        strat = StackingAIStrategy()
        weights = strat.train(adapter, window=draws)
        
        table = Table(title="🧠 Optimized Stacking Weights", box=None)
        table.add_column("Sub-Strategy", style="bold")
        table.add_column("Learned Weight", justify="right")
        for name, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            style = "green" if w > 0 else "red"
            table.add_row(name, f"[{style}]{w:.4f}[/]")
        console.print(table)
        console.print(f"[bold green]✔ Stacking model updated for {lottery}.[/bold green]")
        return

    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    pick_count = rules.pick_count
    
    # Random baseline
    baseline = pick_count * pick_count / pool_size

    # Resolve strategy list
    raw_names = [s.strip() for s in strategies.split(",") if s.strip()]
    strat_names = []
    for name in raw_names:
        if name == "all":
            strat_names.extend([s["name"] for s in list_strategies()])
        elif name in STRATEGY_PRESETS:
            strat_names.extend(STRATEGY_PRESETS[name])
        else:
            strat_names.append(name)
    strat_names = list(dict.fromkeys(strat_names))

    # Target selection
    all_rows = df.reset_index(drop=True)
    n_total = len(all_rows)
    target_indices = []
    for i in range(n_total - draws, n_total):
        if i < min_training:
            continue
        target_indices.append(i)

    if not target_indices:
        console.print(f"[red]Not enough draws. Need ≥{draws + min_training}, have {n_total}.[/red]")
        raise typer.Exit(1)

    # Build Grid
    candidates = []
    for strat_name in strat_names:
        try:
            # Check if strategy exists
            get_strategy(strat_name)
        except Exception:
            continue

        grid = PARAM_GRIDS.get(strat_name, {})
        if no_grid or not grid:
            # Only default params
            for filters in FILTER_GRIDS:
                candidates.append({
                    "strategy": strat_name,
                    "params": {},
                    "filters": filters
                })
        else:
            # Product of parameters
            keys = list(grid.keys())
            values = list(grid.values())
            for p_combo in itertools.product(*values):
                params = dict(zip(keys, p_combo))
                for filters in FILTER_GRIDS:
                    candidates.append({
                        "strategy": strat_name,
                        "params": params,
                        "filters": filters
                    })

    if not candidates:
        console.print("[red]No valid candidates found for tuning.[/red]")
        raise typer.Exit(1)

    n_candidates = len(candidates)
    n_targets = len(target_indices)
    total_runs = n_candidates * n_targets

    console.print(f"[dim]Evaluating {n_candidates} combinations over {n_targets} draws ({total_runs} total runs)...[/dim]\n")

    results_data = defaultdict(list)
    active_candidates = set(range(n_candidates))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        main_task = progress.add_task("Tuning...", total=total_runs)

        for t_idx, target_pos in enumerate(target_indices):
            target_row = all_rows.iloc[target_pos]
            actual_nums = set(target_row["numbers"])
            
            # Training window
            train_start = max(0, target_pos - limit)
            train_df = all_rows.iloc[train_start:target_pos]
            
            for c_idx, cand in enumerate(candidates):
                # (v11.0) Early-Exit Pruning: Skip candidates that failed earlier checks
                if c_idx not in active_candidates:
                    progress.advance(main_task)
                    continue

                progress.update(main_task, description=f"Draw {t_idx+1}/{n_targets} | {cand['strategy']} {c_idx+1}/{n_candidates}")
                
                try:
                    # Strategy instantiation
                    strat = get_strategy(cand["strategy"], **cand["params"], **personal_data)
                    
                    # Suggestion with filters
                    res = strat.suggest(
                        train_df, 
                        rules, 
                        count=1, 
                        temperature=0.0, 
                        filters=cand["filters"]
                    )
                    
                    ticket = sorted(res.tickets[0]) if res.tickets else []
                    hits = len(set(ticket) & actual_nums) if ticket else 0
                    
                    # Store hits for aggregation
                    combo_key = (cand["strategy"], json.dumps(cand["params"], sort_keys=True), json.dumps(cand["filters"]))
                    results_data[combo_key].append(hits)
                    
                    # (v11.0) Early-Exit Check: After 5 draws, if mean hits < 70% of baseline, prune branch
                    if t_idx == 4 and n_targets > 10:
                        mean_temp = sum(results_data[combo_key]) / 5.0
                        if mean_temp < (baseline * 0.7):
                            active_candidates.remove(c_idx)
                            # logging.debug(f"Pruned {cand['strategy']} branch early (mean_hits={mean_temp:.2f})")
                    
                except Exception:
                    pass
                
                progress.advance(main_task)

    if not results_data:
        console.print("[red]No results produced.[/red]")
        raise typer.Exit(1)

    # Aggregate and Rank
    ranked = []
    for combo_key, hits_list in results_data.items():
        strat_name, params_json, filters_json = combo_key
        params = json.loads(params_json)
        filters = json.loads(filters_json)
        
        mean_hits = float(np.mean(hits_list))
        hit_rate = mean_hits / pick_count
        lift = hit_rate / (baseline / pick_count) if baseline > 0 else 1.0
        capture = sum(1 for h in hits_list if h >= 1) / len(hits_list)
        
        # Simulated financial metrics
        ticket_cost = rules.ticket_price if rules.ticket_price > 0 else 1.0
        total_payout = sum(calculate_simulated_prize(lottery, h, rules) for h in hits_list)
        total_cost = len(hits_list) * ticket_cost
        profit = total_payout - total_cost
        roi = (total_payout / total_cost * 100.0) if total_cost > 0 else 0.0
        
        # Precision metric (hypergeometric/exponential weighting of hits)
        min_win_tier = min(rules.prize_tiers) if rules.prize_tiers else 3
        precision = float(np.mean([2**(h - min_win_tier + 1) if h >= min_win_tier else 0.0 for h in hits_list]))
        
        ranked.append({
            "strategy": strat_name,
            "params": params,
            "filters": filters,
            "mean_hits": mean_hits,
            "lift": lift,
            "capture": capture,
            "profit": profit,
            "roi": roi,
            "precision": precision,
            "n": len(hits_list)
        })

    # Sort by chosen metric
    sort_key = (
        "profit" if metric == "profit"
        else "roi" if metric == "roi"
        else "precision" if metric == "precision"
        else "lift" if metric == "lift"
        else "mean_hits" if metric == "hits"
        else "capture"
    )
    ranked.sort(key=lambda x: x[sort_key], reverse=True)

    # Leaderboard UI
    table = Table(title=f"🏆 Optimization Leaderboard - {rules.name}", box=None, header_style="bold cyan")
    table.add_column("Rank", justify="right", style="dim")
    table.add_column("Strategy")
    table.add_column("Parameters", style="dim")
    table.add_column("Filters", style="dim")
    table.add_column("Mean Hits", justify="right")
    table.add_column("Lift", justify="right")
    table.add_column("Capture", justify="right")
    table.add_column("Net Profit", justify="right")
    table.add_column("ROI%", justify="right")
    table.add_column("Precision", justify="right")

    for i, r in enumerate(ranked[:15], 1):
        p_str = ", ".join([f"{k}={v}" for k, v in r["params"].items()]) if r["params"] else "Default"
        f_str = ",".join(r["filters"]) if r["filters"] else "None"
        
        lift_style = "bold green" if r["lift"] > 1.1 else "green" if r["lift"] > 1.0 else "red"
        profit_style = "bold green" if r["profit"] > 0 else "green" if r["profit"] == 0 else "red"
        roi_style = "bold green" if r["roi"] > 100 else "green" if r["roi"] > 0 else "red"
        
        table.add_row(
            str(i),
            r["strategy"],
            p_str,
            f_str,
            f"{r['mean_hits']:.3f}",
            f"[{lift_style}]{r['lift']:.3f}[/]",
            f"{r['capture']*100:.1f}%",
            f"[{profit_style}]{rules.currency} {r['profit']:.2f}[/]",
            f"[{roi_style}]{r['roi']:.1f}%[/]",
            f"{r['precision']:.2f}"
        )

    console.print("\n")
    console.print(table)

    # Winner Panel
    winner = ranked[0]
    console.print(Panel(
        f"Strategy: [bold cyan]{winner['strategy']}[/bold cyan]\n"
        f"Params: [yellow]{winner['params']}[/yellow]\n"
        f"Filters: [green]{winner['filters']}[/green]\n\n"
        f"Metrics: Lift=[bold]{winner['lift']:.3f}[/] | Mean Hits={winner['mean_hits']:.3f} | Net Profit=[bold]{rules.currency} {winner['profit']:.2f}[/] (ROI: {winner['roi']:.1f}%) | Precision={winner['precision']:.2f}",
        title="✨ Best Configuration Found",
        border_style="gold1"
    ))

    # Save to YAML
    if output:
        output_path = pathlib.Path(output)
    else:
        lottery_slug = lottery.replace("/", "_")
        output_dir = pathlib.Path("tuned")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{lottery_slug}.yaml"

    if fmt == "report":
        tuned_data = {
            "reports": [
                {
                    "name": f"tuned_{r['strategy']}_{i}",
                    "strategy": r["strategy"],
                    "params": r["params"],
                    "filters": r["filters"]
                }
                for i, r in enumerate(ranked[:top])
            ]
        }
    else:
        tuned_data = [
            {
                "name": r["strategy"],
                "params": r["params"],
                "filters": r["filters"],
                "metrics": {
                    "lift": float(r["lift"]),
                    "mean_hits": float(r["mean_hits"]),
                    "capture": float(r["capture"]),
                    "profit": float(r["profit"]),
                    "roi": float(r["roi"]),
                    "precision": float(r["precision"])
                }
            }
            for r in ranked[:top]
        ]

    with open(output_path, "w") as f:
        yaml.dump(tuned_data, f, sort_keys=False)

    console.print(f"\n[bold green]✔ Optimization complete.[/bold green] Configuration saved to [cyan]{output_path}[/cyan]")

    if export_md:
        _append_md(export_md, lottery, rules.name, _date.today(), ranked,
                  n_targets, limit, baseline, pick_count, pool_size, metric, rules.currency)


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    ranked: list[dict], n_targets: int, window: int,
    baseline: float, pick_count: int, pool_size: int, metric: str, currency: str
) -> None:
    winner = ranked[0]
    
    header = f"""
---
type: diagnostic
subtype: tuning
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_tested: {n_targets}
training_window: {window}
baseline_hits: {baseline:.3f}
top_strategy: {winner['strategy']}
top_lift: {winner['lift']:.3f}
top_profit: {winner['profit']:.2f}
top_roi: {winner['roi']:.1f}%
ranking_metric: {metric}
---

## Tuning Report: {game_name} ({today.isoformat()})

| # | Strategy | Parameters | Filters | Mean Hits | Lift | Capture | Net Profit | ROI % | Precision |
|---|----------|------------|---------|-----------|------|---------|------------|-------|-----------|
"""
    table_rows = ""
    for rank, r in enumerate(ranked[:15], 1):
        p_str = ", ".join([f"{k}={v}" for k, v in r["params"].items()]) if r["params"] else "Default"
        f_str = ",".join(r["filters"]) if r["filters"] else "None"
        table_rows += (
            f"| {rank} | {r['strategy']} | {p_str} | {f_str} | {r['mean_hits']:.3f} "
            f"| {r['lift']:.3f} | {r['capture']*100:.1f}% | {currency} {r['profit']:.2f} | {r['roi']:.1f}% | {r['precision']:.2f} |\n"
        )

    footer = f"\n*Random baseline: {baseline:.3f} hits/draw  ·  pick {pick_count} from {pool_size}*\n"

    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(header + table_rows + footer)

if __name__ == "__main__":
    app = typer.Typer()
    app.command()(tune)
    app()
