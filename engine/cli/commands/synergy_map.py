"""
Synergy Map Command 🕸️
=====================
Pairwise co-occurrence lift matrix for a given ticket.

For a ticket of N numbers, computes the co-occurrence lift for every
pair (i, j) within the ticket:
  observed = draws containing both i and j
  expected = draws × P(i) × P(j)
  lift     = observed / expected

Lift > 1.0 → these numbers appear together more than chance
Lift < 1.0 → these numbers tend to avoid each other (repellent)

The output is an upper-triangle matrix rendered as a Rich table, plus:
  • Best pair    — highest-lift pair in the ticket
  • Worst pair   — lowest-lift pair (most repellent)
  • Mean synergy — average lift across all C(N,2) pairs
  • Ticket score — composite synergy score (geometric mean of all lifts)

Useful for:
  • Finding the hidden pair synergy in your selected ticket
  • Understanding which numbers in your ticket "clash"
  • Post-session review: did your forecast ticket have internal synergy?

Example
-------
  lottery synergy-map br/lotofacil "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
  lottery synergy-map br/lotofacil "1 7 14 21 28" --draws 200
  lottery synergy-map br/mega-sena "3 12 28 37 41 55" --export-md syn.md
"""

from __future__ import annotations

import math
import sys
from collections import Counter
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.cli.utils import get_adapter

console = Console()


