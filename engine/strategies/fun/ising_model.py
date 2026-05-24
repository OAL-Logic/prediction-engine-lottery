"""
Ising Spin-Glass Model Strategy 🌡️
====================================
Models the lottery pool as a thermodynamic system of interacting spins.
Each number is a spin (drawn = +1, not drawn = -1).
Ferromagnetic couplings (J_ij) are derived from historical co-occurrence.
Local magnetic fields (h_i) are derived from historical individual frequency.
Uses Metropolis-Hastings Monte Carlo to find low-energy (high probability) states.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import random

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class IsingModelStrategy(BaseStrategy):
    name = "ising_model"
    description = "🌡️ Thermodynamic Phase Transition (Ising Model)"
    tier = "fun"

    requires_history = 30

    def __init__(self, steps: int = 5000, temperature: float = 2.0) -> None:
        self.steps = steps
        self.sim_temp = temperature # Thermodynamic temperature, distinct from sampling temp

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        n_numbers = hi - lo + 1
        all_numbers = list(range(lo, hi + 1))
        
        # Calculate local fields (h_i) based on frequency
        counts = {n: 0.0 for n in all_numbers}
        co_occur = {n: {m: 0.0 for m in all_numbers} for n in all_numbers}
        
        total_draws = len(df)
        for row in df.itertuples():
            nums = row.numbers
            for n in nums:
                counts[n] += 1.0
                for m in nums:
                    if n != m:
                        co_occur[n][m] += 1.0
                        
        # Normalize h_i to [-1, 1] based on average
        avg_count = sum(counts.values()) / n_numbers if n_numbers else 1.0
        h = {n: (counts[n] - avg_count) / avg_count for n in all_numbers}
        
        # Calculate couplings (J_ij). 
        # If numbers co-occur often, J > 0 (ferromagnetic, want to be same state)
        # If rarely, J < 0 (anti-ferromagnetic)
        J = {}
        for n in all_numbers:
            J[n] = {}
            for m in all_numbers:
                if n == m:
                    J[n][m] = 0.0
                else:
                    # Expected co-occurrence if independent
                    expected = (counts[n] / total_draws) * (counts[m] / total_draws) * total_draws
                    actual = co_occur[n][m]
                    J[n][m] = (actual - expected) / max(1.0, expected)
                    
        # Metropolis-Hastings Simulation
        # Initialize random state (-1 or 1)
        state = {n: random.choice([-1, 1]) for n in all_numbers}
        
        # Track how often a number is in +1 state during the simulation
        # (Burn-in period: first 20% of steps are ignored)
        burn_in = int(self.steps * 0.2)
        positive_counts = {n: 0.0 for n in all_numbers}
        
        for step in range(self.steps):
            # Pick a random spin to flip
            n = random.choice(all_numbers)
            
            # Calculate energy change dE
            # Energy E = - sum(J_ij s_i s_j) - sum(h_i s_i)
            # If we flip s_n to -s_n, the change is:
            # dE = 2 * s_n * (h_n + sum(J_nm s_m))
            
            interaction = sum(J[n][m] * state[m] for m in all_numbers if m != n)
            dE = 2.0 * state[n] * (h[n] + interaction)
            
            # Acceptance probability
            if dE <= 0:
                state[n] *= -1 # Accept flip (lowers energy)
            else:
                prob = np.exp(-dE / self.sim_temp)
                if random.random() < prob:
                    state[n] *= -1 # Accept flip due to thermal fluctuation
                    
            if step >= burn_in:
                for num in all_numbers:
                    if state[num] == 1:
                        positive_counts[num] += 1.0
                        
        # Final scores based on probability of being in +1 state
        valid_steps = self.steps - burn_in
        scores = {n: positive_counts[n] / valid_steps for n in all_numbers}
        
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: v / max_s for n, v in scores.items()}
