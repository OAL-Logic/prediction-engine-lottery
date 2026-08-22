"""
Backtest Command 🔬
==================
Evaluate one or more strategies against one or more historical draws.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.markup import escape

from engine.cli.utils import get_adapter, print_command_summary
from engine.services.backtest import BacktestResult, DrawResult, UnknownStrategyError, run_backtest

console = Console()

def backtest(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draw_id: Annotated[Optional[str], typer.Argument(help="Draw number(s), range (e.g. 2990-2999), or comma-separated list to test")] = None,
    prev:    Annotated[Optional[str], typer.Option("--prev", "-p", help="Relative index or range (e.g. 1, 1-5, 1,2,5) from latest")] = None,
    strategy: Annotated[Optional[str], typer.Option("--strategy", "-s",
                     help="Strategy name(s). Supports comma-separated list (e.g. 'weighted,markov') or 'all'.")] = None,
    numbers: Annotated[Optional[str], typer.Option("--numbers", "-n", help="Specific numbers to check against the draw. E.g. '4 12 23 35 47 60'")] = None,
    count: Annotated[int, typer.Option("--count", "-c", help="Number of tickets to generate (if using --strategy)")] = 1,
    temperature: Annotated[float, typer.Option("--temp", "-t", help="Sampling temperature (if using --strategy)")] = 0.0,
    limit: Annotated[Optional[int], typer.Option("--limit", "-L", help="History limit (recency bias): only use the most recent N draws for scoring")] = None,
    summary: Annotated[bool, typer.Option("--summary/--no-summary", help="Show a summary report at the end when testing multiple draws")] = True,
    show_map: Annotated[bool, typer.Option("--map", "-m", help="Show board heatmap for each target draw")] = False,
    config: Annotated[Optional[Path], typer.Option("--config", help="Path to a YAML configuration file for batch strategy testing")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append backtest report to this .md file")] = None,
) -> None:
    """
    🔬 Evaluate one or more strategies against one or more historical draws.

    This command performs \"blind\" testing: if you choose strategies, it only
    gives them access to draws that happened BEFORE the one you are testing.
    Supports multiple strategies (comma-separated), IDs, and ranges.
    """
    if draw_id is None and prev is None:
        raise typer.BadParameter("Provide either DRAW_ID(s) or use --prev/-p. Run 'lottery backtest --help' for examples.")

    # Resolve strategy names + per-strategy kwargs (config YAML stays a CLI-only concern)
    strategy_names: list[str] = []
    strategy_kwargs: dict[str, dict] = {}

    if config and config.exists():
        import yaml
        try:
            with open(config, "r") as f:
                config_payload = yaml.safe_load(f)
            if isinstance(config_payload, list):
                entries = config_payload
            elif isinstance(config_payload, dict) and "strategies" in config_payload:
                entries = config_payload["strategies"]
            else:
                entries = []
            strategy_names = [e["name"] for e in entries if "name" in e]
            strategy_kwargs = {e["name"]: e.get("params", {}) for e in entries if "name" in e}
        except Exception as exc:
            console.print(f"[red]Failed to load config: {exc}[/red]")
            raise typer.Exit(1)

    if not strategy_names:
        if strategy:
            strategy_names = ["all"] if strategy.lower() == "all" else [s.strip() for s in strategy.split(",")]
        else:
            strategy_names = ["weighted"]

    print_command_summary("backtest", lottery, strategy=strategy, count=count, temp=temperature, limit=limit)

    game_name = get_adapter(lottery).rules.name

    def _on_draw(draw: DrawResult) -> None:
        console.rule(f"[bold cyan]BACKTEST — {game_name} Draw {draw.draw_id} ({draw.date})[/bold cyan]")
        console.print(f"  [bold]Winning Numbers:[/bold] [green]{escape(str(draw.winning_numbers))}[/green]\n")
        for s_name in draw.attempted_strategies:
            console.print(f"\n[bold]Simulating strategy:[/bold] [cyan]{s_name}[/cyan]")
            if s_name in draw.errors:
                console.print(f"[red]Failed: {draw.errors[s_name]}[/red]")
                continue
            data = draw.strategies[s_name]
            console.print(f"  [dim]Result:[/dim] Avg Rank: [bold]{data.avg_rank:.1f}[/bold] | Top-N Hits: [bold]{data.top_n}[/bold] | Ticket Hits: [bold]{data.hits}[/bold]")

    try:
        result = run_backtest(
            lottery=lottery,
            draw_id=draw_id,
            prev=prev,
            strategy_names=strategy_names,
            strategy_kwargs=strategy_kwargs,
            count=count,
            temperature=temperature,
            limit=limit,
            on_draw=_on_draw,
        )
    except UnknownStrategyError as exc:
        console.print(f"[red]✗ {exc} Run 'lottery strategies' for available options.[/red]")
        raise typer.Exit(1)
    except ValueError as exc:
        console.print(f"[red]✗ {exc}[/red]")
        raise typer.Exit(1)

    if summary and result.summary:
        summary_table = Table(title="BACKTEST COMPARISON SUMMARY", header_style="bold cyan")
        summary_table.add_column("Strategy", style="cyan")
        summary_table.add_column("Avg Rank", justify="right")
        summary_table.add_column("Top-N Capture", justify="right")
        summary_table.add_column("Best Hit", justify="right")
        summary_table.add_column("Win Rate", justify="right")

        for s_name in result.strategy_names:
            s = result.summary.get(s_name)
            if s is None:
                continue
            summary_table.add_row(
                s_name, f"{s.avg_rank:.1f}", f"{s.top_n_capture} ({s.capture_pct:.1f}%)",
                str(s.best_hit), f"{s.win_rate_pct:.1f}%",
            )
        console.print(summary_table)

    if export_md and result.draws:
        _append_md_backtest(export_md, result)
        console.print(f"[green]✔ Backtest report appended to {export_md}[/green]")


def _append_md_backtest(path: str, result: BacktestResult) -> None:
    today = date.today().isoformat()
    draws_tested = len(result.draws)

    rows = ""
    for s_name in result.strategy_names:
        s = result.summary.get(s_name)
        if s is None:
            continue
        rows += f"| {s_name} | {s.avg_rank:.1f} | {s.top_n_capture} ({s.capture_pct:.1f}%) | {s.best_hit} | {s.win_rate_pct:.1f}% |\n"

    content = f"""
---
type: diagnostic
subtype: backtest
date: {today}
game: {result.lottery}
game_name: {result.game_name}
strategies: "{', '.join(result.strategy_names)}"
draws_tested: {draws_tested}
tags: [prediction-engine, backtest, evaluation, pattern-log]
---

## Backtest: {result.game_name} ({today})

**Strategies:** {', '.join(result.strategy_names)}  ·  **Draws tested:** {draws_tested}

| Strategy | Avg Rank | Top-N Capture | Best Hit | Win Rate |
|----------|----------|---------------|----------|----------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
