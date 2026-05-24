"""
Quantum Annealing Approximation Strategy ⚛️
===========================================
Simulates quantum tunneling to escape local minima in historical frequency data.

Theory:
-------
Standard statistical models often get stuck in 'local minima' (overfitting to 
recent hot numbers). Quantum Annealing uses a simulated 'temperature schedule' 
to probabilistically jump to entirely new configurations, discovering hidden 
'Quantum Regimes' of numbers that are theoretically primed but historically dormant.

How it works:
-------------
1. Calculates a base classical score (historical frequency).
2. Applies a simulated quantum perturbation where numbers with historically 
   low scores have a probability of 'tunneling' through the energy barrier 
   to become high-scoring candidates.
3. The tunneling probability is governed by a simulated cooling schedule.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import math
from collections import Counter

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class QuantumStrategy(BaseStrategy):
    name = "quantum_anneal"
    description = "⚛️ Quantum Annealing — Simulated tunneling to escape local minima"
    tier = "statistical"
    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Classical State (Historical Frequency)
        flat = [n for nums in df["numbers"] for n in nums]
        counts = Counter(flat)
        max_c = max(counts.values()) if counts else 1
        classical_scores = {n: counts.get(n, 0) / max_c for n in all_numbers}
        
        # 2. Quantum Perturbation (Tunneling)
        # We simulate an annealing schedule. We want to find numbers that are 
        # 'cold' (low classical score) but might 'tunnel' to a high state.
        
        quantum_scores = {}
        tunneled_numbers = []
        
        # Simulated cooling schedule parameter (fixed for single-shot prediction)
        # Higher beta = higher probability of tunneling
        beta = 0.8 
        
        for n in all_numbers:
            c_score = classical_scores[n]
            
            # Energy barrier: cold numbers have a high barrier to become hot classicaly,
            # but in quantum annealing, they have a chance to tunnel through.
            # Tunneling probability increases as classical score decreases.
            tunnel_prob = math.exp(-c_score / beta) * 0.5 
            
            # Pseudo-random collapse (deterministic based on draw count for testing)
            # In a real quantum system this is probabilistic.
            collapse_val = (hash(f"quantum_{len(df)}_{n}") % 1000) / 1000.0
            
            if collapse_val < tunnel_prob:
                # Tunneling successful: invert the score
                quantum_scores[n] = 1.0 - c_score + 0.2 # Boost tunneled numbers
                tunneled_numbers.append(n)
            else:
                # Stays in classical state, but add slight quantum noise
                quantum_scores[n] = c_score + (collapse_val * 0.1)
                
        # Normalize
        max_q = max(quantum_scores.values()) or 1.0
        final_scores = {n: min(v / max_q, 1.0) for n, v in quantum_scores.items()}
        
        self._meta = {
            "tunneled_count": len(tunneled_numbers),
            "tunneled_sample": tunneled_numbers[:5]
        }
        
        return final_scores

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
