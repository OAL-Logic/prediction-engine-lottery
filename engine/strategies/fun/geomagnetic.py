"""
Geomagnetic Space Weather Strategy ☀️
=====================================
Uses the cached planetary K-index (kp) to modulate the probability field.
High K-index (Solar Storms > 4) introduces massive entropy (jitter).
Low K-index (Quiet Sun < 2) favors strict historical frequencies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import json
import os

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class GeomagneticStrategy(BaseStrategy):
    name = "geomagnetic"
    description = "☀️ Space Weather (Solar K-Index Volatility Modulation)"
    tier = "fun"

    requires_history = 10

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Base frequency
        counts = {n: 0.0 for n in all_numbers}
        for row in df.itertuples():
            for num in row.numbers:
                counts[num] += 1.0
                
        # Normalize
        max_c = max(counts.values()) if counts else 1.0
        if max_c == 0: max_c = 1.0
        base_scores = {n: counts[n] / max_c for n in all_numbers}
        
        # 2. Read Solar K-Index
        kp = 1.0 # Default quiet
        try:
            # Assuming we are running from project root
            file_path = os.path.join("data", "solar_k_index.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    # Extract the latest kp value
                    if "data" in data and len(data["data"]) > 0:
                        kp = float(data["data"][-1].get("kp", 1.0))
        except Exception:
            pass # Fallback to 1.0
            
        # 3. Apply Space Weather Modulation
        scores = {}
        # If kp is high (>4), we add massive jitter (entropy).
        # If kp is low, we stick close to the base scores.
        
        jitter_magnitude = min(1.0, kp / 9.0) # Kp goes up to 9
        
        # We'll use a fixed random seed based on the date so it's stable per day, 
        # but chaotic based on kp.
        import random
        rng = random.Random(int(kp * 100))
        
        for n in all_numbers:
            jitter = rng.uniform(-jitter_magnitude, jitter_magnitude)
            
            # The higher the Kp, the less the base_score matters
            scores[n] = base_scores[n] * (1.0 - jitter_magnitude) + jitter + 1.0 # +1.0 to keep positive
            
        # Normalize
        min_s = min(scores.values()) if scores else 0.0
        for n in all_numbers:
            scores[n] -= min_s
            
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        
        return {n: v / max_s for n, v in scores.items()}
