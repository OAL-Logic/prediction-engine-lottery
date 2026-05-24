"""
Space Weather Command ☀️
========================
Fetches real-time geomagnetic and solar activity data from NOAA.
Updates the local solar cache and adjusts the Global Jitter regime.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Annotated, Optional

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# NOAA SWPC APIs (No key required)
KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
SOLAR_WIND_URL = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"

def fetch_space_weather() -> dict:
    """Fetch live data from NOAA."""
    results = {}
    
    with httpx.Client(timeout=10.0) as client:
        # 1. K-Index
        try:
            resp = client.get(KP_URL)
            data = resp.json()
            # data[0] is header: ["time_tag", "kp", "a_index", "station_count"]
            # Get the latest row
            latest = data[-1]
            results["kp"] = float(latest[1])
            results["kp_time"] = latest[0]
        except Exception as e:
            results["kp_error"] = str(e)
            
        # 2. Solar Wind
        try:
            resp = client.get(SOLAR_WIND_URL)
            data = resp.json()
            # {"WindSpeed": 450.5}
            results["solar_wind"] = data.get("WindSpeed", 0.0)
        except Exception as e:
            results["solar_wind_error"] = str(e)
            
    return results

def space_weather(
    update_cache: Annotated[bool, typer.Option("--update/--no-update", help="Update the data/solar_k_index.json cache")] = True,
) -> None:
    """☀️ Monitor live Geomagnetic and Solar activity.

    Fetches current Planetary K-index (Kp) and Solar Wind speed.
    Correlates solar storms with increased numerical volatility.
    Updates the local cache used by the 'geomagnetic' and 'noosphere' strategies.
    """
    with console.status("[bold yellow]Contacting NOAA Space Weather Prediction Center..."):
        data = fetch_space_weather()
        
    kp = data.get("kp", 0.0)
    wind = data.get("solar_wind", 0.0)
    
    # Verdict
    if kp < 2:
        regime = "[green]QUIET (Static Mode)[/green]"
        jitter_boost = 0.0
    elif kp < 4:
        regime = "[yellow]UNSETTLED (Normal Mode)[/yellow]"
        jitter_boost = 0.2
    elif kp < 6:
        regime = "[orange3]ACTIVE (Entropy Boost)[/orange3]"
        jitter_boost = 0.5
    else:
        regime = "[red]STORM (Maximum Jitter)[/red]"
        jitter_boost = 1.0
        
    console.rule("[bold cyan]☀️ REAL-TIME SPACE WEATHER RESONANCE[/bold cyan]")
    
    table = Table(box=None)
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="cyan")
    table.add_column("Implication", style="dim")
    
    table.add_row("Planetary K-index (Kp)", f"{kp:.2f}", "Geomagnetic stability")
    table.add_row("Solar Wind Speed", f"{wind:.1f} km/s", "Plasma pressure")
    table.add_row("Regime", regime, "Recommended Jitter Level")
    
    console.print(table)
    
    if update_cache:
        cache_path = "data/solar_k_index.json"
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            # Read existing
            if os.path.exists(cache_path):
                with open(cache_path, "r") as f:
                    cache_data = json.load(f)
            else:
                cache_data = {}
            
            # Update today's entry
            cache_data[current_date] = kp
            
            with open(cache_path, "w") as f:
                json.dump(cache_data, f, indent=2)
            console.print(f"\n[bold green]✓[/][dim] Cache updated: {cache_path}[/dim]")
        except Exception as e:
            console.print(f"\n[red]Failed to update cache: {e}[/red]")

    summary = (
        f"Current Solar Jitter: [bold cyan]+{jitter_boost:.2f}[/bold cyan]\n\n"
        "Strategies [white]geomagnetic[/], [white]solar[/], and [white]noosphere[/] "
        "will automatically modulate their sampling chaos based on this live pulse."
    )
    console.print(Panel(summary, title="Space Weather Verdict", border_style="yellow"))

if __name__ == "__main__":
    space_weather()
