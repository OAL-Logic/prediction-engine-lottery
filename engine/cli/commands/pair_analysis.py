"""
Pair Analysis Command 🔗
========================
Co-occurrence frequency analysis for number pairs across recent draws.

Counts how often each pair of numbers appears together in the same draw,
normalised against the expected co-occurrence rate under a uniform random
model. Pairs with lift > 1.0 appear together MORE often than chance; lift
< 1.0 appear together LESS often.

Useful for:
  • Building "synergy tickets" by picking a core pair with high lift
  • Avoiding over-represented pairs (if you believe in reversion)
  • Understanding the structural texture of the draw process

Output
------
  Hot pairs table     top-N pairs by raw co-occurrence count
  Lift table          top-N pairs by lift score (observed / expected)
  Number affinity     for a specific number, its strongest co-occurrence partners
  Summary panel       most synergistic and most repellent pairs

Example
-------
  lottery pair-analysis br/lotofacil
  lottery pair-analysis br/lotofacil --draws 200 --top 15
  lottery pair-analysis br/lotofacil --focus 7      # affinity for number 7
  lottery pair-analysis br/lotofacil --export-md pairs.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

_BAR_FULL = "█"
_BAR_EMPTY = "░"


def _bar(score: float, max_score: float, width: int = 8) -> str:
    if max_score <= 0:
        return _BAR_EMPTY * width
    filled = round(min(score / max_score, 1.0) * width)
    return _BAR_FULL * filled + _BAR_EMPTY * (width - filled)


def pair_analysis(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="How many recent draws to analyse")] = 100,
    top: Annotated[int, typer.Option("--top", "-t",
        help="How many pairs to show per table")] = 15,
    focus: Annotated[Optional[int], typer.Option("--focus", "-f",
        help="Show affinity partners for this specific number")] = None,
    min_count: Annotated[int, typer.Option("--min-count",
        help="Minimum co-occurrence count to include a pair")] = 2,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append pair analysis report to this .md file")] = None,
) -> None:
    """🔗 Co-occurrence frequency analysis for number pairs.

    Shows which pairs of numbers appear together more (or less) often
    than expected by chance (lift score). Useful for synergy-based
    ticket construction.

    Example: lottery pair-analysis br/lotofacil
             lottery pair-analysis br/lotofacil --draws 200 --top 15
             lottery pair-analysis br/lotofacil --focus 7
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = hi - lo + 1

    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # ── Count co-occurrences ──────────────────────────────────────────────────
    pair_counts: Counter[tuple[int, int]] = Counter()
    num_counts:  Counter[int] = Counter()

    for row in window.itertuples():
        nums = sorted(row.numbers)
        for n in nums:
            num_counts[n] += 1
        for a, b in combinations(nums, 2):
            pair_counts[(a, b)] += 1

    if not pair_counts:
        console.print("[dim]No draw data available.[/dim]")
        raise typer.Exit(0)

    # ── Expected co-occurrence under uniform random model ─────────────────────
    # In each draw, pick 'pick' numbers from 'pool'. For any pair (a, b):
    # P(both in draw) = C(pool-2, pick-2) / C(pool, pick) = pick*(pick-1)/(pool*(pool-1))
    p_both = (pick * (pick - 1)) / (pool * (pool - 1))
    expected_per_draw = p_both * n_draws

    def lift(count: int) -> float:
        return count / expected_per_draw if expected_per_draw > 0 else 0.0

    # Filter by min_count
    filtered = {pair: cnt for pair, cnt in pair_counts.items() if cnt >= min_count}
    if not filtered:
        console.print(f"[dim]No pairs appear ≥{min_count} times. Lower --min-count.[/dim]")
        raise typer.Exit(0)

    # ── Hot pairs table (by raw count) ───────────────────────────────────────
    top_by_count = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top]
    max_cnt = top_by_count[0][1] if top_by_count else 1

    hot_table = Table(
        title=f"🔗 Most Frequent Pairs — {rules.name}  (last {n_draws} draws)",
        box=None, padding=(0, 1), header_style="bold",
    )
    hot_table.add_column("Pair",     justify="center", style="bold yellow")
    hot_table.add_column("Count",    justify="right")
    hot_table.add_column("Expected", justify="right",  style="dim")
    hot_table.add_column("Lift",     justify="right")
    hot_table.add_column("Bar",      justify="left",   style="green")

    for (a, b), cnt in top_by_count:
        lft = lift(cnt)
        lft_fmt = (
            f"[green]{lft:.2f}[/green]"  if lft >= 1.2 else
            f"[red]{lft:.2f}[/red]"      if lft <= 0.8 else
            f"[dim]{lft:.2f}[/dim]"
        )
        hot_table.add_row(
            f"{a}–{b}",
            str(cnt),
            f"{expected_per_draw:.1f}",
            lft_fmt,
            _bar(cnt, max_cnt),
        )

    console.print()
    console.print(hot_table)

    # ── Lift table (pairs with highest lift ≥ min_count) ─────────────────────
    top_by_lift = sorted(filtered.items(), key=lambda x: lift(x[1]), reverse=True)[:top]
    max_lift = lift(top_by_lift[0][1]) if top_by_lift else 1.0

    lift_table = Table(
        title="⬆️  Highest-Lift Pairs (more frequent than chance)",
        box=None, padding=(0, 1), header_style="bold",
    )
    lift_table.add_column("Pair",  justify="center", style="bold yellow")
    lift_table.add_column("Count", justify="right")
    lift_table.add_column("Lift",  justify="right",  style="bold green")
    lift_table.add_column("Bar",   justify="left",   style="green")

    for (a, b), cnt in top_by_lift:
        lft = lift(cnt)
        lift_table.add_row(
            f"{a}–{b}", str(cnt), f"{lft:.2f}", _bar(lft, max_lift),
        )

    console.print()
    console.print(lift_table)

    # ── Focus: affinity for a specific number ─────────────────────────────────
    if focus is not None:
        if not (lo <= focus <= hi):
            console.print(f"[red]--focus {focus} is outside pool range [{lo}–{hi}][/red]")
        else:
            focus_pairs = {
                (a, b): cnt for (a, b), cnt in filtered.items()
                if a == focus or b == focus
            }
            if not focus_pairs:
                console.print(f"[dim]No qualifying pairs for #{focus} (raise --draws or lower --min-count)[/dim]")
            else:
                top_focus = sorted(focus_pairs.items(), key=lambda x: x[1], reverse=True)[:top]
                max_fc = top_focus[0][1] if top_focus else 1

                aff_table = Table(
                    title=f"🎯 Affinity Partners for #{focus}",
                    box=None, padding=(0, 1), header_style="bold",
                )
                aff_table.add_column("Partner", justify="center", style="bold yellow")
                aff_table.add_column("Count",   justify="right")
                aff_table.add_column("Lift",    justify="right")
                aff_table.add_column("Bar",     justify="left",  style="green")

                for (a, b), cnt in top_focus:
                    partner = b if a == focus else a
                    lft = lift(cnt)
                    lft_fmt = (
                        f"[green]{lft:.2f}[/green]" if lft >= 1.2
                        else f"[red]{lft:.2f}[/red]" if lft <= 0.8
                        else f"[dim]{lft:.2f}[/dim]"
                    )
                    aff_table.add_row(
                        str(partner), str(cnt), lft_fmt, _bar(cnt, max_fc),
                    )

                console.print()
                console.print(aff_table)

    # ── Summary panel ─────────────────────────────────────────────────────────
    best_pair  = max(filtered, key=lambda p: lift(filtered[p]))
    worst_pair = min(filtered, key=lambda p: lift(filtered[p]))
    best_cnt   = filtered[best_pair]
    worst_cnt  = filtered[worst_pair]
    n_pairs_hot  = sum(1 for cnt in filtered.values() if lift(cnt) >= 1.5)
    n_pairs_cold = sum(1 for cnt in filtered.values() if lift(cnt) <= 0.5)

    console.print()
    console.print(Panel(
        f"[bold green]Most synergistic:[/bold green] {best_pair[0]}–{best_pair[1]}  "
        f"(lift {lift(best_cnt):.2f}, count {best_cnt})\n"
        f"[bold red]Most repellent:[/bold red]   {worst_pair[0]}–{worst_pair[1]}  "
        f"(lift {lift(worst_cnt):.2f}, count {worst_cnt})\n"
        f"[dim]Expected co-occurrence per draw: {p_both:.4f}  "
        f"(~{expected_per_draw:.1f} times in {n_draws} draws)\n"
        f"Pairs with lift ≥1.5: {n_pairs_hot}  ·  "
        f"Pairs with lift ≤0.5: {n_pairs_cold}[/dim]",
        title="🔗 Pair Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, top_by_count[:10], best_pair, worst_pair,
            best_cnt, worst_cnt, p_both, expected_per_draw,
            lift, n_pairs_hot, n_pairs_cold,
        )
        console.print(f"\n[green]✔ Pair analysis appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, top_pairs: list, best_pair: tuple, worst_pair: tuple,
    best_cnt: int, worst_cnt: int, p_both: float, expected: float,
    lift_fn, n_hot: int, n_cold: int,
) -> None:
    pair_rows = "".join(
        f"| {a}–{b} | {cnt} | {expected:.1f} | {lift_fn(cnt):.2f} |\n"
        for (a, b), cnt in top_pairs
    )

    content = f"""
---
type: diagnostic
subtype: pair-analysis
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_analysed: {n_draws}
expected_cooccurrence: {expected:.2f}
most_synergistic: {best_pair[0]}-{best_pair[1]}
most_synergistic_lift: {lift_fn(best_cnt):.2f}
most_repellent: {worst_pair[0]}-{worst_pair[1]}
most_repellent_lift: {lift_fn(worst_cnt):.2f}
pairs_lift_ge_1_5: {n_hot}
pairs_lift_le_0_5: {n_cold}
---

## Pair Analysis: {game_name} ({today.isoformat()})

**Expected co-occurrence:** {p_both:.4f} (~{expected:.1f} times in {n_draws} draws)
**Most synergistic:** {best_pair[0]}–{best_pair[1]} (lift {lift_fn(best_cnt):.2f})  ·
**Most repellent:** {worst_pair[0]}–{worst_pair[1]} (lift {lift_fn(worst_cnt):.2f})

### Top-10 Pairs by Frequency

| Pair | Count | Expected | Lift |
|------|-------|----------|------|
{pair_rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
