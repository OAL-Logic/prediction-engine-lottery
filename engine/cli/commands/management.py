"""
Management Commands 🛠️
======================
Administrative, secondary analytical, and strategy optimization commands.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Annotated, Optional, Any

import typer
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from engine.cli.utils import get_adapter, print_command_summary
from engine.strategies import get_strategy, list_strategies

console = Console()

# ── Historical Data ──────────────────────────────────────────────────────────

def history(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    limit: Annotated[int, typer.Option("--limit", "-L", help="Number of draws to show")] = 10,
) -> None:
    """📅 Chronological Draw Navigator — browse previous results."""
    adapter = get_adapter(lottery)
    df = adapter.fetch().tail(limit)
    
    table = Table(title=f"Draw History: {adapter.rules.name}", box=None)
    table.add_column("Draw ID", justify="right", style="cyan")
    table.add_column("Date", style="dim")
    table.add_column("Winning Numbers", style="bold green")
    table.add_column("Sum", justify="right")
    
    for _, row in df.iterrows():
        table.add_row(
            str(row["draw_id"]),
            str(row["date"])[:10],
            str(sorted(row["numbers"])),
            str(sum(row["numbers"]))
        )
    console.print(table)


def audit_data(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
) -> None:
    """🔍 Audit the integrity of cached data for a lottery."""
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    
    console.rule(f"[bold cyan]Data Audit: {adapter.rules.name}[/bold cyan]")
    
    # Continuity check
    ids = df["draw_id"].sort_values()
    diffs = ids.diff().dropna()
    gaps = diffs[diffs != 1]
    if gaps.empty:
        console.print(f"  [green]✓[/green] Draw Continuity: {len(df)} sequential draws.")
    else:
        console.print(f"  [red]✗[/red] Gaps detected in sequence: {len(gaps)} missing links.")
        
    # Anomaly Dashboard
    from engine.modules import frequency
    f_res = frequency.analyze(df, adapter.rules)
    console.print(f"\n  Statistical Anomaly Dashboard (Z-Scores):")
    console.print(f"    - Global Freq:  Chi2: {f_res.chi2_statistic:.2f} (p={f_res.chi2_p_value:.4f})")
    
    # Atmospheric Physics Layer
    console.print("\n  [bold dim]Atmospheric Physics Layer:[/bold dim]")
    try:
        from engine.strategies.fun.weather import WeatherStrategy
        country = "br" if "br" in lottery else "us"
        w_strat = WeatherStrategy(country_hint=country)
        w_data = w_strat._fetch_upcoming_weather()
        p = w_data.get("surface_pressure_mean")
        t = w_data.get("temperature_2m_mean")
        if p and t is not None:
            n_idx = 77.6 * (p / (t + 273.15))
            console.print(f"    - Refractive Index (N): [green]{n_idx:.2f}[/green] [dim](Dielectric state: {'High' if n_idx > 300 else 'Low'} Charge Potential)[/dim]")
        else:
            console.print("    - Refractive Index (N): [yellow]Weather data unavailable[/yellow]")
    except Exception as e:
        console.print(f"    - Refractive Index (N): [red]Error calculating physics ({e})[/red]")


def export(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    format:  Annotated[str, typer.Option("--format", "-f", help="json | csv")] = "json",
    output:  Annotated[Optional[str], typer.Option("--output", "-o", help="Output filename")] = None,
    console_out: Annotated[bool, typer.Option("--console", "-c", help="Print output to console instead of file")] = False,
) -> None:
    """📤 Export draw history to JSON or CSV."""
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    
    if console_out:
        if format == "json":
            print(df.to_json(orient="records", date_format="iso", indent=2))
        elif format == "csv":
            print(df.to_csv(index=False))
        return

    filename = output or f"export_{lottery.replace('/', '_')}.{format}"
    if format == "json":
        df.to_json(filename, orient="records", date_format="iso", indent=2)
    elif format == "csv":
        df.to_csv(filename, index=False)
        
    console.print(f"[green]✓[/green] Exported {len(df)} draws to {filename}")


# ── Betting & Simulation ─────────────────────────────────────────────────────

def compare_bets(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    numbers: Annotated[str, typer.Argument(help="Space or comma-separated numbers")],
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Check against last N draws")] = 100,
) -> None:
    """⚖️ Compare your set of numbers against historical draws."""
    adapter = get_adapter(lottery)
    df = adapter.fetch().tail(limit)
    my_nums = set(int(n) for n in numbers.replace(",", " ").split())
    
    table = Table(title=f"Performance Audit: {sorted(list(my_nums))}")
    table.add_column("Draw ID", justify="right")
    table.add_column("Date")
    table.add_column("Matches", justify="center", style="bold yellow")
    
    hits = {i: 0 for i in range(len(my_nums) + 1)}
    
    for _, row in df.iterrows():
        matches = len(my_nums & set(row["numbers"]))
        hits[matches] += 1
        if matches >= 3:
            table.add_row(str(row["draw_id"]), str(row["date"])[:10], f"{matches} hits")
            
    console.print(table)
    console.print("\n[bold]Summary Table:[/bold]")
    for m in sorted(hits.keys(), reverse=True):
        if hits[m] > 0 or m >= 3:
            console.print(f"  {m}-match: {hits[m]} times")


def simulate(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    numbers: Annotated[str, typer.Argument(help="Space or comma-separated numbers")],
    range_str: Annotated[str, typer.Option("--range", "-r", help="Draw ID range (e.g. 1000-2000) or 'all'")] = "all",
) -> None:
    """🎮 Run a high-fidelity historical simulation of a specific ticket."""
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    my_nums = set(int(n) for n in numbers.replace(",", " ").split())
    
    if range_str != "all":
        start, end = map(int, range_str.split("-"))
        df = df[(df["draw_id"] >= start) & (df["draw_id"] <= end)]
        
    console.rule(f"[bold cyan]Historical Simulation: {adapter.rules.name}[/bold cyan]")
    console.print(f"  [dim]Numbers: {sorted(list(my_nums))}[/dim]")
    console.print(f"  [dim]Window: {len(df)} draws[/dim]\n")
    
    hits = Counter()
    for _, row in df.iterrows():
        matches = len(my_nums & set(row["numbers"]))
        hits[matches] += 1
        
    table = Table(title="Prize Distribution", box=None)
    table.add_column("Tier", style="bold")
    table.add_column("Frequency", justify="right")
    table.add_column("Chart", width=40)
    
    max_h = max(hits.values()) if hits else 1
    for m in sorted(hits.keys(), reverse=True):
        if m < 2: continue
        bar = int((hits[m] / max_h) * 35)
        color = "green" if m >= adapter.rules.pick_count - 2 else "yellow"
        table.add_row(f"{m}-match", str(hits[m]), f"[{color}]{'█' * bar}[/{color}]")
        
    console.print(table)


def wheel(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    pool: Annotated[Optional[str], typer.Option("--pool", "-p", help="Space/comma-separated list of numbers to wheel")] = None,
    mode: Annotated[str, typer.Option("--mode", "-m", help="Wheel type: full | key | abbreviated")] = "full",
    keys: Annotated[Optional[str], typer.Option("--keys", "-k", help="Numbers that MUST appear in every ticket (for key mode)")] = None,
    guarantee: Annotated[int, typer.Option("--guarantee", "-g", help="Match guarantee (e.g. 4 for '4 if 6')")] = 4,
    test: Annotated[Optional[str], typer.Option("--test", help="Evaluate wheel against these winning numbers")] = None,
    preset: Annotated[Optional[str], typer.Option("--preset", help="Use a predefined number pool (e.g. 'hot-10', 'overdue-12')")] = None,
) -> None:
    """🎡 Generate combinatorial wheels for a pool of numbers."""
    from engine.wheels import generate_full_wheel, generate_key_wheel, generate_abbreviated_wheel, evaluate_prizes
    
    if not pool and not preset:
        console.print("[red]✗ Pool is required. Use --pool or --preset.[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    rules = adapter.rules
    
    # Resolve numbers
    if preset:
        from engine.modules import frequency
        df = adapter.fetch()
        f_res = frequency.analyze(df, rules)
        if preset == "hot-10":
            nums = f_res.hot[:10]
        elif preset == "overdue-12":
            from engine.modules import tendency
            t_res = tendency.analyze_numbers(df, list(range(rules.number_range[0], rules.number_range[1]+1)))
            nums = [s.number for s in sorted(t_res.stats, key=lambda x: x.delay, reverse=True)[:12]]
        else:
            console.print(f"[red]Unknown preset: {preset}[/red]")
            raise typer.Exit(1)
    else:
        nums = sorted(int(n) for n in pool.replace(",", " ").split())

    # Key numbers
    key_nums = []
    if keys:
        key_nums = [int(n) for n in keys.replace(",", " ").split()]

    console.rule(f"[bold cyan]Lottery Wheel: {rules.name}[/bold cyan]")
    console.print(f"  [dim]Pool: {nums} ({len(nums)} numbers)[/dim]")
    console.print(f"  [dim]Mode: {mode} (Guarantee: {guarantee})[/dim]\n")

    tickets = []
    if mode == "full":
        tickets = generate_full_wheel(nums, rules.pick_count)
    elif mode == "key":
        tickets = generate_key_wheel(nums, key_nums, rules.pick_count)
    elif mode == "abbreviated":
        tickets = generate_abbreviated_wheel(nums, rules.pick_count, guarantee)

    for i, t in enumerate(tickets[:20]):
        console.print(f"  Ticket {i+1:2}: {sorted(t)}")
    
    if len(tickets) > 20:
        console.print(f"  [dim]... and {len(tickets)-20} more tickets.[/dim]")

    console.print(f"\n  [bold green]Total tickets: {len(tickets)}[/bold green]")
    console.print(f"  [dim]Estimated cost: {rules.currency} {len(tickets) * rules.ticket_price:.2f}[/dim]")

    if test:
        win_nums = set(int(n) for n in test.replace(",", " ").split())
        prizes = evaluate_prizes(tickets, win_nums, rules)
        console.print("\n[bold]Test Results:[/bold]")
        for match, count in sorted(prizes.items(), reverse=True):
            if count > 0:
                console.print(f"  {match}-match: {count} tickets")


def savings(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    pool_size: Annotated[int, typer.Option("--pool", "-p", help="Size of your candidate pool")],
) -> None:
    """💰 Wheel Savings Calculator — compare the cost of a wheel vs. a full large bet."""
    adapter = get_adapter(lottery)
    rules = adapter.rules
    price = rules.ticket_price
    
    giant_count = math.comb(pool_size, rules.pick_count)
    giant_cost = giant_count * price
    est_wheel_count = pool_size * 2
    est_wheel_cost = est_wheel_count * price
    
    console.print(f"\n  [bold cyan]Savings Analysis: {rules.name}[/bold cyan]")
    table = Table(box=None)
    table.add_column("Method")
    table.add_column("Tickets", justify="right")
    table.add_column("Total Cost", justify="right", style="bold green")
    table.add_row("Single Giant Bet", f"{giant_count:,}", f"{giant_cost:,.2f} {rules.currency}")
    table.add_row("Wheeled Coverage (est)", f"{est_wheel_count:,}", f"{est_wheel_cost:,.2f} {rules.currency}")
    console.print(table)


# ── Optimization ─────────────────────────────────────────────────────────────

def optimize(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Comma-separated strategies to test. Use 'all' for everything.")] = "weighted,markov,momentum",
    limits: Annotated[str, typer.Option("--limits", "-L", help="Comma-separated history limits to test (e.g. '50,100,200')")] = "50,100,200",
    temps: Annotated[str, typer.Option("--temps", "-t", help="Comma-separated temperatures to test (e.g. '0.0,0.5')")] = "0.0",
    prev: Annotated[str, typer.Option("--prev", "-p", help="Range of draws to use for validation (e.g. '1-10')")] = "1-10",
    top_n: Annotated[int, typer.Option("--top-n", help="Number of top picks to check for capture rate")] = None,
) -> None:
    """⚙️ Search for the best strategy configuration."""
    from itertools import product
    print_command_summary("optimize", lottery, strategies=strategies, limits=limits, temps=temps, prev=prev)

    adapter = get_adapter(lottery)
    df = adapter.fetch()

    s_list = [s["name"] for s in list_strategies()] if strategies.lower() == "all" else [s.strip() for s in strategies.split(",")]
    l_list = [int(l.strip()) for l in limits.split(",")]
    t_list = [float(t.strip()) for t in temps.split(",")]

    start_p, end_p = map(int, prev.split("-")) if "-" in prev else (int(prev), int(prev))
    validation_indices = list(range(start_p, end_p + 1))
    target_top_n = top_n or adapter.rules.pick_count

    grid = list(product(s_list, l_list, t_list))
    results = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), MofNCompleteColumn(), transient=True) as progress:
        task = progress.add_task("[cyan]Grid Searching...", total=len(grid))
        for s_name, limit, temp in grid:
            progress.update(task, description=f"[cyan]Testing {s_name} (L={limit}, T={temp})")
            total_winners, captured_winners, ranks = 0, 0, []
            for p_idx in validation_indices:
                try:
                    target_row = df.iloc[-p_idx]
                    t_id, t_date = int(target_row["draw_id"]), target_row["date"]
                    if hasattr(t_date, "date"): t_date = t_date.date()
                    train_df = df[df["draw_id"] < t_id].copy()
                    if train_df.empty: continue
                    
                    strat_kwargs = {}
                    if s_name in ["weather", "moon_phase"]: strat_kwargs["upcoming_draw_date"] = t_date
                    elif s_name in ["numerology"]: strat_kwargs["target_date"] = t_date
                    elif s_name in ["biorhythm", "zodiac"]: strat_kwargs["draw_date"] = t_date
                    
                    strat_obj = get_strategy(s_name, **strat_kwargs)
                    res = strat_obj.suggest(train_df, adapter.rules, count=1, temperature=temp, history_limit=limit)
                    sorted_scores = sorted(res.scores.items(), key=lambda x: x[1], reverse=True)
                    num_ranks = {num: rank + 1 for rank, (num, score) in enumerate(sorted_scores)}
                    draw_ranks = [num_ranks.get(n, 999) for n in target_row["numbers"]]
                    ranks.extend(draw_ranks)
                    captured_winners += sum(1 for r in draw_ranks if r <= target_top_n)
                    total_winners += len(target_row["numbers"])
                except Exception:
                    continue
            
            if total_winners > 0:
                results.append({
                    "strategy": s_name, 
                    "limit": limit, 
                    "temp": temp, 
                    "capture_rate": (captured_winners / total_winners) * 100, 
                    "avg_rank": sum(ranks) / len(ranks)
                })
            progress.advance(task)

    results.sort(key=lambda x: x["capture_rate"], reverse=True)
    
    table = Table(title=f"Optimization Leaderboard: {adapter.rules.name} (Top-{target_top_n} Capture)", header_style="bold cyan")
    table.add_column("Rank", justify="right", style="dim")
    table.add_column("Strategy", style="bold yellow")
    table.add_column("Limit", justify="right")
    table.add_column("Temp", justify="right")
    table.add_column("Capture Rate", justify="right", style="bold green")
    table.add_column("Avg Rank", justify="right")

    for i, res in enumerate(results[:20]):
        table.add_row(
            str(i+1),
            res["strategy"],
            str(res["limit"]),
            f"{res['temp']:.1f}",
            f"{res['capture_rate']:.1f}%",
            f"{res['avg_rank']:.1f}"
        )
    
    console.print(table)
    console.print(f"\n[dim]Grid search covered {len(grid)} combinations over {len(validation_indices)} draws.[/dim]")
