"""
Odds Comparator Module — cross-adapter odds and EV comparison
=============================================================

This module provides tools to compare different lotteries based on their
mathematical odds and financial efficiency (Expected Value heuristics).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from engine.adapters import DrawRules


@dataclass
class ComparisonResult:
    name: str
    jackpot_odds: int
    ticket_price: float
    currency: str
    efficiency_score: float  # log10(odds) / price (lower is better for "pure odds")


def compare_lotteries(rules_list: List[DrawRules]) -> List[ComparisonResult]:
    """
    Rank lotteries by their jackpot odds and cost-efficiency.
    """
    import math

    results = []
    for r in rules_list:
        odds = r.jackpot_odds
        if odds == 0:
            continue
            
        # Heuristic: how many "units of probability" do you buy per currency unit?
        # Since odds vary by orders of magnitude, we use log10.
        score = math.log10(odds) / r.ticket_price if r.ticket_price > 0 else 0.0
        
        results.append(ComparisonResult(
            name=r.name,
            jackpot_odds=odds,
            ticket_price=r.ticket_price,
            currency=r.currency,
            efficiency_score=score
        ))
        
    # Sort by jackpot odds (easiest to win first)
    return sorted(results, key=lambda x: x.jackpot_odds)
