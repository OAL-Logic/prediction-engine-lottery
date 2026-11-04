"""
Synthetic Multiverse Benchmark Command (`engine.cli.commands.synthetic_bench`)
==============================================================================
Benchmarks fringe theories across synthetic universes with controlled physical
anomalies (Ising, Lorenz, Zeno) to measure ROC AUC and statistical power.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from engine.cli.utils import get_adapter
from engine.modules.synthetic_multiverse import (
    run_synthetic_multiverse_benchmark,
    export_synthetic_benchmark_report,
    render_ascii_roc_curve,
)


console = Console()


def synthetic_bench(
    lottery: Annotated[str, typer.Argument(help="Lottery game identifier (e.g. br/mega-sena, br/quina, br/lotofacil)")] = "br/mega-sena",
    draws: Annotated[int, typer.Option("--draws", "-n", help="Synthetic universe draw depth per experiment")] = 120,
    seed: Annotated[int, typer.Option("--seed", "-s", help="Random seed for synthetic universe generator")] = 42,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export markdown report path")] = "reports/br/studies/fringe-theories-synthetic-benchmarks.md",
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Suppress progress output")] = False,
) -> None:
    """🌌 Benchmark fringe theories against controlled synthetic universes with physical anomalies."""
    adapter = get_adapter(lottery)
    rules = adapter.rules

    if not quiet:
        console.print(Panel(
            f"[bold yellow]🌌 SYNTHETIC MULTIVERSE MONTE CARLO BENCHMARK[/bold yellow]\n"
            f"Game: [bold white]{rules.name}[/bold white] ({rules.pick_count}/{rules.number_range[1] - rules.number_range[0] + 1})\n"
            f"Draws per Universe: {draws} | Evaluated Signals: λ ∈ [0.00, 0.15, 0.35, 0.60]\n"
            f"Anomalies Injected: 2D Ising Lattice, Lorenz Strange Attractor, Quantum Zeno Freeze",
            border_style="yellow"
        ))

    def progress_cb(cur: int, total: int, msg: str) -> None:
        if not quiet:
            pct = (cur / total) * 100.0 if total > 0 else 0.0
            print(f"\r  [{cur}/{total}] {pct:5.1f}% | {msg:<60}", end="", flush=True)

    results = run_synthetic_multiverse_benchmark(
        rules=rules,
        n_draws=draws,
        seed=seed,
        on_progress=progress_cb if not quiet else None,
    )

    if not quiet:
        print("\n")
        table = Table(title=f"Synthetic Multiverse Sensitivity Matrix ({rules.name})", border_style="bright_black")
        table.add_column("Strategy", style="bold cyan")
        table.add_column("Anomaly", style="white")
        table.add_column("Signal (λ)", justify="right")
        table.add_column("SNR", justify="right")
        table.add_column("ROC AUC", justify="right", style="bold yellow")
        table.add_column("Power @ 5% FPR", justify="right")
        table.add_column("Mean Hits", justify="right")
        table.add_column("Status", style="green")

        for b in results:
            sig_str = "0.00 (Noise)" if b.signal_strength == 0.0 else f"{b.signal_strength:.2f}"
            snr_str = f"{b.snr:.2f}" if b.snr < 100 else "∞"
            status = "Control (AUC ≈ 0.50)" if b.signal_strength == 0.0 else ("High Confidence" if b.auc_score >= 0.80 else "Partial Detection")
            table.add_row(
                b.strategy_name,
                b.anomaly_type,
                sig_str,
                snr_str,
                f"{b.auc_score:.3f}",
                f"{b.power_at_5pct_fpr * 100:.1f}%",
                f"{b.hit_rate:.2f}",
                status,
            )
        console.print(table)

    if export_md:
        out_path = Path(export_md)
        export_synthetic_benchmark_report(results, rules, out_path)
        if not quiet:
            console.print(f"\n[green]✓[/green] Synthetic benchmark study exported to: [bold]{out_path.as_posix()}[/bold]")
