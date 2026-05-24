"""
Correlation Module
==================
Analyses which numbers tend to appear *together* in the same draw.

Methods
-------
- co_occurrence_matrix : raw count of draws where both Ni and Nj appeared
- lift_matrix          : observed co-occurrence / (expected under independence)
                         lift > 1 → appear together more than chance
                         lift < 1 → appear together less than chance
- top_pairs            : N pairs with highest lift (positive association)
- avoided_pairs        : N pairs with lowest lift (negative association)

Note: with ~60 numbers there are ~1 770 unique pairs. Interesting pairs
with lift > 2 are genuinely unusual; most will hover near 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd

from engine.adapters import DrawRules


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class CorrelationResult:
    """Output of correlation.analyze()."""

    total_draws: int
    co_occurrence: pd.DataFrame   # symmetric matrix, index/cols = number labels
    lift: pd.DataFrame            # same shape, lift values
    top_pairs: List[Tuple[int, int, float]]    # (n1, n2, lift)
    avoided_pairs: List[Tuple[int, int, float]]
    top_triplets: List[Tuple[int, int, int, int]] # (n1, n2, n3, count)

    def __repr__(self) -> str:
        top = [(a, b, round(l, 3)) for a, b, l in self.top_pairs[:3]]
        return (
            f"CorrelationResult(draws={self.total_draws}, "
            f"top_pairs={top})"
        )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def analyze(
    df: pd.DataFrame,
    rules: DrawRules,
    top_n: int = 20,
) -> CorrelationResult:
    """
    Compute pairwise co-occurrence and lift for all number pairs.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical draw DataFrame.
    rules : DrawRules
        Lottery rules — used to build the number universe.
    top_n : int
        Number of top/avoided pairs to return.

    Returns
    -------
    CorrelationResult
    """
    if df.empty:
        raise ValueError("DataFrame is empty — fetch data first.")

    total_draws = len(df)
    lo, hi = rules.number_range
    all_numbers = list(range(lo, hi + 1))
    n = len(all_numbers)
    idx = {num: i for i, num in enumerate(all_numbers)}

    # ---------------------------------------------------------------------------
    # Build co-occurrence matrix (N × N)
    # ---------------------------------------------------------------------------
    co_matrix = np.zeros((n, n), dtype=np.int32)

    for numbers in df["numbers"]:
        nums = sorted(set(numbers))
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                a, b = idx[nums[i]], idx[nums[j]]
                co_matrix[a, b] += 1
                co_matrix[b, a] += 1

    co_df = pd.DataFrame(co_matrix, index=all_numbers, columns=all_numbers)

    # ---------------------------------------------------------------------------
    # Individual appearance counts (diagonal gives marginal probability)
    # ---------------------------------------------------------------------------
    counts = np.array(
        [(df["numbers"].apply(lambda nums: number in nums)).sum() for number in all_numbers],
        dtype=np.float64,
    )
    marginal_probs = counts / total_draws  # P(number appears in a draw)

    # ---------------------------------------------------------------------------
    # Lift matrix: lift(i,j) = P(i∩j) / (P(i) * P(j))
    # ---------------------------------------------------------------------------
    lift_matrix = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(i + 1, n):
            observed = co_matrix[i, j] / total_draws
            expected = marginal_probs[i] * marginal_probs[j]
            lift_val = observed / expected if expected > 0 else 0.0
            lift_matrix[i, j] = lift_val
            lift_matrix[j, i] = lift_val

    lift_df = pd.DataFrame(lift_matrix, index=all_numbers, columns=all_numbers)

    # ---------------------------------------------------------------------------
    # Extract top / avoided pairs
    # ---------------------------------------------------------------------------
    pairs: List[Tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if co_matrix[i, j] > 0:
                pairs.append((all_numbers[i], all_numbers[j], float(lift_matrix[i, j])))

    pairs.sort(key=lambda x: x[2], reverse=True)
    top_pairs = pairs[:top_n]
    avoided_pairs = sorted(pairs, key=lambda x: x[2])[:top_n]

    # ---------------------------------------------------------------------------
    # Triplets (Brute force recent history)
    # ---------------------------------------------------------------------------
    from collections import Counter
    triplet_counts = Counter()
    # Only look at last 500 draws for triplets to keep it fast
    recent_df = df.tail(500)
    for numbers in recent_df["numbers"]:
        nums = sorted(set(numbers))
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                for k in range(j + 1, len(nums)):
                    triplet_counts[(nums[i], nums[j], nums[k])] += 1
    
    top_triplets = []
    for t, c in triplet_counts.most_common(top_n):
        top_triplets.append((t[0], t[1], t[2], c))

    return CorrelationResult(
        total_draws=total_draws,
        co_occurrence=co_df,
        lift=lift_df,
        top_pairs=top_pairs,
        avoided_pairs=avoided_pairs,
        top_triplets=top_triplets,
    )


def print_report(res: CorrelationResult) -> None:
    """Print a rich-formatted summary of the correlation analysis."""
    from rich.console import Console
    from rich.table import Table
    from rich.columns import Columns
    from rich.panel import Panel

    console = Console()
    
    # 1. Top Pairs Table
    pair_table = Table(title="Top Associated Pairs (High Lift)", box=None, padding=(0, 2))
    pair_table.add_column("Pair", style="bold cyan")
    pair_table.add_column("Lift", justify="right")
    
    for n1, n2, lift in res.top_pairs[:10]:
        pair_table.add_row(f"{n1} & {n2}", f"{lift:.3f}")

    # 2. Avoided Pairs Table
    avoid_table = Table(title="Top Avoided Pairs (Low Lift)", box=None, padding=(0, 2))
    avoid_table.add_column("Pair", style="bold magenta")
    avoid_table.add_column("Lift", justify="right")
    
    for n1, n2, lift in res.avoided_pairs[:10]:
        avoid_table.add_row(f"{n1} & {n2}", f"{lift:.3f}")

    # 3. Top Triplets Table
    trip_table = Table(title="Top Triplets (Most Frequent)", box=None, padding=(0, 2))
    trip_table.add_column("Triplet", style="bold yellow")
    trip_table.add_column("Count", justify="right")
    
    for n1, n2, n3, count in res.top_triplets[:10]:
        trip_table.add_row(f"{n1}, {n2}, {n3}", str(count))

    console.print(Columns([pair_table, avoid_table]))
    console.print()
    console.print(trip_table)
    
    console.print("\n[dim]Note: Lift > 1.0 means numbers appear together more often than expected by chance.[/dim]")
