"""
Crowd Avoidance Strategy (Anti-Popular) — Gail Howard Idea 7 & 8.
==============================================================
Scores numbers based on psychological biases rather than historical frequency.

The goal is to maximize Expected Value (EV) by picking combinations that
other humans are unlikely to play. If you do hit the jackpot, you won't
have to share it with 50 other people who played the same pattern.

Biases penalized:
1. Calendar Bias: Humans heavily pick 1-31 (birthdays, anniversaries).
2. Round Numbers: Multiples of 5 and 10 feel "lucky" to humans.
3. Master Numbers: 11, 22, 33, 44, 55 are overrepresented visually.
4. Lucky Numbers: 7, 11, 13, 17, 21, 23 are disproportionately popular.
5. Grid Diagonals: Humans love drawing lines or 'X' shapes on the betslip.
"""

from __future__ import annotations

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules import sum_range


@register
class CrowdAvoidanceStrategy(BaseStrategy):
    name = "crowd_avoidance"
    description = "👤 Psychological bias avoidance — penalize birthdays, round numbers, and betslip patterns"
    tier = "statistical"
    requires_history = 0

    def __init__(
        self, 
        birthday_penalty: float = 0.5, 
        round_penalty: float = 0.4,
        lucky_penalty: float = 0.3,
        diagonal_penalty: float = 0.4,
        w_sum_region: float = 0.3
    ) -> None:
        """
        Parameters
        ----------
        birthday_penalty
            Penalty applied to numbers <= 31 (birthdays/months).
        round_penalty
            Penalty applied to numbers ending in 0 or 5.
        lucky_penalty
            Penalty for 'culturally lucky' numbers (7, 11, 13, etc).
        diagonal_penalty
            Penalty for numbers sitting on board diagonals (visually popular).
        w_sum_region
            Weight for preferring the upper half of the 70% sum range (less popular).
        """
        self.birthday_penalty = float(birthday_penalty)
        self.round_penalty = float(round_penalty)
        self.lucky_penalty = float(lucky_penalty)
        self.diagonal_penalty = float(diagonal_penalty)
        self.w_sum_region = float(w_sum_region)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Geometric context (for diagonals)
        cols = 5 if "lotofacil" in rules.name.lower() else 10
        from engine.modules.geometry import BoardGeometry
        geo = BoardGeometry(max_n=hi, cols=cols)
        
        # 2. Sum context
        lo_70, hi_70, mean, _ = sum_range.most_probable_range(rules)
        mid_sum = mean
        
        lucky_set = {7, 11, 13, 17, 21, 23, 33, 77}
        
        scores = {}
        for n in all_numbers:
            score = 1.0
            
            # (A) Calendar Bias
            if n <= 31:
                score *= (1.0 - self.birthday_penalty)
                
            # (B) Round Numbers
            if n % 5 == 0:
                score *= (1.0 - self.round_penalty)
                
            # (C) Master/Repeating Numbers
            if n > 10 and n % 11 == 0:
                score *= 0.8
                
            # (D) Cultural Lucky Numbers
            if n in lucky_set:
                score *= (1.0 - self.lucky_penalty)
                
            # (E) Betslip Diagonals
            row, col = geo.get_coords(n)
            if row == col or row + col == cols + 1:
                score *= (1.0 - self.diagonal_penalty)
                
            # (F) Upper Half Preference (Implicit in per-number via magnitude)
            # We give a slight nudge to higher numbers since they push the sum up
            mag_boost = (n - lo) / (hi - lo) * self.w_sum_region
            score += mag_boost
            
            scores[n] = max(score, 0.01)
            
        # Normalise to [0, 1]
        max_s = max(scores.values())
        return {n: s / max_s for n, s in scores.items()}
