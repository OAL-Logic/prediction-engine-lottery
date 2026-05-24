"""
Fibonacci / Golden Ratio Strategy  🌀
=======================================
Scores lottery numbers by their relationship to the Fibonacci sequence
and the golden ratio φ = (1 + √5) / 2 ≈ 1.6180339887...

Four scoring layers
--------------------
1. Direct membership  — Is the number itself a Fibonacci number?
                        (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...)
                        Score: +1.0

2. Proximity          — Distance to the nearest Fibonacci number.
                        Score: 1 / (1 + distance)
                        A number immediately adjacent to a Fibonacci number
                        scores nearly as high as the Fibonacci itself.

3. Digit root essence — Does the Pythagorean digit-root of the number
                        equal a single-digit Fibonacci number (1, 2, 3, 5, 8)?
                        Score: +0.5 bonus

4. Golden ratio pair  — For each number n > 1, compute:
                        ratio_up   = n / (n - 1)
                        ratio_down = (n + 1) / n
                        If either ratio is within `phi_tolerance` of φ,
                        the number is in a "golden pair" with its neighbour.
                        Score: +0.4 bonus

The four layer scores are summed and normalised to [0.0, 1.0].

Historical blend
----------------
The base Fibonacci score is blended with a historical frequency signal:
how often did numbers in each Fibonacci proximity tier actually appear?
This grounds the absurdity in real data while keeping the Fibonacci
flavour dominant.

  Final score = 0.6 × fibonacci_score + 0.4 × historical_frequency
"""

from __future__ import annotations

import math

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

_PHI = (1.0 + math.sqrt(5)) / 2.0   # ≈ 1.6180339887


def _fibonacci_set(max_val: int) -> set[int]:
    """Return all Fibonacci numbers up to max_val."""
    fibs: set[int] = set()
    a, b = 1, 1
    while a <= max_val:
        fibs.add(a)
        a, b = b, a + b
    return fibs


def _nearest_fib(n: int, fibs: list[int]) -> int:
    """Return the nearest Fibonacci number to n."""
    return min(fibs, key=lambda f: abs(f - n))


def _digit_reduce(n: int) -> int:
    """Pythagorean reduction to 1–9."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n or 9


_FIB_DIGIT_ROOTS: frozenset[int] = frozenset({1, 2, 3, 5, 8})  # single-digit Fibonacci numbers


@register
class FibonacciStrategy(BaseStrategy):
    name        = "fibonacci"
    description = "🌀 Fibonacci & golden ratio scoring — numbers near φ patterns"
    tier        = "fun"
    requires_history = 1

    def __init__(self, phi_tolerance: float = 0.05, use_history: bool = True) -> None:
        """
        Parameters
        ----------
        phi_tolerance
            Golden ratio tolerance. How close a ratio must be to φ to count as a 
            golden-ratio pair. 0.05 = within 5% of φ.
        use_history
            Historical data blend. If True, numbers that appeared often historically 
            get a boost. Keeps the sequence grounded in data.
        """
        self.phi_tolerance = float(phi_tolerance)
        if isinstance(use_history, str):
            self.use_history = use_history.lower() in ("true", "1", "yes", "y")
        else:
            self.use_history = bool(use_history)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        fib_set  = _fibonacci_set(hi)
        fib_list = sorted(fib_set)

        raw: dict[int, float] = {}
        for num in all_numbers:
            score = 0.0

            # Layer 1: direct Fibonacci membership
            if num in fib_set:
                score += 1.0

            # Layer 2: proximity to nearest Fibonacci number
            nearest = _nearest_fib(num, fib_list)
            distance = abs(num - nearest)
            score += 1.0 / (1.0 + distance)

            # Layer 3: digit-root is a Fibonacci digit
            if _digit_reduce(num) in _FIB_DIGIT_ROOTS:
                score += 0.5

            # Layer 4: golden-ratio pair with neighbour
            if num > 1:
                ratio_up = num / (num - 1)
                if abs(ratio_up - _PHI) / _PHI <= self.phi_tolerance:
                    score += 0.4
            if num < hi:
                ratio_down = (num + 1) / num
                if abs(ratio_down - _PHI) / _PHI <= self.phi_tolerance:
                    score += 0.4

            raw[num] = score

        max_v = max(raw.values()) or 1.0
        fib_scores = {num: raw[num] / max_v for num in all_numbers}

        if not self.use_history or df.empty:
            return fib_scores

        # 2. Fibonacci Frequency Retracement Channels
        # Calculate historical frequency
        counts: dict[int, int] = {num: 0 for num in all_numbers}
        for _, row in df.iterrows():
            for n in row["numbers"]:
                if n in counts:
                    counts[n] += 1

        if not any(counts.values()):
            return fib_scores

        high = max(counts.values())
        low = min(counts.values())
        rng = high - low
        
        # Retracement levels (standard financial Fibonacci levels)
        levels = {
            "23.6%": high - (rng * 0.236),
            "38.2%": high - (rng * 0.382),
            "61.8%": high - (rng * 0.618)
        }
        
        retraced_numbers = []
        
        for n in all_numbers:
            c = counts.get(n, 0)
            # Check if number's frequency is "bouncing" off a support level (within 5% tolerance)
            for lvl_name, lvl_val in levels.items():
                if abs(c - lvl_val) < max(1.0, rng * 0.05):
                    fib_scores[n] += 0.4 # Bounce boost
                    retraced_numbers.append(n)
                    break
                    
        self._meta = {
            "ath_freq": high,
            "low_freq": low,
            "retraced_count": len(retraced_numbers),
            "retracement_sample": list(set(retraced_numbers))[:5]
        }

        # Final Normalization
        max_s = max(fib_scores.values()) or 1.0
        return {n: min(v / max_s, 1.0) for n, v in fib_scores.items()}

    def suggest(self, *args, **kwargs):
        from engine.strategies import SuggestionResult
        result = super().suggest(*args, **kwargs)
        if hasattr(self, "_meta"):
            result.metadata.update(self._meta)
        return result
