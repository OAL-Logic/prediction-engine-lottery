"""
Signature Audit Command 🔍
==========================
Compares the 'Digital Signature' of a given ticket against the 'Golden Signature'
of all historical winning draws. Computes similarities in root sum, digit distribution,
parity, and intervals.
"""

from __future__ import annotations

from typing import Annotated, Optional
import pandas as pd
import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

def digital_root(n: int) -> int:
    """Calculate the digital root of a number."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9

def get_signature(numbers: list[int], lo: int, hi: int) -> dict:
    """Calculate the structural signature of a ticket."""
    sig = {}
    sig["sum"] = sum(numbers)
    sig["root_sum"] = digital_root(sig["sum"])
    
    evens = sum(1 for n in numbers if n % 2 == 0)
    sig["parity_ratio"] = evens / len(numbers)
    
    mid = (lo + hi) / 2
    highs = sum(1 for n in numbers if n > mid)
    sig["high_ratio"] = highs / len(numbers)
    
    # Digit frequencies (first and second digits)
    digits = []
    for n in numbers:
        digits.extend([int(d) for d in str(n)])
    
    from collections import Counter
    dc = Counter(digits)
    sig["most_common_digit"] = dc.most_common(1)[0][0] if dc else 0
    
    # Max interval between sorted numbers
    sorted_n = sorted(numbers)
    intervals = [sorted_n[i+1] - sorted_n[i] for i in range(len(sorted_n)-1)]
    sig["max_gap"] = max(intervals) if intervals else 0
    
    return sig

def signature_audit(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    ticket: Annotated[str, typer.Argument(help="Space-separated ticket numbers")],
) -> None:
    """🔍 Compare ticket structural signature against historical golden average."""
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    
    try:
        user_nums = sorted([int(x) for x in ticket.split()])
    except ValueError:
        console.print("[red]Error: Ticket must be space-separated integers.[/red]")
        return
        
    if len(user_nums) != rules.pick_count:
        console.print(f"[yellow]Warning: Ticket length ({len(user_nums)}) differs from standard pick count ({rules.pick_count}).[/yellow]")
        
    # 1. Calculate historical 'Golden Signature'
    with console.status("[cyan]Computing Golden Historical Signature..."):
        hist_sigs = []
        for row in df.itertuples():
            hist_sigs.append(get_signature(row.numbers, lo, hi))
            
        golden = {}
        golden["sum"] = np.mean([s["sum"] for s in hist_sigs])
        golden["root_sum"] = np.round(np.mean([s["root_sum"] for s in hist_sigs]))
        golden["parity_ratio"] = np.mean([s["parity_ratio"] for s in hist_sigs])
        golden["high_ratio"] = np.mean([s["high_ratio"] for s in hist_sigs])
        golden["most_common_digit"] = np.round(np.mean([s["most_common_digit"] for s in hist_sigs]))
        golden["max_gap"] = np.mean([s["max_gap"] for s in hist_sigs])

    # 2. Calculate User Signature
    user_sig = get_signature(user_nums, lo, hi)
    
    # 3. Compare and Display
    console.rule(f"[bold cyan]🔍 SIGNATURE AUDIT — {rules.name}[/bold cyan]")
    
    table = Table(box=None, title=f"Ticket: {user_nums}")
    table.add_column("Property", style="dim")
    table.add_column("Your Ticket", justify="right", style="bold yellow")
    table.add_column("Golden Mean", justify="right", style="cyan")
    table.add_column("Delta", justify="right")
    
    def add_metric(name, user_v, golden_v, is_float=False):
        if is_float:
            delta = user_v - golden_v
            d_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
            c = "green" if abs(delta) < 0.1 else ("yellow" if abs(delta) < 0.2 else "red")
            table.add_row(name, f"{user_v:.2f}", f"{golden_v:.2f}", f"[{c}]{d_str}[/{c}]")
        else:
            delta = user_v - golden_v
            d_str = f"+{delta:.0f}" if delta > 0 else f"{delta:.0f}"
            c = "green" if abs(delta) <= 1 else ("yellow" if abs(delta) <= 3 else "red")
            table.add_row(name, f"{user_v:.0f}", f"{golden_v:.0f}", f"[{c}]{d_str}[/{c}]")

    add_metric("Total Sum", user_sig["sum"], golden["sum"], is_float=True)
    add_metric("Root Sum", user_sig["root_sum"], golden["root_sum"], is_float=False)
    add_metric("Even Ratio", user_sig["parity_ratio"], golden["parity_ratio"], is_float=True)
    add_metric("High Ratio", user_sig["high_ratio"], golden["high_ratio"], is_float=True)
    add_metric("Common Digit", user_sig["most_common_digit"], golden["most_common_digit"], is_float=False)
    add_metric("Max Interval", user_sig["max_gap"], golden["max_gap"], is_float=True)
    
    console.print(table)
    
    # Verdict
    diffs = [
        abs(user_sig["parity_ratio"] - golden["parity_ratio"]),
        abs(user_sig["high_ratio"] - golden["high_ratio"]),
    ]
    avg_diff = np.mean(diffs)
    
    if avg_diff < 0.05:
        verdict = "[bold green]PERFECT ALIGNMENT[/bold green]: Ticket matches historical attractor."
    elif avg_diff < 0.15:
        verdict = "[bold yellow]ACCEPTABLE DEVIATION[/bold yellow]: Slight structural anomaly."
    else:
        verdict = "[bold red]SEVERE ANOMALY[/bold red]: Ticket defies fundamental draw physics."
        
    console.print(Panel(verdict, title="Audit Verdict", border_style="cyan"))

if __name__ == "__main__":
    signature_audit("br/mega-sena", "1 2 3 4 5 6")
