"""
Ticket Grade Command 🎓
=======================
Evaluate and score a user-supplied ticket against engine diagnostics.

Grades the ticket across four dimensions:
  1. Frequency score    — how often each number appeared in recent draws
  2. Streak score       — are the numbers currently on hot or cold runs?
  3. Pair synergy       — co-occurrence lift for pairs within the ticket
  4. Consensus score    — how much the engine's strategy consensus agrees

Produces an overall grade (A–F) and actionable suggestions for improvement.

Usage
-----
  lottery ticket-grade br/lotofacil 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25
  lottery ticket-grade br/mega-sena 4 12 17 24 36 55
  lottery ticket-grade br/lotofacil 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25 --draws 100
  lottery ticket-grade br/lotofacil 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25 --export-md grade.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from itertools import combinations
from pathlib import Path
from typing import Annotated, Optional

import math
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter
from engine.modules import filters

console = Console()

def _letter_grade(score: float) -> str:
    """Convert 0–100 score to letter grade."""
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def _grade_colour(grade: str) -> str:
    if grade.startswith("A"):
        return "bold green"
    if grade.startswith("B"):
        return "green"
    if grade.startswith("C"):
        return "yellow"
    return "red"


def ticket_grade(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    numbers: Annotated[list[int], typer.Argument(help="Your ticket numbers")],
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="How many recent draws to use for context")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append grade report to this .md file")] = None,
) -> None:
    """🎓 Grade a ticket against engine diagnostics.

    Scores your ticket across frequency, streak, pair synergy,
    consensus, and structural dimensions. Returns a letter grade and suggestions.

    Example: lottery ticket-grade br/lotofacil 1 3 5 7 10 -- \\
                       11 13 15 19 20 21 22 23 24 25
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool    = hi - lo + 1

    # Validate ticket
    ticket = sorted(set(numbers))
    invalid = [n for n in ticket if not (lo <= n <= hi)]
    if invalid:
        console.print(f"[red]Numbers out of range [{lo}–{hi}]: {invalid}[/red]")
        raise typer.Exit(1)

    if len(ticket) != pick:
        console.print(
            f"[yellow]⚠ Ticket has {len(ticket)} numbers; "
            f"{rules.name} expects {pick}. Grading anyway.[/yellow]"
        )

    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # ── Build baseline data ───────────────────────────────────────────────────
    freq: Counter[int] = Counter()
    for row in window.itertuples():
        for n in row.numbers:
            freq[n] += 1

    baseline_rate = pick / pool
    expected_freq = baseline_rate * n_draws

    # Pair co-occurrence
    pair_counts: Counter[tuple[int, int]] = Counter()
    for row in window.itertuples():
        for a, b in combinations(sorted(row.numbers), 2):
            pair_counts[(a, b)] += 1

    p_both = (pick * (pick - 1)) / (pool * (pool - 1))
    expected_cooc = p_both * n_draws

    def pair_lift(a: int, b: int) -> float:
        key = (min(a, b), max(a, b))
        cnt = pair_counts.get(key, 0)
        return cnt / expected_cooc if expected_cooc > 0 else 0.0

    # Current streak for each pool number
    def current_streak(num: int) -> int:
        streak = 0
        val = None
        for row in reversed(list(window.itertuples())):
            hit = num in row.numbers
            if val is None:
                val = hit
            if hit == val:
                streak += 1
            else:
                break
        return streak if val else -streak

    # ── Dimension 1: Frequency score ──────────────────────────────────────────
    freq_scores = []
    for n in ticket:
        f = freq.get(n, 0)
        ratio = f / expected_freq if expected_freq > 0 else 0.5
        score = min(100, 50 + 50 * (ratio - 1.0))
        score = max(0, score)
        freq_scores.append(score)
    freq_dimension = sum(freq_scores) / len(freq_scores) if freq_scores else 50

    # ── Dimension 2: Streak score ─────────────────────────────────────────────
    streak_scores = []
    streaks = {}
    for n in ticket:
        stk = current_streak(n)
        streaks[n] = stk
        score = max(0, min(100, 50 + stk * 10))
        streak_scores.append(score)
    streak_dimension = sum(streak_scores) / len(streak_scores) if streak_scores else 50

    # ── Dimension 3: Pair synergy ─────────────────────────────────────────────
    pair_lifts = []
    for a, b in combinations(ticket, 2):
        pair_lifts.append(pair_lift(a, b))
    avg_lift = sum(pair_lifts) / len(pair_lifts) if pair_lifts else 1.0
    pair_dimension = max(0, min(100, avg_lift * 50))

    # ── Dimension 4: Structural balance ───────────────────────────────────────
    odd_count = filters.get_odd_count(ticket)
    hl_counts = filters.get_high_low_counts(ticket, hi)
    ac_value  = filters.get_ac_value(ticket)
    num_sum   = sum(ticket)
    
    # Ideal Odd/Even is approx 50/50
    oe_ratio = odd_count / pick
    oe_score = max(0, 100 - abs(oe_ratio - 0.5) * 200)
    
    # Ideal High/Low is approx 50/50
    hl_ratio = hl_counts["high"] / pick
    hl_score = max(0, 100 - abs(hl_ratio - 0.5) * 200)
    
    # AC Value baseline
    # Typical: Pick-5 (4-6), Pick-6 (7-10)
    ideal_ac_min = 4 if pick == 5 else 7 if pick == 6 else pick - 2
    ideal_ac_max = 6 if pick == 5 else 10 if pick == 6 else pick + 2
    if ac_value < ideal_ac_min:
        ac_score = 50 * (ac_value / ideal_ac_min)
    elif ac_value > ideal_ac_max:
        ac_score = 100 - 20 * (ac_value - ideal_ac_max)
    else:
        ac_score = 100
    
    # Sum range baseline (bell curve)
    # Estimated mean sum = pick * (pool_size / 2)
    mean_sum = pick * (lo + hi) / 2
    std_sum  = (hi - lo) / 4 * math.sqrt(pick) # rough approximation
    z_sum = abs(num_sum - mean_sum) / std_sum
    sum_score = max(0, 100 - z_sum * 30)
    
    structural_dimension = (oe_score + hl_score + ac_score + sum_score) / 4

    # ── Dimension 5: Consensus score ─────────────────────────────────────────
    consensus_score = 50.0
    consensus_ticket: list[int] = []
    try:
        from engine.strategies import get_strategy
        fast_names = ["bayesian", "weighted", "monte_carlo"]
        win_df = df.tail(50)
        votes: Counter[int] = Counter()
        for name in fast_names:
            try:
                strat = get_strategy(name)
                res = strat.suggest(win_df, rules, count=1, temperature=0.0)
                for n in res.tickets[0]:
                    votes[n] += 1
            except Exception:
                pass
        if votes:
            consensus_ticket = sorted(
                sorted(votes.keys(), key=lambda n: votes[n], reverse=True)[:pick]
            )
            overlap = len(set(ticket) & set(consensus_ticket))
            consensus_score = (overlap / pick) * 100
    except Exception:
        pass

    # ── Per-number detail table ───────────────────────────────────────────────
    detail_table = Table(
        title=f"🎓 Ticket Grade — {rules.name}",
        box=None, padding=(0, 1), header_style="bold",
    )
    detail_table.add_column("Number",   justify="center", style="bold yellow")
    detail_table.add_column("Freq%",    justify="right",  style="dim")
    detail_table.add_column("Streak",   justify="right")
    detail_table.add_column("Consensus",justify="center")
    detail_table.add_column("Score",    justify="right")

    num_scores = []
    for n in ticket:
        f = freq.get(n, 0)
        fq = f / n_draws if n_draws else 0.0
        stk = streaks.get(n, 0)
        in_cons = n in consensus_ticket
        stk_fmt = (
            f"[green]+{stk}[/green]" if stk > 0
            else f"[cyan]{stk}[/cyan]" if stk < 0
            else "[dim]0[/dim]"
        )
        cons_fmt = "[green]✔[/green]" if in_cons else "[dim]·[/dim]"
        ratio = f / expected_freq if expected_freq > 0 else 0.5
        n_score = (
            0.4 * max(0, min(100, 50 + 50 * (ratio - 1.0))) +
            0.3 * max(0, min(100, 50 + stk * 10)) +
            0.3 * (100 if in_cons else 0)
        )
        num_scores.append(n_score)
        detail_table.add_row(
            str(n),
            f"{fq:.0%}",
            stk_fmt,
            cons_fmt,
            f"{n_score:.0f}",
        )

    console.print()
    console.print(detail_table)

    # ── Overall grade ─────────────────────────────────────────────────────────
    overall = (
        0.20 * freq_dimension +
        0.20 * streak_dimension +
        0.15 * pair_dimension +
        0.25 * structural_dimension +
        0.20 * consensus_score
    )
    grade = _letter_grade(overall)
    colour = _grade_colour(grade)

    # Suggestions
    suggestions = []
    if structural_dimension < 60:
        if ac_score < 70: suggestions.append(f"Arithmetic Complexity (AC={ac_value}) is outside ideal range")
        if oe_score < 70: suggestions.append(f"Odd/Even distribution is unbalanced ({odd_count} Odd)")
        if hl_score < 70: suggestions.append(f"High/Low distribution is unbalanced ({hl_counts['high']} High)")
        if sum_score < 70: suggestions.append(f"Total sum ({num_sum}) is far from the statistical mean")
    
    if streak_dimension < 40:
        suggestions.append("Several cold-streak numbers — consider swapping for HOT numbers")
    if freq_dimension < 40:
        suggestions.append("Low historical frequency — check rank-numbers for higher-frequency alternatives")
    if pair_dimension < 40:
        suggestions.append("Below-average pair synergy — use pair-analysis --focus to find better partners")
    if consensus_score < 30:
        suggestions.append(f"Low consensus overlap with strategies — engine favours: {sorted(consensus_ticket)}")
    
    if not suggestions:
        suggestions.append("No major weaknesses detected")

    sug_str = "\n".join(f"  • {s}" for s in suggestions)
    ticket_str = "  ".join(str(n) for n in ticket)

    console.print()
    console.print(Panel(
        f"[bold yellow]{ticket_str}[/bold yellow]\n\n"
        f"[{colour}]Grade: {grade}[/{colour}]  "
        f"[dim](Overall: {overall:.0f}/100)[/dim]\n\n"
        f"[dim]Frequency: {freq_dimension:.0f}/100  "
        f"·  Streak: {streak_dimension:.0f}/100  "
        f"·  Synergy: {pair_dimension:.0f}/100\n"
        f"Structure: {structural_dimension:.0f}/100  "
        f"·  Consensus: {consensus_score:.0f}/100[/dim]\n\n"
        f"[dim]Suggestions:\n{sug_str}[/dim]",
        title="🎓 Ticket Grade",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            ticket, grade, overall, freq_dimension, streak_dimension,
            pair_dimension, structural_dimension, consensus_score, suggestions,
        )
        console.print(f"\n[green]✔ Grade report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    ticket: list[int], grade: str, overall: float,
    freq_d: float, streak_d: float, pair_d: float, 
    struct_d: float, cons_d: float,
    suggestions: list[str],
) -> None:
    ticket_str = ", ".join(str(n) for n in ticket)
    sug_md = "\n".join(f"- {s}" for s in suggestions)

    content = f"""
---
type: diagnostic
subtype: ticket-grade
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket: [{ticket_str}]
grade: {grade}
overall_score: {overall:.1f}
freq_score: {freq_d:.1f}
streak_score: {streak_d:.1f}
pair_score: {pair_d:.1f}
structural_score: {struct_d:.1f}
consensus_score: {cons_d:.1f}
---

## Ticket Grade: {game_name} ({today.isoformat()})

**Ticket:** {ticket_str}
**Grade:** {grade}  ·  **Overall:** {overall:.0f}/100

| Dimension | Score |
|-----------|-------|
| Frequency | {freq_d:.0f}/100 |
| Streak | {streak_d:.0f}/100 |
| Pair synergy | {pair_d:.0f}/100 |
| Structure | {struct_d:.0f}/100 |
| Consensus | {cons_d:.0f}/100 |

**Suggestions:**
{sug_md}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
