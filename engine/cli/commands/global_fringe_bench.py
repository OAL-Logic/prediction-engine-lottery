"""
Global-Fringe-Bench CLI Command 🌐🔬
===================================
Executes cross-jurisdictional empirical benchmarks for the 9 Fringe Theories
across contrasting physical ball machine archetypes (Air-Mix vs Gravity-Pick vs Pneumatic).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.modules.global_fringe_benchmark import (
    export_global_fringe_report,
    run_global_fringe_benchmark,
)

console = Console()


def global_fringe_bench(
    lotteries: str = "br/mega-sena,us/powerball,eu/euro-millions",
    draws: int = 50,
    seed: int = 42,
    export_md: Optional[str] = "reports/global/studies/fringe-theories-international-evaluation.md",
    quiet: bool = False,
) -> None:
    """🌐 Benchmark fringe theories across global lotteries and machine archetypes."""
    target_lotteries = [lid.strip() for lid in lotteries.split(",") if lid.strip()]

    if not quiet:
        console.print(
            Panel.fit(
                f"[bold cyan]🌐 Global Multi-Jurisdiction Fringe Benchmark[/bold cyan]\n"
                f"[dim]Targets: [bold white]{', '.join(target_lotteries)}[/bold white] | Draws per game: [bold white]{draws}[/bold white][/dim]\n"
                f"[dim]Testing Air-Mix (Caixa) vs Gravity-Pick (Smartplay) vs Pneumatic (Stresa)[/dim]",
                border_style="cyan",
            )
        )

    with console.status("[bold green]Executing international blind backtests across jurisdictions..."):
        result = run_global_fringe_benchmark(
            lotteries=target_lotteries,
            draws=draws,
            seed=seed,
        )

    if not quiet:
        for lid, summary in result.lottery_summaries.items():
            table = Table(
                title=f"{summary.lottery_name} ({lid}) — Archetype: {summary.machine_archetype.value.upper()}",
                box=None,
            )
            table.add_column("Strategy", style="bold white")
            table.add_column("Mean Hits (μ)", justify="right")
            table.add_column("Theoretical EV", justify="right")
            table.add_column("Lift vs EV", justify="right")
            table.add_column("p-value (H_0)", justify="right")
            table.add_column("Status", justify="center")

            for s_name, m in summary.strategies.items():
                status_color = "green" if m.h0_retained else "red"
                status_label = "RETAINED" if m.h0_retained else "REJECTED"
                lift_color = "green" if m.lift_vs_ev_pct >= 0 else "red"

                table.add_row(
                    s_name,
                    f"{m.mean_hits:.4f}",
                    f"{m.theoretical_ev:.4f}",
                    f"[{lift_color}]{m.lift_vs_ev_pct:+.2f}%[/{lift_color}]",
                    f"{m.p_value_vs_ev:.4f}",
                    f"[{status_color}]{status_label}[/{status_color}]",
                )
            console.print(table)

        if result.all_h0_retained:
            console.print(
                "\n[bold green]✅ Global Popperian Verdict:[/bold green] All 9 fringe theories retained "
                "the null hypothesis ($p \\ge 0.01$) across all international jurisdictions and machine types. "
                "Physical lottery machines behave as ideal stochastic entropy sources globally."
            )
        else:
            console.print(
                "\n[bold red]⚠️ Global Popperian Verdict:[/bold red] Statistical anomaly detected in one or more "
                "international machine archetypes."
            )

    if export_md:
        out_path = Path(export_md)
        export_global_fringe_report(result, out_path)
        if not quiet:
            console.print(f"[green]✔[/green] Global empirical study saved to [bold cyan]{export_md}[/bold cyan]")
