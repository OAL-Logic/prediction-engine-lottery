"""
Hardware Entropy Strategy 💻
============================
Bypasses Python's pseudo-random number generator and harvests microscopic
timing jitters from the CPU (via time.perf_counter_ns) to generate "true"
chaotic randomness. This strategy asserts that true randomness aligns 
better with quantum probability events like a lottery draw.
"""

from __future__ import annotations

import time
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class CPUEntropyStrategy(BaseStrategy):
    name = "cpu_entropy"
    description = "💻 Hardware Entropy (CPU White Noise)"
    tier = "fun"

    requires_history = 0 # Pure entropy

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        scores = {}
        
        for n in all_numbers:
            # Harvest entropy
            # We measure the time it takes to do a tiny arbitrary computation
            # This is highly dependent on CPU cache, context switches, etc.
            t0 = time.perf_counter_ns()
            _ = [i * i for i in range(100)]
            t1 = time.perf_counter_ns()
            
            # The lowest bits of the delta are pure noise
            delta = t1 - t0
            # Extract the 8 least significant bits to get a value 0-255
            noise = delta & 0xFF
            
            scores[n] = noise / 255.0
            
            # Add a slight delay to ensure the OS does some scheduling
            time.sleep(0.0001)
            
        return scores
