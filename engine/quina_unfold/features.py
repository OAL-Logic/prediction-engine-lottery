"""
FeatureExtractor — parity, sum, decile/quadrant, repeats, and frequency
z-scores for every number in the 1-80 range.
==========================================================================
Wraps the existing engine.modules.frequency / engine.modules.skips
primitives rather than recomputing them, so this stays consistent with
every other strategy in the engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.modules import frequency as frequency_module
from engine.modules import skips as skips_module


@dataclass
class NumberFeatures:
    number: int
    count: int
    frequency: float
    freq_z_score: float          # rolling z-score deviation from uniform expectation
    now_skip: int                # draws since last appearance
    average_skip: float          # historical mean gap between appearances
    delay_ratio: float           # now_skip / average_skip — >1 means "overdue"
    cycle_class: str             # "hot" | "warm" | "cold" | "overdue"
    decile: int                  # 1..10  (8 numbers per decile across 1-80)
    quadrant: int                # 1..4   (20 numbers per quadrant across 1-80)
    is_repeat_of_prior: bool
    is_adjacent_to_prior: bool   # within +/-1 of any number in the prior draw


class FeatureExtractor:
    """Computes the per-number feature table used by FilterPipeline / PoolOptimizer."""

    def __init__(self, rules: DrawRules, hot_z: float = 0.5, cold_z: float = -0.5, overdue_ratio: float = 1.3):
        self.rules = rules
        self.hot_z = hot_z
        self.cold_z = cold_z
        self.overdue_ratio = overdue_ratio

    # ------------------------------------------------------------------

    def compute(self, df: pd.DataFrame, prior_draw: Optional[List[int]] = None, window: Optional[int] = None) -> pd.DataFrame:
        """
        Return a DataFrame indexed by `number` (1..80) with one NumberFeatures
        row per number. `window`, if given, restricts frequency/skip stats to
        the trailing N draws (rolling z-score); default uses full history.
        """
        if df.empty:
            raise ValueError("DataFrame is empty — fetch history first.")

        history = df.tail(window) if window else df
        lo, hi = self.rules.number_range
        prior = sorted(prior_draw) if prior_draw else []
        prior_set = set(prior)
        adjacent_set = {n + d for n in prior for d in (-1, 1)} - prior_set

        freq_res = frequency_module.analyze(history, self.rules, top_n=len(range(lo, hi + 1)))
        freq_by_number = freq_res.table.set_index("number")

        rows = []
        for n in range(lo, hi + 1):
            skip = skips_module.compute_skip_profile(history, n)
            avg_skip = skip["average_skip"] if skip["average_skip"] > 0 else float(skip["total_draws"])
            now_skip = skip["now_skip"]
            delay_ratio = (now_skip / avg_skip) if avg_skip > 0 else 0.0

            f_row = freq_by_number.loc[n]
            z = float(f_row["z_score"])

            if delay_ratio >= self.overdue_ratio:
                cycle_class = "overdue"
            elif z >= self.hot_z:
                cycle_class = "hot"
            elif z <= self.cold_z:
                cycle_class = "cold"
            else:
                cycle_class = "warm"

            rows.append(
                NumberFeatures(
                    number=n,
                    count=int(f_row["count"]),
                    frequency=float(f_row["frequency"]),
                    freq_z_score=z,
                    now_skip=now_skip,
                    average_skip=avg_skip,
                    delay_ratio=round(delay_ratio, 4),
                    cycle_class=cycle_class,
                    decile=self._decile(n, lo, hi),
                    quadrant=self._quadrant(n, lo, hi),
                    is_repeat_of_prior=n in prior_set,
                    is_adjacent_to_prior=n in adjacent_set,
                )
            )

        table = pd.DataFrame([r.__dict__ for r in rows]).set_index("number", drop=False)
        return table

    # ------------------------------------------------------------------

    @staticmethod
    def _decile(n: int, lo: int, hi: int, n_deciles: int = 10) -> int:
        span = hi - lo + 1
        width = span / n_deciles
        return min(n_deciles, int((n - lo) // width) + 1)

    @staticmethod
    def _quadrant(n: int, lo: int, hi: int, n_quadrants: int = 4) -> int:
        span = hi - lo + 1
        width = span / n_quadrants
        return min(n_quadrants, int((n - lo) // width) + 1)
