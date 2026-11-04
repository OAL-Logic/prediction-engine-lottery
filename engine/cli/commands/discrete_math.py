"""
Discrete Mathematics CLI Command 📐🎲
=====================================
Analyzes lottery sample spaces through:
1. Exact Hypergeometric Probability Distributions for all match categories.
2. Linearity of Expectation for overall monetary return and house edge.
3. Birthday Paradox / Hash Collision Risk across historical draw counts.
4. Spectral Graph Laplacian Community Partitioning (Fiedler Vector).
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter
from engine.modules.discrete_math import (
    compute_hypergeometric_distribution,
    compute_spectral_communities,
)

console = Console()


def discrete_math_cmd(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/mega-sena, br/lotofacil")],
    cost_override: Annotated[Optional[float], typer.Option("--cost", "-c", help="Override standard ticket price")] = None,
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-j", help="Estimated top prize jackpot for EV calculation")] = None,
    spectral: Annotated[bool, typer.Option("--spectral", "-s", help="Run Graph Laplacian spectral bisection into orthogonal communities")] = False,
    draws: Annotated[int, typer.Option("--draws", "-n", help="Historical draws to use for co-occurrence graph (default 200)")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append discrete math report to this Markdown file")] = None,
) -> None:
    """📐 Discrete Probability, Hypergeometric Distributions & Graph Spectral Bisection."""
    adapter = get_adapter(lottery)
    rules = adapter.rules
    df = adapter.fetch()

    # Tally observed draws and duplicate check
    observed_draws = len(df)
    seen_draws: set[tuple[int, ...]] = set()
    duplicate_count = 0
    if not df.empty and "numbers" in df.columns:
        for row in df["numbers"]:
            tup = tuple(sorted(row))
            if tup in seen_draws:
                duplicate_count += 1
            seen_draws.add(tup)

    # Approximate prize tier mapping if jackpot passed
    prize_map: dict[int, float] = {}
    if jackpot is not None:
        prize_map[rules.pick_count] = float(jackpot)
        # Scaled secondary tier defaults if known
        if rules.pick_count == 6:  # Mega-Sena style
            prize_map[5] = float(jackpot * 0.003)
            prize_map[4] = float(jackpot * 0.00008)
        elif rules.pick_count == 15:  # Lotofácil style
            prize_map[14] = 1800.0
            prize_map[13] = 30.0
            prize_map[12] = 12.0
            prize_map[11] = 6.0

    report = compute_hypergeometric_distribution(
        rules=rules,
        prize_map=prize_map,
        cost_override=cost_override,
        observed_draws=observed_draws,
        duplicate_draws=duplicate_count,
    )

    cur = getattr(rules, "currency", "BRL")

    # Header Panel
    summary_text = (
        f"[bold cyan]Lottery Game:[/bold cyan]            {rules.name} (Pick {rules.pick_count} from Pool {report.pool_n})\n"
        f"[bold cyan]Discrete State Space:[/bold cyan]    C({report.pool_n}, {rules.pick_count}) = {report.total_combinations:,} distinct combinations\n"
        f"[bold cyan]Ticket Price:[/bold cyan]            {cur} {report.ticket_cost:.2f}\n"
        f"[bold cyan]Birthday Paradox (50%):[/bold cyan] {report.birthday_collision_50pct:,} draws for 50% duplicate collision probability\n"
        f"[bold cyan]Birthday Paradox (99%):[/bold cyan] {report.birthday_collision_99pct:,} draws for 99% duplicate collision probability\n"
        f"[bold cyan]Observed History:[/bold cyan]        {observed_draws:,} draws recorded ({duplicate_count} duplicate draws observed)"
    )
    console.print(Panel(summary_text, title="📐 Discrete Probability & Combinatorial Sample Space", border_style="cyan"))

    # Hypergeometric Table
    table = Table(
        title=f"🎲 Exact Hypergeometric Distribution P(X = m) — {rules.name.upper()}",
        box=ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Matches (m)", justify="center", style="bold yellow")
    table.add_column("Favorable Subsets C(k,m)C(N-k,k-m)", justify="right", style="cyan")
    table.add_column("Exact Probability P(m)", justify="right", style="green")
    table.add_column("Odds (1 in ...)", justify="right", style="bold white")
    if jackpot is not None:
        table.add_column(f"Assigned Prize ({cur})", justify="right", style="dim")
        table.add_column(f"E[X] Contribution", justify="right", style="magenta")

    for t in report.tiers:
        prob_str = f"{t.probability:.8f}" if t.probability >= 1e-6 else f"{t.probability:.2e}"
        odds_str = f"1 in {t.odds_one_in:,.1f}" if t.odds_one_in != float("inf") else "—"
        row_items = [str(t.matches), f"{t.favorable_subsets:,}", prob_str, odds_str]
        if jackpot is not None:
            prize_str = f"{t.prize_amount:,.2f}" if t.prize_amount > 0 else "—"
            ev_str = f"{t.expected_value:.4f}"
            row_items.extend([prize_str, ev_str])
        table.add_row(*row_items)

    console.print(table)

    if jackpot is not None:
        ev_panel = (
            f"[bold green]Total Expected Return E[Payout]:[/bold green] {cur} {report.total_expected_return:.2f}\n"
            f"[bold yellow]Net Expected Value (E[X] - Cost):[/bold yellow]  {cur} {report.net_expected_value:+.2f}\n"
            f"[bold red]Calculated House Edge:[/bold red]            {report.house_edge:.2f}%"
        )
        console.print(Panel(ev_panel, title="⚖️ Linearity of Expectation & Expected Monetary Value", border_style="green"))

    # Graph Laplacian Spectral Bisection
    if spectral:
        spectral_res = compute_spectral_communities(df, rules, draws_limit=draws)
        spec_table = Table(
            title="🕸️ Graph Laplacian Spectral Bisection (Fiedler Vector Community Split)",
            box=ROUNDED,
            header_style="bold cyan",
        )
        spec_table.add_column("Metric", style="bold white")
        spec_table.add_column("Value", style="cyan")

        spec_table.add_row("Algebraic Connectivity (λ₂)", f"{spectral_res.algebraic_connectivity:.4f}")
        spec_table.add_row("Community A (Fiedler ≥ Median)", " ".join(f"{n:02d}" for n in spectral_res.community_a))
        spec_table.add_row("Community B (Fiedler < Median)", " ".join(f"{n:02d}" for n in spectral_res.community_b))
        spec_table.add_row("Interpretation", "Orthogonal communities based on historical co-occurrence graph bisection.")
        console.print(spec_table)

    # Optional Markdown export
    if export_md:
        from pathlib import Path
        out_path = Path(export_md)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        md_lines = [
            f"# Discrete Mathematics & Probability Report: {rules.name}\n\n",
            f"- **Combinatorial Space**: C({report.pool_n}, {rules.pick_count}) = {report.total_combinations:,}\n",
            f"- **Ticket Cost**: {cur} {report.ticket_cost:.2f}\n",
            f"- **Birthday Collision (50%)**: {report.birthday_collision_50pct:,} draws\n",
            f"- **Observed Draws**: {observed_draws:,} (Duplicates: {duplicate_count})\n\n",
            "| Matches | Favorable Subsets | Probability | Odds |\n",
            "| :---: | :---: | :---: | :---: |\n",
        ]
        for t in report.tiers:
            p_s = f"{t.probability:.8f}" if t.probability >= 1e-6 else f"{t.probability:.2e}"
            o_s = f"1 in {t.odds_one_in:,.1f}" if t.odds_one_in != float("inf") else "—"
            md_lines.append(f"| {t.matches} | {t.favorable_subsets:,} | {p_s} | {o_s} |\n")
        out_path.write_text("".join(md_lines), encoding="utf-8")
        console.print(f"\n[bold green]✓ Report exported to:[/bold green] {out_path}")
