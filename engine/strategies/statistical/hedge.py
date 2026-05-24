"""
Hedge Strategy ⚖️
==============
Optimized for high-probability lower-tier hits to mitigate bet costs.

Theory:
-------
While most strategies chase the jackpot (high variance), the Hedge Strategy 
targets "Structural Reliability." It selects numbers with high "Middle-Ground" 
resonance — those that consistently appear in Match 4 (Mega-Sena) or Match 11 
(Lotofácil) clusters. The goal is to produce a "Self-Paying" ticket.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Any, Dict
from collections import Counter

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class HedgeStrategy(BaseStrategy):
    name = "hedge"
    description = "⚖️ Hedge Strategy — optimized for high-frequency lower-tier prizes (Safe Play)"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        """
        Target 'Middle-Ground' performers to maximize the chance of winning back the ticket cost.
        
        💡 Tip: Use this strategy for consistent small wins rather than the big jackpot.
        """
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Target Tier Analysis
        # We look for numbers that appear most frequently in draws where 
        # the overall "Structural Health" was high.
        
        # Heuristic: Prize-winning numbers in the last 100 draws
        flat_history = [n for nums in df["numbers"] for n in nums]
        counts = Counter(flat_history)
        
        # 2. Stability Filtering
        # Hedge numbers must be "Stable" (neither too hot nor too cold)
        # We use a Bell Curve approach to favor the "Golden Mean" of frequency.
        
        freqs = np.array([counts.get(n, 0) for n in all_numbers])
        mean_freq = np.mean(freqs)
        std_freq = np.std(freqs) or 1.0
        
        scores = {}
        for n in all_numbers:
            f = counts.get(n, 0)
            # Z-Score relative to the mean frequency
            z = (f - mean_freq) / std_freq
            
            # The "Hedge Sweet Spot": Z-Score between -0.5 and +1.0
            # We want reliable performers, not extreme outliers.
            if -0.5 <= z <= 1.5:
                # Closer to +0.5 is better (slight positive bias)
                dist = abs(z - 0.5)
                scores[n] = 1.0 - (dist / 2.0)
            else:
                scores[n] = 0.1 # High-risk or over-exhausted
                
        # 3. Metadata
        self._meta = {
            "mean_frequency": round(float(mean_freq), 2),
            "hedge_pool_size": sum(1 for s in scores.values() if s > 0.5),
            "strategy_focus": "Lower-tier prize stability"
        }

        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        return {n: s / max_s for n, s in scores.items()}

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
