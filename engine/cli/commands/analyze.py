"""
Analyze Command 📊
=================
Run statistical analysis modules or a unified dashboard.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, print_command_summary
from engine.modules import frequency, deviation, correlation, weekday, regime

console = Console()

def analyze(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    module: Annotated[str, typer.Option("--module", "-m", help="frequency | deviation | correlation | dashboard | summary | weekday | regime")] = "dashboard",
    limit: Annotated[Optional[int], typer.Option("--limit", "-n", help="Use only the N most recent draws")] = None,
    top: Annotated[int, typer.Option("--top", help="Number of items to show in tables")] = 10,
    view: Annotated[Optional[str], typer.Option("--view", help="Dashboard view: alerts | odd_even | primes | fibonacci | frame | multiples_3 | magic | repeated | complete")] = None,
) -> None:
    """📊 Run statistical analysis modules or a unified dashboard."""

    print_command_summary("analyze", lottery, module=module, limit=limit, top=top)

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch(limit=limit)

    if module == "frequency":
        res = frequency.analyze(df, adapter.rules, top_n=top)
        frequency.print_report(res)
    elif module == "deviation":
        res = deviation.analyze(df, adapter.rules, top_n=top)
        deviation.print_report(res)
    elif module == "correlation":
        res = correlation.analyze(df, adapter.rules, top_n=top)
        correlation.print_report(res)
    elif module == "weekday":
        res = weekday.analyze(df, adapter.rules)
        weekday.print_report(res, top_n=top)
    elif module == "regime":
        res = regime.analyze_stability(df, adapter.rules)
        regime.print_report(res)
    elif module == "dashboard":
        # Deferred import to keep help fast
        from engine.cli.commands.dashboard import render_dashboard
        render_dashboard(df, adapter.rules, limit=limit or 100, view=view)
    elif module == "summary":
        # Minimalist summary for quick look
        f_res = frequency.analyze(df, adapter.rules, top_n=5)
        d_res = deviation.analyze(df, adapter.rules, top_n=5)
        console.print(f"\n[bold]Hot Numbers:[/bold]  {f_res.hot}")
        console.print(f"[bold]Cold Numbers:[/bold] {f_res.cold}")
        console.print(f"[bold]Overdue:[/bold]      {d_res.overdue}")
    else:
        typer.echo(f"Unknown module '{module}'. Choose: frequency, deviation, correlation, dashboard, summary")
        raise typer.Exit(1)
