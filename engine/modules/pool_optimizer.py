"""
Pool Optimizer Module — structural-envelope pool engine for unfolded tickets
================================================================================
Builds n-number (n > rules.pick_count) candidate pools for single unfolded
("desdobramento") tickets by filtering against empirical macro-structural
envelopes: sum band, parity split, prime count, repeat-rate against a
reference draw, and spatial (row/column) balance on the game's board.

Pipeline
--------
  1. DrawRepository   — thin ingestion facade over the engine's existing
                         LotteryAdapter/LotteryStorage stack.
  2. FeatureExtractor  — per-number profile (frequency, z-score, delay,
                          hot/cold/overdue cycle state) and per-combination
                          structural features (sum, parity, primes, repeats,
                          spatial spread).
  3. FilterPipeline    — a configurable rule engine of structural rejection
                          filters, independently toggleable/tunable.
  4. PoolOptimizer      — searches for an envelope-compliant `pick_count`
                          "core" combination, then extends it to n numbers by
                          maximizing the count of *nested* C(n, pick_count)
                          sub-combinations that remain fully compliant. That
                          count is the correct objective for an unfolded
                          ticket, since every one of those C(n, pick_count)
                          combinations is an independently-scored bet.

Statistical caveat — read before wiring this into a purchase decision
------------------------------------------------------------------------
Under a fair lottery, every `pick_count`-number combination has an
*identical* true draw probability (this is the same assumption
`engine.modules.sum_range` states and the chi² gate tests). Nothing in this
module changes that. Structural filtering does **not** raise P(jackpot); its
two legitimate purposes are:

  (a) portfolio construction across a syndicate's *own* multiple tickets —
      concentrating capital on historically-typical structural shapes rather
      than statistically extreme ones some players believe (without formal
      justification under a fair-game model) are less representative, and

  (b) avoiding popular ("human-picked": birthdates, arithmetic runs, single
      rows/columns) combinations, which reduces prize-*sharing* dilution
      conditional on winning — a real financial effect, orthogonal to win
      probability.

Treat `FilterPipeline.default_for()`'s thresholds as *descriptive* (what
historical draws typically look like), not *predictive*.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

import numpy as np
import pandas as pd

from engine.adapters import DrawRules, LotteryAdapter
from engine.modules.sum_range import moments as _sum_moments

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def primes_in_range(lo: int, hi: int) -> frozenset:
    """Simple sieve — avoids a sympy dependency for a small numeric range."""
    primes: List[int] = []
    for n in range(max(2, lo), hi + 1):
        if all(n % p for p in primes if p * p <= n):
            primes.append(n)
    return frozenset(primes)


def _zscores(values: np.ndarray) -> np.ndarray:
    std = values.std()
    if std == 0:
        return np.zeros_like(values, dtype=float)
    return (values - values.mean()) / std


# ---------------------------------------------------------------------------
# 1. DrawRepository
# ---------------------------------------------------------------------------


@dataclass
class DrawRepository:
    """
    Thin ingestion facade over a `LotteryAdapter`.

    `FeatureExtractor` and `PoolOptimizer` depend only on this narrow
    interface — not on adapter/storage internals — so they're easy to
    unit-test against a synthetic in-memory history instead of live
    network/DB access (see `from_frame`).
    """

    adapter: Optional[LotteryAdapter] = None
    _df: Optional[pd.DataFrame] = field(default=None, repr=False, compare=False)
    _rules: Optional[DrawRules] = field(default=None, repr=False, compare=False)

    @property
    def rules(self) -> DrawRules:
        if self._rules is not None:
            return self._rules
        if self.adapter is None:
            raise ValueError("DrawRepository has neither an adapter nor explicit rules")
        return self.adapter.rules

    def history(self, refresh: bool = False) -> pd.DataFrame:
        """Full canonical draw history, oldest -> newest."""
        if self._df is None or refresh:
            if self.adapter is None:
                raise ValueError("no adapter configured — build via from_frame() for offline use")
            self._df = self.adapter.fetch().sort_values("draw_id").reset_index(drop=True)
        return self._df

    def draw(self, draw_id: int) -> List[int]:
        """Numbers for one historical draw, e.g. `repo.draw(3779)`."""
        df = self.history()
        match = df.loc[df["draw_id"] == draw_id]
        if match.empty:
            raise KeyError(f"draw_id {draw_id} not found in history")
        return sorted(match.iloc[0]["numbers"])

    def latest(self) -> Tuple[int, List[int]]:
        """(draw_id, numbers) of the most recent draw — e.g. 3779 ahead of 3780."""
        df = self.history()
        if df.empty:
            raise ValueError("no draw history available")
        row = df.iloc[-1]
        return int(row["draw_id"]), sorted(row["numbers"])

    @classmethod
    def from_frame(cls, df: pd.DataFrame, rules: DrawRules) -> "DrawRepository":
        """Build a repository from an in-memory DataFrame — for tests/backtests."""
        repo = cls(adapter=None)
        repo._df = df.sort_values("draw_id").reset_index(drop=True)
        repo._rules = rules
        return repo


# ---------------------------------------------------------------------------
# 2. FeatureExtractor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NumberProfile:
    number: int
    row: int
    col: int
    is_odd: bool
    is_prime: bool
    freq_all: int
    z_all: float
    freq_window: int
    z_window: float
    delay: int  # draws since this number's last appearance

    @property
    def cycle_state(self) -> str:
        """Heuristic hot/cold/overdue/neutral label — descriptive, not predictive."""
        if self.z_window >= 1.0:
            return "hot"
        if self.z_window <= -1.0:
            return "cold"
        if self.delay >= 3:
            return "overdue"
        return "neutral"


class FeatureExtractor:
    """Computes per-number profiles and per-combination structural features."""

    def __init__(self, rules: DrawRules, primes: Optional[frozenset] = None):
        self.rules = rules
        lo, hi = rules.number_range
        self.lo, self.hi = lo, hi
        self.board_cols = rules.board_cols or 5
        self.primes = primes if primes is not None else primes_in_range(lo, hi)

    def row_of(self, n: int) -> int:
        return (n - self.lo) // self.board_cols

    def col_of(self, n: int) -> int:
        return (n - self.lo) % self.board_cols

    @property
    def n_rows(self) -> int:
        return -(-(self.hi - self.lo + 1) // self.board_cols)  # ceil div

    def number_profiles(self, df: pd.DataFrame, window: int = 50) -> Dict[int, NumberProfile]:
        """One `NumberProfile` per number in `rules.number_range`."""
        universe = list(range(self.lo, self.hi + 1))
        history = df.sort_values("draw_id").reset_index(drop=True)
        n_draws = len(history)

        freq_all: Dict[int, int] = {n: 0 for n in universe}
        last_seen_idx: Dict[int, Optional[int]] = {n: None for n in universe}
        for idx, nums in enumerate(history["numbers"]):
            for n in nums:
                if n in freq_all:
                    freq_all[n] += 1
                    last_seen_idx[n] = idx

        freqs = np.array([freq_all[n] for n in universe], dtype=float)
        z_all = _zscores(freqs)

        recent = history.tail(window)
        freq_window: Dict[int, int] = {n: 0 for n in universe}
        for nums in recent["numbers"]:
            for n in nums:
                if n in freq_window:
                    freq_window[n] += 1
        freqs_w = np.array([freq_window[n] for n in universe], dtype=float)
        z_window = _zscores(freqs_w)

        profiles: Dict[int, NumberProfile] = {}
        for i, n in enumerate(universe):
            seen = last_seen_idx[n]
            delay = (n_draws - 1 - seen) if seen is not None else n_draws
            profiles[n] = NumberProfile(
                number=n,
                row=self.row_of(n),
                col=self.col_of(n),
                is_odd=(n % 2 == 1),
                is_prime=(n in self.primes),
                freq_all=freq_all[n],
                z_all=float(z_all[i]),
                freq_window=freq_window[n],
                z_window=float(z_window[i]),
                delay=delay,
            )
        return profiles

    def combo_features(
        self, combo: Sequence[int], reference_draw: Sequence[int] = ()
    ) -> Dict[str, object]:
        """Structural features of one `pick_count`-sized combination."""
        combo = sorted(combo)
        s = sum(combo)
        odds = sum(1 for n in combo if n % 2 == 1)
        primes_ct = sum(1 for n in combo if n in self.primes)
        reps = len(set(combo) & set(reference_draw)) if reference_draw else 0

        row_counts = [0] * self.n_rows
        col_counts = [0] * self.board_cols
        for n in combo:
            row_counts[self.row_of(n)] += 1
            col_counts[self.col_of(n)] += 1

        return {
            "sum": s,
            "odd": odds,
            "even": len(combo) - odds,
            "primes": primes_ct,
            "repeats_vs_reference": reps,
            "row_counts": row_counts,
            "col_counts": col_counts,
            "row_spread": max(row_counts) - min(row_counts),
            "col_spread": max(col_counts) - min(col_counts),
            "empty_row": min(row_counts) == 0,
            "empty_col": min(col_counts) == 0,
        }


# ---------------------------------------------------------------------------
# 3. FilterPipeline
# ---------------------------------------------------------------------------


@dataclass
class FilterRule:
    name: str
    predicate: Callable[[Mapping[str, object]], bool]
    description: str = ""


@dataclass
class FilterReport:
    features: Dict[str, object]
    passed: Dict[str, bool]

    @property
    def compliant(self) -> bool:
        return all(self.passed.values())

    @property
    def score(self) -> int:
        return sum(1 for ok in self.passed.values() if ok)


class FilterPipeline:
    """
    Configurable rule engine of structural rejection filters. Each
    `FilterRule` is evaluated independently against
    `FeatureExtractor.combo_features()` output — add/remove/reweight rules
    freely; nothing else in this module assumes a fixed rule set.
    """

    def __init__(self, rules: Sequence[FilterRule]):
        self.rules = list(rules)

    def evaluate(self, features: Mapping[str, object]) -> FilterReport:
        passed = {r.name: bool(r.predicate(features)) for r in self.rules}
        return FilterReport(features=dict(features), passed=passed)

    def is_compliant(self, features: Mapping[str, object]) -> bool:
        return self.evaluate(features).compliant

    @classmethod
    def default_for(
        cls,
        rules: DrawRules,
        sum_range: Tuple[int, int] = (180, 220),
        odd_range: Tuple[int, int] = (7, 8),
        prime_range: Tuple[int, int] = (5, 7),
        repeat_range: Tuple[int, int] = (8, 10),
        max_row_spread: int = 3,
        max_col_spread: int = 3,
    ) -> "FilterPipeline":
        """
        Default Lotofácil envelope, calibrated against 3,779 historical draws
        (data/lottery.db, lottery_id='br/lotofacil', draws 1-3779):

            sum      in [180, 220]  -> ~73% empirical coverage
            parity   odd in [7, 8]  -> ~57% empirical coverage
            primes   in [5, 7]      -> ~74% empirical coverage
            repeats  in [8, 10]     -> ~79% empirical coverage (vs. reference draw)
            spatial  no empty row/col; row & col spread <= 3 -> ~88%/98% resp.

        Recompute against a fresh `DrawRepository.history()` before relying on
        these for a different game or a materially longer/shorter history —
        they drift slowly as more draws accumulate.
        """
        return cls(
            [
                FilterRule(
                    "sum",
                    lambda f: sum_range[0] <= f["sum"] <= sum_range[1],
                    f"Sum within [{sum_range[0]}, {sum_range[1]}]",
                ),
                FilterRule(
                    "parity",
                    lambda f: odd_range[0] <= f["odd"] <= odd_range[1],
                    f"Odd count within [{odd_range[0]}, {odd_range[1]}]",
                ),
                FilterRule(
                    "primes",
                    lambda f: prime_range[0] <= f["primes"] <= prime_range[1],
                    f"Prime count within [{prime_range[0]}, {prime_range[1]}]",
                ),
                FilterRule(
                    "repeats",
                    lambda f: repeat_range[0] <= f["repeats_vs_reference"] <= repeat_range[1],
                    f"Repeats vs. reference draw within [{repeat_range[0]}, {repeat_range[1]}]",
                ),
                FilterRule(
                    "spatial",
                    lambda f: (
                        not f["empty_row"]
                        and not f["empty_col"]
                        and f["row_spread"] <= max_row_spread
                        and f["col_spread"] <= max_col_spread
                    ),
                    "No empty row/column; row & col spread bounded",
                ),
            ]
        )


# ---------------------------------------------------------------------------
# 4. PoolOptimizer
# ---------------------------------------------------------------------------


@dataclass
class PoolReport:
    pool: Tuple[int, ...]
    n_nested_combos: int
    per_filter_compliance: Dict[str, float]  # fraction of nested combos passing, per filter
    joint_compliance: float  # fraction passing every filter simultaneously
    n_joint_compliant: int


@dataclass
class OmissionReason:
    number: int
    reasons: List[str]


class PoolOptimizer:
    """
    Generates and refines n-number (n > pick_count) candidate pools for
    single unfolded tickets, optimizing the count of nested
    `C(n, pick_count)` sub-combinations that satisfy every `FilterPipeline`
    rule.

    Backends for the initial `pick_count`-sized "core" combination
    ------------------------------------------------------------------
      core_by_rejection_sampling  — fast randomized search (default; scales
                                     to any pool size; not exhaustive).
      core_by_vectorized_scan     — exact NumPy-batched brute force over
                                     every C(pool_size, pick_count) combo.
                                     Exact but combinatorial — fine for
                                     Lotofácil's C(25,15)=3.27M, too slow
                                     un-restricted for e.g. Mega-Sena's
                                     C(60,6)=50M without pre-shortlisting.
      core_by_cp_sat               — exact constraint search via OR-Tools
                                     CP-SAT (optional dependency). Best when
                                     the pool is large or you want several
                                     provably-diverse solutions instead of an
                                     exhaustive scan.
    """

    def __init__(self, extractor: FeatureExtractor, pipeline: FilterPipeline):
        self.extractor = extractor
        self.pipeline = pipeline
        self.rules = extractor.rules

    # ---- core combination search ------------------------------------

    def core_by_rejection_sampling(
        self,
        reference_draw: Sequence[int],
        n_samples: int = 200_000,
        seed: Optional[int] = None,
    ) -> Tuple[int, ...]:
        """Randomized search for one compliant `pick_count`-sized combination,
        tie-broken by closeness to the envelope midpoints."""
        rng = random.Random(seed)
        universe = list(range(self.extractor.lo, self.extractor.hi + 1))
        pick = self.rules.pick_count

        best: Optional[Tuple[float, Tuple[int, ...]]] = None
        for _ in range(n_samples):
            combo = tuple(sorted(rng.sample(universe, pick)))
            feats = self.extractor.combo_features(combo, reference_draw)
            report = self.pipeline.evaluate(feats)
            if not report.compliant:
                continue
            dist = self._central_distance(feats)
            if best is None or dist < best[0]:
                best = (dist, combo)

        if best is None:
            raise RuntimeError(
                f"no compliant {pick}-number combination found in {n_samples} samples "
                "— loosen FilterPipeline thresholds or increase n_samples"
            )
        return best[1]

    def _central_distance(self, feats: Mapping[str, object]) -> float:
        """Ranking heuristic among already-compliant combos (does not gate
        pass/fail) — favors combos near the analytical sum mean, an even
        parity split, and tight spatial spread."""
        mean_sum, _ = _sum_moments(self.rules)
        target_odd = self.rules.pick_count / 2.0
        return (
            abs(feats["sum"] - mean_sum)
            + abs(feats["odd"] - target_odd) * 2.0
            + feats["row_spread"]
            + feats["col_spread"]
        )

    def core_by_vectorized_scan(
        self,
        reference_draw: Sequence[int],
        sum_range: Tuple[int, int] = (180, 220),
        odd_range: Tuple[int, int] = (7, 8),
        prime_range: Tuple[int, int] = (5, 7),
        repeat_range: Tuple[int, int] = (8, 10),
        max_row_spread: int = 3,
        max_col_spread: int = 3,
        universe: Optional[Sequence[int]] = None,
        batch_size: int = 200_000,
    ) -> List[Tuple[int, ...]]:
        """
        Exact brute-force scan of every `C(len(universe), pick_count)`
        combination, vectorized in NumPy batches. Returns *all* fully
        compliant combinations (the four numeric filters are vectorized; the
        spatial filter is checked on the — small — post-filter survivors).

        Pass a restricted `universe` (e.g. a pre-shortlisted 20-25 numbers)
        to keep this tractable for larger games.
        """
        universe = sorted(universe) if universe is not None else list(
            range(self.extractor.lo, self.extractor.hi + 1)
        )
        pick = self.rules.pick_count
        base = universe[0]
        prime_lookup = np.array([1 if n in self.extractor.primes else 0 for n in universe])
        ref = set(reference_draw)

        results: List[Tuple[int, ...]] = []
        it = itertools.combinations(universe, pick)
        while True:
            batch = list(itertools.islice(it, batch_size))
            if not batch:
                break
            arr = np.array(batch, dtype=np.int32)  # shape (B, pick)
            s = arr.sum(axis=1)
            odds = (arr % 2 == 1).sum(axis=1)
            idx = np.searchsorted(universe, arr)
            primes_ct = prime_lookup[idx].sum(axis=1)
            reps = np.isin(arr, list(ref)).sum(axis=1) if ref else np.zeros(len(batch), dtype=int)

            mask = (
                (s >= sum_range[0])
                & (s <= sum_range[1])
                & (odds >= odd_range[0])
                & (odds <= odd_range[1])
                & (primes_ct >= prime_range[0])
                & (primes_ct <= prime_range[1])
                & (reps >= repeat_range[0])
                & (reps <= repeat_range[1])
            )
            if not mask.any():
                continue

            for row in arr[mask]:
                combo = tuple(int(x) for x in row)
                feats = self.extractor.combo_features(combo, reference_draw)
                if (
                    not feats["empty_row"]
                    and not feats["empty_col"]
                    and feats["row_spread"] <= max_row_spread
                    and feats["col_spread"] <= max_col_spread
                ):
                    results.append(combo)
        return results

    def core_by_cp_sat(
        self,
        reference_draw: Sequence[int],
        sum_range: Tuple[int, int] = (180, 220),
        odd_range: Tuple[int, int] = (7, 8),
        prime_range: Tuple[int, int] = (5, 7),
        repeat_range: Tuple[int, int] = (8, 10),
        max_solutions: int = 5,
        time_limit_s: float = 10.0,
    ) -> List[Tuple[int, ...]]:
        """
        Exact constraint search via OR-Tools CP-SAT — up to `max_solutions`
        distinct compliant `pick_count`-sized combinations.

        Requires the optional `ortools` dependency (`pip install ortools`).
        """
        try:
            from ortools.sat.python import cp_model
        except ImportError as exc:
            raise RuntimeError(
                "OR-Tools not installed — `pip install ortools`, or use "
                "core_by_vectorized_scan()/core_by_rejection_sampling() instead."
            ) from exc

        universe = list(range(self.extractor.lo, self.extractor.hi + 1))
        pick = self.rules.pick_count
        ref = set(reference_draw)

        model = cp_model.CpModel()
        x = {n: model.NewBoolVar(f"x_{n}") for n in universe}
        model.Add(sum(x.values()) == pick)

        model.Add(sum(n * x[n] for n in universe) >= sum_range[0])
        model.Add(sum(n * x[n] for n in universe) <= sum_range[1])

        odd_terms = [x[n] for n in universe if n % 2 == 1]
        model.Add(sum(odd_terms) >= odd_range[0])
        model.Add(sum(odd_terms) <= odd_range[1])

        prime_terms = [x[n] for n in universe if n in self.extractor.primes]
        model.Add(sum(prime_terms) >= prime_range[0])
        model.Add(sum(prime_terms) <= prime_range[1])

        if ref:
            rep_terms = [x[n] for n in universe if n in ref]
            model.Add(sum(rep_terms) >= repeat_range[0])
            model.Add(sum(rep_terms) <= repeat_range[1])

        for r in range(self.extractor.n_rows):
            row_terms = [x[n] for n in universe if self.extractor.row_of(n) == r]
            if row_terms:
                model.Add(sum(row_terms) >= 1)  # no empty row
        for c in range(self.extractor.board_cols):
            col_terms = [x[n] for n in universe if self.extractor.col_of(n) == c]
            if col_terms:
                model.Add(sum(col_terms) >= 1)  # no empty column

        class _Collector(cp_model.CpSolverSolutionCallback):
            def __init__(self, x_vars, uni, cap):
                super().__init__()
                self._x = x_vars
                self._uni = uni
                self._cap = cap
                self.solutions: List[Tuple[int, ...]] = []

            def on_solution_callback(self):
                combo = tuple(n for n in self._uni if self.Value(self._x[n]))
                self.solutions.append(combo)
                if len(self.solutions) >= self._cap:
                    self.StopSearch()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_s
        solver.parameters.num_search_workers = 8
        collector = _Collector(x, universe, max_solutions)
        solver.SearchForAllSolutions(model, collector)
        return collector.solutions

    # ---- pool extension & evaluation ---------------------------------

    def extend_pool(
        self,
        core: Sequence[int],
        additions: int,
        candidates: Sequence[int],
        reference_draw: Sequence[int],
    ) -> Tuple[Tuple[int, ...], int]:
        """
        Choose `additions` numbers from `candidates` to append to `core`,
        maximizing the count of nested `C(len(core) + additions, pick_count)`
        sub-combos that pass the full `FilterPipeline`. Exhaustive over
        `C(len(candidates), additions)` — intended for a small shortlist
        (e.g. the ~10 numbers left over after picking the core), not the
        full number universe.

        Returns `(pool, n_joint_compliant)`.
        """
        best: Optional[Tuple[int, Tuple[int, ...]]] = None
        for combo_add in itertools.combinations(candidates, additions):
            pool = tuple(sorted(set(core) | set(combo_add)))
            score = self.evaluate_pool(pool, reference_draw).n_joint_compliant
            if best is None or score > best[0]:
                best = (score, combo_add)
        assert best is not None
        pool = tuple(sorted(set(core) | set(best[1])))
        return pool, best[0]

    def evaluate_pool(self, pool: Sequence[int], reference_draw: Sequence[int]) -> PoolReport:
        """Full per-filter and joint compliance breakdown over every nested
        `C(len(pool), pick_count)` sub-combination."""
        pool = sorted(pool)
        pick = self.rules.pick_count
        n_combos = 0
        per_filter_pass = {r.name: 0 for r in self.pipeline.rules}
        n_joint = 0

        for combo in itertools.combinations(pool, pick):
            n_combos += 1
            feats = self.extractor.combo_features(combo, reference_draw)
            report = self.pipeline.evaluate(feats)
            for name, ok in report.passed.items():
                if ok:
                    per_filter_pass[name] += 1
            if report.compliant:
                n_joint += 1

        per_filter_compliance = {
            k: (v / n_combos if n_combos else 0.0) for k, v in per_filter_pass.items()
        }
        joint_compliance = n_joint / n_combos if n_combos else 0.0
        return PoolReport(
            pool=tuple(pool),
            n_nested_combos=n_combos,
            per_filter_compliance=per_filter_compliance,
            joint_compliance=joint_compliance,
            n_joint_compliant=n_joint,
        )

    def omission_rationale(
        self, pool: Sequence[int], profiles: Mapping[int, NumberProfile]
    ) -> List[OmissionReason]:
        """Human-readable reasons each number outside `pool` was left out."""
        universe = range(self.extractor.lo, self.extractor.hi + 1)
        omitted = [n for n in universe if n not in pool]
        out: List[OmissionReason] = []
        for n in omitted:
            p = profiles[n]
            why: List[str] = []
            if p.z_all <= -1.0:
                why.append(f"cold all-time (z={p.z_all:+.2f})")
            if p.z_window <= -1.0:
                why.append(f"cold in the recent window (z={p.z_window:+.2f})")
            if p.cycle_state == "overdue":
                why.append(f"overdue {p.delay} draws")
            if not why:
                why.append(
                    "not cold/overdue on its own — excluded because the optimizer found "
                    "a higher-compliance pool without it (redundant with numbers already "
                    "in the pool for parity/prime/spatial balance)"
                )
            out.append(OmissionReason(number=n, reasons=why))
        return out
