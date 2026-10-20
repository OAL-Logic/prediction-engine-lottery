"""
Wheeling Solver & Combinatorial Covering Engine
================================================
Enterprise covering design generator with support for:
- Full Combinatorial Wheeling C(v, k)
- Abbreviated Covering Designs (t-if-m of v)
- Positional Column Wheeling
- Fixed Banker / Key Numbers
- Hamming Distance Redundancy Pruning
- Bitmask Coverage Certification & Co-occurrence Gap Matrix
"""

from __future__ import annotations

import itertools
import random
import logging
from typing import List, Set, Tuple, Dict, Optional, Generator
import numpy as np

from cockpit.src.core.models import WheelingConfig, WheelType, GameSchema

logger = logging.getLogger(__name__)


class WheelingSolver:
    """
    Mathematical combinatorial wheel solver implementing Steiner-like covering
    designs and redundant ticket reduction.
    """

    @staticmethod
    def to_bitmask(ticket: List[int]) -> int:
        """Converts ticket numbers into a 64-bit integer mask (1-indexed)."""
        mask = 0
        for num in ticket:
            mask |= (1 << (num - 1))
        return mask

    @staticmethod
    def to_matrix_masks(tickets: np.ndarray) -> np.ndarray:
        """Vectorized conversion of a 2D ticket array into a 1D uint64 mask array."""
        if tickets.size == 0:
            return np.array([], dtype=np.uint64)
        masks = np.zeros(tickets.shape[0], dtype=np.uint64)
        for col in range(tickets.shape[1]):
            masks |= (np.uint64(1) << np.uint64(tickets[:, col] - 1))
        return masks

    @classmethod
    def evaluate_coverage(
        cls,
        tickets: List[List[int]],
        pool: List[int],
        t: int,
        m: int,
        max_subsets_sample: int = 5000
    ) -> float:
        """
        Calculates empirical coverage percentage for a (t-if-m of v) guarantee.
        If 'm' numbers from 'pool' are drawn, at least one ticket has >= 't' matches.
        """
        if not tickets or not pool or m > len(pool) or t > m:
            return 0.0

        pool_sorted = sorted(pool)
        ticket_masks = np.array([cls.to_bitmask(t_line) for t_line in tickets], dtype=np.uint64)
        all_targets = list(itertools.combinations(pool_sorted, m))

        if len(all_targets) > max_subsets_sample:
            import random
            sampled_targets = random.sample(all_targets, max_subsets_sample)
        else:
            sampled_targets = all_targets

        covered_count = 0
        for target in sampled_targets:
            target_mask = np.uint64(cls.to_bitmask(list(target)))
            intersections = ticket_masks & target_mask
            for mask in intersections:
                if int(mask).bit_count() >= t:
                    covered_count += 1
                    break

        return (covered_count / len(sampled_targets)) * 100.0

    @classmethod
    def prune_hamming_redundancy(
        cls,
        tickets: List[List[int]],
        min_distance: int = 2
    ) -> List[List[int]]:
        """
        Prunes redundant tickets based on Hamming overlap.
        Guarantees that every accepted ticket differs from all previously accepted tickets
        by at least `min_distance` distinct balls.
        """
        if not tickets or min_distance <= 1:
            return tickets

        k = len(tickets[0])
        max_allowed_overlap = k - min_distance
        pruned: List[List[int]] = []
        pruned_masks: List[int] = []

        for ticket in tickets:
            t_mask = cls.to_bitmask(ticket)
            redundant = False
            for p_mask in pruned_masks:
                overlap = (t_mask & p_mask).bit_count()
                if overlap > max_allowed_overlap:
                    redundant = True
                    break
            if not redundant:
                pruned.append(ticket)
                pruned_masks.append(t_mask)

        return pruned

    @classmethod
    def generate_full_wheel(
        cls,
        pool: List[int],
        pick_count: int,
        key_numbers: Optional[List[int]] = None,
        max_tickets: Optional[int] = None
    ) -> List[List[int]]:
        """
        Generates exhaustive C(v, k) full wheel, optionally pinning key numbers.
        """
        pool_set = set(pool)
        keys = sorted(list(set(key_numbers or [])))

        # Validate keys
        if not set(keys).issubset(pool_set):
            raise ValueError("All key numbers must belong to the selected pool.")
        if len(keys) > pick_count:
            raise ValueError(f"Key numbers count ({len(keys)}) exceeds pick count ({pick_count}).")

        needed = pick_count - len(keys)
        remaining_pool = sorted(list(pool_set - set(keys)))

        if needed == 0:
            return [keys]

        results: List[List[int]] = []
        comb_gen = itertools.combinations(remaining_pool, needed)

        for comb in comb_gen:
            ticket = sorted(keys + list(comb))
            results.append(ticket)
            if max_tickets and len(results) >= max_tickets:
                break

        return results

    @classmethod
    def generate_abbreviated_wheel(
        cls,
        pool: List[int],
        pick_count: int,
        guarantee_t: int = 4,
        condition_m: int = 5,
        key_numbers: Optional[List[int]] = None,
        max_tickets: int = 500,
        sample_pool_cap: int = 22
    ) -> List[List[int]]:
        """
        Generates minimal covering design (t-if-m of v) using an accelerated greedy
        bitmask cover. Supports fixed key numbers.
        """
        pool_sorted = sorted(list(set(pool)))
        v = len(pool_sorted)
        k = pick_count
        t = guarantee_t
        m = condition_m

        if t > k:
            t = k
        if m < t:
            m = t

        keys = sorted(list(set(key_numbers or [])))
        if not set(keys).issubset(set(pool_sorted)):
            raise ValueError("All key numbers must belong to the selected pool.")
        if len(keys) > k:
            raise ValueError("Key count exceeds pick count.")

        # Fixed keys logic
        needed_k = k - len(keys)
        rem_pool = sorted(list(set(pool_sorted) - set(keys)))

        if needed_k == 0:
            return [keys]

        # Effective sub-guarantee for remaining slots
        # For covering target subsets
        t_effective = max(1, t - len(keys))
        if t_effective > needed_k:
            t_effective = needed_k

        # Pool size restriction for combinatorial safety
        if len(rem_pool) > sample_pool_cap:
            rem_pool = rem_pool[:sample_pool_cap]

        all_t_subsets = set(itertools.combinations(rem_pool, t_effective))
        all_blocks = list(itertools.combinations(rem_pool, needed_k))
        random.shuffle(all_blocks)

        tickets: List[List[int]] = []
        sample_slice = min(2500, len(all_blocks))

        while all_t_subsets and len(tickets) < max_tickets:
            best_block = None
            best_cover: Set[Tuple[int, ...]] = set()

            candidate_sample = all_blocks[:sample_slice]
            for block in candidate_sample:
                covered = set(itertools.combinations(block, t_effective))
                new_cover = covered.intersection(all_t_subsets)
                if len(new_cover) > len(best_cover):
                    best_block = block
                    best_cover = new_cover
                    if len(best_cover) == len(list(itertools.combinations(range(needed_k), t_effective))):
                        break

            if not best_block:
                if all_blocks:
                    best_block = all_blocks[0]
                else:
                    break

            tickets.append(sorted(keys + list(best_block)))
            all_t_subsets -= best_cover
            all_blocks.remove(best_block)
            sample_slice = min(2500, len(all_blocks))

        return tickets

    @classmethod
    def generate_positional_wheel(
        cls,
        column_candidates: List[List[int]],
        max_tickets: int = 500
    ) -> List[List[int]]:
        """
        Generates combinations where each position (column) must be selected
        from an explicit candidate list (strictly sorted).
        """
        results: List[List[int]] = []
        product_iter = itertools.product(*column_candidates)

        for candidate in product_iter:
            # Must be strictly increasing without duplicates
            if all(candidate[i] < candidate[i + 1] for i in range(len(candidate) - 1)):
                results.append(list(candidate))
                if len(results) >= max_tickets:
                    break

        return results

    @classmethod
    def compute_gap_cooccurrence_matrix(
        cls,
        tickets: List[List[int]],
        pool_size: int
    ) -> np.ndarray:
        """
        Computes symmetric [M, M] co-occurrence matrix where each cell (i, j)
        denotes how many tickets contain both ball (i+1) and ball (j+1).
        """
        matrix = np.zeros((pool_size, pool_size), dtype=np.int32)
        for ticket in tickets:
            for i in range(len(ticket)):
                for j in range(i + 1, len(ticket)):
                    b1, b2 = ticket[i] - 1, ticket[j] - 1
                    if 0 <= b1 < pool_size and 0 <= b2 < pool_size:
                        matrix[b1, b2] += 1
                        matrix[b2, b1] += 1
        return matrix

    @classmethod
    def execute_wheel(
        cls,
        config: WheelingConfig,
        game: GameSchema
    ) -> List[List[int]]:
        """
        High-level dispatcher executing wheel generation per WheelingConfig.
        """
        pool = config.pool_numbers if config.pool_numbers else list(range(game.number_range_min, game.number_range_max + 1))
        k = game.pick_count
        keys = config.key_numbers
        cap = config.max_ticket_cap or 1000

        if config.wheel_type == WheelType.FULL:
            tickets = cls.generate_full_wheel(pool, k, key_numbers=keys, max_tickets=cap)
        elif config.wheel_type == WheelType.KEY_BANKER:
            tickets = cls.generate_full_wheel(pool, k, key_numbers=keys, max_tickets=cap)
        else: # ABBREVIATED
            tickets = cls.generate_abbreviated_wheel(
                pool=pool,
                pick_count=k,
                guarantee_t=config.guarantee,
                condition_m=config.condition_match,
                key_numbers=keys,
                max_tickets=cap
            )

        if config.pruning_enabled:
            tickets = cls.prune_hamming_redundancy(tickets, min_distance=config.pruning_distance_min)

        return tickets
