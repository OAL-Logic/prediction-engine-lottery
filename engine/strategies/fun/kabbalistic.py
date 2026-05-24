"""
Kabbalistic Numerology Strategy ✡️
=================================
Scores lottery numbers using Kabbalistic (Chaldean-style) numerology.

This strategy applies the "Numerology Prediction Engine Framework" based on 
Kabbalistic principles, focusing on the vibration of names and dates.

Core Concepts:
--------------
1.  Vowel vs. Consonant Separation:
    - Motivation (Inner Desire): Sum of vowels in the full name.
    - Impression (External Image): Sum of consonants in the full name.
    - Expression (Talents): Sum of all letters in the full name.

2.  Destiny & Mission:
    - Destiny: Sum of Day + Month + Year of birth.
    - Mission: Expression + Destiny.

3.  Temporal Cycles:
    - Personal Year: Birth Day + Birth Month + Current Year.
    - Personal Month: Personal Year + Current Month.
    - Personal Day: Personal Month + Current Day.

4.  Arcanos & Triangle of Life:
    - Inverted Triangle of Life generated from the name's numerical sequence.
    - Arcanos (1-78) extracted from pairs in the triangle.
    - Dominance Period: Each Arcano dominates ~5.29 years of life.

5.  Karmic Debts & Lessons:
    - Flags 13, 14, 16, 19 before reduction.

Implementation Details:
-----------------------
- Alphabet Map: 1(A,I,Q,J,Y), 2(B,K,R), 3(C,G,L,S), 4(D,M,T), 5(E,H,N,X), 6(U,V,W), 7(O,Z), 8(F,P).
- "Y" Rule: Vowel (1) if no other vowels in syllable, otherwise Consonant (1).
- Reduction: Standard 1-9 reduction, preserving Master Numbers 11 and 22.
"""

from __future__ import annotations

import unicodedata
from collections import Counter
from datetime import date, timedelta
from typing import Any

