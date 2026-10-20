"""
Positional Ticket Generator Command 🎯
======================================
Lottery Studio's "Creating a Position Number Tickets" equivalent (Feature C3):
Independently specify a candidate-number list for each ticket slot/position,
then generate every valid ticket from the Cartesian product of those lists
(distinct numbers only, sorted into the final ticket).
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Annotated, Optional, List

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table

console = Console()
MAX_POSITION_COMBINATIONS = 500_000


def _parse_positions_string(spec: str) -> List[List[int]]:
    """Parses '1,2,3; 10,11,12; 20,21,22' into a list of number lists."""
    pos_lists = []
    for block in spec.split(";"):
        block = block.strip()
        if not block:
            continue
        nums = []
        for token in block.replace(",", " ").split():
            try:
                nums.append(int(token))
            except ValueError:
                pass
        if nums:
            pos_lists.append(sorted(set(nums)))
    return pos_lists


def position_generate(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/mega-sena")],
    positions_spec: Annotated[Optional[str], typer.Option("--positions", "-p", help="Semicolon-separated number lists per slot, e.g. '1,2,3; 10,11,12; 20,21,22'")] = None,
    spec_file: Annotated[Optional[Path], typer.Option("--file", "-f", help="Path to file with one position candidate list per line")] = None,
    limit: Annotated[Optional[int], typer.Option("--limit", "-l", help="Maximum combinations to generate")] = None,
    out: Annotated[Optional[Path], typer.Option("--out", "-o", help="Optional output file to save generated tickets")] = None,
) -> None:
    """🎯 Generate tickets from Cartesian product of independent position candidates."""

    adapter = get_adapter(lottery)
    rules = adapter.rules
    lo, hi = rules.number_range

    pos_candidates: List[List[int]] = []

    if spec_file:
        if not spec_file.exists():
            console.print(f"[red]✗ Position spec file not found: {spec_file}[/red]")
            raise typer.Exit(1)
        lines = [line.strip() for line in spec_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
        pos_candidates = _parse_positions_string("; ".join(lines))
    elif positions_spec:
        pos_candidates = _parse_positions_string(positions_spec)
    else:
        console.print("[red]✗ Must provide either --positions or --file.[/red]")
        console.print("[dim]Example: --positions \"1,2,3; 10,11,12; 20,21,22; 30,31,32; 40,41,42; 50,51,52\"[/dim]")
        raise typer.Exit(1)

    if len(pos_candidates) != rules.pick_count:
        console.print(f"[red]✗ Expected {rules.pick_count} positions for {rules.name}, but received {len(pos_candidates)} position lists.[/red]")
        raise typer.Exit(1)

    # Validate range
    for idx, c_list in enumerate(pos_candidates, 1):
        invalid = [n for n in c_list if not (lo <= n <= hi)]
        if invalid:
            console.print(f"[red]✗ Position {idx} contains numbers out of range {rules.number_range}: {invalid}[/red]")
            raise typer.Exit(1)

    theoretical = 1
    for c_list in pos_candidates:
        theoretical *= max(1, len(c_list))

    if theoretical > MAX_POSITION_COMBINATIONS:
        console.print(f"[red]✗ Product yields {theoretical:,} combinations, exceeding safety cap of {MAX_POSITION_COMBINATIONS:,}. Narrow your candidate lists.[/red]")
        raise typer.Exit(1)

    # Generate Cartesian product, filter distinct numbers, deduplicate
    seen = set()
    tickets = []
    for combo in product(*pos_candidates):
        if len(set(combo)) != len(combo):
            continue  # Number repeated across positions
        ticket = tuple(sorted(combo))
        if ticket not in seen:
            seen.add(ticket)
            tickets.append(list(ticket))
            if limit and len(tickets) >= limit:
                break

    ui_header("POSITIONAL TICKET GENERATOR", f"{rules.name} · {len(tickets)} valid tickets generated")

    pos_table = ui_table("Position Candidate Setup", ["Position", "Candidate Pool", "Count"])
    for idx, c_list in enumerate(pos_candidates, 1):
        pos_table.add_row(f"Slot #{idx}", " ".join(f"{n:02d}" for n in c_list), str(len(c_list)))
    console.print(pos_table)

    summary_table = ui_table("Combinatorial Results", ["Metric", "Value"])
    summary_table.add_row("Theoretical Product", f"{theoretical:,}")
    summary_table.add_row("Valid Distinct Tickets", f"[bold green]{len(tickets):,}[/bold green]")
    if limit and len(tickets) >= limit:
        summary_table.add_row("Output Limit", f"Capped at {limit:,}")
    console.print(summary_table)

    preview_count = min(10, len(tickets))
    if preview_count > 0:
        preview_table = ui_table(f"Generated Tickets (first {preview_count} shown)", ["#", "Ticket Numbers"])
        for idx, t in enumerate(tickets[:preview_count], 1):
            preview_table.add_row(str(idx), " ".join(f"{n:02d}" for n in t))
        console.print(preview_table)

    if out:
        out_content = "\n".join(" ".join(f"{n:02d}" for n in t) for t in tickets)
        out.write_text(out_content + "\n", encoding="utf-8")
        console.print(f"[green]✓ Wrote {len(tickets)} tickets to {out}[/green]")
