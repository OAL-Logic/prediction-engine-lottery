"""
Bayesian Frequency Strategy
============================
Uses a Dirichlet-Multinomial conjugate model to estimate the probability
that each number appears in the next draw.

Model
-----
  Prior:     Dirichlet(α₀) — uniform with concentration α₀
  Likelihood: observed draw counts c_i
  Posterior: Dirichlet(α₀ + c_i)
  Score:     posterior mean = (α₀ + c_i) / (N·α₀ + Σc_i)

With α₀ = 1 this reduces to Laplace-smoothed frequency.
With α₀ > 1 the prior pulls scores toward uniformity (more conservative).
With α₀ < 1 the prior amplifies observed differences (more aggressive).

Decay weighting
---------------
Optionally weight recent draws more heavily using an exponential decay
factor so that last week's draw counts more than draws from 5 years ago.
Set `decay=1.0` to treat all draws equally.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class BayesianStrategy(BaseStrategy):
    name = "bayesian"
    description = "📊 Dirichlet-Multinomial posterior — Bayesian frequency with recency decay"
    tier = "statistical"

    requires_history = 30

    def __init__(self, alpha0: float = 1.0, decay: float = 0.998) -> None:
        """
        Parameters
        ----------
        alpha0
            Prior strength (Starting confidence). 1.0 is neutral. Higher values (e.g. 5.0) 
            make the model more conservative, requiring more data to change its mind. 
            Lower values (e.g. 0.1) make it react aggressively to recent trends.
        decay
            Recency bias (Memory decay). 1.0 treats all history equally. 0.998 (default) 
            makes recent draws count more than old ones. A value of 0.95 would focus 
            almost entirely on the last few months of draws.
        """
        self.alpha0 = alpha0
        self.decay  = decay

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        df = df.sort_values("draw_id").reset_index(drop=True)
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        n_numbers = len(all_numbers)
        n_draws   = len(df)

        # Exponential decay weights: most recent draw has weight 1.0
        weights = np.array([self.decay ** (n_draws - 1 - i) for i in range(n_draws)])

        # Weighted counts
        counts = {n: 0.0 for n in all_numbers}
        for i, row in df.iterrows():
            w = weights[int(i)]  # type: ignore[arg-type]
            for num in row["numbers"]:
                counts[num] = counts.get(num, 0.0) + w

        # Posterior mean under Dirichlet-Multinomial
        total = sum(counts.values()) + n_numbers * self.alpha0
        scores = {n: (counts[n] + self.alpha0) / total for n in all_numbers}

        return scores
