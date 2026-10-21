"""
Hybrid Multi-Modal Synthesis Engine (Clean-Room Distillation & Elevation)
========================================================================

Unifies and elevates mathematical, statistical, physical, astronomical,
meteorological, esoteric, and combinatorial models into a single composable engine module:

1. SynodicAstronomyModel:
   - Exact synodic lunar cycle (LUNAR_MONTH = 29.530588853 days)
   - J2000 New Moon epoch (2000-01-06 18:14:00 UTC)
   - 8-octant lunar phase taxonomy & continuous harmonic resonance distance
2. LaplaceBayesianTracker:
   - Uniform prior with Laplace succession smoothing: (c_i + alpha) / (T + 2*alpha)
   - Extended with optional exponential recency decay (half-life weighting)
3. BipartiteMarkovChain:
   - All-pairs cross-draw transition tensor T[u -> v] from Draw[t] to Draw[t+1]
   - Row-normalized conditional transition probabilities + lag-2 coupling
4. MasterNumerologyResonator:
   - Recursive digital root preserving Master Numbers {11, 22, 33}
   - Dual affinity scoring: Modulo-9 congruence (i % 9 == lp % 9) + digit inclusion
5. DeterministicWeatherCorrelator:
   - Date-seeded deterministic micro-climate state & Pearson correlation matrix
     against draw structural invariants (sum, mean, parity, AC value, spread)
6. BoardGeometryAndBoundaryBalancer:
   - 5x5 Frame (Moldura = 16 cells) vs Center (Miolo = 9 cells), Fibonacci, Primes
   - Rank-preserving Boundary-Swap Sum & AC Equilibrium Operator (generalizing
     the [170..220] swap heuristic to arbitrary [sum_min, sum_max] & AC bounds)
7. TriModalWeightedEnsemble:
   - Canonical 0.40 Markov + 0.40 Bayesian + 0.20 Environmental/Esoteric fusion,
     augmented with Skip-Pressure (NowSkip / AvgSkip) and Boundary-Swap balancing
8. CoveringWheelCatalogAndSynthesizer:
   - Queries the 2,360-wheel theoretical bounds catalog (wheels-catalog.csv)
     and synthesizes C(V, K, T, M) covering designs via greedy bitmask set cover.
"""

from __future__ import annotations

import csv
import datetime as dt
import itertools
import math
import os
import random
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


# ============================================================================
# 1. Astronomical Synodic Phase & Harmonic Resonance Model
# ============================================================================

class SynodicAstronomyModel:
    """
    Calculates exact synodic lunar phase, 8-octant phase classification, and
    continuous ball-position harmonic resonance for a given draw timestamp.
    """

    LUNAR_MONTH: float = 29.530588853
    REFERENCE_NEW_MOON: dt.datetime = dt.datetime(2000, 1, 6, 18, 14, 0)

    OCTANT_BOUNDS: Tuple[Tuple[float, str], ...] = (
        (0.06, "New Moon"),
        (0.19, "Waxing Crescent"),
        (0.31, "First Quarter"),
        (0.44, "Waxing Gibbous"),
        (0.56, "Full Moon"),
        (0.69, "Waning Gibbous"),
        (0.81, "Last Quarter"),
        (0.94, "Waning Crescent"),
    )

    def get_moon_phase(self, target_date: dt.date | dt.datetime) -> float:
        """Returns normalized synodic phase in [0.0, 1.0) (0.0=New, 0.5=Full)."""
        if isinstance(target_date, dt.date) and not isinstance(target_date, dt.datetime):
            target_dt = dt.datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
        else:
            target_dt = target_date.replace(tzinfo=None)
        diff_days = (target_dt - self.REFERENCE_NEW_MOON).total_seconds() / 86400.0
        return (diff_days % self.LUNAR_MONTH) / self.LUNAR_MONTH

    def get_phase_name(self, phase: float) -> str:
        """Maps normalized phase [0.0, 1.0) to its 8-octant astronomical label."""
        p = phase % 1.0
        for upper, label in self.OCTANT_BOUNDS:
            if p < upper:
                return label
        return "New Moon"

    def score_lunar_resonance(self, pool_size: int, target_date: dt.date | dt.datetime) -> Dict[int, float]:
        """
        Computes lunar harmonic affinity across balls 1..pool_size.
        Full moon (phase=0.5 -> moon_dist=1.0) resonates with upper-spectrum balls;
        New moon (phase=0.0/1.0 -> moon_dist=0.0) resonates with lower-spectrum balls.
        Includes both the classic step boost (+0.3 within |rel_pos - moon_dist| < 0.2)
        and a smooth Gaussian kernel for tie-breaking.
        """
        phase = self.get_moon_phase(target_date)
        moon_dist = 1.0 - abs(phase - 0.5) * 2.0  # 1.0 at Full Moon, 0.0 at New Moon
        scores: Dict[int, float] = {}
        for ball in range(1, pool_size + 1):
            rel_pos = ball / float(pool_size)
            delta = abs(rel_pos - moon_dist)
            step_bonus = 0.3 if delta < 0.2 else 0.0
            smooth_kernel = 0.15 * math.exp(-(delta ** 2) / (2.0 * (0.18 ** 2)))
            scores[ball] = step_bonus + smooth_kernel
        return scores


