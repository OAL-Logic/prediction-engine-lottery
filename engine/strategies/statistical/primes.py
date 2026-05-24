"""
Prime Oscillator Strategy 🔢
===========================
Correlates the 'Prime Density' of lottery draws with the lunar cycle.

Theory:
-------
Prime numbers represent 'indivisible mathematical building blocks.' 
The Statistician's expert analysis suggests that the density of primes 
in a draw follows a cyclical harmonic pattern entrained to the synodic month.

How it works:
-------------
1. Identify all prime numbers in the lottery's range.
2. Calculate the 'Prime Density' of every historical draw.
3. Group historical draws by Lunar Phase.
4. If the current phase has historically high prime density, boost prime numbers.
"""

from __future__ import annotations

import pandas as pd
from collections import Counter, defaultdict
from datetime import date

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.strategies.fun.moon_phase import moon_phase_bucket, phase_name

def is_prime(n: int) -> bool:
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

@register
class PrimesStrategy(BaseStrategy):
    name = "primes"
    description = "🔢 Prime Oscillator — Prime number density × Lunar cycle harmonics"
    tier = "statistical"
    requires_history = 50

    def __init__(self, draw_date: date | str | None = None) -> None:
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = draw_date or date.today()
        self._meta = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        primes = {n for n in all_numbers if is_prime(n)}
        
        target_bucket = moon_phase_bucket(self.draw_date)
        
        # Historical analysis: Avg Prime Density per Moon Bucket
        phase_prime_density = defaultdict(list)
        matched_rows: list[dict] = []
        
        for _, row in df.iterrows():
            d = row["date"]
            draw_date = d.date() if hasattr(d, "date") else date.fromisoformat(str(d)[:10])
            bucket = moon_phase_bucket(draw_date)
            
            draw_nums = set(row["numbers"])
            prime_count = len(draw_nums & primes)
            density = prime_count / rules.pick_count
            phase_prime_density[bucket].append(density)
            
            if bucket == target_bucket:
                matched_rows.append({
                    "date": draw_date.isoformat(),
                    "numbers": sorted(row["numbers"]),
                    "prime_count": prime_count,
                    "density": f"{density:.1%}"
                })
            
        # Target density for current phase
        densities = phase_prime_density.get(target_bucket, [0.3]) # Baseline 30% primes
        avg_density = sum(densities) / len(densities)
        
        # Metadata
        matched_rows.sort(key=lambda r: r["date"], reverse=True)
        self._meta = {
            "prime_density": round(avg_density, 3),
            "phase": phase_name(self.draw_date),
            "total_primes_in_range": len(primes),
            "matched_draws": len(densities),
            "recent_matches": matched_rows[:self.recent_matches_count]
        }
        
        # Scoring
        scores = {}
        for n in all_numbers:
            # Base score
            s = 0.4
            
            # If high prime density phase, boost primes. 
            # If low, boost composites.
            if n in primes:
                s += (avg_density - 0.25) * 1.5 # Boost if avg density > 25%
            else:
                s += (0.4 - avg_density) * 1.0  # Boost composites if density is low
                
            scores[n] = max(min(s, 1.0), 0.1)
            
        return scores

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
