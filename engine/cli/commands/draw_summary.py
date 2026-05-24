"""
Draw Summary Command 🎯
=======================
Quick contextual analysis of a specific draw or the latest draw.

For each number in the target draw, shows:
  • Historical frequency (last 100 draws)
  • Whether it was on a hot/cold streak going into the draw
  • How long it had been absent before appearing (gap since last hit)
  • Rarity tier: EXPECTED / OVERDUE / SURPRISE

Aggregate statistics for the draw as a whole:
  • Sum, parity (even/odd count), decade distribution
  • Average gap-since-last-appearance across all drawn numbers
  • "Surprise score" — how unexpected the draw was vs historical base rates

Useful for:
  • Post-draw analysis ("was this a typical draw?")
  • Understanding what a surprise draw looks like
  • Comparing draws over time

Example
-------
  lottery draw-summary br/lotofacil              # most recent draw
  lottery draw-summary br/lotofacil --id 3670    # specific draw by ID
  lottery draw-summary br/lotofacil --export-md summary.md
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

console = Console()


def draw_summary(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draw_id: Annotated[Optional[int], typer.Option("--id", "-i",
        help="Specific draw ID to analyse (default: latest)")] = None,
    context: Annotated[int, typer.Option("--context", "-c",
        help="How many prior draws to use as frequency baseline")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append draw summary to this .md file")] = None,
) -> None:
    """🎯 Contextual analysis of a specific draw vs historical patterns.

    Shows frequency, streak-going-in, and gap-since-last-appearance for
    each drawn number. Summarises the draw's overall "surprise" level.

    Example: lottery draw-summary br/lotofacil
             lottery draw-summary br/lotofacil --id 3670
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = hi - lo + 1

    # ── Select target draw ────────────────────────────────────────────────────
    # Filter to rows that actually have numbers
    def is_valid(x):
        try:
            return x is not None and len(x) > 0
        except TypeError:
            return False
            
    valid = df[df["numbers"].apply(is_valid)]
    if valid.empty:
        console.print("[red]No draw data available.[/red]")
        raise typer.Exit(1)

    if draw_id is not None:
        target_rows = valid[valid["draw_id"] == draw_id]
        if target_rows.empty:
            console.print(f"[red]Draw ID {draw_id} not found.[/red]")
            raise typer.Exit(1)
        target_idx = target_rows.index[0]
    else:
        target_idx = valid.index[-1]

    target_row  = df.loc[target_idx]
    target_nums = sorted(target_row.numbers)
    target_did  = int(target_row.draw_id)
    target_date = str(target_row.draw_date) if str(target_row.draw_date) != "nan" else "?"

    # Prior draws used as context (before the target draw)
    prior = valid[valid.index < target_idx].tail(context)
    n_prior = len(prior)

    if n_prior == 0:
        console.print("[dim]No prior draws available for context.[/dim]")
        raise typer.Exit(0)

    # ── Build historical data per number ──────────────────────────────────────
    freq: Counter[int] = Counter()
    for row in prior.itertuples():
        for n in row.numbers:
            freq[n] += 1

    baseline_rate = pick / pool   # expected hit rate per draw

    # Gap since last appearance (draws before target where number appeared)
    def gap_before(num: int) -> int:
        """Draws since num last appeared, looking backwards from target."""
        for i, row in enumerate(reversed(list(prior.itertuples()))):
            if num in row.numbers:
                return i
        return n_prior  # never appeared in window

    # Streak going into the draw (hot or cold)
    def streak_before(num: int) -> int:
        """Consecutive hit (+) or miss (-) streak ending just before target."""
        streak = 0
        prev_rows = list(prior.itertuples())
        if not prev_rows:
            return 0
        val = num in prev_rows[-1].numbers
        for row in reversed(prev_rows):
            if (num in row.numbers) == val:
                streak += 1
            else:
                break
        return streak if val else -streak

    # ── Per-number table ──────────────────────────────────────────────────────
    num_table = Table(
        title=f"🎯 Draw #{target_did}  ({target_date})  — {rules.name}",
        box=None, padding=(0, 1), header_style="bold",
    )
    num_table.add_column("Number",  justify="center", style="bold yellow")
    num_table.add_column("Freq%",   justify="right",  style="dim")
    num_table.add_column("Gap",     justify="right")
    num_table.add_column("Streak",  justify="right")
    num_table.add_column("Tier",    justify="center")

    surprise_total = 0.0
    num_data = []

    for n in target_nums:
        f    = freq.get(n, 0)
        fq   = f / n_prior if n_prior else 0.0
        gap  = gap_before(n)
        stk  = streak_before(n)

        # Tier: compare frequency to baseline
        if fq >= baseline_rate * 1.4:
            tier = "[bold green]EXPECTED[/bold green]"
        elif fq >= baseline_rate * 0.7:
            tier = "[green]NORMAL[/green]"
        elif gap > 10:
            tier = "[bold yellow]OVERDUE[/bold yellow]"
        else:
            tier = "[yellow]SURPRISE[/yellow]"

        # Surprise contribution: how unlikely was this number appearing?
        # Simple model: rarer in recent history = more surprising
        # Normalise gap against expected gap = pool/pick
        expected_gap = pool / pick
        gap_factor = gap / expected_gap if expected_gap > 0 else 1.0
        surprise_total += max(0, gap_factor - 1.0)

        gap_fmt = (
            f"[bold yellow]{gap}[/bold yellow]" if gap > expected_gap * 1.5
            else f"[green]{gap}[/green]" if gap <= 3
            else str(gap)
        )
        stk_fmt = (
            f"[green]+{stk}[/green]" if stk > 0
            else f"[cyan]{stk}[/cyan]" if stk < 0
            else "[dim]0[/dim]"
        )

        num_table.add_row(
            str(n),
            f"{fq:.0%}",
            gap_fmt,
            stk_fmt,
            tier,
        )
        num_data.append({"num": n, "freq": fq, "gap": gap, "streak": stk})

    console.print()
    console.print(num_table)

    # ── Aggregate stats ───────────────────────────────────────────────────────
    total_sum   = sum(target_nums)
    n_even      = sum(1 for n in target_nums if n % 2 == 0)
    n_odd       = pick - n_even
    decades     = Counter((n - lo) // 10 for n in target_nums)
    avg_gap     = sum(d["gap"] for d in num_data) / len(num_data) if num_data else 0
    surprise_score = surprise_total / pick if pick else 0.0

    # Surprise verdict
    if surprise_score >= 1.5:
        verdict = "[bold red]VERY UNUSUAL[/bold red]"
    elif surprise_score >= 0.8:
        verdict = "[yellow]ABOVE AVERAGE SURPRISE[/yellow]"
    elif surprise_score >= 0.3:
        verdict = "[green]TYPICAL[/green]"
    else:
        verdict = "[bold green]HIGHLY PREDICTABLE[/bold green]"

    decade_str = "  ".join(
        f"[dim]{lo + k*10}–{lo + k*10+9}:[/dim] {v}"
        for k, v in sorted(decades.items())
    )

    console.print()
    console.print(Panel(
        f"[bold]Draw #{target_did}[/bold]  {target_date}  ·  {rules.name}\n"
        f"[dim]Numbers:[/dim] {' '.join(str(n) for n in target_nums)}\n\n"
        f"[dim]Sum:[/dim] {total_sum}   "
        f"[dim]Even/Odd:[/dim] {n_even}/{n_odd}   "
        f"[dim]Avg gap:[/dim] {avg_gap:.1f}\n"
        f"[dim]Decades:[/dim] {decade_str}\n"
        f"[dim]Surprise score:[/dim] {surprise_score:.2f}  →  {verdict}\n"
        f"[dim]Context: {n_prior} prior draws[/dim]",
        title="🎯 Draw Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            target_did, target_date, target_nums, n_prior,
            total_sum, n_even, n_odd, avg_gap, surprise_score,
        )
        console.print(f"\n[green]✔ Draw summary appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    draw_id: int, draw_date: str, numbers: list[int], n_prior: int,
    total_sum: int, n_even: int, n_odd: int, avg_gap: float,
    surprise_score: float,
) -> None:
    verdict = (
        "VERY_UNUSUAL"   if surprise_score >= 1.5 else
        "ABOVE_AVERAGE"  if surprise_score >= 0.8 else
        "TYPICAL"        if surprise_score >= 0.3 else
        "HIGHLY_PREDICTABLE"
    )
    content = f"""
---
type: diagnostic
subtype: draw-summary
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draw_id: {draw_id}
draw_date: {draw_date}
numbers: {numbers}
context_draws: {n_prior}
sum: {total_sum}
even: {n_even}
odd: {n_odd}
avg_gap: {avg_gap:.2f}
surprise_score: {surprise_score:.3f}
verdict: {verdict}
---

## Draw Summary: {game_name} Draw #{draw_id} ({draw_date})

**Numbers:** {' '.join(str(n) for n in numbers)}
**Sum:** {total_sum}  ·  **Even/Odd:** {n_even}/{n_odd}  ·  **Avg gap:** {avg_gap:.1f}
**Surprise score:** {surprise_score:.2f}  →  **{verdict}**

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
