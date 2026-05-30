"""
Board Command 🗺️
==============
Advanced board analytics and grid-based visualizations.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
# import pandas as pd # Moved inside
from rich.console import Console, Group
from rich.table import Table
from rich.columns import Columns

from rich.markup import escape

from engine.cli.utils import get_adapter
from engine.modules import sum_range, correlation
from engine.modules.geometry import BoardGeometry

console = Console()

def board(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    view: Annotated[str, typer.Option("--view", "-v", help="heatmap | balance | halves | rows | cluster | positional")] = "heatmap",
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Use only the N most recent draws")] = 20,
    numbers: Annotated[Optional[str], typer.Option("--numbers", "-n", help="Mark these numbers on the board (e.g. '1 13 32')")] = None,
    cols:    Annotated[Optional[int], typer.Option("--cols", "-C", help="Override number of columns in the grid")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append board analytics report to this .md file")] = None,
) -> None:
    """🗺️ Advanced Board Analytics showing Pattern Coverage, Balance, Clusters, Voids, Halves, and Row-of-10."""
    import pandas as pd
    adapter = get_adapter(lottery)
    df_full = adapter.fetch()
    df_tail = df_full.tail(limit)
    rules = adapter.rules
    lo, hi = rules.number_range
    total_range = list(range(lo, hi + 1))

    # Grid configuration
    grid_cols = cols or rules.board_cols or 10

    # Parse marked numbers
    marked = set()
    if numbers:
        try:
            marked = set(int(n) for n in numbers.replace(",", " ").split())
        except ValueError:
            console.print("[yellow]⚠ Warning: Could not parse --numbers. Use space or comma separation.[/yellow]")

    console.rule(f"[bold cyan]Advanced Analytics: {rules.name} ({view.upper()})[/bold cyan]")

    if view == "balance":
        _render_balance_view(df_tail, lo, hi)
    elif view == "heatmap":
        _render_heatmap_view(df_full, total_range, grid_cols, rules)
    elif view == "halves":
        _render_halves_view(df_tail, rules)
    elif view == "rows":
        _render_rows_view(df_tail, grid_cols, rules)
    elif view == "cluster":
        _render_cluster_view(df_tail, rules)
    elif view == "positional":
        _render_positional_heatmap_view(df_tail, rules)
    elif view == "sacred":
        target_numbers = marked if marked else set(df_tail.iloc[-1]["numbers"])
        _render_sacred_view(target_numbers, grid_cols, rules)
    else:
        console.print(f"[yellow]⚠ View '{view}' is currently being modularized or is not supported.[/yellow]")

    if export_md:
        flat = [n for nums in df_full["numbers"] for n in nums]
        counts = Counter(flat)
        pool_sz = hi - lo + 1
        _append_md_board(export_md, lottery, rules.name, view, len(df_full), limit, counts, pool_sz)
        console.print(f"[green]✔ Board report appended to {export_md}[/green]")

def _render_balance_view(df_tail, lo, hi):
    table = Table(title="Recent Draw Balance", box=None, padding=(0, 2))
    table.add_column("Draw", justify="right", style="dim")
    table.add_column("Numbers", style="bold green", min_width=30)
    table.add_column("Odd/Even", justify="center")
    table.add_column("High/Low", justify="center")
    table.add_column("Sum", justify="right")
    
    mid = (lo + hi) / 2
    for _, row in df_tail.iterrows():
        nums = row["numbers"]
        odds = sum(1 for n in nums if n % 2 != 0)
        evens = len(nums) - odds
        highs = sum(1 for n in nums if n > mid)
        lows = len(nums) - highs
        s = sum(nums)
        
        table.add_row(
            str(row["draw_id"]),
            escape(str([int(n) for n in sorted(nums)])),
            f"{odds:2d} / {evens:2d}",
            f"{highs:2d} / {lows:2d}",
            str(s)
        )
    console.print(table)

def _append_md_board(
    path: str, lottery: str, game_name: str, view: str,
    total_draws: int, limit: int, counts: Counter, pool_sz: int,
) -> None:
    today = _date.today().isoformat()
    sorted_nums = sorted(counts.keys(), key=lambda n: counts[n], reverse=True)
    top5 = sorted_nums[:5]
    bot5 = sorted_nums[-5:]
    top_rows = "".join(f"| {n} | {counts[n]} |\n" for n in top5)
    bot_rows = "".join(f"| {n} | {counts[n]} |\n" for n in bot5)

    content = f"""
