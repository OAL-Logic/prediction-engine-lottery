from __future__ import annotations

import pandas as pd
import random
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class CrowdAntagonismStrategy(BaseStrategy):
    """
    Crowd Antagonism Strategy (Anti-Mass Filter) 🚫👥
    ================================================
    This strategy applies the theory that very 'popular' numbers
    (birthdays, famous dates, common lucky numbers like 7, 13)
    should be avoided to avoid sharing the prize with thousands of people
    and because 'Collective Intent' can create negative quantum interference.
    """
    name = "crowd_antagonism"
    description = "🚫 Anti-Mass Filter (Avoids popular and saturated numbers)"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        scores = {n: 1.0 for n in range(lo, hi + 1)}
        
        # 'Psychologically Popular' Numbers (Based on human bias studies)
        # 1-12: Months (Birthdays) - Very popular
        # 1-31: Days (Birthdays) - Popular
        # 7, 13, 21: Universal 'Lucky' numbers
        
        for num in range(lo, hi + 1):
            penalty = 0.0
            if num <= 12: penalty += 0.4 # Months
            elif num <= 31: penalty += 0.2 # Days
            
            if num in [7, 13, 21, 33, 44]: penalty += 0.3 # Common cabalistic numbers
            
            # Penalty for ending in 0 or 5 (human tendency to pick round numbers)
            if num % 10 == 0 or num % 10 == 5: penalty += 0.1
            
            scores[num] = max(0.1, 1.0 - penalty)
            
            # Adds a 'Standard Deviation' noise to not be deterministic
            scores[num] += random.uniform(-0.05, 0.05)
            
        return scores
