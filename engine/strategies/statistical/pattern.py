"""
Pattern Matching Strategy
==========================
Scores numbers by how often they participate in combinations that fit the
historical pattern envelope (sum, odd/even ratio, high/low ratio, consecutive
pair count).

Sprint 1.1 refactor (2026-04-28)
--------------------------------
Previously this strategy did empirical Monte-Carlo sampling (`n_samples=5000`)
to estimate the sum-range envelope. That has been replaced with the analytical
truncated-normal range from ``engine.modules.sum_range`` — accurate, fast, and
no `n_samples` parameter to tune. The empirical envelope is still used for
odd/even, high/low, and consecutive-pair distributions, since those *are*
genuinely game-specific (they depend on the historical realization, not just
the rules).

The sampling loop that scores numbers by participation is preserved but
shrunk; ~2000 samples is now enough since the sum filter is exact.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from collections import Counter

from engine.adapters import DrawRules
from engine.modules import sum_range as _sum_range
from engine.strategies import BaseStrategy, register


@register
class PatternStrategy(BaseStrategy):
    name = "pattern"
    description = "🧩 Pattern matching — numbers that fit historical sum/odd-even/high-low distributions"
    tier = "statistical"

    requires_history = 50

    def __init__(self, n_samples: int = 2000, sum_coverage: float = 0.70) -> None:
        """
        Parameters
        ----------
        n_samples
            Number of random combinations to score per draw. Lower than the
            pre-1.1 default (5000) because the sum filter is now analytical.
        sum_coverage
            Central-probability mass for the sum envelope (default 0.70 — the
            "Most Probable Range of Sums" Smart Luck publishes).
        """
        self.n_samples = int(n_samples)
        self.sum_coverage = float(sum_coverage)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        df = df.sort_values("draw_id").reset_index(drop=True)
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pick = rules.pick_count
        mid = (lo + hi) / 2

        draws = [list(row) for row in df["numbers"]]

        # --- Analytical sum envelope (replaces 5th–95th percentile sampling) ---
        sum_lo, sum_hi, _midpoint, _sigma = _sum_range.most_probable_range(
            rules, coverage=self.sum_coverage,
        )

        # --- Empirical envelopes for the genuinely-historical distributions ---
        odd_ratios  = [sum(1 for n in d if n % 2 != 0) / pick for d in draws]
        high_ratios = [sum(1 for n in d if n > mid) / pick for d in draws]
        consec      = [_count_consecutive(d) for d in draws]

        odd_lo,  odd_hi  = np.percentile(odd_ratios,  5), np.percentile(odd_ratios, 95)
        high_lo, high_hi = np.percentile(high_ratios, 5), np.percentile(high_ratios,95)
        con_lo,  con_hi  = np.percentile(consec,      5), np.percentile(consec,     95)

        # --- Base sampling weights from frequency ---
        flat  = [n for d in draws for n in d]
        freq  = Counter(flat)
        raw   = np.array([freq.get(n, 1) for n in all_numbers], dtype=float)
        probs = raw / raw.sum()

        # --- Score each number by how often it appears in "good" combinations ---
        
        # --- Vectorized sampling using Gumbel-max trick ---
        # Generate all combos at once without loops
        u = np.random.uniform(size=(self.n_samples, len(all_numbers)))
        # Add small epsilon to avoid log(0) or div by zero
        keys = -np.log(u + 1e-10) / (probs + 1e-10)
        
        # Get indices of top `pick` items per sample
        combo_indices = np.argsort(keys, axis=1)[:, -pick:]
        
        # Map indices back to actual numbers
        numbers_array = np.array(all_numbers)
        combos = numbers_array[combo_indices]
        
        # Vectorized calculations
        sums = combos.sum(axis=1)
        odds = (combos % 2 != 0).sum(axis=1) / pick
        highs = (combos > mid).sum(axis=1) / pick
        
        # Consecutive calculation
        combos_sorted = np.sort(combos, axis=1)
        consec = (np.diff(combos_sorted, axis=1) == 1).sum(axis=1)
        
        # Filter mask
        mask = (
            (sums >= sum_lo) & (sums <= sum_hi) &
            (odds >= odd_lo) & (odds <= odd_hi) &
            (highs >= high_lo) & (highs <= high_hi) &
            (consec >= con_lo) & (consec <= con_hi)
        )
        
        # Get passing combos
        good_combos = combos[mask]
        good = len(good_combos)
        
        if good == 0:
            return {n: float(freq.get(n, 0)) for n in all_numbers}
            
        # Count frequencies in good combos
        flat_good = good_combos.flatten()
        unique, counts = np.unique(flat_good, return_counts=True)
        counter = dict(zip(unique, counts))
        
        total = good * pick
        return {n: counter.get(n, 0) / total for n in all_numbers}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _count_consecutive(numbers: list[int]) -> int:
    """Count how many pairs of consecutive integers appear in a draw."""
    s = set(numbers)
    return sum(1 for n in numbers if n + 1 in s)
