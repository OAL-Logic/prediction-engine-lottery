"""
Popper-Check CLI Command 🏛️⚖️
=============================
Exposes the Popperian Strategy Governance and Tier Isolation Quality Gate
directly through the canonical CLI `./p4lottery popper-check`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.modules.popperian_governance import (
    EMPIRICAL_STUDY_PATH,
    run_popperian_governance_audit,
)

console = Console()


def popper_check(
    report: Optional[str] = None,
    quiet: bool = False,
) -> None:
    """🏛️ Verify Popperian strategy tier governance and falsification invariants."""
    report_path = Path(report) if report else EMPIRICAL_STUDY_PATH

    audit_result = run_popperian_governance_audit(report_path=report_path)

    if not quiet:
        console.print(
            Panel.fit(
                f"[bold cyan]🏛️ Popperian Strategy Governance & Quality Gate[/bold cyan]\n"
                f"[dim]Enforcing ADR-0005: Strict Tier Demarcation & Null Hypothesis Audit[/dim]",
                border_style="cyan",
            )
        )

        table = Table(title="Popperian Invariant Audit Summary", box=None)
        table.add_column("Metric / Check", style="bold white")
        table.add_column("Result", justify="right")

        table.add_row("Total Strategies Audited", f"[cyan]{audit_result.total_strategies}[/cyan]")
        table.add_row("Presets Verified", f"[cyan]{audit_result.total_presets}[/cyan]")
        table.add_row("Canonical Fringe Models", f"[yellow]{audit_result.fringe_theories_checked} / 9[/yellow]")
        table.add_row("Empirical Study Report", f"[dim]{report_path.name}[/dim]")
        
        status_style = "[bold green]PASSED[/bold green]" if audit_result.passed else "[bold red]FAILED[/bold red]"
        table.add_row("Governance Verdict", status_style)
        console.print(table)

    if audit_result.violations:
        console.print("\n[bold yellow]⚠️ Governance Audit Findings:[/bold yellow]")
        v_table = Table(box=None)
        v_table.add_column("Severity", style="bold")
        v_table.add_column("Rule", style="dim")
        v_table.add_column("Strategy", style="cyan")
        v_table.add_column("Message")

        for v in audit_result.violations:
            sev_color = "red" if v.severity == "ERROR" else "yellow"
            v_table.add_row(
                f"[{sev_color}]{v.severity}[/{sev_color}]",
                v.rule,
                v.strategy or "N/A",
                v.message,
            )
        console.print(v_table)

    if not audit_result.passed:
        console.print(
            "\n[bold red]❌ Quality Gate Rejected:[/bold red] "
            "Strategy tier invariants are violated. Production presets must not contain uncertified 'fun' tier strategies."
        )
        raise SystemExit(1)
    else:
        if not quiet:
            console.print("\n[bold green]✅ Quality Gate Passed:[/bold green] All strategy tiers and Popperian invariants are fully verified.")
