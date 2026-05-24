"""
Moon Phase Strategy  🌕
========================
Correlates lottery draw outcomes with the lunar phase on the draw date.

No external dependencies — moon phase is calculated with pure arithmetic
using the known new moon epoch (Jan 6, 2000).

Lunar phases (8 segments)
--------------------------
  0  New Moon          (0.00 – 0.125)
  1  Waxing Crescent   (0.125 – 0.25)
  2  First Quarter     (0.25 – 0.375)
  3  Waxing Gibbous    (0.375 – 0.50)
  4  Full Moon         (0.50 – 0.625)
  5  Waning Gibbous    (0.625 – 0.75)
  6  Last Quarter      (0.75 – 0.875)
  7  Waning Crescent   (0.875 – 1.00)

How it works
------------
1. Compute the moon phase for every historical draw date
2. Group draws by phase bucket
3. For the upcoming draw date, compute its moon phase
4. Score each number by its appearance frequency in draws that share
   the same phase bucket

If the upcoming draw date is not known, we use today + 1.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from collections import Counter, defaultdict
from typing import Any

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

_LUNAR_CYCLE = 29.53058867        # synodic days (phases)
_ANOMALISTIC = 27.554551          # days (perigee to perigee)
_KNOWN_NEW   = date(2000, 1, 6)   # reference new moon
_KNOWN_PERIGEE = date(2000, 1, 10) # approximate reference perigee

_PHASE_NAMES = [
    "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
    "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
]


def moon_phase_ratio(d: date | str) -> float:
    """Return moon phase as a float 0.0 (new) → ~1.0 (back to new)."""
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d[:10])
        except ValueError:
            return 0.0
    
    import pandas as pd
    if pd.isna(d):
        return 0.0

    days = (d - _KNOWN_NEW).days
    return (days % _LUNAR_CYCLE) / _LUNAR_CYCLE


def moon_distance_ratio(d: date | str) -> float:
    """
    Return moon distance as a float 0.0 (perigee/closest) → 1.0 (apogee/farthest).
    Uses a simple sinusoidal approximation.
    """
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d[:10])
        except ValueError:
            return 0.5
            
    import pandas as pd
    if pd.isna(d):
        return 0.5

    days = (d - _KNOWN_PERIGEE).days
    # Use cosine so 0.0 days (perigee) = cos(0) = 1.0 (mapped to 0.0 distance)
    # We want perigee to be 0.0 and apogee to be 1.0
    val = math.cos(2 * math.pi * (days % _ANOMALISTIC) / _ANOMALISTIC)
    return (1.0 - val) / 2.0


def tidal_intensity(phase_ratio: float, dist_ratio: float) -> float:
    """
    Calculate tidal intensity (0.0 to 1.0).
    Higher at New/Full moon (Syzygy) and Perigee (Proxigean).
    """
    # Phase effect: strongest at 0.0 (New) and 0.5 (Full)
    phase_factor = math.cos(4 * math.pi * phase_ratio) # Peaks at 0, 0.5, 1.0
    phase_factor = (phase_factor + 1.0) / 2.0
    
    # Distance effect: strongest at 0.0 (Perigee)
    dist_factor = 1.0 - dist_ratio
    
    return (0.7 * phase_factor + 0.3 * dist_factor)


def moon_phase_bucket(d: date | str) -> int:
    """Return phase bucket 0–7."""
    return int(moon_phase_ratio(d) * 8) % 8


def phase_name(d: date | str) -> str:
    return _PHASE_NAMES[moon_phase_bucket(d)]


@register
class MoonPhaseStrategy(BaseStrategy):
    name        = "moon_phase"
    description = "🌕 Lunar phase correlation — numbers that shine under the same moon"
    tier        = "fun"
    requires_history = 30

    def __init__(self, upcoming_draw_date: date | None = None) -> None:
        self.upcoming_draw_date = upcoming_draw_date or date.today()
        self._correlation: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        target_bucket = moon_phase_bucket(self.upcoming_draw_date)
        target_ratio  = moon_phase_ratio(self.upcoming_draw_date)
        target_dist   = moon_distance_ratio(self.upcoming_draw_date)
        target_tide   = tidal_intensity(target_ratio, target_dist)

        # Tidal bucket: light, normal, heavy
        def _tide_bucket(t: float) -> str:
            if t < 0.33: return "low"
            if t < 0.66: return "normal"
            return "high"
            
        target_t_bucket = _tide_bucket(target_tide)

        # Group historical draws by composite bucket (Phase + Tide)
        bucket_counts: dict[str, Counter] = defaultdict(Counter)
        bucket_total:  dict[str, int]     = defaultdict(int)
        matched_rows:  list[dict]         = []

        for _, row in df.iterrows():
            try:
                d = row["date"]
                draw_date = d.date() if hasattr(d, "date") else date.fromisoformat(str(d)[:10])
                p_bucket  = moon_phase_bucket(draw_date)
                p_ratio   = moon_phase_ratio(draw_date)
                d_ratio   = moon_distance_ratio(draw_date)
                tide      = tidal_intensity(p_ratio, d_ratio)
                t_bucket  = _tide_bucket(tide)
                
                # Composite key
                key = f"{p_bucket}_{t_bucket}"
                bucket_counts[key].update(row["numbers"])
                bucket_total[key] += 1
                
                if p_bucket == target_bucket and t_bucket == target_t_bucket:
                    matched_rows.append({
                        "date":    draw_date.isoformat(),
                        "numbers": sorted(row["numbers"]),
                        "phase":   phase_name(draw_date),
                        "tide":    t_bucket,
                        "intensity": round(tide, 2)
                    })
            except Exception:
                continue

        target_key    = f"{target_bucket}_{target_t_bucket}"
        target_counts = bucket_counts.get(target_key, Counter())
        target_draws  = bucket_total.get(target_key, 0)

        # Build correlation evidence
        matched_rows.sort(key=lambda r: r["date"], reverse=True)
        top_numbers = [
            {"number": n, "frequency": target_counts.get(n, 0)}
            for n, _ in target_counts.most_common(self.top_numbers_count)
        ]
        self._correlation = {
            "phase_name":    phase_name(self.upcoming_draw_date),
            "phase_bucket":  target_bucket,
            "phase_ratio":   round(target_ratio, 4),
            "moon_distance": "Perigee" if target_dist < 0.2 else "Apogee" if target_dist > 0.8 else "Neutral",
            "tidal_intensity": target_t_bucket,
            "matched_draws": target_draws,
            "recent_matches": matched_rows[:self.recent_matches_count],
            "top_numbers":   top_numbers,
        }

        if target_draws == 0:
            return {n: 1.0 / len(all_numbers) for n in all_numbers}

        raw = {n: target_counts.get(n, 0) / target_draws for n in all_numbers}
        max_v = max(raw.values()) or 1.0
        return {n: v / max_v for n, v in raw.items()}

    # ------------------------------------------------------------------
    # suggest() — override to inject correlation evidence
    # ------------------------------------------------------------------

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._correlation)
        return result
