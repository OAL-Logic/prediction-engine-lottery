"""
Combinatorial Covering Design Strategy (Steiner Wheel approximation)
====================================================================
Generates a set of tickets that guarantee a specific match condition.

If you pick a pool of `v` numbers, and you want to guarantee you hit at least
`t` numbers correctly IF the draw lands within your pool, this strategy computes 
the minimal (or near-minimal) set of tickets of size `k` to cover every possible
`t`-subset of the `v` pool.

This is pure combinatorics. It doesn't predict the draw; it mathematically 
optimizes your ticket spread to prevent overlap and maximize coverage.
"""

from __future__ import annotations

import itertools
import random
from collections import Counter

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register


@register
class SteinerWheelStrategy(BaseStrategy):
    name = "steiner_wheel"
    description = "🎡 Combinatorial Covering Design — guarantees a match if the draw falls in a hot pool"
    tier = "statistical"
    requires_history = 30

    def __init__(self, pool_size: int = 15, match_guarantee: int = 3, max_tickets: int = 100) -> None:
        """
        Parameters
        ----------
        pool_size
            Size of the candidate pool (v). We select the top `pool_size` hottest numbers 
            from historical frequency. E.g. pool of 15 hot numbers.
        match_guarantee
            The subset size to cover (t). E.g., a guarantee of 3 means that EVERY 3-number 
            combination from your pool is covered by at least one ticket.
        max_tickets
            Safety limit for ticket generation. If the combinatorial math requires too many 
            tickets to guarantee the cover, it stops here to prevent endless loops.
        """
        self.pool_size = int(pool_size)
        self.match_guarantee = int(match_guarantee)
        self.max_tickets = int(max_tickets)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        # Base scoring: Frequency (to pick the pool of `v`)
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        flat = [n for nums in df["numbers"] for n in nums]
        counts = Counter(flat)
        max_c = max(counts.values()) if counts else 1
        
        return {n: counts.get(n, 0) / max_c for n in all_numbers}

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        """
        Override suggest to generate a deterministic covering set instead of sampling.
        We ignore `count` if the wheel needs more tickets, because a wheel is useless 
        if broken apart.
        """
        from engine.wheels import generate_abbreviated_wheel
        
        # Extract necessary arguments from args/kwargs or defaults
        import inspect
        # Match BaseStrategy.suggest signature
        base_sig = inspect.signature(BaseStrategy.suggest)
        bound = base_sig.bind_partial(self, *args, **kwargs)
        bound.apply_defaults()
        
        df = bound.arguments['df']
        rules = bound.arguments['rules']
        count = bound.arguments['count']
        history_limit = bound.arguments['history_limit']
        pick = bound.arguments['pick']

        # Apply recency bias limit if requested
        if history_limit is not None and history_limit > 0:
            df = df.tail(history_limit)

        scores = self.score(df, rules)
        
        # 1. Pick the pool of `v` numbers
        sorted_nums = sorted(scores, key=scores.__getitem__, reverse=True)
        v = min(self.pool_size, len(sorted_nums))
        
        target_pick = pick if pick is not None else rules.pick_count
        t = self.match_guarantee

        # Prevent absurd combinatorial explosions / invalid params
        if t > target_pick:
            t = target_pick
        if t > 4 or v > 20:
            # Downgrade gracefully for safety (combinatorics explode quickly)
            t = min(t, 3)
            v = min(v, 18)
            
        pool = sorted_nums[:v]

        # 2. Use the central wheeling logic
        tickets = generate_abbreviated_wheel(pool, target_pick, t, max_tickets=self.max_tickets)

        # A wheel shouldn't return just 1 ticket if it generated 12, it breaks the wheel.
        # So we return the full wheel, or at least up to `count` if count is high.
        final_tickets = tickets[:max(count, len(tickets))]

        # Normalise scores for SuggestionResult interface
        min_s = min(scores.values())
        max_s = max(scores.values())
        rng = max_s - min_s or 1.0
        normed = {n: (scores.get(n, 0.0) - min_s) / rng for n in scores}
        confidence = float(np.mean(list(normed.values())))

        # Dynamic parameter capture for transparency
        params = {}
        try:
            sig = inspect.signature(self.__class__.__init__)
            for p_name in sig.parameters:
                if p_name == "self":
                    continue
                if hasattr(self, p_name):
                    val = getattr(self, p_name)
                    params[p_name] = val.isoformat() if hasattr(val, "isoformat") else val
        except Exception:
            pass

        return SuggestionResult(
            strategy_name=self.name,
            tickets=final_tickets,
            scores=normed,
            confidence=confidence,
            metadata={
                "pool_size": v,
                "match_guarantee": t,
                "wheel_size": len(final_tickets),
                "parameters": params
            }
        )
