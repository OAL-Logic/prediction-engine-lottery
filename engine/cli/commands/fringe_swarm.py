"""
Fringe Swarm Command 🐝
======================
Autonomous multi-modal candidate polling, consensus disagreement computation (D_fringe),
and dynamic counter-hedging across all 9 speculative physics models and orthodox filters.
"""

from __future__ import annotations

from typing import Annotated, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import ui_header
from engine.modules.fringe_swarm import (
    run_fringe_swarm_telemetry,
    export_swarm_report_md,
)

console = Console()


def fringe_swarm(
    lottery: Annotated[
        str,
        typer.Argument(help="Lottery game identifier (e.g. br/mega-sena, br/quina, br/lotofacil)"),
    ] = "br/mega-sena",
    draws: Annotated[
        int,
        typer.Option("--draws", "-n", help="Historical window of draws to analyze"),
    ] = 100,
    tickets: Annotated[
        int,
        typer.Option("--tickets", "-k", help="Total tickets to emit (Core + Hedged)"),
    ] = 5,
    hedge_ratio: Annotated[
        float,
        typer.Option("--hedge-ratio", "-r", help="Proportion of tickets allocated to divergence counter-hedging"),
    ] = 0.4,
    export_md: Annotated[
        Optional[str],
        typer.Option("--export-md", help="Export markdown telemetry report path"),
    ] = "reports/br/studies/fringe-theories-swarm-telemetry.md",
    emit: Annotated[
        bool,
        typer.Option("--emit", help="Emit live UDP telemetry pulse to local gateway"),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress detailed console tables"),
    ] = False,
    seed: Annotated[
        int,
        typer.Option("--seed", "-s", help="Random seed for ticket reproducibility"),
    ] = 42,
) -> None:
    """🐝 Autonomous multi-modal candidate polling and dynamic counter-hedging for fringe models."""
    if not quiet:
        ui_header("FRINGE SWARM & TELEMETRY", f"{lottery.upper()} · D_fringe Consensus & Hedging")

    with console.status("[bold cyan]Polling 9 Fringe Models & Orthodox Baseline Ensemble...[/bold cyan]"):
        report = run_fringe_swarm_telemetry(
            lottery=lottery,
            draws_window=draws,
            num_tickets=tickets,
            hedge_ratio=hedge_ratio,
            emit_telemetry=emit,
            seed=seed,
        )

    # 1. Summary Metrics Table
    summary_table = Table(title="🐝 Swarm Telemetry & Epistemic Friction", border_style="bright_blue", box=None)
    summary_table.add_column("Telemetry Metric", style="cyan", justify="right")
    summary_table.add_column("Observed Value", style="bold white")

    summary_table.add_row("Lottery Target", report.lottery)
    summary_table.add_row("Draws Analyzed", str(report.draws_analyzed))
    summary_table.add_row("Fringe Strategies Voted", f"{report.total_fringe_strategies} / 9 (Tier: fun)")
    summary_table.add_row("Orthodox Baselines Voted", f"{report.total_orthodox_strategies} (Tier: core)")
    summary_table.add_row(
        "Consensus Disagreement Index (D_fringe)",
        f"[bold yellow]{report.disagreement_index:.4f}[/bold yellow] (Jensen-Shannon Divergence)",
    )
    summary_table.add_row("Epistemic Regime", f"[bold green]{report.epistemic_regime}[/bold green]")
    summary_table.add_row("Top Consensus Dezenas", " ".join(f"{n:02d}" for n in report.consensus_numbers[:8]))
    summary_table.add_row("Fringe-Exclusive Singularity", " ".join(f"{n:02d}" for n in report.fringe_exclusive_numbers[:6]))
    summary_table.add_row("Orthodox-Exclusive Anchors", " ".join(f"{n:02d}" for n in report.orthodox_exclusive_numbers[:6]))

    if not quiet:
        console.print(summary_table)

    # 2. Tickets Table
    ticket_table = Table(title=f"🎯 Dynamically Hedged Tickets ({tickets} Total)", border_style="magenta")
    ticket_table.add_column("#", style="dim", justify="right")
    ticket_table.add_column("Role / Archetype", style="bold cyan")
    ticket_table.add_column("Selected Numbers", style="bold green")

    for i, t in enumerate(report.core_tickets):
        ticket_table.add_row(f"{i+1}", "Core Consensus", " ".join(f"{n:02d}" for n in t))

    for i, t in enumerate(report.hedged_tickets):
        ticket_table.add_row(f"{len(report.core_tickets) + i + 1}", "[bold yellow]Counter-Hedge[/bold yellow]", " ".join(f"{n:02d}" for n in t))

    if not quiet:
        console.print(ticket_table)

    # 3. Export Report if specified
    if export_md:
        out_path = export_swarm_report_md(report, export_md)
        if not quiet:
            console.print(f"\n[bold green]✓ Swarm Telemetry Report Exported:[/bold green] [cyan]{out_path}[/cyan]")
