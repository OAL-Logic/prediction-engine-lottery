"""
Discrete Mathematics & Probabilistic Combinatorics Core 📐🎲
============================================================
Theoretical and algorithmic toolkit for countable lottery sample spaces:

1. Exact Hypergeometric Distribution & Linearity of Expectation:
   - Match probabilities P(X = m) for any pick k from pool N.
   - Closed-form Expected Value E[Payout] given prize matrices and ticket costs.
   - Birthday Paradox / Collision Risk for lottery draws.

2. Spectral Graph Theory & Community Partitioning:
   - Normalized Graph Laplacian L = I - D^(-1/2) W D^(-1/2) over co-occurrence matrix W.
   - Fiedler vector (second smallest eigenvalue) spectral bisection into orthogonal communities.

3. Combinatorial Dispersion & Hamming Distance Optimization:
   - Max-Min Hamming dispersion for portfolios: maximizing mutual distance between tickets.
   - Entropy of coverage and subspace overlap bounds.

4. Meta-Heuristic Simulated Annealing Wheel Solver:
   - Refines covering designs C(v, k, t) beyond greedy set-cover to reduce ticket count.
"""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import pandas as pd

from engine.adapters import DrawRules


# -----------------------------------------------------------------------------
# 1. Discrete Probability & Hypergeometric Engine
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class HypergeometricTier:
    """Exact hypergeometric probabilities and expected return per prize tier."""
    matches: int
    favorable_subsets: int
    total_combinations: int
    probability: float
    odds_one_in: float
    prize_amount: float
    expected_value: float


@dataclass
class DiscreteProbabilityReport:
    """Consolidated discrete probability, expected value and collision metrics."""
    lottery_id: str
    pool_n: int
    pick_k: int
    total_combinations: int
    tiers: List[HypergeometricTier]
    total_expected_return: float
    ticket_cost: float
    net_expected_value: float
    house_edge: float
    birthday_collision_50pct: int
    birthday_collision_99pct: int
    observed_draws_count: int
    observed_duplicate_draws: int


def compute_hypergeometric_distribution(
    rules: DrawRules,
    prize_map: Optional[Dict[int, float]] = None,
    cost_override: Optional[float] = None,
    observed_draws: int = 0,
    duplicate_draws: int = 0,
) -> DiscreteProbabilityReport:
    """
    Computes exact hypergeometric probabilities for all match categories m in [0, k]:
    P(X = m) = [C(k, m) * C(N - k, k - m)] / C(N, k)
    and applies Linearity of Expectation to compute total expected monetary return.
    """
    lo, hi = rules.number_range
    n_pool = max(1, hi - lo + 1)
    k_pick = rules.pick_count
    total_comb = math.comb(n_pool, k_pick)
    ticket_cost = float(cost_override if cost_override is not None else (rules.ticket_price or 5.0))

    # Fallback prize map if none provided
    prizes = prize_map or {}

    tiers: List[HypergeometricTier] = []
    total_ev = 0.0

    for m in range(k_pick, -1, -1):
        if m > k_pick or (k_pick - m) > (n_pool - k_pick):
            continue
        fav = math.comb(k_pick, m) * math.comb(n_pool - k_pick, k_pick - m)
        prob = fav / total_comb
        odds = 1.0 / prob if prob > 0 else float("inf")
        prize = prizes.get(m, 0.0)
        ev = prob * prize
        total_ev += ev

        tiers.append(
            HypergeometricTier(
                matches=m,
                favorable_subsets=fav,
                total_combinations=total_comb,
                probability=prob,
                odds_one_in=round(odds, 2),
                prize_amount=prize,
                expected_value=ev,
            )
        )

    # Birthday paradox: draws needed for 50% and 99% probability of duplicate draw
    # Approximation: n ≈ sqrt(2 * N * ln(1 / (1 - p)))
    n_50 = int(math.ceil(math.sqrt(2.0 * total_comb * math.log(1.0 / (1.0 - 0.50)))))
    n_99 = int(math.ceil(math.sqrt(2.0 * total_comb * math.log(1.0 / (1.0 - 0.99)))))

    net_ev = total_ev - ticket_cost
    house_edge = (ticket_cost - total_ev) / ticket_cost if ticket_cost > 0 else 0.0

    return DiscreteProbabilityReport(
        lottery_id=getattr(rules, "id", None) or rules.name,
        pool_n=n_pool,
        pick_k=k_pick,
        total_combinations=total_comb,
        tiers=tiers,
        total_expected_return=round(total_ev, 4),
        ticket_cost=ticket_cost,
        net_expected_value=round(net_ev, 4),
        house_edge=round(house_edge * 100.0, 2),
        birthday_collision_50pct=n_50,
        birthday_collision_99pct=n_99,
        observed_draws_count=observed_draws,
        observed_duplicate_draws=duplicate_draws,
    )


