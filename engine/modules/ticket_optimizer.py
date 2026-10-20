"""
Lottery Studio Ticket Optimization Engine ✂️
======================================
Ported from Lottery Studio TopForm (Doc 01 §F10, Doc 05 §C, EPIC 7 F7.2).

Provides combinatorial cost-reduction algorithms to reduce large sets of
candidate tickets while maximizing space coverage and diversity:

1. Same-number reduction (AC-T4):
   Collapses lines sharing >= X identical numbers to one representative,
   preventing duplicate prize clustering and over-concentration.

2. Reserve-per-block reduction (AC-T3):
   From every group of N lines (default 10), reserves exactly X lines
   (e.g., reserve 3 per 10 lines reduces 100 tickets to 30).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Set, Optional
import numpy as np


@dataclass
class OptimizationReport:
    initial_count: int
    kept_count: int
    eliminated_count: int
    reduction_pct: float
    strategy: str
    parameter_summary: str
    kept_tickets: List[List[int]]


def same_number_reduction(
    tickets: Sequence[Sequence[int]],
    max_shared: int,
    positions: Optional[Sequence[int]] = None,
) -> OptimizationReport:
    """
    Same-number reduction (Lottery Studio 'Optimization 1'):
    Eliminates candidate tickets that share >= `max_shared` numbers with
    any already accepted representative ticket.

    Args:
        tickets: Sequence of ticket lists/tuples.
        max_shared: Maximum allowed count of identical numbers. A ticket sharing
                    >= max_shared numbers with an already-accepted ticket is pruned.
        positions: Optional 0-indexed positions to restrict comparison to.
                   If None, full tickets are compared as sets.

    Returns:
        OptimizationReport with kept tickets and reduction metrics.
    """
    initial_count = len(tickets)
    if initial_count == 0:
        return OptimizationReport(
            initial_count=0,
            kept_count=0,
            eliminated_count=0,
            reduction_pct=0.0,
            strategy="same_number",
            parameter_summary=f"max_shared={max_shared}",
            kept_tickets=[],
        )

    # Standardize tickets to sorted lists
    cleaned_tickets: List[List[int]] = [sorted(list(t)) for t in tickets]
    
    kept_tickets: List[List[int]] = []
    # Store kept tickets as sets for fast intersection testing
    kept_sets: List[Set[int]] = []

    for ticket in cleaned_tickets:
        if positions is not None:
            # Position-specific comparison
            target_slice = set(ticket[p] for p in positions if p < len(ticket))
        else:
            target_slice = set(ticket)

        # Check collision with already accepted tickets
        collided = False
        for s in kept_sets:
            if len(target_slice & s) >= max_shared:
                collided = True
                break

        if not collided:
            kept_tickets.append(ticket)
            kept_sets.append(target_slice)

    kept_count = len(kept_tickets)
    eliminated = initial_count - kept_count
    reduction_pct = (eliminated / initial_count) * 100.0 if initial_count > 0 else 0.0

    pos_info = f", positions={list(positions)}" if positions is not None else ""
    return OptimizationReport(
        initial_count=initial_count,
        kept_count=kept_count,
        eliminated_count=eliminated,
        reduction_pct=reduction_pct,
        strategy="same_number",
        parameter_summary=f"max_shared={max_shared}{pos_info}",
        kept_tickets=kept_tickets,
    )


def reserve_per_block(
    tickets: Sequence[Sequence[int]],
    reserve_count: int = 3,
    block_size: int = 10,
) -> OptimizationReport:
    """
    Reserve-per-block reduction (Lottery Studio 'Optimization 2' / AC-T3):
    From each consecutive block of `block_size` tickets, keeps `reserve_count`
    tickets (e.g., reserve 3 tickets per 10 lines).

    Args:
        tickets: Sequence of ticket lists/tuples.
        reserve_count: How many tickets to keep per block (1 <= reserve_count < block_size).
        block_size: Size of each partition block (default 10).

    Returns:
        OptimizationReport with kept tickets and reduction metrics.
    """
    initial_count = len(tickets)
    if initial_count == 0:
        return OptimizationReport(
            initial_count=0,
            kept_count=0,
            eliminated_count=0,
            reduction_pct=0.0,
            strategy="reserve_per_block",
            parameter_summary=f"reserve={reserve_count}/{block_size}",
            kept_tickets=[],
        )

    if reserve_count <= 0:
        raise ValueError(f"reserve_count must be >= 1, got {reserve_count}")
    if block_size <= 0:
        raise ValueError(f"block_size must be >= 1, got {block_size}")
    if reserve_count > block_size:
        raise ValueError(f"reserve_count ({reserve_count}) cannot exceed block_size ({block_size})")

    cleaned_tickets: List[List[int]] = [sorted(list(t)) for t in tickets]
    kept_tickets: List[List[int]] = []

    for block_start in range(0, initial_count, block_size):
        block = cleaned_tickets[block_start : block_start + block_size]
        # Keep the first `reserve_count` tickets in this block
        kept_tickets.extend(block[:reserve_count])

    kept_count = len(kept_tickets)
    eliminated = initial_count - kept_count
    reduction_pct = (eliminated / initial_count) * 100.0 if initial_count > 0 else 0.0

    return OptimizationReport(
        initial_count=initial_count,
        kept_count=kept_count,
        eliminated_count=eliminated,
        reduction_pct=reduction_pct,
        strategy="reserve_per_block",
        parameter_summary=f"reserve={reserve_count}/{block_size}",
        kept_tickets=kept_tickets,
    )
