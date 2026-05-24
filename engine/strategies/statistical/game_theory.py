"""
Game Theory / Crowd Antagonism Strategy ♟️
==========================================
Maximizes Expected Value (EV) by explicitly avoiding the numbers that 
human players are statistically most likely to pick. This doesn't increase 
the probability of winning, but dramatically increases the expected payout 
by reducing the chance of a shared jackpot.

Avoids:
- The "Birthday Bias" (1-31)
- The "Lucky 7" bias (7, 14, 21, 77)
- Geometric centers of the ticket
"""

from __future__ import annotations

import math
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class GameTheoryStrategy(BaseStrategy):
    name = "game_theory"
    description = "♟️ Game Theory (EV Maximization via Crowd Antagonism)"
    tier = "statistical"

    requires_history = 0

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        scores = {n: 1.0 for n in all_numbers} # Start with max score
        
        width = rules.board_cols or 10
        height = math.ceil((hi - lo + 1) / width)
        
        center_x = (width - 1) / 2.0
        center_y = (height - 1) / 2.0
        
        for n in all_numbers:
            penalty = 0.0
            
            # 1. Birthday Bias
            if 1 <= n <= 31:
                penalty += 0.4
                # Months (1-12) are even more common
                if n <= 12:
                    penalty += 0.2
                    
            # 2. Lucky 7s
            if n % 7 == 0 or '7' in str(n):
                penalty += 0.3
                
            # 3. Multiples of 10 (people like round numbers)
            if n % 10 == 0:
                penalty += 0.2
                
            # 4. Geometric Center Bias
            # People tend to pick numbers in the middle of the ticket
            row = (n - 1) // width
            col = (n - 1) % width
            
            dist_to_center = math.sqrt((col - center_x)**2 + (row - center_y)**2)
            max_dist = math.sqrt(center_x**2 + center_y**2)
            
            # Closer to center = higher penalty
            center_penalty = (1.0 - (dist_to_center / max_dist)) * 0.3
            penalty += center_penalty
            
            # 5. Edges (People AVOID edges, so we boost them by reducing penalty)
            if row == 0 or row == height - 1 or col == 0 or col == width - 1:
                penalty -= 0.2
                
            # Calculate final score
            # A completely "ugly" number like 48 (not a birthday, not lucky, on an edge)
            # will have a penalty near 0, keeping its score near 1.0.
            scores[n] = max(0.01, 1.0 - penalty)
            
        # Add micro jitter
        for n in scores:
            scores[n] += (n % 13) * 0.005
            
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        
        return {n: min(1.0, v / max_s) for n, v in scores.items()}
