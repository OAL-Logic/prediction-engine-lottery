"""
Hyper-Explorer Command 🚀
=========================
Project historical draws into a low-dimensional manifold using UMAP.
Visualizes the 'Shape of the Lottery' in interactive 2D/3D.
"""

from __future__ import annotations

import os
from typing import Annotated, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import typer
from rich.console import Console

try:
    import umap
except ImportError:
    umap = None

from engine.cli.utils import get_adapter

console = Console()

def hyper_explorer(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to analyze")] = 500,
    dim: Annotated[int, typer.Option("--dim", "-d", help="Projection dimensions (2 or 3)")] = 2,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
) -> None:
    """🚀 'Fly' through the high-dimensional manifold of historical draws.

    Uses UMAP to find structural relationships between different winning combinations.
    Visualizes the history as a topological surface. 
    Coloring by date reveals 'Temporal Drifts' in the draw physics.
    """
    if umap is None:
        console.print("[bold red]Error:[/] 'umap-learn' is required for this command. Install with: pip install umap-learn")
        return

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    
    if output is None:
        output = f"data/hyper_explorer_{lottery.replace('/', '_')}.html"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws).copy()
    
    # 1. Vectorize Draws
    # Binary occurrence matrix
    pool_size = hi - lo + 1
    matrix = np.zeros((n_draws, pool_size))
    for i, row in enumerate(window.itertuples()):
        for n in row.numbers:
            if lo <= n <= hi:
                matrix[i, n - lo] = 1.0
                
    # 2. UMAP Projection
    console.print(f"[cyan]Projecting {n_draws} draws into {dim}D space using UMAP...")
    reducer = umap.UMAP(n_components=dim, n_neighbors=15, min_dist=0.1, metric='jaccard', random_state=42)
    embedding = reducer.fit_transform(matrix)
    
    # 3. Build Plotly Dataframe
    window['x'] = embedding[:, 0]
    window['y'] = embedding[:, 1]
    if dim == 3:
        window['z'] = embedding[:, 2]
        
    window['draw_label'] = window['draw_id'].apply(lambda x: f"Draw {x}")
    window['nums_label'] = window['numbers'].apply(lambda x: ", ".join(map(str, x)))
    
    # 4. Create Plot
    if dim == 2:
        fig = px.scatter(
            window, x='x', y='y', color='draw_id',
            hover_name='draw_label', hover_data={'draw_id': False, 'nums_label': True, 'x': False, 'y': False},
            color_continuous_scale='Viridis',
            title=f"UMAP Manifold Projection — {rules.name} (Topological clusters)"
        )
    else:
        fig = px.scatter_3d(
            window, x='x', y='y', z='z', color='draw_id',
            hover_name='draw_label', hover_data={'draw_id': False, 'nums_label': True, 'x': False, 'y': False, 'z': False},
            color_continuous_scale='Viridis',
            title=f"3D UMAP Manifold Projection — {rules.name}"
        )

    fig.update_traces(marker=dict(size=5, opacity=0.8))
    fig.update_layout(coloraxis_colorbar=dict(title="Time (Draw ID)"))
    
    fig.write_html(output)
    
    console.print(f"\n[bold green]✅ Hyper-Explorer Map generated:[/bold green] [cyan]{output}[/cyan]")
    console.print("[dim]Navigate the manifold to find historical clusters and structural neighbors.[/dim]")

if __name__ == "__main__":
    hyper_explorer("br/lotofacil")