---
type: diagnostic
subtype: board
date: {today}
game: {lottery}
game_name: {game_name}
view: {view}
total_draws: {total_draws}
limit: {limit}
pool_size: {pool_sz}
tags: [prediction-engine, board, heatmap, pattern-log]
---

## Board Analytics: {game_name} ({today})

**View:** {view}  ·  **Draws used:** {total_draws}  ·  **Pool size:** {pool_sz}

### Top 5 Hottest Numbers

| Number | Count |
|--------|-------|
{top_rows}
### Top 5 Coldest Numbers

| Number | Count |
|--------|-------|
{bot_rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)


def _render_heatmap_view(df_full, total_range, cols, rules):
    flat = [n for nums in df_full["numbers"] for n in nums]
    counts = Counter(flat)
    max_c = max(counts.values()) if counts else 1
    
    rows = math.ceil(len(total_range) / cols)
    table = Table(title=f"Board Frequency Heatmap: {rules.name}", box=None, padding=(0, 1))
    for _ in range(cols):
        table.add_column(justify="center")
        
    for r_idx in range(rows):
        row_data = []
        for c_idx in range(cols):
            idx = r_idx * cols + c_idx
            if idx < len(total_range):
                n = total_range[idx]
                c = counts.get(n, 0)
                ratio = c / max_c
                color = "dim"
                if ratio > 0.9: color = "bold red"
                elif ratio > 0.7: color = "bold yellow"
                elif ratio > 0.5: color = "green"
                elif ratio > 0.3: color = "blue"
                elif ratio > 0.1: color = "cyan"
                row_data.append(f"[{color}]{n:2}[/{color}]")
            else:
                row_data.append("")
        table.add_row(*row_data)
    console.print(table)


def _render_halves_view(df_tail, rules):
    """Analyze Upper vs Lower half distribution."""
    lo, hi = rules.number_range
    mid = (lo + hi) / 2
    table = Table(title="Positional Halves Analysis (Upper/Lower)", box=None)
    table.add_column("Draw", justify="right", style="dim")
    table.add_column("Distribution (Lower | Upper)", justify="center", width=40)
    table.add_column("Ratio (L:U)", justify="right")

    for _, row in df_tail.iterrows():
        nums = row["numbers"]
        lower = [n for n in nums if n <= mid]
        upper = [n for n in nums if n > mid]
        l_cnt, u_cnt = len(lower), len(upper)
        
        # Visual bar
        total = l_cnt + u_cnt
        l_bar = "█" * int(l_cnt / total * 30)
        u_bar = "▒" * int(u_cnt / total * 30)
        
        table.add_row(
            str(row["draw_id"]),
            f"[cyan]{l_bar}[/cyan]|[magenta]{u_bar}[/magenta]",
            f"{l_cnt}:{u_cnt}"
        )
    console.print(table)


def _render_rows_view(df_tail, cols, rules):
    """Analyze horizontal row distribution (Row-of-10)."""
    table = Table(title=f"Horizontal Row Distribution ({cols} cols)", box=None)
    table.add_column("Draw", justify="right", style="dim")
    
    n_rows = math.ceil((rules.number_range[1] - rules.number_range[0] + 1) / cols)
    for r in range(n_rows):
        table.add_column(f"R{r+1}", justify="center")

    for _, row in df_tail.iterrows():
        nums = row["numbers"]
        row_counts = Counter()
        for n in nums:
            r_idx = (n - rules.number_range[0]) // cols
            row_counts[r_idx] += 1
            
        row_data = [str(row["draw_id"])]
        for r in range(n_rows):
            cnt = row_counts[r]
            color = "bold green" if cnt >= 3 else "dim" if cnt == 0 else "white"
            row_data.append(f"[{color}]{cnt}[/{color}]")
        table.add_row(*row_data)
    console.print(table)


