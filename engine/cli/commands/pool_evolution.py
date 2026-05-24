"""
Pool Evolution Command 🌊
========================
Visualizes how the 'Hot/Cold/Warm' partitions of the number pool 
have shifted over time using an interactive Plotly stacked area chart.
"""

from __future__ import annotations

import os
from typing import Annotated, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import typer
from rich.console import Console

from engine.cli.utils import get_adapter

console = Console()

def pool_evolution(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to trace")] = 100,
    window: Annotated[int, typer.Option("--window", "-w", help="Rolling window size for hot/cold definition")] = 15,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
) -> None:
    """🌊 Visualize the dynamic shifts in Hot/Warm/Cold numbers over time.

    Calculates the state of every number at each historical step using a rolling window.
    Generates a stacked area chart showing the macroscopic thermal regime of the drum.
    Useful for deciding between momentum (if Heating) or mean-reversion (if Cooling) strategies.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    
    if output is None:
        output = f"data/pool_evolution_{lottery.replace('/', '_')}.html"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    df = df.sort_values("draw_id").reset_index(drop=True)
    n_total = len(df)
    
    # We need to trace the last `draws` draws. But we need `window` draws before that to calculate state.
    start_idx = n_total - draws
    if start_idx < window:
        console.print(f"[red]Not enough history. Need at least {draws + window} draws.[/red]")
        return
        
    # Build binary matrix for fast rolling sums
    matrix = np.zeros((n_total, pool_size))
    for i, row in enumerate(df.itertuples()):
        for n in row.numbers:
            if lo <= n <= hi:
                matrix[i, n - lo] = 1.0

    hot_counts = []
    warm_counts = []
    cold_counts = []
    draw_ids = []

    # Calculate expected hits in the window
    expected_hits = window * (rules.pick_count / pool_size)

    with console.status("[cyan]Tracing pool thermodynamics..."):
        for t in range(start_idx, n_total):
            draw_ids.append(df.iloc[t]["draw_id"])
            
            # The window of history up to time t
            history_window = matrix[t - window:t]
            hits = np.sum(history_window, axis=0)
            
            # Thresholds
            # Hot: > 1.3 * expected
            # Cold: < 0.7 * expected
            # Warm: in between
            hot = np.sum(hits > expected_hits * 1.3)
            cold = np.sum(hits < expected_hits * 0.7)
            warm = pool_size - hot - cold
            
            hot_counts.append(hot)
            warm_counts.append(warm)
            cold_counts.append(cold)
            
    # Plotly Stacked Area Chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=draw_ids, y=cold_counts,
        mode='lines',
        line=dict(width=0.5, color='blue'),
        fill='tozeroy',
        name='Cold Numbers (< 0.7x expected)'
    ))
    
    # For stacking, we add the previous values
    y_warm = [c + w for c, w in zip(cold_counts, warm_counts)]
    fig.add_trace(go.Scatter(
        x=draw_ids, y=y_warm,
        mode='lines',
        line=dict(width=0.5, color='orange'),
        fill='tonexty',
        name='Warm Numbers (Average)'
    ))
    
    y_hot = [w + h for w, h in zip(y_warm, hot_counts)]
    fig.add_trace(go.Scatter(
        x=draw_ids, y=y_hot,
        mode='lines',
        line=dict(width=0.5, color='red'),
        fill='tonexty',
        name='Hot Numbers (> 1.3x expected)'
    ))

    fig.update_layout(
        title=f"Pool Thermodynamics (Evolution of Hot/Cold States) — {rules.name}",
        xaxis_title="Draw ID",
        yaxis_title="Number of Balls in Pool",
        hovermode="x unified"
    )
    
    fig.write_html(output)
    
    console.print(f"\n[bold green]✅ Pool Evolution Map generated:[/bold green] [cyan]{output}[/cyan]")
    
    # Verdict
    current_hot = hot_counts[-1]
    current_cold = cold_counts[-1]
    avg_hot = np.mean(hot_counts)
    
    if current_hot > avg_hot * 1.2:
        verdict = "[red]OVERHEATING[/red]: The pool has too many hot numbers. Expect mean-reversion (Cold numbers to wake up)."
    elif current_cold > np.mean(cold_counts) * 1.2:
        verdict = "[blue]FREEZING OVER[/blue]: High entropy. The game is highly distributed right now."
    else:
        verdict = "[green]STABLE[/green]: Normal thermodynamic regime. Standard strategies apply."
        
    console.print(f"Current Regime Verdict: {verdict}")

if __name__ == "__main__":
    pool_evolution("br/mega-sena", draws=100)