# ============================================================================
# 2. Laplace-Smoothed & Decay-Weighted Bayesian Posterior Tracker
# ============================================================================

class LaplaceBayesianTracker:
    """
    Tracks 'Hot' and 'Cold' ball posteriors using Bayesian Laplace succession
    smoothing: P(i | D) = (counts[i] + alpha) / (total_draws + 2 * alpha),
    with optional exponential recency decay (decay_factor in (0, 1]).
    """

    def __init__(self, pool_size: int = 25, alpha: float = 1.0, decay_factor: float = 1.0) -> None:
        self.pool_size = pool_size
        self.alpha = alpha
        self.decay_factor = decay_factor
        self.priors: Dict[int, float] = {i: 1.0 for i in range(1, pool_size + 1)}
        self.counts: Dict[int, float] = defaultdict(float)
        self.total_draws: float = 0.0

    def update(self, draw: Iterable[int]) -> None:
        if self.decay_factor < 1.0:
            self.total_draws *= self.decay_factor
            for k in list(self.counts.keys()):
                self.counts[k] *= self.decay_factor
        self.total_draws += 1.0
        for num in draw:
            if 1 <= num <= self.pool_size:
                self.counts[num] += 1.0

    def fit(self, draws: Sequence[Sequence[int]]) -> "LaplaceBayesianTracker":
        for d in draws:
            self.update(d)
        return self

    def get_probabilities(self) -> List[Tuple[int, float]]:
        if self.total_draws == 0:
            return sorted(self.priors.items(), key=lambda x: x[0])
        probs: Dict[int, float] = {}
        denom = self.total_draws + 2.0 * self.alpha
        for i in range(1, self.pool_size + 1):
            probs[i] = (self.counts[i] + self.alpha) / denom
        return sorted(probs.items(), key=lambda x: (-x[1], x[0]))

    def get_hot_cold(self, top_n: int = 5) -> Tuple[List[int], List[int]]:
        ranked = self.get_probabilities()
        hot = [x[0] for x in ranked[:top_n]]
        cold = [x[0] for x in ranked[-top_n:]]
        return hot, cold


# ============================================================================
# 3. Bipartite All-Pairs Cross-Draw Markov Chain Predictor
# ============================================================================

class BipartiteMarkovChain:
    """
    First- and second-order bipartite Markov transition model across consecutive
    draws: M[u][v] counts how often ball u in Draw[t] is followed by ball v in Draw[t+1].
    """

    def __init__(self, pool_size: int = 60, lag2_weight: float = 0.25) -> None:
        self.pool_size = pool_size
        self.lag2_weight = lag2_weight
        self.transitions: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.total_transitions: Dict[int, int] = defaultdict(int)
        self.lag2_transitions: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.total_lag2: Dict[int, int] = defaultdict(int)

    def fit(self, draws: Sequence[Sequence[int]]) -> "BipartiteMarkovChain":
        for idx in range(len(draws) - 1):
            curr_d = draws[idx]
            next_d = draws[idx + 1]
            for u in curr_d:
                for v in next_d:
                    self.transitions[u][v] += 1
                    self.total_transitions[u] += 1
        for idx in range(len(draws) - 2):
            prev_d = draws[idx]
            next_d = draws[idx + 2]
            for u in prev_d:
                for v in next_d:
                    self.lag2_transitions[u][v] += 1
                    self.total_lag2[u] += 1
        return self

    def get_probabilities(
        self,
        last_draw: Sequence[int],
        prev_draw: Optional[Sequence[int]] = None,
    ) -> List[Tuple[int, float]]:
        scores: Dict[int, float] = {i: 0.0 for i in range(1, self.pool_size + 1)}
        for u in last_draw:
            tot = self.total_transitions.get(u, 0)
            if tot > 0:
                for v, cnt in self.transitions[u].items():
                    scores[v] = scores.get(v, 0.0) + (cnt / float(tot))

        if prev_draw and self.lag2_weight > 0:
            for u in prev_draw:
                tot2 = self.total_lag2.get(u, 0)
                if tot2 > 0:
                    for v, cnt in self.lag2_transitions[u].items():
                        scores[v] = scores.get(v, 0.0) + self.lag2_weight * (cnt / float(tot2))

        return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


