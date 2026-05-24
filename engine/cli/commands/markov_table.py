"""
Markov Table Command 🔗
=======================
Diagnostic surface for the Markov Chain strategy.

The markov strategy scores numbers by "what tends to follow what in
consecutive draws". This command makes that inner workings visible:

  Default       Top-K followers per number across the whole pool
  --from N      Full transition row for number N (all followers ranked)
  --stationary  Stationary distribution π — the long-run probability of
                each number appearing under the chain (reveals whether
                the chain actually converges or is uniform)
  --last-draw   Transition probabilities from the most recent draw only
                (what the strategy used to generate its last suggestion)

Transition matrix construction
-------------------------------
  M[i, j] = count of draws where i appeared in draw t AND j appeared
             in draw t+1 (first-order transition)
  P[i, j] = M[i, j] / sum(M[i, :])  (row-normalised probability)

Stationary distribution via power iteration:
  π(0) = uniform
  π(k+1) = π(k) · P  until ‖π(k+1) − π(k)‖ < ε

A perfectly uniform lottery has a uniform stationary distribution.
Deviations flag persistent structural biases in the transition chain.

Example
-------
  lottery markov-table br/lotofacil
  lottery markov-table br/lotofacil --from 13 --top 10
  lottery markov-table br/lotofacil --stationary
  lottery markov-table br/lotofacil --last-draw
  lottery markov-table br/mega-sena --top 3 --export-md markov.md
"""

from __future__ import annotations

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


def _build_matrix(df, pool: list[int]) -> tuple[dict, dict]:
    """Build raw count matrix and row-normalised P matrix."""
    idx  = {num: i for i, num in enumerate(pool)}
    n    = len(pool)
    mat  = [[0.0] * n for _ in range(n)]

    rows = list(df.itertuples())
    for t in range(len(rows) - 1):
        for i in rows[t].numbers:
            if i not in idx:
                continue
            ri = idx[i]
            for j in rows[t + 1].numbers:
                if j in idx:
                    mat[ri][idx[j]] += 1.0

    P = []
    for row in mat:
        s = sum(row)
        P.append([v / s if s > 0 else 1.0 / n for v in row])

    return mat, P


def _stationary(P: list[list[float]]) -> list[float]:
    """Power-iteration stationary distribution."""
    n  = len(P)
    pi = [1.0 / n] * n
    for _ in range(600):
        new_pi = [sum(pi[i] * P[i][j] for i in range(n)) for j in range(n)]
        s      = sum(new_pi)
        new_pi = [v / s for v in new_pi]
        if all(abs(new_pi[j] - pi[j]) < 1e-9 for j in range(n)):
            break
        pi = new_pi
    return new_pi