import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Kabbalistic Letter Values
# 1: A, I, Q, J, Y
# 2: B, K, R
# 3: C, G, L, S
# 4: D, M, T
# 5: E, H, N, X
# 6: U, V, W
# 7: O, Z
# 8: F, P
_LETTER_MAP = {
    'A': 1, 'I': 1, 'Q': 1, 'J': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

_VOWELS = set("AEIOU")

# Master numbers preserved in Kabbalistic system
_MASTER = {11, 22}

# Favorable Arcanos for sudden wealth/success
_FAVORABLE_ARCANOS = {32, 64, 65, 69, 70, 78}
# Warning Arcanos
_WARNING_ARCANOS = {13, 14, 16}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_accents(text: str) -> str:
    """Remove accents from characters (e.g., 'á' -> 'a')."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

def _digit_reduce(n: int, preserve_master: bool = True) -> int:
    """Kabbalistic reduction to 1-9, optionally preserving 11, 22."""
    if preserve_master and n in _MASTER:
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n or 9

def _get_name_values(name: str) -> list[int]:
    """Convert a name into its Kabbalistic numerical sequence."""
    clean_name = _strip_accents(name.upper())
    values = []
    for char in clean_name:
        if char in _LETTER_MAP:
            values.append(_LETTER_MAP[char])
    return values

def _is_vowel_y(index: int, name: str) -> bool:
    """
    Determine if 'Y' at index in name acts as a vowel.
    Kabbalistic rule: Vowel if no other vowels in the syllable.
    Simplified here: Vowel if not adjacent to another vowel.
    """
    if name[index] != 'Y':
        return name[index] in _VOWELS
    
    # Check neighbors
    has_vowel_neighbor = False
    if index > 0 and name[index-1] in _VOWELS:
        has_vowel_neighbor = True
    if index < len(name) - 1 and name[index+1] in _VOWELS:
        has_vowel_neighbor = True
        
    return not has_vowel_neighbor

def _calculate_core_numbers(name: str) -> dict[str, int]:
    """Calculate Motivation, Impression, and Expression."""
    clean_name = _strip_accents(name.upper()).replace(" ", "")
    vowel_sum = 0
    consonant_sum = 0
    
    for i, char in enumerate(clean_name):
        if char not in _LETTER_MAP:
            continue
        val = _LETTER_MAP[char]
        if _is_vowel_y(i, clean_name):
            vowel_sum += val
        else:
            consonant_sum += val
            
    return {
        "motivation": _digit_reduce(vowel_sum),
        "impression": _digit_reduce(consonant_sum),
        "expression": _digit_reduce(vowel_sum + consonant_sum),
    }

def _calculate_triangle_arcanos(name_values: list[int]) -> tuple[list[list[int]], list[int]]:
    """Build the Inverted Triangle of Life and extract Arcanos (1-78)."""
    if not name_values:
        return [], []
        
    triangle = [name_values]
    current_row = name_values
    
    while len(current_row) > 1:
        next_row = []
        for i in range(len(current_row) - 1):
            # Sum adjacent and reduce to single digit (Kabbalistic reduction always reduces in triangle)
            res = _digit_reduce(current_row[i] + current_row[i+1], preserve_master=False)
            next_row.append(res)
        triangle.append(next_row)
        current_row = next_row
        
    # Extract Arcanos (pairs from all rows)
    arcanos = []
    for row in triangle:
        for i in range(len(row) - 1):
            arc = int(f"{row[i]}{row[i+1]}")
            if 1 <= arc <= 78:
                arcanos.append(arc)
                
    return triangle, arcanos

# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------

@register
class KabbalisticStrategy(BaseStrategy):
    name        = "kabbalistic"
    description = "✡️ Kabbalistic Numerology — Arcanos × Triangle of Life × Destiny"
    tier        = "fun"
    requires_history = 1

    def __init__(
        self,
        full_name:       str               = "GEMINI ENGINE",
        birth_date:      date | str | None = "1990-01-01",
        draw_date:       date | str | None = None,
        use_history:     bool              = True,
        topic:           str               = "",
    ) -> None:
        """
        Parameters
        ----------
        full_name
            Full birth name for Kabbalistic calculations.
        birth_date
            Birthday for Destiny and cycle calculations.
        draw_date
            Target draw date.
        use_history
            Blend with historical data matching Kabbalistic vibrations.
        topic
            Optional contextual topic (Universal Gematria).
        """
        self.full_name = full_name
        self.topic = topic
        
        if isinstance(birth_date, str) and birth_date.strip() and birth_date != "None":
            self.birth_date = date.fromisoformat(birth_date[:10])
        else:
            self.birth_date = birth_date or date(1990, 1, 1)

        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = draw_date or date.today()

        if isinstance(use_history, str):
            self.use_history = use_history.lower() in ("true", "1", "yes", "y")
        else:
            self.use_history = bool(use_history)

        # Pre-calculate personal numbers
        self.core = _calculate_core_numbers(self.full_name)
        
        # Destiny: Sum of reduced day + reduced month + reduced year
        d_red = _digit_reduce(self.birth_date.day, preserve_master=False)
        m_red = _digit_reduce(self.birth_date.month, preserve_master=False)
        y_red = _digit_reduce(sum(int(d) for d in str(self.birth_date.year)), preserve_master=False)
        self.destiny = _digit_reduce(d_red + m_red + y_red)
        
        self.mission = _digit_reduce(self.core["expression"] + self.destiny)
        
        # Calculate Arcanos from Triangle
        self.name_values = _get_name_values(self.full_name)
        
        # Topic Gematria Overlay
        if self.topic:
            topic_vals = _get_name_values(self.topic)
            if topic_vals:
                # Merge name and topic values (cycling topic if shorter)
                merged = []
                for i, val in enumerate(self.name_values):
                    t_val = topic_vals[i % len(topic_vals)]
                    merged.append(_digit_reduce(val + t_val, preserve_master=False))
                self.name_values = merged

        self.triangle, self.arcanos = _calculate_triangle_arcanos(self.name_values)
        
        # Determine current Arcano based on age (5.29 year blocks)
        age_days = (self.draw_date - self.birth_date).days
        age_years = age_days / 365.25
        arcano_index = int(age_years / 5.29)
        if self.arcanos and arcano_index < len(self.arcanos):
            self.current_arcano = self.arcanos[arcano_index]
        else:
            self.current_arcano = self.arcanos[-1] if self.arcanos else None

        # Calculate Challenges (subtractions of birth date components)
        d, m, y = self.birth_date.day, self.birth_date.month, self.birth_date.year
        self.challenges = {
            _digit_reduce(abs(m - d), preserve_master=False),
            _digit_reduce(abs(d - _digit_reduce(y, preserve_master=False)), preserve_master=False)
        }

        # Detect Negative Sequences in name values (≥3 identical adjacent digits)
        self.negative_sequences = set()
        count = 1
        for i in range(1, len(self.name_values)):
            if self.name_values[i] == self.name_values[i-1]:
                count += 1
            else:
                if count >= 3:
                    self.negative_sequences.add(self.name_values[i-1])
                count = 1
        if count >= 3:
            self.negative_sequences.add(self.name_values[-1])

        # Detect Karmic Lessons (missing numbers 1-9 from name values)
        # Note: 9 is usually not a lesson in most systems, but we check 1-8
        present_values = set(self.name_values)
        self.karmic_lessons = {i for i in range(1, 9) if i not in present_values}

        # Detect Karmic Debts in core sums (before reduction)
        # We need to re-calculate them slightly differently to catch the 13, 14, 16, 19
        self.karmic_debts = set()
        
        def _check_debt(n: int):
            if n in (13, 14, 16, 19):
                self.karmic_debts.add(n)
            # Also check intermediate reductions
            while n > 9:
                n = sum(int(d) for d in str(n))
                if n in (13, 14, 16, 19):
                    self.karmic_debts.add(n)

        # Check birth day and month
        _check_debt(self.birth_date.day)
        _check_debt(self.birth_date.month)
        # Check birth year (sum of digits first, e.g. 1990 -> 19)
        _check_debt(sum(int(d) for d in str(self.birth_date.year)))
        
        # Check core totals (vowels, consonants, full)
        clean_name = _strip_accents(self.full_name.upper()).replace(" ", "")
        v_sum = sum(_LETTER_MAP[c] for i, c in enumerate(clean_name) if c in _LETTER_MAP and _is_vowel_y(i, clean_name))
        c_sum = sum(_LETTER_MAP[c] for i, c in enumerate(clean_name) if c in _LETTER_MAP and not _is_vowel_y(i, clean_name))
        _check_debt(v_sum)
        _check_debt(c_sum)
        _check_debt(v_sum + c_sum)
        # Check destiny
        _check_debt(d_red + m_red + sum(int(d) for d in str(self.birth_date.year)))

    def _get_vibrations(self, d: date) -> dict[str, int]:
        """Calculate temporal vibrations for a specific date."""
        # Personal Year: Day + Month + Current Year
        py = _digit_reduce(self.birth_date.day + self.birth_date.month + d.year)
        # Personal Month: Personal Year + Month
        pm = _digit_reduce(py + d.month)
        # Personal Day: Personal Month + Day
        pd = _digit_reduce(pm + d.day)
        
        return {"year": py, "month": pm, "day": pd}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        vib = self._get_vibrations(self.draw_date)
        
        # Determine Harmonic Parity (Even/Odd preference)
        destiny_root = _digit_reduce(self.destiny, preserve_master=False)
        prefer_even = (destiny_root % 2 == 0)

        # Calculate base scores for each number
        scores: dict[int, float] = {}
        
        # 1. Multipliers from Arcanos & Personal Day
        multiplier = 1.0
        if self.current_arcano in _FAVORABLE_ARCANOS:
            multiplier *= 1.25
        elif self.current_arcano in _WARNING_ARCANOS:
            multiplier *= 0.75
            
        if vib["day"] in (1, 8):  # Pioneer or Achiever days
            multiplier *= 1.15
        elif vib["year"] == 9:    # Year of endings (wait)
            multiplier *= 0.85

        # Favorable day boost (Repeating monthly based on Birth Day)
        if self.draw_date.day == self.birth_date.day:
            multiplier *= 1.1

        for num in all_numbers:
            root = _digit_reduce(num)
            
            # Match against core numbers
            is_harmonic = (num % 2 == 0) == prefer_even
            
            # Match core values (Motivation, Impression, Expression, Destiny, Mission)
            core_vals = set(self.core.values()) | {self.destiny, self.mission}
            match_core = root in core_vals
            
            # Success Trigger: Personal Day/Month/Year matches core numbers
            is_success_period = (vib["day"] in core_vals or vib["month"] in core_vals)
            
            # Challenge penalty
            is_challenge = root in self.challenges or vib["day"] in self.challenges
            
            # Negative sequence penalty
            is_negative_seq = root in self.negative_sequences
            
            # Karmic Lesson penalty (missing numbers from name)
            is_karmic_lesson = root in self.karmic_lessons
            
            # Karmic Debt penalty (if root matches a reduced debt)
            is_karmic_debt = any(_digit_reduce(d) == root for d in self.karmic_debts)

            # Score formula
            s = 0.35  # base
            if is_harmonic: s += 0.1
            if match_core:  s += 0.2
            if vib["day"] == root: s += 0.25
            if is_success_period: s += 0.1
            
            # Penalties
            if is_challenge: s -= 0.15
            if is_negative_seq: s -= 0.1
            if is_karmic_lesson: s -= 0.1
            if is_karmic_debt: s -= 0.1
            
            # Special case for "Lucky 21"
            if num == 21: s += 0.1
            
            scores[num] = max(min(s * multiplier, 1.0), 0.0)

        # 2. Historical Blend
        if self.use_history and not df.empty:
            hist_counts: Counter = Counter()
            matched_draws = 0
            
            for _, row in df.iterrows():
                try:
                    raw = row["date"]
                    draw_date = raw.date() if hasattr(raw, "date") else date.fromisoformat(str(raw)[:10])
                    v = self._get_vibrations(draw_date)
                    if v["day"] == vib["day"]:
                        hist_counts.update(row["numbers"])
                        matched_draws += 1
                except Exception:
                    continue
            
            if matched_draws > 0:
                max_count = max(hist_counts.values())
                for num in all_numbers:
                    hist_score = hist_counts.get(num, 0) / max_count
                    # Blend: 60% numerology, 40% historical matching vibrations
                    scores[num] = (scores[num] * 0.6) + (hist_score * 0.4)

        return scores

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        # Extract necessary arguments from args/kwargs or defaults
        import inspect
        base_sig = inspect.signature(BaseStrategy.suggest)
        bound = base_sig.bind_partial(self, *args, **kwargs)
        bound.apply_defaults()
        
        # Generate Intentional Seed (Synchronicity Matrix)
        # Unique deterministic hash based on name + topic + birth date + current arcano
        import hashlib
        seed_str = f"{self.full_name}{self.topic}{self.birth_date}{self.current_arcano}"
        intent_seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (2**32)

        # Pass seed to super().suggest if not already provided
        if 'seed' not in bound.arguments or bound.arguments['seed'] is None:
            kwargs['seed'] = intent_seed

        result = super().suggest(*args, **kwargs)

        # Inject "Success Trigger" metadata for the Orchestrator
        alerts = []
        if self.current_arcano == 78:
            alerts.append("Arcano 78 (Sudden Windfall) is active! High-reward cycle.")
        elif self.current_arcano in _FAVORABLE_ARCANOS:
            alerts.append(f"Favorable Arcano {self.current_arcano} active. Positive energy period.")
        elif self.current_arcano in _WARNING_ARCANOS:
            alerts.append(f"Warning Arcano {self.current_arcano} active. Exercise caution.")
            
        vib = self._get_vibrations(self.draw_date)
        if vib["year"] == 9:
            alerts.append("Personal Year 9 (Endings). Not recommended for major investments.")
            
        if self.draw_date.day == self.birth_date.day:
            alerts.append("Favorable Day (Birth Day Match)! Enhanced potential.")

        if alerts:
            result.metadata["kabbalistic_alerts"] = alerts
        
        result.metadata["kabbalistic_profile"] = {
            "motivation": self.core["motivation"],
            "impression": self.core["impression"],
            "expression": self.core["expression"],
            "destiny": self.destiny,
            "mission": self.mission
        }
        result.metadata["kabbalistic_triangle"] = self.triangle
        result.metadata["negative_sequences"] = list(self.negative_sequences)
        result.metadata["karmic_lessons"] = list(self.karmic_lessons)
        result.metadata["karmic_debts"] = list(self.karmic_debts)
        result.metadata["arcanos"] = self.arcanos
        result.metadata["current_arcano"] = self.current_arcano
            
        return result
