"""
Fractal Scan Command 🌀
======================
Calculates the fractal dimension (Box-Counting) of winning patterns on the grid.
"""

from __future__ import annotations

import numpy as np
import math
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

def calculate_box_dimension(numbers: list[int], width: int) -> float:
    """
    Measure fractal dimension of a winning pattern on a square number grid.
    Uses box-counting method with scales of 1, 2, and 4.
    """
    positions = [((n - 1) % width, (n - 1) // width) for n in numbers]
    
    counts = []
    scales = [1, 2, 4]  # box sizes
    
    for box_size in scales:
        boxes = set()
        for x, y in positions:
            boxes.add((x // box_size, y // box_size))
        counts.append(len(boxes))
        
    # If all counts are same or zero, it's effectively 2D (uniform) or 0D (empty)
    if len(set(counts)) <= 1 or counts[0] == 0:
        return 2.0
        
    log_scales = np.log(1.0 / np.array(scales))
    log_counts = np.log(counts)
    
    # D = log(N) / log(1/scale)
    # The slope of log(N) vs log(1/scale) is the dimension
    slope, _ = np.polyfit(log_scales, log_counts, 1)
    return abs(float(slope))

def fractal_scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena)")],
    draws: Annotated[int, typer.Option("--draws", "-n", help="Number of recent draws to analyze")] = 30,
) -> None:
    """🌀 Analyze spatial fractal dimension of historical draws.

    Detects 'clustering' on the physical board. 
    Low dimension (< 1.5) indicates highly clustered 'fractal' draws.
    High dimension (~ 2.0) indicates uniform distribution.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    
    width = rules.board_cols or 10
    
    n_draws = min(draws, len(df))
    window = df.tail(n_draws)
    
    if window.empty:
        console.print("[red]No data available.[/red]")
        return
        
    results = []
    for row in window.itertuples():
        d = calculate_box_dimension(row.numbers, width)
        results.append((row.draw_id, d))
        
    # Stats
    dims = [r[1] for r in results]
    avg_dim = np.mean(dims)
    std_dim = np.std(dims)
    
    console.rule(f"[bold cyan]🌀 FRACTAL SPATIAL SCAN — {rules.name}[/bold cyan]")
    
    table = Table(title=f"Fractal Dimension (D) — Last {n_draws} Draws", box=None)
    table.add_column("Draw ID", style="dim")
    table.add_column("Dimension (D)", justify="right")
    table.add_column("Verdict", style="bold")
    
    for draw_id, d in results[-15:]: # Show last 15
        if d < 1.4:
            verdict = "[red]Highly Clustered[/red]"
        elif d < 1.7:
            verdict = "[yellow]Moderate Clumping[/yellow]"
        else:
            verdict = "[green]Uniform Spread[/green]"
        table.add_row(str(draw_id), f"{d:.3f}", verdict)
        
    console.print(table)
    
    # Summary
    summary = (
        f"Mean Fractal Dimension: [bold]{avg_dim:.3f}[/bold] (±{std_dim:.3f})\n\n"
        "• [bold cyan]D ≈ 2.0[/bold cyan]: Numbers are spread evenly (standard entropy).\n"
        "• [bold yellow]D < 1.6[/bold yellow]: Spatial patterns are emerging. Consider 'spatial' strategy.\n"
        "• [bold red]D < 1.3[/bold red]: Extreme fractal clustering detected. Machine bias likely."
    )
    
    console.print(Panel(summary, title="Diagnostic Summary", border_style="cyan"))

if __name__ == "__main__":
    fractal_scan("br/mega-sena", draws=10)
