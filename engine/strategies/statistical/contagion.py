"""
Cluster Contagion Strategy 🦠
============================
Scores numbers based on 'Board Contagion' — adjacency to previous winners.

Theory:
-------
Based on the physical mechanics of pneumatic machines, this strategy assumes 
that winners 'Spark' their grid neighbors on the board. We model the 
'Lagged Adjacency' effect: how often does a number hit in Draw N if its 
physical grid neighbor hit in Draw N-1?
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Any, Dict, List
from collections import Counter

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules.geometry import BoardGeometry

@register
class ContagionStrategy(BaseStrategy):
    name = "contagion"
    description = "🦠 Cluster Contagion — Lagged adjacency resonance (Board Contagion)"
    tier = "statistical"
    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Setup Geometry
        cols = 5 if "lotofacil" in rules.name.lower() else 10
        geo = BoardGeometry(max_n=hi, cols=cols)
        
        # 2. Historical Analysis: Does adjacency to PREVIOUS winners matter?
        # we track: (neighbor_of_prev_winner -> did_hit)
        contagion_counts = Counter()
        total_neighbor_occurrences = Counter()
        
        for i in range(1, len(df)):
            prev_winners = set(df.iloc[i-1]["numbers"])
            curr_winners = set(df.iloc[i]["numbers"])
            
            # Find all numbers that were neighbors of prev winners
            neighbors = set()
            for w in prev_winners:
                neighbors.update(geo.get_neighbors(w))
            
            for n in neighbors:
                total_neighbor_occurrences[n] += 1
                if n in curr_winners:
                    contagion_counts[n] += 1
        
        # 3. Current State
        last_winners = set(df.iloc[-1]["numbers"])
        active_neighbors = set()
        for w in last_winners:
            active_neighbors.update(geo.get_neighbors(w))
            
        # 4. Scoring
        scores = {}
        for n in all_numbers:
            # Base probability of being 'sparked'
            prob = contagion_counts.get(n, 0) / max(total_neighbor_occurrences.get(n, 0), 1)
            
            # If the number is currently a neighbor of a winner, boost its probability
            if n in active_neighbors:
                scores[n] = 0.5 + (prob * 0.5)
            else:
                scores[n] = prob * 0.5 # Dormant potential
                
        # 5. Metadata
        self._meta = {
            "active_neighbors": sorted(list(active_neighbors))[:10],
            "top_contagion_nodes": sorted(contagion_counts, key=contagion_counts.get, reverse=True)[:5]
        }

        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        return {n: s / max_s for n, s in scores.items()}

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