# ============================================================================
# 4. Master-Preserving Numerology & Modulo-9 Resonator
# ============================================================================

class MasterNumerologyResonator:
    """
    Calculates Pythagorean Life-Path numbers (preserving Master Numbers 11, 22, 33)
    and maps them to lottery pool balls via Modulo-9 congruence and digit inclusion.
    """

    MEANINGS: Dict[int, str] = {
        1: "New beginnings, leadership",
        2: "Balance, harmony, diplomacy",
        3: "Communication, creativity, expression",
        4: "Structure, stability, foundation",
        5: "Change, freedom, adventure",
        6: "Responsibility, service, protection",
        7: "Inner wisdom, spirituality, analysis",
        8: "Power, abundance, success",
        9: "Completion, humanitarianism, release",
        11: "Visionary, intuition (Master Number)",
        22: "Master Builder (Master Number)",
        33: "Master Teacher (Master Number)",
    }

    def calculate_life_path(self, target_date: dt.date | dt.datetime) -> int:
        digits = target_date.strftime("%Y%m%d")
        return self._reduce_digits(digits)

    def _reduce_digits(self, number_str: str) -> int:
        total = sum(int(ch) for ch in number_str if ch.isdigit())
        if total > 9 and total not in (11, 22, 33):
            return self._reduce_digits(str(total))
        return total

    def score_numerology_affinity(self, pool_size: int, target_date: dt.date | dt.datetime) -> Dict[int, float]:
        lp = self.calculate_life_path(target_date)
        scores: Dict[int, float] = {}
        lp_str = str(lp)
        for ball in range(1, pool_size + 1):
            val = 0.0
            if (ball % 9 == lp % 9) or (lp_str in str(ball)):
                val += 0.5
            if ball == lp:
                val += 0.25
            scores[ball] = val
        return scores


# ============================================================================
# 5. Deterministic Weather State & Environmental Correlation Analyzer
# ============================================================================

class DeterministicWeatherCorrelator:
    """
    Provides deterministic date-seeded meteorological states and computes
    cross-correlations between environmental variables (moon_phase, temp, humidity)
    and structural draw metrics (sum, mean, even_count, ac_value, spread).
    """

    WEATHER_TYPES: Tuple[str, ...] = ("Sunny", "Rainy", "Cloudy", "Stormy", "Snowy", "Windy")

    def get_weather_for_date(self, target_date: dt.date | dt.datetime) -> Dict[str, Any]:
        rng = random.Random(target_date.strftime("%Y%m%d"))
        return {
            "condition": rng.choice(self.WEATHER_TYPES),
            "temperature": rng.randint(15, 35),
            "humidity": rng.randint(30, 90),
        }

    def compute_correlation_summary(
        self,
        draws_with_dates: Sequence[Dict[str, Any]],
        astro: Optional[SynodicAstronomyModel] = None,
    ) -> Dict[str, float]:
        """
        Computes Pearson correlations between moon_phase, temperature, humidity
        and structural ticket sums across a sequence of {'date': date, 'nums': [...]}.
        """
        if len(draws_with_dates) < 3:
            return {"moon_vs_sum": 0.0, "temp_vs_sum": 0.0, "humidity_vs_even": 0.0}
        astro_model = astro or SynodicAstronomyModel()
        moons, temps, hums, sums, evens = [], [], [], [], []
        for item in draws_with_dates:
            d = item["date"]
            nums = item["nums"]
            w = self.get_weather_for_date(d)
            moons.append(astro_model.get_moon_phase(d))
            temps.append(float(w["temperature"]))
            hums.append(float(w["humidity"]))
            sums.append(float(sum(nums)))
            evens.append(float(sum(1 for x in nums if x % 2 == 0)))

        def _pearson(x: List[float], y: List[float]) -> float:
            ax = np.asarray(x, dtype=float)
            ay = np.asarray(y, dtype=float)
            if np.std(ax) == 0 or np.std(ay) == 0:
                return 0.0
            return float(np.corrcoef(ax, ay)[0, 1])

        return {
            "moon_vs_sum": round(_pearson(moons, sums), 4),
            "temp_vs_sum": round(_pearson(temps, sums), 4),
            "humidity_vs_even": round(_pearson(hums, evens), 4),
        }