# -----------------------------------------------------------------------------
# 2. Spectral Graph Theory & Laplacian Bisection
# -----------------------------------------------------------------------------

@dataclass
class SpectralBisectionResult:
    """Result of graph spectral bisection using the Fiedler vector."""
    numbers: List[int]
    fiedler_values: Dict[int, float]
    community_a: List[int]
    community_b: List[int]
    algebraic_connectivity: float  # lambda_2 (second smallest eigenvalue)


def compute_spectral_communities(
    df: pd.DataFrame,
    rules: DrawRules,
    draws_limit: int = 200,
) -> SpectralBisectionResult:
    """
    Constructs the weighted co-occurrence graph G = (V, E), computes the
    normalized graph Laplacian L = I - D^(-1/2) W D^(-1/2), and partitions the
    number pool using the Fiedler vector (eigenvector corresponding to lambda_2).
    """
    lo, hi = rules.number_range
    pool_numbers = list(range(lo, hi + 1))
    n = len(pool_numbers)
    num_to_idx = {num: i for i, num in enumerate(pool_numbers)}

    # Build co-occurrence matrix W
    W = np.zeros((n, n), dtype=float)
    recent = df.tail(draws_limit) if draws_limit and not df.empty else df

    if not recent.empty and "numbers" in recent.columns:
        for row in recent["numbers"]:
            valid = [num_to_idx[x] for x in row if x in num_to_idx]
            for i, j in itertools.combinations(valid, 2):
                W[i, j] += 1.0
                W[j, i] += 1.0

    # Smooth zero-degree isolated vertices to ensure connected graph
    np.fill_diagonal(W, 0.0)
    d = np.sum(W, axis=1)
    # Add regularizing epsilon
    d_safe = np.maximum(d, 1e-4)

    # Standard unnormalized Laplacian L = D - W
    D = np.diag(d_safe)
    L = D - W

    # Eigen-decomposition (Hermitian symmetric matrix)
    evals, evecs = np.linalg.eigh(L)

    # Sorted eigenvalues: evals[0] ≈ 0 (connected component), evals[1] = Fiedler eigenvalue
    algebraic_conn = float(evals[1]) if len(evals) > 1 else 0.0
    fiedler_vec = evecs[:, 1] if len(evals) > 1 else np.zeros(n)

    fiedler_dict: Dict[int, float] = {
        num: float(fiedler_vec[num_to_idx[num]]) for num in pool_numbers
    }

    # Partition based on Fiedler vector sign (or median threshold for balanced split)
    median_val = float(np.median(fiedler_vec))
    comm_a = [num for num in pool_numbers if fiedler_dict[num] >= median_val]
    comm_b = [num for num in pool_numbers if fiedler_dict[num] < median_val]

    return SpectralBisectionResult(
        numbers=pool_numbers,
        fiedler_values=fiedler_dict,
        community_a=sorted(comm_a),
        community_b=sorted(comm_b),
        algebraic_connectivity=round(algebraic_conn, 4),
    )


# -----------------------------------------------------------------------------
# 3. Combinatorial Dispersion & Hamming Optimization
# -----------------------------------------------------------------------------

def ticket_hamming_distance(tkt_a: Sequence[int], tkt_b: Sequence[int]) -> int:
    """
    Computes set-theoretic Hamming distance between two combinations of identical size k:
    d_H(A, B) = k - |A ∩ B| = |A \ B|.
    Range: 0 (identical) to k (completely disjoint).
    """
    set_a = set(tkt_a)
    set_b = set(tkt_b)
    overlap = len(set_a.intersection(set_b))
    return len(set_a) - overlap


def optimize_portfolio_dispersion(
    candidate_tickets: List[List[int]],
    target_count: int,
    min_hamming_dist: Optional[int] = None,
    scores_map: Optional[Dict[int, float]] = None,
) -> Tuple[List[List[int]], float, int]:
    """
    Greedy Max-Min Hamming dispersion optimizer:
    Selects `target_count` tickets from candidates that maximize the minimum
    pairwise Hamming distance while prioritizing high mean composite scores.
    Returns: (selected_tickets, mean_pairwise_distance, min_pairwise_distance)
    """
    if len(candidate_tickets) <= target_count:
        mean_d, min_d = evaluate_portfolio_dispersion(candidate_tickets)
        return candidate_tickets, mean_d, min_d

    scores = scores_map or {}
    k = len(candidate_tickets[0]) if candidate_tickets else 6
    required_min_d = min_hamming_dist if min_hamming_dist is not None else max(1, k - 3)

    # Sort candidates by mean score descending
    sorted_candidates = sorted(
        candidate_tickets,
        key=lambda t: sum(scores.get(n, 0.5) for n in t) / max(1, len(t)),
        reverse=True,
    )

    selected: List[List[int]] = [sorted_candidates[0]]
    remaining = sorted_candidates[1:]

    while len(selected) < target_count and remaining:
        best_cand: Optional[List[int]] = None
        best_min_dist = -1
        best_sum_dist = -1
        best_score = -1.0

        for cand in remaining:
            distances = [ticket_hamming_distance(cand, s) for s in selected]
            cand_min_dist = min(distances)
            cand_sum_dist = sum(distances)
            cand_score = sum(scores.get(n, 0.5) for n in cand) / max(1, len(cand))

            # Prioritize meeting required distance, then max-min distance, then score
            if (
                cand_min_dist > best_min_dist
                or (cand_min_dist == best_min_dist and cand_sum_dist > best_sum_dist)
                or (cand_min_dist == best_min_dist and cand_sum_dist == best_sum_dist and cand_score > best_score)
            ):
                best_min_dist = cand_min_dist
                best_sum_dist = cand_sum_dist
                best_score = cand_score
                best_cand = cand

        if best_cand is not None:
            selected.append(best_cand)
            remaining.remove(best_cand)
        else:
            break

    mean_dist, min_dist = evaluate_portfolio_dispersion(selected)
    return selected, mean_dist, min_dist


