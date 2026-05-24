"""
Reincarnation Strategy 🧘
=========================
Finds the 'Past Life' of the upcoming draw based on historical signatures.

Theory:
-------
Every draw date has a unique vibrational signature (hashed date + rules).
This strategy scans the entire history to find the draw that most closely 
matches today's signature, assuming that time is cyclical and events 
eventually 'reincarnate'.
"""

from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd
from datetime import date
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class ReincarnationStrategy(BaseStrategy):
    name = "reincarnation"
    description = "🧘 Reincarnation — identify the 'Past Life' draw via signature matching"
    tier = "fun"
    requires_history = 100

    def __init__(self, sensitivity: float = 1.0) -> None:
        """
        Parameters
        ----------
        sensitivity
            How selective the matching is. Higher = only very close matches.
        """
        self.sensitivity = float(sensitivity)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Generate Signature for the Target Date
        target_date = kwargs.get("draw_date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date[:10])
        
        # Handle NaT (Temporal Blindness fix)
        if pd.isna(target_date):
            return {n: 0.5 for n in all_numbers}
            
        target_sig = self._get_signature(target_date, rules)
        
        # 2. Scan History for the best match (Past Life)
        # We calculate the distance between signatures
        best_dist = float('inf')
        past_life_numbers = []
        
        for _, row in df.iterrows():
            d_str = str(row["date"])[:10]
            d_obj = date.fromisoformat(d_str)
            sig = self._get_signature(d_obj, rules)
            
            # Simple Euclidean distance between hashes (interpreting as vectors)
            dist = np.linalg.norm(target_sig - sig)
            if dist < best_dist:
                best_dist = dist
                past_life_numbers = row["numbers"]
                
        # 3. Score numbers based on proximity to the 'Past Life' winners
        scores = {}
        for n in all_numbers:
            if n in past_life_numbers:
                scores[n] = 1.0
            else:
                # Harmonic resonance (inverse distance to any past winner)
                dists = [abs(n - winner) for winner in past_life_numbers]
                min_d = min(dists)
                scores[n] = 1.0 / (min_d + 1)
                
        return scores

    def _get_signature(self, d: date, rules: DrawRules) -> np.ndarray:
        """
        Generate a deterministic numerical vector for a date/game combo.
        """
        seed_str = f"{d.isoformat()}{rules.name}{rules.pool_size if hasattr(rules, 'pool_size') else ''}"
        h = hashlib.sha256(seed_str.encode()).hexdigest()
        # Convert hex to 8 numerical chunks (0-255)
        chunks = [int(h[i:i+4], 16) % 256 for i in range(0, 32, 4)]
        return np.array(chunks, dtype=float)
