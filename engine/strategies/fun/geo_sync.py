from __future__ import annotations

import pandas as pd
import math
import random
from typing import Dict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class GeoSyncStrategy(BaseStrategy):
    """
    Geographic Synchronizer Strategy 🌍
    ==================================
    Correlates the user's geographic coordinates (Piracicaba/SP)
    with the geometric grid of the lottery ticket.
    
    Theory: The telluric resonance of the betting location (Astro-Cartography)
    pulls certain numbers through local 'Ley Lines'.
    """
    name = "geo_sync"
    description = "🌍 Geographic Synchronizer (Local Telluric Resonance)"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        scores = {n: 0.5 for n in range(lo, hi + 1)}
        
        # Coordinates of Piracicaba/SP
        lat = -22.7253
        lon = -47.6492
        
        # Seed based on local geometry
        geo_seed = abs(lat * lon)
        
        # Geometric matrix of the ticket (e.g., 10x6 for Mega-Sena)
        cols = 10 if hi == 60 else (5 if hi == 25 else 10)
        
        for num in range(lo, hi + 1):
            # Map the number to X, Y coordinate on the ticket
            row = (num - 1) // cols
            col = (num - 1) % cols
            
            # Calculate the 'energy distance' between the city coordinate
            # and the position of the number in the mathematical grid (Normalized)
            
            # A 'playful' mathematics based on spherical harmonics
            phase = math.sin(lat * row) + math.cos(lon * col)
            resonance = (phase + 2) / 4.0 # Normalizes between 0 and 1
            
            # Cross with history: Has this number resonated and appeared before?
            freq = 0
            if len(df) > 0:
                # Checks the last 50 draws
                recent = df.head(50)
                for _, d_row in recent.iterrows():
                    if num in d_row['numbers']:
                        freq += 1
                        
            # Modulates resonance by history (telluric 'hot' spots)
            final_score = resonance * (1.0 + (freq * 0.05))
            
            # Adds telluric noise
            jitter = random.uniform(-0.02, 0.02)
            
            scores[num] = min(1.0, max(0.0, final_score + jitter))

        # Normalize
        max_s = max(scores.values())
        min_s = min(scores.values())
        if max_s > min_s:
            scores = {k: (v - min_s) / (max_s - min_s) for k, v in scores.items()}
            
        return scores
