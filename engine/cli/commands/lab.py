"""
Lab Command 🔬
=============
Interactive Web Synthesis & Frontier Theories Laboratory.
Launches the zero-dependency offline HTML5 laboratory for real-time visualization of
chaotic phase space, Ising spin lattice, topological data analysis, quantum multiverse,
and Popperian falsification metrics.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Optional
import webbrowser
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import ui_header

console = Console()


def lab(
    tab: Annotated[
        str,
        typer.Option("--tab", "-t", help="Initial tab to focus: fringe | orbital | wheels | followers | kuramoto | poincare | rmt"),
    ] = "fringe",
    no_browser: Annotated[
        bool,
        typer.Option("--no-browser", "-n", help="Do not launch system web browser automatically; print local path only"),
    ] = False,
    host: Annotated[
        bool,
        typer.Option("--host", help="Print instructions for local HTTP hosting"),
    ] = False,
) -> None:
    """🔬 Launch the interactive offline Web Synthesis & Fringe Theories Laboratory."""
    ui_header("INTERACTIVE SYNTHESIS LAB", "Offline Frontier Physics & Popperian Falsification")

    # Locate docs/reference/frontier-synthesis-lab.html relative to engine or repo root
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    lab_path = repo_root / "docs" / "reference" / "frontier-synthesis-lab.html"

    if not lab_path.is_file():
        # Fallback search if installed as package
        fallback = Path("docs/reference/frontier-synthesis-lab.html").resolve()
        if fallback.is_file():
            lab_path = fallback
        else:
            console.print(f"[bold red]Error:[/bold red] Synthesis lab HTML not found at [yellow]{lab_path}[/yellow]")
            raise typer.Exit(code=1)

    tab_normalized = tab.strip().lower()
    if not tab_normalized.startswith("tab-"):
        tab_param = f"tab-{tab_normalized}"
    else:
        tab_param = tab_normalized

    file_uri = f"{lab_path.as_uri()}#{tab_param}"

    table = Table(title="🔬 Lab Environment & Runtime Parameters", border_style="bright_blue", box=None)
    table.add_column("Parameter", style="cyan", justify="right")
    table.add_column("Value", style="bold white")

    table.add_row("Local Document", str(lab_path))
    table.add_row("Target URI", file_uri)
    table.add_row("Focused Module", f"[bold green]{tab_normalized}[/bold green]")
    table.add_row("Browser Auto-Launch", "[dim red]Disabled (--no-browser)[/dim red]" if no_browser else "[bold green]Enabled[/bold green]")
    table.add_row("Dependencies", "[bold yellow]100% Offline Zero-Dependency (Vanilla Canvas / SVG / JS)[/bold yellow]")
    console.print(table)

    features = (
        "[bold cyan]Interactive Quadrants & Falsification Engines Available:[/bold cyan]\n"
        " • [bold white]1. 3D Lorenz Chaotic Attractor[/bold white]: RK4 integration of convective Rayleigh-Bénard roll instability\n"
        " • [bold white]2. 2D Ising Spin Lattice[/bold white]: Metropolis Monte Carlo sampling with Curie phase transition ($T/T_c$)\n"
        " • [bold white]3. Persistent Homology (TDA)[/bold white]: Vietoris-Rips simplicial filtration with $\\beta_0, \\beta_1$ barcode cavities\n"
        " • [bold white]4. Everett Quantum Multiverse[/bold white]: Many-worlds decoherence tree and phase interference spectrum $|\\psi(n)|^2$\n"
        " • [bold white]5. Popperian Falsification Matrix[/bold white]: 9 Speculative theories benchmarked against $H_0$ across 3 global jurisdictions\n"
        " • [bold white]6. Physical Machine Archetypes[/bold white]: Air-Mix Fluid Dynamics vs Gravity-Pick vs Pneumatic Drop comparison"
    )
    console.print(Panel(features, title="🔬 Lab Capabilities", border_style="cyan"))

    if not no_browser:
        console.print(f"\n[bold green]Opening interactive lab in your default web browser...[/bold green]")
        try:
            opened = webbrowser.open_new_tab(file_uri)
            if not opened:
                console.print("[yellow]Webbrowser open returned false (headless environment). Please open manually:[/yellow]")
                console.print(f"[bold underline cyan]{file_uri}[/bold underline cyan]")
        except Exception as exc:
            console.print(f"[yellow]Could not open browser automatically ({exc}). Access via:[/yellow]")
            console.print(f"[bold underline cyan]{file_uri}[/bold underline cyan]")
    else:
        console.print(f"\n[dim]To view, open in browser:[/dim] [bold cyan]{file_uri}[/bold cyan]")

    if host:
        console.print("\n[bold dim]To serve over local HTTP (e.g. for remote browser/tablet testing):[/bold dim]")
        console.print(f"  cd '{repo_root}' && python3 -m http.server 8080")
        console.print(f"  URL: http://localhost:8080/docs/reference/frontier-synthesis-lab.html#{tab_param}")

    console.print("\n[bold green]✓ Synthesis Lab Ready.[/bold green]")
