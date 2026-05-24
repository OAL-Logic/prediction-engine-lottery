"""
Noosphere Jitter Strategy 🧠
===========================
Simulates the 'Global Consciousness Project' (GCP) by calculating 
vibrational jitter in the human Noosphere.

Theory:
-------
Mass human events (news, emotions, focus) create coherent fluctuations 
in random number generators. By identifying 'Entropy Peaks' in current 
global data, we can detect when the lottery machines are most likely 
to deviate from historical averages.

How it works:
-------------
1. Calculates a 'Noosphere Seed' based on current top global news / time-drift.
2. Identifies 'Global Focus' peaks.
3. Modifies sampling temperature based on detected Jitter.
"""

from __future__ import annotations

import pandas as pd
import hashlib
import time
from datetime import date

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class NoosphereStrategy(BaseStrategy):
    name = "noosphere"
    description = "🧠 Noosphere Jitter — Global consciousness entropy peaks"
    tier = "fun"
    requires_history = 1

    def __init__(self, draw_date: date | str | None = None) -> None:
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = date.today()
        self._meta = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Calculate 'Noosphere Jitter' based on high-frequency time data
        # Simulated drift: how many seconds since the last hour, hashed
        t = time.time()
        jitter_hash = hashlib.sha256(str(int(t // 3600)).encode()).hexdigest()
        jitter_val = int(jitter_hash[:4], 16) / 65535.0
        
        # Entropy Peak detection (Pseudo-OSINT)
        # If jitter is high, we are in a 'Volatile' consciousness regime
        is_volatile = jitter_val > 0.7
        intensity = "Volatile" if is_volatile else "Stable" if jitter_val < 0.3 else "Coherent"
        
        self._meta = {
            "noosphere_intensity": intensity,
            "jitter_score": round(jitter_val, 3),
            "regime": "High Focus" if is_volatile else "Default Resonance"
        }
        
        scores = {}
        for n in all_numbers:
            # Hash every number against the hourly jitter
            n_hash = hashlib.sha256(f"{jitter_hash}{n}".encode()).hexdigest()
            n_jitter = int(n_hash[:2], 16) / 255.0
            
            # Blend base score (0.5) with local jitter
            scores[n] = 0.3 + (n_jitter * 0.7)
            
        return scores

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
