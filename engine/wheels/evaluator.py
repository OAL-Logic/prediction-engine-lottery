"""
Wheel Prize Evaluator — test how a wheel performs against a winning combo.
"""

from __future__ import annotations

from typing import List, Dict, Set


def evaluate_prizes(tickets: List[List[int]], winning_numbers: List[int]) -> Dict[int, int]:
    """
    Count how many tickets in the set hit each prize tier.
    
    Returns
    -------
    dict: {match_count: number_of_tickets}
    """
    win_set = set(winning_numbers)
    counts: Dict[int, int] = {}
    
    for ticket in tickets:
        matches = len(set(ticket) & win_set)
        if matches > 0:
            counts[matches] = counts.get(matches, 0) + 1
            
    return dict(sorted(counts.items(), reverse=True))
