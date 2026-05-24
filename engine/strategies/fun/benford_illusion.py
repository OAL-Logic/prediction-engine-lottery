from __future__ import annotations

import math
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class BenfordIllusionStrategy(BaseStrategy):
    """
    Benford's Illusion Strategy 🔢
    ==============================
    Applies Benford's Law (logarithmic distribution of leading digits)
    to lottery numbers, even though mathematically it shouldn't apply to a uniform distribution.
    A fringe "weird statistics" theory.
    """
    name = "benford_illusion"
    description = "🔢 Applied Benford's Law (Statistical Paradox)"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        scores = {}
        
        # Calculate theoretical Benford probabilities for leading digits 1-9
        benford_probs = {d: math.log10(1 + 1/d) for d in range(1, 10)}
        
        # Max score scaling
        max_prob = max(benford_probs.values())
        
        for num in range(lo, hi + 1):
            # Get leading digit
            leading_digit = int(str(num)[0])
            
            if leading_digit == 0:
                # Handle cases like "05" if zero-padded, though as int it's 5.
                leading_digit = num if num < 10 else int(str(num)[0])
                
            # Assign score based on Benford's expected probability curve
            # We invert it slightly to favor the "anomalies" or follow the law directly.
            # Let's follow the law: numbers starting with 1 get highest score.
            score = benford_probs.get(leading_digit, 0.1) / max_prob
            
            # Add a micro-jitter based on the number itself to prevent exact ties
            jitter = (num % 10) * 0.01
            
            scores[num] = min(1.0, score + jitter)
            
        return scores
