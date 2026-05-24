"""
Momentum Strategy  📈
=====================
RSI-inspired frequency momentum — rewards numbers that are accelerating
in appearance frequency relative to their long-term baseline.

Concept
-------
Borrowed from quantitative trading: the Relative Strength Index (RSI) measures
whether an asset is trending above or below its historical average. Applied to
lottery numbers:

  momentum(n) = recent_freq(n) / long_term_freq(n)

  momentum > 1  → number is appearing more than usual  ("hot momentum")
  momentum < 1  → number is appearing less than usual  ("cooling momentum")
  momentum = 1  → number is exactly on its historical average

Modes
-----
  "hot"         Score ∝ upward momentum  (recent_freq > baseline).
                Bet that current runs continue.

  "cold"        Score ∝ downward momentum (recent_freq < baseline).
                Bet on mean-reversion — overdue numbers are primed to return.

  "divergence"  Score ∝ absolute deviation from baseline (either direction).
                Useful in ensembles: surfaces numbers that are doing something
                unusual regardless of direction.

Parameters
----------
  short_window : int   (default 20)
      Recent window in draws. Measures the "fast" frequency.
  mode         : str   (default "hot")
      "hot" | "cold" | "divergence"
  min_baseline : float (default 0.001)
      Minimum long-term frequency to avoid div-by-zero on unseen numbers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class MomentumStrategy(BaseStrategy):
    name        = "momentum"
    description = "📈 RSI-style frequency momentum — trending numbers score highest"
    tier        = "statistical"
    requires_history = 25

    def __init__(
        self,
        short_window: int   = 20,
        mode:         str   = "hot",
        min_baseline: float = 0.001,
    ) -> None:
        """
        Parameters
        ----------
        short_window
            Recent draws window. Measures the "fast" frequency over this many recent draws.
        mode
            Momentum mode. "hot" (trending up), "cold" (trending down, due to return), 
            or "divergence" (unusual activity in either direction).
        min_baseline
            Baseline frequency floor. Prevents division-by-zero errors for numbers 
            that have never appeared historically.
        """
        if mode not in ("hot", "cold", "divergence"):
            raise ValueError("mode must be 'hot', 'cold', or 'divergence'")
        self.short_window = int(short_window)
        self.mode         = mode
        self.min_baseline = float(min_baseline)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)

        df = df.sort_values("draw_id").reset_index(drop=True)
        n_draws = len(df)

        # Long-term frequency (all draws)
        lt_counts: dict[int, int] = {num: 0 for num in all_numbers}
        for _, row in df.iterrows():
            for num in row["numbers"]:
                if num in lt_counts:
                    lt_counts[num] += 1
        lt_freq = {num: lt_counts[num] / max(n_draws, 1) for num in all_numbers}

        # Short-term frequency (last short_window draws)
        window = min(self.short_window, n_draws)
        recent_df = df.tail(window)
        st_counts: dict[int, int] = {num: 0 for num in all_numbers}
        for _, row in recent_df.iterrows():
            for num in row["numbers"]:
                if num in st_counts:
                    st_counts[num] += 1
        st_freq = {num: st_counts[num] / window for num in all_numbers}

        # Compute momentum ratio
        raw: dict[int, float] = {}
        for num in all_numbers:
            baseline   = max(lt_freq[num], self.min_baseline)
            ratio      = st_freq[num] / baseline

            if self.mode == "hot":
                # Reward upward momentum; floor at 0
                raw[num] = max(ratio - 1.0, 0.0)
            elif self.mode == "cold":
                # Reward downward momentum (mean-reversion bet); floor at 0
                raw[num] = max(1.0 - ratio, 0.0)
            else:
                # Divergence: absolute deviation from baseline in either direction
                raw[num] = abs(ratio - 1.0)

        max_v = max(raw.values()) if raw else 1.0
        if max_v == 0:
            # All numbers at baseline — uniform fallback
            return {num: 1.0 / pool for num in all_numbers}

        return {num: raw[num] / max_v for num in all_numbers}
