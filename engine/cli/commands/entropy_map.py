"""
Entropy Map Command 🌀
======================
Generates an interactive 2D heatmap of spatial Shannon entropy.
Identifies 'Information Peaks' and 'Chaos Voids' on the bet slip.
"""

from __future__ import annotations

import os
import math
from typing import Annotated, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import typer
from rich.console import Console

from engine.cli.utils import get_adapter

console = Console()

def calculate_local_entropy(n: int, draw_matrix: np.ndarray, width: int) -> float:
    """Calculate Shannon entropy for a number based on its neighbors' co-occurrence."""
    n_draws, pool_size = draw_matrix.shape
    idx = n - 1
    
    # Get neighbors (up, down, left, right)
    row = idx // width
    col = idx % width
    
    neighbor_indices = []
    if col > 0: neighbor_indices.append(idx - 1)
    if col < width - 1 and idx + 1 < pool_size: neighbor_indices.append(idx + 1)
    if row > 0: neighbor_indices.append(idx - width)
    if idx + width < pool_size: neighbor_indices.append(idx + width)
    
    if not neighbor_indices:
        return 0.0
        
    # P(neighbor | n is drawn)
    n_hits = np.sum(draw_matrix[:, idx])
    if n_hits == 0:
        return 0.0
        
    probabilities = []
    for n_idx in neighbor_indices:
        # Number of times both n and neighbor were drawn
        co_occur = np.sum((draw_matrix[:, idx] == 1) & (draw_matrix[:, n_idx] == 1))
        p = co_occur / n_hits
        if p > 0:
            probabilities.append(p)
            
    # Shannon Entropy H = - sum(p * log2(p))
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

def entropy_map(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to analyze")] = 300,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
) -> None:
    """🌀 Map the 'Information Density' of the bet slip.

    Calculates local Shannon entropy for each number on the grid.
    Low entropy (blue) indicates highly predictable clusters.
    High entropy (red) indicates high-uncertainty 'Chaos Voids'.
    Useful for balancing a ticket between certainty and random coverage.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    width = rules.board_cols or 10
    height = (pool_size + width - 1) // width
    
    if output is None:
        output = f"data/entropy_map_{lottery.replace('/', '_')}.html"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws)
    
    # 1. Build Signal Matrix
    all_numbers = list(range(lo, hi + 1))
    matrix = np.zeros((n_draws, pool_size))
    for i, row in enumerate(window.itertuples()):
        for n in row.numbers:
            if lo <= n <= hi:
                matrix[i, n - lo] = 1.0
                
    # 2. Calculate Local Entropy for every cell
    entropies = []
    for n in all_numbers:
        h = calculate_local_entropy(n, matrix, width)
        entropies.append(h)
        
    # Reshape to grid
    grid = np.zeros((height, width))
    for idx, h in enumerate(entropies):
        r = idx // width
        c = idx % width
        if r < height and c < width:
            grid[r, c] = h
            
    # 3. Create Interactive Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=grid,
        x=[str(i+1) for i in range(width)],
        y=[str(i+1) for i in range(height)],
        colorscale='RdBu_r', # Red for high entropy, Blue for low
        text=[[f"Num: {r*width + c + 1}<br>Entropy: {grid[r,c]:.3f}" for c in range(width)] for r in range(height)],
        hoverinfo='text'
    ))

    fig.update_layout(
        title=f"Spatial Entropy Map — {rules.name} (Window: {n_draws})",
        xaxis_title="Column",
        yaxis_title="Row",
        yaxis_autorange='reversed'
    )
    
    fig.write_html(output)
    
    console.print(f"\n[bold green]✅ Entropy Map generated:[/bold green] [cyan]{output}[/cyan]")
    console.print("[dim]Identify structural stability vs. high-information zones visually.[/dim]")

if __name__ == "__main__":
    entropy_map("br/lotofacil")
