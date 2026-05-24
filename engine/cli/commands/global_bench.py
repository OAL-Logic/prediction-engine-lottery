"""
Global Benchmark Command 🏆
==========================
Exhaustive performance analysis of all strategies across all lotteries.
Ranks strategies by 'Global Lift' to find the most dominant models.
"""

from __future__ import annotations

from typing import Annotated, Optional, List, Dict
import pandas as pd
import numpy as np
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from engine.adapters.registry import registry
from engine.cli.utils import get_adapter
from engine.strategies import list_strategies, get_strategy

console = Console()

def global_bench(
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to test for each lottery")] = 10,
    limit: Annotated[int, typer.Option("--limit", "-L", help="History window for each strategy")] = 50,
) -> None:
    """🏆 Exhaustive Backtest of ALL strategies across ALL lotteries.

    Runs a massive cross-validation loop to identify which strategies 
    consistently capture the top-N winning numbers across different games.
    Outputs a 'Global MVP' leaderboard.
    """
    all_strategies = list_strategies()
    all_games = [g for g in registry.list_games() if g.data_available]
    
    results: Dict[str, list[float]] = {s["name"]: [] for s in all_strategies}
    
    total_tasks = len(all_games) * len(all_strategies)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Running Global Benchmark...", total=total_tasks)
        
        for game in all_games:
            try:
                adapter = get_adapter(game.id)
                df = adapter.fetch()
                rules = adapter.rules
                pick = rules.pick_count
                
                target_draws = df.tail(draws)
                
                for s_meta in all_strategies:
                    s_name = s_meta["name"]
                    progress.update(task, description=f"[cyan]Benchmarking {s_name} on {game.name}...")
                    
                    hits_acc = []
                    for row in target_draws.itertuples():
                        t_id = row.draw_id
                        winning_nums = set(row.numbers)
                        
                        # Data BEFORE this draw
                        train_df = df[df["draw_id"] < t_id]
                        if len(train_df) < 10: continue
                        
                        try:
                            strat = get_strategy(s_name)
                            res = strat.suggest(train_df, rules, history_limit=limit, count=1)
                            # Top N capture
                            scores = res.scores
                            top_n = sorted(scores.keys(), key=lambda x: scores.get(x, 0.0), reverse=True)[:pick]
                            hits = len(set(top_n) & winning_nums)
                            hits_acc.append(hits / pick) # Normalized hit rate
                        except:
                            continue
                            
                    if hits_acc:
                        results[s_name].append(np.mean(hits_acc))
                    
                    progress.advance(task)
            except:
                progress.advance(task, advance=len(all_strategies))
                continue

    # 2. Compile Leaderboard
    leaderboard = []
    for s_name, scores in results.items():
        if scores:
            avg_lift = np.mean(scores)
            leaderboard.append({
                "Strategy": s_name,
                "Global Lift": avg_lift,
                "Reliability": len(scores) / len(all_games)
            })
            
    leaderboard.sort(key=lambda x: x["Global Lift"], reverse=True)
    
    # 3. Display Results
    console.rule("[bold yellow]🏆 GLOBAL STRATEGY MVP LEADERBOARD[/bold yellow]")
    
    table = Table(box=None, header_style="bold cyan")
    table.add_column("Rank", justify="center")
    table.add_column("Strategy", style="bold white")
    table.add_column("Global Lift (Avg)", justify="right", style="green")
    table.add_column("Market Coverage", justify="right", style="dim")
    
    for i, entry in enumerate(leaderboard[:15]): # Top 15
        table.add_row(
            str(i + 1),
            entry["Strategy"],
            f"{entry['Global Lift']:.4f}",
            f"{entry['Reliability']*100:.0f}%"
        )
        
    console.print(table)
    
    if leaderboard:
        mvp = leaderboard[0]["Strategy"]
        summary = (
            f"The current Global MVP is [bold green]{mvp.upper()}[/bold green].\n\n"
            "Recommendations:\n"
            "• Use MVP for high-stakes consensus.\n"
            "• Avoid bottom-tier models in the current volatility regime."
        )
        console.print(Panel(summary, title="Global Benchmark Verdict", border_style="yellow"))

if __name__ == "__main__":
    global_bench(draws=3)
