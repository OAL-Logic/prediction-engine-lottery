"""
Coverage Check Command 🗺️
=========================
Pool coverage analysis for a set of tickets.

Given multiple tickets, computes:
  • Which pool numbers appear in at least one ticket (covered)
  • Which numbers are NOT covered (gaps)
  • How many times each number is covered (redundancy)
  • Prize tier coverage: given the covered set, what's the minimum
    guaranteed overlap with any draw that uses the full pool?
  • Entropy: is the coverage uniform, or clustered?

Useful for:
  • Syndicates playing multiple tickets — are you covering the pool well?
  • Seeing whether your regular ticket set has persistent blind spots
  • Optimizing a portfolio of tickets for breadth vs depth

Usage
-----
  Pass tickets as comma-separated groups:
    lottery coverage-check br/lotofacil "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15" \\
                                        "11 12 13 14 15 16 17 18 19 20 21 22 23 24 25"

  Or read tickets from a file (one ticket per line):
    lottery coverage-check br/lotofacil --file tickets.txt

Example
-------
  lottery coverage-check br/lotofacil "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
  lottery coverage-check br/lotofacil \\
      "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25" \\
      "2 4 6 8 9 12 14 16 17 18 19 20 21 22 25"
"""

from __future__ import annotations

import math
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


def coverage_check(
    lottery:  Annotated[str, typer.Argument(help="Lottery name [Required]")],
    tickets:  Annotated[Optional[list[str]], typer.Argument(
        help="Tickets as quoted space-separated strings [Required]")] = None,
    file:     Annotated[Optional[str], typer.Option("--file", "-f",
        help="File with one ticket per line")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append coverage report to this .md file")] = None,
) -> None:
    """🗺️ Pool coverage analysis for one or more tickets.

    Shows which pool numbers are covered/uncovered, redundancy per number,
    and coverage % for prize tiers.

    Example: lottery coverage-check br/lotofacil "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
    """
    adapter = get_adapter(lottery)
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = list(range(lo, hi + 1))
    pool_size = hi - lo + 1

    # ── Load tickets ──────────────────────────────────────────────────────────
    parsed_tickets: list[list[int]] = []

    if file:
        try:
            for line in Path(file).read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                nums = [int(x) for x in line.split() if x.isdigit()]
                if nums:
                    parsed_tickets.append(sorted(nums))
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)

    if tickets:
        for t_str in tickets:
            nums = [int(x) for x in t_str.split() if x.isdigit()]
            if nums:
                parsed_tickets.append(sorted(nums))

    if not parsed_tickets:
        console.print("[dim]No tickets provided. Pass tickets as arguments or use --file.[/dim]")
        raise typer.Exit(0)

    # Validate
    invalid_tickets = []
    for i, t in enumerate(parsed_tickets):
        bad = [n for n in t if not (lo <= n <= hi)]
        if bad:
            invalid_tickets.append((i + 1, bad))
    if invalid_tickets:
        for i, bad in invalid_tickets:
            console.print(f"[yellow]Ticket {i} has out-of-range numbers: {bad}[/yellow]")

    n_tickets = len(parsed_tickets)

    # ── Coverage counter ──────────────────────────────────────────────────────
    coverage: Counter[int] = Counter()
    for t in parsed_tickets:
        for n in t:
            if lo <= n <= hi:
                coverage[n] += 1

    covered_set   = {n for n in pool if coverage[n] > 0}
    uncovered_set = {n for n in pool if coverage[n] == 0}
    cover_pct     = len(covered_set) / pool_size * 100

    # ── Redundancy distribution ───────────────────────────────────────────────
    max_cov = max(coverage.values()) if coverage else 1
    redundancy: Counter[int] = Counter(coverage[n] for n in pool)  # how many numbers have cov=k

    # ── Coverage grid display ─────────────────────────────────────────────────
    console.print(f"\n[bold]{rules.name}[/bold]  —  "
                  f"{n_tickets} ticket{'s' if n_tickets != 1 else ''}  ·  "
                  f"Pool: {pool_size} numbers ({lo}–{hi})\n")

    # Show coverage per number as a horizontal bar
    row_text = Text()
    for n in pool:
        c = coverage.get(n, 0)
        if c == 0:
            row_text.append(f" {n:2}░", style="dim")
        elif c == 1:
            row_text.append(f" {n:2}▓", style="green")
        else:
            row_text.append(f" {n:2}█", style="bold green")
        if (n - lo + 1) % 10 == 0:
            row_text.append("  ")

    console.print(row_text)
    console.print(
        f"  [green]█[/green] = covered ×2+  "
        f"[green]▓[/green] = covered ×1  "
        f"[dim]░[/dim] = not covered\n"
    )

    # ── Coverage stats table ──────────────────────────────────────────────────
    stats_table = Table(title="🗺️ Coverage Statistics", box=None, padding=(0, 1), header_style="bold")
    stats_table.add_column("Metric",  justify="left")
    stats_table.add_column("Value",   justify="right",  style="bold yellow")
    stats_table.add_column("Detail",  justify="left",   style="dim")

    stats_table.add_row("Tickets",      str(n_tickets),      "")
    stats_table.add_row("Pool size",    str(pool_size),      f"{lo}–{hi}")
    stats_table.add_row("Covered",      f"{len(covered_set)}", f"{cover_pct:.1f}%")
    stats_table.add_row("Uncovered",    str(len(uncovered_set)),
                        f"{', '.join(str(n) for n in sorted(uncovered_set)[:10])}"
                        + ("…" if len(uncovered_set) > 10 else ""))
    stats_table.add_row("Max redundancy", str(max_cov),
                        f"Numbers covered {max_cov}×: "
                        f"{', '.join(str(n) for n, c in coverage.items() if c == max_cov)[:30]}")

    # Coverage efficiency: covered / (n_tickets * pick)
    total_slots = n_tickets * pick
    efficiency  = len(covered_set) / total_slots if total_slots > 0 else 0.0
    stats_table.add_row("Coverage efficiency", f"{efficiency:.2%}",
                        f"{len(covered_set)} unique / {total_slots} total slots")

    console.print(stats_table)

    # ── Prize tier simulation ─────────────────────────────────────────────────
    if rules.prize_tiers:
        tier_table = Table(
            title="Prize Tier Coverage (if ALL covered numbers are drawn)",
            box=None, padding=(0, 1), header_style="bold",
        )
        tier_table.add_column("Tier (min hits)", justify="center", style="cyan")
        tier_table.add_column("Tickets covering",justify="right")
        tier_table.add_column("Best ticket",     justify="left",  style="dim")

        # Simulate: if a draw contained ALL covered numbers (best case),
        # how many tickets would hit each tier?
        best_case_draw = covered_set

        for min_hits in sorted(rules.prize_tiers):
            n_qualifying = 0
            best_t_str = "—"
            best_hits  = 0
            for t in parsed_tickets:
                hits = len(set(t) & best_case_draw)
                if hits >= min_hits:
                    n_qualifying += 1
                if hits > best_hits:
                    best_hits = hits
                    best_t_str = " ".join(str(n) for n in t[:6]) + "…"

            tier_table.add_row(
                f"Match {min_hits}",
                str(n_qualifying),
                best_t_str,
            )

        console.print()
        console.print(tier_table)

    # ── Summary panel ─────────────────────────────────────────────────────────
    # Coverage entropy (how uniform is the coverage?)
    total_covered_slots = sum(coverage.values())
    if total_covered_slots > 0:
        probs = [coverage[n] / total_covered_slots for n in pool if coverage[n] > 0]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        max_entropy = math.log2(len(covered_set)) if covered_set else 0
        entropy_pct = entropy / max_entropy * 100 if max_entropy > 0 else 0
    else:
        entropy_pct = 0

    coverage_verdict = (
        "EXCELLENT" if cover_pct >= 95 else
        "GOOD"      if cover_pct >= 80 else
        "PARTIAL"   if cover_pct >= 60 else
        "LIMITED"
    )
    cv_colour = "bold green" if cover_pct >= 80 else "yellow" if cover_pct >= 60 else "red"

    console.print()
    console.print(Panel(
        f"[{cv_colour}]{coverage_verdict}[/{cv_colour}]  —  "
        f"{len(covered_set)}/{pool_size} numbers covered ({cover_pct:.1f}%)\n"
        f"[dim]Uncovered: {len(uncovered_set)} numbers  ·  "
        f"Coverage efficiency: {efficiency:.1%}  ·  "
        f"Distribution entropy: {entropy_pct:.0f}%[/dim]",
        title="🗺️ Coverage Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_tickets, pool_size, len(covered_set), len(uncovered_set),
            cover_pct, efficiency, sorted(uncovered_set), coverage_verdict,
        )
        console.print(f"\n[green]✔ Coverage report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_tickets: int, pool_size: int, n_covered: int, n_uncovered: int,
    cover_pct: float, efficiency: float, uncovered: list[int],
    verdict: str,
) -> None:
    unc_str = ", ".join(str(n) for n in uncovered) if uncovered else "none"
    content = f"""
---
type: diagnostic
subtype: coverage-check
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
tickets: {n_tickets}
pool_size: {pool_size}
covered: {n_covered}
uncovered: {n_uncovered}
cover_pct: {cover_pct:.1f}
coverage_efficiency: {cover_pct / 100:.4f}
efficiency: {efficiency:.3f}
verdict: {verdict}
uncovered_numbers: [{unc_str}]
---

## Coverage Check: {game_name} ({today.isoformat()})

**Tickets:** {n_tickets}  ·  **Covered:** {n_covered}/{pool_size} ({cover_pct:.1f}%)
**Efficiency:** {efficiency:.1%}  ·  **Verdict:** {verdict}

**Uncovered numbers:** {unc_str}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