def _render_cluster_view(df_tail, rules):
    """Analyze Frequent Triplets and Pair Lift."""
    from engine.modules import correlation
    res = correlation.analyze(df_tail, rules, top_n=10)
    
    # Triplets
    trip_table = Table(title="Top Triplets (Most Frequent in Window)", box=None, padding=(0, 2))
    trip_table.add_column("Triplet", style="bold yellow")
    trip_table.add_column("Count", justify="right")
    
    for n1, n2, n3, count in res.top_triplets:
        if count >= 2:
            trip_table.add_row(f"{n1}, {n2}, {n3}", str(count))
            
    # Associated Pairs
    pair_table = Table(title="Associated Pairs (Highest Lift)", box=None, padding=(0, 2))
    pair_table.add_column("Pair", style="bold cyan")
    pair_table.add_column("Lift", justify="right")
    
    for n1, n2, lift in res.top_pairs:
        if lift > 1.2:
            pair_table.add_row(f"{n1} & {n2}", f"{lift:.2f}")

    console.print(Columns([trip_table, pair_table]))
    console.print("\n[dim]Surfacing complex correlations beyond simple frequency.[/dim]")


def _render_positional_heatmap_view(df_tail, rules):
    """Analyze exact slot frequencies (Positional Heatmap)."""
    pick = rules.pick_count
    table = Table(title=f"Positional Slot Frequencies: {rules.name}", box=None)
    table.add_column("Slot", style="bold yellow")
    table.add_column("Mean", justify="right")
    table.add_column("StdDev", justify="right", style="dim")
    table.add_column("Recent Trend (Last 10)", justify="center")

    import numpy as np
    slot_data = [[] for _ in range(pick)]
    for _, row in df_tail.iterrows():
        nums = sorted(row["numbers"])
        for i in range(min(pick, len(nums))):
            slot_data[i].append(nums[i])

    for i in range(pick):
        data = slot_data[i]
        if not data: continue
        mean = np.mean(data)
        std = np.std(data)
        
        # Trend (sparkline)
        from engine.cli.utils import sparkline
        trend = sparkline([float(x) for x in data[-10:]], width=10)
        
        table.add_row(
            f"Pos {i+1}",
            f"{mean:.1f}",
            f"{std:.1f}",
            trend
        )
    console.print(table)
    console.print("\n[dim]Exposing positional machines biases and sorting regularities.[/dim]")


