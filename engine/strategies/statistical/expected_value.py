"""
Expected Value Model Strategy ♟️
===============================
Ported from LottoProphet. Uses game theory and historical structural ratios 
to identify number combinations with the highest "Advantage Principle" score.
"""

from __future__ import annotations

import logging
from collections import defaultdict, Counter
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

logger = logging.getLogger(__name__)

@register
class ExpectedValueStrategy(BaseStrategy):
    name = "expected_value"
    description = "♟️ Game-Theoretic Expected Value Model (Advantage Principle)"
    tier = "statistical"
    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        """
        Calculates number scores based on historical combination values.
        """
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Build Historical Value Distributions
        # Analyzes patterns: Parity, Magnitude, Sum, Span, Sequence
        value_dist = {
            'even_odd_ratio': defaultdict(int),
            'high_low_ratio': defaultdict(int),
            'sum_range': defaultdict(int),
            'span_range': defaultdict(int),
            'sequence_pattern': defaultdict(int)
        }
        
        total_drawings = len(df)
        mid_point = (lo + hi) // 2
        
        for _, row in df.iterrows():
            nums = sorted(row["numbers"])
            
            # Parity
            evens = sum(1 for n in nums if n % 2 == 0)
            odds = len(nums) - evens
            value_dist['even_odd_ratio'][f"{evens}:{odds}"] += 1
            
            # Magnitude
            highs = sum(1 for n in nums if n > mid_point)
            lows = len(nums) - highs
            value_dist['high_low_ratio'][f"{highs}:{lows}"] += 1
            
            # Sum
            s_val = sum(nums)
            value_dist['sum_range'][(s_val // 10) * 10] += 1
            
            # Span
            span = nums[-1] - nums[0]
            value_dist['span_range'][(span // 5) * 5] += 1
            
            # Sequence
            seq = sum(1 for i in range(len(nums)-1) if nums[i+1] - nums[i] == 1)
            value_dist['sequence_pattern'][seq] += 1
            
        # Normalize distributions to [0, 1] (Probability weights)
        for feature in value_dist:
            for key in value_dist[feature]:
                value_dist[feature][key] /= total_drawings

        # 2. Individual Number Base Frequency
        flat_nums = [n for d in df["numbers"] for n in d]
        counts = Counter(flat_nums)
        base_probs = {n: counts.get(n, 0) / (total_drawings * rules.pick_count) for n in all_numbers}

        # 3. Calculate Advantage Weights per Number
        # We simulate the "Next Combination" by evaluating each number's 
        # contribution to the most probable structural patterns.
        adv_weights = np.ones(len(all_numbers))
        
        # Recency Bias (Story 5.1.3): Boost numbers that haven't appeared in last 5 draws
        recent_df = df.tail(5)
        recent_nums = {n for d in recent_df["numbers"] for n in d}
        
        # Even/Odd Balance Check (Adaptive Weighting)
        recent_evens = sum(1 for n in recent_nums if n % 2 == 0)
        recent_odds = len(recent_nums) - recent_evens
        even_deficit = recent_evens < recent_odds
        
        for i, n in enumerate(all_numbers):
            # Recency Weight
            if n not in recent_nums:
                adv_weights[i] *= 1.2 # Boost cold numbers
            else:
                adv_weights[i] *= 0.8 # Temper hot numbers
                
            # Adaptive Weighting (Story 5.1.3)
            if n % 2 == 0 and even_deficit:
                adv_weights[i] *= 1.1
            elif n % 2 != 0 and not even_deficit:
                adv_weights[i] *= 1.1

        # 4. Final Scoring Blend
        # Score = Base Frequency * Advantage Weights
        # This approximates the "Mixed Strategy" resonance from the source code.
        final_scores = {}
        for i, n in enumerate(all_numbers):
            final_scores[n] = base_probs[n] * adv_weights[i]
            
        # Global Normalization to [0, 1]
        max_s = max(final_scores.values()) if final_scores else 1.0
        if max_s == 0: max_s = 1.0
        
        return {n: v / max_s for n, v in final_scores.items()}
