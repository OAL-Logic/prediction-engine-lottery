"""
Co-Occurrence Pairs Strategy 🤝
==============================
Scores numbers based on their historical 'Lift' with the most recent draw.

Theory:
-------
If number 17 and 42 have a high historical Lift (>1.2), and 17 was drawn 
last night, 42 gets a boost today. This is the 'Handicapper's Buddy' 
technique — betting on pairs that travel together.
"""

from __future__ import annotations

import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules import correlation


@register
class CooccurrenceStrategy(BaseStrategy):
    name = "copairs"
    description = "👯 Co-occurrence Pairs — boost numbers that historically 'travel together' with recent winners"
    tier = "statistical"

    requires_history = 50

    def __init__(self, history_limit: int = 200) -> None:
        self.history_limit = int(history_limit)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        if df.empty:
            return {n: 0.5 for n in range(rules.number_range[0], rules.number_range[1] + 1)}
            
        # 1. Analyze historical correlations
        corr = correlation.analyze(df.tail(self.history_limit), rules)
        lift_matrix = corr.lift
        
        # 2. Get the most recent draw
        last_draw = set(df.iloc[-1]["numbers"])
        
        # 3. Score each number based on its max lift with ANY number in the last draw
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        scores = {}
        
        for n in all_numbers:
            if n in last_draw:
                # Numbers that just appeared get a slight penalty or stay neutral
                # (Gambler's fallacy vs Hot hand - we keep them neutral)
                scores[n] = 0.5
                continue
            
            # Find the strongest historical companion in the last draw
            lifts = [lift_matrix.loc[n, companion] for companion in last_draw]
            max_lift = max(lifts) if lifts else 1.0
            
            # Score: 0.5 is neutral (lift=1.0). Scale accordingly.
            scores[n] = max(min(0.5 * max_lift, 1.0), 0.0)
            
        return scores
