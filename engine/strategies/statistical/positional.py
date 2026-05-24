"""
Positional Oscillator Strategy 📐
================================
Scores numbers based on their fit within specific draw positions (PDF).

Theory:
-------
Every lottery number has a unique 'Positional Probability Density Function'. 
In a sorted draw of 6 numbers (Mega-Sena), the number '1' has a high probability 
of being in position 1, and near-zero probability of being in position 6. 
This strategy models these distributions and scores candidate combinations 
by how well they 'fit' the historical positional slots.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Any, Dict
from collections import defaultdict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class PositionalStrategy(BaseStrategy):
    name = "positional"
    description = "📐 Positional Oscillator — Probability density of sorted draw slots"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        pick = rules.pick_count
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Build Historical PDF for each slot
        # pdf[slot][number] = frequency
        pdf = [defaultdict(int) for _ in range(pick)]
        
        for nums in df["numbers"]:
            sorted_draw = sorted(nums)
            for i, val in enumerate(sorted_draw[:pick]): # Guard against variable pick draws
                pdf[i][val] += 1
                
        # 2. Normalize PDFs
        n_draws = len(df)
        norm_pdf = []
        for slot_counts in pdf:
            max_c = max(slot_counts.values()) if slot_counts else 1
            norm_pdf.append({n: slot_counts.get(n, 0) / max_c for n in all_numbers})

        # 3. Scoring
        # For a single number 'n', its score is its MAX probability across ANY slot.
        # This identifies numbers that 'belong' somewhere in a draw.
        scores = {}
        for n in all_numbers:
            slot_probs = [slot.get(n, 0.0) for slot in norm_pdf]
            # Boost numbers that are very 'locked' to a specific position
            scores[n] = max(slot_probs)

        # 4. Metadata for CLI
        self._meta = {
            "top_slots": [
                {"slot": i+1, "top_n": sorted(norm_pdf[i], key=norm_pdf[i].get, reverse=True)[:3]}
                for i in range(pick)
            ]
        }

        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        return {n: s / max_s for n, s in scores.items()}

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
