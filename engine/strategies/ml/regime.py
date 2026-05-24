"""
Regime-Switching Strategy 📉
===========================
Dynamically switches between base strategies based on detected 'Market Regime'.

Regimes:
--------
1. Pattern Regime (p < 0.05): Use Markov/Spectral.
2. Stable Regime (p > 0.8): Use Weighted/Bayesian.
3. Sparse Regime (Mega-Sena/Powerball): Use Void/Copairs.
"""

from __future__ import annotations

import pandas as pd
from scipy import stats
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register, get_strategy


@register
class RegimeStrategy(BaseStrategy):
    name = "regime"
    description = "📉 Regime-Switching — dynamic model selection based on statistical stability"
    tier = "ml"
    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        from collections import Counter
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Detect Regime via Chi2 on last 30 draws
        recent = df.tail(30)
        flat = [n for d in recent["numbers"] for n in d]
        counts = Counter(flat)
        _, p_val = stats.chisquare(list(counts.values()))
        
        # 2. Select Strategy
        # Logic: 
        # - If very sparse (pool > 50 and pick < 10) -> favor spatial void
        # - If p < 0.05 -> patterns exist, use markov
        # - Else -> stable, use weighted
        
        is_sparse = (hi - lo + 1) > 50 and rules.pick_count < 10
        
        if is_sparse:
            s_name = "void"
        elif p_val < 0.05:
            s_name = "markov"
        else:
            s_name = "weighted"
            
        strat = get_strategy(s_name, **kwargs)
        return strat.score(df, rules, **kwargs)
