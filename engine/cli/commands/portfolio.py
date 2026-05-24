"""
Portfolio Command 💼
==================
Generates a diversified ticket portfolio across multiple tiers.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

def portfolio(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    full_name: Annotated[str, typer.Option("--full-name", help="Full birth name for Kabbalistic numerology (use quotes for multi-word names)")] = "GEMINI ENGINE",
    birth_date: Annotated[str, typer.Option("--birth-date", help="Birthday (YYYY-MM-DD)")] = "1990-01-01",
) -> None:
    """
    💼 Generate a diversified ticket portfolio (Statistical, Chaos, and Deep tiers).
    """
    # Bootstrap strategy registry
    import engine.strategies.statistical  # noqa: F401
    import engine.strategies.fun          # noqa: F401
    try:
        import engine.strategies.ml       # noqa: F401
    except Exception:
        pass
    try:
        import engine.strategies.deep     # noqa: F401
    except Exception:
        pass

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    
    console.rule(f"[bold cyan]Strategic Portfolio: {adapter.rules.name}[/bold cyan]")
    
    tiers = {
        "Statistical (Nerd)": ["hybrid:markov,bayesian,weighted", "mutual_info"],
        "Chaos (Esoteric)": ["kabbalistic", "reincarnation"],
        "Deep Learning (AI)": ["transformer", "cnn_1d"]
    }
    
    total_tickets = []
    
    for tier_name, strat_list in tiers.items():
        console.print(f"\n  [bold]{tier_name}[/bold]")
        for s_name in strat_list:
            try:
                # Setup
                if ":" in s_name:
                    ename, mstr = s_name.split(":", 1)
                    members = [m.strip() for m in mstr.split(",")]
                    from engine.strategies.ml.ensemble import HybridEnsemble
                    strat = HybridEnsemble(members=members)
                else:
                    strat = get_strategy(s_name, full_name=full_name, birth_date=birth_date)
                
                # Run
                res = strat.suggest(df, adapter.rules, count=1)
                ticket = res.tickets[0]
                total_tickets.append(ticket)
                
                # Display
                s_label = s_name.split(":")[0]
                console.print(f"    • {s_label:15} : [bold green]{ticket}[/bold bold green]  [dim](conf: {res.confidence:.2f})[/dim]")
            except Exception as e:
                console.print(f"    • {s_name:15} : [red]Failed ({type(e).__name__})[/red]")

    # Convergence Check
    from collections import Counter
    flat = [n for t in total_tickets for n in t]
    counts = Counter(flat)
    common = [n for n, c in counts.items() if c >= 2]
    
    if common:
        console.print(f"\n  [bold yellow]🔥 Convergence Detected:[/bold yellow] Numbers {sorted(common)} appear in multiple tiers.")
    
    console.rule()
