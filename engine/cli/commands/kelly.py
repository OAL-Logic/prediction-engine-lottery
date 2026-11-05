"""
CLI Command: Fractional Kelly Bankroll Allocator (Track R)
==========================================================
Exposes `./p4lottery kelly` for optimal bankroll sizing under special jackpots.
"""

from __future__ import annotations

from typing import Optional
import typer
from rich.console import Console

from engine.modules.kelly_bankroll import (
    compute_fractional_kelly,
    format_kelly_report,
)

app = typer.Typer(help="Calculate optimal fractional Kelly bankroll allocation.")
console = Console()


@app.command("kelly")
def kelly_cmd(
    lottery: str = typer.Argument("br/mega-sena", help="Game slug (e.g. br/mega-sena, br/lotofacil, us/powerball)."),
    jackpot: float = typer.Option(600_000_000.0, "--jackpot", "-j", help="Estimated top prize (e.g. 600000000 for Mega da Virada)."),
    bankroll: float = typer.Option(1000.0, "--bankroll", "-b", help="Total available betting capital."),
    fraction: float = typer.Option(0.05, "--fraction", "-f", help="Safety fractional Kelly multiplier (0.01 to 0.10)."),
    subspace: str = typer.Option("anti-popular", "--subspace", "-s", help="subspace type: 'anti-popular', 'uniform', 'popular'."),
    export_md: Optional[str] = typer.Option(None, "--export-md", help="Path to export markdown summary."),
) -> None:
    """Calculate mathematically safe, ruin-free bet allocation using Fractional Kelly Criterion."""
    res = compute_fractional_kelly(
        lottery=lottery,
        jackpot=jackpot,
        bankroll=bankroll,
        fraction=fraction,
        subspace=subspace,
    )

    report_str = format_kelly_report(res)
    console.print(report_str)

    if export_md:
        from pathlib import Path
        md_content = f"# Relatório de Alocação de Banca Kelly — {res.lottery.upper()}\n\n```text\n{report_str}\n```\n"
        Path(export_md).write_text(md_content, encoding="utf-8")
        console.print(f"[green]✓ Relatório exportado para {export_md}[/green]")
