"""
Deviation Module
================
Tracks how many draws have elapsed since each number last appeared.
Numbers that haven't appeared in a long time are considered "overdue".

Note: in a truly fair lottery every draw is independent — "overdue" is a
statistical observation, not a prediction guarantee. We surface it as data.

Outputs
-------
- draws_since_last: draws elapsed since each number was last seen
- overdue:          numbers exceeding their expected return interval
- expected_interval: average gap between appearances for a given number
- gap_history:      full list of gaps between appearances per number
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from engine.adapters import DrawRules


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class DeviationResult:
    """Output of deviation.analyze()."""

    total_draws: int
    table: pd.DataFrame          # number, last_seen_draw, draws_since_last,
    #                              expected_interval, deviation_ratio
    overdue: List[int]           # numbers where draws_since_last > expected_interval
    streak_free: List[int]       # numbers not drawn in the longest consecutive streak
    gap_stats: Dict[int, dict]   # per-number: mean/std/max gap

    def __repr__(self) -> str:
        return (
            f"DeviationResult(draws={self.total_draws}, "
            f"overdue={self.overdue[:5]}, streak_free={self.streak_free[:5]})"
        )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def analyze(
    df: pd.DataFrame,
    rules: DrawRules,
    top_n: int = 10,
) -> DeviationResult:
    """
    Compute deviation (recency / overdue) statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical draw DataFrame sorted by draw_id ascending.
    rules : DrawRules
        Lottery rules — used to build the full number universe.
    top_n : int
        Number of overdue / streak-free numbers to return.

    Returns
    -------
    DeviationResult
    """
    if df.empty:
        raise ValueError("DataFrame is empty — fetch data first.")

    df = df.sort_values("draw_id").reset_index(drop=True)
    total_draws = len(df)
    lo, hi = rules.number_range
    all_numbers = list(range(lo, hi + 1))

    # Expected appearances per draw and expected return interval
    numbers_per_draw = rules.pick_count
    pool_size = hi - lo + 1
    expected_freq = numbers_per_draw / pool_size           # P(n appears in a single draw)
    expected_interval = 1.0 / expected_freq                # avg draws between appearances

    rows = []
    gap_stats: Dict[int, dict] = {}

    for number in all_numbers:
        # Find draw indices where this number appeared
        appearance_indices = [
            idx for idx, nums in enumerate(df["numbers"]) if number in nums
        ]

        if not appearance_indices:
            last_seen = -1
            draws_since = total_draws
            gaps: List[int] = []
        else:
            last_seen = int(df.iloc[appearance_indices[-1]]["draw_id"])
            draws_since = total_draws - 1 - appearance_indices[-1]

            # Compute consecutive gaps between appearances
            gaps = [
                appearance_indices[i + 1] - appearance_indices[i]
                for i in range(len(appearance_indices) - 1)
            ]

        # Gap statistics
        if gaps:
            gap_stats[number] = {
                "mean": float(np.mean(gaps)),
                "std": float(np.std(gaps)),
                "max": int(np.max(gaps)),
                "min": int(np.min(gaps)),
            }
        else:
            gap_stats[number] = {"mean": None, "std": None, "max": None, "min": None}

        deviation_ratio = draws_since / expected_interval

        rows.append(
            {
                "number": number,
                "last_seen_draw": last_seen,
                "draws_since_last": draws_since,
                "expected_interval": round(expected_interval, 2),
                "deviation_ratio": round(deviation_ratio, 4),
            }
        )

    table = pd.DataFrame(rows).sort_values("draws_since_last", ascending=False).reset_index(drop=True)

    overdue = table[table["deviation_ratio"] > 1.0].head(top_n)["number"].tolist()
    streak_free = table.head(top_n)["number"].tolist()

    return DeviationResult(
        total_draws=total_draws,
        table=table,
        overdue=overdue,
        streak_free=streak_free,
        gap_stats=gap_stats,
    )


def print_report(res: DeviationResult) -> None:
    """Print a rich-formatted table of the deviation (overdue) analysis."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    
    table = Table(
        title=f"Deviation Analysis — Overdue & Gaps",
        box=None,
        padding=(0, 2)
    )
    table.add_column("Number", style="bold yellow")
    table.add_column("Last Seen", justify="right", style="dim")
    table.add_column("Since (d)", justify="right")
    table.add_column("Exp. Gap", justify="right", style="dim")
    table.add_column("Ratio", justify="right")

    # Show top overdue numbers
    # We'll show the top_n from analyze (already sorted by draws_since_last)
    display_rows = res.table.head(15)
    
    for _, row in display_rows.iterrows():
        ratio = row["deviation_ratio"]
        color = "white"
        if ratio > 2.0: color = "bold red"
        elif ratio > 1.5: color = "red"
        elif ratio > 1.0: color = "yellow"
        
        table.add_row(
            str(int(row["number"])),
            f"#{int(row['last_seen_draw'])}",
            str(int(row["draws_since_last"])),
            str(row["expected_interval"]),
            f"[{color}]{ratio:.2f}[/{color}]"
        )

    console.print(table)
    console.print(f"\n⌛ [bold]Overdue (>1.0):[/bold]  {res.overdue}")
    console.print(f"❄️ [bold]Longest Gaps:[/bold]    {res.streak_free}")
