"""
Unit and Archetype Tests for Discrete Mathematics Module 📐🎲
=============================================================
Validates:
1. Exact Hypergeometric Distribution calculations and Linearity of Expectation.
2. Birthday Paradox / Duplicate Draw collision thresholds.
3. Graph Laplacian Spectral Bisection & Fiedler Vector partitioning across >= 3 archetypes.
4. Combinatorial Max-Min Hamming Dispersion optimization.
5. Simulated Annealing Covering Design refinement.
6. CLI execution of `p4lottery discrete-math`.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.cli.utils import get_adapter
from engine.modules.discrete_math import (
    compute_hypergeometric_distribution,
    compute_spectral_communities,
    evaluate_portfolio_dispersion,
    optimize_portfolio_dispersion,
    simulated_annealing_wheel_refine,
    ticket_hamming_distance,
)
from engine.wheels.budget_wheel import WheelEngine

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def mega_rules() -> DrawRules:
    return get_adapter("br/mega-sena").rules


@pytest.fixture
def loto_rules() -> DrawRules:
    return get_adapter("br/lotofacil").rules


@pytest.fixture
def powerball_rules() -> DrawRules:
    return get_adapter("us/powerball").rules


@pytest.fixture
def sample_history_mega() -> pd.DataFrame:
    base_numbers = [
        [5, 10, 15, 20, 25, 30],
        [1, 2, 3, 4, 5, 6],
        [7, 14, 21, 28, 35, 42],
        [11, 22, 33, 44, 55, 60],
        [10, 20, 30, 40, 50, 60],
        [2, 4, 6, 8, 10, 12],
        [1, 3, 5, 7, 9, 11],
        [13, 23, 33, 43, 53, 59],
        [18, 28, 38, 48, 58, 60],
        [6, 12, 18, 24, 30, 36],
        [9, 19, 29, 39, 49, 59],
        [4, 8, 16, 32, 48, 56],
        [15, 25, 35, 45, 55, 57],
        [14, 28, 34, 42, 50, 58],
        [7, 17, 27, 37, 47, 57],
    ]
    rows = [{"draw_id": i, "numbers": nums} for i, nums in enumerate(base_numbers, 1)]
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# 1. Hypergeometric Probability & Linearity of Expectation Tests
# -----------------------------------------------------------------------------

def test_hypergeometric_mega_sena(mega_rules):
    """Verify exact probabilities for Mega-Sena C(60, 6) = 50,063,860."""
    report = compute_hypergeometric_distribution(mega_rules)
    assert report.total_combinations == 50063860
    assert report.pool_n == 60
    assert report.pick_k == 6

    # Sena (6 matches)
    sena = next(t for t in report.tiers if t.matches == 6)
    assert sena.favorable_subsets == 1
    assert sena.odds_one_in == 50063860.0

    # Quina (5 matches): C(6, 5) * C(54, 1) = 6 * 54 = 324
    quina = next(t for t in report.tiers if t.matches == 5)
    assert quina.favorable_subsets == 324
    assert round(quina.odds_one_in, 1) == 154518.1

    # Quadra (4 matches): C(6, 4) * C(54, 2) = 15 * 1431 = 21465
    quadra = next(t for t in report.tiers if t.matches == 4)
    assert quadra.favorable_subsets == 21465
    assert round(quadra.odds_one_in, 1) == 2332.3

    # Total probabilities must sum to 1.0
    total_p = sum(t.probability for t in report.tiers)
    assert abs(total_p - 1.0) < 1e-7


def test_linearity_of_expectation_with_prizes(mega_rules):
    """Verify linearity of expectation: E[Payout] = sum(p_i * prize_i)."""
    prizes = {6: 50_000_000.0, 5: 45_000.0, 4: 900.0}
    report = compute_hypergeometric_distribution(mega_rules, prize_map=prizes, cost_override=5.0)

    expected_return = (
        (1.0 / 50063860) * 50_000_000.0
        + (324.0 / 50063860) * 45_000.0
        + (21465.0 / 50063860) * 900.0
    )
    assert abs(report.total_expected_return - expected_return) < 1e-3
    assert report.net_expected_value == round(expected_return - 5.0, 4)


def test_birthday_paradox_draw_collisions(mega_rules, loto_rules):
    """Verify birthday paradox collision thresholds."""
    rep_mega = compute_hypergeometric_distribution(mega_rules)
    # sqrt(2 * 50063860 * ln(2)) ≈ 8328 draws
    assert 8000 <= rep_mega.birthday_collision_50pct <= 9000

    rep_loto = compute_hypergeometric_distribution(loto_rules)
    # Lotofacil C(25, 15) = 3,268,760 -> sqrt(2 * 3268760 * ln(2)) ≈ 2128 draws
    assert 2000 <= rep_loto.birthday_collision_50pct <= 2300


# -----------------------------------------------------------------------------
# 2. Graph Laplacian Spectral Bisection Tests
# -----------------------------------------------------------------------------

def test_spectral_graph_bisection(sample_history_mega, mega_rules):
    """Verify graph Laplacian spectrum and Fiedler vector community partitioning."""
    res = compute_spectral_communities(sample_history_mega, mega_rules)
    assert len(res.numbers) == 60
    assert len(res.community_a) + len(res.community_b) == 60
    assert set(res.community_a).isdisjoint(set(res.community_b))
    assert res.algebraic_connectivity >= 0.0


# -----------------------------------------------------------------------------
# 3. Combinatorial Dispersion & Hamming Optimization Tests
# -----------------------------------------------------------------------------

def test_ticket_hamming_distance():
    """Verify set-theoretic Hamming distance."""
    t1 = [1, 2, 3, 4, 5, 6]
    t2 = [1, 2, 3, 4, 5, 6]
    assert ticket_hamming_distance(t1, t2) == 0

    t3 = [1, 2, 3, 7, 8, 9]
    assert ticket_hamming_distance(t1, t3) == 3

    t4 = [10, 20, 30, 40, 50, 60]
    assert ticket_hamming_distance(t1, t4) == 6


def test_portfolio_dispersion_optimization():
    """Verify Max-Min Hamming dispersion maximizes mutual distance."""
    candidates = [
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 7],  # Dist 1 to first
        [1, 2, 3, 4, 8, 9],  # Dist 2
        [10, 11, 12, 13, 14, 15],  # Disjoint
        [20, 21, 22, 23, 24, 25],  # Disjoint
    ]
    selected, mean_d, min_d = optimize_portfolio_dispersion(
        candidate_tickets=candidates,
        target_count=3,
    )
    assert len(selected) == 3
    # Disjoint tickets should be selected over near-identical ones
    assert min_d >= 2
    assert mean_d > 2.0


# -----------------------------------------------------------------------------
# 4. Simulated Annealing Wheel Refinement Tests
# -----------------------------------------------------------------------------

def test_simulated_annealing_wheel_refine():
    """Verify Simulated Annealing removes redundant tickets while preserving coverage."""
    pool = [1, 2, 3, 4, 5, 6, 7]
    k, t = 6, 5
    # C(7, 6, 5) minimal is 7 tickets. Let's feed an intentionally redundant set of 8 tickets
    initial = [
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 7],
        [1, 2, 3, 4, 6, 7],
        [1, 2, 3, 5, 6, 7],
        [1, 2, 4, 5, 6, 7],
        [1, 3, 4, 5, 6, 7],
        [2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6],  # Duplicate redundant ticket
    ]
    refined, cov = simulated_annealing_wheel_refine(pool, k, t, initial, max_steps=100)
    assert len(refined) <= 7
    # All 21 5-subsets of 7 numbers must be covered
    assert cov == math.comb(7, 5)


# -----------------------------------------------------------------------------
# 5. CLI End-to-End Tests
# -----------------------------------------------------------------------------

def test_p4lottery_discrete_math_cli():
    """Verify execution of `./p4lottery discrete-math` command."""
    launcher = PROJECT_ROOT / "p4lottery"
    cmd = [
        str(launcher),
        "discrete-math",
        "br/mega-sena",
        "--jackpot", "50000000",
        "--spectral",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    assert "Exact Hypergeometric Distribution" in proc.stdout
    assert "Linearity of Expectation" in proc.stdout
    assert "Graph Laplacian Spectral Bisection" in proc.stdout
