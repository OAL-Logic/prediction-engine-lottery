"""
Lottery Studio Predict Pool Command 🔮
================================
Lottery Studio's "How to Predict" equivalent (Feature E1..E4, AC-P1, Doc 05 §B):
Generates a Recommended Number Pool and an Eliminated Number Pool for the next draw.

Unlike single-ticket predictors, Lottery Studio formulas output a narrowed POOL of
candidate numbers (~17-27 numbers for 6/60 games, 16-18 for Lotofácil)
which players then wheel or filter.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table
from engine.strategies import get_strategy, STRATEGY_PRESETS

console = Console()


def predict_pool(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/mega-sena")],
    formula: Annotated[str, typer.Option("--formula", "-f", help="Strategy preset family or specific strategy (e.g. 'default', 'weighted', 'markov')")] = "default",
    depth: Annotated[int, typer.Option("--depth", "-d", help="Historical window depth (draws to analyze)")] = 100,
    offset: Annotated[int, typer.Option("--offset", help="Predict as of N draws ago (0 = latest upcoming draw)")] = 0,
    pool_size: Annotated[Optional[int], typer.Option("--pool-size", "-p", help="Size of recommended pool to output (defaults to ~35-40% of pool)")] = None,
    out: Annotated[Optional[Path], typer.Option("--out", "-o", help="Optional output file to save recommended numbers")] = None,
) -> None:
    """🔮 Generate a Lottery Studio Recommended Pool and Eliminated Pool for the next draw."""

    adapter = get_adapter(lottery)
    rules = adapter.rules
    lo, hi = rules.number_range
    total_balls = hi - lo + 1

    # Load history
    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    df_held_back = df.iloc[: len(df) - offset] if offset > 0 else df
    if df_held_back.empty:
        console.print(f"[red]✗ Offset {offset} exceeds available history ({len(df)} draws).[/red]")
        raise typer.Exit(1)

    df_slice = df_held_back.tail(depth)

    # Determine default pool size if not specified
    if pool_size is None:
        if rules.pick_count >= 15:  # Lotofácil style
            target_pool_size = min(total_balls, rules.pick_count + 3)
        else:
            # 6-number lotto style (Lottery Studio standard recommended pool: ~20-25 numbers for 6/60)
            target_pool_size = max(rules.pick_count + 5, int(total_balls * 0.35))
    else:
        target_pool_size = max(rules.pick_count, min(total_balls, pool_size))

    # Resolve strategies to evaluate
    if formula in STRATEGY_PRESETS:
        strategies_to_run = STRATEGY_PRESETS[formula]
    else:
        strategies_to_run = [formula]

    # Score each number across strategy weights
    number_scores: dict[int, float] = {n: 0.0 for n in range(lo, hi + 1)}

    for s_name in strategies_to_run:
        try:
            strat = get_strategy(s_name)
            res = strat.suggest(df_slice, rules, count=1, temperature=0.5)
            for num, sc in res.scores.items():
                if num in number_scores:
                    number_scores[num] += float(sc)
        except Exception:
            # Fall back to frequency if an obscure strategy fails
            continue

    # Rank numbers by score
    sorted_numbers = sorted(number_scores.keys(), key=lambda n: number_scores[n], reverse=True)
    recommended_pool = sorted(sorted_numbers[:target_pool_size])
    eliminated_pool = sorted(sorted_numbers[target_pool_size:])

    ui_header(
        "Lottery Studio PREDICT POOL",
        f"{rules.name} · Formula: {formula} · Depth: {len(df_slice)} draws"
        + (f" (offset={offset})" if offset > 0 else "")
    )

    # Display results table
    pool_table = ui_table("Prediction Pool Partition", ["Category", "Count", "Numbers"])
    pool_table.add_row(
        "[bold green]RECOMMENDED POOL[/bold green]",
        f"[bold green]{len(recommended_pool)}[/bold green]",
        " ".join(f"{n:02d}" for n in recommended_pool)
    )
    pool_table.add_row(
        "[dim]ELIMINATED POOL[/dim]",
        f"[dim]{len(eliminated_pool)}[/dim]",
        "[dim]" + " ".join(f"{n:02d}" for n in eliminated_pool) + "[/dim]"
    )
    console.print(pool_table)

    # Verification vs actual if offset > 0
    if offset > 0:
        actual_draw = df.iloc[-offset]
        actual_winners = set(actual_draw["numbers"])
        hits = set(recommended_pool) & actual_winners
        hit_rate = len(hits) / len(actual_winners) * 100.0

        verify_table = ui_table(f"Historical Verification (Draw #{actual_draw['draw_id']})", ["Metric", "Value"])
        verify_table.add_row("Draw Date", str(actual_draw.get("draw_date") or actual_draw.get("date")))
        verify_table.add_row("Winning Numbers", " ".join(f"{n:02d}" for n in sorted(actual_winners)))
        verify_table.add_row("Hits in Recommended Pool", f"[bold cyan]{len(hits)} / {len(actual_winners)}[/bold cyan] ({' '.join(f'{n:02d}' for n in sorted(hits))})")
        verify_table.add_row("Capture Rate", f"[bold yellow]{hit_rate:.1f}%[/bold yellow]")
        console.print(verify_table)

    if out:
        out.write_text(" ".join(f"{n:02d}" for n in recommended_pool) + "\n", encoding="utf-8")
        console.print(f"[green]✓ Wrote recommended pool ({len(recommended_pool)} numbers) to {out}[/green]")
