"""
Synergy Graph Command 🕸️
=========================
Generates an interactive network graph of numerical co-occurrences.
Uses NetworkX for topology and Plotly for visualization.
"""

from __future__ import annotations

import os
from typing import Annotated, Optional
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import typer
from rich.console import Console

from engine.cli.utils import get_adapter

console = Console()

def synergy_graph(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of historical draws to analyze")] = 300,
    threshold: Annotated[float, typer.Option("--threshold", "-t", help="Minimum co-occurrence lift to show edge")] = 1.2,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
) -> None:
    """🕸️ Map the 'Clique Structure' of the lottery number pool.

    Treats each number as a node and co-occurrences as edges.
    Calculates 'Lift' (actual vs expected co-occurrence).
    Visualizes the resulting graph to find tight-knit numerical families.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    all_numbers = list(range(lo, hi + 1))
    
    if output is None:
        output = f"data/synergy_graph_{lottery.replace('/', '_')}.html"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws)
    
    # 1. Build Co-occurrence Matrix
    counts = {n: 0 for n in all_numbers}
    co_occur = {n: {m: 0 for m in all_numbers} for n in all_numbers}
    
    for row in window.itertuples():
        nums = row.numbers
        for n in nums:
            if n in counts: counts[n] += 1
            for m in nums:
                if n != m and n in co_occur and m in co_occur[n]:
                    co_occur[n][m] += 1
                    
    # 2. Build NetworkX Graph
    G = nx.Graph()
    G.add_nodes_from(all_numbers)
    
    for n in all_numbers:
        for m in all_numbers:
            if n >= m: continue
            
            actual = co_occur[n][m]
            # Expected co-occurrence if independent
            # P(n and m) = P(n) * P(m)
            p_n = counts[n] / n_draws
            p_m = counts[m] / n_draws
            expected = p_n * p_m * n_draws
            
            if expected > 0:
                lift = actual / expected
                if lift >= threshold and actual > 1:
                    G.add_edge(n, m, weight=lift, actual=actual)
                    
    # 3. Graph Layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # 4. Prepare Plotly Visualization
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0); edge_x.append(x1); edge_x.append(None)
        edge_y.append(y0); edge_y.append(y1); edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        deg = G.degree(node)
        node_text.append(f'Number {node}<br>Synergies: {deg}')
        node_color.append(deg)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[str(n) for n in G.nodes()],
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=15,
            color=node_color,
            colorbar=dict(
                thickness=15,
                title='Network Degree',
                xpad=0
            ),
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=f'Numerical Synergy Network — {rules.name} (Lift > {threshold})',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    
    fig.write_html(output)
    
    console.print(f"\n[bold green]✅ Synergy Graph generated:[/bold green] [cyan]{output}[/cyan]")
    console.print("[dim]Nodes are numbers, edges represent strong co-occurrence 'families'.[/dim]")

if __name__ == "__main__":
    synergy_graph("br/lotofacil")
