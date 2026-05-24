"""
Compare Strategies Command ⚖️
==============================
Side-by-side ticket comparison across all strategies in a group.

Each strategy independently generates a ticket for the current conditions.
Numbers that appear in multiple strategy tickets are highlighted (consensus).
Output includes a consensus heatmap and a merged "union ticket" sorted by
how many strategies agree.

Useful for:
  • Understanding how strategies diverge under current conditions
  • Finding numbers with strong cross-strategy agreement (low-variance picks)
  • Spotting the "always cold" numbers that every strategy avoids

Output
------
  Strategy table   one row per strategy — its ticket and how many numbers
                   overlap with each other strategy
  Consensus table  every number in the union, ranked by how many strategies
                   include it (agreement count + bar)
  Summary panel    top consensus numbers → suggested "safest" ticket

Example
-------
  lottery compare-strategies br/lotofacil
  lottery compare-strategies br/lotofacil --strategies fast
  lottery compare-strategies br/lotofacil --top 20
  lottery compare-strategies br/mega-sena --export-md cmp.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

_STRATEGY_GROUPS: dict[str, list[str]] = {
    "default":     ["weighted", "markov", "bayesian", "monte_carlo", "spectral", "cycle"],
    "fast":        ["bayesian", "weighted", "monte_carlo"],
    "statistical": ["markov", "bayesian", "weighted", "monte_carlo", "pattern",
                    "momentum", "spectral", "streak", "cycle", "harmonic",
                    "stability", "fisher"],
    "esoteric":    ["moon_phase", "solar", "noosphere", "numerology", "fibonacci"],
}

_BAR_FULL = "█"
_BAR_EMPTY = "░"


def _bar(count: int, max_count: int, width: int = 10) -> str:
    if max_count == 0:
        return _BAR_EMPTY * width
    filled = round(count / max_count * width)
    return _BAR_FULL * filled + _BAR_EMPTY * (width - filled)


def compare_strategies(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Group: default | fast | statistical | esoteric | comma-list")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window for strategy scoring")] = 50,
    top: Annotated[int, typer.Option("--top", "-N",
        help="Show top-N consensus numbers (0 = all unique numbers)")] = 0,
    temperature: Annotated[float, typer.Option("--temperature",
        help="Suggestion temperature")] = 0.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append comparison report to this .md file")] = None,
) -> None:
    """⚖️ Side-by-side ticket comparison across all strategies.

    Runs each strategy independently and highlights where they agree.
    High-agreement numbers are your engine's most consistent picks.

    Example: lottery compare-strategies br/lotofacil
             lottery compare-strategies br/lotofacil --strategies fast
             lottery compare-strategies br/lotofacil --strategies statistical --top 20
    """

    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    pick    = rules.pick_count

    if strategies in _STRATEGY_GROUPS:
        names = _STRATEGY_GROUPS[strategies]
    else:
        names = [s.strip() for s in strategies.split(",") if s.strip()]

    win_df = df.tail(window)

    # ── Run each strategy ─────────────────────────────────────────────────────
    results: dict[str, list[int]] = {}   # name → sorted ticket
    failures: list[str] = []

    with console.status("") as status:
        for name in names:
            status.update(f"[dim]Running {name}…[/dim]")
            try:
                strat = get_strategy(name)
                res   = strat.suggest(win_df, rules, count=1, temperature=temperature)
                ticket = sorted(res.tickets[0])
                results[name] = ticket
            except Exception:
                failures.append(name)

    if not results:
        console.print("[red]No strategies produced results.[/red]")
        raise typer.Exit(1)

    n_strats = len(results)

    # ── Consensus counter ─────────────────────────────────────────────────────
    freq: Counter[int] = Counter()
    for ticket in results.values():
        for n in ticket:
            freq[n] += 1

    # ── Strategy comparison table ─────────────────────────────────────────────
    strategy_table = Table(
        title=f"Strategy Tickets — {rules.name}  ({n_strats} strategies)",
        box=None, padding=(0, 1), header_style="bold",
    )
    strategy_table.add_column("Strategy",  style="bold cyan", no_wrap=True)
    strategy_table.add_column("Ticket",    justify="left")
    strategy_table.add_column("Unique",    justify="right", style="dim")
    strategy_table.add_column("Shared",    justify="right")

    # Numbers present in ALL strategies (full consensus)
    all_agree: set[int] = set.intersection(*[set(t) for t in results.values()]) if results else set()

    for name, ticket in sorted(results.items()):
        # Colour numbers by agreement level
        parts = []
        for n in ticket:
            c = freq[n]
            if c == n_strats:
                parts.append(f"[bold green]{n}[/bold green]")
            elif c >= n_strats * 0.67:
                parts.append(f"[green]{n}[/green]")
            elif c >= n_strats * 0.5:
                parts.append(f"[yellow]{n}[/yellow]")
            else:
                parts.append(f"[dim]{n}[/dim]")
        ticket_str = "  ".join(parts)

        # How many numbers are unique to this strategy?
        n_unique = sum(1 for n in ticket if freq[n] == 1)
        n_shared = pick - n_unique
        shared_fmt = (
            f"[green]{n_shared}[/green]" if n_shared >= pick * 0.75
            else f"[yellow]{n_shared}[/yellow]" if n_shared >= pick * 0.5
            else f"[dim]{n_shared}[/dim]"
        )
        strategy_table.add_row(name, ticket_str, str(n_unique), shared_fmt)

    console.print()
    console.print(strategy_table)

    # ── Consensus heatmap ─────────────────────────────────────────────────────
    all_nums = sorted(freq.keys(), key=lambda n: freq[n], reverse=True)
    display_nums = all_nums[:top] if top > 0 else all_nums
    max_freq = max(freq.values()) if freq else 1

    consensus_table = Table(
        title="Consensus Heatmap — by agreement count",
        box=None, padding=(0, 1), header_style="bold",
    )
    consensus_table.add_column("Number",    justify="center", style="bold yellow")
    consensus_table.add_column("Agree",     justify="right")
    consensus_table.add_column("Pct",       justify="right",  style="dim")
    consensus_table.add_column("Bar",       justify="left",   style="green")
    consensus_table.add_column("In all?",   justify="center")

    for num in display_nums:
        c   = freq[num]
        pct = c / n_strats * 100
        bar = _bar(c, max_freq)
        all_str = "[bold green]✔[/bold green]" if num in all_agree else "[dim]·[/dim]"
        consensus_table.add_row(str(num), f"{c}/{n_strats}", f"{pct:.0f}%", bar, all_str)

    console.print()
    console.print(consensus_table)

    # ── Summary panel ─────────────────────────────────────────────────────────
    # "Safest" ticket = top pick_count by agreement count
    top_nums = sorted(all_nums[:pick], key=lambda n: n)
    ticket_str = "  ".join(str(n) for n in top_nums)

    full_agree_count = len(all_agree)
    avg_overlap = (
        sum(
            len(set(t1) & set(t2))
            for i, (n1, t1) in enumerate(results.items())
            for j, (n2, t2) in enumerate(results.items())
            if i < j
        ) / max(1, n_strats * (n_strats - 1) / 2)
    )

    console.print()
    console.print(Panel(
        f"[bold yellow]{ticket_str}[/bold yellow]\n"
        f"[dim]Top {pick} numbers by cross-strategy agreement  ·  "
        f"{n_strats} strategies  ·  {strategies} group\n"
        f"Numbers in all strategies: {full_agree_count}/{pick}  ·  "
        f"Avg pairwise overlap: {avg_overlap:.1f} numbers[/dim]",
        title="⚖️ Consensus Ticket",
        border_style="yellow",
    ))

    if failures:
        console.print(
            f"[dim]⚠ {len(failures)} strategies failed and were excluded: "
            f"{', '.join(failures)}[/dim]"
        )

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(), results,
            freq, top_nums, all_agree, n_strats, avg_overlap, strategies,
        )
        console.print(f"[green]✔ Comparison report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    results: dict[str, list[int]], freq: Counter, top_nums: list[int],
    all_agree: set[int], n_strats: int, avg_overlap: float,
    group: str,
) -> None:
    ticket_str = ", ".join(str(n) for n in top_nums)

    # Strategy rows
    strat_rows = ""
    for name, ticket in sorted(results.items()):
        strat_rows += f"| {name} | {' '.join(str(n) for n in ticket)} |\n"

    # Consensus rows (top 20)
    all_nums = sorted(freq.keys(), key=lambda n: freq[n], reverse=True)
    cons_rows = ""
    for num in all_nums[:20]:
        c = freq[num]
        pct = c / n_strats * 100
        flag = "✓" if num in all_agree else ""
        cons_rows += f"| **{num}** | {c}/{n_strats} | {pct:.0f}% | {flag} |\n"

    content = f"""
---
type: diagnostic
subtype: compare-strategies
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
strategies_group: {group}
n_strategies: {n_strats}
full_consensus_count: {len(all_agree)}
avg_pairwise_overlap: {avg_overlap:.2f}
consensus_ticket: [{ticket_str}]
---

## Strategy Comparison: {game_name} ({today.isoformat()})

**Group:** {group}  ·  **Strategies:** {n_strats}
**Avg overlap:** {avg_overlap:.1f} numbers  ·  **Full consensus:** {len(all_agree)} numbers

### Strategy Tickets

| Strategy | Ticket |
|----------|--------|
{strat_rows}
### Consensus Heatmap (top 20)

| Number | Agreement | % | All? |
|--------|-----------|---|------|
{cons_rows}
**Consensus Ticket:** {ticket_str}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
