from __future__ import annotations

import pandas as pd
import numpy as np
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class NashEquilibriumStrategy(BaseStrategy):
    """
    Nash Equilibrium Strategy ♟️
    ===========================
    Theory: The lottery is a non-cooperative multiplayer game. The goal is not
    just to guess the numbers, but to choose a combination that other 
    players *won't choose*. In Nash Equilibrium, we play against the 
    psychological tendencies of the population.
    """
    name = "nash_equilibrium"
    description = "♟️ Nash Equilibrium (Game Theory / Prize Division)"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Nash strategy focuses on *player* behavior, not the drum.
        scores = {n: 0.5 for n in all_numbers}
        
        # Anti-popularity filters:
        # 1. Birthday dates (1-31)
        # 2. Visual patterns (diagonals, straight lines on slip)
        # 3. Just-drawn numbers (recency bias) or very overdue (gambler's fallacy)
        
        # Analyze last 3 draws to punish 'recency bias'
        last_draws = []
        for _, row in df.tail(3).iterrows():
            last_draws.extend(row['numbers'])
        last_draws = set(last_draws)

        for num in all_numbers:
            penalty = 0.0
            
            # Penalty 1: Birthday Zones (High sharing risk)
            if num <= 31:
                penalty += 0.3
                if num <= 12: penalty += 0.1 # Months are even more common
            else:
                # Bonus for high numbers (less chosen by humans)
                scores[num] += 0.2
                
            # Penalty 2: Recency Bias (Humans repeat what they just saw)
            if num in last_draws:
                penalty += 0.2
                
            # Penalty 3: Obvious slip geometry
            # Multiples of 10 are chosen frequently as they form the right column
            if num % 10 == 0:
                penalty += 0.15
            
            # 7, 13, 11 are common 'lucky' numbers
            if num in [7, 11, 13, 21, 33]:
                penalty += 0.25

            scores[num] = max(0.01, scores[num] - penalty)

        # Normalize
        max_s = max(scores.values())
        min_s = min(scores.values())
        if max_s > min_s:
            scores = {k: (v - min_s) / (max_s - min_s) for k, v in scores.items()}
            
        return scores
