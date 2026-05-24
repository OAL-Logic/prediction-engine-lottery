"""
Multi Ticket Command 🎟️
=======================
Generates a portfolio of N tickets with maximised pool coverage.

Rather than running the same strategy N times (which tends to produce
overlapping tickets), this command explicitly diversifies:

Algorithm
---------
  1. Generate a base ticket using the engine's forecast strategy.
  2. Track which numbers have been "used" across all tickets so far.
  3. For each subsequent ticket, score candidate numbers by:
       diversity bonus  = 1 if not yet used in any ticket, else 0
       base score       = composite frequency/streak/consensus score
       combined         = base_score × (1 + diversity_weight × bonus)
  4. Select the top-K combined-score numbers for each ticket.

This produces a set of tickets where:
  • Each ticket is individually strong (not random)
  • Collectively they cover a wider portion of the pool
  • Overlap between tickets is minimised

Useful for:
  • Syndicates playing multiple tickets per draw
  • Optimising a set of tickets for breadth vs redundancy
  • Combined with coverage-check to verify final pool coverage

Output
------
  Ticket grid   N tickets side-by-side, shared numbers highlighted
  Coverage bar  pool coverage after all tickets combined
  Summary panel total unique numbers covered, mean overlap between tickets

Example
-------
  lottery multi-ticket br/lotofacil --count 4
  lottery multi-ticket br/lotofacil --count 6 --diversity 0.8
  lottery multi-ticket br/mega-sena --count 3 --export-md portfolio.md
"""

from __future__ import annotations

import random
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


