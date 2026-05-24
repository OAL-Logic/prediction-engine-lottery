"""
Fisher Information Strategy 🎣
=============================
Scores numbers based on their 'Information Sensitivity'.

Theory:
-------
Fisher Information measures the amount of information that an observable 
random variable carries about an unknown parameter. In lottery terms, 
it identifies numbers that are currently at a 'Critical Phase Transition' 
in their hit probability—numbers that are most sensitive to the underlying 
statistical regime change.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class FisherStrategy(BaseStrategy):
    name = "fisher"
    description = "🎣 Fisher Information — score numbers by their sensitivity to probability regime changes"
    tier = "statistical"
    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_draws = len(df)
        
        # 1. Calculate Time-Varying Probabilities (p_t)
        # Use a rolling window to get local probabilities
        window = 30
        matrix = np.zeros((n_draws, hi + 1))
        for i, row in enumerate(df["numbers"]):
            matrix[i, row] = 1.0
            
        # 2. Approximate Fisher Information (I)
        # For a Bernoulli process, I(p) = 1 / (p * (1-p))
        # We calculate the 'Stability of Information'
        
        # Rolling probabilities
        rolling_p = np.zeros_like(matrix)
        for t in range(window, n_draws):
            rolling_p[t] = matrix[t-window:t].mean(axis=0)
            
        # Avoid division by zero
        rolling_p = np.clip(rolling_p, 0.01, 0.99)
        
        # Calculate Fisher Information per number over the history
        # We look for where Information is PEAKING (Phase Transition)
        fisher_inf = 1.0 / (rolling_p * (1.0 - rolling_p))
        
        # Score based on current Information Momentum
        # Numbers where Info is high relative to its mean are 'Sensitive'
        current_i = fisher_inf[-1]
        mean_i = fisher_inf.mean(axis=0)
        
        # Score = Current / Mean (sensitivity ratio)
        scores_raw = current_i / (mean_i + 1e-9)
        
        # Normalise
        max_s = np.max(scores_raw[all_numbers]) if np.any(scores_raw[all_numbers]) else 1.0
        scores_norm = scores_raw[all_numbers] / max_s
        
        return dict(zip(all_numbers.tolist(), scores_norm.tolist()))
