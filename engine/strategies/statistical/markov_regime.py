"""
Markov Regime Strategy 🔗📉
===========================
A Markov Chain strategy that dynamically adjusts to 'Regime Shifts' 
in transition probabilities. 

Compiles a 'Global' transition matrix and a 'Local' (recent) matrix.
If the local matrix significantly diverges from the global (regime shift),
it weights the local transitions more heavily to capture emerging patterns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

def get_transition_matrix(df: pd.DataFrame, lo: int, hi: int) -> np.ndarray:
    """Build first-order transition matrix."""
    matrix = np.zeros((hi + 1, hi + 1), dtype=float)
    draws = [set(d) for d in df["numbers"].tolist()]
    for t in range(len(draws) - 1):
        current_draw = draws[t]
        next_draw = draws[t+1]
        for i in current_draw:
            for j in next_draw:
                matrix[i, j] += 1
    return matrix

def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon Divergence as a proxy for regime drift."""
    # Normalize to distributions
    p_norm = p / (np.sum(p) + 1e-9)
    q_norm = q / (np.sum(q) + 1e-9)
    m = 0.5 * (p_norm + q_norm)
    
    def kl_div(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))

    return 0.5 * kl_div(p_norm, m) + 0.5 * kl_div(q_norm, m)

@register
class MarkovRegimeStrategy(BaseStrategy):
    name = "markov_regime"
    description = "🔗📉 Markov Transition Drift — detects shifts in number-to-number relationships"
    tier = "statistical"

    requires_history = 100

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        
        # 1. Global Matrix (Full history)
        global_matrix = get_transition_matrix(df, lo, hi)
        
        # 2. Local Matrix (Last 20 draws)
        local_df = df.tail(21) # 21 draws = 20 transitions
        local_matrix = get_transition_matrix(local_df, lo, hi)
        
        # 3. Detect Drift
        # We compare the row-wise JS divergence for each number in the last draw
        last_draw = list(df.iloc[-1]["numbers"])
        
        drifts = []
        for i in last_draw:
            d = js_divergence(global_matrix[i], local_matrix[i])
            drifts.append(d)
        
        avg_drift = np.mean(drifts) if drifts else 0.0
        
        # 4. Weighted Score
        # Drift-weighted blend: if drift is high, use local more.
        # Local weight = min(0.9, avg_drift * 5)
        local_weight = min(0.8, avg_drift * 4.0)
        global_weight = 1.0 - local_weight
        
        scores_raw = np.zeros(hi + 1)
        for i in last_draw:
            combined_row = (global_matrix[i] * global_weight) + (local_matrix[i] * local_weight)
            scores_raw += combined_row
            
        # 5. Normalize
        max_s = np.max(scores_raw[all_numbers]) if np.any(scores_raw[all_numbers]) else 1.0
        scores_norm = scores_raw[all_numbers] / max_s
        
        return dict(zip(all_numbers.tolist(), scores_norm.tolist()))