def _render_sacred_view(marked_nums: set[int], cols: int, rules: DrawRules):
    """
    Renders a physical 2D grid of the board with Center of Mass overlay,
    and a symmetry analytics side-panel.
    """
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from engine.modules.geometry import calculate_symmetry_metrics, get_manifold_coords
    from engine.modules.environment import EnvironmentalService
    
    lo, hi = rules.number_range
    total_range = list(range(lo, hi + 1))
    rows = math.ceil(len(total_range) / cols)
    
    # 1. Calculate symmetry metrics
    metrics = calculate_symmetry_metrics(list(marked_nums), rules, "sphere")
    cm_x, cm_y, cm_z = metrics["center_of_mass"]
    resonance = metrics["resonance"]
    ref_h = metrics["reflection_h"]
    ref_v = metrics["reflection_v"]
    grade = metrics["symmetry_grade"]
    
    # Map Center of Mass (3D sphere projection) back to 2D row/col coordinates for visual overlay
    grid_center_x = (cols - 1) / 2.0
    grid_center_y = (rows - 1) / 2.0
    
    # Map sphere X/Y coordinates onto the grid space
    overlay_col = int(round(grid_center_x + cm_x * grid_center_x))
    overlay_row = int(round(grid_center_y + cm_y * grid_center_y))
    
    # Boundaries clamping
    overlay_col = max(0, min(cols - 1, overlay_col))
    overlay_row = max(0, min(rows - 1, overlay_row))
    
    # 2. Build physical ASCII grid
    grid_table = Table(title="🌀 PHYSICAL SACRED MANIFOLD GRID", show_header=False, box=None, padding=(0, 1))
    for _ in range(cols):
        grid_table.add_column(justify="center")
        
    for r_idx in range(rows):
        row_data = []
        for c_idx in range(cols):
            idx = r_idx * cols + c_idx
            if idx < len(total_range):
                n = total_range[idx]
                
                # Check if it's the Center of Mass overlay cell
                is_cm = (r_idx == overlay_row and c_idx == overlay_col)
                
                if n in marked_nums:
                    symbol = "●"
                    color = "bold magenta"
                    if is_cm:
                        symbol = "❂"
                        color = "bold yellow"
                    row_data.append(f"[{color}]{symbol} {n:02d}[/{color}]")
                else:
                    symbol = "◌"
                    color = "dim"
                    if is_cm:
                        symbol = "x"
                        color = "bold yellow"
                    row_data.append(f"[{color}]{symbol} {n:02d}[/{color}]")
            else:
                row_data.append("")
        grid_table.add_row(*row_data)
        
    # 3. Build Celestial and Symmetry Analytics Card
    try:
        env = EnvironmentalService()
        jitter = env.get_jitter()
        kp = jitter.get("kp", 3.0)
        seismic = jitter.get("seismic_mag", 0.0)
    except Exception:
        kp = 3.0
        seismic = 0.0
        
    # Derive planetary transits representation
    from datetime import datetime
    now = datetime.now()
    hour_fraction = (now.hour * 3600 + now.minute * 60 + now.second) / 86400.0
    transit_angle = (hour_fraction * 360.0 + kp * 20.0) % 360.0
    
    # Quality status
    grade_status = "Gold Balance" if grade > 75.0 else "Silver Balance" if grade > 50.0 else "Standard Scatter"
    grade_color = "gold1" if grade > 75.0 else "cyan" if grade > 50.0 else "dim"
    
    analytics_text = Text.from_markup(
        f"[bold yellow]🌌 COSMIC TRANSITS LOG[/bold yellow]\n"
        f"  [dim]Celestial Angle :[/dim] [yellow]{transit_angle:.2f}°[/yellow]\n"
        f"  [dim]Space Weather   :[/dim] Solar Kp {kp:.1f} | Seismic {seismic:.1f}M\n"
        f"  [dim]Geo-Manifold    :[/dim] Sphere (EAA Projection)\n\n"
        f"[bold green]📐 SYMMETRY METRICS[/bold green]\n"
        f"  [dim]Vector Balance  :[/dim] {resonance*100.0:.1f}%\n"
        f"  [dim]Mirror Vertical :[/dim] {ref_v*100.0:.1f}%\n"
        f"  [dim]Mirror Horiz.   :[/dim] {ref_h*100.0:.1f}%\n"
        f"  [dim]Center of Mass  :[/dim] X={cm_x:+.2f}, Y={cm_y:+.2f}, Z={cm_z:+.2f}\n\n"
        f"🏆 [bold]Resonance Grade:[/bold] [bold {grade_color}]{grade:.1f}% ({grade_status})[/bold {grade_color}]"
    )
    
    analytics_panel = Panel(analytics_text, title="🔬 NON-EUCLIDEAN SYMMETRY REPORT", border_style="green", expand=False)
    grid_panel = Panel(grid_table, border_style="bright_black", expand=False)
    
    console.print(Columns([grid_panel, analytics_panel], equal=True))

