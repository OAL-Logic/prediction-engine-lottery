"""
Cluster Walk Command 🚶‍♂️
=========================
Visualizes the 'Drift Path' of recent draws across the UMAP manifold.
Shows whether the draw mechanism is currently dwelling in a specific 
topological cluster or jumping chaotically.
"""

from __future__ import annotations

import os
from typing import Annotated, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import typer
from rich.console import Console

try:
    import umap
except ImportError:
    umap = None

from engine.cli.utils import get_adapter

console = Console()

def cluster_walk(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws for manifold base")] = 300,
    path_length: Annotated[int, typer.Option("--path", "-p", help="Length of recent draw path to trace")] = 15,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
) -> None:
    """🚶‍♂️ Visualize the recent trajectory of draws through the topological manifold."""
    if umap is None:
        console.print("[bold red]Error:[/] 'umap-learn' is required. Install with: pip install umap-learn")
        return

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    
    if output is None:
        output = f"data/cluster_walk_{lottery.replace('/', '_')}.html"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws).copy()
    
    # 1. Vectorize
    pool_size = hi - lo + 1
    matrix = np.zeros((n_draws, pool_size))
    for i, row in enumerate(window.itertuples()):
        for n in row.numbers:
            if lo <= n <= hi:
                matrix[i, n - lo] = 1.0
                
    # 2. UMAP Projection
    with console.status(f"[cyan]Projecting manifold and tracing last {path_length} draws..."):
        reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='jaccard', random_state=42)
        embedding = reducer.fit_transform(matrix)
        
        window['x'] = embedding[:, 0]
        window['y'] = embedding[:, 1]
        window['draw_label'] = window['draw_id'].apply(lambda x: f"Draw {x}")
        window['nums_label'] = window['numbers'].apply(lambda x: ", ".join(map(str, x)))
        
        # Base manifold scatter
        fig = px.scatter(
            window, x='x', y='y', color='draw_id',
            hover_name='draw_label', hover_data={'draw_id': False, 'nums_label': True, 'x': False, 'y': False},
            color_continuous_scale='Greys',
            title=f"Manifold Trajectory Walk — {rules.name}"
        )
        fig.update_traces(marker=dict(size=4, opacity=0.3))
        
        # Add path
        path_df = window.tail(path_length)
        fig.add_trace(go.Scatter(
            x=path_df['x'], y=path_df['y'],
            mode='lines+markers+text',
            text=[f"{i}" for i in range(1, path_length + 1)],
            textposition="top center",
            line=dict(color='red', width=2),
            marker=dict(size=8, color='red', symbol='cross'),
            name='Recent Trajectory'
        ))
        
        # Highlight last draw
        last_draw = path_df.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_draw['x']], y=[last_draw['y']],
            mode='markers',
            marker=dict(size=14, color='yellow', symbol='star'),
            name='Latest Draw'
        ))

        fig.write_html(output)
        
    console.print(f"\n[bold green]✅ Cluster Walk Map generated:[/bold green] [cyan]{output}[/cyan]")
    console.print(f"[dim]Shows the drift path of the last {path_length} draws across the historical manifold.[/dim]")

if __name__ == "__main__":
    cluster_walk("br/mega-sena")
