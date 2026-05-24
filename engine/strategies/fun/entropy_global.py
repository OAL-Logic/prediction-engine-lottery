"""
Global Entropy Strategy 🌪️
=========================
Correlates numbers with simulated 'Global Entropy' jitter.

Theory:
-------
High-entropy periods (volatile markets, seismic activity, solar flares) 
are thought by some to increase 'Collective Unconscious' noise. 
This strategy identifies numbers that traditionally hit during these 
noisy periods.
"""

from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd
from datetime import date
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class GlobalEntropyStrategy(BaseStrategy):
    name = "entropy_global"
    description = "🌪️ Global Entropy — correlate numbers with simulated collective-unconscious jitter"
    tier = "fun"
    requires_history = 50

    def __init__(self, volatility_weight: float = 1.0) -> None:
        self.v_weight = float(volatility_weight)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Simulate Historical Entropy Peaks
        # In a real app, this would fetch VIX / Seismic data.
        # Here we simulate via deterministic hash of the date.
        
        def _get_entropy(d_str: str) -> float:
            h = hashlib.sha256(d_str.encode()).hexdigest()
            return int(h[:4], 16) / 65535.0  # 0.0 to 1.0

        hist_entropy = [(_get_entropy(str(row["date"])[:10]), row["numbers"]) for _, row in df.iterrows()]
        
        # 2. Get Today's Entropy
        target_date = kwargs.get("draw_date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date[:10])
        today_entropy = _get_entropy(target_date.isoformat())
        
        # 3. Score numbers by frequency in draws with SIMILAR entropy
        tolerance = 0.2 * self.v_weight
        matched_draws = [nums for e, nums in hist_entropy if abs(e - today_entropy) < tolerance]
        
        if not matched_draws:
            return {n: 0.5 for n in all_numbers}
            
        from collections import Counter
        counts = Counter([n for nums in matched_draws for n in nums])
        max_c = max(counts.values()) if counts else 1
        
        return {n: counts.get(n, 0) / max_c for n in all_numbers}
