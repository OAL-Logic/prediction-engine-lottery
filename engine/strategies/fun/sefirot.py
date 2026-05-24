"""
Sephoric Tree of Life Strategy 🌳
================================
Maps lottery numbers to the 10 Sephiroth and 22 Paths of the Kabbalistic Tree.

Theory:
-------
Numbers are not just quantities; they are emanations. The Tree of Life provides
a structural map of how 'Idea' becomes 'Manifestation' (Malkuth). 
By identifying which Sephirah or Path is 'Active' in a draw cycle, 
we can predict where the next manifestation will land.

Mapping:
--------
- 1-10:   The 10 Sephiroth (Keter to Malkuth)
- 11-32:  The 22 Paths connecting the Sephiroth
- 33-60:  The 'External Shells' (Qlippoth) and Secondary Harmonics
"""

from __future__ import annotations

import pandas as pd
from collections import Counter, defaultdict
from datetime import date

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

_SEPHIROTH = {
    1: "Keter (Crown)", 2: "Chokmah (Wisdom)", 3: "Binah (Understanding)",
    4: "Chesed (Mercy)", 5: "Gevurah (Severity)", 6: "Tiferet (Beauty)",
    7: "Netzach (Victory)", 8: "Hod (Splendor)", 9: "Yesod (Foundation)",
    10: "Malkuth (Kingdom)"
}

@register
class SefirotStrategy(BaseStrategy):
    name = "sefirot"
    description = "🌳 Sephoric Tree of Life — Emanation paths and Sephirah resonance"
    tier = "fun"
    requires_history = 20

    def __init__(self, draw_date: date | str | None = None) -> None:
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = draw_date or date.today()
        self._meta = {}

    def _get_node_name(self, n: int) -> str:
        if n in _SEPHIROTH: return _SEPHIROTH[n]
        if 11 <= n <= 32: return f"Path {n-10}"
        return f"Harmonic {n}"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Historical Analysis: Which Sephoric Zone is 'Hot'?
        zone_counts = Counter()
        for _, row in df.iterrows():
            for n in row["numbers"]:
                if n <= 10: zone_counts["Sephiroth"] += 1
                elif n <= 32: zone_counts["Paths"] += 1
                else: zone_counts["Harmonics"] += 1
        
        total = sum(zone_counts.values()) or 1
        zone_probs = {k: v / total for k, v in zone_counts.items()}
        
        # Determine current 'Active Node' based on Draw Date
        # Esoteric formula: (Day + Month) % 10 + 1 (Sephirah of the Day)
        active_sephirah_idx = (self.draw_date.day + self.draw_date.month - 1) % 10 + 1
        active_sephirah = _SEPHIROTH[active_sephirah_idx]
        
        self._meta = {
            "active_sephirah": active_sephirah,
            "zone_distribution": {k: f"{v:.1%}" for k, v in zone_probs.items()}
        }
        
        scores = {}
        for n in all_numbers:
            s = 0.5
            # Boost if in the active Sephirah
            if n == active_sephirah_idx: s += 0.4
            
            # Boost based on historical zone probability
            if n <= 10: s += zone_probs.get("Sephiroth", 0.3)
            elif n <= 32: s += zone_probs.get("Paths", 0.3)
            else: s += zone_probs.get("Harmonics", 0.3)
            
            scores[n] = min(s, 1.0)
            
        return scores

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
