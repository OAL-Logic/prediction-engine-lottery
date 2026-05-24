"""
Universal Synapse Strategy 🧠
===========================
The engine's peak convergent strategy. 

It runs three independent 'cylinders' (Statistical, Deep, Chaos) and calculates 
their Universal Conjunction — numbers that appear in the top-10 of all three 
cylinders receive a 1.5x Conjunction Boost.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Any, Dict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, get_strategy, register

@register
class SynapseStrategy(BaseStrategy):
    name = "synapse"
    description = "🧠 Universal Synapse — Peak convergent meta-ensemble"
    tier = "ml"
    requires_history = 100

    def __init__(self, members: list[str] | None = None) -> None:
        # Default cylinders
        self.cylinders = {
            "statistical": ["weighted", "markov", "momentum"],
            "deep": ["transformer", "lstm_gru", "cnn_1d"],
            "chaos": ["kabbalistic", "reincarnation", "noosphere"]
        }

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Run the three cylinders
        cylinder_scores = {}
        for cyl_name, members in self.cylinders.items():
            cyl_total = {n: 0.0 for n in all_numbers}
            valid_count = 0
            for s_name in members:
                try:
                    strat = get_strategy(s_name)
                    s_scores = strat.score(df, rules)
                    for n, val in s_scores.items():
                        cyl_total[n] += val
                    valid_count += 1
                except Exception:
                    continue
            
            if valid_count > 0:
                max_v = max(cyl_total.values()) or 1.0
                cylinder_scores[cyl_name] = {n: v / max_v for n, v in cyl_total.items()}
            else:
                cylinder_scores[cyl_name] = {n: 0.5 for n in all_numbers}

        # 2. Identify top-10 per cylinder
        top_10s = {}
        for cyl_name, scores in cylinder_scores.items():
            sorted_nums = sorted(scores.keys(), key=lambda n: scores[n], reverse=True)
            top_10s[cyl_name] = set(sorted_nums[:10])

        # 3. Calculate Universal Conjunction
        final_scores = {n: 0.0 for n in all_numbers}
        for n in all_numbers:
            # Base score is average of cylinders
            base = sum(cyl[n] for cyl in cylinder_scores.values()) / 3.0
            
            # Conjunction check
            in_stat = n in top_10s["statistical"]
            in_deep = n in top_10s["deep"]
            in_chaos = n in top_10s["chaos"]
            
            boost = 1.0
            if in_stat and in_deep and in_chaos:
                boost = 1.5 # Triple conjunction
            elif (in_stat and in_deep) or (in_stat and in_chaos) or (in_deep and in_chaos):
                boost = 1.2 # Double conjunction
                
            final_scores[n] = base * boost

        # Normalise
        max_f = max(final_scores.values()) or 1.0
        return {n: v / max_f for n, v in final_scores.items()}
