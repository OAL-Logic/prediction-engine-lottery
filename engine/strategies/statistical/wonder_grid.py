"""
Wonder Grid Strategy 🔮
=====================
Based on Ion Saliu's "Lotto Wonder Grid" methodology.

The strategy works in two phases:
1. Identify a "Key/Favorite" number (the hottest or most overdue).
2. Pair that Key number with the Top 25% of numbers it historically 
   appears with (high-affinity partners).

This strategy focuses on affinity and co-occurrence rather than independent 
probabilities.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class WonderGridStrategy(BaseStrategy):
    name = "wonder_grid"
    description = "🔮 Ion Saliu's Wonder Grid: Key number paired with top 25% affinity partners"
    tier = "statistical"

    requires_history = 50

    def __init__(
        self,
        key_mode: str = "hot",  # "hot" | "overdue"
        affinity_pct: float = 0.25,
    ) -> None:
        """
        Parameters
        ----------
        key_mode
            How to select the 'Key' number. 
            'hot' selects the number with the highest frequency.
            'overdue' selects the number with the largest current gap.
        affinity_pct
            The percentage of the pool to consider as 'Top Pairs' (default 25%).
        """
        self.key_mode = key_mode
        self.affinity_pct = float(affinity_pct)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        import numpy as np
        
        lo, hi = rules.number_range
        pick = rules.pick_count
        pool_size = hi - lo + 1
        n_draws = len(df)
        
        # ── 1. Find the Key Number ───────────────────────────────────────────
        draws_matrix = np.array([sorted(row) for row in df["numbers"]])
        flat_draws = draws_matrix.flatten()
        
        if self.key_mode == "hot":
            # Most frequent
            counts = Counter(flat_draws)
            key_num = counts.most_common(1)[0][0]
        else:
            # Most overdue (largest gap)
            last_indices = np.full(hi + 1, -1)
            for i, row in enumerate(draws_matrix):
                last_indices[row] = i
            gaps = (n_draws - 1) - last_indices[lo:hi+1]
            key_num = lo + np.argmax(gaps)

        # ── 2. Calculate Affinity (Pairs with Key) ───────────────────────────
        # Filter draws containing the key number
        key_mask = [key_num in draw for draw in df["numbers"]]
        key_draws = df[key_mask]
        
        if key_draws.empty:
            # Fallback if key never appeared (unlikely)
            return {n: 1.0 / pool_size for n in range(lo, hi + 1)}

        partner_counts: Counter[int] = Counter()
        for draw in key_draws["numbers"]:
            for n in draw:
                if n != key_num:
                    partner_counts[n] += 1
        
        # ── 3. Assign Scores ─────────────────────────────────────────────────
        # Number of partners to include in the 'Top Affinity' set
        top_n_partners = max(pick - 1, int(pool_size * self.affinity_pct))
        
        top_partners = [n for n, c in partner_counts.most_common(top_n_partners)]
        top_partner_set = set(top_partners)

        scores = {}
        for n in range(lo, hi + 1):
            if n == key_num:
                # Key number gets the absolute highest priority
                scores[n] = 1.0
            elif n in top_partner_set:
                # Affinity partners get high score
                # We can also weight them by their relative frequency with the key
                max_c = partner_counts.most_common(1)[0][1] if partner_counts else 1
                scores[n] = 0.8 * (partner_counts[n] / max_c) + 0.1
            else:
                # The rest get very low score
                scores[n] = 0.05

        return scores
