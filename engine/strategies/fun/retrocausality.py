"""
Quantum Retrocausality Strategy ⏳
==================================
Simulates "echoes from the future". Uses an extrapolated moving average
(a simple delay-differential proxy) to predict the future target 'Sum'
of the next draw. Then, scores numbers based on how well they fit into 
that future target sum, heavily favoring numbers that appeared exactly
at Fibonacci delay intervals (3, 5, 8, 13 draws ago) acting as temporal echoes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class RetrocausalityStrategy(BaseStrategy):
    name = "retrocausality"
    description = "⏳ Retrocausalidade Quântica (Ecos do Futuro)"
    tier = "fun"

    requires_history = 20

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Project the future sum
        sums = [sum(row.numbers) for row in df.itertuples()]
        if len(sums) < 5:
            return {n: 0.5 for n in all_numbers}
            
        # Simple linear extrapolation of the last 5 sums
        x = np.arange(5)
        y = np.array(sums[-5:])
        coeffs = np.polyfit(x, y, 1)
        future_sum_target = coeffs[0] * 5 + coeffs[1]
        
        # Expected average per number to hit the sum target
        target_avg = future_sum_target / rules.pick_count
        
        # 2. Score numbers based on proximity to target_avg
        scores = {}
        max_dist = max(abs(hi - target_avg), abs(lo - target_avg))
        if max_dist == 0: max_dist = 1.0
        
        for n in all_numbers:
            # Base score: closer to target average is better
            dist = abs(n - target_avg)
            scores[n] = 1.0 - (dist / max_dist)
            
        # 3. Temporal Echoes (Fibonacci delays)
        # If a number appeared exactly 3, 5, 8, or 13 draws ago, it gets a "retrocausal boost"
        # as if it is echoing backward from the future sequence.
        
        fib_delays = [3, 5, 8, 13]
        total_draws = len(df)
        
        for delay in fib_delays:
            if total_draws >= delay:
                echo_row = df.iloc[-delay]
                for n in echo_row.numbers:
                    if n in scores:
                        scores[n] += 0.2 # Boost
                        
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: min(1.0, v / max_s) for n, v in scores.items()}
