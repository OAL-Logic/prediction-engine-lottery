"""
Survival of the Fittest (Adaptive Meta-Strategy) 🧬
====================================================
A hyper-reactive ensemble that auto-tunes itself based on the 'hot streak'
of underlying strategies.

Algorithm:
----------
1. Evaluate every member strategy against the last N draws (default 10).
2. Rank strategies by their 'Hit Rate' (how many drawn numbers were in their top-10).
3. The 'Alpha' strategy (highest recent precision) gets a massive boost.
4. Strategies that have failed to predict anything recently are 'muted'.

This creates a self-healing prediction engine that adapts to the current 
statistical or mystical regime of the lottery.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from collections import Counter
from typing import Any, List

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, get_strategy, register

logger = logging.getLogger(__name__)

@register
class SurvivalStrategy(BaseStrategy):
    name = "survival"
    description = "🧬 Survival of the Fittest — auto-boost strategies on a winning streak"
    tier = "statistical"
    requires_history = 50

    def __init__(
        self, 
        members: str = "markov,bayesian,weighted,momentum,kabbalistic,solar",
        window: int = 10
    ) -> None:
        self._member_names = [m.strip() for m in members.split(",")]
        self.window = int(window)
        self._leaderboard: list[dict] = []
        self._meta: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        n_draws = len(df)
        bt_window = min(self.window, n_draws // 3)

        performance = {}
        strategy_scores = {}

        # 1. Back-test recent performance
        for name in self._member_names:
            try:
                strat = get_strategy(name)
                total_hits = 0
                for i in range(n_draws - bt_window, n_draws):
                    # Previous data
                    train_df = df.iloc[:i]
                    actual = set(df.iloc[i]["numbers"])
                    
                    # Score and check top 10
                    s = strat.score(train_df, rules)
                    top_10 = sorted(s, key=s.get, reverse=True)[:10]
                    total_hits += len(set(top_10) & actual)
                
                performance[name] = total_hits / (bt_window * rules.pick_count) if bt_window > 0 else 1.0
                # Get current scores
                strategy_scores[name] = strat.score(df, rules)
            except Exception as e:
                logger.debug(f"Survival: skipping {name} due to error: {e}")
                performance[name] = 0.0

        # 2. Rank and weight
        sorted_perf = sorted(performance.items(), key=lambda x: x[1], reverse=True)
        self._leaderboard = [{"name": name, "precision": round(p, 3)} for name, p in sorted_perf]
        self._meta = {"leaderboard": self._leaderboard}
        
        # 3. Recursive Ensemble Pruning (Statistician Expert)
        # Discard the bottom 25% of strategies entirely to reduce noise
        prune_count = max(1, len(sorted_perf) // 4)
        alpha_group = sorted_perf[:-prune_count] if len(sorted_perf) > 2 else sorted_perf
        
        # Alpha boost: top strategy gets 2x weight, others decay exponentially
        weights = {}
        for rank, (name, p) in enumerate(alpha_group):
            if p == 0:
                weights[name] = 0.01
            else:
                weights[name] = p * (2.0 if rank == 0 else (1.0 / (rank + 1)))

        total_weight = sum(weights.values()) or 1.0
        
        # 4. Blend and Simulate Convergence (v7.0)
        final_scores = {n: 0.0 for n in all_numbers}
        
        # We perform a 500-iteration internal simulation to find 'Convergence Zones'
        convergence_counts = Counter()
        
        # Calculate base blended scores first
        for name, weight in weights.items():
            s_dict = strategy_scores.get(name, {})
            w_norm = weight / total_weight
            for n in all_numbers:
                final_scores[n] += s_dict.get(n, 0.5) * w_norm
        
        # Normalise blended scores for sampling
        b_max = max(final_scores.values()) or 1.0
        b_min = min(final_scores.values())
        b_rng = b_max - b_min or 1.0
        b_normed = {n: (v - b_min) / b_rng for n, v in final_scores.items()}
        
        # Run 500 Monte Carlo simulations to find clusters
        from engine.strategies import _weighted_sample
        import numpy as np
        
        for _ in range(500):
            # Sample using a slightly higher temperature for exploration
            sim_ticket = _weighted_sample(all_numbers, b_normed, rules.pick_count, temperature=1.2)
            convergence_counts.update(sim_ticket)
            
        # Boost numbers with high convergence
        max_conv = max(convergence_counts.values()) or 1
        for n in all_numbers:
            conv_boost = convergence_counts.get(n, 0) / max_conv
            final_scores[n] = (final_scores[n] * 0.7) + (conv_boost * 0.3)
            
        return final_scores

    def suggest(self, df: pd.DataFrame, rules: DrawRules, count: int = 1, temperature: float = 1.0, history_limit: int | None = None, **kwargs: Any) -> SuggestionResult:
        result = super().suggest(df, rules, count, temperature, history_limit=history_limit, **kwargs)
        result.metadata.update(self._meta)
        return result
