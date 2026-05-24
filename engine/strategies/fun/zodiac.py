"""
Zodiac Strategy  ♈
====================
Scores lottery numbers based on the Western astrological sign of
the draw date — correlating the zodiac's elemental and numerical
associations with historical draw outcomes.

The twelve signs
-----------------
Each sign spans roughly 30 days of the solar year and carries:

  Element    Fire (Aries, Leo, Sagittarius)
             Earth (Taurus, Virgo, Capricorn)
             Air (Gemini, Libra, Aquarius)
             Water (Cancer, Scorpio, Pisces)

  Modality   Cardinal, Fixed, Mutable (less relevant here)

  Lucky numbers  Traditional numerological associations per sign.

Scoring layers
--------------
1. Direct lucky numbers (highest score: 1.0)
   Each sign has 3–5 traditionally lucky numbers.

2. Elemental range (score: 0.7)
   The number pool is divided into 4 elemental quadrants:
     Fire:  numbers in the lowest quartile
     Earth: second quartile
     Air:   third quartile
     Water: highest quartile
   Numbers in the same element as today's sign score 0.7.

3. Compatible signs (score: 0.5)
   Signs of the same element are compatible (trine aspect).
   Their lucky numbers also score 0.5.

4. Baseline (score: 0.1)
   All other numbers.

Historical correlation
-----------------------
Like moon_phase, the final score blends the pure zodiac signal with
the historical frequency of numbers in draws that shared the same
zodiac sign. This surfaces any genuine data-backed patterns while
retaining the zodiac flavour.

  Final = 0.55 × zodiac_score + 0.45 × historical_freq
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register


# ---------------------------------------------------------------------------
# Zodiac data
# ---------------------------------------------------------------------------

# (sign_name, month_start, day_start, month_end, day_end, element, lucky_numbers)
_SIGNS: list[tuple] = [
    ("Aries",       3, 21,  4, 19,  "Fire",   [1, 9, 19, 41]),
    ("Taurus",      4, 20,  5, 20,  "Earth",  [2, 6, 24, 42]),
    ("Gemini",      5, 21,  6, 20,  "Air",    [3, 5, 14, 23]),
    ("Cancer",      6, 21,  7, 22,  "Water",  [2, 7, 11, 29]),
    ("Leo",         7, 23,  8, 22,  "Fire",   [1, 10, 19, 40]),
    ("Virgo",       8, 23,  9, 22,  "Earth",  [5, 14, 23, 32]),
    ("Libra",       9, 23, 10, 22,  "Air",    [4, 6, 15, 24]),
    ("Scorpio",    10, 23, 11, 21,  "Water",  [8, 11, 18, 22]),
    ("Sagittarius",11, 22, 12, 21,  "Fire",   [3, 9, 21, 36]),
    ("Capricorn",  12, 22,  1, 19,  "Earth",  [4, 8, 13, 17]),
    ("Aquarius",    1, 20,  2, 18,  "Air",    [4, 7, 11, 22]),
    ("Pisces",      2, 19,  3, 20,  "Water",  [3, 7, 12, 29]),
]

_ELEMENT_COLORS = {
    "Fire":  "♈🔥",
    "Earth": "♉🌍",
    "Air":   "♊💨",
    "Water": "♋💧",
}


def _sign_for_date(d: date) -> dict:
    """Return the zodiac sign dict for a given date."""
    m, day = d.month, d.day
    for name, ms, ds, me, de, element, lucky in _SIGNS:
        # Handle signs that span year-end (Capricorn: Dec 22 – Jan 19)
        if ms == me:
            if m == ms and ds <= day <= de:
                return {"name": name, "element": element, "lucky": lucky}
        elif ms < me:
            if (m == ms and day >= ds) or (m == me and day <= de) or (ms < m < me):
                return {"name": name, "element": element, "lucky": lucky}
        else:
            # Wraps year (e.g., Dec 22 – Jan 19)
            if (m == ms and day >= ds) or (m == me and day <= de) or m > ms or m < me:
                return {"name": name, "element": element, "lucky": lucky}
    # Fallback: Capricorn (rare edge case)
    return {"name": "Capricorn", "element": "Earth", "lucky": [4, 8, 13, 17]}


def _element_for_sign(name: str) -> str:
    for sign in _SIGNS:
        if sign[0] == name:
            return sign[5]
    return "Earth"


def _lucky_for_element(element: str, hi: int) -> list[int]:
    """Collect all lucky numbers for all signs of a given element, clipped to pool."""
    out: list[int] = []
    for sign in _SIGNS:
        if sign[5] == element:
            out.extend(n for n in sign[6] if n <= hi)
    return list(set(out))


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@register
class ZodiacStrategy(BaseStrategy):
    name        = "zodiac"
    description = "♈ Western zodiac — elemental and numerical resonance of the draw date"
    tier        = "fun"
    requires_history = 30

    def __init__(self, draw_date: date | str | None = None) -> None:
        """
        Parameters
        ----------
        draw_date
            Upcoming Draw Date. The date to score for, determining the active 
            Western zodiac sign.
        """
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = draw_date or (date.today() + timedelta(days=1))
        self._correlation: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)

        sign = _sign_for_date(self.draw_date)

        # Elemental quartile boundaries (scale to pool)
        q = pool // 4
        element_ranges = {
            "Fire":  set(all_numbers[:q]),
            "Earth": set(all_numbers[q: 2 * q]),
            "Air":   set(all_numbers[2 * q: 3 * q]),
            "Water": set(all_numbers[3 * q:]),
        }
        sign_element  = sign["element"]
        compat_luckies = set(_lucky_for_element(sign_element, hi))

        # Clip lucky numbers to pool
        lucky_set = set(n for n in sign["lucky"] if lo <= n <= hi)

        # Base zodiac score
        base_scores: dict[int, float] = {}
        for num in all_numbers:
            if num in lucky_set:
                base_scores[num] = 1.0
            elif num in compat_luckies:
                base_scores[num] = 0.6
            elif num in element_ranges.get(sign_element, set()):
                base_scores[num] = 0.4
            else:
                base_scores[num] = 0.1

        # Historical correlation: draws under the same zodiac sign
        sign_counts: Counter = Counter()
        matched_draws = 0
        matched_rows: list[dict] = []

        for _, row in df.iterrows():
            try:
                raw       = row["date"]
                draw_date = raw.date() if hasattr(raw, "date") else date.fromisoformat(str(raw)[:10])
                row_sign  = _sign_for_date(draw_date)
                if row_sign["name"] == sign["name"]:
                    sign_counts.update(row["numbers"])
                    matched_draws += 1
                    matched_rows.append({
                        "date":    draw_date.isoformat(),
                        "numbers": sorted(row["numbers"]),
                        "sign":    row_sign["name"],
                    })
            except Exception:
                continue

        matched_rows.sort(key=lambda r: r["date"], reverse=True)
        top_numbers = [
            {"number": n, "frequency": sign_counts.get(n, 0)}
            for n, _ in sign_counts.most_common(10)
        ]
        self._correlation = {
            "sign":          sign["name"],
            "element":       sign_element,
            "lucky_numbers": sorted(lucky_set),
            "matched_draws": matched_draws,
            "recent_matches": matched_rows[:5],
            "top_numbers":   top_numbers,
        }

        if matched_draws == 0:
            return base_scores

        max_h = max(sign_counts.values()) or 1.0
        hist_norm = {n: sign_counts.get(n, 0) / max_h for n in all_numbers}

        return {
            n: 0.55 * base_scores[n] + 0.45 * hist_norm.get(n, 0.0)
            for n in all_numbers
        }

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._correlation)
        return result
