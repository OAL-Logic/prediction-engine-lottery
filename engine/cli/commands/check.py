"""
Check Command ✅
==============
Ticket structural evaluator and validator.
"""

from __future__ import annotations

from typing import Annotated
from collections import Counter

import typer
from rich.console import Console
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

def check(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    numbers: Annotated[str, typer.Argument(help="Space or comma-separated numbers [Required]")],
    show_range: Annotated[bool, typer.Option("--range", "-r", help="Visualize sum in analytical distribution")] = False,
) -> None:
    """✅ Check a ticket's structural patterns against historical rules."""
    from engine.modules.sum_range import classify, most_probable_range
    from engine.modules import filters as f_mod
    from engine.modules.harmony import registry

    adapter = get_adapter(lottery)
    rules = adapter.rules
    nums = sorted([int(n) for n in numbers.replace(",", " ").split()])

    if not adapter.validate(nums):
        console.print(f"[red]✗ Invalid ticket format for {rules.name}.[/red]")
        return

    console.rule(f"[bold cyan]Audit Report: {nums}[/bold cyan]")
    
    table = Table(box=None)
    table.add_column("Metric", style="dim")
    table.add_column("Value", style="bold")
    table.add_column("Status")
    
    # 1. Sum Range
    lo, hi, mean, sigma = most_probable_range(rules)
    s_val = sum(nums)
    s_status = "[green]Pass[/green]" if lo <= s_val <= hi else "[red]Fail[/red]"
    table.add_row("Sum", f"{s_val} (avg {mean:.1f})", s_status)
    
    # 2. Odd/Even (Parity)
    odds = [n for n in nums if n % 2 != 0]
    evens = [n for n in nums if n % 2 == 0]
    p_status = "[green]Balanced[/green]" if abs(len(odds) - len(evens)) <= 2 else "[yellow]Skewed[/yellow]"
    table.add_row("Odd/Even", f"{len(odds)}/{len(evens)}", p_status)

    # 3. High/Low
    mid = (rules.number_range[0] + rules.number_range[1]) / 2
    highs = [n for n in nums if n > mid]
    lows = [n for n in nums if n <= mid]
    hl_status = "[green]Balanced[/green]" if abs(len(highs) - len(lows)) <= 2 else "[yellow]Skewed[/yellow]"
    table.add_row("High/Low", f"{len(highs)}/{len(lows)}", hl_status)

    # 4. Decades (Decade Groups)
    decades = Counter(n // 10 for n in nums)
    d_count = len(decades)
    d_status = "[green]Well Spread[/green]" if d_count >= (3 if rules.pick_count <= 6 else 4) else "[yellow]Clustered[/yellow]"
    table.add_row("Decades", f"{d_count} groups", d_status)

    # 5. Last Digits (Unit Different)
    units = {n % 10 for n in nums}
    u_status = "[green]Unique[/green]" if len(units) >= (rules.pick_count - 2) else "[yellow]Repeated[/yellow]"
    table.add_row("Last Digits", f"{len(units)} distinct", u_status)

    # 6. Consecutive (Successive)
    succ = f_mod.get_successive_metrics(nums)
    c_status = "[green]Normal[/green]" if succ["max_successive"] < 3 else "[red]Clustered[/red]"
    table.add_row("Max Consec", f"{succ['max_successive']} run", c_status)

    # 7. Advanced (AC, Root Sum)
    ac = f_mod.get_ac_value(nums)
    rs = f_mod.get_root_sum(nums)
    table.add_row("AC Value", str(ac), "[green]Pass[/green]" if ac >= (rules.pick_count - 1) else "[red]Low[/red]")
    table.add_row("Root Sum", str(rs), "")
    
    console.print(table)

    # Final Structural Score (Heuristic)
    passed = sum(1 for status in [s_status, p_status, hl_status, d_status, u_status, c_status] if "green" in status)
    score = int((passed / 6) * 100)
    
    color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    console.print(f"\n[bold]Structural Score:[/bold] [{color}]{score}/100[/{color}]")


def validate(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    numbers: Annotated[str, typer.Argument(help="Numbers to validate [Required]")],
) -> None:
    """✔️ Quickly check if a set of numbers is valid for a given lottery's rules."""
    adapter = get_adapter(lottery)
    nums = [int(n) for n in numbers.replace(",", " ").split()]
    
    if adapter.validate(nums):
        console.print(f"[green]✓ Valid ticket[/green] for {adapter.rules.name}: {nums}")
    else:
        console.print(f"[red]✗ Invalid ticket[/red] for {adapter.rules.name}")
        r = adapter.rules
        console.print(f"  Rules: pick {r.pick_count} from {r.number_range[0]}–{r.number_range[1]}")
