"""
Streak Strategy  🔥
====================
Tracks hot and cold streaks — numbers that have appeared (or not appeared)
in many of the most recent draws.

Unlike the Bayesian strategy (which weighs all draws with exponential decay)
or Momentum (which computes a ratio to baseline), Streak simply counts raw
appearances inside a fixed recent window. It models the gambler's two most
common intuitions directly:

  Hot mode     "This number keeps coming up — ride the streak."
               Score ∝ appearances in the last `window` draws.

  Cold mode    "This number hasn't shown up in forever — it's due."
               Score ∝ absences in the last `window` draws.
               (Mean-reversion bet: statistically equivalent to hot mode
                for a fair lottery, but emotionally very different.)

Parameters
----------
  window       : int   (default 15)
      Number of recent draws to look at.
  mode         : str   (default "hot")
      "hot"   — reward current hot streaks
      "cold"  — reward current cold streaks (mean-reversion)
  min_score    : float (default 0.05)
      Minimum score for any number, so numbers with zero recent appearances
      aren't completely excluded from sampling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class StreakStrategy(BaseStrategy):
    name        = "streak"
    description = "🔥 Hot/cold streak tracking — numbers on a current run score highest"
    tier        = "statistical"
    requires_history = 15

    def __init__(
        self,
        window:    int   = 15,
        mode:      str   = "hot",
        min_score: float = 0.05,
    ) -> None:
        """
        Parameters
        ----------
        window
            Recent draws window. How many past draws to analyze for streaks.
        mode
            Streak mode. 'hot' targets numbers that appear often in the window, 
            'cold' targets numbers that are overdue in the window.
        min_score
            Minimum score floor. Ensures even the coldest/hottest numbers have a 
            tiny non-zero chance of being picked.
        """
        if mode not in ("hot", "cold"):
            raise ValueError("mode must be 'hot' or 'cold'")
        self.window    = int(window)
        self.mode      = mode
        self.min_score = float(min_score)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)

        df = df.sort_values("draw_id").reset_index(drop=True)
        recent = df.tail(min(self.window, len(df)))

        counts: dict[int, int] = {num: 0 for num in all_numbers}
        for _, row in recent.iterrows():
            for num in row["numbers"]:
                if num in counts:
                    counts[num] += 1

        n_recent = len(recent)

        if self.mode == "hot":
            raw = {num: counts[num] / n_recent for num in all_numbers}
        else:
            # cold: invert — reward numbers that did NOT appear recently
            raw = {num: (n_recent - counts[num]) / n_recent for num in all_numbers}

        max_v = max(raw.values()) if raw else 1.0
        if max_v == 0:
            return {num: 1.0 / pool for num in all_numbers}

        normed = {num: max(v / max_v, self.min_score) for num, v in raw.items()}

        # Re-normalise after applying min_score floor
        total = sum(normed.values())
        return {num: normed[num] / total * pool for num in all_numbers}  # keep ~1.0 range
