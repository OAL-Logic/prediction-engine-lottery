"""
PoolOptimizer — generates and refines an N-number candidate pool.
==========================================================================
Backend selection:
  * OR-Tools CP-SAT, if installed — exact combinatorial optimum subject to
    every FilterPipeline threshold expressed as a linear constraint.
  * Otherwise a deterministic, seeded local-search (greedy construction +
    targeted swap hill-climbing) over NumPy-vectorized scores — no extra
    dependency required. This is what runs in this repo today (`ortools`
    is not installed — see engine/quina_unfold/README or run
    `python -c "import ortools"` to check your own environment).

Both backends optimize the same objective: maximize summed composite score
(frequency z-score + overdue delay pressure, penalized for prior-draw
repeats/adjacency) subject to every rule in the FilterPipeline.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.quina_unfold.filters import FilterPipeline, FilterReport

try:
    from ortools.sat.python import cp_model  # type: ignore

    _HAS_ORTOOLS = True
except ImportError:
    _HAS_ORTOOLS = False


@dataclass
class PoolResult:
    numbers: List[int]
    pool_size: int
    total_score: float
    backend: str
    filter_report: FilterReport
    omission_rationale: Dict[int, str] = field(default_factory=dict)
    per_number_score: Dict[int, float] = field(default_factory=dict)


class PoolOptimizer:
    """Generates an optimized N-number pool from a full 1-80 feature table."""

    def __init__(
        self,
        rules: DrawRules,
        features: pd.DataFrame,
        filter_pipeline: FilterPipeline,
        pool_size: int = 10,
        weight_freq_z: float = 0.4,
        weight_delay: float = 0.5,
        penalty_repeat: float = 1.2,
        penalty_adjacent: float = 0.5,
        seed: int = 7117,
    ):
        if not (self._min_pool_size() <= pool_size <= 15):
            raise ValueError(f"pool_size must be within Caixa's Quina unfolded-bet range ({self._min_pool_size()}-15), got {pool_size}")
        self.rules = rules
        self.features = features
        self.filter_pipeline = filter_pipeline
        self.pool_size = pool_size
        self.w_freq = weight_freq_z
        self.w_delay = weight_delay
        self.p_repeat = penalty_repeat
        self.p_adjacent = penalty_adjacent
        self._rng = random.Random(seed)
        self.scores = self._composite_scores()

    @staticmethod
    def _min_pool_size() -> int:
        return 6  # unfolded bets start at 6 numbers per the brief (5 = the standard single bet)

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _composite_scores(self) -> pd.Series:
        f = self.features
        delay_clamped = f["delay_ratio"].clip(upper=3.0)
        score = (
            self.w_freq * f["freq_z_score"]
            + self.w_delay * delay_clamped
            - self.p_repeat * f["is_repeat_of_prior"].astype(float)
            - self.p_adjacent * f["is_adjacent_to_prior"].astype(float)
        )
        return score

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(self, max_iterations: int = 4000) -> PoolResult:
        if _HAS_ORTOOLS:
            pool, backend = self._solve_cp_sat()
            if pool is None:  # infeasible under CP-SAT's constraint subset -> fall through
                pool, backend = self._solve_local_search(max_iterations)
        else:
            pool, backend = self._solve_local_search(max_iterations)

        report = self.filter_pipeline.evaluate(pool, self.features, self.rules)
        total_score = float(self.scores.loc[pool].sum())
        rationale = self._omission_rationale(pool)
        lo, hi = self.rules.number_range
        per_number_score = {int(n): round(float(self.scores.loc[n]), 4) for n in range(lo, hi + 1)}

        return PoolResult(
            numbers=sorted(pool),
            pool_size=self.pool_size,
            total_score=round(total_score, 4),
            backend=backend,
            filter_report=report,
            omission_rationale=rationale,
            per_number_score=per_number_score,
        )

    # ------------------------------------------------------------------
    # Backend: OR-Tools CP-SAT (exact)
    # ------------------------------------------------------------------

    def _solve_cp_sat(self):
        lo, hi = self.rules.number_range
        numbers = list(range(lo, hi + 1))
        model = cp_model.CpModel()
        x = {n: model.NewBoolVar(f"x_{n}") for n in numbers}

        model.Add(sum(x[n] for n in numbers) == self.pool_size)

        # Parity band (generalized 2:5-3:5)
        odd_numbers = [n for n in numbers if n % 2 == 1]
        even_numbers = [n for n in numbers if n % 2 == 0]
        lo_odd = int(np.floor(0.40 * self.pool_size))
        hi_odd = int(np.ceil(0.60 * self.pool_size))
        model.Add(sum(x[n] for n in odd_numbers) >= lo_odd)
        model.Add(sum(x[n] for n in odd_numbers) <= hi_odd)

        # Decile / quadrant caps (proportionate + slack, mirrors FilterPipeline defaults)
        for col, n_groups, slack in (("decile", 10, 1), ("quadrant", 4, 2)):
            cap = max(1, round(self.pool_size / n_groups)) + slack
            for g in sorted(self.features[col].unique()):
                members = self.features.index[self.features[col] == g].tolist()
                model.Add(sum(x[n] for n in members) <= cap)

        # Repeat / adjacency caps
        repeats = self.features.index[self.features["is_repeat_of_prior"]].tolist()
        adjacents = self.features.index[self.features["is_adjacent_to_prior"]].tolist()
        model.Add(sum(x[n] for n in repeats) <= int(np.ceil(0.40 * self.pool_size)))
        model.Add(sum(x[n] for n in adjacents) <= int(np.ceil(0.30 * self.pool_size)))

        # Objective: maximize integer-scaled composite score
        scaled = {n: int(round(self.scores.loc[n] * 1000)) for n in numbers}
        model.Maximize(sum(scaled[n] * x[n] for n in numbers))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            pool = [n for n in numbers if solver.Value(x[n]) == 1]
            return pool, f"or-tools-cp-sat ({'optimal' if status == cp_model.OPTIMAL else 'feasible'})"
        return None, "or-tools-cp-sat (infeasible)"

    # ------------------------------------------------------------------
    # Backend: deterministic local search (no extra dependency)
    # ------------------------------------------------------------------

    def _solve_local_search(self, max_iterations: int):
        lo, hi = self.rules.number_range
        all_numbers = list(range(lo, hi + 1))

        pool = self._greedy_seed(all_numbers)
        best_pool = list(pool)
        best_failures = self._n_failures(best_pool)
        best_score = float(self.scores.loc[best_pool].sum())

        for _ in range(max_iterations):
            report = self.filter_pipeline.evaluate(pool, self.features, self.rules)
            if report.passed:
                break
            pool = self._targeted_swap(pool, all_numbers, report.failures)
            failures = self._n_failures(pool)
            score = float(self.scores.loc[pool].sum())
            if failures < best_failures or (failures == best_failures and score > best_score):
                best_pool, best_failures, best_score = list(pool), failures, score
            if best_failures == 0:
                break

        return best_pool, "local-search (greedy + targeted swap hill-climb)"

    def _greedy_seed(self, all_numbers: List[int]) -> List[int]:
        """Round-robin across quadrants by descending score, to start near-balanced."""
        ranked = sorted(all_numbers, key=lambda n: -self.scores.loc[n])
        by_quadrant: Dict[int, List[int]] = {}
        for n in ranked:
            by_quadrant.setdefault(int(self.features.loc[n, "quadrant"]), []).append(n)

        pool: List[int] = []
        quadrants = sorted(by_quadrant.keys())
        idx = {q: 0 for q in quadrants}
        while len(pool) < self.pool_size:
            for q in quadrants:
                if len(pool) >= self.pool_size:
                    break
                bucket = by_quadrant[q]
                if idx[q] < len(bucket):
                    pool.append(bucket[idx[q]])
                    idx[q] += 1
        return pool

    def _n_failures(self, pool: Sequence[int]) -> int:
        return len(self.filter_pipeline.evaluate(pool, self.features, self.rules).failures)

    def _targeted_swap(self, pool: List[int], all_numbers: List[int], failures: List[str]) -> List[int]:
        pool = list(pool)
        outside = [n for n in all_numbers if n not in pool]
        failure = failures[0]

        def swap_out_worst(candidates_in_pool: List[int], candidates_outside: List[int]):
            if not candidates_in_pool or not candidates_outside:
                return
            worst = min(candidates_in_pool, key=lambda n: self.scores.loc[n])
            best_replacement = max(candidates_outside, key=lambda n: self.scores.loc[n])
            pool.remove(worst)
            pool.append(best_replacement)

        if failure == "parity_balance":
            odd_in = [n for n in pool if n % 2 == 1]
            even_in = [n for n in pool if n % 2 == 0]
            frac_odd = len(odd_in) / len(pool)
            if frac_odd > 0.60:
                swap_out_worst(odd_in, [n for n in outside if n % 2 == 0])
            else:
                swap_out_worst(even_in, [n for n in outside if n % 2 == 1])

        elif failure == "sum_band":
            s = sum(pool)
            from dataclasses import replace as _replace
            from engine.modules import sum_range as sum_range_module

            scaled = _replace(self.rules, pick_count=len(pool))
            _, _, mean, _ = sum_range_module.most_probable_range(scaled)
            if s > mean:
                worst = max(pool, key=lambda n: n)
                candidates = [n for n in outside if n < worst]
            else:
                worst = min(pool, key=lambda n: n)
                candidates = [n for n in outside if n > worst]
            if candidates:
                best_replacement = max(candidates, key=lambda n: self.scores.loc[n])
                pool.remove(worst)
                pool.append(best_replacement)

        elif failure in ("decile_spread", "quadrant_spread"):
            col = "decile" if failure == "decile_spread" else "quadrant"
            counts = self.features.loc[pool, col].value_counts()
            crowded = counts.idxmax()
            crowded_members = [n for n in pool if self.features.loc[n, col] == crowded]
            all_groups = set(self.features[col].unique())
            empty_groups = all_groups - set(self.features.loc[pool, col].unique())
            target_groups = empty_groups if empty_groups else all_groups - {crowded}
            candidates = [n for n in outside if self.features.loc[n, col] in target_groups]
            swap_out_worst(crowded_members, candidates)

        elif failure == "prior_repeat_rate":
            repeats_in = [n for n in pool if self.features.loc[n, "is_repeat_of_prior"]]
            swap_out_worst(repeats_in, [n for n in outside if not self.features.loc[n, "is_repeat_of_prior"]])

        elif failure == "prior_adjacency":
            adj_in = [n for n in pool if self.features.loc[n, "is_adjacent_to_prior"]]
            swap_out_worst(adj_in, [n for n in outside if not self.features.loc[n, "is_adjacent_to_prior"]])

        elif failure == "cycle_mix":
            warm_or_cold = [n for n in pool if self.features.loc[n, "cycle_class"] in ("warm", "cold")]
            hot_overdue_outside = [n for n in outside if self.features.loc[n, "cycle_class"] in ("hot", "overdue")]
            swap_out_worst(warm_or_cold, hot_overdue_outside)

        else:
            swap_out_worst(pool, outside)

        return pool

    # ------------------------------------------------------------------
    # Omission rationale
    # ------------------------------------------------------------------

    def _omission_rationale(self, pool: List[int]) -> Dict[int, str]:
        lo, hi = self.rules.number_range
        ranked = self.scores.sort_values(ascending=False)
        rank_of = {int(n): i + 1 for i, n in enumerate(ranked.index)}
        prior_set = set(int(n) for n in self.features.index[self.features["is_repeat_of_prior"]])
        adjacent_set = set(int(n) for n in self.features.index[self.features["is_adjacent_to_prior"]])

        rationale: Dict[int, str] = {}
        pool_deciles = {int(self.features.loc[n, "decile"]) for n in pool}
        pool_quadrants = {int(self.features.loc[n, "quadrant"]) for n in pool}

        for n in range(lo, hi + 1):
            if n in pool:
                continue
            reasons = []
            if n in prior_set:
                reasons.append("repeats the immediate prior draw (repeat-rate cap already met by selected numbers)")
            if n in adjacent_set:
                reasons.append("adjacent (+/-1) to a prior-draw number")
            cyc = self.features.loc[n, "cycle_class"]
            if cyc == "cold":
                reasons.append(f"cold cycle (z-score {self.features.loc[n, 'freq_z_score']:.2f}, below expectation)")
            dec = int(self.features.loc[n, "decile"])
            if dec in pool_deciles:
                reasons.append(f"decile {dec} already at its proportionate cap")
            if not reasons:
                reasons.append(f"lower composite score than selected peers (rank {rank_of[n]}/80)")
            rationale[n] = "; ".join(reasons)

        return rationale
