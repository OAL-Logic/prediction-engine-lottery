"""
Suggest Swaps Command 🔄
========================
Given a starting ticket, suggests the best number swaps to improve it.

For each number in your ticket, computes an improvement score for
every possible replacement from the pool. Ranks swaps by net gain
(replacement score minus removed number's score). Shows the top-K
most impactful single-swap improvements.

Score is a composite of:
  • Historical frequency (last 100 draws)
  • Current streak (positive = bonus)
  • Strategy consensus vote count
  • Pair synergy with the remaining numbers in the ticket

Useful for:
  • Refining a hand-picked ticket before playing
  • Post-grade improvement ("my ticket graded C — what's the best fix?")
  • Systematic ticket evolution

Example
-------
  lottery suggest-swaps br/lotofacil 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25
  lottery suggest-swaps br/lotofacil 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25 --swaps 3
  lottery suggest-swaps br/lotofacil 1 3 5 7 10 11 13 15 19 20 21 22 23 24 25 --export-md swaps.md
"""

from __future__ import annotations

from collections import Counter
from datetime import date as _date
from itertools import combinations
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()


def _num_score(
    num: int,
    ticket_context: list[int],
    freq: Counter,
    n_draws: int,
    streaks: dict,
    votes: Counter,
    pair_counts: Counter,
    expected_cooc: float,
    pick: int,
    pool_size: int,
    n_strats: int,
) -> float:
    """Composite score for a number given the surrounding ticket context."""
    baseline_rate = pick / pool_size
    expected_freq = baseline_rate * n_draws

    # Frequency sub-score (0–1)
    f = freq.get(num, 0)
    freq_s = min(1.0, f / (expected_freq * 2) if expected_freq > 0 else 0.5)

    # Streak sub-score (0–1); hot=good, cold=bad
    stk = streaks.get(num, 0)
    streak_s = max(0.0, min(1.0, 0.5 + stk * 0.1))

    # Consensus sub-score (0–1)
    v = votes.get(num, 0)
    cons_s = v / n_strats if n_strats > 0 else 0.5

    # Pair synergy with rest of ticket
    ctx = [n for n in ticket_context if n != num]
    lifts = []
    for partner in ctx:
        key = (min(num, partner), max(num, partner))
        cnt = pair_counts.get(key, 0)
        lift = cnt / expected_cooc if expected_cooc > 0 else 1.0
        lifts.append(lift)
    avg_lift = sum(lifts) / len(lifts) if lifts else 1.0
    pair_s = min(1.0, avg_lift / 2.0)

    return 0.30 * freq_s + 0.25 * streak_s + 0.25 * cons_s + 0.20 * pair_s