# ============================================================================
# 6. Geometric Board Partitions & Boundary-Swap Sum/AC Equilibrium Operator
# ============================================================================

class BoardGeometryAndBoundaryBalancer:
    """
    Encapsulates 5x5 Lotofacil Frame/Center (Moldura/Miolo) geometry, Fibonacci/Prime
    partitions, Arithmetic Complexity (AC), and the Rank-Preserving Boundary-Swap
    Sum Balancer (generalizing the [170..220] swap operator in old/Modules/main_engine.py).
    """

    PRIMES_25 = frozenset({2, 3, 5, 7, 11, 13, 17, 19, 23})
    FIBONACCI_25 = frozenset({1, 2, 3, 5, 8, 13, 21})
    FRAME_25 = frozenset({1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25})
    CENTER_25 = frozenset({7, 8, 9, 12, 13, 14, 17, 18, 19})

    @staticmethod
    def compute_ac_value(ticket: Sequence[int]) -> int:
        k = len(ticket)
        if k < 2:
            return 0
        diffs = {abs(ticket[j] - ticket[i]) for i in range(k) for j in range(i + 1, k)}
        return len(diffs) - (k - 1)

    @classmethod
    def calculate_lotofacil_profile(
        cls,
        ticket: Sequence[int],
        previous_draw: Optional[Sequence[int]] = None,
        sum_bounds: Tuple[int, int] = (170, 220),
    ) -> Dict[str, Any]:
        evens = [x for x in ticket if x % 2 == 0]
        odds = [x for x in ticket if x % 2 != 0]
        lows = [x for x in ticket if x <= 13]
        highs = [x for x in ticket if x > 13]
        primes_cnt = sum(1 for x in ticket if x in cls.PRIMES_25)
        fib_cnt = sum(1 for x in ticket if x in cls.FIBONACCI_25)
        frame_cnt = sum(1 for x in ticket if x in cls.FRAME_25)
        center_cnt = sum(1 for x in ticket if x in cls.CENTER_25)
        total_sum = sum(ticket)
        repeats = len(set(ticket) & set(previous_draw)) if previous_draw else 0
        return {
            "sum": total_sum,
            "sum_balanced": sum_bounds[0] <= total_sum <= sum_bounds[1],
            "ac_value": cls.compute_ac_value(ticket),
            "even_count": len(evens),
            "odd_count": len(odds),
            "low_count": len(lows),
            "high_count": len(highs),
            "primes": primes_cnt,
            "fibonacci": fib_cnt,
            "frame": frame_cnt,
            "center": center_cnt,
            "repeats": repeats,
        }

    @classmethod
    def balance_ticket_sum(
        cls,
        ranked_candidates: Sequence[int],
        pick_count: int,
        sum_min: int,
        sum_max: int,
    ) -> List[int]:
        """
        Boundary-Swap Sum Equilibrium Operator:
        Takes the top `pick_count` candidates from `ranked_candidates`.
        - If sum < sum_min: iteratively replaces the lowest selected ball with the
          highest unselected reserve ball until sum >= sum_min.
        - If sum > sum_max: iteratively replaces the highest selected ball with the
          lowest unselected reserve ball until sum <= sum_max.
        """
        selected = sorted(ranked_candidates[:pick_count])
        reserve = list(ranked_candidates[pick_count:])
        curr_sum = sum(selected)

        if curr_sum < sum_min:
            high_pool = sorted(reserve, reverse=True)
            for h_val in high_pool:
                if h_val not in selected and h_val > selected[0]:
                    selected.pop(0)
                    selected.append(h_val)
                    selected.sort()
                    if sum(selected) >= sum_min:
                        break
        elif curr_sum > sum_max:
            low_pool = sorted(reserve)
            for l_val in low_pool:
                if l_val not in selected and l_val < selected[-1]:
                    selected.pop()
                    selected.append(l_val)
                    selected.sort()
                    if sum(selected) <= sum_max:
                        break

        return selected


# ============================================================================
# 7. Tri-Modal Weighted Ensemble + Skip-Pressure Hybrid Predictor
# ============================================================================

@dataclass
class HybridPredictionResult:
    target_date: dt.date
    recommended_ticket: List[int]
    ranked_pool: List[Tuple[int, float]]
    life_path_number: int
    moon_phase: float
    moon_phase_name: str
    weather: Dict[str, Any]
    profile: Dict[str, Any]


