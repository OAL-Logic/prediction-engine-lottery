"""
Spectral 3D Command 📊
=====================
Generates an interactive 3D frequency spectrum visualization using Plotly.
Maps number pool vs. frequency components vs. spectral power.
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

def spectral_3d(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyze")] = 200,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output HTML path")] = None,
) -> None:
    """📊 Generate an interactive 3D Spectral landscape of the lottery.

    Treats each number's hit history as a signal and performs FFT.
    Visualizes the entire pool's frequency domain in a 3D navigable chart.
    Identify 'Resonance Peaks' where numbers have strong periodic signatures.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    
    if output is None:
        output = f"data/spectral_3d_{lottery.replace('/', '_')}.html"
        
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws)
    
    # 1. Build Signal Matrix
    all_numbers = list(range(lo, hi + 1))
    matrix = np.zeros((n_draws, len(all_numbers)))
    for i, row in enumerate(window.itertuples()):
        for n in row.numbers:
            if lo <= n <= hi:
                matrix[i, n - lo] = 1.0
                
    # 2. Perform FFT on each column
    freq_data = []
    # FFT frequencies (standard)
    freqs = np.fft.rfftfreq(n_draws)
    
    # We'll skip the DC component (index 0)
    for idx, n in enumerate(all_numbers):
        signal = matrix[:, idx]
        # Mean center to remove DC bias
        signal = signal - np.mean(signal)
        fft_values = np.abs(np.fft.rfft(signal))
        
        for f_idx, val in enumerate(fft_values[1:]): # skip 0
            freq_data.append({
                "Number": n,
                "Frequency": freqs[f_idx + 1],
                "Magnitude": val
            })
            
    plot_df = pd.DataFrame(freq_data)
    
    # 3. Create 3D Surface/Scatter
    fig = go.Figure(data=[go.Scatter3d(
        x=plot_df['Number'],
        y=plot_df['Frequency'],
        z=plot_df['Magnitude'],
        mode='markers',
        marker=dict(
            size=4,
            color=plot_df['Magnitude'],
            colorscale='Viridis',
            opacity=0.8
        )
    )])

    fig.update_layout(
        title=f"3D Spectral Resonance Map — {rules.name} (Window: {n_draws})",
        scene=dict(
            xaxis_title='Number Pool',
            yaxis_title='Frequency (Cycles/Draw)',
            zaxis_title='Spectral Magnitude (Power)'
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    
    fig.write_html(output)
    
    console.print(f"\n[bold green]✅ 3D Spectral Map generated:[/bold green] [cyan]{output}[/cyan]")
    console.print("[dim]Open this file in your browser to interact with the probability landscape.[/dim]")

if __name__ == "__main__":
    spectral_3d("br/lotofacil")
