"""
Ticket DNA Command 🧬
====================
Structural fingerprint of a ticket vs the historical draw population.

Decomposes a ticket into 7 structural dimensions and compares each
against the empirical distribution from recent draws:

  1. Sum          — total of all numbers
  2. Mean         — average number value
  3. Parity       — even count / pick_count
  4. Consecutive  — count of adjacent consecutive pairs
  5. Spread       — max - min (range)
  6. Decade dist  — how numbers spread across decades of the pool
  7. Symmetry     — distance from pool midpoint (low = balanced)

For each dimension the command reports:
  • Ticket value
  • Historical median for that dimension
  • Percentile rank (how many draws scored below this value)
  • Tier: COMMON (25th–75th pct), ABOVE/BELOW AVERAGE, RARE

A high RARE count means the ticket is structurally unusual relative
to what actually gets drawn — useful for rejection filtering.

Output
------
  DNA table     7 dimensions with value / median / percentile / tier
  Fingerprint   one-line encoded tag  e.g.  S↑ M→ P↓ C→ Sp↑ D→ Sy→
  Summary panel overall typicality score + recommendation

Example
-------
  lottery ticket-dna br/lotofacil "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
  lottery ticket-dna br/mega-sena "3 12 28 37 41 55" --draws 300
  lottery ticket-dna br/lotofacil "..." --export-md dna.md
"""

from __future__ import annotations

import sys
import numpy as np
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import (
    get_adapter,
    percentile_rank as _percentile_rank,
    decade_spread as _decade_spread,
    symmetry_score as _symmetry_score,
)

console = Console()


