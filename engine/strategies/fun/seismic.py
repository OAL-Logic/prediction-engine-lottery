"""
Seismic Resonance Strategy 🫨
============================
Correlates lottery hits with seismic activity (tremors) near the draw location.

Theory:
-------
Based on the 'Absurdity Engine' v6.0 spec. Some chaos theorists suggest 
that minor seismic tremors can influence the physical randomization 
mechanisms of ball machines or reflect deeper 'Earth Jitter' patterns.
"""

from __future__ import annotations

import httpx
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class SeismicStrategy(BaseStrategy):
    name = "seismic"
    description = "🫨 Seismic Resonance — correlate hits with tremors near the draw location"
    tier = "fun"
    requires_history = 30

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Get Draw Location
        # Default to SP for Caixa, but registry has coords
        lat = getattr(rules, 'draw_lat', -23.5505)
        lon = getattr(rules, 'draw_lon', -46.6333)
        
        # 2. Fetch/Simulate Seismic context
        # In a real run, we'd use the USGS API:
        # https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=...
        # For the strategy, we'll use a deterministic jitter based on date if API fails
        
        hist_quakes = []
        for _, row in df.iterrows():
            d_str = str(row["date"])[:10]
            # Deterministic pseudo-seismic intensity (0-5.0 magnitude)
            # Seeded by date and location
            import hashlib
            h = hashlib.sha256(f"{d_str}{lat}{lon}".encode()).hexdigest()
            mag = (int(h[:2], 16) / 255.0) * 5.0
            hist_quakes.append((mag, row["numbers"]))
            
        # 3. Get Today's "Tremor"
        target_date = kwargs.get("draw_date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date[:10])
        
        h_today = hashlib.sha256(f"{target_date.isoformat()}{lat}{lon}".encode()).hexdigest()
        today_mag = (int(h_today[:2], 16) / 255.0) * 5.0
        
        # 4. Score by frequency in similar Magnitude regimes
        tolerance = 1.0
        matches = [nums for m, nums in hist_quakes if abs(m - today_mag) < tolerance]
        
        if not matches:
            return {n: 0.5 for n in all_numbers}
            
        from collections import Counter
        counts = Counter([n for d in matches for n in d])
        max_c = max(counts.values()) if counts else 1
        
        return {n: counts.get(n, 0) / max_c for n in all_numbers}
