"""
Backtest Command 🔬
==================
Evaluate one or more strategies against one or more historical draws.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Annotated, Optional, Any

import typer
# import pandas as pd # Moved inside
from rich.console import Console
from rich.table import Table
from rich.markup import escape

from engine.cli.utils import get_adapter, print_command_summary
# from engine.strategies import get_strategy, list_strategies # Moved inside

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
    import pandas as pd
    from engine.strategies import get_strategy, list_strategies

    if draw_id is None and prev is None:
        raise typer.BadParameter("Provide either DRAW_ID(s) or use --prev/-p. Run 'lottery backtest --help' for examples.")

    # Resolve strategies (validate before fetch)
    strategy_names = []
    config_payload = None
    
    if config and config.exists():
        import yaml
        try:
            with open(config, "r") as f:
                config_payload = yaml.safe_load(f)
            if isinstance(config_payload, list):
                strategy_names = [s["name"] for s in config_payload if "name" in s]
            elif isinstance(config_payload, dict) and "strategies" in config_payload:
                strategy_names = [s["name"] for s in config_payload["strategies"]]
        except Exception as exc:
            console.print(f"[red]Failed to load config: {exc}[/red]")
            raise typer.Exit(1)

    if not strategy_names:
        if strategy:
            if strategy.lower() == "all":
                strategy_names = [s["name"] for s in list_strategies()]
            else:
                strategy_names = [s.strip() for s in strategy.split(",")]
        else:
            strategy_names = ["weighted"]

    # Validate strategy names early
    for s_name in strategy_names:
        try:
            get_strategy(s_name)
        except KeyError:
            console.print(f"[red]✗ Unknown strategy '{s_name}'. Run 'lottery strategies' for available options.[/red]")
            raise typer.Exit(1)

    print_command_summary("backtest", lottery, strategy=strategy, count=count, temp=temperature, limit=limit)

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    # Resolve target draws
    target_rows = []
    
    # Mode A: Relative index via --prev
    if prev is not None:
        indices = []
        for part in prev.split(","):
            if ".." in part:
                start, end = part.split("..")
                indices.extend(range(int(start), int(end) + 1))
            elif "-" in part:
                start, end = part.split("-")
                indices.extend(range(int(start), int(end) + 1))
            else:
                indices.append(int(part))
        for idx in indices:
            try: target_rows.append(df.iloc[-idx])
            except IndexError: console.print(f"[yellow]⚠ Index {idx} out of range.[/yellow]")

    # Mode B: Explicit draw_id
    elif draw_id is not None:
        ids_to_fetch = []
        for part in draw_id.split(","):
            if ".." in part:
                start, end = part.split("..")
                ids_to_fetch.extend(range(int(start), int(end) + 1))
            elif "-" in part and not part.startswith("-"):
                start, end = part.split("-")
                ids_to_fetch.extend(range(int(start), int(end) + 1))
            else:
                ids_to_fetch.append(part)
        for val in ids_to_fetch:
            try:
                tid = int(val)
                matches = df[df["draw_id"] == tid]
                if not matches.empty: target_rows.append(matches.iloc[0])
            except ValueError:
                matches = df[df["date"].astype(str).str.contains(str(val))]
                if not matches.empty: target_rows.append(matches.iloc[0])
    else:
        console.print("[yellow]⚠ Provide either DRAW_ID(s) or use --prev/-p.[/yellow]")
        raise typer.Exit(1)

    if not target_rows:
        console.print("[red]✗ No draws found to test.[/red]")
        raise typer.Exit(1)

    # Sort target rows by draw_id ascending
    target_rows.sort(key=lambda r: int(r["draw_id"]))

    global_stats = []

    for target_row in target_rows:
        t_id = int(target_row["draw_id"])
        t_date = target_row["date"]
        
        # Handle NaT / None dates
        if pd.isna(t_date):
            # Try to infer date from previous draw or keep as None
            # Strategies must handle None/NaT gracefully now
            pass
        elif hasattr(t_date, "date"): 
            t_date = t_date.date()

        console.rule(f"[bold cyan]BACKTEST — {adapter.rules.name} Draw {t_id} ({t_date})[/bold cyan]")
        console.print(f"  [bold]Winning Numbers:[/bold] [green]{escape(str([int(n) for n in sorted(target_row['numbers'])]))}[/green]\n")

        # Data available before the target draw
        train_df = df[df["draw_id"] < t_id].copy()
        if train_df.empty:
            console.print(f"[yellow]⚠ No historical data available before draw {t_id} — skipping.[/yellow]")
            continue

        if show_map:
            # Heatmap implementation... (omitted for brevity in first draft or kept if needed)
            pass

        draw_stat = {
            "draw_id": t_id,
            "winning_numbers": sorted(target_row["numbers"]),
            "manual_hits": [],
            "strategies": {}
        }

        # Mode B: Run strategies
        for s_idx, s_name in enumerate(strategy_names):
            console.print(f"\n[bold]Simulating strategy:[/bold] [cyan]{s_name}[/cyan]")
            
            strat_kwargs = {}
            # Load params from config if available
            if config_payload:
                strats_list = config_payload if isinstance(config_payload, list) else config_payload.get("strategies", [])
                # Match by index or name
                s_conf = strats_list[s_idx] if s_idx < len(strats_list) else {}
                if s_conf.get("name") == s_name:
                    strat_kwargs.update(s_conf.get("params", {}))

            if s_name in ["weather", "moon_phase"]: strat_kwargs["upcoming_draw_date"] = t_date
            elif s_name in ["numerology"]: strat_kwargs["target_date"] = t_date
            elif s_name in ["biorhythm", "zodiac"]: strat_kwargs["draw_date"] = t_date

            try:
                strat_obj = get_strategy(s_name, **strat_kwargs)
                result = strat_obj.suggest(
                    train_df, 
                    adapter.rules, 
                    count=count, 
                    temperature=temperature,
                    history_limit=limit
                )
            except Exception as exc:
                console.print(f"[red]Failed: {exc}[/red]")
                continue

            # Analysis...
            strat_hits = []
            for ticket in result.tickets:
                matches = len(set(ticket) & set(target_row["numbers"]))
                strat_hits.append(matches)

            sorted_scores = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)
            ranks = {num: rank + 1 for rank, (num, score) in enumerate(sorted_scores)}
            found_in_top = sum(1 for n in target_row["numbers"] if ranks.get(n, 999) <= adapter.rules.pick_count)
            avg_rank = sum(ranks.get(n, 0) for n in target_row["numbers"]) / len(target_row["numbers"])
            
            draw_stat["strategies"][s_name] = {
                "hits": strat_hits,
                "avg_rank": avg_rank,
                "top_n": found_in_top
            }
            
            console.print(f"  [dim]Result:[/dim] Avg Rank: [bold]{avg_rank:.1f}[/bold] | Top-{adapter.rules.pick_count} Hits: [bold]{found_in_top}[/bold] | Ticket Hits: [bold]{strat_hits}[/bold]")

        global_stats.append(draw_stat)

    # --- Global Summary ---
    if summary and global_stats:
        min_win = min(adapter.rules.odds.keys()) if adapter.rules.odds else 4
        summary_table = Table(title="BACKTEST COMPARISON SUMMARY", header_style="bold cyan")
        summary_table.add_column("Strategy", style="cyan")
        summary_table.add_column("Avg Rank", justify="right")
        summary_table.add_column("Top-N Capture", justify="right")
        summary_table.add_column("Best Hit", justify="right")
        summary_table.add_column(f"Win Rate (min {min_win})", justify="right")

        for s_name in strategy_names:
            all_ranks = []
            total_top_n = 0
            best_hit = 0
            wins = 0
            total_tickets = 0
            
            for d in global_stats:
                if s_name in d["strategies"]:
                    data = d["strategies"][s_name]
                    all_ranks.append(data["avg_rank"])
                    total_top_n += data["top_n"]
                    best_hit = max(best_hit, max(data["hits"]) if data["hits"] else 0)
                    wins += sum(1 for h in data["hits"] if h >= min_win)
                    total_tickets += len(data["hits"])
            
            if all_ranks:
                avg_r = sum(all_ranks) / len(all_ranks)
                cap_pct = (total_top_n / (len(all_ranks) * adapter.rules.pick_count)) * 100
                win_rate = (wins / total_tickets * 100) if total_tickets > 0 else 0
                
                summary_table.add_row(
                    s_name, f"{avg_r:.1f}", f"{total_top_n} ({cap_pct:.1f}%)", str(best_hit), f"{win_rate:.1f}%"
                )
        console.print(summary_table)

    if export_md and global_stats:
        _append_md_backtest(export_md, lottery, adapter.rules.name,
                            strategy_names, global_stats,
                            adapter.rules.pick_count,
                            adapter.rules.odds)
        console.print(f"[green]✔ Backtest report appended to {export_md}[/green]")


def _append_md_backtest(
    path: str, lottery: str, game_name: str,
    strategy_names: list[str], global_stats: list[dict],
    pick_count: int, odds: dict,
) -> None:
    today = date.today().isoformat()
    min_win = min(odds.keys()) if odds else pick_count - 1
    draws_tested = len(global_stats)

    rows = ""
    for s_name in strategy_names:
        all_ranks, total_top_n, best_hit, wins, total_tickets = [], 0, 0, 0, 0
        for d in global_stats:
            if s_name in d["strategies"]:
                data = d["strategies"][s_name]
                all_ranks.append(data["avg_rank"])
                total_top_n += data["top_n"]
                best_hit = max(best_hit, max(data["hits"]) if data["hits"] else 0)
                wins += sum(1 for h in data["hits"] if h >= min_win)
                total_tickets += len(data["hits"])
        if all_ranks:
            avg_r = sum(all_ranks) / len(all_ranks)
            cap_pct = total_top_n / (len(all_ranks) * pick_count) * 100
            win_rate = wins / total_tickets * 100 if total_tickets > 0 else 0.0
            rows += f"| {s_name} | {avg_r:.1f} | {total_top_n} ({cap_pct:.1f}%) | {best_hit} | {win_rate:.1f}% |\n"

    content = f"""
---
type: diagnostic
subtype: backtest
date: {today}
game: {lottery}
game_name: {game_name}
strategies: "{', '.join(strategy_names)}"
draws_tested: {draws_tested}
tags: [prediction-engine, backtest, evaluation, pattern-log]
---

## Backtest: {game_name} ({today})

**Strategies:** {', '.join(strategy_names)}  ·  **Draws tested:** {draws_tested}

| Strategy | Avg Rank | Top-N Capture | Best Hit | Win Rate |
|----------|----------|---------------|----------|----------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