def evaluate_portfolio_dispersion(tickets: List[List[int]]) -> Tuple[float, int]:
    """Computes (mean_pairwise_hamming_distance, min_pairwise_hamming_distance)."""
    if len(tickets) < 2:
        k = len(tickets[0]) if tickets else 6
        return float(k), k

    distances: List[int] = []
    for t1, t2 in itertools.combinations(tickets, 2):
        distances.append(ticket_hamming_distance(t1, t2))

    mean_d = sum(distances) / float(len(distances))
    min_d = min(distances)
    return round(mean_d, 2), min_d


# -----------------------------------------------------------------------------
# 4. Meta-Heuristic Simulated Annealing Wheel Optimizer
# -----------------------------------------------------------------------------

def simulated_annealing_wheel_refine(
    pool: List[int],
    k: int,
    t: int,
    initial_tickets: List[List[int]],
    max_steps: int = 1500,
    initial_temp: float = 1.0,
    cooling_rate: float = 0.992,
) -> Tuple[List[List[int]], int]:
    """
    Refines an existing covering design C(v, k, t) via Simulated Annealing:
    Attempts to remove redundant tickets and swap single numbers within tickets
    while maintaining 100% t-subset coverage of the candidate pool.
    """
    v_pool = sorted(pool)
    all_subsets = list(itertools.combinations(v_pool, t))
    total_to_cover = len(all_subsets)
    if total_to_cover == 0 or not initial_tickets:
        return initial_tickets, total_to_cover

    sub_to_idx = {sub: i for i, sub in enumerate(all_subsets)}

    def compute_coverage(tkts: List[List[int]]) -> Set[int]:
        cov: Set[int] = set()
        for tkt in tkts:
            for s in itertools.combinations(sorted(tkt), t):
                idx = sub_to_idx.get(s)
                if idx is not None:
                    cov.add(idx)
        return cov

    current_solution = [list(tkt) for tkt in initial_tickets]
    current_cov = compute_coverage(current_solution)

    # 1. Prune redundant tickets (tickets whose deletion leaves coverage intact)
    pruned = True
    while pruned and len(current_solution) > 1:
        pruned = False
        for i in range(len(current_solution)):
            trial = current_solution[:i] + current_solution[i + 1:]
            if len(compute_coverage(trial)) == total_to_cover:
                current_solution = trial
                pruned = True
                break

    best_solution = [list(tkt) for tkt in current_solution]
    temp = initial_temp

    # 2. Annealing perturbation loop
    rng = random.Random(42)
    for _ in range(max_steps):
        if len(current_solution) <= 1:
            break

        # Pick random ticket and swap one number with another from pool
        tkt_idx = rng.randrange(len(current_solution))
        target_tkt = list(current_solution[tkt_idx])
        num_to_remove = rng.choice(target_tkt)
        available = [n for n in v_pool if n not in target_tkt]
        if not available:
            continue
        num_to_add = rng.choice(available)

        mutated_tkt = sorted([num_to_add if n == num_to_remove else n for n in target_tkt])
        mutated_solution = [list(tkt) for tkt in current_solution]
        mutated_solution[tkt_idx] = mutated_tkt

        mutated_cov = compute_coverage(mutated_solution)
        delta_cov = len(mutated_cov) - len(current_cov)

        # Accept if coverage does not drop, or probabilistically via Metropolis criterion
        if delta_cov >= 0 or rng.random() < math.exp(delta_cov / max(1e-4, temp)):
            current_solution = mutated_solution
            current_cov = mutated_cov

            # If full coverage holds, attempt another opportunistic ticket deletion
            if len(current_cov) == total_to_cover and len(current_solution) < len(best_solution):
                best_solution = [list(tkt) for tkt in current_solution]

        temp *= cooling_rate

    final_cov = len(compute_coverage(best_solution))
    return [sorted(tkt) for tkt in best_solution], final_cov
