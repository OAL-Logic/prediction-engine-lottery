"""
Topological Data Analysis (TDA) Strategy 🍩
===========================================
Maps historical draws into a high-dimensional manifold and searches for
topological 'holes' (analogous to Betti numbers). Numbers that sit on the
boundary of these holes are considered 'structurally due' to close the manifold.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class TDATopologyStrategy(BaseStrategy):
    name = "tda_topology"
    description = "🍩 Topological Data Analysis (Structural Holes)"
    tier = "fun"

    requires_history = 20

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Create a distance matrix (co-occurrence inverse)
        co_occur = {n: {m: 0.0 for m in all_numbers} for n in all_numbers}
        counts = {n: 0.0 for n in all_numbers}
        
        for row in df.itertuples():
            nums = row.numbers
            for n in nums:
                counts[n] += 1
                for m in nums:
                    co_occur[n][m] += 1
                    
        scores = {n: 0.0 for n in all_numbers}
        
        # Find the hottest numbers to form the 'core complex'
        hot_threshold = np.percentile(list(counts.values()), 80)
        core_complex = [n for n, c in counts.items() if c >= hot_threshold]
        
        if not core_complex:
            return {n: 0.5 for n in all_numbers}
            
        for n in all_numbers:
            if n in core_complex:
                scores[n] = 0.1 # Core is already filled
                continue
                
            # Distance to core complex (inverse of co-occurrence)
            connectivity = sum(co_occur[n][c] for c in core_complex)
            expected_connectivity = counts[n] * len(core_complex) * (rules.pick_count / (hi - lo))
            
            # The 'hole' score is the deficit in expected connectivity
            deficit = expected_connectivity - connectivity
            
            # We want to fill the biggest deficits
            scores[n] = max(0.0, float(deficit))
            
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        
        return {n: v / max_s for n, v in scores.items()}
