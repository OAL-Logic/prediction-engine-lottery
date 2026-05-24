"""
Advanced Structural Metrics Strategy 🛡️
======================================
Scores numbers based on their contribution to 'Harmonious' structural patterns.

Theory:
-------
Winning lottery tickets typically exhibit a 'Normal' distribution of structural
properties like Arithmetic Complexity (AC), Root Sums, and Unit Sums. This 
strategy identifies the historical 'Sweet Spot' for each metric and scores
numbers by how often they participate in combinations that land in these spots.

Metrics tracked:
1. AC Value (Arithmetic Complexity)
2. Root Sum (Recursive digital root)
3. Unit Sum (Sum of last digits)
4. Successive Groups (Count of adjacent pairs/triplets)
5. Spread (Distance between min and max)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Any

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules import filters as f_mod


@register
class AdvancedStrategy(BaseStrategy):
    name = "advanced"
    description = "🧪 Advanced Metrics — scores numbers by structural harmony (AC, Root Sum, Unit Sum, etc.)"
    tier = "statistical"

    requires_history = 100

    def __init__(self, n_samples: int = 1000) -> None:
        """
        Parameters
        ----------
        n_samples
            Number of random combinations to generate for participation scoring.
        """
        self.n_samples = int(n_samples)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> Dict[int, float]:
        lo, hi = rules.number_range
        pick = rules.pick_count
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Analyze historical distributions
        draws = df["numbers"].tolist()
        
        ac_hist = [f_mod.get_ac_value(d) for d in draws]
        root_hist = [f_mod.get_root_sum(d) for d in draws]
        unit_hist = [f_mod.get_unit_metrics(d)["sum"] for d in draws]
        spread_hist = [f_mod.get_distance_metrics(d)["spread"] for d in draws]
        succ_hist = [f_mod.get_successive_metrics(d)["groups"] for d in draws]
        
        # Calculate stats for "Normal" zone
        def get_z_dist(val, hist):
            m, s = np.mean(hist), np.std(hist)
            if s == 0: return 0.0
            return abs((val - m) / s)

        # 2. Score combinations by "Harmonic Distance"
        # Generate random combinations
        u = np.random.uniform(size=(self.n_samples, len(all_numbers)))
        combo_indices = np.argsort(u, axis=1)[:, -pick:]
        nums_arr = np.array(all_numbers)
        combos = nums_arr[combo_indices]
        
        # We'll score each combo by its total Z-distance (lower is more harmonious)
        combo_harmony = np.zeros(self.n_samples)
        
        for i in range(self.n_samples):
            c = list(combos[i])
            
            z_total = 0.0
            z_total += get_z_dist(f_mod.get_ac_value(c), ac_hist)
            z_total += get_z_dist(f_mod.get_root_sum(c), root_hist)
            z_total += get_z_dist(f_mod.get_unit_metrics(c)["sum"], unit_hist)
            z_total += get_z_dist(f_mod.get_distance_metrics(c)["spread"], spread_hist)
            z_total += get_z_dist(f_mod.get_successive_metrics(c)["groups"], succ_hist)
            
            # Map Z-total to a score [0, 1] where lower Z is higher score
            # Using exponential decay for sharp "Sweet Spot" targeting
            combo_harmony[i] = np.exp(-z_total / 2.0)
                
        # 3. Aggregate Number Scores via weighted participation
        scores = {n: 0.0 for n in all_numbers}
        for i in range(self.n_samples):
            h_score = combo_harmony[i]
            for n in combos[i]:
                scores[n] += h_score
                
        # Normalise
        max_s = max(scores.values()) if any(scores.values()) else 1.0
        return {n: s / max_s for n, s in scores.items()}
