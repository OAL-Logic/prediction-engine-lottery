"""
Ticket Optimize Command ✂️
=========================
SamLotto's "Optimize Bet Tickets" (TopForm) equivalent: reduces candidate
ticket pools to save wager costs while preserving broad combinatorial coverage.

Offers two core strategies:
1. Same-number reduction: collapses lines sharing >= X identical numbers.
2. Reserve-per-block: reserves X lines from every block of N lines (e.g. 3 of 10).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, Theme
from engine.modules.ticket_optimizer import same_number_reduction, reserve_per_block

console = Console()


def _parse_ticket_file(file_path: Path) -> list[list[int]]:
    tickets = []
    text = file_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Split by whitespace or commas
        delimiters = [",", ";", "\t", " "]
        parts = []
        for token in line.replace(",", " ").replace(";", " ").split():
            try:
                parts.append(int(token))
            except ValueError:
                pass
        if parts:
            tickets.append(sorted(parts))
    return tickets


def ticket_optimize(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/lotofacil")],
    tickets_file: Annotated[Optional[Path], typer.Option("--file", "-f", help="Path to text file containing tickets (one line per ticket)")] = None,
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Optimization strategy: 'same-number' or 'reserve-per-block'")] = "same-number",
    shared: Annotated[int, typer.Option("--shared", help="For same-number: prune lines sharing >= this many numbers")] = 4,
    reserve: Annotated[int, typer.Option("--reserve", help="For reserve-per-block: how many tickets to keep per block")] = 3,
    block_size: Annotated[int, typer.Option("--block-size", help="For reserve-per-block: block partition size (default 10)")] = 10,
    generate_count: Annotated[int, typer.Option("--gen-count", help="If no file provided, auto-generate this many tickets to optimize")] = 30,
    out: Annotated[Optional[Path], typer.Option("--out", "-o", help="Optional output file to save optimized tickets")] = None,
) -> None:
    """✂️ Optimize and prune bet tickets using SamLotto's TopForm reduction rules."""

    adapter = get_adapter(lottery)
    rules = adapter.rules

    # Load tickets from file or generate a sample candidate set
    raw_tickets: list[list[int]] = []
    if tickets_file:
        if not tickets_file.exists():
            console.print(f"[red]✗ Tickets file not found: {tickets_file}[/red]")
            raise typer.Exit(1)
        raw_tickets = _parse_ticket_file(tickets_file)
        if not raw_tickets:
            console.print(f"[red]✗ No valid tickets parsed from {tickets_file}[/red]")
            raise typer.Exit(1)
    else:
        # Generate candidate tickets using the engine's weighted strategy
        df = adapter.fetch()
        if df.empty:
            console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
            raise typer.Exit(1)
        from engine.strategies import get_strategy
        strat = get_strategy("weighted")
        res = strat.suggest(df, rules, count=generate_count, temperature=0.7)
        raw_tickets = [sorted(t) for t in res.tickets]

    ui_header(
        "TICKET OPTIMIZER",
        f"{rules.name} · SamLotto TopForm · {len(raw_tickets)} candidate tickets loaded"
    )

    # Execute optimization based on strategy
    strat_key = strategy.lower().replace("_", "-")
    if strat_key in ("same-number", "samenumber", "same"):
        report = same_number_reduction(raw_tickets, max_shared=shared)
    elif strat_key in ("reserve-per-block", "reserve", "block"):
        report = reserve_per_block(raw_tickets, reserve_count=reserve, block_size=block_size)
    else:
        console.print(f"[red]✗ Unknown strategy: '{strategy}'. Choose 'same-number' or 'reserve-per-block'.[/red]")
        raise typer.Exit(1)

    # Print summary table
    summary_table = ui_table("Optimization Funnel", ["Metric", "Value"])
    summary_table.add_row("Strategy Applied", f"[bold cyan]{report.strategy}[/bold cyan]")
    summary_table.add_row("Parameters", report.parameter_summary)
    summary_table.add_row("Initial Ticket Count", f"{report.initial_count:,}")
    summary_table.add_row("Kept Ticket Count", f"[bold green]{report.kept_count:,}[/bold green]")
    summary_table.add_row("Eliminated Count", f"[bold red]{report.eliminated_count:,}[/bold red]")
    summary_table.add_row("Cost Reduction Ratio", f"[bold yellow]{report.reduction_pct:.1f}% saved[/bold yellow]")
    console.print(summary_table)

    # Preview kept tickets
    preview_count = min(10, len(report.kept_tickets))
    if preview_count > 0:
        preview_table = ui_table(f"Optimized Tickets (first {preview_count} shown)", ["#", "Numbers"])
        for idx, ticket in enumerate(report.kept_tickets[:preview_count], 1):
            formatted_nums = " ".join(f"{n:02d}" for n in ticket)
            preview_table.add_row(str(idx), formatted_nums)
        console.print(preview_table)

    # Write output if requested
    if out:
        out_content = "\n".join(" ".join(f"{n:02d}" for n in t) for t in report.kept_tickets)
        out.write_text(out_content + "\n", encoding="utf-8")
        console.print(f"[green]✓ Wrote {len(report.kept_tickets)} optimized tickets to {out}[/green]")
