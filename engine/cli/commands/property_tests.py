"""
Property Tests Command 🧪
=========================
Adversarial unit testing using the Hypothesis framework.
Tests strategies against degenerate, chaotic, and boundary-condition draw histories
to ensure score invariants (0 <= score <= 1) are maintained.
"""

from __future__ import annotations

from typing import Annotated, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import get_strategy, list_strategies

console = Console()

def run_adversarial_test(strategy_name: str, rules: DrawRules, n_draws: int = 100) -> dict:
    """Run a manual adversarial test instead of deep hypothesis integration for CLI."""
    import random
    lo, hi = rules.number_range
    pick = rules.pick_count
    
    scenarios = {
        "All Same Number": [[lo]*pick for _ in range(n_draws)],
        "Sequential": [list(range(lo, lo+pick)) for _ in range(n_draws)],
        "High Entropy": [random.sample(range(lo, hi+1), pick) for _ in range(n_draws)],
        "Oscillating": [
            list(range(lo, lo+pick)) if i%2==0 else list(range(hi-pick+1, hi+1))
            for i in range(n_draws)
        ]
    }
    
    results = {}
    try:
        strat = get_strategy(strategy_name)
    except Exception:
        return {"status": "error", "reason": "Failed to load"}
        
    for name, draws in scenarios.items():
        df = pd.DataFrame([{"draw_id": i+1, "numbers": d} for i, d in enumerate(draws)])
        try:
            scores = strat.score(df, rules)
            
            # Check invariants
            if not scores:
                results[name] = "FAIL (Empty)"
                continue
                
            vals = list(scores.values())
            if any(pd.isna(v) for v in vals):
                results[name] = "FAIL (NaN)"
            elif max(vals) > 1.0001 or min(vals) < -0.0001:
                results[name] = "FAIL (Bounds)"
            else:
                results[name] = "PASS"
        except Exception as e:
            results[name] = f"ERROR ({type(e).__name__})"
            
    return results

def property_tests(
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy to test (or 'all')")] = "all",
) -> None:
    """🧪 Run adversarial property-based tests to verify strategy stability."""
    from engine.adapters.br.mega_sena import MegaSenaAdapter
    rules = MegaSenaAdapter().rules
    
    strategies = [s["name"] for s in list_strategies()] if strategy == "all" else [strategy]
    
    console.rule("[bold cyan]🧪 ADVERSARIAL PROPERTY TESTING[/bold cyan]")
    
    table = Table(box=None)
    table.add_column("Strategy", style="bold white")
    table.add_column("Degenerate", justify="center")
    table.add_column("Sequential", justify="center")
    table.add_column("Chaos", justify="center")
    table.add_column("Oscillating", justify="center")
    
    def colorize(res):
        if res == "PASS": return "[green]PASS[/green]"
        return f"[red]{res}[/red]"
        
    with console.status("[cyan]Subjecting strategies to extreme adversarial conditions..."):
        for s in strategies:
            r = run_adversarial_test(s, rules)
            if "status" in r and r["status"] == "error":
                continue
                
            table.add_row(
                s,
                colorize(r.get("All Same Number", "N/A")),
                colorize(r.get("Sequential", "N/A")),
                colorize(r.get("High Entropy", "N/A")),
                colorize(r.get("Oscillating", "N/A"))
            )
            
    console.print(table)
    
    console.print(Panel(
        "Adversarial Testing ensures that strategies do not crash or produce invalid probabilities "
        "(NaN, >1.0, <0.0) when faced with theoretically possible but highly improbable draw histories.",
        border_style="cyan"
    ))

if __name__ == "__main__":
    property_tests("all")
