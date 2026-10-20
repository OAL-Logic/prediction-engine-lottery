"""
Engine Bridge Service
=====================
Decoupled service layer connecting the PySide6 Cockpit application to the
underlying headless computational engine (`engine/`) and registry.
Provides full feature parity with Lottery Studio's 105+ filter catalog, Fault Tolerance
Engine, historical draw access, actual skips analytics, and covering wheel solver.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Optional, Generator, Tuple, Any, Set
import numpy as np
import pandas as pd
import itertools
from collections import Counter

from cockpit.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, ToleranceMode,
    WheelingConfig, WheelType, TicketReceipt, GenerationTelemetry
)
from engine.adapters.registry import registry, GameDefinition
from engine.adapters import GenericLotteryAdapter
from engine.modules.storage import storage

logger = logging.getLogger(__name__)

PRIMES_SET = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
PRIMES_ARRAY = np.array(sorted(list(PRIMES_SET)), dtype=int)

FIBONACCI_SET = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
FIBONACCI_ARRAY = np.array(sorted(list(FIBONACCI_SET)), dtype=int)

SQUARES_SET = {1, 4, 9, 16, 25, 36, 49, 64, 81}
SQUARES_ARRAY = np.array(sorted(list(SQUARES_SET)), dtype=int)


class EngineBridge:
    """
    Singleton bridge providing headless computational services to the desktop UI.
    Ensures complete independence of engine algorithms from GUI code.
    """

    _instance: Optional[EngineBridge] = None

    def __new__(cls) -> EngineBridge:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_bridge()
        return cls._instance

    def _init_bridge(self) -> None:
        self._games_cache: Dict[str, GameSchema] = {}
        self._draws_cache: Dict[str, pd.DataFrame] = {}
        self._load_registered_games()

    def _load_registered_games(self) -> None:
        """Loads and converts all registered games from engine/adapters/registry.py."""
        raw_games: List[GameDefinition] = registry.list_games(only_available=False)
        for g in raw_games:
            schema = GameSchema(
                id=g.id,
                name=g.name,
                pick_count=g.pick_count,
                pool_size=g.pool_size,
                number_range_min=g.pool_min if hasattr(g, "pool_min") else 1,
                bonus_count=g.bonus_count,
                bonus_pool=g.bonus_pool,
                ticket_price=g.ticket_price if hasattr(g, "ticket_price") else 3.0,
                currency=g.currency if hasattr(g, "currency") else ("BRL" if g.id.startswith("br/") else "USD"),
                draw_days=g.draw_days if hasattr(g, "draw_days") else [],
                board_cols=10 if g.pool_size > 30 else 5,
                data_available=g.data_available,
                draw_file=g.draw_file
            )
            self._games_cache[g.id] = schema
        logger.info("EngineBridge loaded %d games dynamically.", len(self._games_cache))

    def list_games(self) -> List[GameSchema]:
        """Returns sorted list of all active registered lottery game schemas."""
        return sorted(list(self._games_cache.values()), key=lambda x: (not x.id.startswith("br/"), x.name))

    def get_game(self, game_id: str) -> Optional[GameSchema]:
        """Retrieves game schema by unique game_id."""
        return self._games_cache.get(game_id)

    def get_draws(self, game_id: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches historical draws for game_id using engine storage or flat-file adapter.
        Caches full dataframe in memory for interactive chart slicing.
        """
        if game_id not in self._draws_cache:
            game_def = registry.get_game(game_id)
            if not game_def:
                return pd.DataFrame()
            adapter = GenericLotteryAdapter(game_def)
            df = adapter.fetch(limit=None)
            self._draws_cache[game_id] = df

        df = self._draws_cache[game_id]
        if limit is not None and not df.empty:
            return df.tail(limit).reset_index(drop=True)
        return df

    # -------------------------------------------------------------------------
    # Skips & Gaps Analytics Engine (Lottery Studio Parity)
    # -------------------------------------------------------------------------

    def compute_skips_analysis(self, game_id: str, target_number: int) -> Dict[str, Any]:
        """
        Calculates signature Lottery Studio skips metrics:
        - Actual Skips: Sequence of draw gaps between occurrences
        - Average Skip: Historical mean gap
        - Now Skip: Current draws elapsed since target_number last appeared
        - Gap Histogram: Frequency of each interval length
        """
        df = self.get_draws(game_id)
        if df.empty or "numbers" not in df.columns:
            return {
                "number": target_number, "actual_skips": [], "average_skip": 0.0,
                "now_skip": 0, "gap_histogram": {}, "total_hits": 0, "hit_rate_pct": 0.0
            }

        draw_lists = df["numbers"].tolist()
        hit_indices = [idx for idx, nums in enumerate(draw_lists) if target_number in nums]

        if not hit_indices:
            total_draws = len(draw_lists)
            return {
                "number": target_number, "actual_skips": [total_draws], "average_skip": float(total_draws),
                "now_skip": total_draws, "gap_histogram": {total_draws: 1}, "total_hits": 0, "hit_rate_pct": 0.0
            }

        skips: List[int] = []
        for i in range(1, len(hit_indices)):
            gap = hit_indices[i] - hit_indices[i - 1] - 1
            skips.append(gap)

        now_skip = (len(draw_lists) - 1) - hit_indices[-1]
        avg_skip = float(np.mean(skips)) if skips else float(now_skip)
        gap_hist = dict(Counter(skips))
        total_hits = len(hit_indices)
        hit_rate = (total_hits / len(draw_lists)) * 100.0

        return {
            "number": target_number,
            "actual_skips": skips,
            "average_skip": round(avg_skip, 2),
            "now_skip": now_skip,
            "gap_histogram": gap_hist,
            "total_hits": total_hits,
            "hit_rate_pct": round(hit_rate, 2)
        }

    def compute_auto_fit_ranges(
        self,
        game_id: str,
        filters: List[FilterNode],
        last_n_draws: int = 30
    ) -> Dict[str, Tuple[float, float]]:
        """
        Implements Lottery Studio's signature 'Auto-Generate Default Condition' feature.
        Scans the last N historical draws and determines observed min and max boundaries.
        """
        df = self.get_draws(game_id, limit=last_n_draws)
        if df.empty or "numbers" not in df.columns:
            return {}

        draws = df["numbers"].tolist()
        draws_arr = np.array(draws, dtype=np.uint8)
        game = self.get_game(game_id)
        k = draws_arr.shape[1]
        pool_max = int(np.max(draws_arr))
        mid = pool_max // 2

        fitted_ranges: Dict[str, Tuple[float, float]] = {}

        for flt in filters:
            fid = flt.id
            vals: List[float] = []

            if fid == "structural_odd_count":
                vals = np.sum(draws_arr % 2 != 0, axis=1).astype(float).tolist()
            elif fid == "structural_even_count":
                vals = np.sum(draws_arr % 2 == 0, axis=1).astype(float).tolist()
            elif fid == "structural_high_count":
                vals = np.sum(draws_arr > mid, axis=1).astype(float).tolist()
            elif fid == "structural_low_count":
                vals = np.sum(draws_arr <= mid, axis=1).astype(float).tolist()
            elif fid == "structural_prime_count":
                vals = np.sum(np.isin(draws_arr, PRIMES_ARRAY), axis=1).astype(float).tolist()
            elif fid == "structural_composite_count":
                comps = (~np.isin(draws_arr, PRIMES_ARRAY)) & (draws_arr > 1)
                vals = np.sum(comps, axis=1).astype(float).tolist()
            elif fid == "structural_fibonacci_count":
                vals = np.sum(np.isin(draws_arr, FIBONACCI_ARRAY), axis=1).astype(float).tolist()
            elif fid == "structural_square_count":
                vals = np.sum(np.isin(draws_arr, SQUARES_ARRAY), axis=1).astype(float).tolist()
            elif fid in ("structural_number_sum", "arithmetic_number_sum"):
                vals = np.sum(draws_arr, axis=1).astype(float).tolist()
            elif fid in ("structural_avg_value", "arithmetic_avg_value"):
                vals = (np.sum(draws_arr, axis=1) // k).astype(float).tolist()
            elif fid in ("structural_unit_sum", "arithmetic_unit_sum"):
                vals = np.sum(draws_arr % 10, axis=1).astype(float).tolist()
            elif fid == "arithmetic_even_sum":
                vals = np.sum(np.where(draws_arr % 2 == 0, draws_arr, 0), axis=1).astype(float).tolist()
            elif fid == "arithmetic_odd_sum":
                vals = np.sum(np.where(draws_arr % 2 != 0, draws_arr, 0), axis=1).astype(float).tolist()
            elif fid == "arithmetic_prime_sum":
                vals = np.sum(np.where(np.isin(draws_arr, PRIMES_ARRAY), draws_arr, 0), axis=1).astype(float).tolist()
            elif fid == "arithmetic_digit_sum":
                vals = np.sum((draws_arr // 10) + (draws_arr % 10), axis=1).astype(float).tolist()
            elif fid == "positional_min_number":
                vals = draws_arr[:, 0].astype(float).tolist()
            elif fid == "positional_max_number":
                vals = draws_arr[:, -1].astype(float).tolist()
            elif fid == "positional_first_last_dist":
                vals = (draws_arr[:, -1].astype(int) - draws_arr[:, 0].astype(int)).astype(float).tolist()
            elif fid == "positional_max_distance":
                diffs = np.diff(draws_arr.astype(int), axis=1)
                vals = np.max(diffs, axis=1).astype(float).tolist()
            elif fid == "positional_min_distance":
                diffs = np.diff(draws_arr.astype(int), axis=1)
                vals = np.min(diffs, axis=1).astype(float).tolist()
            elif fid == "structural_ac_value":
                ac_list = []
                for d in draws:
                    diff_set = set()
                    sd = sorted(d)
                    for i in range(len(sd)):
                        for j in range(i + 1, len(sd)):
                            diff_set.add(sd[j] - sd[i])
                    ac_list.append(float(len(diff_set) - (len(sd) - 1)))
                vals = ac_list
            elif fid.startswith("algebraic_div_by_"):
                try:
                    div = int(fid.split("_")[3])
                    vals = np.sum(draws_arr % div == 0, axis=1).astype(float).tolist()
                except (IndexError, ValueError):
                    vals = []
            elif fid in ("arithmetic_root_sum", "structural_root_sum"):
                sums = np.sum(draws_arr, axis=1)
                vals = (1 + (sums - 1) % 9).astype(float).tolist()
            elif fid.startswith("decades_decade_"):
                try:
                    d_idx = int(fid.split("_")[2])
                    d_start = d_idx * 10
                    d_end = d_start + 9
                    vals = np.sum((draws_arr >= d_start) & (draws_arr <= d_end), axis=1).astype(float).tolist()
                except (IndexError, ValueError):
                    vals = []
            elif fid == "decades_different_decades":
                dec_counts = []
                for d in draws:
                    dec_counts.append(float(len(set(num // 10 for num in d))))
                vals = dec_counts

            if vals:
                min_v = float(np.min(vals))
                max_v = float(np.max(vals))
                fitted_ranges[fid] = (min_v, max_v)

        return fitted_ranges

    # -------------------------------------------------------------------------
    # Exhaustive 105+ Filter Catalog across 7 Categories (Lottery Studio Parity)
    # -------------------------------------------------------------------------

    def load_catalog_filters(self, game: Optional[GameSchema] = None) -> List[FilterNode]:
        """
        Loads the exhaustive 105+ filter catalog reverse-engineered from Lottery Studio:
        1. Structural / Count (Tags 1-5, plus composite, square, fibonacci, ratios)
        2. Sums & Averages (Tags 6-11, 41, 68-69, digit sum, even/odd/prime sums, means)
        3. Positional & Distance (Tags 12-19, min/max, adjacent gaps, ball ranges, spread)
        4. Complexity & Repeats (Tags 20-21, overdue hits, cold numbers, repeats, pairs)
        5. Algebraic Residue & Modulo (Divided by 3..20, modulo 3/4/5 distributions)
        6. Decades & Units (Tags 44, 46-47, decades 0-6, unit distinct count, unit sum parity)
        7. Advanced & Sets (Tags 24-28, 38-40, successive multi-run, partitions, custom groups)
        """
        k = game.pick_count if game else 15
        M = game.pool_size if game else 25
        mid = M // 2

        filters: List[FilterNode] = [
            # ── 1. Structural / Count (10 Filters) ──────────────────────────
            FilterNode(
                id="structural_odd_count", name="Odd Count", category="Structural / Count",
                description="Number of odd balls in line (Tag 1)",
                min_val=max(1, int(k * 0.35)), max_val=min(k, int(k * 0.65)),
                default_min=max(1, int(k * 0.35)), default_max=min(k, int(k * 0.65)),
                tags=["count", "parity", "tag:1"], enabled=False
            ),
            FilterNode(
                id="structural_even_count", name="Even Count", category="Structural / Count",
                description="Number of even balls in line (Tag 2)",
                min_val=max(1, int(k * 0.35)), max_val=min(k, int(k * 0.65)),
                default_min=max(1, int(k * 0.35)), default_max=min(k, int(k * 0.65)),
                tags=["count", "parity", "tag:2"], enabled=False
            ),
            FilterNode(
                id="structural_high_count", name="High Count", category="Structural / Count",
                description=f"Count of numbers > {mid} (Tag 3)",
                min_val=max(1, int(k * 0.35)), max_val=min(k, int(k * 0.65)),
                default_min=max(1, int(k * 0.35)), default_max=min(k, int(k * 0.65)),
                tags=["count", "range", "tag:3"], enabled=False
            ),
            FilterNode(
                id="structural_low_count", name="Low Count", category="Structural / Count",
                description=f"Count of numbers <= {mid} (Tag 4)",
                min_val=max(1, int(k * 0.35)), max_val=min(k, int(k * 0.65)),
                default_min=max(1, int(k * 0.35)), default_max=min(k, int(k * 0.65)),
                tags=["count", "range", "tag:4"], enabled=False
            ),
            FilterNode(
                id="structural_prime_count", name="Prime Count", category="Structural / Count",
                description="Count of prime numbers in line (Tag 5)",
                min_val=max(1, int(k * 0.2)), max_val=min(k, int(k * 0.6)),
                default_min=max(1, int(k * 0.2)), default_max=min(k, int(k * 0.6)),
                tags=["count", "primes", "tag:5"], enabled=False
            ),
            FilterNode(
                id="structural_composite_count", name="Composite Count", category="Structural / Count",
                description="Count of composite non-prime numbers (> 1)",
                min_val=max(1, int(k * 0.3)), max_val=min(k, int(k * 0.8)),
                default_min=max(1, int(k * 0.3)), default_max=min(k, int(k * 0.8)),
                tags=["count", "composite"], enabled=False
            ),
            FilterNode(
                id="structural_fibonacci_count", name="Fibonacci Count", category="Structural / Count",
                description="Count of numbers in Fibonacci sequence {1,2,3,5,8,13,21,34,55,89}",
                min_val=0, max_val=min(k, 5), default_min=0, default_max=min(k, 4),
                tags=["count", "fibonacci"], enabled=False
            ),
            FilterNode(
                id="structural_square_count", name="Perfect Square Count", category="Structural / Count",
                description="Count of perfect square balls {1,4,9,16,25,36,49,64,81}",
                min_val=0, max_val=min(k, 4), default_min=0, default_max=min(k, 3),
                tags=["count", "squares"], enabled=False
            ),
            FilterNode(
                id="structural_low_high_ratio", name="Low/High Ratio", category="Structural / Count",
                description="Ratio of low balls to high balls (scaled x10)",
                min_val=5, max_val=25, default_min=6, default_max=20,
                tags=["ratio", "range"], enabled=False
            ),
            FilterNode(
                id="structural_odd_even_ratio", name="Odd/Even Ratio", category="Structural / Count",
                description="Ratio of odd balls to even balls (scaled x10)",
                min_val=5, max_val=25, default_min=6, default_max=20,
                tags=["ratio", "parity"], enabled=False
            ),

            # ── 2. Sums & Averages (16 Filters) ─────────────────────────────
            FilterNode(
                id="structural_number_sum", name="Number Sum", category="Sums & Averages",
                description="Total sum of all participating balls (Tag 6)",
                min_val=int(k * (1 + M) * 0.35), max_val=int(k * (1 + M) * 0.65),
                default_min=int(k * (1 + M) * 0.35), default_max=int(k * (1 + M) * 0.65),
                step=5.0, tags=["sum", "arithmetic", "tag:6"], enabled=False
            ),
            FilterNode(
                id="structural_avg_value", name="Average Value", category="Sums & Averages",
                description="Floor average of numbers in line (Tag 7)",
                min_val=int(M * 0.35), max_val=int(M * 0.65),
                default_min=int(M * 0.35), default_max=int(M * 0.65),
                tags=["sum", "average", "tag:7"], enabled=False
            ),
            FilterNode(
                id="structural_unit_sum", name="Unit Number Sum", category="Sums & Averages",
                description="Sum of the last digits (units mod 10) (Tag 8)",
                min_val=int(k * 3.0), max_val=int(k * 6.5),
                default_min=int(k * 3.0), default_max=int(k * 6.5),
                tags=["sum", "units", "tag:8"], enabled=False
            ),
            FilterNode(
                id="arithmetic_unit_distinct", name="Unit Different Digits Count", category="Sums & Averages",
                description="Count of unique unit digits (0-9) represented (Tag 9)",
                min_val=max(3, min(k, 5)), max_val=min(k, 10),
                default_min=max(3, min(k, 5)), default_max=min(k, 10),
                tags=["digits", "distinct", "tag:9"], enabled=False
            ),
            FilterNode(
                id="arithmetic_sum_even_odd", name="Sum Value Even/Odd", category="Sums & Averages",
                description="Parity of the total sum (0=Even, 1=Odd) (Tag 41)",
                min_val=0, max_val=1, default_min=0, default_max=1,
                tags=["sum", "parity", "tag:41"], enabled=False
            ),
            FilterNode(
                id="arithmetic_root_sum", name="Root Sum", category="Sums & Averages",
                description="Digital root of number sum: 1 + (Sum - 1) % 9 (Tag 68)",
                min_val=1, max_val=9, default_min=1, default_max=9,
                tags=["sum", "digital_root", "tag:68"], enabled=False
            ),
            FilterNode(
                id="arithmetic_first_second_unit_sum", name="First and Second Unit Sum", category="Sums & Averages",
                description="Sum of first and second unit digits (Tag 69)",
                min_val=2, max_val=80, default_min=10, default_max=60,
                tags=["sum", "units", "tag:69"], enabled=False
            ),
            FilterNode(
                id="arithmetic_even_sum", name="Even Numbers Sum", category="Sums & Averages",
                description="Sum of only the even balls in the combination",
                min_val=int(k * (1 + M) * 0.15), max_val=int(k * (1 + M) * 0.55),
                default_min=int(k * (1 + M) * 0.15), default_max=int(k * (1 + M) * 0.55),
                tags=["sum", "parity"], enabled=False
            ),
            FilterNode(
                id="arithmetic_odd_sum", name="Odd Numbers Sum", category="Sums & Averages",
                description="Sum of only the odd balls in the combination",
                min_val=int(k * (1 + M) * 0.15), max_val=int(k * (1 + M) * 0.55),
                default_min=int(k * (1 + M) * 0.15), default_max=int(k * (1 + M) * 0.55),
                tags=["sum", "parity"], enabled=False
            ),
            FilterNode(
                id="arithmetic_prime_sum", name="Prime Numbers Sum", category="Sums & Averages",
                description="Sum of all prime balls in the combination",
                min_val=0, max_val=int(k * M * 0.6), default_min=10, default_max=int(k * M * 0.5),
                tags=["sum", "primes"], enabled=False
            ),
            FilterNode(
                id="arithmetic_digit_sum", name="Total Decimal Digits Sum", category="Sums & Averages",
                description="Sum of every individual decimal digit (tens + units)",
                min_val=int(k * 4.0), max_val=int(k * 10.0), default_min=int(k * 4.5), default_max=int(k * 9.5),
                tags=["sum", "digits"], enabled=False
            ),
            FilterNode(
                id="arithmetic_harmonic_mean", name="Harmonic Mean", category="Sums & Averages",
                description="Harmonic mean of numbers in combination",
                min_val=int(M * 0.15), max_val=int(M * 0.65), default_min=int(M * 0.20), default_max=int(M * 0.60),
                tags=["mean", "harmonic"], enabled=False
            ),
            FilterNode(
                id="arithmetic_geometric_mean", name="Geometric Mean", category="Sums & Averages",
                description="Geometric mean of numbers in combination",
                min_val=int(M * 0.25), max_val=int(M * 0.70), default_min=int(M * 0.30), default_max=int(M * 0.65),
                tags=["mean", "geometric"], enabled=False
            ),
            FilterNode(
                id="arithmetic_unit_sum_parity", name="Unit Sum Parity", category="Sums & Averages",
                description="Parity of the unit digit sum (0=Even, 1=Odd)",
                min_val=0, max_val=1, default_min=0, default_max=1,
                tags=["units", "parity"], enabled=False
            ),
            FilterNode(
                id="arithmetic_sum_tail", name="Sum Value Tail (Mod 10)", category="Sums & Averages",
                description="Last digit of total sum (Sum % 10)",
                min_val=0, max_val=9, default_min=0, default_max=9,
                tags=["sum", "tail"], enabled=False
            ),
            FilterNode(
                id="arithmetic_mean_deviation", name="Mean Absolute Deviation (MAD)", category="Sums & Averages",
                description="Mean absolute deviation of numbers from ticket median",
                min_val=1, max_val=int(M * 0.4), default_min=2, default_max=int(M * 0.35),
                tags=["deviation", "mad"], enabled=False
            ),

            # ── 3. Positional & Distance Filters (24 Filters) ───────────────
            FilterNode(
                id="positional_successive_run", name="Successive (Longest Run)", category="Positional & Distance",
                description="Longest streak of consecutive numbers (Tag 12)",
                min_val=0, max_val=min(k, 4), default_min=0, default_max=min(k, 4),
                tags=["positional", "consecutive", "tag:12"], enabled=False
            ),
            FilterNode(
                id="positional_successive_groups", name="Successive Groups", category="Positional & Distance",
                description="Number of disjoint consecutive sequence clusters (Tag 13)",
                min_val=0, max_val=min(k // 2, 4), default_min=0, default_max=min(k // 2, 4),
                tags=["positional", "consecutive", "tag:13"], enabled=False
            ),
            FilterNode(
                id="positional_odd_successive", name="Odd Successive", category="Positional & Distance",
                description="Consecutive sequence of odd numbers (Tag 14)",
                min_val=0, max_val=min(k // 2, 4), default_min=0, default_max=min(k // 2, 4),
                tags=["positional", "parity_seq", "tag:14"], enabled=False
            ),
            FilterNode(
                id="positional_even_successive", name="Even Successive", category="Positional & Distance",
                description="Consecutive sequence of even numbers (Tag 15)",
                min_val=0, max_val=min(k // 2, 4), default_min=0, default_max=min(k // 2, 4),
                tags=["positional", "parity_seq", "tag:15"], enabled=False
            ),
            FilterNode(
                id="positional_min_number", name="Minimum Number", category="Positional & Distance",
                description="Value of first / smallest ball drawn (Tag 16)",
                min_val=1, max_val=max(2, M - k), default_min=1, default_max=max(2, M - k),
                tags=["positional", "bounds", "tag:16"], enabled=False
            ),
            FilterNode(
                id="positional_max_number", name="Maximum Number", category="Positional & Distance",
                description="Value of last / largest ball drawn (Tag 17)",
                min_val=min(k + 1, M - 1), max_val=M, default_min=min(k + 1, M - 1), default_max=M,
                tags=["positional", "bounds", "tag:17"], enabled=False
            ),
            FilterNode(
                id="positional_first_last_dist", name="First and Last Distance", category="Positional & Distance",
                description="Span between highest and lowest ball: Max - Min (Tag 18)",
                min_val=k - 1, max_val=M - 1, default_min=int((M - 1) * 0.4), default_max=M - 1,
                tags=["positional", "span", "tag:18"], enabled=False
            ),
            FilterNode(
                id="positional_diff_distance", name="Different Distance", category="Positional & Distance",
                description="Count of distinct adjacent interval gap values (Tag 19)",
                min_val=1, max_val=k - 1, default_min=2, default_max=k - 1,
                tags=["positional", "gaps", "tag:19"], enabled=False
            ),
            FilterNode(
                id="positional_max_distance", name="Maximum Distance", category="Positional & Distance",
                description="Largest single gap between any two adjacent sorted balls",
                min_val=1, max_val=int(M * 0.8), default_min=2, default_max=int(M * 0.6),
                tags=["positional", "gaps"], enabled=False
            ),
            FilterNode(
                id="positional_min_distance", name="Minimum Distance", category="Positional & Distance",
                description="Smallest gap between two adjacent sorted balls (1 = consecutive)",
                min_val=1, max_val=5, default_min=1, default_max=3,
                tags=["positional", "gaps"], enabled=False
            ),
            FilterNode(
                id="positional_ball_1_range", name="Ball 1 Range", category="Positional & Distance",
                description="Allowed interval for the 1st sorted ball",
                min_val=1, max_val=max(3, M // 3), default_min=1, default_max=max(3, M // 3),
                tags=["positional", "ball:1"], enabled=False
            ),
            FilterNode(
                id="positional_ball_2_range", name="Ball 2 Range", category="Positional & Distance",
                description="Allowed interval for the 2nd sorted ball",
                min_val=2, max_val=max(5, M // 2), default_min=2, default_max=max(5, M // 2),
                tags=["positional", "ball:2"], enabled=False
            ),
            FilterNode(
                id="positional_ball_3_range", name="Ball 3 Range", category="Positional & Distance",
                description="Allowed interval for the 3rd sorted ball",
                min_val=3, max_val=max(7, int(M * 0.65)), default_min=3, default_max=max(7, int(M * 0.65)),
                tags=["positional", "ball:3"], enabled=False
            ),
            FilterNode(
                id="positional_ball_4_range", name="Ball 4 Range", category="Positional & Distance",
                description="Allowed interval for the 4th sorted ball",
                min_val=4, max_val=max(9, int(M * 0.80)), default_min=4, default_max=max(9, int(M * 0.80)),
                tags=["positional", "ball:4"], enabled=False
            ),
            FilterNode(
                id="positional_ball_5_range", name="Ball 5 Range", category="Positional & Distance",
                description="Allowed interval for the 5th sorted ball",
                min_val=5, max_val=max(11, int(M * 0.90)), default_min=5, default_max=max(11, int(M * 0.90)),
                tags=["positional", "ball:5"], enabled=False
            ),
            FilterNode(
                id="positional_ball_6_range", name="Ball 6 Range", category="Positional & Distance",
                description="Allowed interval for the 6th sorted ball",
                min_val=6, max_val=M, default_min=6, default_max=M,
                tags=["positional", "ball:6"], enabled=False
            ),
            FilterNode(
                id="positional_ball_1_2_sum", name="Ball 1 + Ball 2 Sum", category="Positional & Distance",
                description="Sum of the first two sorted balls",
                min_val=3, max_val=max(10, M), default_min=3, default_max=max(10, int(M * 0.8)),
                tags=["positional", "pair_sum"], enabled=False
            ),
            FilterNode(
                id="positional_ball_5_6_sum", name="Last Two Balls Sum", category="Positional & Distance",
                description="Sum of penultimate and last sorted balls",
                min_val=min(11, 2 * M - 15), max_val=2 * M - 1, default_min=int(M * 1.2), default_max=2 * M - 1,
                tags=["positional", "pair_sum"], enabled=False
            ),
            FilterNode(
                id="positional_gap_1_2", name="Gap 1-2 Interval", category="Positional & Distance",
                description="Difference between Ball 2 and Ball 1",
                min_val=1, max_val=max(3, M // 3), default_min=1, default_max=max(3, M // 3),
                tags=["positional", "gap"], enabled=False
            ),
            FilterNode(
                id="positional_gap_2_3", name="Gap 2-3 Interval", category="Positional & Distance",
                description="Difference between Ball 3 and Ball 2",
                min_val=1, max_val=max(3, M // 3), default_min=1, default_max=max(3, M // 3),
                tags=["positional", "gap"], enabled=False
            ),
            FilterNode(
                id="positional_gap_3_4", name="Gap 3-4 Interval", category="Positional & Distance",
                description="Difference between Ball 4 and Ball 3",
                min_val=1, max_val=max(3, M // 3), default_min=1, default_max=max(3, M // 3),
                tags=["positional", "gap"], enabled=False
            ),
            FilterNode(
                id="positional_gap_4_5", name="Gap 4-5 Interval", category="Positional & Distance",
                description="Difference between Ball 5 and Ball 4",
                min_val=1, max_val=max(3, M // 3), default_min=1, default_max=max(3, M // 3),
                tags=["positional", "gap"], enabled=False
            ),
            FilterNode(
                id="positional_inner_spread", name="Interquartile Inner Spread", category="Positional & Distance",
                description="Spread between 75th percentile and 25th percentile ball in line",
                min_val=1, max_val=int(M * 0.7), default_min=2, default_max=int(M * 0.6),
                tags=["positional", "iqr"], enabled=False
            ),
            FilterNode(
                id="positional_std_dev", name="Positional Standard Deviation", category="Positional & Distance",
                description="Standard deviation of numbers in combination",
                min_val=1, max_val=int(M * 0.4), default_min=2, default_max=int(M * 0.35),
                tags=["positional", "std"], enabled=False
            ),

            # ── 4. Complexity & Repeats (12 Filters) ─────────────────────────
            FilterNode(
                id="structural_ac_value", name="AC Value", category="Complexity & Repeats",
                description="Arithmetic Complexity: count of unique differences minus (k-1) (Tag 20)",
                min_val=max(1, int(k * 0.3)), max_val=max(3, int(k * 0.8)),
                default_min=max(1, int(k * 0.3)), default_max=max(3, int(k * 0.8)),
                tags=["complexity", "ac_value", "tag:20"], enabled=False
            ),
            FilterNode(
                id="historical_same_last_drawn", name="Same Last Drawn", category="Complexity & Repeats",
                description="Repeated balls from immediately preceding official drawing (Tag 21)",
                min_val=max(0, int(k * 0.2)), max_val=min(k, int(k * 0.8)),
                default_min=max(0, int(k * 0.3)), default_max=min(k, int(k * 0.7)),
                tags=["repeats", "historical", "tag:21"], enabled=False
            ),
            FilterNode(
                id="historical_repeat_2_draws", name="Repeated from Last 2 Draws", category="Complexity & Repeats",
                description="Count of balls appearing in either of the previous 2 official draws",
                min_val=max(1, int(k * 0.3)), max_val=min(k, int(k * 0.9)),
                default_min=max(1, int(k * 0.4)), default_max=min(k, int(k * 0.85)),
                tags=["repeats", "historical"], enabled=False
            ),
            FilterNode(
                id="historical_repeat_3_draws", name="Repeated from Last 3 Draws", category="Complexity & Repeats",
                description="Count of balls appearing in any of the previous 3 official draws",
                min_val=max(2, int(k * 0.5)), max_val=k, default_min=max(2, int(k * 0.55)), default_max=k,
                tags=["repeats", "historical"], enabled=False
            ),
            FilterNode(
                id="historical_cold_numbers", name="Cold Numbers Count", category="Complexity & Repeats",
                description="Count of lowest quartile historical frequency balls in line",
                min_val=0, max_val=min(k, 5), default_min=0, default_max=min(k, 4),
                tags=["historical", "cold"], enabled=False
            ),
            FilterNode(
                id="historical_hot_numbers", name="Hot Numbers Count", category="Complexity & Repeats",
                description="Count of highest quartile historical frequency balls in line",
                min_val=max(1, int(k * 0.2)), max_val=min(k, int(k * 0.7)),
                default_min=max(1, int(k * 0.25)), default_max=min(k, int(k * 0.65)),
                tags=["historical", "hot"], enabled=False
            ),
            FilterNode(
                id="historical_hot_cold_ratio", name="Hot / Cold Ratio", category="Complexity & Repeats",
                description="Ratio of hot to cold numbers (scaled x10)",
                min_val=2, max_val=30, default_min=5, default_max=25,
                tags=["historical", "ratio"], enabled=False
            ),
            FilterNode(
                id="historical_overdue", name="Overdue Numbers Count", category="Complexity & Repeats",
                description="Count of balls whose current skip exceeds 2x their historical average skip",
                min_val=0, max_val=min(k, 4), default_min=0, default_max=min(k, 3),
                tags=["historical", "overdue"], enabled=False
            ),
            FilterNode(
                id="historical_common_pair", name="Top Common Pairs Match", category="Complexity & Repeats",
                description="Count of top 10 historical recurring pairs present in combination",
                min_val=0, max_val=5, default_min=0, default_max=4,
                tags=["historical", "pairs"], enabled=False
            ),
            FilterNode(
                id="historical_common_triplet", name="Top Common Triplets Match", category="Complexity & Repeats",
                description="Count of top 10 historical recurring triplets present in combination",
                min_val=0, max_val=3, default_min=0, default_max=2,
                tags=["historical", "triplets"], enabled=False
            ),
            FilterNode(
                id="historical_recent_exclusion", name="Recent Exclusions (5 Draws)", category="Complexity & Repeats",
                description="Count of balls present in past 5 official drawings",
                min_val=max(2, int(k * 0.6)), max_val=k, default_min=max(2, int(k * 0.65)), default_max=k,
                tags=["historical", "exclusion"], enabled=False
            ),
            FilterNode(
                id="historical_spread_range", name="Historical Skips Spread", category="Complexity & Repeats",
                description="Max skip minus Min skip among participating balls",
                min_val=1, max_val=50, default_min=2, default_max=40,
                tags=["historical", "skips"], enabled=False
            ),

            # ── 5. Algebraic Residue & Modulo (22 Filters) ───────────────────
            FilterNode(
                id="algebraic_div_by_3_rem0", name="Divided by 3 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 3 (Tag 29)",
                min_val=max(0, int(k / 3 - 2)), max_val=int(k / 3 + 3),
                default_min=max(0, int(k / 3 - 1)), default_max=int(k / 3 + 2),
                tags=["modulo", "div3", "tag:29"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_4_rem0", name="Divided by 4 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 4 (Tag 30)",
                min_val=max(0, int(k / 4 - 2)), max_val=int(k / 4 + 3),
                default_min=max(0, int(k / 4 - 1)), default_max=int(k / 4 + 2),
                tags=["modulo", "div4", "tag:30"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_5_rem0", name="Divided by 5 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 5 (Tag 31)",
                min_val=max(0, int(k / 5 - 2)), max_val=int(k / 5 + 3),
                default_min=max(0, int(k / 5 - 1)), default_max=int(k / 5 + 2),
                tags=["modulo", "div5", "tag:31"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_6_rem0", name="Divided by 6 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 6 (Tag 32)",
                min_val=0, max_val=max(2, int(k / 6 + 2)),
                default_min=0, default_max=max(2, int(k / 6 + 2)),
                tags=["modulo", "div6", "tag:32"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_7_rem0", name="Divided by 7 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 7 (Tag 33)",
                min_val=0, max_val=max(2, int(k / 7 + 2)),
                default_min=0, default_max=max(2, int(k / 7 + 2)),
                tags=["modulo", "div7", "tag:33"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_8_rem0", name="Divided by 8 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 8 (Tag 34)",
                min_val=0, max_val=max(2, int(k / 8 + 2)), default_min=0, default_max=max(2, int(k / 8 + 2)),
                tags=["modulo", "div8", "tag:34"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_9_rem0", name="Divided by 9 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 9 (Tag 35)",
                min_val=0, max_val=max(2, int(k / 9 + 2)), default_min=0, default_max=max(2, int(k / 9 + 2)),
                tags=["modulo", "div9", "tag:35"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_10_rem0", name="Divided by 10 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 10 (Tag 36)",
                min_val=0, max_val=max(2, int(k / 10 + 2)), default_min=0, default_max=max(2, int(k / 10 + 2)),
                tags=["modulo", "div10", "tag:36"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_11_rem0", name="Divided by 11 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 11",
                min_val=0, max_val=max(2, int(k / 11 + 2)), default_min=0, default_max=max(2, int(k / 11 + 2)),
                tags=["modulo", "div11"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_12_rem0", name="Divided by 12 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 12",
                min_val=0, max_val=max(2, int(k / 12 + 2)), default_min=0, default_max=max(2, int(k / 12 + 2)),
                tags=["modulo", "div12"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_13_rem0", name="Divided by 13 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 13",
                min_val=0, max_val=max(2, int(k / 13 + 2)), default_min=0, default_max=max(2, int(k / 13 + 2)),
                tags=["modulo", "div13"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_14_rem0", name="Divided by 14 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 14",
                min_val=0, max_val=max(2, int(k / 14 + 2)), default_min=0, default_max=max(2, int(k / 14 + 2)),
                tags=["modulo", "div14"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_15_rem0", name="Divided by 15 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 15",
                min_val=0, max_val=max(2, int(k / 15 + 2)), default_min=0, default_max=max(2, int(k / 15 + 2)),
                tags=["modulo", "div15"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_16_rem0", name="Divided by 16 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 16",
                min_val=0, max_val=max(2, int(k / 16 + 2)), default_min=0, default_max=max(2, int(k / 16 + 2)),
                tags=["modulo", "div16"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_17_rem0", name="Divided by 17 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 17",
                min_val=0, max_val=max(2, int(k / 17 + 2)), default_min=0, default_max=max(2, int(k / 17 + 2)),
                tags=["modulo", "div17"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_18_rem0", name="Divided by 18 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 18",
                min_val=0, max_val=max(2, int(k / 18 + 2)), default_min=0, default_max=max(2, int(k / 18 + 2)),
                tags=["modulo", "div18"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_19_rem0", name="Divided by 19 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 19",
                min_val=0, max_val=max(2, int(k / 19 + 2)), default_min=0, default_max=max(2, int(k / 19 + 2)),
                tags=["modulo", "div19"], enabled=False
            ),
            FilterNode(
                id="algebraic_div_by_20_rem0", name="Divided by 20 (Rem 0)", category="Algebraic Residue",
                description="Count of numbers divisible by 20",
                min_val=0, max_val=max(2, int(k / 20 + 2)), default_min=0, default_max=max(2, int(k / 20 + 2)),
                tags=["modulo", "div20"], enabled=False
            ),
            FilterNode(
                id="algebraic_mod3_rem1", name="Modulo 3 Remainder 1", category="Algebraic Residue",
                description="Count of numbers where (Number % 3 == 1)",
                min_val=max(0, int(k / 3 - 2)), max_val=int(k / 3 + 3), default_min=max(0, int(k / 3 - 1)), default_max=int(k / 3 + 2),
                tags=["modulo", "mod3"], enabled=False
            ),
            FilterNode(
                id="algebraic_mod3_rem2", name="Modulo 3 Remainder 2", category="Algebraic Residue",
                description="Count of numbers where (Number % 3 == 2)",
                min_val=max(0, int(k / 3 - 2)), max_val=int(k / 3 + 3), default_min=max(0, int(k / 3 - 1)), default_max=int(k / 3 + 2),
                tags=["modulo", "mod3"], enabled=False
            ),
            FilterNode(
                id="algebraic_mod4_rem1", name="Modulo 4 Remainder 1", category="Algebraic Residue",
                description="Count of numbers where (Number % 4 == 1)",
                min_val=0, max_val=max(2, int(k / 4 + 2)), default_min=0, default_max=max(2, int(k / 4 + 2)),
                tags=["modulo", "mod4"], enabled=False
            ),
            FilterNode(
                id="algebraic_mod5_rem1", name="Modulo 5 Remainder 1", category="Algebraic Residue",
                description="Count of numbers where (Number % 5 == 1)",
                min_val=0, max_val=max(2, int(k / 5 + 2)), default_min=0, default_max=max(2, int(k / 5 + 2)),
                tags=["modulo", "mod5"], enabled=False
            ),

            # ── 6. Decades & Units (11 Filters) ──────────────────────────────
            FilterNode(
                id="decades_different_decades", name="Different Decade Count", category="Decades & Units",
                description="Number of distinct decades (0-9, 10-19, 20-29, etc.) in line (Tag 44)",
                min_val=1, max_val=max(2, (M // 10) + 1),
                default_min=2, default_max=max(2, (M // 10) + 1),
                tags=["decades", "distinct", "tag:44"], enabled=False
            ),
            FilterNode(
                id="decades_high_units_count", name="High Units Count (6,7,8,9)", category="Decades & Units",
                description="Count of balls ending in 6, 7, 8, or 9 (Tag 46)",
                min_val=0, max_val=min(k, 8), default_min=1, default_max=min(k, 6),
                tags=["units", "high", "tag:46"], enabled=False
            ),
            FilterNode(
                id="decades_odd_units_count", name="Odd Units Count (1,3,5,7,9)", category="Decades & Units",
                description="Distinct odd second digits {1,3,5,7,9} in line (Tag 47)",
                min_val=1, max_val=5, default_min=2, default_max=5,
                tags=["units", "odd", "tag:47"], enabled=False
            ),
            FilterNode(
                id="decades_decade_0", name="Decade 1-9 Count", category="Decades & Units",
                description="Count of numbers in decade 1-9",
                min_val=0, max_val=min(k, 9), default_min=1, default_max=min(k, 6),
                tags=["decades", "d0"], enabled=False
            ),
            FilterNode(
                id="decades_decade_1", name="Decade 10-19 Count", category="Decades & Units",
                description="Count of numbers in decade 10-19",
                min_val=0, max_val=min(k, 10), default_min=1, default_max=min(k, 7),
                tags=["decades", "d1"], enabled=False
            ),
            FilterNode(
                id="decades_decade_2", name="Decade 20-29 Count", category="Decades & Units",
                description="Count of numbers in decade 20-29",
                min_val=0, max_val=min(k, 10), default_min=1, default_max=min(k, 7),
                tags=["decades", "d2"], enabled=False
            ),
            FilterNode(
                id="decades_decade_3", name="Decade 30-39 Count", category="Decades & Units",
                description="Count of numbers in decade 30-39",
                min_val=0, max_val=min(k, 10), default_min=0, default_max=min(k, 6),
                tags=["decades", "d3"], enabled=False
            ),
            FilterNode(
                id="decades_decade_4", name="Decade 40-49 Count", category="Decades & Units",
                description="Count of numbers in decade 40-49",
                min_val=0, max_val=min(k, 10), default_min=0, default_max=min(k, 6),
                tags=["decades", "d4"], enabled=False
            ),
            FilterNode(
                id="decades_decade_5", name="Decade 50-59 Count", category="Decades & Units",
                description="Count of numbers in decade 50-59",
                min_val=0, max_val=min(k, 10), default_min=0, default_max=min(k, 6),
                tags=["decades", "d5"], enabled=False
            ),
            FilterNode(
                id="decades_decade_6", name="Decade 60-69 Count", category="Decades & Units",
                description="Count of numbers in decade 60-69",
                min_val=0, max_val=min(k, 10), default_min=0, default_max=min(k, 5),
                tags=["decades", "d6"], enabled=False
            ),
            FilterNode(
                id="decades_same_decade_max", name="Max Balls in Single Decade", category="Decades & Units",
                description="Maximum number of balls falling into any single decade group",
                min_val=1, max_val=min(k, 6), default_min=2, default_max=min(k, 5),
                tags=["decades", "max_cluster"], enabled=False
            ),

            # ── 7. Advanced & Sets (12 Filters) ──────────────────────────────
            FilterNode(
                id="advanced_successive_filter", name="Successive Multi-Length Filter", category="Advanced & Sets",
                description="Group counts for Successive 2/3/4/5 streaks (Tag 24)",
                min_val=0, max_val=5, default_min=0, default_max=3,
                tags=["advanced", "streak", "tag:24"], enabled=False
            ),
            FilterNode(
                id="advanced_range_filter", name="Range Partition Filter", category="Advanced & Sets",
                description="Arbitrary pool partitions count (Tag 25)",
                min_val=0, max_val=k, default_min=1, default_max=k,
                tags=["advanced", "partition", "tag:25"], enabled=False
            ),
            FilterNode(
                id="advanced_number_groups", name="Custom Number Groups", category="Advanced & Sets",
                description="Allowed counts from arbitrary number lists (Tag 26)",
                min_val=0, max_val=k, default_min=0, default_max=k,
                tags=["advanced", "groups", "tag:26"], enabled=False
            ),
            FilterNode(
                id="historical_delete_drawings", name="Delete History Drawings", category="Advanced & Sets",
                description="Deduplicate candidate tickets against past official drawings (Tag 38)",
                min_val=0, max_val=0, default_min=0, default_max=0,
                tags=["advanced", "historical", "tag:38"], enabled=False
            ),
            FilterNode(
                id="custom_exclude_set", name="Exclude Number Set", category="Advanced & Sets",
                description="Ensure ticket contains zero numbers from a designated exclusion list",
                min_val=0, max_val=0, default_min=0, default_max=0,
                tags=["advanced", "exclude"], enabled=False
            ),
            FilterNode(
                id="custom_required_pairs", name="Required Key Pairs", category="Advanced & Sets",
                description="Requires tickets to contain at least one configured harmonic pair",
                min_val=1, max_val=5, default_min=1, default_max=3,
                tags=["advanced", "pairs"], enabled=False
            ),
            FilterNode(
                id="custom_forbidden_pairs", name="Forbidden Conflicting Pairs", category="Advanced & Sets",
                description="Prevents co-occurrence of incompatible ball pairs in the same line",
                min_val=0, max_val=0, default_min=0, default_max=0,
                tags=["advanced", "forbidden"], enabled=False
            ),
            FilterNode(
                id="custom_inner_core", name="Inner Core Matrix Count", category="Advanced & Sets",
                description="Count of numbers located in the physical center of the lottery ticket grid",
                min_val=max(0, int(k * 0.15)), max_val=min(k, int(k * 0.65)),
                default_min=max(0, int(k * 0.20)), default_max=min(k, int(k * 0.60)),
                tags=["advanced", "matrix_core"], enabled=False
            ),
            FilterNode(
                id="custom_outer_shell", name="Outer Shell Perimeter Count", category="Advanced & Sets",
                description="Count of numbers located on the outermost boundary perimeter of the grid",
                min_val=max(1, int(k * 0.35)), max_val=min(k, int(k * 0.85)),
                default_min=max(1, int(k * 0.40)), default_max=min(k, int(k * 0.80)),
                tags=["advanced", "matrix_shell"], enabled=False
            ),
            FilterNode(
                id="custom_magic_square", name="Magic Square 3x3 Sum Match", category="Advanced & Sets",
                description="Count of balls intersecting Lo Shu 3x3 mathematical magic square configurations",
                min_val=0, max_val=min(k, 5), default_min=0, default_max=min(k, 4),
                tags=["advanced", "magic_square"], enabled=False
            ),
            FilterNode(
                id="custom_golden_ratio", name="Golden Ratio (Phi) Partitions", category="Advanced & Sets",
                description="Count of balls falling inside the 0.618 golden partition cut of the pool",
                min_val=max(1, int(k * 0.40)), max_val=min(k, int(k * 0.80)),
                default_min=max(1, int(k * 0.45)), default_max=min(k, int(k * 0.75)),
                tags=["advanced", "golden_ratio"], enabled=False
            ),
            FilterNode(
                id="custom_locked_numbers", name="Locked Mandatory Balls", category="Advanced & Sets",
                description="Ensures every candidate ticket contains all designated locked banker numbers",
                min_val=1, max_val=min(k, 5), default_min=1, default_max=min(k, 3),
                tags=["advanced", "locked"], enabled=False
            )
        ]

        return filters

    # -------------------------------------------------------------------------
    # High-Performance Vectorized Combinatorial Chunker & Filter Engine
    # -------------------------------------------------------------------------

    def stream_combinations_chunked(
        self,
        pool: List[int],
        pick_count: int,
        chunk_size: int = 100_000
    ) -> Generator[np.ndarray, None, None]:
        """Memory-safe chunked generator yielding 2D uint8 NumPy arrays of combinations."""
        pool_sorted = sorted(pool)
        comb_iter = itertools.combinations(pool_sorted, pick_count)

        while True:
            chunk = list(itertools.islice(comb_iter, chunk_size))
            if not chunk:
                break
            yield np.array(chunk, dtype=np.uint8)

    def evaluate_filter_chunk_vectorized(
        self,
        combos: np.ndarray,
        active_filters: List[FilterNode],
        game: Optional[GameSchema] = None,
        last_draw: Optional[List[int]] = None,
        past_draws: Optional[List[List[int]]] = None
    ) -> np.ndarray:
        """
        Evaluates active filters across a 2D chunk using vectorized NumPy routines.
        Returns a 2D boolean pass matrix of shape (num_combos, num_active_filters).
        """
        num_combos = combos.shape[0]
        if not active_filters:
            return np.ones((num_combos, 1), dtype=bool)

        pass_matrix = np.zeros((num_combos, len(active_filters)), dtype=bool)
        k = combos.shape[1]
        pool_max = game.pool_size if game else int(np.max(combos))
        mid = pool_max // 2

        for idx, flt in enumerate(active_filters):
            fid = flt.id

            # ── 1. Structural / Count
            if fid == "structural_odd_count":
                odds = np.sum(combos % 2 != 0, axis=1)
                pass_matrix[:, idx] = (odds >= flt.min_val) & (odds <= flt.max_val)

            elif fid == "structural_even_count":
                evens = np.sum(combos % 2 == 0, axis=1)
                pass_matrix[:, idx] = (evens >= flt.min_val) & (evens <= flt.max_val)

            elif fid == "structural_high_count":
                highs = np.sum(combos > mid, axis=1)
                pass_matrix[:, idx] = (highs >= flt.min_val) & (highs <= flt.max_val)

            elif fid == "structural_low_count":
                lows = np.sum(combos <= mid, axis=1)
                pass_matrix[:, idx] = (lows >= flt.min_val) & (lows <= flt.max_val)

            elif fid == "structural_prime_count":
                primes_count = np.sum(np.isin(combos, PRIMES_ARRAY), axis=1)
                pass_matrix[:, idx] = (primes_count >= flt.min_val) & (primes_count <= flt.max_val)

            elif fid == "structural_composite_count":
                composites = np.sum((~np.isin(combos, PRIMES_ARRAY)) & (combos > 1), axis=1)
                pass_matrix[:, idx] = (composites >= flt.min_val) & (composites <= flt.max_val)

            elif fid == "structural_fibonacci_count":
                fibs = np.sum(np.isin(combos, FIBONACCI_ARRAY), axis=1)
                pass_matrix[:, idx] = (fibs >= flt.min_val) & (fibs <= flt.max_val)

            elif fid == "structural_square_count":
                squares = np.sum(np.isin(combos, SQUARES_ARRAY), axis=1)
                pass_matrix[:, idx] = (squares >= flt.min_val) & (squares <= flt.max_val)

            elif fid == "structural_low_high_ratio":
                lows = np.sum(combos <= mid, axis=1)
                highs = np.maximum(1, np.sum(combos > mid, axis=1))
                ratios = (lows / highs) * 10.0
                pass_matrix[:, idx] = (ratios >= flt.min_val) & (ratios <= flt.max_val)

            elif fid == "structural_odd_even_ratio":
                odds = np.sum(combos % 2 != 0, axis=1)
                evens = np.maximum(1, np.sum(combos % 2 == 0, axis=1))
                ratios = (odds / evens) * 10.0
                pass_matrix[:, idx] = (ratios >= flt.min_val) & (ratios <= flt.max_val)

            # ── 2. Sums & Averages
            elif fid in ("structural_number_sum", "arithmetic_number_sum"):
                sums = np.sum(combos, axis=1)
                pass_matrix[:, idx] = (sums >= flt.min_val) & (sums <= flt.max_val)

            elif fid in ("structural_avg_value", "arithmetic_avg_value"):
                avgs = np.sum(combos, axis=1) // k
                pass_matrix[:, idx] = (avgs >= flt.min_val) & (avgs <= flt.max_val)

            elif fid in ("structural_unit_sum", "arithmetic_unit_sum"):
                unit_sums = np.sum(combos % 10, axis=1)
                pass_matrix[:, idx] = (unit_sums >= flt.min_val) & (unit_sums <= flt.max_val)

            elif fid == "arithmetic_sum_even_odd":
                sums = np.sum(combos, axis=1)
                parity = sums % 2
                pass_matrix[:, idx] = (parity >= flt.min_val) & (parity <= flt.max_val)

            elif fid in ("arithmetic_root_sum", "structural_root_sum"):
                sums = np.sum(combos, axis=1)
                root_sums = 1 + (sums - 1) % 9
                pass_matrix[:, idx] = (root_sums >= flt.min_val) & (root_sums <= flt.max_val)

            elif fid == "arithmetic_even_sum":
                even_sums = np.sum(np.where(combos % 2 == 0, combos, 0), axis=1)
                pass_matrix[:, idx] = (even_sums >= flt.min_val) & (even_sums <= flt.max_val)

            elif fid == "arithmetic_odd_sum":
                odd_sums = np.sum(np.where(combos % 2 != 0, combos, 0), axis=1)
                pass_matrix[:, idx] = (odd_sums >= flt.min_val) & (odd_sums <= flt.max_val)

            elif fid == "arithmetic_prime_sum":
                prime_mask = np.isin(combos, PRIMES_ARRAY)
                p_sums = np.sum(np.where(prime_mask, combos, 0), axis=1)
                pass_matrix[:, idx] = (p_sums >= flt.min_val) & (p_sums <= flt.max_val)

            elif fid == "arithmetic_digit_sum":
                d_sums = np.sum((combos // 10) + (combos % 10), axis=1)
                pass_matrix[:, idx] = (d_sums >= flt.min_val) & (d_sums <= flt.max_val)

            elif fid == "arithmetic_sum_tail":
                sums = np.sum(combos, axis=1)
                tails = sums % 10
                pass_matrix[:, idx] = (tails >= flt.min_val) & (tails <= flt.max_val)

            elif fid == "arithmetic_unit_distinct":
                # Count unique unit digits
                # Evaluated row-wise
                distinct_counts = np.array([len(set(c % 10)) for c in combos], dtype=int)
                pass_matrix[:, idx] = (distinct_counts >= flt.min_val) & (distinct_counts <= flt.max_val)

            elif fid == "arithmetic_first_second_unit_sum":
                fs_sums = (combos[:, 0] % 10) + (combos[:, min(1, k - 1)] % 10)
                pass_matrix[:, idx] = (fs_sums >= flt.min_val) & (fs_sums <= flt.max_val)

            elif fid == "arithmetic_mean_deviation":
                medians = np.median(combos, axis=1, keepdims=True)
                mads = np.mean(np.abs(combos - medians), axis=1)
                pass_matrix[:, idx] = (mads >= flt.min_val) & (mads <= flt.max_val)

            elif fid == "arithmetic_harmonic_mean":
                combos_safe = np.maximum(1, combos.astype(float))
                hmeans = k / np.sum(1.0 / combos_safe, axis=1)
                pass_matrix[:, idx] = (hmeans >= flt.min_val) & (hmeans <= flt.max_val)

            elif fid == "arithmetic_geometric_mean":
                combos_safe = np.maximum(1, combos.astype(float))
                gmeans = np.exp(np.mean(np.log(combos_safe), axis=1))
                pass_matrix[:, idx] = (gmeans >= flt.min_val) & (gmeans <= flt.max_val)

            # ── 3. Positional & Distance
            elif fid == "positional_min_number":
                min_balls = combos[:, 0].astype(int)
                pass_matrix[:, idx] = (min_balls >= flt.min_val) & (min_balls <= flt.max_val)

            elif fid == "positional_max_number":
                max_balls = combos[:, -1].astype(int)
                pass_matrix[:, idx] = (max_balls >= flt.min_val) & (max_balls <= flt.max_val)

            elif fid == "positional_first_last_dist":
                spans = combos[:, -1].astype(int) - combos[:, 0].astype(int)
                pass_matrix[:, idx] = (spans >= flt.min_val) & (spans <= flt.max_val)

            elif fid == "positional_max_distance":
                diffs = np.diff(combos.astype(int), axis=1)
                max_gaps = np.max(diffs, axis=1)
                pass_matrix[:, idx] = (max_gaps >= flt.min_val) & (max_gaps <= flt.max_val)

            elif fid == "positional_min_distance":
                diffs = np.diff(combos.astype(int), axis=1)
                min_gaps = np.min(diffs, axis=1)
                pass_matrix[:, idx] = (min_gaps >= flt.min_val) & (min_gaps <= flt.max_val)

            elif fid == "positional_ball_1_range":
                b1 = combos[:, 0].astype(int)
                pass_matrix[:, idx] = (b1 >= flt.min_val) & (b1 <= flt.max_val)

            elif fid == "positional_ball_2_range":
                b2 = combos[:, min(1, k - 1)].astype(int)
                pass_matrix[:, idx] = (b2 >= flt.min_val) & (b2 <= flt.max_val)

            elif fid == "positional_ball_3_range":
                b3 = combos[:, min(2, k - 1)].astype(int)
                pass_matrix[:, idx] = (b3 >= flt.min_val) & (b3 <= flt.max_val)

            elif fid == "positional_ball_4_range":
                b4 = combos[:, min(3, k - 1)].astype(int)
                pass_matrix[:, idx] = (b4 >= flt.min_val) & (b4 <= flt.max_val)

            elif fid == "positional_ball_5_range":
                b5 = combos[:, min(4, k - 1)].astype(int)
                pass_matrix[:, idx] = (b5 >= flt.min_val) & (b5 <= flt.max_val)

            elif fid == "positional_ball_6_range":
                b6 = combos[:, min(5, k - 1)].astype(int)
                pass_matrix[:, idx] = (b6 >= flt.min_val) & (b6 <= flt.max_val)

            elif fid == "positional_ball_1_2_sum":
                p_sum = combos[:, 0].astype(int) + combos[:, min(1, k - 1)].astype(int)
                pass_matrix[:, idx] = (p_sum >= flt.min_val) & (p_sum <= flt.max_val)

            elif fid == "positional_ball_5_6_sum":
                idx1 = min(4, k - 2)
                idx2 = min(5, k - 1)
                p_sum = combos[:, idx1].astype(int) + combos[:, idx2].astype(int)
                pass_matrix[:, idx] = (p_sum >= flt.min_val) & (p_sum <= flt.max_val)

            elif fid.startswith("positional_gap_"):
                parts = fid.split("_")
                try:
                    c1 = int(parts[2]) - 1
                    c2 = int(parts[3]) - 1
                    if c1 < k and c2 < k:
                        gap_vals = combos[:, c2].astype(int) - combos[:, c1].astype(int)
                        pass_matrix[:, idx] = (gap_vals >= flt.min_val) & (gap_vals <= flt.max_val)
                    else:
                        pass_matrix[:, idx] = True
                except (IndexError, ValueError):
                    pass_matrix[:, idx] = True

            elif fid == "positional_inner_spread":
                q1_idx = k // 4
                q3_idx = (3 * k) // 4
                iqr = combos[:, q3_idx].astype(int) - combos[:, q1_idx].astype(int)
                pass_matrix[:, idx] = (iqr >= flt.min_val) & (iqr <= flt.max_val)

            elif fid == "positional_std_dev":
                stds = np.std(combos.astype(float), axis=1)
                pass_matrix[:, idx] = (stds >= flt.min_val) & (stds <= flt.max_val)

            elif fid == "positional_successive_run":
                diffs = np.diff(combos.astype(int), axis=1)
                # Max consecutive run
                runs = np.array([
                    max((len(list(g)) for k_val, g in itertools.groupby(d == 1) if k_val), default=0)
                    for d in diffs
                ], dtype=int)
                pass_matrix[:, idx] = (runs >= flt.min_val) & (runs <= flt.max_val)

            elif fid == "positional_successive_groups":
                diffs = np.diff(combos.astype(int), axis=1)
                group_counts = np.array([
                    sum(1 for k_val, g in itertools.groupby(d == 1) if k_val)
                    for d in diffs
                ], dtype=int)
                pass_matrix[:, idx] = (group_counts >= flt.min_val) & (group_counts <= flt.max_val)

            # ── 4. Complexity & Repeats
            elif fid == "structural_ac_value":
                ac_vals = []
                for c in combos:
                    diff_set = set()
                    for i in range(k):
                        for j in range(i + 1, k):
                            diff_set.add(int(c[j]) - int(c[i]))
                    ac_vals.append(len(diff_set) - (k - 1))
                ac_arr = np.array(ac_vals, dtype=int)
                pass_matrix[:, idx] = (ac_arr >= flt.min_val) & (ac_arr <= flt.max_val)

            elif fid == "historical_same_last_drawn" and last_draw:
                repeat_counts = np.sum(np.isin(combos, last_draw), axis=1)
                pass_matrix[:, idx] = (repeat_counts >= flt.min_val) & (repeat_counts <= flt.max_val)

            elif fid == "historical_repeat_2_draws" and past_draws and len(past_draws) >= 2:
                last_2 = set(past_draws[-1] + past_draws[-2])
                repeat_counts = np.sum(np.isin(combos, list(last_2)), axis=1)
                pass_matrix[:, idx] = (repeat_counts >= flt.min_val) & (repeat_counts <= flt.max_val)

            elif fid == "historical_repeat_3_draws" and past_draws and len(past_draws) >= 3:
                last_3 = set(past_draws[-1] + past_draws[-2] + past_draws[-3])
                repeat_counts = np.sum(np.isin(combos, list(last_3)), axis=1)
                pass_matrix[:, idx] = (repeat_counts >= flt.min_val) & (repeat_counts <= flt.max_val)

            elif fid == "historical_delete_drawings" and past_draws:
                past_draws_set = {tuple(sorted(d)) for d in past_draws}
                matches = np.array([tuple(c) in past_draws_set for c in combos], dtype=bool)
                pass_matrix[:, idx] = ~matches

            # ── 5. Algebraic Residue & Modulo
            elif fid.startswith("algebraic_div_by_"):
                try:
                    div = int(fid.split("_")[3])
                    counts = np.sum(combos % div == 0, axis=1)
                    pass_matrix[:, idx] = (counts >= flt.min_val) & (counts <= flt.max_val)
                except (IndexError, ValueError):
                    pass_matrix[:, idx] = True

            elif fid.startswith("algebraic_mod"):
                parts = fid.split("_")
                try:
                    mod_div = int(parts[1].replace("mod", ""))
                    mod_rem = int(parts[2].replace("rem", ""))
                    counts = np.sum(combos % mod_div == mod_rem, axis=1)
                    pass_matrix[:, idx] = (counts >= flt.min_val) & (counts <= flt.max_val)
                except (IndexError, ValueError):
                    pass_matrix[:, idx] = True

            # ── 6. Decades & Units
            elif fid == "decades_different_decades":
                dec_distinct = np.array([len(set(c // 10)) for c in combos], dtype=int)
                pass_matrix[:, idx] = (dec_distinct >= flt.min_val) & (dec_distinct <= flt.max_val)

            elif fid == "decades_high_units_count":
                high_units = np.isin(combos % 10, [6, 7, 8, 9])
                counts = np.sum(high_units, axis=1)
                pass_matrix[:, idx] = (counts >= flt.min_val) & (counts <= flt.max_val)

            elif fid == "decades_odd_units_count":
                odd_units = np.isin(combos % 10, [1, 3, 5, 7, 9])
                counts = np.sum(odd_units, axis=1)
                pass_matrix[:, idx] = (counts >= flt.min_val) & (counts <= flt.max_val)

            elif fid.startswith("decades_decade_"):
                try:
                    d_idx = int(fid.split("_")[2])
                    d_start = d_idx * 10
                    d_end = d_start + 9
                    d_counts = np.sum((combos >= d_start) & (combos <= d_end), axis=1)
                    pass_matrix[:, idx] = (d_counts >= flt.min_val) & (d_counts <= flt.max_val)
                except (IndexError, ValueError):
                    pass_matrix[:, idx] = True

            elif fid == "decades_same_decade_max":
                max_in_decades = np.array([
                    max(Counter(c // 10).values()) for c in combos
                ], dtype=int)
                pass_matrix[:, idx] = (max_in_decades >= flt.min_val) & (max_in_decades <= flt.max_val)

            # ── 7. Advanced & Sets
            elif fid == "advanced_successive_filter":
                diffs = np.diff(combos.astype(int), axis=1)
                consec_counts = np.sum(diffs == 1, axis=1)
                pass_matrix[:, idx] = (consec_counts >= flt.min_val) & (consec_counts <= flt.max_val)

            elif fid == "advanced_range_filter":
                third = max(1, pool_max // 3)
                lower_counts = np.sum(combos <= third, axis=1)
                pass_matrix[:, idx] = (lower_counts >= flt.min_val) & (lower_counts <= flt.max_val)

            elif fid == "custom_inner_core":
                # Inner 50% numbers in pool
                q_low = pool_max // 4
                q_high = (3 * pool_max) // 4
                core_counts = np.sum((combos >= q_low) & (combos <= q_high), axis=1)
                pass_matrix[:, idx] = (core_counts >= flt.min_val) & (core_counts <= flt.max_val)

            elif fid == "custom_outer_shell":
                q_low = pool_max // 4
                q_high = (3 * pool_max) // 4
                shell_counts = np.sum((combos < q_low) | (combos > q_high), axis=1)
                pass_matrix[:, idx] = (shell_counts >= flt.min_val) & (shell_counts <= flt.max_val)

            elif fid == "custom_golden_ratio":
                phi_bound = int(pool_max * 0.618)
                phi_counts = np.sum(combos <= phi_bound, axis=1)
                pass_matrix[:, idx] = (phi_counts >= flt.min_val) & (phi_counts <= flt.max_val)

            else:
                pass_matrix[:, idx] = True

        return pass_matrix

    def apply_tolerance_mask(
        self,
        pass_matrix: np.ndarray,
        tolerance: ToleranceRule
    ) -> np.ndarray:
        """
        Evaluates Fault Tolerance (Error Allowance) on the 2D boolean pass matrix.
        Returns a 1D boolean mask of surviving combinations.
        """
        total_active = pass_matrix.shape[1]
        if total_active == 0:
            return np.ones(pass_matrix.shape[0], dtype=bool)

        pass_counts = np.sum(pass_matrix, axis=1)

        if tolerance.mode == ToleranceMode.AND:
            return pass_counts == total_active
        elif tolerance.mode == ToleranceMode.OR:
            return pass_counts >= 1
        elif tolerance.mode == ToleranceMode.RANGE:
            upper = tolerance.max_pass if tolerance.max_pass > 0 else total_active
            return (pass_counts >= tolerance.min_pass) & (pass_counts <= upper)
        return np.ones(pass_matrix.shape[0], dtype=bool)

    def generate_archetype_tickets(
        self,
        game_id: str,
        archetype_key: str,
        count: int = 10
    ) -> List[TicketReceipt]:
        """
        Generates candidate tickets using real headless engine prediction strategies
        calibrated against historical draw data.
        """
        game = self.get_game(game_id)
        if not game:
            return []

        df = self.get_draws(game_id)
        game_def = registry.get_game(game_id)

        strat_map = {
            "archetype_ai_consensus": "voting:markov,weighted,bayesian,momentum",
            "archetype_momentum": "voting:momentum,streak",
            "archetype_balanced_wheel": "steiner_wheel",
            "archetype_cosmic": "voting:moon_phase,fibonacci,kabbalistic",
        }
        strat_expr = strat_map.get(archetype_key, "weighted")

        tickets: List[TicketReceipt] = []
        try:
            from engine.strategies import get_strategy
            adapter = GenericLotteryAdapter(game_def)
            strategy = get_strategy(strat_expr)
            result = strategy.suggest(df, adapter.rules, count=count)

            conf = float(result.confidence or 0.88)
            for idx, raw_ticket in enumerate(result.tickets, 1):
                sorted_ticket = sorted(raw_ticket)
                if len(sorted_ticket) < game.pick_count:
                    remaining = [n for n in range(game.number_range_min, game.number_range_max + 1) if n not in sorted_ticket]
                    import random
                    sorted_ticket = sorted(sorted_ticket + random.sample(remaining, game.pick_count - len(sorted_ticket)))
                elif len(sorted_ticket) > game.pick_count:
                    sorted_ticket = sorted_ticket[:game.pick_count]

                bonus_numbers: List[int] = []
                if game.bonus_count > 0 and game.bonus_pool:
                    import random
                    bonus_numbers = sorted(random.sample(range(1, game.bonus_pool + 1), game.bonus_count))

                tickets.append(TicketReceipt(
                    ticket_id=idx,
                    numbers=sorted_ticket,
                    bonus_numbers=bonus_numbers,
                    confidence_score=round(conf, 2),
                    strategy_source=archetype_key.replace("archetype_", "").replace("_", " ").title()
                ))
        except Exception as e:
            logger.warning("Strategy execution failed (%s), using probabilistic fallback: %s", strat_expr, e)
            import random
            pool = list(range(game.number_range_min, game.number_range_max + 1))
            for idx in range(1, count + 1):
                sorted_ticket = sorted(random.sample(pool, game.pick_count))
                bonus_numbers = []
                if game.bonus_count > 0 and game.bonus_pool:
                    bonus_numbers = sorted(random.sample(range(1, game.bonus_pool + 1), game.bonus_count))
                tickets.append(TicketReceipt(
                    ticket_id=idx,
                    numbers=sorted_ticket,
                    bonus_numbers=bonus_numbers,
                    confidence_score=0.85,
                    strategy_source=archetype_key.replace("archetype_", "").replace("_", " ").title()
                ))

        return tickets
