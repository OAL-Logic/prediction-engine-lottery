"""
Unfolded Bets Module — desdobramento economics for multi-number single tickets
================================================================================
A Caixa "single unfolded ticket" (aposta múltipla / desdobramento) of
``n_picked`` numbers (n_picked > rules.pick_count) is registered as one
official bet but is mathematically equivalent to playing every
``C(n_picked, pick_count)`` base-ticket sub-combination at once.

Given the actual draw, each of those sub-combinations independently matches
some number of drawn numbers ("tier"). This module answers three questions:

  multiplier_matrix() : for a ticket that ends up containing `hits` of the
                         drawn numbers, exactly how many of its C(n, pick)
                         sub-games win at each prize tier?
  hit_probability()   : under the fair-game assumption (every superset of
                         size n_picked is equally likely to contain any given
                         number of the actual draw), what's P(hits)?
  evaluate()           : combine the two into expected payout, net EV, ROI%
                         and breakeven jackpot for a given prize table.

Statistical caveat (mirrors `engine.modules.sum_range`)
--------------------------------------------------------
Unfolding a ticket does **not** change its expected ROI% — see the module
docstring of `PoolOptimizer` in `engine.modules.pool_optimizer` for why.
It only buys more combinations (and hence a higher P(any prize) and higher
variance), proportionally to cost. This falls straight out of the
hypergeometric structure below and is verified in
``tests/test_unfolded_bets.py`` (ROI% is invariant to `n_picked`, holding the
prize table fixed).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import comb
from typing import Dict, Optional

from engine.adapters import DrawRules


# ---------------------------------------------------------------------------
# Multiplier matrix
# ---------------------------------------------------------------------------


def multiplier_matrix(rules: DrawRules, n_picked: int) -> Dict[int, Dict[int, int]]:
    """
    ``{hits: {tier: games_won}}`` for a ticket of `n_picked` numbers.

    ``hits`` is how many of the actual `rules.pick_count` drawn numbers fall
    inside the `n_picked`-number ticket. Given that, the number of the
    ticket's ``C(n_picked, pick_count)`` sub-games that score exactly `tier`
    hits is the standard "choose the winners, choose the losers" count:

        games_won(hits, tier) = C(hits, tier) * C(n_picked - hits, pick - tier)

    Rows below the lowest paying tier are omitted (they can only ever
    contribute zero winning games).
    """
    pick = rules.pick_count
    lo_tier = min(rules.prize_tiers)
    if not (rules.pick_count <= n_picked):
        raise ValueError(f"n_picked ({n_picked}) must be >= pick_count ({pick})")

    matrix: Dict[int, Dict[int, int]] = {}
    for hits in range(lo_tier, pick + 1):
        row: Dict[int, int] = {}
        for tier in rules.prize_tiers:
            row[tier] = 0 if tier > hits else comb(hits, tier) * comb(n_picked - hits, pick - tier)
        matrix[hits] = row
    return matrix


def hit_probability(rules: DrawRules, n_picked: int, hits: int) -> float:
    """
    P(exactly `hits` of the `pick_count` drawn numbers fall inside an
    `n_picked`-number ticket), under the fair-game / uninformed-selection
    assumption — i.e. treating the ticket as a uniformly random subset of the
    pool (hypergeometric distribution). This is the mathematically correct
    baseline regardless of *which* n numbers were chosen — see the
    `PoolOptimizer` docstring for why structural filters don't change it.
    """
    lo, hi = rules.number_range
    pool = hi - lo + 1
    pick = rules.pick_count
    denom = comb(pool, n_picked)
    if denom == 0:
        return 0.0
    return comb(pick, hits) * comb(pool - pick, n_picked - hits) / denom


# ---------------------------------------------------------------------------
# Expected value
# ---------------------------------------------------------------------------


@dataclass
class UnfoldedBetEV:
    n_picked: int
    n_games: int
    cost: float
    expected_games_won: Dict[int, float]
    expected_payout: Dict[int, float]
    total_expected_payout: float
    net_ev: float
    roi_pct: float
    p_any_prize: float

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"UnfoldedBetEV(n={self.n_picked}, games={self.n_games}, "
            f"cost={self.cost:.2f}, net_ev={self.net_ev:.2f}, roi={self.roi_pct:.2f}%, "
            f"p_any_prize={self.p_any_prize:.4f})"
        )


def evaluate(
    rules: DrawRules,
    n_picked: int,
    prize_table: Dict[int, float],
    ticket_price: Optional[float] = None,
) -> UnfoldedBetEV:
    """
    Expected value of one single unfolded ticket of `n_picked` numbers.

    `prize_table` maps tier -> prize amount. Fixed lower tiers (11-13 for
    Lotofácil) are stable Caixa constants; the top 1-2 tiers are pari-mutuel
    and fluctuate per draw — pull live values from the draw's raw API payload
    via `DrawRepository` rather than hardcoding them in production.
    """
    price = ticket_price if ticket_price is not None else rules.ticket_price
    pick = rules.pick_count
    n_games = comb(n_picked, pick)
    cost = n_games * price

    matrix = multiplier_matrix(rules, n_picked)
    expected_games_won: Dict[int, float] = {t: 0.0 for t in rules.prize_tiers}
    for hits, row in matrix.items():
        p_hits = hit_probability(rules, n_picked, hits)
        for tier, games in row.items():
            expected_games_won[tier] += p_hits * games

    expected_payout = {
        t: expected_games_won[t] * prize_table.get(t, 0.0) for t in rules.prize_tiers
    }
    total_expected_payout = sum(expected_payout.values())
    net_ev = total_expected_payout - cost
    roi_pct = (net_ev / cost * 100.0) if cost else 0.0

    lo_tier = min(rules.prize_tiers)
    p_any_prize = sum(hit_probability(rules, n_picked, h) for h in range(lo_tier, pick + 1))

    return UnfoldedBetEV(
        n_picked=n_picked,
        n_games=n_games,
        cost=cost,
        expected_games_won=expected_games_won,
        expected_payout=expected_payout,
        total_expected_payout=total_expected_payout,
        net_ev=net_ev,
        roi_pct=roi_pct,
        p_any_prize=p_any_prize,
    )


@dataclass
class BetConfiguration:
    """One leg of a capital-allocation comparison, e.g. '4x18' = copies=4, n_picked=18."""

    label: str
    n_picked: int
    copies: int = 1


@dataclass
class ConfigurationComparison:
    label: str
    n_picked: int
    copies: int
    total_cost: float
    total_expected_payout: float
    net_ev: float
    roi_pct: float
    p_any_prize_per_ticket: float
    # Upper/lower bound on "at least one ticket wins something", depending on
    # how correlated the `copies` tickets are (shared vs. disjoint numbers).
    p_any_prize_union_independent_bound: float


def compare_configurations(
    rules: DrawRules,
    configs: list[BetConfiguration],
    prize_table: Dict[int, float],
    ticket_price: Optional[float] = None,
) -> list[ConfigurationComparison]:
    """
    Compare capital-allocation strategies (e.g. 1x19 vs. 4x18). EV and cost
    scale linearly with `copies` regardless of correlation between tickets
    (linearity of expectation), but P(at least one ticket wins) depends
    heavily on how much the `copies` tickets' numbers overlap — this function
    reports the *independent-tickets upper bound* only; real syndicates
    typically share a "core" of numbers across tickets, which pulls the true
    value down toward `p_any_prize_per_ticket`.
    """
    out = []
    for cfg in configs:
        single = evaluate(rules, cfg.n_picked, prize_table, ticket_price)
        p_single = single.p_any_prize
        p_union_bound = 1.0 - (1.0 - p_single) ** cfg.copies
        out.append(
            ConfigurationComparison(
                label=cfg.label,
                n_picked=cfg.n_picked,
                copies=cfg.copies,
                total_cost=single.cost * cfg.copies,
                total_expected_payout=single.total_expected_payout * cfg.copies,
                net_ev=single.net_ev * cfg.copies,
                roi_pct=single.roi_pct,  # ROI% is copy-count invariant
                p_any_prize_per_ticket=p_single,
                p_any_prize_union_independent_bound=p_union_bound,
            )
        )
    return out
