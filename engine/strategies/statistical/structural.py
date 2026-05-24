"""
Structural Strategy — scores numbers based on their membership in harmonious sets.
=============================================================================
Allows targeting specific mathematical sets (Primes, Fibonacci, Frame).
"""

from __future__ import annotations

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules.patterns import PRIMES, FIBONACCI, get_frame_center_logic


@register
class StructuralStrategy(BaseStrategy):
    name = "structural"
    description = "🏗️ Structural Focus — target Primes, Fibonacci, and Frame/Center balance"
    tier = "statistical"
    requires_history = 0  # Can work without history, though scoring improves with it

    def __init__(
        self, 
        w_primes: float = 1.0, 
        w_fibonacci: float = 1.0, 
        w_frame: float = 0.5,
        w_center: float = 0.5
    ) -> None:
        self.w_primes = float(w_primes)
        self.w_fibonacci = float(w_fibonacci)
        self.w_frame = float(w_frame)
        self.w_center = float(w_center)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Grid layout for Frame/Center
        cols = 5 if "lotofacil" in rules.name.lower() else 10
        fc_logic = get_frame_center_logic(all_numbers, cols=cols, max_n=hi)
        frame_set = set(fc_logic["frame"])
        center_set = set(fc_logic["center"])
        
        scores = {}
        for n in all_numbers:
            s = 0.1  # baseline
            if n in PRIMES: s += self.w_primes
            if n in FIBONACCI: s += self.w_fibonacci
            if n in frame_set: s += self.w_frame
            if n in center_set: s += self.w_center
            scores[n] = s
            
        # Normalise to [0, 1]
        max_s = max(scores.values())
        return {n: scores[n] / max_s for n in scores}
