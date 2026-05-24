"""
Pruning Command ✂️
===============
Identifies and flags underperforming strategies that fail to beat the random baseline.
"""

from __future__ import annotations

from typing import Annotated, Optional, List

import typer
from rich.console import Console
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary
from engine.strategies import list_strategies
from engine.modules.pruning import run_pruning_audit, PruningMetrics

console = Console()

def prune(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Comma-separated strategies to audit. Use 'all' for everything.")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Backtest window for performance audit")] = 30,
    threshold: Annotated[float, typer.Option("--threshold", "-t",
        help="Minimum required lift over random baseline")] = 0.02,
    redundancy: Annotated[bool, typer.Option("--redundancy",
        help="Show Jaccard similarity matrix between strategy outputs")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append pruning report to this .md file")] = None,
) -> None:
    """✂️ Identify and 'hibernate' underperforming strategies."""
    print_command_summary("prune", lottery, strategies=strategies, window=window, threshold=threshold)

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    
    if strategies.lower() == "all":
        s_list = [s["name"] for s in list_strategies()]
    elif strategies.lower() == "default":
        from engine.strategies import CURATED_PRESETS
        s_list = CURATED_PRESETS.get("default", ["weighted", "markov", "bayesian"])
    else:
        s_list = [s.strip() for s in strategies.split(",")]

    with console.status(f"[bold green]Running Pruning Audit for {lottery}..."):
        from engine.modules.pruning import run_pruning_audit
        metrics = run_pruning_audit(adapter, s_list, window=window, threshold=threshold)

    if not metrics:
        console.print("[yellow]No strategies were audited. Check history length.[/yellow]")
        return

    table = Table(title=f"Pruning Audit: {adapter.rules.name}", box=None)
    table.add_column("Strategy", style="bold yellow")
    table.add_column("Lift vs Random", justify="right")
    table.add_column("Avg Rank", justify="right", style="dim")
    table.add_column("Best Hit", justify="right")
    table.add_column("Status")

    for m in metrics:
        status = "[red]PRUNE (Hibernate)[/red]" if m.is_hibernated else "[green]KEEP (Active)[/green]"
        lift_color = "green" if m.lift_over_random > 0 else "red"
        
        table.add_row(
            m.strategy_name,
            f"[{lift_color}]{m.lift_over_random*100:+.1f}%[/{lift_color}]",
            f"{m.avg_rank:.1f}",
            str(m.best_hit),
            status
        )

    console.print(table)
    
    if redundancy:
        _show_redundancy(adapter, df, [m.strategy_name for m in metrics if not m.is_hibernated])

    if any(m.is_hibernated for m in metrics):
        console.print("\n[dim]💡 Tip: Hibernated strategies are statistically indistinguishable from noise for this lottery/window.[/dim]")

    if export_md:
        _append_md_report(export_md, lottery, adapter.rules.name, window, metrics)


def _show_redundancy(adapter, df, active_names):
    if len(active_names) < 2:
        return
        
    console.print("\n[bold cyan]🕸️  Redundancy Analysis (Jaccard Similarity)[/bold cyan]")
    from engine.modules.pruning import calculate_redundancy_matrix
    from engine.strategies import get_strategy
    
    results = []
    for name in active_names:
        try:
            strat = get_strategy(name)
            res = strat.suggest(df, adapter.rules, count=10, temperature=1.0)
            results.append(res)
        except Exception:
            continue
            
    if len(results) < 2: return
    
    matrix = calculate_redundancy_matrix(results)
    
    table = Table(box=None, padding=(0, 1))
    table.add_column("Strategy", style="bold yellow")
    for name in active_names:
        table.add_column(name[:6], justify="center")
        
    for i, name in enumerate(active_names):
        row = [name]
        for j in range(len(active_names)):
            val = matrix[i, j]
            color = "red" if val > 0.4 else "yellow" if val > 0.2 else "green"
            row.append(f"[{color}]{val:.2f}[/{color}]")
        table.add_row(*row)
        
    console.print(table)
    console.print("[dim]High similarity (>0.4) indicates strategies are finding the same numbers.[/dim]")


def _append_md_report(path: str, lottery: str, game_name: str, window: int, metrics: List[PruningMetrics]) -> None:
    from pathlib import Path
    import datetime
    
    rows = ""
    for m in metrics:
        status = "PRUNE" if m.is_hibernated else "KEEP"
        rows += f"| {m.strategy_name} | {m.lift_over_random*100:+.1f}% | {m.avg_rank:.1f} | {m.best_hit} | {status} |\n"
        
    content = f"""
---
type: diagnostic
subtype: pruning-audit
date: {datetime.date.today().isoformat()}
game: {lottery}
window: {window}
---

## Pruning Audit: {game_name}

| Strategy | Lift vs Random | Avg Rank | Best Hit | Status |
|----------|----------------|----------|----------|--------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
