"""
Lyapunov Chaos Strategy 🦋
==========================
Calculates a proxy for the largest Lyapunov exponent of the historical draw sequence
(using the sequence of draw sums) to identify whether the system is in a state of 
extreme chaos (high divergence) or a "window of order" (low divergence). 

If in chaos: seeks high-entropy numbers (numbers with high variance in their intervals).
If in order: seeks low-entropy, highly stable periodic numbers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class LyapunovChaosStrategy(BaseStrategy):
    name = "lyapunov_chaos"
    description = "🦋 Janelas de Ordem no Caos (Expoente de Lyapunov)"
    tier = "fun"

    requires_history = 30

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Calculate sequence of sums
        sums = [sum(row.numbers) for row in df.itertuples()]
        
        # 2. Calculate local divergence (Lyapunov proxy)
        # We compare the difference between consecutive sums
        diffs = np.abs(np.diff(sums))
        
        # If the recent differences are expanding exponentially, we are in chaos.
        # Let's take the log of the ratio of recent diffs
        # Avoid division by zero
        diffs = np.where(diffs == 0, 1, diffs)
        
        # Simple proxy: average log divergence over the last 10 draws
        if len(diffs) > 10:
            recent_diffs = diffs[-10:]
            lyapunov_proxy = np.mean(np.log(recent_diffs))
        else:
            lyapunov_proxy = 0.0
            
        # Threshold for chaos vs order
        is_chaos = lyapunov_proxy > np.mean(np.log(diffs)) if len(diffs) > 0 else False
        
        # 3. Calculate number entropy (variance of gaps)
        gaps = {n: [] for n in all_numbers}
        last_seen = {n: -1 for n in all_numbers}
        
        for i, row in enumerate(df.itertuples()):
            for num in row.numbers:
                if last_seen[num] != -1:
                    gaps[num].append(i - last_seen[num])
                last_seen[num] = i
                
        scores = {}
        for n in all_numbers:
            if len(gaps[n]) > 1:
                variance = np.var(gaps[n])
            else:
                variance = 0.0
                
            scores[n] = variance

        # 4. Score mapping based on chaotic regime
        max_v = max(scores.values()) if scores else 1.0
        if max_v == 0: max_v = 1.0
        
        final_scores = {}
        for n in all_numbers:
            norm_var = scores[n] / max_v
            if is_chaos:
                # In chaos, we embrace the chaos: high variance numbers
                final_scores[n] = norm_var
            else:
                # In a window of order, we seek stability: low variance numbers
                final_scores[n] = 1.0 - norm_var
                
        # Normalize
        max_s = max(final_scores.values()) if final_scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: v / max_s for n, v in final_scores.items()}
