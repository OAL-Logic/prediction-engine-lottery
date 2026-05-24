"""
Monte Carlo Strategy
====================
Simulates N future draws by sampling from a weighted distribution derived
from historical frequency + gap patterns.

Each simulated draw is "scored" against historical quality criteria
(sum range, odd/even ratio). Numbers that appear more often in
high-quality simulated draws get higher scores.

This separates Monte Carlo into two phases:
  1. Simulate  — generate future draws using a seeded weighted sampler
  2. Filter    — keep only draws that match historical distribution patterns
  3. Score     — rank numbers by frequency in the kept simulations

Temperature note: the Monte Carlo sampler already has its own temperature
(via `sim_temperature`). The suggest() temperature controls final ticket
sampling on top of that.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from collections import Counter

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class MonteCarloStrategy(BaseStrategy):
    name = "monte_carlo"
    description = "🎲 Monte Carlo simulation — frequency-weighted draws filtered by historical quality"
    tier = "statistical"

    requires_history = 50

    def __init__(self, n_simulations: int = 10_000, sim_temperature: float = 1.2) -> None:
        """
        Parameters
        ----------
        n_simulations
            Simulation depth. How many future draws to imagine. Higher values (e.g. 50,000) 
            are more accurate but take longer to compute.
        sim_temperature
            Prediction sharpness. Controls how much we rely on historical frequency during 
            simulation. Higher (1.5+) = more varied/random simulations. 
            Lower (0.8) = focused on hot numbers.
        """
        self.n_simulations   = n_simulations
        self.sim_temperature = sim_temperature

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pick = rules.pick_count

        # --- Base weights from historical frequency ---
        flat = [n for nums in df["numbers"] for n in nums]
        freq = Counter(flat)
        raw  = np.array([max(freq.get(n, 0) + 1, 1) for n in all_numbers], dtype=float)
        raw  = raw ** (1.0 / self.sim_temperature)
        base_probs = raw / raw.sum()

        # --- Historical quality bounds ---
        sums      = [sum(nums) for nums in df["numbers"]]
        odd_ratios = [sum(1 for n in nums if n % 2 != 0) / len(nums) for nums in df["numbers"]]
        
        # Use analytical sum if possible, else empirical
        from engine.modules import sum_range
        sum_lo, sum_hi, _, _ = sum_range.most_probable_range(rules)
        odd_lo, odd_hi   = np.percentile(odd_ratios, 5), np.percentile(odd_ratios, 95)

        # --- Vectorized Simulation using Gumbel-max trick ---
        n_numbers = len(all_numbers)
        
        # Generate all combos at once
        u = np.random.uniform(size=(self.n_simulations, n_numbers))
        keys = -np.log(u + 1e-10) / (base_probs + 1e-10)
        
        # Top `pick` indices per sample
        combo_indices = np.argsort(keys, axis=1)[:, -pick:]
        
        # Map indices to numbers
        numbers_array = np.array(all_numbers)
        combos = numbers_array[combo_indices]
        
        # Calculate stats for all combos
        s = combos.sum(axis=1)
        o = (combos % 2 != 0).mean(axis=1)
        
        # Filter mask
        mask = (s >= sum_lo) & (s <= sum_hi) & (o >= odd_lo) & (o <= odd_hi)
        
        # Get passing combos
        good_combos = combos[mask]
        kept = len(good_combos)

        if kept == 0:
            # Fallback: no draws passed filter, use raw frequency
            return {n: float(freq.get(n, 0)) for n in all_numbers}

        # Count frequencies in good combos
        flat_good = good_combos.flatten()
        unique, counts = np.unique(flat_good, return_counts=True)
        counter = dict(zip(unique, counts))
        
        total = kept * pick
        return {n: counter.get(n, 0) / total for n in all_numbers}
