"""
Markov Chain Strategy 🔗
========================
Scores numbers based on first-order transition probabilities.

Theory:
-------
While lottery draws are independent, this strategy looks for 'Follower 
Numbers'—numbers that historically tend to appear in the draw IMMEDIATELY 
FOLLOWING another number. 
Example: If 17 is drawn, how often does 42 appear in the next draw?
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class MarkovStrategy(BaseStrategy):
    name = "markov"
    description = "🔗 Markov Chain — score numbers by historical transition probability from last draw"
    tier = "statistical"
    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_pool = len(all_numbers)
        
        # 1. Build Transition Matrix (Vectorized)
        # matrix[i, j] = count(draw_t has i AND draw_{t+1} has j)
        matrix = np.zeros((hi + 1, hi + 1), dtype=float)
        
        draws = [set(d) for d in df["numbers"].tolist()]
        for t in range(len(draws) - 1):
            current_draw = draws[t]
            next_draw = draws[t+1]
            for i in current_draw:
                for j in next_draw:
                    matrix[i, j] += 1
                    
        # 2. Get the Most Recent Draw
        last_draw = draws[-1]
        
        # 3. Score each number based on transitions from the last draw
        # Score(j) = sum(matrix[i, j] for i in last_draw)
        scores_raw = np.zeros(hi + 1)
        for i in last_draw:
            scores_raw += matrix[i]
            
        # 4. Normalise
        max_s = np.max(scores_raw[all_numbers]) if np.any(scores_raw[all_numbers]) else 1.0
        scores_norm = scores_raw[all_numbers] / max_s
        
        return dict(zip(all_numbers.tolist(), scores_norm.tolist()))