def _num_score(num: int, df, rules, n_draws: int) -> float:
    """Quick composite score: frequency (60%) + recency (40%)."""
    window   = df.tail(n_draws)
    all_rows = list(window.itertuples())
    freq     = sum(1 for row in all_rows if num in row.numbers) / n_draws

    # Recency: did it appear in the most recent quarter?
    recent_n = max(1, n_draws // 4)
    recent   = sum(1 for row in all_rows[-recent_n:] if num in row.numbers) / recent_n

    return 0.6 * freq + 0.4 * recent


def multi_ticket(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    count: Annotated[int, typer.Option("--count", "-k",
        help="Number of tickets to generate")] = 3,
    diversity: Annotated[float, typer.Option("--diversity", "-d",
        help="Diversity weight 0–1 (higher = more distinct tickets)")] = 0.6,
    score_window: Annotated[int, typer.Option("--limit", "-L",
        help="Draws used for scoring")] = 100,
    seed: Annotated[Optional[int], typer.Option("--seed",
        help="Random seed for reproducibility")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append multi-ticket report to this .md file")] = None,
) -> None:
    """🎟️ Generate a portfolio of N diverse tickets with maximised pool coverage.

    Each ticket is individually strong; together they minimise redundancy
    across the pool. Useful for syndicates.

    Example: lottery multi-ticket br/lotofacil --count 4
             lottery multi-ticket br/lotofacil --count 6 --diversity 0.8
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    pick     = rules.pick_count
    pool     = list(range(lo, hi + 1))
    pool_sz  = hi - lo + 1

    if count < 1:
        console.print("[dim]--count must be at least 1.[/dim]")
        raise typer.Exit(0)

    if len(df) < score_window + 5:
        score_window = max(10, len(df) - 5)

    if seed is not None:
        random.seed(seed)

    # ── Score every pool number ────────────────────────────────────────────
    base_scores = {num: _num_score(num, df, rules, score_window) for num in pool}

    # ── Generate tickets greedily ──────────────────────────────────────────
    used_counter: Counter[int] = Counter()
    tickets: list[list[int]] = []

    for t_idx in range(count):
        # Combine base score with diversity bonus
        combined = {}
        for num in pool:
            bonus      = 1.0 if used_counter[num] == 0 else 0.0
            combined[num] = base_scores[num] * (1.0 + diversity * bonus)

        # Add small random jitter to break ties and vary tickets
        for num in pool:
            combined[num] += random.uniform(0, 0.01)

        # Select top-pick numbers
        ranked = sorted(pool, key=lambda n: -combined[n])
        ticket = sorted(ranked[:pick])
        tickets.append(ticket)

        for n in ticket:
            used_counter[n] += 1

    # ── Coverage analysis ──────────────────────────────────────────────────
    covered_set = set()
    for t in tickets:
        covered_set.update(t)
    cover_pct = len(covered_set) / pool_sz * 100

    # Mean pairwise overlap
    overlaps = []
    for i in range(len(tickets)):
        for j in range(i + 1, len(tickets)):
            overlap = len(set(tickets[i]) & set(tickets[j]))
            overlaps.append(overlap)
    mean_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    max_overlap  = max(overlaps) if overlaps else 0

    # Numbers that appear in all tickets
    universal = [n for n in covered_set if used_counter[n] == count]

    # ── Ticket grid ────────────────────────────────────────────────────────
    tbl = Table(
        title=f"🎟️ Multi-Ticket Portfolio — {rules.name}  ({count} tickets)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Ticket", justify="center", style="bold yellow")
    tbl.add_column("Numbers", justify="left")
    tbl.add_column("Unique?", justify="right", style="dim")

    all_nums_set = set(n for t in tickets for n in t)

    for idx, t in enumerate(tickets, 1):
        nums_text = Text()
        unique_in_t = 0
        for n in t:
            if used_counter[n] == 1:
                nums_text.append(f"{n:2}", style="bold green")
                unique_in_t += 1
            elif used_counter[n] == count:
                nums_text.append(f"{n:2}", style="dim")
            else:
                nums_text.append(f"{n:2}", style="yellow")
            nums_text.append(" ")

        tbl.add_row(f"T{idx}", nums_text, f"{unique_in_t} excl.")

    console.print()
    console.print(tbl)
    console.print(
        f"\n  [bold green]Green[/bold green] = exclusive to this ticket  "
        f"[yellow]Yellow[/yellow] = shared  "
        f"[dim]Dim[/dim] = in all tickets\n"
    )

    # Coverage bar
    bar_width = 40
    filled    = round(len(covered_set) / pool_sz * bar_width)
    bar_str   = "█" * filled + "░" * (bar_width - filled)
    console.print(f"  Pool coverage: [{bar_str}] {len(covered_set)}/{pool_sz} ({cover_pct:.1f}%)")

    # ── Summary panel ──────────────────────────────────────────────────────
    univ_str = "  ".join(f"#{n}" for n in sorted(universal)[:10]) or "none"

    console.print()
    console.print(Panel(
        f"[bold]{count} tickets[/bold]  ·  "
        f"Pool coverage: [bold green]{cover_pct:.1f}%[/bold green] "
        f"({len(covered_set)}/{pool_sz} numbers)\n"
        f"Mean overlap: {mean_overlap:.1f} numbers/pair  ·  "
        f"Max overlap: {max_overlap}\n"
        f"[dim]Universal (in all tickets): {univ_str}\n"
        f"Diversity weight: {diversity}  ·  Score window: {score_window} draws[/dim]",
        title="🎟️ Portfolio Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            count, tickets, cover_pct, len(covered_set), pool_sz,
            mean_overlap, max_overlap, diversity, score_window,
        )
        console.print(f"\n[green]✔ Multi-ticket report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    count: int, tickets: list, cover_pct: float,
    n_covered: int, pool_sz: int,
    mean_overlap: float, max_overlap: int,
    diversity: float, score_window: int,
) -> None:
    ticket_rows = ""
    for i, t in enumerate(tickets, 1):
        nums = " ".join(str(n) for n in t)
        ticket_rows += f"| T{i} | {nums} |\n"

    content = f"""
---
type: diagnostic
subtype: multi-ticket
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket_count: {count}
pool_size: {pool_sz}
covered: {n_covered}
cover_pct: {cover_pct:.1f}
coverage_efficiency: {cover_pct / 100:.4f}
mean_overlap: {mean_overlap:.2f}
max_overlap: {max_overlap}
diversity_weight: {diversity}
score_window: {score_window}
---

## Multi-Ticket Portfolio: {game_name} ({today.isoformat()})

**Tickets:** {count}  ·  **Coverage:** {n_covered}/{pool_sz} ({cover_pct:.1f}%)
**Mean overlap:** {mean_overlap:.1f}  ·  **Max overlap:** {max_overlap}
**Diversity weight:** {diversity}

| Ticket | Numbers |
|--------|---------|
{ticket_rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
