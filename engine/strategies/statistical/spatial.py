"""
Spatial Grid Strategy 📐
=======================
Analyzes the physical layout of the lottery ticket (grid).
Captures 'contagion' and 'cluster' effects based on 2D adjacency.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class SpatialStrategy(BaseStrategy):
    name = "spatial"
    description = "📐 Grid-aware analysis — models physical adjacency and clusters on the ticket"
    tier = "statistical"

    requires_history = 10

    def __init__(self, decay: float = 0.9, neighbor_boost: float = 0.5) -> None:
        """
        Parameters
        ----------
        decay
            How fast the 'heat' from previous draws dissipates.
        neighbor_boost
            How much a number's score is influenced by its physical neighbors.
        """
        self.decay = decay
        self.neighbor_boost = neighbor_boost

    def _get_coords(self, n: int, rules: DrawRules) -> tuple[int, int]:
        """Convert number to (row, col) based on game pool size and board width."""
        width = rules.board_cols or 10
                
        row = (n - 1) // width
        col = (n - 1) % width
        return row, col

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Calculate raw frequency heat
        n_draws = len(df)
        heat = {n: 0.0 for n in all_numbers}
        
        for i, row in enumerate(df.itertuples()):
            # Recency weighting
            w = self.decay ** (n_draws - 1 - i)
            for num in row.numbers:
                if num in heat:
                    heat[num] += w

        # 2. Diffuse heat to neighbors
        final_scores = {n: 0.0 for n in all_numbers}
        
        for n in all_numbers:
            r1, c1 = self._get_coords(n, rules)
            
            # Base score from own heat
            score = heat[n]
            
            # Add boost from neighbors
            neighbor_contribution = 0.0
            for m in all_numbers:
                if n == m: continue
                r2, c2 = self._get_coords(m, rules)
                
                # Manhattan distance
                dist = abs(r1 - r2) + abs(c1 - c2)
                
                if dist == 1: # Immediate neighbor
                    neighbor_contribution += heat[m] * self.neighbor_boost
                elif dist == 2: # Diagonal or two steps
                    neighbor_contribution += heat[m] * (self.neighbor_boost * 0.3)
            
            final_scores[n] = score + neighbor_contribution

        # Normalize
        max_v = max(final_scores.values()) if final_scores else 1.0
        if max_v > 0:
            final_scores = {n: v / max_v for n, v in final_scores.items()}
            
        return final_scores