def suggest_swaps(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    numbers: Annotated[list[int], typer.Argument(help="Your current ticket numbers")],
    swaps: Annotated[int, typer.Option("--swaps", "-k",
        help="How many swap suggestions to show")] = 5,
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="How many recent draws for context")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append swap suggestions to this .md file")] = None,
) -> None:
    """🔄 Suggest best number swaps to improve a ticket.

    Evaluates every possible single-swap and ranks them by net score
    gain (replacement score minus removed score).

    Example: lottery suggest-swaps br/lotofacil 1 3 5 7 10 -- ...25
             lottery suggest-swaps br/lotofacil ... --swaps 3
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pick    = rules.pick_count
    pool_size = hi - lo + 1

    # Validate ticket
    ticket = sorted(set(numbers))
    invalid = [n for n in ticket if not (lo <= n <= hi)]
    if invalid:
        console.print(f"[red]Numbers out of range [{lo}–{hi}]: {invalid}[/red]")
        raise typer.Exit(1)

    pool = set(range(lo, hi + 1))
    candidates = pool - set(ticket)   # numbers NOT in the ticket

    n_draws = min(draws, len(df))
    window  = df.tail(n_draws)

    # ── Build context data ────────────────────────────────────────────────────
    freq: Counter[int] = Counter()
    pair_counts: Counter[tuple[int, int]] = Counter()
    for row in window.itertuples():
        for n in row.numbers:
            freq[n] += 1
        for a, b in combinations(sorted(row.numbers), 2):
            pair_counts[(a, b)] += 1

    p_both = (pick * (pick - 1)) / (pool_size * (pool_size - 1))
    expected_cooc = p_both * n_draws

    # Streaks
    def _streak(num: int) -> int:
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
        return streak if val else -(streak)

    streaks = {n: _streak(n) for n in range(lo, hi + 1)}

    # Strategy consensus votes
    votes: Counter[int] = Counter()
    n_strats = 0
    try:
        from engine.strategies import get_strategy
        fast_names = ["bayesian", "weighted", "monte_carlo"]
        win_df = df.tail(50)
        for name in fast_names:
            try:
                strat = get_strategy(name)
                res = strat.suggest(win_df, rules, count=1, temperature=0.0)
                for n in res.tickets[0]:
                    votes[n] += 1
                n_strats += 1
            except Exception:
                pass
    except Exception:
        pass

    # ── Score current ticket ──────────────────────────────────────────────────
    def score_num(num: int, context: list[int]) -> float:
        return _num_score(
            num, context, freq, n_draws, streaks, votes,
            pair_counts, expected_cooc, pick, pool_size, max(1, n_strats),
        )

    ticket_scores = {n: score_num(n, ticket) for n in ticket}
    current_total = sum(ticket_scores.values())

    # ── Evaluate all single swaps ─────────────────────────────────────────────
    swap_options: list[dict] = []

    with console.status("[dim]Evaluating swaps…[/dim]"):
        for remove in ticket:
            new_ctx = [n for n in ticket if n != remove]
            rm_score = ticket_scores[remove]
            for add in candidates:
                add_score = score_num(add, new_ctx + [add])
                gain = add_score - rm_score
                swap_options.append({
                    "remove": remove,
                    "add":    add,
                    "rm_score": rm_score,
                    "add_score": add_score,
                    "gain":  gain,
                })

    top_swaps = sorted(swap_options, key=lambda s: s["gain"], reverse=True)[:swaps]

    # ── Display current ticket scores ─────────────────────────────────────────
    cur_table = Table(
        title=f"🎯 Current Ticket Scores — {rules.name}",
        box=None, padding=(0, 1), header_style="bold",
    )
    cur_table.add_column("Number", justify="center", style="bold yellow")
    cur_table.add_column("Score",  justify="right")
    cur_table.add_column("Freq%",  justify="right",  style="dim")
    cur_table.add_column("Streak", justify="right")
    cur_table.add_column("Tier",   justify="center")

    for n in ticket:
        s   = ticket_scores[n]
        f   = freq.get(n, 0)
        fq  = f / n_draws if n_draws else 0.0
        stk = streaks.get(n, 0)
        stk_fmt = (
            f"[green]+{stk}[/green]" if stk > 0
            else f"[cyan]{stk}[/cyan]" if stk < 0
            else "[dim]0[/dim]"
        )
        tier = "[bold green]KEEP[/bold green]" if s >= 0.6 else "[yellow]SWAP?[/yellow]" if s < 0.4 else "[dim]OK[/dim]"
        cur_table.add_row(str(n), f"{s:.3f}", f"{fq:.0%}", stk_fmt, tier)

    console.print()
    console.print(cur_table)

    # ── Display swap recommendations ──────────────────────────────────────────
    swap_table = Table(
        title=f"🔄 Top-{swaps} Swap Suggestions",
        box=None, padding=(0, 1), header_style="bold",
    )
    swap_table.add_column("Remove",    justify="center", style="bold red")
    swap_table.add_column("→ Add",     justify="center", style="bold green")
    swap_table.add_column("Rm score",  justify="right",  style="dim")
    swap_table.add_column("Add score", justify="right",  style="bold green")
    swap_table.add_column("Net gain",  justify="right")

    for s in top_swaps:
        gain_fmt = (
            f"[bold green]+{s['gain']:.3f}[/bold green]" if s["gain"] > 0.05
            else f"[green]+{s['gain']:.3f}[/green]" if s["gain"] > 0
            else f"[dim]{s['gain']:.3f}[/dim]"
        )
        swap_table.add_row(
            str(s["remove"]),
            str(s["add"]),
            f"{s['rm_score']:.3f}",
            f"{s['add_score']:.3f}",
            gain_fmt,
        )

    console.print()
    console.print(swap_table)

    # ── Best improved ticket ──────────────────────────────────────────────────
    if top_swaps and top_swaps[0]["gain"] > 0:
        best = top_swaps[0]
        improved = sorted([n for n in ticket if n != best["remove"]] + [best["add"]])
        imp_str = "  ".join(str(n) for n in improved)
        console.print()
        console.print(Panel(
            f"[bold yellow]{imp_str}[/bold yellow]\n"
            f"[dim]Best single swap: remove [bold]{best['remove']}[/bold] → "
            f"add [bold]{best['add']}[/bold]  "
            f"(net gain: {best['gain']:+.3f})[/dim]",
            title="🔄 Improved Ticket",
            border_style="green",
        ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            ticket, top_swaps, current_total / len(ticket) if ticket else 0,
        )
        console.print(f"\n[green]✔ Swap suggestions appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    ticket: list[int], top_swaps: list[dict], avg_score: float,
) -> None:
    ticket_str = ", ".join(str(n) for n in ticket)
    rows = "".join(
        f"| {s['remove']} | {s['add']} | {s['rm_score']:.3f} | "
        f"{s['add_score']:.3f} | {s['gain']:+.3f} |\n"
        for s in top_swaps
    )

    best = top_swaps[0] if top_swaps else None
    improved = ""
    if best and best["gain"] > 0:
        imp_nums = sorted([n for n in ticket if n != best["remove"]] + [best["add"]])
        improved = ", ".join(str(n) for n in imp_nums)

    content = f"""
---
type: diagnostic
subtype: suggest-swaps
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
ticket: [{ticket_str}]
avg_score: {avg_score:.3f}
best_swap_remove: {best['remove'] if best else 'none'}
best_swap_add: {best['add'] if best else 'none'}
best_swap_gain: {f"{best['gain']:.3f}" if best else "0"}
improved_ticket: [{improved}]
---

## Swap Suggestions: {game_name} ({today.isoformat()})

**Ticket:** {ticket_str}  ·  **Avg score:** {avg_score:.3f}

| Remove | Add | Rm score | Add score | Net gain |
|--------|-----|----------|-----------|----------|
{rows}
{f"**Best improved ticket:** {improved}" if improved else ""}

"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
