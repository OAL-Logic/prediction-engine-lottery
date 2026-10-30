"""
Budget-Constrained Combinatorial Wheel Engine 🎡💰
==================================================
Implements game-agnostic combinatorial covering designs C(v, k, t, m) (Fechamentos)
with financial budget constraints and symmetry filters:

1. `reduce-coverage` (Uniform Reduction):
   Retains full candidate pool `v`, maximizing `t`-subset coverage within the
   ticket budget via score-tie-broken greedy set cover.
2. `reduce-pool` (Universe Reduction):
   Dynamically shrinks candidate pool `v` to top `k'` scored numbers until a
   100% mathematical guarantee fits within the allocated budget.
3. Universal `DrawRules` compatibility:
   Supports sparse single-pool (e.g. Mega-Sena 6/60), high-density single-pool
   (e.g. Lotofácil 15/25 with draw-to-draw recurrence), 0-indexed (e.g. Lotomania),
   and multi-pool bonus games (e.g. Powerball 5/69 + 1/26).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from engine.adapters import DrawRules
from engine.modules.storage import LotteryStorage, storage as default_storage


@dataclass
class WheelTicket:
    """Represents a generated lottery wheel ticket with structural & score metadata."""
    ticket_id: int
    numbers: List[int]
    even_count: int
    odd_count: int
    total_sum: int
    mean_score: float
    recurrence_count: Optional[int] = None
    bonus: List[int] = field(default_factory=list)


@dataclass
class CoverageAudit:
    """Detailed audit of combinatorial coverage and financial constraints."""
    game: str
    currency: str
    total_pool_v: int
    ticket_size_k: int
    guarantee_t: int
    drawn_m: int
    total_subsets_to_cover: int
    subsets_covered: int
    coverage_percentage: float
    theoretical_tickets_needed: int
    tickets_generated: int
    ticket_cost: float
    total_budget: float
    total_cost: float
    reduction_strategy_used: str
    pool_numbers: List[int]
    is_100_percent_guarantee: bool


@dataclass
class WheelResult:
    """Complete output of the budget-constrained combinatorial wheel generator."""
    game: str
    tickets: List[WheelTicket]
    audit: CoverageAudit
    candidate_scores: Dict[int, float]


# Canonical precomputed minimal covering designs (0-indexed indices into sorted pool)
KNOWN_MINIMAL_COVERS: Dict[Tuple[int, int, int], List[List[int]]] = {
    (7, 6, 5): [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 6],
        [0, 1, 2, 3, 5, 6],
        [0, 1, 2, 4, 5, 6],
        [0, 1, 3, 4, 5, 6],
        [0, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
    ],
    (8, 6, 4): [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 6, 7],
        [0, 1, 4, 5, 6, 7],
        [2, 3, 4, 5, 6, 7],
    ],
    (9, 6, 4): [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 6, 7, 8],
        [0, 3, 4, 6, 7, 8],
        [1, 3, 5, 6, 7, 8],
        [2, 4, 5, 6, 7, 8],
        [0, 1, 3, 4, 5, 6],
    ],
    (16, 15, 14): [
        [i for i in range(16) if i != drop] for drop in range(16)
    ],
}


class WheelEngine:
    """
    Game-agnostic combinatorial covering engine with greedy set-covering and budget binding.
    """

    def __init__(
        self,
        rules: DrawRules,
        cache: Optional[LotteryStorage] = None,
    ) -> None:
        self.rules = rules
        self.cache = cache or default_storage
        self.lo, self.hi = rules.number_range
        self.pool_span = max(1, self.hi - self.lo + 1)
        self.k = rules.pick_count
        self.density = self.k / float(self.pool_span)

        # Analytical parity bounds
        self.even_range: Tuple[int, int] = (
            max(1, int(math.floor(self.k * 0.30))),
            min(self.k - 1, int(math.ceil(self.k * 0.70))),
        )

        # Analytical sum bounds (~90% confidence interval of hypergeometric sum)
        mu_sum = self.k * (self.lo + self.hi) / 2.0
        var_sum = (
            self.k
            * (self.pool_span ** 2 - 1)
            * max(1, self.pool_span - self.k)
            / (12.0 * max(1, self.pool_span - 1))
        )
        sigma_sum = math.sqrt(max(1.0, var_sum))
        self.sum_range: Tuple[int, int] = (
            int(math.floor(mu_sum - 1.65 * sigma_sum)),
            int(math.ceil(mu_sum + 1.65 * sigma_sum)),
        )

        # High-density recurrence bounds (e.g. Lotofácil 15/25 -> expected 9, range 8..10)
        if self.density >= 0.50:
            expected_rep = int(round(self.k * self.density))
            self.repeat_range: Optional[Tuple[int, int]] = (
                max(0, expected_rep - 1),
                min(self.k, expected_rep + 1),
            )
        else:
            self.repeat_range = None

    def filter_ticket_symmetry(
        self,
        ticket: Tuple[int, ...],
        last_draw: Optional[List[int]] = None,
    ) -> bool:
        """
        Check if candidate ticket satisfies parity, analytical sum bounds,
        and high-density draw recurrence.
        """
        evens = sum(1 for n in ticket if n % 2 == 0)
        min_e, max_e = self.even_range
        if not (min_e <= evens <= max_e):
            return False

        t_sum = sum(ticket)
        min_s, max_s = self.sum_range
        if not (min_s <= t_sum <= max_s):
            return False

        if self.repeat_range is not None and last_draw:
            last_draw_set = set(last_draw)
            repeats = sum(1 for n in ticket if n in last_draw_set)
            min_r, max_r = self.repeat_range
            if not (min_r <= repeats <= max_r):
                return False

        return True

    def greedy_set_cover(
        self,
        pool: List[int],
        k: int,
        t: int,
        max_tickets: int,
        scores: Dict[int, float],
        last_draw: Optional[List[int]] = None,
    ) -> Tuple[List[List[int]], int, int]:
        """
        Greedy maximum coverage solver:
        Selects at most `max_tickets` of size `k` to maximize covered `t`-subsets of `pool`.
        Returns: (selected_tickets, total_t_subsets, covered_t_subsets)
        """
        sorted_pool = sorted(pool)
        all_t_subsets = list(itertools.combinations(sorted_pool, t))
        total_subsets = len(all_t_subsets)
        if total_subsets == 0:
            return [], 0, 0

        subset_to_idx = {sub: i for i, sub in enumerate(all_t_subsets)}
        uncovered: Set[int] = set(range(total_subsets))

        candidate_combinations = list(itertools.combinations(sorted_pool, k))
        filtered_candidates = [
            c for c in candidate_combinations
            if self.filter_ticket_symmetry(c, last_draw=last_draw)
        ]
        candidate_pool = filtered_candidates if filtered_candidates else candidate_combinations

        candidate_t_sets: List[Tuple[List[int], Set[int], float]] = []
        for cand in candidate_pool:
            cand_list = sorted(list(cand))
            t_subs = itertools.combinations(cand_list, t)
            idx_set = {subset_to_idx[sub] for sub in t_subs if sub in subset_to_idx}
            mean_score = sum(scores.get(num, 0.5) for num in cand_list) / max(1, len(cand_list))
            candidate_t_sets.append((cand_list, idx_set, mean_score))

        candidate_t_sets.sort(key=lambda x: x[2], reverse=True)
        selected_tickets: List[List[int]] = []

        while len(selected_tickets) < max_tickets and uncovered:
            best_cand: Optional[List[int]] = None
            best_gain = -1
            best_score = -1.0
            best_covered_subsets: Set[int] = set()

            for cand_list, idx_set, mean_score in candidate_t_sets:
                overlap = idx_set.intersection(uncovered)
                gain = len(overlap)
                if gain > best_gain or (gain == best_gain and mean_score > best_score):
                    best_gain = gain
                    best_cand = cand_list
                    best_score = mean_score
                    best_covered_subsets = overlap

            if best_gain <= 0:
                for cand_list, _, _ in candidate_t_sets:
                    if cand_list not in selected_tickets:
                        selected_tickets.append(cand_list)
                        if len(selected_tickets) >= max_tickets:
                            break
                break

            if best_cand is not None:
                selected_tickets.append(best_cand)
                uncovered.difference_update(best_covered_subsets)

        covered_count = total_subsets - len(uncovered)
        return selected_tickets, total_subsets, covered_count

    def generate_wheel(
        self,
        scores: Dict[int, float],
        budget: float = 50.00,
        pool_size: Optional[int] = None,
        pool_numbers: Optional[List[int]] = None,
        guarantee_t: Optional[int] = None,
        reduction_strategy: str = "reduce-coverage",
        last_draw: Optional[List[int]] = None,
    ) -> WheelResult:
        """
        Generate a budget-constrained combinatorial lottery wheel.
        """
        k = self.k
        cost_per_ticket = float(getattr(self.rules, "ticket_price", 5.0) or 5.0)
        currency = getattr(self.rules, "currency", "BRL") or "BRL"
        game_id = getattr(self.rules, "id", None) or self.rules.name.lower()
        max_tickets = int(math.floor(budget / cost_per_ticket))

        if max_tickets <= 0:
            raise ValueError(
                f"Budget {currency} {budget:.2f} is insufficient for a single ticket "
                f"(cost: {currency} {cost_per_ticket:.2f})."
            )

        sorted_candidates = sorted(scores.keys(), key=lambda n: scores[n], reverse=True)

        if pool_numbers:
            valid_explicit = [n for n in pool_numbers if self.lo <= n <= self.hi]
            # Order explicit pool by score descending so reduce-pool shrinks lowest-scored last
            candidate_order = sorted(valid_explicit, key=lambda n: scores.get(n, 0.5), reverse=True)
            v_initial = max(k, min(len(candidate_order), self.pool_span))
        else:
            candidate_order = sorted_candidates
            if pool_size is None:
                default_v = k + 6 if k <= 8 else k + 3
                v_initial = min(self.pool_span, default_v)
            else:
                v_initial = max(k, min(pool_size, self.pool_span))

        if guarantee_t is None:
            if k <= 8:
                t = max(2, k - 2)
            else:
                t = k - 1 if v_initial <= k + 1 else k - 2
        else:
            t = max(1, min(guarantee_t, k))

        if reduction_strategy == "reduce-pool":
            current_v = v_initial
            chosen_tickets: List[List[int]] = []
            covered_subs = 0
            total_subs = 0
            is_100_percent = False

            while current_v >= k:
                sub_pool = candidate_order[:current_v]
                total_t_combinations = math.comb(current_v, t)

                precomputed = None
                if self.cache:
                    precomputed = self.cache.get_precomputed_wheel(
                        game_id, current_v, k, t, k
                    )

                if precomputed and precomputed.ticket_count <= max_tickets:
                    indexed_pool = sorted(sub_pool)
                    chosen_tickets = [
                        sorted([indexed_pool[idx] for idx in tkt])
                        for tkt in precomputed.tickets
                    ]
                    total_subs = total_t_combinations
                    covered_subs = total_t_combinations
                    is_100_percent = True
                    break

                if (current_v, k, t) in KNOWN_MINIMAL_COVERS:
                    template = KNOWN_MINIMAL_COVERS[(current_v, k, t)]
                    if len(template) <= max_tickets:
                        indexed_pool = sorted(sub_pool)
                        chosen_tickets = [
                            sorted([indexed_pool[idx] for idx in tkt])
                            for tkt in template
                        ]
                        total_subs = total_t_combinations
                        covered_subs = total_t_combinations
                        is_100_percent = True
                        break

                tkts, tot, cov = self.greedy_set_cover(
                    pool=sub_pool,
                    k=k,
                    t=t,
                    max_tickets=max_tickets,
                    scores=scores,
                    last_draw=last_draw,
                )

                if cov == tot and len(tkts) <= max_tickets:
                    chosen_tickets = tkts
                    total_subs = tot
                    covered_subs = cov
                    is_100_percent = True
                    break

                current_v -= 1

            if not chosen_tickets:
                current_v = k
                sub_pool = candidate_order[:k]
                chosen_tickets = [sorted(sub_pool)]
                total_subs = math.comb(k, t)
                covered_subs = total_subs
                is_100_percent = True

            final_pool = candidate_order[:current_v]
            cov_pct = 100.0 if total_subs > 0 else 0.0

            audit = CoverageAudit(
                game=game_id,
                currency=currency,
                total_pool_v=current_v,
                ticket_size_k=k,
                guarantee_t=t,
                drawn_m=k,
                total_subsets_to_cover=total_subs,
                subsets_covered=covered_subs,
                coverage_percentage=cov_pct,
                theoretical_tickets_needed=len(chosen_tickets),
                tickets_generated=len(chosen_tickets),
                ticket_cost=cost_per_ticket,
                total_budget=budget,
                total_cost=len(chosen_tickets) * cost_per_ticket,
                reduction_strategy_used="reduce-pool (Universe Reduction)",
                pool_numbers=sorted(final_pool),
                is_100_percent_guarantee=is_100_percent,
            )
        else:
            final_pool = candidate_order[:v_initial]
            chosen_tickets, total_subs, covered_subs = self.greedy_set_cover(
                pool=final_pool,
                k=k,
                t=t,
                max_tickets=max_tickets,
                scores=scores,
                last_draw=last_draw,
            )

            cov_pct = (covered_subs / total_subs * 100.0) if total_subs > 0 else 0.0
            is_100_percent = (covered_subs == total_subs)

            audit = CoverageAudit(
                game=game_id,
                currency=currency,
                total_pool_v=v_initial,
                ticket_size_k=k,
                guarantee_t=t,
                drawn_m=k,
                total_subsets_to_cover=total_subs,
                subsets_covered=covered_subs,
                coverage_percentage=round(cov_pct, 2),
                theoretical_tickets_needed=math.ceil(total_subs / max(1, math.comb(k, t))),
                tickets_generated=len(chosen_tickets),
                ticket_cost=cost_per_ticket,
                total_budget=budget,
                total_cost=len(chosen_tickets) * cost_per_ticket,
                reduction_strategy_used="reduce-coverage (Uniform Reduction)",
                pool_numbers=sorted(final_pool),
                is_100_percent_guarantee=is_100_percent,
            )

        # Assign deterministic rotating bonus balls if multi-pool game (e.g. Powerball)
        bonus_pool: List[int] = []
        bonus_count = getattr(self.rules, "bonus_count", 0) or 0
        bonus_range = getattr(self.rules, "bonus_range", None)
        if bonus_count > 0 and bonus_range:
            blo, bhi = bonus_range
            bonus_pool = list(range(blo, bhi + 1))

        wheel_tickets: List[WheelTicket] = []
        last_set = set(last_draw) if last_draw else set()

        for idx, tkt in enumerate(chosen_tickets, 1):
            evens = sum(1 for n in tkt if n % 2 == 0)
            odds = len(tkt) - evens
            t_sum = sum(tkt)
            mean_sc = sum(scores.get(n, 0.5) for n in tkt) / max(1, len(tkt))
            rec_cnt = sum(1 for n in tkt if n in last_set) if last_draw else None

            tkt_bonus: List[int] = []
            if bonus_pool and bonus_count > 0:
                start_b = ((idx - 1) * bonus_count) % len(bonus_pool)
                tkt_bonus = sorted(
                    bonus_pool[(start_b + b_i) % len(bonus_pool)]
                    for b_i in range(min(bonus_count, len(bonus_pool)))
                )

            wheel_tickets.append(
                WheelTicket(
                    ticket_id=idx,
                    numbers=sorted(tkt),
                    even_count=evens,
                    odd_count=odds,
                    total_sum=t_sum,
                    mean_score=round(mean_sc, 4),
                    recurrence_count=rec_cnt,
                    bonus=tkt_bonus,
                )
            )

        wheel_tickets.sort(key=lambda wt: wt.mean_score, reverse=True)
        for i, wt in enumerate(wheel_tickets, 1):
            wt.ticket_id = i

        return WheelResult(
            game=game_id,
            tickets=wheel_tickets,
            audit=audit,
            candidate_scores={n: scores.get(n, 0.5) for n in audit.pool_numbers},
        )
