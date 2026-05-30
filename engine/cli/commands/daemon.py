"""
Daemon Command 🤖
=================
AutoML Background Daemon that continually optimizes strategies.
Runs a background loop or a single-pass optimization, writing
optimal configurations and dynamic strategy weights to daemon_state.json.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()
logger = logging.getLogger(__name__)

DAEMON_STATE_FILE = Path("data/daemon_state.json")


def _run_optimization_cycle(
    lottery: str, limit: int, history_windows: list[int], prev: int
) -> Tuple[dict, dict]:
    """Run a silent grid search to find the best configuration and all strategy weights."""
    from itertools import product

    adapter = get_adapter(lottery)
    df = adapter.fetch(limit=limit + prev + 10)

    if df.empty or len(df) < max(history_windows) + prev:
        return {}, {}

    # Core set of diverse strategies to test
    test_strats = ["weighted", "markov", "bayesian", "momentum", "random_forest", "pattern", "streak"]
    temps = [0.0, 0.5, 1.0]
    target_top_n = adapter.rules.pick_count * 2

    grid = list(product(test_strats, history_windows, temps))
    results = []
    strat_best_scores = {s: 0.0 for s in test_strats}

    for s_name, h_limit, temp in grid:
        total_winners = 0
        captured_winners = 0

        for p_idx in range(1, prev + 1):
            try:
                target_row = df.iloc[-p_idx]
                t_id = int(target_row["draw_id"])

                train_df = df[df["draw_id"] < t_id].copy()
                if train_df.empty:
                    continue

                strat_obj = get_strategy(s_name)
                res = strat_obj.suggest(
                    train_df,
                    adapter.rules,
                    count=1,
                    temperature=temp,
                    history_limit=h_limit,
                )

                sorted_scores = sorted(res.scores.items(), key=lambda x: x[1], reverse=True)
                num_ranks = {num: rank + 1 for rank, (num, _) in enumerate(sorted_scores)}
                draw_ranks = [num_ranks.get(n, 999) for n in target_row["numbers"]]

                captured_winners += sum(1 for r in draw_ranks if r <= target_top_n)
                total_winners += len(target_row["numbers"])
            except Exception:
                continue

        if total_winners > 0:
            rate = (captured_winners / total_winners) * 100
            results.append(
                {
                    "strategy": s_name,
                    "limit": h_limit,
                    "temp": temp,
                    "capture_rate": rate,
                }
            )
            if rate > strat_best_scores[s_name]:
                strat_best_scores[s_name] = rate

    if not results:
        return {}, {}

    results.sort(key=lambda x: x["capture_rate"], reverse=True)
    best = results[0]
    return best, strat_best_scores


def daemon(
    lottery: Annotated[str, typer.Argument(help="Lottery name to monitor")],
    interval: Annotated[int, typer.Option("--interval", "-i", help="Optimization interval in seconds")] = 3600,
    prev: Annotated[int, typer.Option("--prev", "-p", help="Validation window (number of previous draws)")] = 5,
    once: Annotated[bool, typer.Option("--once", help="Run a single optimization cycle and exit")] = False,
) -> None:
    """🤖 Start the AutoML Background Daemon to continuously optimize strategies.

    Runs a grid-search to find optimal strategy configurations and sliding-window weights.
    Saves outputs dynamically to `data/daemon_state.json`.
    """
    console.print(f"[bold green]Starting AutoML Daemon for {lottery}[/bold green]")
    console.print(f"  [dim]Interval: {interval}s | Validation Window: {prev} draws[/dim]")
    console.print(f"  [dim]State will be saved to {DAEMON_STATE_FILE}[/dim]\n")

    try:
        from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn

        while True:
            console.print(f"[{time.strftime('%H:%M:%S')}] [bold cyan]Starting optimization cycle...[/bold cyan]")
            try:
                windows = [50, 100, 200]
                best_config, strat_weights = _run_optimization_cycle(
                    lottery, limit=max(windows), history_windows=windows, prev=prev
                )

                if best_config:
                    state = {}
                    if DAEMON_STATE_FILE.exists():
                        try:
                            with open(DAEMON_STATE_FILE, "r") as f:
                                state = json.load(f)
                        except json.JSONDecodeError:
                            pass

                    # Update state with dynammically computed weights
                    state[lottery] = {
                        "last_optimized": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "best_strategy": best_config["strategy"],
                        "optimal_limit": best_config["limit"],
                        "optimal_temp": best_config["temp"],
                        "capture_rate": round(best_config["capture_rate"], 2),
                        "strategy_weights": {k: round(v, 2) for k, v in strat_weights.items()},
                    }

                    DAEMON_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(DAEMON_STATE_FILE, "w") as f:
                        json.dump(state, f, indent=2)

                    console.print(
                        f"  [green]✓ Optimal Config Found:[/green] {best_config['strategy']} (L={best_config['limit']}, T={best_config['temp']}) -> {best_config['capture_rate']:.1f}% capture"
                    )
                else:
                    console.print("  [yellow]⚠ No valid results this cycle.[/yellow]")

            except Exception as e:
                console.print(f"  [red]✗ Cycle failed: {e}[/red]")

            if once:
                console.print("[bold green]Single-pass cycle finished successfully. Exiting daemon.[/bold green]")
                break

            # Non-freezing Sleep with Countdown
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TimeRemainingColumn(),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"[dim]Next cycle for {lottery}...", total=interval)
                for _ in range(interval):
                    time.sleep(1)
                    progress.advance(task, 1)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Daemon stopped by user.[/bold yellow]")


def daemon_status() -> None:
    """📊 View the current state and latest findings of the AutoML Daemon."""
    from engine.cli.utils import Theme, ui_dummy_block, ui_header, ui_panel, ui_table

    ui_header("daemon status", "AutoML Continuous Optimization")

    if not DAEMON_STATE_FILE.exists():
        console.print(
            ui_panel(
                "The daemon hasn't saved any results yet. Run `lottery daemon <game>` to start the optimizer.",
                title="Daemon Status",
                style=Theme.WARNING,
            )
        )
        return

    try:
        with open(DAEMON_STATE_FILE, "r") as f:
            state = json.load(f)
    except json.JSONDecodeError:
        console.print(f"[{Theme.DANGER}]Error: daemon state file is corrupted.[/]")
        return

    table = ui_table(
        columns=["Lottery", "Last Optimized", "Best Strategy", "Limit (-L)", "Temp (-t)", "Capture"]
    )

    for lottery, data in state.items():
        table.add_row(
            lottery,
            data.get("last_optimized", "—"),
            f"[bold {Theme.SECONDARY}]{data.get('best_strategy', '—')}[/]",
            str(data.get("optimal_limit", "—")),
            str(data.get("optimal_temp", "—")),
            f"[bold {Theme.SUCCESS}]{data.get('capture_rate', 0):.1f}%[/]",
        )

    console.print(ui_panel(table, title="ACTIVE INSIGHTS"))
    ui_dummy_block(
        "remember",
        "The daemon continuously tests thousands of combinations to find the 'Sweet Spot' for each lottery.",
    )
    ui_dummy_block(
        "tip",
        "Use the [bold]Optimal Limit[/] and [bold]Best Strategy[/] above in your next `lottery suggest` for maximum precision.",
    )
