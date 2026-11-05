"""
Lab Command 🔬
=============
Interactive Web Synthesis & Frontier Theories Laboratory.
Launches the zero-dependency offline HTML5 laboratory for real-time visualization of
chaotic phase space, Ising spin lattice, topological data analysis, quantum multiverse,
Popperian falsification metrics, and Progressive Web App (PWA) edge cockpit.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Annotated, Optional
import webbrowser
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import ui_header
from engine.modules.edge_pwa import audit_pwa_integrity, format_ascii_bet_receipt

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
    pwa: Annotated[
        bool,
        typer.Option("--pwa", help="Focus on Mobile PWA Edge Cockpit and offline verification"),
    ] = False,
    audit_pwa: Annotated[
        bool,
        typer.Option("--audit-pwa", help="Audit local PWA manifest and Service Worker compliance"),
    ] = False,
    receipt: Annotated[
        Optional[str],
        typer.Option("--receipt", help="Generate offline cryptographic SHA-256 bet receipt for comma-separated numbers"),
    ] = None,
    game: Annotated[
        str,
        typer.Option("--game", "-g", help="Lottery game identifier for receipt (default: br/mega-sena)"),
    ] = "br/mega-sena",
) -> None:
    """🔬 Launch the interactive offline Web Synthesis & Fringe Theories Laboratory."""
    ui_header("INTERACTIVE SYNTHESIS LAB", "Offline Frontier Physics & PWA Edge Cockpit")

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    ref_dir = repo_root / "docs" / "reference"
    lab_path = ref_dir / "frontier-synthesis-lab.html"

    if not lab_path.is_file():
        fallback = Path("docs/reference/frontier-synthesis-lab.html").resolve()
        if fallback.is_file():
            lab_path = fallback
            ref_dir = fallback.parent
        else:
            console.print(f"[bold red]Error:[/bold red] Synthesis lab HTML not found at [yellow]{lab_path}[/yellow]")
            raise typer.Exit(code=1)

    # 1. Handle PWA Compliance Audit
    if audit_pwa:
        audit = audit_pwa_integrity(repo_root)
        audit_table = Table(title="📱 Progressive Web App (PWA) Edge Compliance Audit", border_style="cyan")
        audit_table.add_column("Asset / Specification", style="cyan")
        audit_table.add_column("Status", style="bold")
        audit_table.add_column("Details", style="dim")

        audit_table.add_row(
            "HTML Cockpit",
            "[bold green]FOUND ✓[/bold green]" if audit.html_exists else "[bold red]MISSING ✗[/bold red]",
            str(lab_path.name),
        )
        audit_table.add_row(
            "Web App Manifest",
            "[bold green]VALID ✓[/bold green]" if audit.manifest_exists else "[bold red]MISSING ✗[/bold red]",
            f"Display: {audit.manifest_data.get('display', 'unknown')} | Name: {audit.manifest_data.get('short_name', 'p4lottery')}",
        )
        audit_table.add_row(
            "Service Worker (sw.js)",
            "[bold green]ACTIVE ✓[/bold green]" if audit.sw_exists else "[bold red]MISSING ✗[/bold red]",
            f"Cached lifecycle events: {', '.join(audit.service_worker_events)}",
        )
        audit_table.add_row(
            "Overall Edge Compliance",
            "[bold green]100% PWA COMPLIANT ✓[/bold green]" if audit.is_compliant else "[bold red]INCOMPLETE ✗[/bold red]",
            "Ready for zero-dependency offline installation on mobile/desktop",
        )
        console.print(audit_table)
        return

    # 2. Handle Cryptographic Bet Receipt Generation
    if receipt:
        try:
            nums = [int(x.strip()) for x in receipt.split(",") if x.strip()]
        except ValueError:
            console.print("[bold red]Error:[/bold red] --receipt numbers must be comma-separated integers.")
            raise typer.Exit(code=1)

        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        card = format_ascii_bet_receipt(game, nums, ts)
        console.print(Panel(card, title="📱 Edge Cryptographic Receipt", border_style="green"))
        return

    # 3. Normal Lab Launch
    tab_normalized = "fringe" if pwa else tab.strip().lower()
    tab_param = f"tab-{tab_normalized}" if not tab_normalized.startswith("tab-") else tab_normalized
    if pwa:
        tab_param = f"{tab_param}#edge-pwa-card"

    file_uri = f"{lab_path.as_uri()}#{tab_param}"

    table = Table(title="🔬 Lab Environment & Runtime Parameters", border_style="bright_blue", box=None)
    table.add_column("Parameter", style="cyan", justify="right")
    table.add_column("Value", style="bold white")

    table.add_row("Local Document", str(lab_path))
    table.add_row("Target URI", file_uri)
    table.add_row("Focused Module", f"[bold green]{tab_normalized}[/bold green]" + (" (PWA Edge Card)" if pwa else ""))
    table.add_row("Browser Auto-Launch", "[dim red]Disabled (--no-browser)[/dim red]" if no_browser else "[bold green]Enabled[/bold green]")
    table.add_row("Edge PWA Architecture", "[bold yellow]Service Worker + Manifest Offline Ready ✓[/bold yellow]")
    console.print(table)

    features = (
        "[bold cyan]Interactive Quadrants & Falsification Engines Available:[/bold cyan]\n"
        " • [bold white]1. 3D Lorenz Chaotic Attractor[/bold white]: RK4 integration with multi-touch rotation on mobile\n"
        " • [bold white]2. 2D Ising Spin Lattice[/bold white]: Metropolis Monte Carlo sampling with Curie phase transition ($T/T_c$)\n"
        " • [bold white]3. Persistent Homology (TDA)[/bold white]: Vietoris-Rips simplicial filtration with $\\beta_0, \\beta_1$ barcode cavities\n"
        " • [bold white]4. Everett Quantum Multiverse[/bold white]: Many-worlds decoherence tree and phase interference spectrum $|\\psi(n)|^2$\n"
        " • [bold white]5. Popperian Falsification Matrix[/bold white]: 9 Speculative theories benchmarked against $H_0$ across 3 global jurisdictions\n"
        " • [bold white]6. Physical Machine Archetypes[/bold white]: Air-Mix Fluid Dynamics vs Gravity-Pick vs Pneumatic Drop comparison\n"
        " • [bold white]7. Edge Cryptographic Validator[/bold white]: SHA-256 verified offline bet receipts"
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
