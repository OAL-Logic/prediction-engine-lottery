"""
Batch Grade Command 📋
======================
Quick structural screen for many tickets at once (one line each) — sum,
parity, prime count, decade spread, symmetry, and validity. A fast triage
pass to spot outliers before running the deeper `ticket-grade` (frequency/
streak/pair-synergy/consensus) on the tickets that look interesting.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, decade_spread, symmetry_score
from engine.modules.filters import PRIMES

console = Console()
_PRIME_SET = set(int(p) for p in PRIMES)


def parse_tickets_file(path: str) -> list[list[int]]:
    tickets = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        nums = [int(x) for x in line.split() if x.lstrip("-").isdigit()]
        if nums:
            tickets.append(nums)
    return tickets


def score_ticket(nums: list[int], adapter) -> dict:
    lo, hi = adapter.rules.number_range
    odds = sum(1 for n in nums if n % 2 == 1)
    primes = sum(1 for n in nums if n in _PRIME_SET)
    return {
        "numbers": nums,
        "valid": adapter.validate(sorted(nums)),
        "sum": sum(nums),
        "odd_even": f"{odds}/{len(nums) - odds}",
        "primes": primes,
        "decade_spread": decade_spread(nums, lo, hi),
        "symmetry": symmetry_score(nums, lo, hi),
    }


def batch_grade(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    file: Annotated[str, typer.Option("--file", "-f", help="File with one ticket per line, space-separated numbers")],
    export_csv: Annotated[Optional[str], typer.Option("--export-csv", help="Write the summary table to this CSV file")] = None,
) -> None:
    """📋 Quick structural screen (sum/parity/primes/spread) for many tickets at once."""

    adapter = get_adapter(lottery)

    try:
        tickets = parse_tickets_file(file)
    except OSError as e:
        console.print(f"[red]✗ Could not read {file}: {e}[/red]")
        raise typer.Exit(1)

    if not tickets:
        console.print(f"[yellow]No tickets found in {file}.[/yellow]")
        raise typer.Exit(1)

    scored = [score_ticket(t, adapter) for t in tickets]

    ui_header("BATCH GRADE", f"{adapter.rules.name} · {len(scored)} tickets")
    table = ui_table(columns=["#", "Ticket", "Valid", "Sum", "Odd/Even", "Primes", "Decade Spread", "Symmetry"])
    for i, s in enumerate(scored, start=1):
        valid_str = "[green]✓[/green]" if s["valid"] else "[red]✗[/red]"
        table.add_row(str(i), str(s["numbers"]), valid_str, str(s["sum"]), s["odd_even"], str(s["primes"]), f"{s['decade_spread']:.2f}", f"{s['symmetry']:.1f}")
    console.print(table)

    n_valid = sum(1 for s in scored if s["valid"])
    console.print(f"\n[bold]{n_valid}/{len(scored)}[/bold] tickets are structurally valid for {adapter.rules.name}.")

    if export_csv:
        with open(export_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["#", "numbers", "valid", "sum", "odd_even", "primes", "decade_spread", "symmetry"])
            for i, s in enumerate(scored, start=1):
                writer.writerow([i, " ".join(map(str, s["numbers"])), s["valid"], s["sum"], s["odd_even"], s["primes"], f"{s['decade_spread']:.4f}", f"{s['symmetry']:.4f}"])
        console.print(f"[dim]Summary written to {export_csv}[/dim]")
