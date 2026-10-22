"""
Weibull Hazard & Delay Survival Strategy ⌛
===========================================
Scores numbers based on empirical conditional hazard rates and parametric
Weibull survival models for draw-to-draw delays.

Theory:
-------
Under pure memoryless randomness, the wait time between occurrences follows
a Geometric distribution (constant hazard rate h(t) = p0). In real finite
sequences or physical mechanical draws, deviations in the hazard rate indicate:
  - gamma > 1: 'Aging' or wear-out effect — likelihood increases with delay.
  - gamma < 1: Clustering / burstiness effect.
  - gamma = 1: Memoryless renewal process.

This strategy computes both empirical conditional hazard:
  P(hit at t+1 | survival >= t)
and a robust method-of-moments Weibull hazard to identify numbers at high
probabilistic tension of return.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from scipy.special import gamma as gamma_fn
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class HazardWeibullStrategy(BaseStrategy):
    name = "hazard_weibull"
    description = "⌛ Hazard Rate & Weibull Delay — parametric & empirical survival hazard modeling for overdue numbers"
    tier = "statistical"
    requires_history = 50

    def __init__(self, alpha: float = 0.5, blend_weight: float = 0.5) -> None:
        """
        Args:
            alpha: Laplace smoothing pseudocount for empirical hazard estimation.
            blend_weight: Weight given to empirical hazard vs. parametric Weibull hazard (0.0 to 1.0).
        """
        self.alpha = float(alpha)
        self.blend_weight = float(np.clip(blend_weight, 0.0, 1.0))

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_pool = len(all_numbers)
        balls_drawn = getattr(rules, "pick_count", 6)
        p0 = float(balls_drawn) / float(n_pool)

        draws = [set(d) for d in df["numbers"].tolist()]
        total_draws = len(draws)

        if total_draws < self.requires_history:
            return {int(n): 1.0 / n_pool for n in all_numbers}

        raw_scores: dict[int, float] = {}

        for num in all_numbers:
            hit_indices = [idx for idx, d in enumerate(draws) if num in d]

            if len(hit_indices) < 2:
                # Insufficient hits to estimate delay distribution
                raw_scores[int(num)] = p0
                continue

            delays = np.diff(hit_indices).astype(float)
            curr_delay = float(total_draws - 1 - hit_indices[-1])
            t_target = curr_delay + 1.0

            # 1. Non-parametric Empirical Conditional Hazard
            # P(T = curr_delay + 1 | T >= curr_delay + 1)
            c_eq = float(np.sum(delays == t_target))
            c_ge = float(np.sum(delays >= t_target))
            h_emp = (c_eq + self.alpha * p0) / (c_ge + self.alpha)

            # 2. Parametric Weibull Hazard via Moment Estimation
            m = float(np.mean(delays))
            v = float(np.var(delays, ddof=1)) if len(delays) > 1 else m * m
            std_d = float(np.sqrt(max(v, 1e-4)))
            cv = std_d / max(m, 1e-4)

            # Approximate shape parameter gamma from coefficient of variation (Menon / Moment relation)
            # cv approx gamma(1+2/g)/gamma(1+1/g)^2 - 1 -> g approx cv^(-1.086)
            gamma_param = float(np.clip(cv ** (-1.086), 0.5, 3.5))
            lambda_param = float(m / max(gamma_fn(1.0 + 1.0 / gamma_param), 1e-4))

            # Weibull Hazard: h(t) = (gamma / lambda) * (t / lambda)^(gamma - 1)
            h_weibull = (gamma_param / lambda_param) * ((t_target / lambda_param) ** (gamma_param - 1.0))
            h_weibull = float(np.clip(h_weibull, 0.0, 1.0))

            # Blend empirical and parametric models
            combined = (self.blend_weight * h_emp) + ((1.0 - self.blend_weight) * h_weibull)
            raw_scores[int(num)] = combined

        # 3. Normalise across the candidate pool to [0, 1]
        vals = np.array([raw_scores[int(n)] for n in all_numbers], dtype=float)
        min_v = float(np.min(vals))
        max_v = float(np.max(vals))

        if max_v > min_v:
            norm_vals = (vals - min_v) / (max_v - min_v)
        else:
            norm_vals = np.ones(n_pool, dtype=float)

        return dict(zip([int(n) for n in all_numbers], norm_vals.tolist()))
