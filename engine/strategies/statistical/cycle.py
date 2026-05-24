"""
Cycle Analysis Strategy 🚲
=========================
Scores numbers based on their detected 'Hit Cycles'.

Theory:
-------
Every number in a lottery has a natural cycle of return. This strategy 
identifies the mean and standard deviation of gaps between hits for each 
number and scores them based on how close they are to their expected 'due' 
point in the current cycle.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class CycleStrategy(BaseStrategy):
    name = "cycle"
    description = "🚲 Cycle Analysis — score numbers by proximity to their mean hit interval"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_draws = len(df)
        
        # 1. Calculate Gaps for each number
        # matrix[d, n] = 1 if n in draw d
        matrix = np.zeros((n_draws, hi + 1))
        for i, row in enumerate(df["numbers"]):
            matrix[i, row] = 1.0
            
        scores = {}
        for n in all_numbers:
            indices = np.where(matrix[:, n] == 1)[0]
            if len(indices) < 3:
                scores[n] = 0.5
                continue
                
            gaps = np.diff(indices)
            mean_gap = np.mean(gaps)
            last_idx = indices[-1]
            draws_since = (n_draws - 1) - last_idx
            
            # Proximity to cycle completion
            # If mean_gap = 10 and draws_since = 9, score is high.
            # If mean_gap = 10 and draws_since = 20, score is also high (overdue).
            
            if draws_since >= mean_gap:
                # Overdue: higher score as it gets further past mean
                score = 0.8 + min(0.2, (draws_since - mean_gap) / mean_gap)
            else:
                # Approaching mean: score rises as draws_since -> mean_gap
                score = 0.3 + (draws_since / mean_gap) * 0.5
                
            scores[n] = float(score)
            
        # Normalise
        max_s = max(scores.values()) if scores else 1.0
        return {n: s / max_s for n, s in scores.items()}
