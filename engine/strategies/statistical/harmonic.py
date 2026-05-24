"""
Harmonic Resonance Strategy 💎
==============================
Scores numbers by combining spatial geometry with statistical co-occurrence.

Theory:
-------
This strategy assumes that the 'Resonance' of a number is highest when its 
physical neighbors on the board (Geometry) AND its statistical 'Buddies' 
(Lift) have hit recently.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules import correlation


@register
class HarmonicResonanceStrategy(BaseStrategy):
    name = "harmonic"
    description = "💎 Harmonic Resonance — blend of spatial adjacency and statistical co-occurrence"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        
        # 1. Statistical Resonance (Lift matrix)
        corr = correlation.analyze(df.tail(200), rules)
        lift_matrix = corr.lift
        
        # 2. Geometric Adjacency (Neighbors)
        cols = 5 if "lotofacil" in rules.name.lower() else 10
        from engine.modules.geometry import BoardGeometry
        geo = BoardGeometry(max_n=hi, cols=cols)
        
        # 3. Analyze Most Recent Draw
        last_draw = set(df.iloc[-1]["numbers"])
        
        scores = {}
        for n in all_numbers:
            # (A) Statistical Harmonic: Max lift with ANY winner from last draw
            lifts = [lift_matrix.loc[n, winner] for winner in last_draw]
            s_res = max(lifts) if lifts else 1.0
            
            # (B) Geometric Harmonic: Is touching any winner?
            neighbors = set(geo.get_neighbors(n))
            g_res = 1.5 if (neighbors & last_draw) else 1.0
            
            # Final blend
            # We use 0.5 as neutral
            scores[n] = (s_res / (corr.lift.max().max() or 1.0)) * 0.7 + (g_res / 1.5) * 0.3
            
        # Normalise
        max_s = max(scores.values()) if scores else 1.0
        return {n: s / max_s for n, s in scores.items()}
