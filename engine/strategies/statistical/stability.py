"""
Stability Strategy ⚖️
====================
Scores numbers based on the consistency (low variance) of their hit rate.

Theory:
-------
Some numbers hit in short, intense bursts (volatile), while others hit 
regularly and consistently over long periods (stable). This strategy 
identifies 'Old Reliable' numbers that have the lowest variance in their 
return intervals.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class StabilityStrategy(BaseStrategy):
    name = "stability"
    description = "⚖️ Stability — score numbers by the consistency (low variance) of their historical hit rate"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_draws = len(df)
        
        # 1. Build Binary Matrix
        matrix = np.zeros((n_draws, hi + 1))
        for i, row in enumerate(df["numbers"]):
            matrix[i, row] = 1.0
            
        # 2. Calculate Rolling Hit Rate Variance
        # We split history into 5 blocks
        block_size = n_draws // 5
        variances = {}
        
        for n in all_numbers:
            hit_rates = []
            for b in range(5):
                block = matrix[b*block_size : (b+1)*block_size, n]
                hit_rates.append(block.mean())
            
            # Variance of hit rates across blocks
            # Lower variance = More stable
            v = np.var(hit_rates) if hit_rates else 1.0
            variances[n] = v
            
        # 3. Score = 1.0 - normalised variance
        max_v = max(variances.values()) if variances else 1.0
        scores = {n: 1.0 - (variances[n] / max_v) for n in all_numbers}
        
        return scores
