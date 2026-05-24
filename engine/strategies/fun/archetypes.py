"""
Number Archetypes Strategy 🎭
=============================
Classifies every number into one of 5 psychological archetypes
based on its recent historical behavior. 
Generates tickets that have a 'Balanced Narrative' (mix of archetypes).

Archetypes:
- THE HERO: High momentum, frequently hit.
- THE SHADOW: Deeply overdue, hiding in the dark.
- THE TRICKSTER: Unpredictable, high variance in gaps.
- THE SAGE: Long-term statistical stability.
- THE CHILD: Recently 'reborn' (emerged from a long cold streak).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class ArchetypesStrategy(BaseStrategy):
    name = "archetypes"
    description = "🎭 Numerical Archetypes (Balanced Narrative)"
    tier = "fun"

    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        n_draws = len(df)
        
        # 1. Calculate Metrics
        hits = {n: 0 for n in all_numbers}
        gaps = {n: [] for n in all_numbers}
        last_seen = {n: -1 for n in all_numbers}
        
        for i, row in enumerate(df.itertuples()):
            for num in row.numbers:
                hits[num] += 1
                if last_seen[num] != -1:
                    gaps[num].append(i - last_seen[num])
                last_seen[num] = i
                
        current_gaps = {n: (n_draws - 1 - last_seen[n]) for n in all_numbers}
        
        # 2. Assign Archetypes
        # Heuristics for classification
        avg_hits = np.mean(list(hits.values()))
        avg_gap = np.mean([np.mean(g) if g else 20 for g in gaps.values()])
        
        scores = {}
        self._archetypes = {}
        
        for n in all_numbers:
            num_hits = hits[n]
            cur_gap = current_gaps[n]
            var_gap = np.var(gaps[n]) if len(gaps[n]) > 1 else 0
            
            # Logic
            if num_hits > avg_hits * 1.3:
                arch = "THE HERO"
                base_score = 0.8
            elif cur_gap > avg_gap * 2.5:
                arch = "THE SHADOW"
                base_score = 0.9
            elif var_gap > 50:
                arch = "THE TRICKSTER"
                base_score = 0.6
            elif abs(num_hits - avg_hits) < (avg_hits * 0.1):
                arch = "THE SAGE"
                base_score = 0.7
            elif cur_gap < 2 and max(gaps[n] or [0]) > avg_gap * 3:
                arch = "THE CHILD"
                base_score = 1.0 # High priority for the newly reborn
            else:
                arch = "THE CITIZEN" # Standard background
                base_score = 0.4
                
            self._archetypes[n] = arch
            scores[n] = base_score + (n % 10) * 0.01 # jitter
            
        return scores

    def suggest(self, df: pd.DataFrame, rules: DrawRules, **kwargs):
        # We override suggest to ensure archetypal balance
        scores = self.score(df, rules)
        pick = rules.pick_count
        
        # Ensure we have at least one from each interesting category if possible
        archetype_groups = {}
        for n, arch in self._archetypes.items():
            if arch not in archetype_groups: archetype_groups[arch] = []
            archetype_groups[arch].append(n)
            
        # Sampling logic: 
        # Pick 1 Hero, 1 Shadow, 1 Child/Trickster, fill rest with highest scores
        ticket = []
        
        def pick_from(arch_name):
            if arch_name in archetype_groups:
                pool = archetype_groups[arch_name]
                # Pick the one with highest score in that pool
                best = max(pool, key=lambda x: scores[x])
                if best not in ticket:
                    ticket.append(best)

        pick_from("THE HERO")
        pick_from("THE SHADOW")
        pick_from("THE CHILD")
        
        # Fill the rest
        sorted_all = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        for n in sorted_all:
            if len(ticket) >= pick: break
            if n not in ticket:
                ticket.append(n)
                
        from engine.strategies import SuggestionResult
        res = SuggestionResult(
            strategy_name=self.name,
            tickets=[sorted(ticket)],
            scores=scores,
            confidence=0.65,
            metadata={"archetypes": self._archetypes}
        )
        return res