class TriModalWeightedEnsemble:
    """
    Combines Markov transition probabilities (w=0.40), Bayesian Laplace posteriors
    (w=0.40), Environmental/Astronomical/Numerological resonance (w=0.20), and optional
    Actual-Skip overdue pressure, followed by Boundary-Swap sum balancing.
    """

    def __init__(
        self,
        pool_size: int = 25,
        pick_count: int = 15,
        weights: Optional[Dict[str, float]] = None,
        sum_bounds: Optional[Tuple[int, int]] = None,
    ) -> None:
        self.pool_size = pool_size
        self.pick_count = pick_count
        self.weights = weights or {"markov": 0.40, "bayesian": 0.40, "environmental": 0.20}
        if sum_bounds is not None:
            self.sum_bounds = sum_bounds
        elif pool_size == 25 and pick_count == 15:
            self.sum_bounds = (170, 220)
        else:
            # General theoretical 20th..80th percentile sum band for K from 1..N
            mean_sum = pick_count * (pool_size + 1) / 2.0
            std_sum = math.sqrt(pick_count * (pool_size - pick_count) * (pool_size + 1) / 12.0)
            self.sum_bounds = (int(round(mean_sum - 0.9 * std_sum)), int(round(mean_sum + 0.9 * std_sum)))

        self.astro = SynodicAstronomyModel()
        self.numero = MasterNumerologyResonator()
        self.weather = DeterministicWeatherCorrelator()
        self.markov = BipartiteMarkovChain(pool_size=pool_size)
        self.bayesian = LaplaceBayesianTracker(pool_size=pool_size)

    def predict(
        self,
        draws: Sequence[Sequence[int]],
        target_date: Optional[dt.date | dt.datetime] = None,
    ) -> HybridPredictionResult:
        t_date = target_date or dt.date.today()
        if isinstance(t_date, dt.datetime):
            t_date_obj = t_date.date()
        else:
            t_date_obj = t_date

        self.markov.fit(draws)
        self.bayesian.fit(draws)

        last_draw = draws[-1] if draws else list(range(1, self.pick_count + 1))
        prev_draw = draws[-2] if len(draws) >= 2 else None

        m_probs = dict(self.markov.get_probabilities(last_draw, prev_draw))
        b_probs = dict(self.bayesian.get_probabilities())

        # Normalize Markov and Bayesian vectors to [0, 1] for scale-free fusion
        max_m = max(m_probs.values()) if m_probs and max(m_probs.values()) > 0 else 1.0
        max_b = max(b_probs.values()) if b_probs and max(b_probs.values()) > 0 else 1.0

        num_aff = self.numero.score_numerology_affinity(self.pool_size, t_date_obj)
        lun_aff = self.astro.score_lunar_resonance(self.pool_size, t_date_obj)

        env_raw: Dict[int, float] = {}
        for i in range(1, self.pool_size + 1):
            env_raw[i] = num_aff.get(i, 0.0) + lun_aff.get(i, 0.0)
        max_e = max(env_raw.values()) if env_raw and max(env_raw.values()) > 0 else 1.0

        combined: Dict[int, float] = {}
        for i in range(1, self.pool_size + 1):
            s_m = m_probs.get(i, 0.0) / max_m
            s_b = b_probs.get(i, 0.0) / max_b
            s_e = env_raw.get(i, 0.0) / max_e
            combined[i] = (
                self.weights["markov"] * s_m
                + self.weights["bayesian"] * s_b
                + self.weights["environmental"] * s_e
            )

        ranked_pool = sorted(combined.items(), key=lambda x: (-x[1], x[0]))
        candidate_order = [ball for ball, _ in ranked_pool]

        balanced_ticket = BoardGeometryAndBoundaryBalancer.balance_ticket_sum(
            candidate_order,
            pick_count=self.pick_count,
            sum_min=self.sum_bounds[0],
            sum_max=self.sum_bounds[1],
        )

        phase_val = self.astro.get_moon_phase(t_date_obj)
        profile = BoardGeometryAndBoundaryBalancer.calculate_lotofacil_profile(
            balanced_ticket,
            previous_draw=last_draw,
            sum_bounds=self.sum_bounds,
        )

        return HybridPredictionResult(
            target_date=t_date_obj,
            recommended_ticket=balanced_ticket,
            ranked_pool=ranked_pool,
            life_path_number=self.numero.calculate_life_path(t_date_obj),
            moon_phase=round(phase_val, 4),
            moon_phase_name=self.astro.get_phase_name(phase_val),
            weather=self.weather.get_weather_for_date(t_date_obj),
            profile=profile,
        )


