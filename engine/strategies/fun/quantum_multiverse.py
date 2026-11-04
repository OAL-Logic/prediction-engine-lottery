"""
Quantum Multiverse & Immortality Strategy 🌌
============================================
Based on Hugh Everett III's Many-Worlds Interpretation (1957) and Max Tegmark's
Quantum Immortality thought experiment (1998).

Theory:
-------
Every lottery draw constitutes a macroscopic quantum measurement that branches the
universal wave function |Ψ⟩ into decoherent parallel realities. Under quantum
anthropic selection (the 'Quantum Immortality' conjecture), an observer only
perceives trajectories where constructive interference preserves the observer's
winning timeline.

Mechanics:
----------
1. Simulates M parallel universe branches (default: M=1000).
2. Uses OS physical entropy (/dev/urandom via secrets/hashlib) to compute complex
   quantum state amplitudes c_m = a_m + i*b_m for each candidate number in the pool.
3. Modulates state vectors using historical transition coherence (phase shifts).
4. Computes probability densities P(n) = |ψ(n)|² = ∑_m |c_{m,n}|² and normalizes
   them across the number range defined by DrawRules.
"""

from __future__ import annotations

import hashlib
import math
import os
import secrets
from typing import Any

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class QuantumMultiverseStrategy(BaseStrategy):
    name = "quantum_multiverse"
    description = "🌌 Quantum Multiverse & Immortality (Everett Branching & Anthropic Selection)"
    tier = "fun"
    requires_history = 5

    def __init__(self, branches: int = 1000, coherence_decay: float = 0.85, seed: int | None = None) -> None:
        """
        Parameters
        ----------
        branches : int
            Number of simulated Everett universe branches (M).
        coherence_decay : float
            Decoherence rate factor between past draws and current superposition.
        seed : int | None
            Optional deterministic seed for reproducible backtesting.
        """
        self.branches = max(100, int(branches))
        self.coherence_decay = float(coherence_decay)
        self.seed = seed

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool_size = len(all_numbers)

        if pool_size == 0:
            return {}

        # 1. Base quantum phase from historical decoherence
        # Calculate empirical frequency and phase angle from recent draws
        recent_df = df.tail(20) if len(df) >= 20 else df
        freq_map: dict[int, int] = {n: 0 for n in all_numbers}
        for row in recent_df.itertuples():
            nums = getattr(row, "numbers", None)
            if nums:
                for num in nums:
                    if num in freq_map:
                        freq_map[num] += 1

        total_recent_draws = max(1, len(recent_df))

        # 2. Derive entropy source: OS hardware entropy or seeded PRNG
        if self.seed is not None:
            rng = np.random.default_rng(self.seed)
        else:
            # Gather OS physical entropy (32 bytes)
            raw_entropy = os.urandom(32)
            seed_int = int.from_bytes(raw_entropy[:8], byteorder="big")
            rng = np.random.default_rng(seed_int)

        # 3. Simulate M Everett branches
        # Complex state amplitudes: shape (branches, pool_size)
        real_parts = rng.normal(loc=0.0, scale=1.0, size=(self.branches, pool_size))
        imag_parts = rng.normal(loc=0.0, scale=1.0, size=(self.branches, pool_size))

        # 4. Apply anthropic constructive interference phase
        # Numbers with balanced historical resonance receive constructive phase coherence
        phase_shifts = np.zeros(pool_size, dtype=np.float64)
        for idx, n in enumerate(all_numbers):
            rel_freq = freq_map[n] / total_recent_draws
            # Quantum phase theta_n proportional to empirical frequency and golden ratio
            phase_shifts[idx] = (rel_freq * 2.0 * math.pi) + (n * ((math.sqrt(5) - 1) / 2.0))

        cos_phase = np.cos(phase_shifts)
        sin_phase = np.sin(phase_shifts)

        # Apply phase modulation across branches
        mod_real = (real_parts * cos_phase) - (imag_parts * sin_phase)
        mod_imag = (real_parts * sin_phase) + (imag_parts * cos_phase)

        # 5. Modulate with anthropic filter: survival weight in winning timelines
        # In the Everett multiverse, branches where numbers form viable non-degenerate
        # distributions interfere constructively
        branch_amplitudes = np.sqrt(mod_real**2 + mod_imag**2)
        survivor_magnitudes = np.mean(branch_amplitudes, axis=0)

        # Calculate |psi(n)|^2
        prob_densities = survivor_magnitudes**2
        total_density = np.sum(prob_densities)

        if total_density > 0:
            prob_densities = prob_densities / total_density
        else:
            prob_densities = np.full(pool_size, 1.0 / pool_size)

        return {n: float(prob_densities[idx]) for idx, n in enumerate(all_numbers)}
