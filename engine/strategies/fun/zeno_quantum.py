"""
Quantum Zeno Effect Strategy 👁️
================================
In quantum mechanics, observing a system frequently can "freeze" its evolution (the Zeno effect).
In this strategy, numbers that are "observed" (drawn) too frequently in the recent window
experience a sudden probability collapse, as they are "frozen" and cannot evolve into the next draw.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class ZenoQuantumStrategy(BaseStrategy):
    name = "zeno_quantum"
    description = "👁️ Quantum Zeno Effect (Observation Freeze)"
    tier = "fun"

    requires_history = 10

    def __init__(self, observation_window: int = 15, zeno_threshold: float = 0.8) -> None:
        """
        Parameters
        ----------
        observation_window : The number of recent draws to consider for observation density.
        zeno_threshold : The normalized frequency above which a number "freezes".
        """
        self.observation_window = observation_window
        self.zeno_threshold = zeno_threshold

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # We only look at the observation window
        window_df = df.tail(self.observation_window)
        
        counts = {n: 0.0 for n in all_numbers}
        for row in window_df.itertuples():
            for num in row.numbers:
                counts[num] += 1.0
                
        # Normalize to find observation density
        max_c = max(counts.values()) if counts else 1.0
        if max_c == 0: max_c = 1.0
        
        scores = {}
        for n in all_numbers:
            density = counts[n] / max_c
            
            # The Quantum Zeno logic:
            # If density is very high, it freezes (score collapses to near 0).
            # If density is medium, it has standard probability.
            # If density is low, it evolves freely (high score).
            
            if density >= self.zeno_threshold:
                # Zeno freeze!
                scores[n] = 0.05 # small quantum tunneling probability
            else:
                # Free evolution (anti-Zeno)
                # The less it is observed, the more it evolves
                scores[n] = 1.0 - density
                
        # Add tiny jitter to prevent exact ties
        for n in scores:
            scores[n] += (n % 10) * 0.001
            
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        return {n: min(1.0, v / max_s) for n, v in scores.items()}
