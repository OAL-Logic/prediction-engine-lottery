"""
Trevo da Sorte Strategy 🍀
==========================
Implements the "Trevo da Sorte — Loterias & Numerologia" (Márcia Sensitiva)
framework combined with Pythagorean/Kabbalistic harmonics and historical
draw resonance, supporting both single-draw and Teimosinha (multi-draw week)
horizons.

Core Rules (Márcia Sensitiva Master Table)
------------------------------------------
1. Lucky Number (`numero_da_sorte`):
   Digit reduction (1–9) of the birth day (1–31):
     e.g., day 16 -> 1 + 6 = 7 -> Lucky Number = 7

2. Master Table (`TREVO_MASTER_TABLE`):
   - 1: Days [1, 10, 19, 28], Months [1, 10], Weekday: Sunday (Domingo)
   - 2: Days [2, 11, 21, 29], Months [2, 11], Weekday: Monday (Segunda)
   - 3: Days [3, 12, 21, 30], Months [3, 12], Weekday: Tuesday (Terça)
   - 4: Days [4, 13, 22, 31], Months [4, 1],  Weekday: Wednesday (Quarta)
   - 5: Days [5, 14, 23],     Months [5, 2],  Weekday: Thursday (Quinta)
   - 6: Days [6, 15, 24],     Months [6, 3],  Weekday: Friday (Sexta)
   - 7: Days [7, 16, 25],     Months [7, 4],  Weekday: Saturday (Sábado)
   - 8: Days [8, 17, 26],     Months [8],     Weekday: Sunday (Domingo)
   - 9: Days [9, 18, 27],     Months [9, 6],  Weekday: Monday (Segunda)

3. Harmonized Ticket Generation & Teimosinha Horizon:
   - Incorporates the personal lucky number, correlated lucky days of the month,
     birthdate components (day, month, century, year digits, life path),
     digit-root resonant numbers, and multiples of the lucky number.
   - Evaluates Teimosinha weekly draw schedules to boost numbers that resonate
     across all consecutive draws of the week (especially on the user's
     Sacred Weekday and Lucky Days).
   - Blends numerological vibration with empirical historical draw frequencies
     on matching weekdays/vibrations and enforces harmonic odd/even and
     quadrant/decade distribution.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register


# ---------------------------------------------------------------------------
# Márcia Sensitiva Master Table
# ---------------------------------------------------------------------------

TREVO_MASTER_TABLE: dict[int, dict[str, Any]] = {
    1: {
        "lucky_days": [1, 10, 19, 28],
        "table_days": [10, 19, 28],
        "lucky_months": [1, 10],
        "js_weekday": 0,
        "py_weekday": 6,  # Sunday
        "weekday_pt": "Domingo",
        "weekday_en": "Sunday",
    },
    2: {
        "lucky_days": [2, 11, 20, 21, 29],
        "table_days": [2, 11, 21, 29],
        "lucky_months": [2, 11],
        "js_weekday": 1,
        "py_weekday": 0,  # Monday
        "weekday_pt": "Segunda-feira",
        "weekday_en": "Monday",
    },
    3: {
        "lucky_days": [3, 12, 21, 30],
        "table_days": [3, 12, 21, 30],
        "lucky_months": [3, 12],
        "js_weekday": 2,
        "py_weekday": 1,  # Tuesday
        "weekday_pt": "Terça-feira",
        "weekday_en": "Tuesday",
    },
    4: {
        "lucky_days": [4, 13, 22, 31],
        "table_days": [4, 13, 22, 31],
        "lucky_months": [4, 1],
        "js_weekday": 3,
        "py_weekday": 2,  # Wednesday
        "weekday_pt": "Quarta-feira",
        "weekday_en": "Wednesday",
    },
    5: {
        "lucky_days": [5, 14, 23],
        "table_days": [5, 14, 23],
        "lucky_months": [5, 2],
        "js_weekday": 4,
        "py_weekday": 3,  # Thursday
        "weekday_pt": "Quinta-feira",
        "weekday_en": "Thursday",
    },
    6: {
        "lucky_days": [6, 15, 24],
        "table_days": [6, 15, 24],
        "lucky_months": [6, 3],
        "js_weekday": 5,
        "py_weekday": 4,  # Friday
        "weekday_pt": "Sexta-feira",
        "weekday_en": "Friday",
    },
    7: {
        "lucky_days": [7, 16, 25],
        "table_days": [7, 16, 25],
        "lucky_months": [7, 4],
        "js_weekday": 6,
        "py_weekday": 5,  # Saturday
        "weekday_pt": "Sábado",
        "weekday_en": "Saturday",
    },
    8: {
        "lucky_days": [8, 17, 26],
        "table_days": [8, 17, 26],
        "lucky_months": [8],
        "js_weekday": 0,
        "py_weekday": 6,  # Sunday
        "weekday_pt": "Domingo",
        "weekday_en": "Sunday",
    },
    9: {
        "lucky_days": [9, 18, 27],
        "table_days": [9, 18, 27],
        "lucky_months": [9, 6],
        "js_weekday": 1,
        "py_weekday": 0,  # Monday
        "weekday_pt": "Segunda-feira",
        "weekday_en": "Monday",
    },
}

_PYTHAGOREAN_COMPAT: dict[int, set[int]] = {
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


def get_lucky_number(day: int | str | date) -> int:
    """Reduce a birth day (1-31) or ISO birth date string to its single-digit lucky number (1-9)."""
    if isinstance(day, date):
        d_int = day.day
    elif isinstance(day, str):
        s_clean = day.strip()
        if "-" in s_clean:
            d_int = date.fromisoformat(s_clean[:10]).day
        else:
            d_int = int(s_clean)
    else:
        d_int = int(day)
    s = (d_int // 10) + (d_int % 10)
    while s > 9:
        s = (s // 10) + (s % 10)
    return s or 9


def digit_reduce(n: int) -> int:
    """Reduce any positive integer to a single digit 1-9."""
    while n > 9:
        n = sum(int(d) for d in str(abs(n)))
    return n or 9


def compute_trevo_profile(
    birth_date: date | str | None = None,
    target_date: date | str | None = None,
    pool_max: int = 60,
    teimosinha_days: int = 7,
    *,
    birth_date_str: str | None = None,
    target_date_str: str | None = None,
    max_num: int | None = None,
    teimosinha_draws: int | None = None,
    game_name: str | None = None,
) -> dict[str, Any]:
    """
    Compute the complete Trevo da Sorte + Pythagorean profile for a birth date
    and target play date / Teimosinha week. Defaults to synthetic placeholder
    date(1990, 1, 1) when no birth_date is supplied (never hardcode real PII).
    """
    eff_birth = birth_date_str or birth_date or date(1990, 1, 1)
    if isinstance(eff_birth, str):
        birth_date_obj = date.fromisoformat(eff_birth.strip()[:10])
    else:
        birth_date_obj = eff_birth

    eff_target = target_date_str or target_date or date.today()
    if isinstance(eff_target, str):
        target_date_obj = date.fromisoformat(eff_target.strip()[:10])
    else:
        target_date_obj = eff_target

    if max_num is not None:
        pool_max = int(max_num)
    if teimosinha_draws is not None:
        teimosinha_days = max(7, int(teimosinha_draws))

    birth_date = birth_date_obj
    target_date = target_date_obj
    lucky_num = get_lucky_number(birth_date.day)
    master = TREVO_MASTER_TABLE[lucky_num]

    # Birthdate numerological components
    day_val = birth_date.day
    month_val = birth_date.month
    year_val = birth_date.year
    century_val = year_val // 100
    year_tail = year_val % 100
    year_digit_sum = sum(int(d) for d in str(year_val))
    year_tail_sum = sum(int(d) for d in f"{year_tail:02d}")
    full_digit_sum = sum(int(d) for d in birth_date.strftime("%Y%m%d"))
    reduced_sum = digit_reduce(day_val) + digit_reduce(month_val) + digit_reduce(year_digit_sum)
    life_path = digit_reduce(reduced_sum)

    # Temporal vibrations on target_date
    personal_year_raw = digit_reduce(day_val) + digit_reduce(month_val) + digit_reduce(target_date.year)
    personal_year = digit_reduce(personal_year_raw)
    personal_month_raw = personal_year + digit_reduce(target_date.month)
    personal_month = digit_reduce(personal_month_raw)
    personal_day = digit_reduce(personal_month + digit_reduce(target_date.day))
    universal_day = digit_reduce(target_date.year + target_date.month + target_date.day)

    # Core anchor numbers inside [1, pool_max]
    core_anchors: set[int] = set()
    for candidate in (
        lucky_num,
        *master["lucky_days"],
        day_val,
        month_val,
        century_val,
        year_digit_sum,
        year_tail_sum,
        full_digit_sum,
        reduced_sum,
        life_path,
        personal_year_raw,
        personal_month_raw,
    ):
        if 1 <= candidate <= pool_max:
            core_anchors.add(int(candidate))

    # Handle year_tail (e.g. 89): direct in Lotomania, modular wrap or complement in 60/80 pools
    if 1 <= year_tail <= pool_max:
        core_anchors.add(year_tail)
    elif year_tail > pool_max:
        wrapped = ((year_tail - 1) % pool_max) + 1
        core_anchors.add(wrapped)

    # Resonant root numbers (numbers whose digit root == lucky_num)
    root_resonants = [n for n in range(1, pool_max + 1) if digit_reduce(n) == lucky_num]

    # Multiples of lucky_num
    multiples = [n for n in range(1, pool_max + 1) if n % lucky_num == 0]

    # Life-path resonant numbers
    life_path_resonants = [n for n in range(1, pool_max + 1) if digit_reduce(n) == life_path]

    # Teimosinha week analysis (target_date through target_date + teimosinha_days - 1)
    week_dates: list[dict[str, Any]] = []
    confluences: list[str] = []
    week_resonant_days: set[int] = set()

    for offset in range(teimosinha_days):
        d = target_date + timedelta(days=offset)
        is_lucky_day = d.day in master["lucky_days"]
        is_lucky_month = d.month in master["lucky_months"]
        is_lucky_weekday = d.weekday() == master["py_weekday"]
        p_day = digit_reduce(personal_month + digit_reduce(d.day))
        u_day = digit_reduce(d.year + d.month + d.day)

        score_day = 0
        reasons = []
        if is_lucky_weekday:
            score_day += 3
            reasons.append(f"Dia da Semana Sagrado ({master['weekday_pt']})")
        if is_lucky_day:
            score_day += 3
            reasons.append(f"Dia da Sorte do Mês ({d.day})")
        if is_lucky_month:
            score_day += 2
            reasons.append(f"Mês da Sorte ({d.month})")
        if personal_month == lucky_num:
            score_day += 2
            reasons.append(f"Mês Pessoal {personal_month} = Número da Sorte {lucky_num}")
        if p_day in (lucky_num, life_path):
            score_day += 1
            reasons.append(f"Dia Pessoal {p_day}")

        if 1 <= d.day <= pool_max and (is_lucky_weekday or is_lucky_day or p_day in (lucky_num, life_path)):
            week_resonant_days.add(d.day)

        if reasons:
            confluences.append(f"{d.isoformat()}: {', '.join(reasons)}")

        week_dates.append({
            "date": d.isoformat(),
            "weekday_Index": d.weekday(),
            "is_lucky_weekday": is_lucky_weekday,
            "is_sacred_weekday": is_lucky_weekday,
            "is_lucky_day": is_lucky_day,
            "is_lucky_month": is_lucky_month,
            "personal_day": p_day,
            "universal_day": u_day,
            "confluence_score": score_day,
            "reasons": reasons,
        })

    harmonic_pool = sorted(
        set(core_anchors)
        | set(root_resonants)
        | set(multiples)
        | set(life_path_resonants)
        | set(week_resonant_days)
    )

    return {
        "birth_date": birth_date.isoformat(),
        "target_date": target_date.isoformat(),
        "lucky_number": lucky_num,
        "lucky_days": master["table_days"],
        "lucky_months": master["lucky_months"],
        "lucky_weekday_pt": master["weekday_pt"],
        "sacred_weekday_pt": master["weekday_pt"],
        "lucky_weekday_en": master["weekday_en"],
        "py_weekday": master["py_weekday"],
        "sacred_py_weekday": master["py_weekday"],
        "life_path": life_path,
        "life_path_unreduced": reduced_sum,
        "full_digit_sum": full_digit_sum,
        "year_digit_sum": year_digit_sum,
        "year_tail": year_tail,
        "personal_year": personal_year,
        "personal_month": personal_month,
        "personal_month_raw": personal_month_raw,
        "personal_day": personal_day,
        "universal_day": universal_day,
        "core_anchors": sorted(core_anchors),
        "harmonic_pool": harmonic_pool,
        "root_resonants": root_resonants,
        "multiples": multiples,
        "life_path_resonants": life_path_resonants,
        "week_resonant_days": sorted(week_resonant_days),
        "week_schedule": week_dates,
        "teimosinha_schedule": week_dates,
        "confluences": confluences,
    }


@register
class TrevoSorteStrategy(BaseStrategy):
    name = "trevo_sorte"
    description = "🍀 Trevo da Sorte (Márcia Sensitiva) — Lucky Day/Month/Weekday × Teimosinha Harmony"
    tier = "fun"
    requires_history = 1

    def __init__(
        self,
        birth_date: date | str | None = "1990-01-01",
        target_date: date | str | None = None,
        draw_date: date | str | None = None,
        use_history: bool = True,
        teimosinha_days: int = 7,
    ) -> None:
        if isinstance(birth_date, str) and birth_date.strip() and birth_date != "None":
            self.birth_date = date.fromisoformat(birth_date[:10])
        elif isinstance(birth_date, date):
            self.birth_date = birth_date
        else:
            self.birth_date = date(1990, 1, 1)

        eff_target = target_date or draw_date
        if isinstance(eff_target, str) and eff_target.strip() and eff_target != "None":
            self.target_date = date.fromisoformat(eff_target[:10])
        elif isinstance(eff_target, date):
            self.target_date = eff_target
        else:
            self.target_date = date.today()

        if isinstance(use_history, str):
            self.use_history = use_history.lower() in ("true", "1", "yes", "y")
        else:
            self.use_history = bool(use_history)

        self.teimosinha_days = int(teimosinha_days)
        self._last_profile: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        profile = compute_trevo_profile(
            birth_date=self.birth_date,
            target_date=self.target_date,
            pool_max=hi,
            teimosinha_days=self.teimosinha_days,
        )
        self._last_profile = profile

        lucky_num = profile["lucky_number"]
        lucky_days_set = set(profile["lucky_days"]) | {lucky_num}
        core_anchors_set = set(profile["core_anchors"])
        root_set = set(profile["root_resonants"])
        mult_set = set(profile["multiples"])
        lp_set = set(profile["life_path_resonants"])
        week_days_set = set(profile["week_resonant_days"])
        compat_roots = _PYTHAGOREAN_COMPAT.get(lucky_num, {lucky_num})

        # 1. Numerological Trevo Score [0, 1]
        trevo_scores: dict[int, float] = {}
        for n in all_numbers:
            s = 0.15  # baseline
            root_n = digit_reduce(n)

            # Mandatory / primary lucky day & personal number
            if n == lucky_num:
                s += 0.45
            elif n in lucky_days_set:
                s += 0.38

            # Core birthdate & cycle anchors (19, 27, 17, 23, 41, 16, 29, etc.)
            if n in core_anchors_set:
                s += 0.25

            # Digit-root resonance with lucky_number (e.g., 7, 16, 25, 34, 43, 52, 61, 70, 79)
            if n in root_set:
                s += 0.22
            elif root_n in compat_roots:
                s += 0.10

            # Multiples of lucky_number (e.g., 7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77)
            if n in mult_set:
                s += 0.18

            # Life path resonance (root == 5)
            if n in lp_set:
                s += 0.12

            # Teimosinha week confluence days (e.g., 24 Saturday, 25 Lucky Day, 20, 22)
            if n in week_days_set:
                s += 0.14

            trevo_scores[n] = min(1.0, s)

        if not self.use_history or df.empty:
            return trevo_scores

        # 2. Empirical Historical Resonance
        # Boost numbers that historically hit on the user's Sacred Weekday, Lucky Months,
        # orLucky Day-of-Month roots, plus overall recent momentum & overdue catch-up.
        sacred_weekday = profile["py_weekday"]
        lucky_months = set(profile["lucky_months"])

        aligned_counts: Counter = Counter()
        overall_counts: Counter = Counter()
        recent_counts: Counter = Counter()

        recent_df = df.tail(min(100, len(df)))
        for nums in recent_df["numbers"]:
            recent_counts.update(nums)

        for _, row in df.iterrows():
            nums = row["numbers"]
            overall_counts.update(nums)
            try:
                raw_d = row["date"]
                d_obj = raw_d.date() if hasattr(raw_d, "date") else date.fromisoformat(str(raw_d)[:10])
                w = 0.0
                if d_obj.weekday() == sacred_weekday:
                    w += 1.5
                if d_obj.month in lucky_months:
                    w += 1.2
                if digit_reduce(d_obj.day) == lucky_num:
                    w += 1.3
                if w > 0:
                    for num in nums:
                        aligned_counts[num] += w
            except Exception:
                continue

        max_aligned = max(aligned_counts.values()) if aligned_counts else 1.0
        max_overall = max(overall_counts.values()) if overall_counts else 1.0
        max_recent = max(recent_counts.values()) if recent_counts else 1.0

        blended: dict[int, float] = {}
        for n in all_numbers:
            h_aligned = aligned_counts.get(n, 0.0) / (max_aligned or 1.0)
            h_overall = overall_counts.get(n, 0.0) / (max_overall or 1.0)
            h_recent = recent_counts.get(n, 0.0) / (max_recent or 1.0)
            hist_blend = 0.50 * h_aligned + 0.30 * h_recent + 0.20 * h_overall
            blended[n] = round(0.62 * trevo_scores[n] + 0.38 * hist_blend, 6)

        return blended

    def suggest(
        self,
        df: pd.DataFrame,
        rules: DrawRules,
        count: int = 1,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> SuggestionResult:
        # Ensure at least the primary lucky number or one of the lucky days is anchored
        # when no explicit key is provided, matching the Trevo da Sorte specification:
        # "incorporando obrigatoriamente o número pessoal, dias associados e números ressonantes"
        result = super().suggest(
            df=df,
            rules=rules,
            count=count,
            temperature=temperature,
            **kwargs,
        )
        if self._last_profile:
            result.metadata["trevo_profile"] = {
                "lucky_number": self._last_profile["lucky_number"],
                "lucky_days": self._last_profile["lucky_days"],
                "lucky_months": self._last_profile["lucky_months"],
                "sacred_weekday": self._last_profile["lucky_weekday_pt"],
                "life_path": self._last_profile["life_path"],
                "personal_year": self._last_profile["personal_year"],
                "personal_month": self._last_profile["personal_month"],
                "core_anchors": self._last_profile["core_anchors"],
                "confluences": self._last_profile["confluences"][:5],
            }
        return result
