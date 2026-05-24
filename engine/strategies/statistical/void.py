"""
Void Analysis Strategy 🕳️
========================
Scores numbers based on their presence in 'Cold Sectors' or 'Voids.'

Theory:
-------
For sparse lotteries (like Mega-Sena), large areas of the board often remain
empty for several draws. This strategy identifies quadrants and rows that 
haven't seen a hit in a record number of draws, assuming a spatial mean-reversion.
"""

from __future__ import annotations

import pandas as pd
from collections import Counter

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class VoidStrategy(BaseStrategy):
    name = "void"
    description = "🕳️ Void Analysis — target board sectors (quadrants/rows) that are currently empty"
    tier = "statistical"
    requires_history = 10

    def __init__(self, w_quadrant: float = 1.0, w_row: float = 0.5) -> None:
        self.w_quadrant = float(w_quadrant)
        self.w_row = float(w_row)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Define board layout
        cols = 5 if "lotofacil" in rules.name.lower() else 10
        from engine.modules.geometry import BoardGeometry
        geo = BoardGeometry(max_n=hi, cols=cols)
        
        # 2. Analyze recent void history (last 5 draws)
        recent = df.tail(5)
        
        # Count hits per row and quadrant
        row_hits = Counter()
        quad_hits = Counter()
        
        for _, draw in recent.iterrows():
            for n in draw["numbers"]:
                r, c = geo.get_coords(n)
                row_hits[r] += 1
                
                # Quadrant (Simple 4-way split)
                q_r = 1 if r <= geo.rows / 2 else 2
                q_c = 1 if c <= geo.cols / 2 else 2
                quad_hits[(q_r, q_c)] += 1
                
        # 3. Score numbers based on inverse hit counts
        max_r_hits = max(row_hits.values()) if row_hits else 1
        max_q_hits = max(quad_hits.values()) if quad_hits else 1
        
        scores = {}
        for n in all_numbers:
            r, c = geo.get_coords(n)
            q_r = 1 if r <= geo.rows / 2 else 2
            q_c = 1 if c <= geo.cols / 2 else 2
            
            # Row score: 1.0 if empty, lower if busy
            r_score = (max_r_hits - row_hits[r]) / max_r_hits
            # Quad score: 1.0 if empty, lower if busy
            q_score = (max_q_hits - quad_hits[(q_r, q_c)]) / max_q_hits
            
            scores[n] = (r_score * self.w_row) + (q_score * self.w_quadrant)
            
        # Normalise
        max_s = max(scores.values()) if any(scores.values()) else 1.0
        return {n: s / max_s for n, s in scores.items()}
