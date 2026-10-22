"""
Markov Chain Strategy 🔗
========================
Scores numbers based on first-order transition probabilities with Dirichlet prior smoothing
and exponential temporal decay.

Theory:
-------
While lottery draws are independent, this strategy looks for 'Follower 
Numbers'—numbers that historically tend to appear in the draw IMMEDIATELY 
FOLLOWING another number. Regularized with a Dirichlet prior distribution
to prevent zero-probability traps and smoothed over time regimes.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class MarkovStrategy(BaseStrategy):
    name = "markov"
    description = "🔗 Markov Chain — score numbers by historical transition probability from last draw with Dirichlet smoothing"
    tier = "statistical"
    requires_history = 50

    def __init__(self, alpha: float = 1.0, half_life: float | None = 150.0) -> None:
        """
        Args:
            alpha: Dirichlet pseudocount scaling for prior smoothing.
            half_life: Exponential decay half-life in draws (None or <= 0 for uniform history).
        """
        self.alpha = float(alpha)
        self.half_life = float(half_life) if half_life and half_life > 0 else None

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_pool = len(all_numbers)
        
        # 1. Build Transition Matrix with optional temporal decay
        matrix = np.zeros((hi + 1, hi + 1), dtype=float)
        draws = [set(d) for d in df["numbers"].tolist()]
        n_transitions = len(draws) - 1

        if n_transitions <= 0:
            return {int(n): 1.0 / n_pool for n in all_numbers}

        if self.half_life:
            decay_weights = np.exp(-np.log(2.0) / self.half_life * (n_transitions - 1 - np.arange(n_transitions)))
        else:
            decay_weights = np.ones(n_transitions, dtype=float)

        for t in range(n_transitions):
            w = decay_weights[t]
            for i in draws[t]:
                for j in draws[t + 1]:
                    matrix[i, j] += w
                    
        # 2. Get the Most Recent Draw
        last_draw = draws[-1]
        if not last_draw:
            return {int(n): 1.0 / n_pool for n in all_numbers}
        
        # 3. Calculate Dirichlet-Smoothed Conditional Transition Probabilities P(j | i)
        # alpha_eff = alpha / n_pool (symmetric Dirichlet prior)
        alpha_eff = max(self.alpha / n_pool, 1e-6)
        scores_raw = np.zeros(hi + 1, dtype=float)

        for i in last_draw:
            row_sum = np.sum(matrix[i, all_numbers])
            # Posterior mean under Dirichlet conjugate prior
            p_cond = (matrix[i, all_numbers] + alpha_eff) / (row_sum + n_pool * alpha_eff)
            scores_raw[all_numbers] += p_cond

        scores_raw[all_numbers] /= len(last_draw)
            
        # 4. Normalise to [0, 1] range
        min_s = float(np.min(scores_raw[all_numbers]))
        max_s = float(np.max(scores_raw[all_numbers]))
        if max_s > min_s:
            scores_norm = (scores_raw[all_numbers] - min_s) / (max_s - min_s)
        else:
            scores_norm = np.ones(n_pool, dtype=float)
        
        return dict(zip(all_numbers.tolist(), scores_norm.tolist()))