def markov_table(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    from_num: Annotated[Optional[int], typer.Option("--from", "-f",
        help="Show full transition row for this number")] = None,
    stationary: Annotated[bool, typer.Option("--stationary", "-S",
        help="Show stationary distribution instead")] = False,
    last_draw: Annotated[bool, typer.Option("--last-draw", "-l",
        help="Show transitions from the most recent draw")] = False,
    top: Annotated[int, typer.Option("--top", "-k",
        help="Top-K followers to show per number")] = 5,
    score_window: Annotated[int, typer.Option("--limit", "-L",
        help="Draws used to build the matrix")] = 200,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append Markov table report to this .md file")] = None,
) -> None:
    """🔗 Diagnostic surface for the Markov Chain strategy.

    Exposes transition probabilities, stationary distribution, and
    per-number follower rankings from the existing markov strategy.

    Example: lottery markov-table br/lotofacil
             lottery markov-table br/lotofacil --from 13
             lottery markov-table br/lotofacil --stationary
    """
    adapter = get_adapter(lottery)
    df      = adapter.fetch()
    rules   = adapter.rules
    lo, hi  = rules.number_range
    pool    = list(range(lo, hi + 1))
    n       = len(pool)

    n_draws = min(score_window, len(df))
    df_win  = df.tail(n_draws)

    if len(df_win) < 20:
        console.print("[dim]Not enough draw data.[/dim]")
        raise typer.Exit(0)

    _, P = _build_matrix(df_win, pool)

    # ── --stationary mode ──────────────────────────────────────────────────
    if stationary:
        pi     = _stationary(P)
        uniform = 1.0 / n
        ranked = sorted(enumerate(pool), key=lambda x: -pi[x[0]])

        tbl = Table(
            title=f"🔗 Markov Stationary Distribution — {rules.name}  (window={n_draws})",
            box=None, padding=(0, 1), header_style="bold",
        )
        tbl.add_column("Rank",    justify="right", style="dim")
        tbl.add_column("Number",  justify="center", style="bold yellow")
        tbl.add_column("π",       justify="right")
        tbl.add_column("vs uniform", justify="right")
        tbl.add_column("Bar",     justify="left",  style="dim")

        for rank, (i, num) in enumerate(ranked, 1):
            p_val  = pi[i]
            delta  = p_val - uniform
            bar_w  = round(p_val / max(pi) * 20)
            bar    = "█" * bar_w + "░" * (20 - bar_w)
            delta_col = "green" if delta > 0 else "red" if delta < 0 else "dim"
            tbl.add_row(
                str(rank),
                str(num),
                f"{p_val:.4f}",
                f"[{delta_col}]{delta:+.4f}[/{delta_col}]",
                bar,
            )

        console.print()
        console.print(tbl)

        max_dev_i, max_dev_num = max(enumerate(pool), key=lambda x: abs(pi[x[0]] - uniform))
        console.print()
        console.print(Panel(
            f"[dim]Stationary vs uniform — max deviation: "
            f"#{max_dev_num} ({pi[max_dev_i] - uniform:+.4f})\n"
            f"If all πᵢ ≈ {uniform:.4f} the chain is essentially uniform (expected for fair lotteries)\n"
            f"Window: {n_draws} draws  ·  Pool: {n} numbers[/dim]",
            title="🔗 Stationary Distribution",
            border_style="yellow",
        ))
        return

    # ── --from mode ────────────────────────────────────────────────────────
    if from_num is not None:
        if from_num not in range(lo, hi + 1):
            console.print(f"[red]Number {from_num} is out of range [{lo},{hi}].[/red]")
            raise typer.Exit(2)
        idx    = {num: i for i, num in enumerate(pool)}
        ri     = idx[from_num]
        row_p  = P[ri]
        ranked = sorted(enumerate(pool), key=lambda x: -row_p[x[0]])

        tbl = Table(
            title=f"🔗 Transitions from #{from_num} — {rules.name}  (window={n_draws})",
            box=None, padding=(0, 1), header_style="bold",
        )
        tbl.add_column("Rank",     justify="right", style="dim")
        tbl.add_column("Follows",  justify="center", style="bold yellow")
        tbl.add_column("P(%)",     justify="right")
        tbl.add_column("Bar",      justify="left",  style="dim")

        shown = 0
        for rank, (j, num) in enumerate(ranked, 1):
            p_val = row_p[j]
            if shown >= (top if top > 0 else n):
                break
            bar_w = round(p_val / max(row_p) * 20) if max(row_p) > 0 else 0
            bar   = "█" * bar_w + "░" * (20 - bar_w)
            tbl.add_row(str(rank), str(num), f"{p_val:.2%}", bar)
            shown += 1

        console.print()
        console.print(tbl)
        console.print()
        console.print(Panel(
            f"[dim]Showing top {shown} followers of #{from_num}\n"
            f"Based on {n_draws} consecutive draw pairs[/dim]",
            title=f"🔗 #{from_num} Transitions",
            border_style="yellow",
        ))

        if export_md:
            _append_md_from(export_md, lottery, rules.name, _date.today(),
                            from_num, n_draws, ranked[:top], P, pool)
        return

    # ── --last-draw mode ────────────────────────────────────────────────────
    if last_draw:
        last_nums = list(df_win.tail(1)["numbers"].iloc[0])
        idx = {num: i for i, num in enumerate(pool)}
        agg: list[float] = [0.0] * n
        for num in last_nums:
            if num in idx:
                ri = idx[num]
                for j in range(n):
                    agg[j] += P[ri][j]
        total = sum(agg)
        agg   = [v / total if total > 0 else 1.0 / n for v in agg]
        ranked = sorted(enumerate(pool), key=lambda x: -agg[x[0]])

        tbl = Table(
            title=f"🔗 Transitions from last draw — {rules.name}  (window={n_draws})",
            box=None, padding=(0, 1), header_style="bold",
        )
        tbl.add_column("Rank",    justify="right", style="dim")
        tbl.add_column("Number",  justify="center", style="bold yellow")
        tbl.add_column("Score",   justify="right")
        tbl.add_column("Bar",     justify="left",  style="dim")

        for rank, (j, num) in enumerate(ranked[: top * 3], 1):
            p_val = agg[j]
            bar_w = round(p_val / agg[ranked[0][0]] * 20)
            bar   = "█" * bar_w + "░" * (20 - bar_w)
            tbl.add_row(str(rank), str(num), f"{p_val:.4f}", bar)

        last_str = " ".join(str(n) for n in sorted(last_nums))
        console.print()
        console.print(tbl)
        console.print()
        console.print(Panel(
            f"Last draw numbers: {last_str}\n"
            f"[dim]Aggregated transition probabilities from each number in last draw\n"
            f"(This is the scores that the markov strategy uses internally)[/dim]",
            title="🔗 Last-Draw Transition Scores",
            border_style="yellow",
        ))
        return

    # ── Default: top-K followers per number ───────────────────────────────
    tbl = Table(
        title=f"🔗 Markov Top-{top} Transitions — {rules.name}  (window={n_draws})",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("From #",   justify="center", style="bold yellow")
    tbl.add_column(f"Top {top} followers (P%)", justify="left")

    uniform = 1.0 / n
    for i, num in enumerate(pool):
        row_p = P[i]
        top_k = sorted(range(n), key=lambda j: -row_p[j])[:top]
        parts = []
        for j in top_k:
            p_val    = row_p[j]
            colour   = "green" if p_val > uniform * 1.2 else "dim"
            parts.append(f"[{colour}]{pool[j]}→{p_val:.0%}[/{colour}]")
        tbl.add_row(str(num), "  ".join(parts))

    console.print()
    console.print(tbl)

    # ── Summary panel ──────────────────────────────────────────────────────
    # Most "predictable" number = highest max-row probability
    max_p_i = max(range(n), key=lambda i: max(P[i]))
    max_p   = max(P[max_p_i])
    max_num = pool[max_p_i]
    max_j   = max(range(n), key=lambda j: P[max_p_i][j])

    console.print()
    console.print(Panel(
        f"Most focused transition: [bold]#{max_num} → #{pool[max_j]}[/bold] "
        f"(P = {max_p:.2%})\n"
        f"[dim]Uniform baseline: {uniform:.2%} per number  ·  "
        f"Window: {n_draws} draws  ·  Matrix: {n}×{n}[/dim]",
        title="🔗 Markov Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md_default(export_md, lottery, rules.name, _date.today(),
                           n_draws, n, top, P, pool, max_num, pool[max_j], max_p)


def _append_md_from(path, lottery, game_name, today, from_num, n_draws, ranked, P, pool):
    idx = {num: i for i, num in enumerate(pool)}
    ri  = idx[from_num]
    rows = ""
    for rank, (j, num) in enumerate(ranked, 1):
        rows += f"| {rank} | {num} | {P[ri][j]:.2%} |\n"

    content = f"""
---
type: diagnostic
subtype: markov-table
mode: from
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
from_number: {from_num}
draws_window: {n_draws}
---

## Markov Transitions from #{from_num}: {game_name} ({today.isoformat()})

| Rank | Follower | P(%) |
|------|----------|------|
{rows}
"""
    _write_md(path, content)


def _append_md_default(path, lottery, game_name, today, n_draws, pool_n, top,
                       P, pool, max_from, max_to, max_p):
    content = f"""
---
type: diagnostic
subtype: markov-table
mode: default
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_window: {n_draws}
matrix_size: {pool_n}
top_k: {top}
max_transition_from: {max_from}
max_transition_to: {max_to}
max_transition_p: {max_p:.4f}
---

## Markov Table: {game_name} ({today.isoformat()})

**Window:** {n_draws} draws  ·  **Matrix:** {pool_n}×{pool_n}  ·  **Top-K:** {top}
**Most focused:** #{max_from} → #{max_to} (P = {max_p:.2%})
"""
    _write_md(path, content)


def _write_md(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
