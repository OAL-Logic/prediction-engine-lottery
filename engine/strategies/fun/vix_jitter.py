"""
VIX Jitter Strategy 📉
====================
Correlates historical lottery anomalies with global financial volatility (VIX).

Theory:
-------
"Do lottery machines panic when humans panic?"
The CBOE Volatility Index (VIX) measures market expectation of near-term volatility.
This strategy tests the absurd hypothesis that periods of extreme human financial
anxiety (high VIX) create a "Jitter Resonance" that affects mechanical randomness,
causing "safe" or "popular" numbers to hit less frequently.

How it works:
-------------
1. Maps historical dates to simulated VIX regimes (Calm, Anxious, Panic).
   (Note: Uses a deterministic pseudo-VIX for standalone operation, but structured 
   to accept real API data).
2. If the current regime is "Panic", it aggressively boosts numbers that have 
   historically hit during other market crashes.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from datetime import date
from typing import Any

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

def _get_pseudo_vix(d: date) -> float:
    """
    Generates a deterministic pseudo-VIX score (10.0 to 80.0) based on date.
    Simulates known historical spikes (e.g., 2008 crash, 2020 pandemic).
    """
    # Base baseline
    base = 15.0
    
    # 2008 Financial Crisis (Oct-Nov)
    if d.year == 2008 and d.month in [10, 11]:
        return 60.0 + (d.day % 20)
        
    # 2020 COVID Crash (March)
    if d.year == 2020 and d.month == 3:
        return 70.0 + (d.day % 10)
        
    # Standard cyclical noise
    days = d.toordinal()
    noise = math.sin(days * 0.1) * 5 + math.cos(days * 0.05) * 3
    
    # Add a pseudo-random spike every ~100 days
    rng = random.Random(days)
    if rng.random() > 0.98:
        return 35.0 + rng.random() * 15.0
        
    return max(10.0, base + noise)

def _vix_regime(vix: float) -> str:
    if vix < 20.0: return "Calm"
    if vix < 35.0: return "Anxious"
    return "Panic"

@register
class VixJitterStrategy(BaseStrategy):
    name        = "vix_jitter"
    description = "📉 Financial Volatility Resonance — correlate hits with global anxiety (VIX)"
    tier        = "fun"
    requires_history = 50

    def __init__(self, draw_date: date | str | None = None, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        draw_date : date | str | None
            The target date to evaluate market volatility. 
            (💡 Tip: Leave blank to use today's sentiment).
        """
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            try:
                self.draw_date = date.fromisoformat(draw_date[:10])
            except ValueError:
                self.draw_date = date.today()
        else:
            self.draw_date = draw_date or date.today()

        self._meta: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        """
        Calculates scores by matching the current 'Market Anxiety' with historical draws.

        🧠 Technical Stuff: 
        Matches the target pseudo-VIX regime (Calm/Anxious/Panic) against 
        historical volatility windows to find numbers that thrive in chaos.
        """
        lo, hi = rules.number_range

        all_numbers = list(range(lo, hi + 1))
        
        target_vix = _get_pseudo_vix(self.draw_date)
        target_regime = _vix_regime(target_vix)
        
        bucket_counts: dict[str, Counter] = defaultdict(Counter)
        bucket_draws: dict[str, int] = defaultdict(int)
        
        for _, row in df.iterrows():
            d_val = row["date"]
            if pd.isna(d_val): continue
            
            d_obj = d_val.date() if hasattr(d_val, "date") else date.fromisoformat(str(d_val)[:10])
            vix = _get_pseudo_vix(d_obj)
            regime = _vix_regime(vix)
            
            bucket_counts[regime].update(row["numbers"])
            bucket_draws[regime] += 1
            
        target_counts = bucket_counts.get(target_regime, Counter())
        target_n = bucket_draws.get(target_regime, 0)
        
        self._meta = {
            "target_vix": round(target_vix, 2),
            "market_regime": target_regime,
            "matched_historical_draws": target_n,
            "top_panic_numbers": [n for n, c in bucket_counts.get("Panic", Counter()).most_common(5)]
        }
        
        if target_n == 0:
            return {n: 0.5 for n in all_numbers}
            
        raw = {n: target_counts.get(n, 0) / target_n for n in all_numbers}
        max_v = max(raw.values()) or 1.0
        return {n: v / max_v for n, v in raw.items()}

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
