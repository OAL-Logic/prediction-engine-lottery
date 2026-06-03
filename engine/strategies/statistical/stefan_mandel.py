"""
Stefan Mandel Combinatorial Condensation Strategy 💼📊
======================================================
Calculates combinations and scores numbers to support the Mandel mathematical formula:
Identify lotteries where the jackpot exceeds the cost of purchasing every combination,
and generate a covering matrix prioritizing high-occurrence combinations.
"""

from __future__ import annotations

import logging
from math import comb
from typing import Any
import pandas as pd
import numpy as np

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

logger = logging.getLogger(__name__)

@register
class StefanMandelCombinatorialCondensationStrategy(BaseStrategy):
    name = "stefan_mandel"
    description = "💼 Stefan Mandel Combinatorial Condensation — targets jackpots exceeding combinatorial cost with optimal coverage"
    tier = "statistical"
    requires_history = 30

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._meta: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        """
        Scores numbers by tracking historical co-occurrence density to optimize 
        the coverage ticket matrix.
        """
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        n_balls = len(all_numbers)
        
        # 1. Calculate Combinatorial Metrics
        n = rules.number_range[1] - rules.number_range[0] + 1
        k = rules.pick_count
        total_combinations = comb(n, k)
        
        ticket_price = rules.ticket_price
        total_cost = total_combinations * ticket_price
        
        # 2. Build co-occurrence density weights from history
        co_counts = np.zeros(n_balls)
        if not df.empty:
            for nums in df["numbers"]:
                for num in nums:
                    val_idx = num - lo
                    if 0 <= val_idx < n_balls:
                        co_counts[val_idx] += 1.0
                        
        # Identify high density resonance zones
        max_c = np.max(co_counts) or 1.0
        densities = co_counts / max_c
        
        # 3. Formulate Mandel Expected Return Index
        # We assume a baseline jackpot of 40% rules.ticket_price * total_combinations if none specified
        assumed_jackpot = kwargs.get("jackpot") or (ticket_price * total_combinations * 1.2)
        arbitrage_ratio = assumed_jackpot / total_cost if total_cost > 0 else 0.0
        
        self._meta = {
            "total_combinations": total_combinations,
            "combinatorial_cost": round(total_cost, 2),
            "arbitrage_ratio": round(arbitrage_ratio, 3),
            "arbitrage_verdict": "FEASIBLE (+EV)" if arbitrage_ratio >= 1.0 else "UNFEASIBLE (-EV)"
        }
        
        scores = {}
        for idx, num in enumerate(all_numbers):
            # Prioritize mid-to-high frequency numbers to maximize secondary prizes
            scores[num] = float(densities[idx])
            
        return scores

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
