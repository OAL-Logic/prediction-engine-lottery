"""
Dual-Core Statistical & Deterministic Contextual Scoring Engine 🎱🌌
===================================================================
Implements a game-agnostic Dual-Core Scoring Architecture (80% Statistical Pipeline +
20% Deterministic Astronomical/Temporal Contextual Layer) operating against `DrawRules`:

1. Statistical Pipeline (80% weight):
   - Multi-horizon rolling frequency z-scores (H10, H50, All-Time).
   - Recency anomaly (Atraso): standardized delay vs historical renewal cycles.
   - Universal 4-quadrant spatial board balance via `rules.board_cols` & `rules.number_range`.
   - High-density draw-to-draw recurrence prior (automatic when pick/pool density >= 0.50).
2. Contextual Pipeline (20% weight):
   - Lunar synodic month cycle and phase illumination.
   - Solar declination and seasonal day-of-year trigonometric harmonics.
   - Epoch timestamp SHA-256 cryptographic modulo mapping (Zero PRNG drift).
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

import pandas as pd

from engine.adapters import DrawRules

# Default target draw context: October 29, 2026 at 20:30 BRT (UTC-3)
DEFAULT_TARGET_ISO = "2026-10-29T20:30:00-03:00"

# Synodic lunar month constants
SYNODIC_MONTH_DAYS = 29.530588853
# Reference New Moon: 2000-01-06 18:14:00 UTC (Julian Day 2451549.26)
REFERENCE_NEW_MOON_EPOCH = 947182440.0  # Unix timestamp (seconds)

# Solar orbital constants
TROPICAL_YEAR_DAYS = 365.2422
EARTH_AXIAL_TILT_DEG = 23.44


@dataclass(frozen=True)
class AstronomicalContext:
    """Encapsulates deterministic astronomical and temporal variables."""
    target_time: datetime
    lunar_phase: float           # [0.0, 1.0) where 0=New, 0.25=First Qtr, 0.5=Full, 0.75=Last Qtr
    lunar_illumination: float    # [0.0, 1.0]
    solar_declination_deg: float # -23.44 to +23.44 degrees
    solar_harmonic_sin: float    # sin(2*pi*DOY/365.25)
    solar_harmonic_cos: float    # cos(2*pi*DOY/365.25)
    day_of_year: int
    iso_timestamp: str


def sigmoid(z: float) -> float:
    """Numerically stable sigmoid mapping R -> (0, 1)."""
    if z < -20.0:
        return 0.0
    if z > 20.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def get_quadrant(number: int, rules: DrawRules) -> int:
    """
    Determine the spatial quadrant index (1..4) for a number on any lottery grid
    using `rules.number_range` and `rules.board_cols` (zero hardcoded pool sizes).
    """
    lo, hi = rules.number_range
    pool_size = max(1, hi - lo + 1)
    cols = max(2, getattr(rules, "board_cols", 0) or (5 if pool_size <= 25 else 10))
    rows = max(2, math.ceil(pool_size / cols))

    idx = max(0, number - lo)
    row = idx // cols
    col = idx % cols

    mid_row = math.ceil(rows / 2.0)
    mid_col = math.ceil(cols / 2.0)

    if row < mid_row and col < mid_col:
        return 1
    elif row < mid_row and col >= mid_col:
        return 2
    elif row >= mid_row and col < mid_col:
        return 3
    return 4


class ContextEngine:
    """
    Computes deterministic temporal, astronomical, and cyclical context parameters.
    Translates environmental harmonics into per-number score modulations.
    """

    def __init__(self, target_iso: Optional[str] = None) -> None:
        self.iso_str = target_iso or DEFAULT_TARGET_ISO
        self.target_time = self._parse_iso(self.iso_str)
        self.astronomy = self._compute_astronomy(self.target_time)

    @staticmethod
    def _parse_iso(iso_string: str) -> datetime:
        """Parse ISO date or datetime with timezone fallback."""
        try:
            clean = iso_string.strip()
            if len(clean) == 10 and "T" not in clean:
                clean = f"{clean}T20:30:00-03:00"
            dt = datetime.fromisoformat(clean)
            if dt.tzinfo is None:
                brt = timezone(timedelta(hours=-3))
                dt = dt.replace(tzinfo=brt)
            return dt
        except Exception:
            brt = timezone(timedelta(hours=-3))
            return datetime(2026, 10, 29, 20, 30, 0, tzinfo=brt)

    @classmethod
    def _compute_astronomy(cls, dt: datetime) -> AstronomicalContext:
        """Calculate exact deterministic astronomical cycles for the timestamp."""
        utc_dt = dt.astimezone(timezone.utc)
        epoch_seconds = utc_dt.timestamp()

        # 1. Lunar Synodic Phase
        elapsed_seconds = epoch_seconds - REFERENCE_NEW_MOON_EPOCH
        elapsed_days = elapsed_seconds / 86400.0
        lunar_phase = (elapsed_days % SYNODIC_MONTH_DAYS) / SYNODIC_MONTH_DAYS
        lunar_illumination = (1.0 - math.cos(2.0 * math.pi * lunar_phase)) / 2.0

        # 2. Solar Declination & Seasonal Harmonics
        doy = utc_dt.timetuple().tm_yday
        fractional_year = doy / TROPICAL_YEAR_DAYS
        harmonic_angle = 2.0 * math.pi * fractional_year

        sin_harmonic = math.sin(harmonic_angle)
        cos_harmonic = math.cos(harmonic_angle)

        dec_angle = 2.0 * math.pi * ((doy + 10) / TROPICAL_YEAR_DAYS)
        solar_declination = -EARTH_AXIAL_TILT_DEG * math.cos(dec_angle)

        return AstronomicalContext(
            target_time=dt,
            lunar_phase=lunar_phase,
            lunar_illumination=lunar_illumination,
            solar_declination_deg=solar_declination,
            solar_harmonic_sin=sin_harmonic,
            solar_harmonic_cos=cos_harmonic,
            day_of_year=doy,
            iso_timestamp=dt.isoformat(),
        )

    def compute_hash_modulo(self, number: int, modulo: int = 10000) -> float:
        """
        Deterministic cryptographic hash modulo mapping.
        Produces a stationary, repeatable float in [0.0, 1.0] for (timestamp, number).
        """
        payload = f"{self.astronomy.iso_timestamp}:{number}".encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        int_val = int(digest[:8], 16)
        return (int_val % modulo) / float(modulo - 1)

    def score_context(self, number: int, lo: int, hi: int) -> float:
        """
        Compute contextual fitness score S_ctx(n) strictly bounded between [0.0, 1.0]
        for any number range [lo, hi] (including 0-indexed games).
        """
        total_pool = max(1, hi - lo + 1)
        h_score = self.compute_hash_modulo(number)

        theta_n = 2.0 * math.pi * ((number - lo) / total_pool)
        lunar_resonance = (1.0 + math.cos(theta_n - 2.0 * math.pi * self.astronomy.lunar_phase)) / 2.0

        dec_rad = math.radians(self.astronomy.solar_declination_deg)
        solar_resonance = (1.0 + math.sin(theta_n + dec_rad)) / 2.0

        raw_score = (
            0.40 * h_score +
            0.35 * lunar_resonance +
            0.25 * solar_resonance
        )
        return max(0.0, min(1.0, float(raw_score)))

    def generate_context_scores(
        self,
        pool_or_range: Union[int, Tuple[int, int], DrawRules],
    ) -> Dict[int, float]:
        """
        Generate deterministic S_ctx(n) scores for all numbers in the game pool.
        Accepts DrawRules, a (lo, hi) tuple, or an integer pool size (1..total_pool).
        """
        if isinstance(pool_or_range, DrawRules):
            lo, hi = pool_or_range.number_range
        elif isinstance(pool_or_range, tuple):
            lo, hi = pool_or_range
        else:
            lo, hi = 1, int(pool_or_range)

        scores: Dict[int, float] = {}
        for n in range(lo, hi + 1):
            scores[n] = round(self.score_context(n, lo, hi), 6)
        return scores


class StatisticalPipeline:
    """
    Computes statistical fitness scores S_stat(n) for candidate numbers across any `DrawRules`.
    Evaluates multi-horizon rolling frequency z-scores, delay anomalies, spatial quadrants,
    and high-density draw recurrence priors.
    """

    def __init__(
        self,
        history: Union[pd.DataFrame, Sequence[Any]],
        rules: DrawRules,
    ) -> None:
        self.rules = rules
        self.lo, self.hi = rules.number_range
        self.pool_size = max(1, self.hi - self.lo + 1)
        self.draws_numbers: List[List[int]] = self._extract_draws(history)
        self.total_draws = len(self.draws_numbers)
        self.last_draw: List[int] = self.draws_numbers[-1] if self.draws_numbers else []

    @staticmethod
    def _extract_draws(history: Union[pd.DataFrame, Sequence[Any]]) -> List[List[int]]:
        if isinstance(history, pd.DataFrame):
            if history.empty or "numbers" not in history.columns:
                return []
            return [[int(x) for x in row] for row in history["numbers"].tolist() if isinstance(row, (list, tuple))]
        extracted: List[List[int]] = []
        for item in history:
            if isinstance(item, dict) and "numbers" in item:
                extracted.append([int(x) for x in item["numbers"]])
            elif hasattr(item, "numbers"):
                extracted.append([int(x) for x in getattr(item, "numbers")])
            elif isinstance(item, (list, tuple)):
                extracted.append([int(x) for x in item])
        return extracted

    def compute_frequencies(self, horizon: Optional[int] = None) -> Dict[int, int]:
        """Compute occurrence counts for each number in the specified horizon."""
        subset = (
            self.draws_numbers[-horizon:]
            if horizon and horizon < self.total_draws
            else self.draws_numbers
        )
        counts: Dict[int, int] = {n: 0 for n in range(self.lo, self.hi + 1)}
        for draw in subset:
            for num in draw:
                if self.lo <= num <= self.hi:
                    counts[num] += 1
        return counts

    def compute_frequency_zscores(self, horizon: Optional[int] = None) -> Dict[int, float]:
        """Compute standardized frequency z-scores for a given horizon."""
        subset_len = min(horizon, self.total_draws) if horizon else self.total_draws
        if subset_len == 0:
            return {n: 0.0 for n in range(self.lo, self.hi + 1)}

        counts = self.compute_frequencies(horizon=subset_len)
        p = min(0.999, max(0.001, self.rules.pick_count / float(self.pool_size)))
        expected_mu = subset_len * p
        variance = subset_len * p * (1.0 - p)
        sigma = math.sqrt(variance) if variance > 0 else 1.0

        return {n: (count - expected_mu) / sigma for n, count in counts.items()}

    def compute_delay_anomalies(self) -> Dict[int, float]:
        """
        Recency Anomaly (Atraso):
        Current delay vs historical interval expectation across all numbers in [lo, hi].
        """
        intervals: Dict[int, List[int]] = {n: [] for n in range(self.lo, self.hi + 1)}
        last_seen_idx: Dict[int, int] = {n: -1 for n in range(self.lo, self.hi + 1)}

        for draw_idx, draw in enumerate(self.draws_numbers):
            for num in draw:
                if self.lo <= num <= self.hi:
                    if last_seen_idx[num] != -1:
                        intervals[num].append(draw_idx - last_seen_idx[num])
                    last_seen_idx[num] = draw_idx

        theoretical_mean_gap = self.pool_size / float(max(1, self.rules.pick_count))
        delay_scores: Dict[int, float] = {}

        for n in range(self.lo, self.hi + 1):
            current_delay = (
                (self.total_draws - 1) - last_seen_idx[n]
                if last_seen_idx[n] != -1
                else self.total_draws
            )
            hist_gaps = intervals[n]
            if len(hist_gaps) >= 2:
                mean_gap = sum(hist_gaps) / len(hist_gaps)
                var_gap = sum((g - mean_gap) ** 2 for g in hist_gaps) / (len(hist_gaps) - 1)
                std_gap = math.sqrt(var_gap) if var_gap > 0 else 1.0
            else:
                mean_gap = theoretical_mean_gap
                std_gap = theoretical_mean_gap * 0.8

            z_delay = (current_delay - mean_gap) / max(std_gap, 1.0)
            delay_scores[n] = sigmoid(z_delay)

        return delay_scores

    def compute_stat_scores(self) -> Dict[int, float]:
        """
        Compute composite S_stat(n) strictly bounded between [0.0, 1.0].
        """
        z_10 = self.compute_frequency_zscores(horizon=10)
        z_50 = self.compute_frequency_zscores(horizon=50)
        z_all = self.compute_frequency_zscores(horizon=None)
        delay_scores = self.compute_delay_anomalies()

        last_draw_set: Set[int] = set(self.last_draw)
        density = self.rules.pick_count / float(self.pool_size)

        counts_10 = self.compute_frequencies(horizon=10)
        quad_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for n, cnt in counts_10.items():
            q = get_quadrant(n, self.rules)
            quad_counts[q] += cnt
        avg_quad_cnt = sum(quad_counts.values()) / 4.0 if quad_counts else 1.0

        scores: Dict[int, float] = {}
        for n in range(self.lo, self.hi + 1):
            freq_score = (
                0.40 * sigmoid(z_10[n]) +
                0.35 * sigmoid(z_50[n]) +
                0.25 * sigmoid(z_all[n])
            )
            d_score = delay_scores[n]
            s_stat = 0.55 * freq_score + 0.45 * d_score

            # High-density game recurrence prior (e.g., 15/25 Lotofácil where density >= 0.50)
            if density >= 0.50 and last_draw_set:
                if n in last_draw_set:
                    s_stat *= 1.15
                else:
                    s_stat *= 0.90

            q = get_quadrant(n, self.rules)
            quad_diff = (avg_quad_cnt - quad_counts[q]) / max(avg_quad_cnt, 1.0)
            quad_mod = 1.0 + (0.05 * max(-1.0, min(1.0, quad_diff)))
            s_stat *= quad_mod

            scores[n] = max(0.001, s_stat)

        min_s = min(scores.values()) if scores else 0.0
        max_s = max(scores.values()) if scores else 1.0
        spread = max_s - min_s if max_s > min_s else 1.0

        normalized_scores: Dict[int, float] = {}
        for n, raw_val in scores.items():
            norm_val = (raw_val - min_s) / spread
            normalized_scores[n] = round(max(0.0, min(1.0, norm_val)), 6)

        return normalized_scores


class DualCoreScorer:
    """
    Blends Statistical and Contextual scores with the strict 80/20 ratio:
    S(n) = 0.80 * S_stat(n) + 0.20 * S_ctx(n)
    Strictly bounded between [0.0, 1.0].
    """

    STAT_WEIGHT = 0.80
    CTX_WEIGHT = 0.20

    def __init__(
        self,
        stat_scores: Dict[int, float],
        ctx_scores: Dict[int, float],
    ) -> None:
        self.stat_scores = stat_scores
        self.ctx_scores = ctx_scores

    def compute_composite_scores(self) -> Dict[int, float]:
        """Returns map of candidate number -> fitness score S(n) in [0.0, 1.0]."""
        composite: Dict[int, float] = {}
        all_numbers = sorted(set(self.stat_scores.keys()).union(self.ctx_scores.keys()))

        for n in all_numbers:
            s_stat = self.stat_scores.get(n, 0.5)
            s_ctx = self.ctx_scores.get(n, 0.5)
            score = (self.STAT_WEIGHT * s_stat) + (self.CTX_WEIGHT * s_ctx)
            composite[n] = round(max(0.0, min(1.0, score)), 6)

        return composite
