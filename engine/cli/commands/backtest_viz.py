"""
Backtest Visualization Command 📉
=================================
Generates a visual 'Hit-Map' showing strategy performance over time.
Identifies patterns of success and failure (Hits vs Misses) in recent draws.
"""

from __future__ import annotations

from typing import Annotated, Optional, List
import pandas as pd
import numpy as np
import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

def backtest_viz(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to visualize")] = "weighted",
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of draws to backtest")] = 10,
    limit: Annotated[int, typer.Option("--limit", "-L", help="History window for each step")] = 100,
) -> None:
    """📉 Visual Confusion Heatmap of strategy performance over time.

    Rows represent recent draws, Columns represent the Number Pool.
    Legend:
    - [bold green]H[/bold green] : HIT (Strategy ranked it in top-N AND it was drawn)
    - [bold red]X[/bold red] : FALSE POSITIVE (Strategy ranked it high but it missed)
    - [bold blue]![/bold blue] : FALSE NEGATIVE (Number was drawn but strategy missed it)
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pick = rules.pick_count
    
    # We only look at the last N draws for the visualization
    target_draws = df.tail(draws).sort_values("draw_id")
    
    table = Table(title=f"Temporal Performance Map: {strategy} ({rules.name})", box=None, padding=0)
    table.add_column("Draw", style="dim", width=6)
    
    # Number columns
    all_numbers = list(range(lo, hi + 1))
    for n in all_numbers:
        table.add_column(str(n), justify="center", width=2)

    with console.status(f"[cyan]Backtesting {strategy} across {draws} draws..."):
        for row in target_draws.itertuples():
            t_id = row.draw_id
            winning_nums = set(row.numbers)
            
            # Data BEFORE this draw
            train_df = df[df["draw_id"] < t_id]
            
            try:
                strat_obj = get_strategy(strategy)
                res = strat_obj.suggest(train_df, rules, history_limit=limit, count=1)
                # Strategy's top picks
                scores = res.scores
                top_picks = set(sorted(all_numbers, key=lambda n: scores.get(n, 0.0), reverse=True)[:pick])
            except Exception:
                top_picks = set()

            row_cells = [f"#{t_id}"]
            for n in all_numbers:
                is_win = n in winning_nums
                is_pick = n in top_picks
                
                if is_win and is_pick:
                    char = "[bold green]H[/bold green]"
                elif is_pick and not is_win:
                    char = "[red]X[/red]"
                elif is_win and not is_pick:
                    char = "[bold blue]![/bold blue]"
                else:
                    char = "[dim]·[/dim]"
                row_cells.append(char)
            
            table.add_row(*row_cells)

    console.rule(f"[bold cyan]📉 BACKTEST HIT-MAP — {strategy.upper()}[/bold cyan]")
    console.print(table)
    
    # Legend
    legend = (
        "[bold green]H[/] : Hit (Success)  |  "
        "[red]X[/] : False Positive (Over-predicted)  |  "
        "[bold blue]![/] : False Negative (Missed draw)  |  "
        "[dim]·[/] : True Negative"
    )
    console.print(Panel(legend, title="Legend", border_style="dim"))

if __name__ == "__main__":
    backtest_viz("br/lotofacil", draws=5)
