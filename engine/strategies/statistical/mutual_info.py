"""
Mutual Information Strategy 🧠
==============================
Scores numbers based on their statistical dependency with the most recent draw.

Theory:
-------
Uses Information Theory (Mutual Information) to identify which numbers 
historically convey the most information about each other. If number 17 
has high MI with 42, and 17 was drawn last, 42 gets a boost.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
try:
    from sklearn.metrics import mutual_info_score
    _SKLEARN = True
except ImportError:
    _SKLEARN = False

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class MutualInfoStrategy(BaseStrategy):
    name = "mutual_info"
    description = "🧠 Mutual Information — score numbers by statistical dependency with recent winners"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        if not _SKLEARN:
            return {n: 0.5 for n in range(rules.number_range[0], rules.number_range[1] + 1)}

        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_draws = len(df)
        
        # 1. Build Binary Presence Matrix (D x N)
        matrix = np.zeros((n_draws, hi + 1))
        for i, row in enumerate(df["numbers"]):
            matrix[i, row] = 1.0
            
        # 2. Compute Mutual Information Matrix
        # MI(X, Y) measures how much knowing X reduces uncertainty about Y.
        mi_matrix = np.zeros((hi + 1, hi + 1))
        
        # To make it fast, we only compute MI for numbers that actually appeared
        active_nums = [n for n in all_numbers if matrix[:, n].any()]
        
        for i in active_nums:
            for j in active_nums:
                if i >= j: continue
                # mutual_info_score expects categorical labels
                score = mutual_info_score(matrix[:, i], matrix[:, j])
                mi_matrix[i, j] = score
                mi_matrix[j, i] = score
                
        # 3. Get the Most Recent Draw
        last_draw = list(df.iloc[-1]["numbers"]) if not df.empty else []
        
        # 4. Score each number based on its MI with the last draw
        scores_raw = np.zeros(hi + 1)
        for n in all_numbers:
            if n in last_draw:
                scores_raw[n] = 0.5
                continue
            
            # Find max dependency with ANY number in last draw
            dependencies = [mi_matrix[n, companion] for companion in last_draw]
            scores_raw[n] = max(dependencies) if dependencies else 0.0
            
        # Normalise
        max_s = np.max(scores_raw[all_numbers]) if np.any(scores_raw[all_numbers]) else 1.0
        scores_norm = scores_raw[all_numbers] / max_s
        
        return dict(zip(all_numbers.tolist(), scores_norm.tolist()))