def synergy_map(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    ticket:  Annotated[Optional[str], typer.Argument(
        help="Space-separated ticket numbers (quoted). Omit when using --from-stdin.")] = None,
    draws:   Annotated[int, typer.Option("--draws", "-n",
        help="Number of recent draws to analyse")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append synergy report to this .md file")] = None,
    from_stdin: Annotated[bool, typer.Option("--from-stdin",
        help="Read ticket numbers from stdin (enables piping from 'picks --raw')")] = False,
) -> None:
    """🕸️ Pairwise co-occurrence lift matrix for a given ticket.

    Shows which number pairs in your ticket have historically appeared
    together more (synergistic) or less (repellent) than expected.

    Example: lottery synergy-map br/lotofacil "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
             lottery picks br/lotofacil --raw | lottery synergy-map br/lotofacil --from-stdin
    """
    if from_stdin:
        ticket = sys.stdin.read().strip()
    if not ticket:
        console.print("[red]Provide a ticket argument or use --from-stdin.[/red]")
        raise typer.Exit(1)

    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pick     = rules.pick_count
    pool_sz  = hi - lo + 1

    # Parse ticket
    try:
        t_nums = sorted(int(x) for x in ticket.split() if x.isdigit())
    except ValueError:
        console.print("[red]Invalid ticket — could not parse numbers.[/red]")
        raise typer.Exit(1)

    bad = [n for n in t_nums if not (lo <= n <= hi)]
    if bad:
        console.print(f"[red]Numbers out of range [{lo},{hi}]: {bad}[/red]")
        raise typer.Exit(1)

    if len(t_nums) < 2:
        console.print("[dim]Need at least 2 numbers to build a synergy map.[/dim]")
        raise typer.Exit(0)

    n_draws  = min(draws, len(df))
    window   = df.tail(n_draws)
    all_rows = list(window.itertuples())

    # ── Frequency and co-occurrence counts ─────────────────────────────────
    freq: Counter[int] = Counter()
    co:   Counter[tuple] = Counter()

    for row in all_rows:
        nums_set = set(row.numbers)
        for n in t_nums:
            if n in nums_set:
                freq[n] += 1
        # Only count pairs within the ticket
        t_in_draw = [n for n in t_nums if n in nums_set]
        for i in range(len(t_in_draw)):
            for j in range(i + 1, len(t_in_draw)):
                co[(t_in_draw[i], t_in_draw[j])] += 1

    # ── Compute lifts ───────────────────────────────────────────────────────
    lift_matrix: dict[tuple, float] = {}
    for i_idx in range(len(t_nums)):
        for j_idx in range(i_idx + 1, len(t_nums)):
            a, b    = t_nums[i_idx], t_nums[j_idx]
            obs     = co.get((a, b), 0)
            p_a     = freq[a] / n_draws
            p_b     = freq[b] / n_draws
            exp     = n_draws * p_a * p_b
            lift    = obs / exp if exp > 0 else (1.0 if obs == 0 else 2.0)
            lift_matrix[(a, b)] = lift

    # ── Summary stats ───────────────────────────────────────────────────────
    lifts = list(lift_matrix.values())
    mean_lift = sum(lifts) / len(lifts) if lifts else 1.0
    # Geometric mean
    log_sum = sum(math.log(max(l, 1e-6)) for l in lifts)
    geo_mean = math.exp(log_sum / len(lifts)) if lifts else 1.0

    best_pair  = max(lift_matrix.items(), key=lambda x: x[1])
    worst_pair = min(lift_matrix.items(), key=lambda x: x[1])

    # ── Colour helper ───────────────────────────────────────────────────────
    def lift_colour(l: float) -> str:
        if l >= 1.5:   return "bold green"
        if l >= 1.15:  return "green"
        if l >= 0.85:  return "dim"
        if l >= 0.6:   return "yellow"
        return "red"

    def lift_fmt(l: float) -> str:
        colour = lift_colour(l)
        return f"[{colour}]{l:.2f}[/{colour}]"

    # ── Matrix table ────────────────────────────────────────────────────────
    tbl = Table(
        title=f"🕸️ Synergy Map — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold yellow",
        show_header=True,
    )
    tbl.add_column("↓ \\ →", justify="right", style="bold yellow")
    for n in t_nums:
        tbl.add_column(str(n), justify="center")

    for i_idx, a in enumerate(t_nums):
        row_cells = [str(a)]
        for j_idx, b in enumerate(t_nums):
            if j_idx <= i_idx:
                row_cells.append("·")
            else:
                l = lift_matrix.get((a, b), lift_matrix.get((b, a), 1.0))
                row_cells.append(lift_fmt(l))
        tbl.add_row(*row_cells)

    console.print()
    console.print(tbl)

    # ── Legend ──────────────────────────────────────────────────────────────
    console.print(
        "\n  [bold green]≥1.5[/bold green] strong synergy  "
        "[green]1.15–1.5[/green] mild synergy  "
        "[dim]0.85–1.15[/dim] neutral  "
        "[yellow]0.6–0.85[/yellow] mild repellent  "
        "[red]<0.6[/red] repellent\n"
    )

    # ── Summary panel ───────────────────────────────────────────────────────
    bp_a, bp_b   = best_pair[0]
    wp_a, wp_b   = worst_pair[0]
    score_colour = "bold green" if geo_mean >= 1.1 else "yellow" if geo_mean >= 0.9 else "red"

    console.print(Panel(
        f"[{score_colour}]Ticket synergy score: {geo_mean:.3f}×[/{score_colour}]\n\n"
        f"[bold green]Best pair:[/bold green]   #{bp_a} & #{bp_b} "
        f"→ lift {best_pair[1]:.2f}× "
        f"(appeared together {co.get((bp_a, bp_b), 0)} times)\n"
        f"[red]Worst pair:[/red]  #{wp_a} & #{wp_b} "
        f"→ lift {worst_pair[1]:.2f}× "
        f"(appeared together {co.get((wp_a, wp_b), 0)} times)\n"
        f"[dim]Mean lift: {mean_lift:.3f}×  ·  Pairs: {len(lifts)}  ·  "
        f"Draws: {n_draws}[/dim]",
        title="🕸️ Synergy Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            t_nums, n_draws, geo_mean, mean_lift,
            best_pair, worst_pair, co, lift_matrix,
        )
        console.print(f"\n[green]✔ Synergy map appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    ticket: list, n_draws: int, geo_mean: float, mean_lift: float,
    best_pair: tuple, worst_pair: tuple,
    co: Counter, lift_matrix: dict,
) -> None:
    bp_a, bp_b = best_pair[0]
    wp_a, wp_b = worst_pair[0]
    ticket_str = " ".join(str(n) for n in ticket)

    top_pairs = sorted(lift_matrix.items(), key=lambda x: -x[1])[:10]
    rows = ""
    for (a, b), l in top_pairs:
        rows += f"| {a} & {b} | {co.get((a, b), 0)} | {l:.3f} |\n"

    content = f"""
---
type: diagnostic
subtype: synergy-map
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket: [{ticket_str}]
draws_analysed: {n_draws}
geo_mean_lift: {geo_mean:.4f}
mean_lift: {mean_lift:.4f}
best_pair: [{bp_a}, {bp_b}]
best_pair_lift: {best_pair[1]:.4f}
worst_pair: [{wp_a}, {wp_b}]
worst_pair_lift: {worst_pair[1]:.4f}
---

## Synergy Map: {game_name} ({today.isoformat()})

**Ticket:** {ticket_str}
**Synergy score:** {geo_mean:.3f}×  ·  **Mean lift:** {mean_lift:.3f}×
**Best pair:** #{bp_a} & #{bp_b} → {best_pair[1]:.3f}×
**Worst pair:** #{wp_a} & #{wp_b} → {worst_pair[1]:.3f}×

| Pair | Co-occur | Lift |
|------|----------|------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
