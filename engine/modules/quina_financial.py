"""
Quina Financial Module — Unfolded (Desdobrada) Bet Economics
==============================================================

Quina is a pari-mutuel game: Caixa does not publish a fixed cash prize per
tier, it splits a pool among winners. What *is* deterministic — and what this
module computes exactly, with no historical fitting — is:

  1. Ticket cost scaling for an N-number unfolded bet (N in 5..15):
         cost(N) = C(N, 5) * base_ticket_price

  2. How many of an N-number ticket's C(N, 5) internal combinations land in
     each prize tier (Quina/Quadra/Terno/Duque), as a function of how many of
     the 5 officially-drawn numbers fall inside your N-number pool (`hits`):
         lines_at_tier(N, hits, tier) = C(hits, tier) * C(N - hits, 5 - tier)
     This is exact combinatorics, not an estimate — every unfolded ticket is
     literally the set of all 5-number sub-combinations of your N numbers.

  3. "1 in X" odds of achieving >= a given number of hits when drawing 5 balls
     from an 80-ball pool, for a fixed N-number ticket (hypergeometric).

Nothing here predicts outcomes — every 5-number combination remains exactly
1-in-24,040,016. This module only prices bets and quantifies the payout
*structure* an unfolded ticket exposes you to.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Dict, List

from engine.adapters import DrawRules

# Caixa Quina prize tiers, by number of matches out of the 5 drawn.
TIERS: Dict[str, int] = {"Quina": 5, "Quadra": 4, "Terno": 3, "Duque": 2}


# ---------------------------------------------------------------------------
# Cost scaling
# ---------------------------------------------------------------------------


def ticket_cost(n_numbers: int, rules: DrawRules) -> float:
    """Cost of a single unfolded (desdobrada) bet with `n_numbers` numbers."""
    return rules.calculate_bet_cost(n_numbers)


def n_combinations(n_numbers: int, pick_count: int = 5) -> int:
    """How many base 5-number lines an N-number unfolded ticket contains."""
    return comb(n_numbers, pick_count)


# ---------------------------------------------------------------------------
# Payout structure — exact combinatorics
# ---------------------------------------------------------------------------


def lines_at_tier(n_numbers: int, hits: int, tier: int) -> int:
    """
    Number of the ticket's C(n_numbers, 5) internal lines that score exactly
    `tier` matches, given that `hits` of the 5 drawn numbers fall inside the
    ticket's N-number pool.

    lines_at_tier(N, D, j) = C(D, j) * C(N - D, 5 - j)
    """
    if tier > hits or (5 - tier) > (n_numbers - hits):
        return 0
    return comb(hits, tier) * comb(n_numbers - hits, 5 - tier)


@dataclass
class TierPayoutRow:
    tier: str
    matches_required: int
    lines_won: int


def payout_breakdown(n_numbers: int, hits: int) -> List[TierPayoutRow]:
    """Full Quina/Quadra/Terno/Duque line-count breakdown for a given hit count."""
    return [
        TierPayoutRow(tier=name, matches_required=req, lines_won=lines_at_tier(n_numbers, hits, req))
        for name, req in TIERS.items()
    ]


def multiplier_matrix(n_values: tuple[int, ...] = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)) -> Dict[int, Dict]:
    """
    Full cost/multiplier + per-tier line-count matrix for the given N values,
    assuming the maximum possible `hits` for each tier (hits == 5, the ceiling
    every N-number ticket can ever realise). Used to compare ticket sizes.
    """
    out: Dict[int, Dict] = {}
    for n in n_values:
        combos = n_combinations(n)
        out[n] = {
            "combinations": combos,
            "cost_multiplier_vs_single": combos,  # C(N,5) base-bet equivalents
            "cost_brl": combos * 2.5,
            "max_lines_by_tier": {name: lines_at_tier(n, 5, req) for name, req in TIERS.items()},
        }
    return out


# ---------------------------------------------------------------------------
# Odds — hypergeometric, exact
# ---------------------------------------------------------------------------


def prob_at_least_hits(n_numbers: int, min_hits: int, pool_size: int = 80, drawn: int = 5) -> float:
    """
    P(>= min_hits of the 5 drawn numbers fall inside a fixed n_numbers-sized
    ticket), via the hypergeometric distribution. Exact, not simulated.
    """
    total = comb(pool_size, drawn)
    p = 0.0
    for h in range(min_hits, drawn + 1):
        p += comb(n_numbers, h) * comb(pool_size - n_numbers, drawn - h)
    return p / total


def odds_table(n_numbers: int, pool_size: int = 80, drawn: int = 5) -> Dict[str, Dict]:
    """1-in-X odds of hitting each tier at least once, for a fixed N-number ticket."""
    out: Dict[str, Dict] = {}
    for name, req in TIERS.items():
        p = prob_at_least_hits(n_numbers, req, pool_size, drawn)
        out[name] = {"probability": p, "one_in_x": (1.0 / p) if p > 0 else float("inf")}
    return out
