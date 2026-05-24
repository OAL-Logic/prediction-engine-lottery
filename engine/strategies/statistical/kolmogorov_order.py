from __future__ import annotations

import pandas as pd
import zlib
import numpy as np
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class KolmogorovOrderStrategy(BaseStrategy):
    """
    Kolmogorov Complexity Strategy 🧩
    ================================
    Measures the algorithmic complexity (compressibility) of sequences.
    Random sequences are hard to compress. Ordered (structured) 
    sequences are easy.
    
    Theory: Draw physics sometimes enters 'Ordered Mode' (low complexity regimes).
    If complexity is dropping, it bets on numbers that maintain the pattern simplicity.
    """
    name = "kolmogorov_order"
    description = "🧩 Kolmogorov Complexity (Emergent Order)"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Calculate historical complexity (using Zlib as Kolmogorov proxy)
        def get_complexity(nums):
            # Convert list of numbers to a compact byte string
            data = bytes(sorted(nums))
            return len(zlib.compress(data))

        complexities = [get_complexity(row['numbers']) for _, row in df.tail(20).iterrows()]
        
        # 2. Detect Gradient (Is order increasing?)
        # A negative gradient means complexity is dropping (order is emerging)
        if len(complexities) > 1:
            gradient = np.gradient(complexities)[-1]
        else:
            gradient = 0
            
        # 3. Score numbers based on their contribution to 'Simplicity'
        # Numbers that appear in 'Low Complexity' draws are valued
        scores = {n: 0.1 for n in all_numbers}
        
        for _, row in df.tail(10).iterrows():
            c = get_complexity(row['numbers'])
            # The lower the complexity, the higher the boost to participating numbers
            weight = 1.0 / (c + 1)
            for n in row['numbers']:
                if n in scores:
                    # Emergent Order: Values numbers participating in structured draws
                    scores[n] += weight * (1.0 if gradient <= 0 else 0.5)

        # Normalize
        max_s = max(scores.values())
        min_s = min(scores.values())
        if max_s > min_s:
            scores = {k: (v - min_s) / (max_s - min_s) for k, v in scores.items()}
            
        return scores
