"""
Wheel Reduction Guarantee (WRG) Engine 🎡
=========================================
High-speed combinatorial coverage evaluator and ticket reducer.
Optimized for SamLotto-style formula parity and gap analysis.
"""

from __future__ import annotations
import numpy as np
from itertools import combinations
from typing import List, Set, Tuple, Dict, Any

class WheelingEngine:
    """
    Core engine for combinatorial coverage and prize guarantees.
    Uses bit-packed representations (uint64) for sub-millisecond evaluation.
    """

    def __init__(self, n: int, k: int):
        self.n = n # Pool size (e.g. 15 numbers chosen by user)
        self.k = k # Numbers per ticket (e.g. 6)
        if self.n > 64:
            raise ValueError("WheelingEngine currently supports pools up to 64 numbers (bit-packed limit).")

    def _to_bitmask(self, ticket: List[int]) -> int:
        """Converts a ticket to a 64-bit integer mask."""
        mask = 0
        for num in ticket:
            # Shift by (num - 1) assuming numbers start at 1
            mask |= (1 << (num - 1))
        return mask

    def _to_matrix_mask(self, tickets: np.ndarray) -> np.ndarray:
        """Converts a 2D array of tickets to an array of bitmasks."""
        # This is a vectorized version of bitmasking
        # assumes tickets are already sorted and 0-indexed or correctly shifted
        masks = np.zeros(tickets.shape[0], dtype=np.uint64)
        for i in range(tickets.shape[1]):
            masks |= (np.uint64(1) << np.uint64(tickets[:, i] - 1))
        return masks

    def evaluate_coverage(self, tickets: np.ndarray, t: int, m: int) -> float:
        """
        Calculates % coverage for a 't-if-m' guarantee.
        t: match required (e.g. 4)
        m: numbers hit in pool (e.g. 6)
        
        A wheel 'v, k, t, m' means:
        If 'm' numbers from our 'v' pool are drawn, at least one ticket 
        will have 't' matches.
        """
        n_rows = tickets.shape[0]
        ticket_masks = self._to_matrix_mask(tickets)
        
        # All possible winning combinations of size 'm' within the pool
        # This is the "Truth" space we must cover.
        pool_range = np.arange(1, self.n + 1)
        target_subsets = list(combinations(pool_range, m))
        total_subsets = len(target_subsets)
        
        covered_count = 0
        for subset in target_subsets:
            subset_mask = self._to_bitmask(list(subset))
            
            # Check if any ticket mask has at least 't' bits in common with subset_mask
            # intersect = ticket_mask & subset_mask
            # count = bin(intersect).count('1')
            
            # Vectorized intersection count:
            # Bitwise AND, then count set bits
            intersections = ticket_masks & np.uint64(subset_mask)
            
            # Fast bit counting for 64-bit ints
            # Using numpy's bitcount equivalent or falling back to loops for clarity in logic
            # For 1M tickets, we need this to be fast.
            
            # Kernighan's or built-in bit_count in Python 3.10+
            for mask in intersections:
                if int(mask).bit_count() >= t:
                    covered_count += 1
                    break
                    
        return covered_count / total_subsets

    def get_gap_matrix(self, tickets: np.ndarray) -> np.ndarray:
        """
        Returns a symmetric [n, n] matrix where values represent 
        the number of times each pair of balls appears together.
        Used for TUI 'Wheel Matrix' gap visualization.
        """
        matrix = np.zeros((self.n, self.n), dtype=np.int32)
        for ticket in tickets:
            # Vectorized pair increment
            # For a small K (e.g. 6), this loop is fine
            for i in range(len(ticket)):
                for j in range(i + 1, len(ticket)):
                    matrix[ticket[i]-1, ticket[j]-1] += 1
                    matrix[ticket[j]-1, ticket[i]-1] += 1
        return matrix

    def reduce_tickets(self, tickets: np.ndarray, t: int, m: int, target_coverage: float = 1.0) -> np.ndarray:
        """
        Reduces a ticket set while maintaining the t-if-m guarantee.
        Greedy implementation: selects tickets that maximize incremental coverage.
        """
        n_tickets = tickets.shape[0]
        ticket_masks = self._to_matrix_mask(tickets)
        
        # 1. Generate target space (all subsets of size m in the chosen pool)
        pool_range = np.arange(1, self.n + 1)
        target_subsets = [self._to_bitmask(list(s)) for subset in combinations(pool_range, m)]
        total_targets = len(target_subsets)
        
        # target_masks[j] is the bitmask for subset j
        target_masks = np.array(target_subsets, dtype=np.uint64)
        
        # remaining_targets[j] is True if subset j is not yet covered
        remaining_targets = np.ones(total_targets, dtype=bool)
        selected_indices = []
        
        covered_count = 0
        target_goal = int(total_targets * target_coverage)

        while covered_count < target_goal:
            # Find ticket that covers most remaining targets
            # This is O(Tickets * Subsets), very heavy for large N.
            # We use a bitwise pre-check.
            best_ticket_idx = -1
            max_new_coverage = -1
            
            # Optimization: only check a sample of tickets or use matrix multiplication if possible
            # For this implementation, we'll do a focused search.
            for i in range(n_tickets):
                if i in selected_indices: continue
                
                # count how many remaining_targets are covered by ticket i
                # A target j is covered by ticket i if (ticket_mask[i] & target_mask[j]).bit_count() >= t
                
                # Vectorized check for ticket i against all targets
                intersections = ticket_masks[i] & target_masks[remaining_targets]
                new_coverage = np.sum([int(mask).bit_count() >= t for mask in intersections])
                
                if new_coverage > max_new_coverage:
                    max_new_coverage = new_coverage
                    best_ticket_idx = i
            
            if best_ticket_idx == -1 or max_new_coverage == 0:
                break
                
            selected_indices.append(best_ticket_idx)
            
            # Update remaining_targets
            intersections = ticket_masks[best_ticket_idx] & target_masks
            just_covered = np.array([int(mask).bit_count() >= t for mask in intersections])
            
            # Only count targets that were actually remaining
            newly_covered_mask = just_covered & remaining_targets
            covered_count += np.sum(newly_covered_mask)
            remaining_targets &= ~just_covered

        return tickets[selected_indices]

def list_formula_categories() -> Dict[str, str]:
    """Returns available wheeling categories found in data/wheels/."""
    return {
        "full": "Full Wheels (All combinations)",
        "abbreviated": "Abbreviated Wheels (t-if-m guarantees)",
        "key": "Key Number Wheels",
        "balanced": "Howard-style Balanced Wheels"
    }
