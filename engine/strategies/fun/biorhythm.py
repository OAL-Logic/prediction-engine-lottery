"""
Biorhythm Strategy  🌀
=======================
Scores lottery numbers using personal biorhythm cycle theory.

Biorhythm theory holds that human life follows three sinusoidal cycles
starting from the moment of birth:

  Physical     23-day cycle — stamina, strength, reflexes
  Emotional    28-day cycle — mood, creativity, sensitivity
  Intellectual 33-day cycle — memory, learning, alertness

Each cycle oscillates between -1 (low) and +1 (peak). The current
position in each cycle is calculated from the number of days since birth.

  cycle_value = sin(2π × days_since_birth / cycle_length)

Mapping cycles to numbers
--------------------------
Each number's digit-root (Pythagorean reduction) determines which
biorhythm domain it belongs to:

  1, 4, 7  →  Physical domain     (action, structure, completion)
  2, 5, 8  →  Emotional domain    (intuition, freedom, power)
  3, 6, 9  →  Intellectual domain (expression, harmony, wisdom)

A number scores highest when:
  1. Its domain cycle is at a high positive value on the draw date
  2. Its digit-root is at a critical day (cycle crosses zero) → bonus

Critical days
-------------
When a cycle value is near 0 (crossing point), energy is unstable —
some interpretations say luck is heightened. The `critical_bonus`
parameter adds extra score on these days.

Historical blend
----------------
Like moon_phase and weather, if `use_history=True` (default), the
biorhythm score is blended with historical frequency from draws where
the same phase grouping (high/low/critical for each cycle) applied.

Parameters
----------
  birth_date      Your birthday. If None, a universal epoch (2000-01-01)
                  is used, producing a "universal biorhythm" the same
                  for everyone.
  draw_date       The date to score for. Defaults to today + 1.
  use_history     Blend with historical draws that shared similar
                  biorhythm phase states. Default True.
  critical_bonus  Extra score for numbers whose domain is at a cycle
                  crossing point. Default 0.2.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Any

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

# Cycle lengths in days
_CYCLES = {"physical": 23, "emotional": 28, "intellectual": 33}

# Digit-root → domain mapping (Pythagorean tradition)
_DOMAIN_MAP = {
    1: "physical",   4: "physical",   7: "physical",
    2: "emotional",  5: "emotional",  8: "emotional",
    3: "intellectual", 6: "intellectual", 9: "intellectual",
}

_DEFAULT_EPOCH = date(2000, 1, 1)   # "universal biorhythm" when no birth date given


def _digit_reduce(n: int) -> int:
    """Pythagorean digit reduction to 1–9."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n or 9


def _cycle_value(days: int, period: int) -> float:
    """Return sin value for a biorhythm cycle. -1.0 (low) to +1.0 (peak)."""
    return math.sin(2 * math.pi * days / period)


def _phase_bucket(val: float) -> str:
    """Classify a cycle value into 'high', 'low', or 'critical'."""
    if abs(val) < 0.15:
        return "critical"
    return "high" if val > 0 else "low"


@register
class BiorhythmStrategy(BaseStrategy):
    name        = "biorhythm"
    description = "🌀 Personal biorhythm cycles — physical, emotional, intellectual"
    tier        = "fun"
    requires_history = 1

    def __init__(
        self,
        birth_date:      date | str | None = None,
        draw_date:       date | str | None = None,
        use_history:     bool              = True,
        critical_bonus:  float             = 0.2,
    ) -> None:
        """
        Parameters
        ----------
        birth_date
            Personal birthday. If not provided, a universal epoch (2000-01-01) 
            is used, producing a "universal biorhythm".
        draw_date
            Upcoming Draw Date. The date to score for.
        use_history
            Historical data blend. Blend with historical draws that shared similar 
            biorhythm phase states.
        critical_bonus
            Critical day score. Extra score for numbers whose domain is at a cycle 
            crossing point (high instability/luck).
        """
        if isinstance(birth_date, str) and birth_date.strip() and birth_date != "None":
            self.birth_date = date.fromisoformat(birth_date[:10])
        else:
            self.birth_date = birth_date or _DEFAULT_EPOCH
            
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = draw_date or (date.today() + timedelta(days=1))
            
        if isinstance(use_history, str):
            self.use_history = use_history.lower() in ("true", "1", "yes", "y")
        else:
            self.use_history = bool(use_history)
            
        self.critical_bonus = float(critical_bonus)
        self._correlation: dict[str, Any] = {}

    def _cycles_for_date(self, d: date) -> dict[str, float]:
        import pandas as pd
        if pd.isna(d):
            return {name: 0.0 for name in _CYCLES}
        
        days = (d - self.birth_date).days
        return {name: _cycle_value(days, period) for name, period in _CYCLES.items()}

    def _phase_signature(self, cycles: dict[str, float]) -> str:
        """Compact string describing the phase state (for history grouping)."""
        return "|".join(f"{name}:{_phase_bucket(val)}" for name, val in sorted(cycles.items()))

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        target_cycles = self._cycles_for_date(self.draw_date)
        target_sig    = self._phase_signature(target_cycles)

        # --- Base biorhythm score ---
        base_scores: dict[int, float] = {}
        for num in all_numbers:
            root   = _digit_reduce(num)
            domain = _DOMAIN_MAP.get(root, "intellectual")
            val    = target_cycles[domain]
            # Normalise [-1,1] → [0,1]
            score  = (val + 1.0) / 2.0
            # Critical day bonus
            if abs(val) < 0.15:
                score = min(score + self.critical_bonus, 1.0)
            base_scores[num] = score

        if not self.use_history or df.empty:
            self._correlation = {
                "cycles": {k: round(v, 3) for k, v in target_cycles.items()},
                "phase_signature": target_sig,
                "birth_date": self.birth_date.isoformat(),
                "matched_draws": 0,
                "recent_matches": [],
                "top_numbers": [],
            }
            return base_scores

        # --- Historical correlation: find draws with same phase signature ---
        hist_counts: Counter = Counter()
        matched_draws = 0
        matched_rows: list[dict] = []

        for _, row in df.iterrows():
            try:
                raw       = row["date"]
                draw_date = raw.date() if hasattr(raw, "date") else date.fromisoformat(str(raw)[:10])
                cycles    = self._cycles_for_date(draw_date)
                sig       = self._phase_signature(cycles)
                if sig == target_sig:
                    hist_counts.update(row["numbers"])
                    matched_draws += 1
                    matched_rows.append({
                        "date":    draw_date.isoformat(),
                        "numbers": sorted(row["numbers"]),
                        "signature": sig,
                    })
            except Exception:
                continue

        matched_rows.sort(key=lambda r: r["date"], reverse=True)
        top_numbers = [
            {"number": n, "frequency": hist_counts.get(n, 0)}
            for n, _ in hist_counts.most_common(10)
        ]
        self._correlation = {
            "cycles": {k: round(v, 3) for k, v in target_cycles.items()},
            "phase_signature": target_sig,
            "birth_date": self.birth_date.isoformat(),
            "matched_draws": matched_draws,
            "recent_matches": matched_rows[:5],
            "top_numbers": top_numbers,
        }

        if matched_draws == 0:
            return base_scores

        max_h   = max(hist_counts.values()) or 1.0
        hist_norm = {n: hist_counts.get(n, 0) / max_h for n in all_numbers}

        return {
            n: 0.55 * base_scores[n] + 0.45 * hist_norm.get(n, 0.0)
            for n in all_numbers
        }

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._correlation)
        return result