def ticket_dna(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    ticket:  Annotated[Optional[str], typer.Argument(
        help="Space-separated ticket numbers (quoted). Omit when using --from-stdin.")] = None,
    draws:   Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws used as population")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append DNA report to this .md file")] = None,
    from_stdin: Annotated[bool, typer.Option("--from-stdin",
        help="Read ticket numbers from stdin (enables piping from 'picks --raw')")] = False,
) -> None:
    """🧬 Structural fingerprint of a ticket vs historical draw population.

    Compares 7 ticket properties to the empirical distribution from recent
    draws and gives a percentile rank + typicality verdict for each.

    Example: lottery ticket-dna br/lotofacil "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
             lottery picks br/lotofacil --raw | lottery ticket-dna br/lotofacil --from-stdin
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

    if not t_nums:
        console.print("[dim]No numbers provided.[/dim]")
        raise typer.Exit(0)

    n_draws  = min(draws, len(df))
    window   = df.tail(n_draws)
    all_rows = [row for row in window.itertuples() if row.numbers is not None and len(row.numbers) > 0]

    # ── Build historical population for each dimension ─────────────────────
    pop_sum:    list[float] = []
    pop_mean:   list[float] = []
    pop_parity: list[float] = []
    pop_consec: list[float] = []
    pop_spread: list[float] = []
    pop_decade: list[float] = []
    pop_sym:    list[float] = []

    for row in all_rows:
        nums = sorted(row.numbers)
        if not nums:
            continue
        pop_sum.append(float(sum(nums)))
        pop_mean.append(float(sum(nums) / len(nums)))
        pop_parity.append(sum(1 for n in nums if n % 2 == 0) / len(nums))
        pop_consec.append(float(sum(1 for a, b in zip(nums, nums[1:]) if b == a + 1)))
        pop_spread.append(float(nums[-1] - nums[0]))
        pop_decade.append(_decade_spread(nums, lo, hi))
        pop_sym.append(_symmetry_score(nums, lo, hi))

    # ── Ticket values ──────────────────────────────────────────────────────
    t_sum    = float(sum(t_nums))
    t_mean   = t_sum / len(t_nums)
    t_parity = sum(1 for n in t_nums if n % 2 == 0) / len(t_nums)
    t_consec = float(sum(1 for a, b in zip(t_nums, t_nums[1:]) if b == a + 1))
    t_spread = float(t_nums[-1] - t_nums[0])
    t_decade = _decade_spread(t_nums, lo, hi)
    t_sym    = _symmetry_score(t_nums, lo, hi)

    dimensions = [
        ("Sum",         t_sum,    pop_sum,    ".0f", "↑ = high total"),
        ("Mean",        t_mean,   pop_mean,   ".1f", "↑ = skewed high"),
        ("Parity",      t_parity, pop_parity, ".0%", "↑ = more evens"),
        ("Consecutive", t_consec, pop_consec, ".0f", "↑ = more adjacent pairs"),
        ("Spread",      t_spread, pop_spread, ".0f", "↑ = wider range"),
        ("Decade cov.", t_decade, pop_decade, ".0%", "↑ = covers more bands"),
        ("Symmetry",    t_sym,    pop_sym,    ".1f", "↑ = further from midpoint"),
    ]

    # ── DNA table ──────────────────────────────────────────────────────────
    tbl = Table(
        title=f"🧬 Ticket DNA — {rules.name}  (population: {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Dimension",  justify="left")
    tbl.add_column("Ticket",     justify="right",  style="bold yellow")
    tbl.add_column("Median",     justify="right",  style="dim")
    tbl.add_column("Percentile", justify="right")
    tbl.add_column("Tier",       justify="center")
    tbl.add_column("Note",       justify="left",   style="dim")

    fingerprint_parts: list[str] = []
    tier_scores: list[str] = []

    dim_abbrevs = ["S", "M", "P", "C", "Sp", "D", "Sy"]

    for (name, val, pop, fmt, note), abbrev in zip(dimensions, dim_abbrevs):
        pct = _percentile_rank(val, pop)
        med = np.median(pop) if pop else val

        if pct <= 10 or pct >= 90:
            tier = "RARE"
            tier_fmt = "[red]RARE[/red]"
        elif pct <= 25 or pct >= 75:
            tier = "UNUSUAL"
            tier_fmt = "[yellow]UNUSUAL[/yellow]"
        else:
            tier = "COMMON"
            tier_fmt = "[green]COMMON[/green]"

        tier_scores.append(tier)

        arrow = "↑" if pct >= 60 else "↓" if pct <= 40 else "→"
        fingerprint_parts.append(f"{abbrev}{arrow}")

        val_str = format(val, fmt)
        med_str = format(med, fmt)
        pct_col = "red" if pct <= 10 or pct >= 90 else "yellow" if pct <= 25 or pct >= 75 else "dim"

        tbl.add_row(
            name,
            val_str,
            med_str,
            f"[{pct_col}]{pct:.0f}th[/{pct_col}]",
            tier_fmt,
            note,
        )

    console.print()
    console.print(tbl)

    # ── Fingerprint line ───────────────────────────────────────────────────
    fingerprint = "  ".join(fingerprint_parts)
    console.print(f"\n  [bold]Fingerprint:[/bold]  {fingerprint}")
    console.print(f"  [dim]Ticket:     {' '.join(str(n) for n in t_nums)}[/dim]")

    # ── Summary panel ──────────────────────────────────────────────────────
    n_rare    = tier_scores.count("RARE")
    n_unusual = tier_scores.count("UNUSUAL")
    n_common  = tier_scores.count("COMMON")

    typicality = n_common / len(tier_scores) * 100 if tier_scores else 0

    if typicality >= 70:
        verdict  = "TYPICAL — ticket structure matches historical draw patterns well"
        colour   = "bold green"
    elif typicality >= 40:
        verdict  = "MIXED — some unusual structural properties"
        colour   = "yellow"
    else:
        verdict  = "ATYPICAL — ticket structure is rare relative to historical draws"
        colour   = "red"

    console.print()
    console.print(Panel(
        f"[{colour}]{verdict}[/{colour}]\n\n"
        f"[dim]Common: {n_common}/7  ·  Unusual: {n_unusual}/7  ·  Rare: {n_rare}/7\n"
        f"Typicality score: {typicality:.0f}%  ·  Fingerprint: {fingerprint}[/dim]",
        title="🧬 DNA Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            t_nums, n_draws, fingerprint, typicality, n_rare, n_unusual, n_common,
            verdict, dimensions,
        )
        console.print(f"\n[green]✔ DNA report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    ticket: list, n_draws: int, fingerprint: str, typicality: float,
    n_rare: int, n_unusual: int, n_common: int,
    verdict: str, dimensions: list,
) -> None:
    ticket_str = " ".join(str(n) for n in ticket)

    rows = ""
    for (name, val, pop, fmt, note) in dimensions:
        pct = sum(1 for v in pop if v < val) / len(pop) * 100 if pop else 50.0
        med = np.median(pop) if pop else val
        rows += f"| {name} | {format(val, fmt)} | {format(med, fmt)} | {pct:.0f}th |\n"

    content = f"""
---
type: diagnostic
subtype: ticket-dna
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket: [{ticket_str}]
draws_analysed: {n_draws}
fingerprint: "{fingerprint}"
typicality: {typicality:.1f}
rare_dims: {n_rare}
unusual_dims: {n_unusual}
common_dims: {n_common}
verdict: {verdict.split('—')[0].strip()}
---

## Ticket DNA: {game_name} ({today.isoformat()})

**Ticket:** {ticket_str}
**Fingerprint:** {fingerprint}
**Typicality:** {typicality:.0f}%  ·  **Verdict:** {verdict}

| Dimension | Ticket | Median | Percentile |
|-----------|--------|--------|------------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
