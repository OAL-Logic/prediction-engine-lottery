"""
Entropy-Bench CLI Command ⚛️🔌
==============================
Benchmarks hardware entropy sources (PRNG, CSPRNG, HWRNG, Quantum Cache)
against NIST SP 800-22 randomness tests and audits real lottery globes
against true quantum entropy.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter
from engine.modules.hardware_entropy import (
    audit_lottery_vs_quantum,
    export_quantum_entropy_report,
)

console = Console()


def entropy_bench(
    lottery: str = "br/mega-sena",
    bytes_bench: int = 16384,
    export_md: Optional[str] = "reports/br/studies/fringe-theories-quantum-entropy-benchmarks.md",
    quiet: bool = False,
) -> None:
    """⚛️ Benchmark hardware & quantum entropy sources against NIST tests and lottery draws."""
    adapter = get_adapter(lottery)
    df = adapter.fetch()

    if not quiet:
        console.print(
            Panel.fit(
                f"[bold cyan]⚛️ Hardware & Quantum Entropy (QRNG) Benchmark[/bold cyan]\n"
                f"[dim]Game: [bold white]{lottery}[/bold white] | Draws: [bold white]{len(df)}[/bold white] | Sample: [bold white]{bytes_bench:,} bytes[/bold white][/dim]",
                border_style="cyan",
            )
        )

    with console.status("[bold green]Harvesting multi-source physical entropy and running NIST tests..."):
        audit = audit_lottery_vs_quantum(
            df=df,
            rules=adapter.rules,
            lottery_name=lottery,
            n_benchmark_bytes=bytes_bench,
        )

    if not quiet:
        table = Table(title="NIST SP 800-22 Entropy Source Benchmark", box=None)
        table.add_column("Source", style="bold white")
        table.add_column("Shannon Entropy", justify="right")
        table.add_column("Monobit p-val", justify="right")
        table.add_column("Runs p-val", justify="right")
        table.add_column("Lag-1 Autocorr", justify="right")
        table.add_column("Status", justify="center")

        for name, ev in audit.source_evaluations.items():
            status = "[bold green]PASS[/bold green]" if ev.passed_all_tests else "[bold yellow]WARN[/bold yellow]"
            table.add_row(
                name.upper(),
                f"{ev.shannon_entropy_bits:.5f} / 8.0",
                f"{ev.monobit_p_val:.4f}",
                f"{ev.runs_p_val:.4f}",
                f"{ev.serial_autocorr:+.5f}",
                status,
            )
        console.print(table)

        # Lottery vs Quantum Comparison Table
        q_table = Table(title="Lottery Globe vs Quantum Entropy Audit (Indistinguishability)", box=None)
        q_table.add_column("Statistical Test", style="bold white")
        q_table.add_column("Metric / Statistic", justify="right")
        q_table.add_column("p-value", justify="right")
        q_table.add_column("Status", justify="center")

        ks_status = "[bold green]PASS (H_0)[/bold green]" if audit.ks_p_value >= 0.01 else "[bold red]FAIL[/bold red]"
        chi2_status = "[bold green]PASS (H_0)[/bold green]" if audit.chi2_p_value >= 0.01 else "[bold red]FAIL[/bold red]"

        q_table.add_row("Kolmogorov-Smirnov (2-sample)", f"D = {audit.ks_statistic:.4f}", f"{audit.ks_p_value:.4f}", ks_status)
        q_table.add_row("Chi-Square Uniformity", f"N = {audit.total_draws_evaluated} draws", f"{audit.chi2_p_value:.4f}", chi2_status)
        console.print(q_table)

        if audit.is_indistinguishable:
            console.print(
                "\n[bold green]✅ Popperian Verdict:[/bold green] Real lottery balls are statistically indistinguishable "
                "from pure quantum physical entropy ($p \\ge 0.01$). Null hypothesis $H_0$ is retained."
            )
        else:
            console.print(
                "\n[bold yellow]⚠️ Popperian Verdict:[/bold yellow] Real lottery draws exhibited statistically significant "
                "deviation from quantum randomness ($p < 0.01$)."
            )

    if export_md:
        out_path = Path(export_md)
        export_quantum_entropy_report(audit, out_path)
        if not quiet:
            console.print(f"[green]✔[/green] Quantum entropy empirical study saved to [bold cyan]{export_md}[/bold cyan]")
