"""
Combo Diff Command 🆚
=====================
Structural side-by-side comparison of two tickets: shared numbers, numbers
unique to each side, and a delta on sum/parity/spread. Useful when deciding
between two candidate tickets or understanding how a swap changed a ticket.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, Theme, decade_spread, symmetry_score

console = Console()


def _parse_numbers(raw: str) -> list[int]:
    return sorted({int(x.strip()) for x in raw.split(",") if x.strip()})


def _parity(nums: list[int]) -> tuple[int, int]:
    odds = sum(1 for n in nums if n % 2 == 1)
    return odds, len(nums) - odds


def combo_diff(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    a: Annotated[str, typer.Option("--a", help="First ticket, comma-separated numbers")],
    b: Annotated[str, typer.Option("--b", help="Second ticket, comma-separated numbers")],
) -> None:
    """🆚 Structural side-by-side comparison of two tickets."""

    adapter = get_adapter(lottery)
    lo, hi = adapter.rules.number_range
    ta, tb = _parse_numbers(a), _parse_numbers(b)

    if not ta or not tb:
        console.print("[red]✗ --a and --b must both contain at least one integer.[/red]")
        raise typer.Exit(1)

    ui_header("COMBO DIFF", adapter.rules.name)

    shared = sorted(set(ta) & set(tb))
    only_a = sorted(set(ta) - set(tb))
    only_b = sorted(set(tb) - set(ta))

    console.print(f"[bold]Ticket A:[/bold] {ta}")
    console.print(f"[bold]Ticket B:[/bold] {tb}")
    console.print(f"[bold {Theme.SUCCESS}]Shared ({len(shared)}):[/bold {Theme.SUCCESS}] {shared}")
    console.print(f"[bold]Only in A ({len(only_a)}):[/bold] {only_a}")
    console.print(f"[bold]Only in B ({len(only_b)}):[/bold] {only_b}")

    odds_a, evens_a = _parity(ta)
    odds_b, evens_b = _parity(tb)

    table = ui_table(title="Structural delta", columns=["Metric", "Ticket A", "Ticket B", "Δ (B − A)"])
    sum_a, sum_b = sum(ta), sum(tb)
    table.add_row("Sum", str(sum_a), str(sum_b), f"{sum_b - sum_a:+d}")
    table.add_row("Odd / Even", f"{odds_a}/{evens_a}", f"{odds_b}/{evens_b}", f"{(odds_b - odds_a):+d} odd")
    table.add_row("Decade spread", f"{decade_spread(ta, lo, hi):.2f}", f"{decade_spread(tb, lo, hi):.2f}", f"{decade_spread(tb, lo, hi) - decade_spread(ta, lo, hi):+.2f}")
    table.add_row("Symmetry (MAD from mid)", f"{symmetry_score(ta, lo, hi):.1f}", f"{symmetry_score(tb, lo, hi):.1f}", f"{symmetry_score(tb, lo, hi) - symmetry_score(ta, lo, hi):+.1f}")
    console.print(table)
