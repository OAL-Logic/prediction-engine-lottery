"""
Numerology Strategy  🔮
========================
Scores lottery numbers using classical Pythagorean numerology.

Three vibration layers (all optional, all combinable)
------------------------------------------------------
1. Universal Day   — the draw date reduced to its life-path number.
                     Applies to everyone on that day. Always active.

2. Personal Life Path — your permanent number, derived from your birthday.
                     Reflects who you are across time, not just the day.
                     Enabled when ``birth_date`` is provided.

3. Personal Day    — digit_reduce(Life Path + draw_month + draw_day).
                     Represents YOUR unique energy on THIS specific draw date.
                     Enabled when both ``birth_date`` and ``use_personal_day=True``.

Scoring per number
------------------
For each active vibration layer, the number's essence (digit-reduced value)
is compared:
  - Exact match     → +1.0 contribution from that layer
  - Compatible      → +0.5 contribution from that layer  (see table below)
  - No match        → +0.0 contribution from that layer
  - Master number   → +0.15 flat bonus on top (11, 22, 33 are inherently powerful)

Final base score = total_contributions / max_possible  →  [0.0, 1.0]

Compatibility table (Pythagorean tradition)
-------------------------------------------
  Life Path 1  → compatible with 1, 5, 7
  Life Path 2  → compatible with 2, 4, 8
  Life Path 3  → compatible with 3, 6, 9
  Life Path 4  → compatible with 2, 4, 8
  Life Path 5  → compatible with 1, 5, 7
  Life Path 6  → compatible with 3, 6, 9
  Life Path 7  → compatible with 1, 5, 7
  Life Path 8  → compatible with 2, 4, 8
  Life Path 9  → compatible with 3, 6, 9

Historical correlation mode
----------------------------
If ``use_history=True`` (default), we also look at which numbers appeared
most frequently on draws whose Universal Day life-path matched today's.
This blends the pure numerology score with a data-driven signal.

  - 1 active layer (Universal only)  →  40% numerology + 60% historical
  - 2+ active layers                 →  60% numerology + 40% historical
    (more personal context = trust the numerology model more)

Usage examples
--------------
  # Universal Day only (original behaviour)
  strategy = NumerologyStrategy()

  # Add Life Path layer from birthday
  strategy = NumerologyStrategy(birth_date=date(1990, 6, 15))

  # All three layers
  strategy = NumerologyStrategy(birth_date=date(1990, 6, 15), use_personal_day=True)

  # Just score, no historical blend
  strategy = NumerologyStrategy(birth_date=date(1990, 6, 15), use_history=False)
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Pythagorean compatibility groups (keyed by root 1–9)
_COMPAT: dict[int, set[int]] = {
    1: {1, 5, 7},
    2: {2, 4, 8},
    3: {3, 6, 9},
    4: {2, 4, 8},
    5: {1, 5, 7},
    6: {3, 6, 9},
    7: {1, 5, 7},
    8: {2, 4, 8},
    9: {3, 6, 9},
}

# Master numbers — never reduced further; always receive a score bonus
_MASTER: frozenset[int] = frozenset({11, 22, 33})

_MASTER_BONUS: float = 0.15


# ---------------------------------------------------------------------------
# Core numerology helpers
# ---------------------------------------------------------------------------


def _digit_reduce(n: int) -> int:
    """
    Pythagorean reduction to a single digit (1–9).

    Master numbers (11, 22, 33) are preserved and never reduced further.
    Returns 9 instead of 0 (9 = completion in Pythagorean numerology).
    """
    if n in _MASTER:
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n or 9


def _life_path(d: date) -> int:
    """Reduce a full date to its numerological life-path number."""
    return _digit_reduce(d.year + d.month + d.day)


def _personal_day(birth_date: date, draw_date: date) -> int:
    """
    Personal Day number for a specific draw date.

    Formula: digit_reduce(Life Path + draw_month + draw_day)

    This represents the user's unique energetic vibration on a given day —
    distinct from the Universal Day (which is the same for everyone).
    """
    user_lp = _life_path(birth_date)
    return _digit_reduce(user_lp + draw_date.month + draw_date.day)


def _compat_root(vibration: int) -> int:
    """Normalize a vibration (including master numbers) to its root for compat lookup."""
    if vibration in _MASTER:
        return vibration % 9 or 9  # 11→2, 22→4, 33→6
    return vibration


def _compat_set(vibration: int) -> set[int]:
    """Return the Pythagorean compatibility set for a vibration."""
    return _COMPAT.get(_compat_root(vibration), set())


def _number_score(essence: int, vibrations: list[int]) -> float:
    """
    Score a number's essence against all active vibration layers.

    Each vibration independently contributes to the score:
      +1.0  exact match   (essence == vibration, or their roots match)
      +0.5  compat match  (essence is in the vibration's compatibility set)
      +0.0  no match

    Returns a value in [0.0, 1.0] — total / max_possible.
    """
    if not vibrations:
        return 0.5  # no active layers → neutral

    total = 0.0
    for vib in vibrations:
        vib_root = _compat_root(vib)
        ess_root = _compat_root(essence) if essence in _MASTER else essence
        if ess_root == vib_root or essence == vib:
            total += 1.0
        elif essence in _compat_set(vib):
            total += 0.5

    return min(total / float(len(vibrations)), 1.0)


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@register
class NumerologyStrategy(BaseStrategy):
    name        = "numerology"
    description = "🔮 Pythagorean numerology — Universal Day × Life Path × Personal Day"
    tier        = "fun"
    requires_history = 1

    def __init__(
        self,
        use_history:      bool              = True,
        target_date:      date | str | None = None,
        birth_date:       date | str | None = None,
        use_personal_day: bool              = True,
    ) -> None:
        """
        Parameters
        ----------
        use_history
            Historical data blend. If True, numbers that appeared on matching 
            historical dates get a boost. Keeps the mysticism grounded in data.
        target_date
            Draw date. The day the lottery occurs. Used to calculate the "Universal Day" 
            energy that affects everyone playing on that date.
        birth_date
            Personal birthday. Unlocks your unique "Life Path" number, making 
            the prediction specific to your own numerical essence.
        use_personal_day
            Personal vibration. If True, computes your unique energy specifically 
            for the draw date. Highly recommended for the most personalized result.
        """
        if isinstance(use_history, str):
            self.use_history = use_history.lower() in ("true", "1", "yes", "y")
        else:
            self.use_history = bool(use_history)
            
        if isinstance(target_date, str) and target_date.strip() and target_date != "None":
            self.target_date = date.fromisoformat(target_date[:10])
        else:
            self.target_date = target_date or date.today()
            
        if isinstance(birth_date, str) and birth_date.strip() and birth_date != "None":
            self.birth_date = date.fromisoformat(birth_date[:10])
        else:
            self.birth_date = birth_date
            
        if isinstance(use_personal_day, str):
            use_personal_day = use_personal_day.lower() in ("true", "1", "yes", "y")
        else:
            use_personal_day = bool(use_personal_day)
            
        # Personal Day only makes sense when we have a birth date
        self.use_personal_day = use_personal_day and self.birth_date is not None

    # ------------------------------------------------------------------
    # Vibration helpers
    # ------------------------------------------------------------------

    def _active_vibrations(self) -> list[int]:
        """
        Build the ordered list of active vibration numbers.

        Always:     [universal_day]
        + birthday: [universal_day, user_life_path]
        + pers.day: [universal_day, user_life_path, personal_day]
        """
        vibs = [_life_path(self.target_date)]  # Universal Day — always first

        if self.birth_date is not None:
            vibs.append(_life_path(self.birth_date))  # Personal Life Path

        if self.use_personal_day and self.birth_date is not None:
            vibs.append(_personal_day(self.birth_date, self.target_date))  # Personal Day

        return vibs

    def _layer_labels(self) -> list[str]:
        """Human-readable names for each active vibration layer."""
        labels = ["universal_day"]
        if self.birth_date is not None:
            labels.append("life_path")
        if self.use_personal_day:
            labels.append("personal_day")
        return labels

    # ------------------------------------------------------------------
    # score()
    # ------------------------------------------------------------------

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi      = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        vibrations  = self._active_vibrations()
        universal   = vibrations[0]  # always the draw-date life path

        # --- Base numerology score -------------------------------------------
        base_scores: dict[int, float] = {}
        for num in all_numbers:
            essence  = _digit_reduce(num)
            master_b = _MASTER_BONUS if num in _MASTER else 0.0
            base_scores[num] = min(_number_score(essence, vibrations) + master_b, 1.0)

        if not self.use_history or df.empty:
            return base_scores

        # --- Historical correlation -------------------------------------------
        # Count number appearances on draws whose Universal Day matches today's.
        hist_scores: dict[int, float] = {n: 0.0 for n in all_numbers}
        matched_draws = 0

        for _, row in df.iterrows():
            try:
                raw       = row["date"]
                draw_date = raw.date() if hasattr(raw, "date") else date.fromisoformat(str(raw)[:10])
                if _life_path(draw_date) == universal:
                    for num in row["numbers"]:
                        if num in hist_scores:
                            hist_scores[num] += 1.0
                    matched_draws += 1
            except Exception:
                continue

        if matched_draws == 0:
            return base_scores

        max_h     = max(hist_scores.values()) or 1.0
        hist_norm = {n: v / max_h for n, v in hist_scores.items()}

        # When more personal layers are active we trust numerology more
        # and rely on history less — the model is more specifically tuned.
        if len(vibrations) == 1:
            num_weight, hist_weight = 0.40, 0.60   # Universal only
        else:
            num_weight, hist_weight = 0.60, 0.40   # Personalized layers present

        return {
            n: num_weight * base_scores[n] + hist_weight * hist_norm.get(n, 0.0)
            for n in all_numbers
        }

    # ------------------------------------------------------------------
    # suggest() — override only to inject rich metadata
    # ------------------------------------------------------------------

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)

        vibrations = self._active_vibrations()
        labels     = self._layer_labels()

        result.metadata.update({
            "target_date":   self.target_date.isoformat(),
            "birth_date":    self.birth_date.isoformat() if self.birth_date else None,
            "active_layers": labels,
            "vibrations":    dict(zip(labels, vibrations)),
            "use_history":   self.use_history,
        })
        return result
