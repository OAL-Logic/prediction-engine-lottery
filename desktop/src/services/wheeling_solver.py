"""
Mathematical Wheeling Solver & Covering Designs
================================================
Implements full and abbreviated combinatorial wheels, Banker keys,
Hamming distance redundancy pruning, and prize guarantee reports.
"""

from __future__ import annotations

import math
import itertools
import logging
from typing import List, Dict, Tuple, Set, Optional, Any

from desktop.src.core.models import (
    WheelingConfig, WheelType, GameSchema
)

logger = logging.getLogger(__name__)


class WheelingSolver:
    """
    Mathematical covering designs engine.
    Supports full wheels, greedy abbreviated covering algorithms,
    Banker key numbers, and Hamming distance overlap reduction.
    """

    @staticmethod
    def generate_tickets(config: WheelingConfig, game: GameSchema) -> List[List[int]]:
        """Generates candidate ticket lines according to wheeling configuration."""
        pool = sorted(list(set(config.pool_numbers)))
        k = game.pick_count
        bankers = sorted(list(set(config.key_numbers)))

        if len(pool) < k:
            return []

        # Validate bankers
        bankers = [b for b in bankers if b in pool]
        rem_pool = [n for n in pool if n not in bankers]
        needed_rem = k - len(bankers)

        if needed_rem < 0 or len(rem_pool) < needed_rem:
            return []

        if config.wheel_type == WheelType.FULL:
            # Full C(v, k)
            combos = list(itertools.combinations(rem_pool, needed_rem))
            lines = [sorted(bankers + list(c)) for c in combos]

        elif config.wheel_type == WheelType.ABBREVIATED:
            # Greedy Covering Design heuristic for t-if-m guarantee
            lines = WheelingSolver._solve_abbreviated_covering(
                bankers=bankers,
                rem_pool=rem_pool,
                needed_rem=needed_rem,
                guarantee_t=config.guarantee,
                condition_m=config.condition_match,
                max_cap=config.max_ticket_cap or 1500
            )
        else:
            # Default to full
            combos = list(itertools.combinations(rem_pool, needed_rem))
            lines = [sorted(bankers + list(c)) for c in combos]

        # Apply Hamming distance redundancy pruning if requested
        if config.pruning_enabled:
            lines = WheelingSolver.prune_redundant_overlaps(
                lines, min_distinct=config.pruning_distance_min
            )

        if config.max_ticket_cap and len(lines) > config.max_ticket_cap:
            lines = lines[:config.max_ticket_cap]

        return lines

    @staticmethod
    def _solve_abbreviated_covering(
        bankers: List[int],
        rem_pool: List[int],
        needed_rem: int,
        guarantee_t: int,
        condition_m: int,
        max_cap: int = 1500
    ) -> List[List[int]]:
        """
        Greedy covering algorithm:
        Maximizes coverage of required sub-combinations (t-subsets) per selected ticket line.
        """
        all_candidates = list(itertools.combinations(rem_pool, needed_rem))
        if len(all_candidates) <= 20:
            return [sorted(bankers + list(c)) for c in all_candidates]

        # Target sub-combinations to cover
        t_subsets = list(itertools.combinations(rem_pool, min(needed_rem, guarantee_t)))
        uncovered: Set[Tuple[int, ...]] = set(t_subsets)

        selected_lines: List[List[int]] = []

        # Candidate sub-combination mapping
        cand_map: List[Tuple[Tuple[int, ...], Set[Tuple[int, ...]]]] = []
        for cand in all_candidates:
            subs = set(itertools.combinations(cand, min(needed_rem, guarantee_t)))
            cand_map.append((cand, subs))

        # Iterative greedy selection
        while uncovered and len(selected_lines) < max_cap:
            # Pick candidate covering the largest number of remaining uncovered sub-combinations
            best_cand = None
            best_cover_count = -1
            best_subs = None

            for cand, subs in cand_map:
                cov = len(subs.intersection(uncovered))
                if cov > best_cover_count:
                    best_cover_count = cov
                    best_cand = cand
                    best_subs = subs

            if not best_cand or best_cover_count <= 0:
                break

            selected_lines.append(sorted(bankers + list(best_cand)))
            uncovered.difference_update(best_subs)

        return selected_lines

    @staticmethod
    def prune_redundant_overlaps(lines: List[List[int]], min_distinct: int = 2) -> List[List[int]]:
        """
        Prunes lines where Hamming distance between combinations is smaller than min_distinct.
        Ensures diverse asset distribution.
        """
        if not lines or min_distinct <= 1:
            return lines

        pruned: List[List[int]] = []
        for cand in lines:
            cand_set = set(cand)
            keep = True
            for accepted in pruned:
                common = len(cand_set.intersection(accepted))
                # Distinct elements = len(cand) - common
                distinct = len(cand) - common
                if distinct < min_distinct:
                    keep = False
                    break
            if keep:
                pruned.append(cand)

        return pruned

    @staticmethod
    def compute_guarantee_report(
        lines: List[List[int]],
        pool: List[int],
        k: int,
        price_per_ticket: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Calculates ticket count, reduction %, and estimated cost."""
        total_possible = math.comb(len(pool), k) if len(pool) >= k else len(lines)
        num_lines = len(lines)
        reduction_rate = 100.0 * (1.0 - (num_lines / max(1, total_possible)))
        cost = num_lines * price_per_ticket

        return {
            "total_possible_lines": total_possible,
            "generated_lines": num_lines,
            "reduction_rate_pct": round(reduction_rate, 2),
            "estimated_cost": round(cost, 2),
            "formatted_cost": f"{currency} {cost:,.2f}",
        }