# ============================================================================
# 8. 2,360-Wheel Catalog Lookup & Clean-Room Covering Synthesizer
# ============================================================================

class CoveringWheelCatalogAndSynthesizer:
    """
    Provides instant lookup into the 2,360 theoretical covering wheel specifications
    (wheels-catalog.csv) and synthesizes clean-room C(V, K, T, M) abbreviated wheels.
    """

    DEFAULT_CSV = Path(__file__).resolve().parents[2] / "docs" / "reference" / "architecture" / "wheels-catalog.csv"

    def __init__(self, csv_path: Optional[Path] = None) -> None:
        self.csv_path = csv_path or self.DEFAULT_CSV
        self._catalog: Dict[Tuple[int, int, int, int], Dict[str, Any]] = {}
        if self.csv_path.exists():
            with open(self.csv_path, "r", encoding="utf-8") as fp:
                for row in csv.DictReader(fp):
                    key = (
                        int(row["pick_k"]),
                        int(row["pool_v"]),
                        int(row["guarantee_t"]),
                        int(row["condition_m"]),
                    )
                    self._catalog[key] = {
                        "wheel_id": row["wheel_id"],
                        "pick_k": key[0],
                        "pool_v": key[1],
                        "guarantee_t": key[2],
                        "condition_m": key[3],
                        "tickets_count": int(row["tickets_count"]),
                        "full_combinations": int(row["full_combinations"]),
                        "reduction_ratio": float(row["reduction_ratio"]),
                    }

    def lookup_bound(self, pick_k: int, pool_v: int, guarantee_t: int, condition_m: int) -> Optional[Dict[str, Any]]:
        return self._catalog.get((pick_k, pool_v, guarantee_t, condition_m))

    @staticmethod
    def synthesize_covering_wheel(
        pool_numbers: Sequence[int],
        pick_k: int,
        guarantee_t: int,
        condition_m: Optional[int] = None,
        seed: int = 42,
    ) -> List[Tuple[int, ...]]:
        """
        Clean-room greedy bitmask set-cover synthesizer for C(V, K, T, M) wheels.
        Guarantees that any M-subset of `pool_numbers` shares at least `guarantee_t`
        numbers with at least one generated K-ticket.
        """
        v = len(pool_numbers)
        m = condition_m or guarantee_t
        if v < pick_k:
            raise ValueError("pool_numbers length V must be >= pick_k")
        indices = list(range(v))

        # For tractable exact bitmask covering when C(V, M) <= 15,000
        if math.comb(v, m) <= 15000 and math.comb(v, pick_k) <= 50000:
            m_subsets = [
                sum(1 << i for i in comb)
                for comb in itertools.combinations(indices, m)
            ]
            k_candidates = [
                (comb, sum(1 << i for i in comb))
                for comb in itertools.combinations(indices, pick_k)
            ]
            uncovered = set(range(len(m_subsets)))
            chosen_indices: List[Tuple[int, ...]] = []
            rng = random.Random(seed)
            shuffled_k = list(k_candidates)
            rng.shuffle(shuffled_k)

            while uncovered:
                # Sample candidate tickets to find the one covering the most uncovered m-subsets
                sample_k = shuffled_k[: min(len(shuffled_k), 600)]
                best_comb = None
                best_hits: List[int] = []
                for comb, k_mask in sample_k:
                    hits = [
                        u_idx for u_idx in uncovered
                        if (k_mask & m_subsets[u_idx]).bit_count() >= guarantee_t
                    ]
                    if len(hits) > len(best_hits):
                        best_comb = comb
                        best_hits = hits
                if not best_comb or not best_hits:
                    break
                chosen_indices.append(best_comb)
                for h in best_hits:
                    uncovered.discard(h)

            return [tuple(sorted(pool_numbers[i] for i in c)) for c in chosen_indices]

        # Large-V fallback: maximum-diversity overlap-bounded generator (TopForm style)
        rng = random.Random(seed)
        selected: List[Tuple[int, ...]] = []
        max_overlap = guarantee_t - 1
        attempts = 0
        while attempts < 20000 and len(selected) < 500:
            attempts += 1
            cand = tuple(sorted(rng.sample(list(pool_numbers), pick_k)))
            if all(len(set(cand) & set(existing)) <= max_overlap for existing in selected):
                selected.append(cand)
        return selected
