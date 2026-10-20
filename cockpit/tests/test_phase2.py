"""
Phase 2 Test Suite: Combinatorial Filters, Fault Tolerance, Wheeling & Streaming
================================================================================
Comprehensive verification for Phase 2:
1. 105+ Filter Catalog across 7 categories
2. Vectorized NumPy Chunk Filter Evaluation
3. Fault Tolerance Engine (AND, OR, RANGE)
4. Covering Wheeling Solver (Full, Abbreviated, Banker Keys, Hamming Pruning)
5. Condition Optimizer & Historical Backtester
6. Streaming Combinatorial Worker (Telemetry & Cooperative Cancellation)
"""

import pytest
import numpy as np
from typing import List

from cockpit.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, ToleranceMode,
    WheelingConfig, WheelType, TicketReceipt, GenerationTelemetry
)
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.services.wheeling_solver import WheelingSolver
from cockpit.src.services.condition_optimizer import ConditionOptimizer
from cockpit.src.services.streaming_worker import StreamingCombinatorialWorker


@pytest.fixture
def bridge() -> EngineBridge:
    return EngineBridge()


@pytest.fixture
def lotofacil_game(bridge: EngineBridge) -> GameSchema:
    game = bridge.get_game("br/lotofacil")
    assert game is not None
    return game


@pytest.fixture
def megasena_game(bridge: EngineBridge) -> GameSchema:
    game = bridge.get_game("br/mega-sena")
    assert game is not None
    return game


def test_catalog_105_plus_filters(lotofacil_game: GameSchema, bridge: EngineBridge):
    """Verifies that the catalog contains 105+ unique filters across 7 categories."""
    filters = bridge.load_catalog_filters(lotofacil_game)
    assert len(filters) >= 105, f"Expected >= 105 filters, got {len(filters)}"

    # Check uniqueness of IDs
    ids = [f.id for f in filters]
    assert len(ids) == len(set(ids)), f"Duplicate filter IDs detected: {len(ids)} vs {len(set(ids))}"

    # Check 7 categories
    categories = {f.category for f in filters}
    expected_categories = {
        "Structural / Count",
        "Sums & Averages",
        "Positional & Distance",
        "Complexity & Repeats",
        "Algebraic Residue",
        "Decades & Units",
        "Advanced & Sets"
    }
    assert expected_categories.issubset(categories), f"Missing categories: {expected_categories - categories}"

    for cat in expected_categories:
        cat_filters = [f for f in filters if f.category == cat]
        assert len(cat_filters) >= 5, f"Category '{cat}' has fewer than 5 filters: {len(cat_filters)}"


def test_vectorized_filter_chunk_evaluation(lotofacil_game: GameSchema, bridge: EngineBridge):
    """Verifies vectorized NumPy evaluation against known combinatorial matrices."""
    # Test matrix: 3 tickets of size 6
    combos = np.array([
        [1, 2, 3, 4, 5, 6],       # Odds: 3, Evens: 3, Sum: 21, Min: 1, Max: 6
        [2, 4, 6, 8, 10, 12],     # Odds: 0, Evens: 6, Sum: 42, Min: 2, Max: 12
        [1, 3, 5, 7, 9, 11]       # Odds: 6, Evens: 0, Sum: 36, Min: 1, Max: 11
    ], dtype=np.uint8)

    filters = [
        FilterNode(id="structural_odd_count", name="Odd Count", category="Structural", min_val=2, max_val=4),
        FilterNode(id="structural_even_count", name="Even Count", category="Structural", min_val=4, max_val=6),
        FilterNode(id="structural_number_sum", name="Number Sum", category="Sums", min_val=20, max_val=30),
        FilterNode(id="positional_min_number", name="Min Number", category="Positional", min_val=2, max_val=5),
    ]

    pass_matrix = bridge.evaluate_filter_chunk_vectorized(combos, filters, game=lotofacil_game)
    assert pass_matrix.shape == (3, 4)

    # Filter 0: Odd count in [2, 4] -> Combo 0 passes (3 odds), Combo 1 fails (0), Combo 2 fails (6)
    assert pass_matrix[0, 0] == True
    assert pass_matrix[1, 0] == False
    assert pass_matrix[2, 0] == False

    # Filter 1: Even count in [4, 6] -> Combo 0 fails (3 evens), Combo 1 passes (6), Combo 2 fails (0)
    assert pass_matrix[0, 1] == False
    assert pass_matrix[1, 1] == True
    assert pass_matrix[2, 1] == False

    # Filter 2: Sum in [20, 30] -> Combo 0 passes (21), Combo 1 fails (42), Combo 2 fails (36)
    assert pass_matrix[0, 2] == True
    assert pass_matrix[1, 2] == False
    assert pass_matrix[2, 2] == False

    # Filter 3: Min number in [2, 5] -> Combo 0 fails (1), Combo 1 passes (2), Combo 2 fails (1)
    assert pass_matrix[0, 3] == False
    assert pass_matrix[1, 3] == True
    assert pass_matrix[2, 3] == False


def test_fault_tolerance_mask(bridge: EngineBridge):
    """Verifies Fault Tolerance logic for AND, OR, and RANGE N-of-M modes."""
    # 4 combinations, 3 filters:
    # Combo 0: True, True, True  (3/3)
    # Combo 1: True, True, False (2/3)
    # Combo 2: True, False, False (1/3)
    # Combo 3: False, False, False (0/3)
    pass_matrix = np.array([
        [True, True, True],
        [True, True, False],
        [True, False, False],
        [False, False, False]
    ], dtype=bool)

    # 1. Mode: AND (100% strict)
    tol_and = ToleranceRule(mode=ToleranceMode.AND)
    mask_and = bridge.apply_tolerance_mask(pass_matrix, tol_and)
    np.testing.assert_array_equal(mask_and, [True, False, False, False])

    # 2. Mode: OR (Any match)
    tol_or = ToleranceRule(mode=ToleranceMode.OR)
    mask_or = bridge.apply_tolerance_mask(pass_matrix, tol_or)
    np.testing.assert_array_equal(mask_or, [True, True, True, False])

    # 3. Mode: RANGE (Between 1 and 2 matching filters)
    tol_range = ToleranceRule(mode=ToleranceMode.RANGE, min_pass=1, max_pass=2)
    mask_range = bridge.apply_tolerance_mask(pass_matrix, tol_range)
    np.testing.assert_array_equal(mask_range, [False, True, True, False])


def test_wheeling_solver_full():
    """Verifies full wheel combinatorial expansion C(v, k) and fixed Banker keys."""
    pool = [1, 2, 3, 4, 5]
    pick = 3

    # C(5, 3) = 10
    full_wheel = WheelingSolver.generate_full_wheel(pool, pick)
    assert len(full_wheel) == 10
    for ticket in full_wheel:
        assert len(ticket) == 3
        assert len(set(ticket)) == 3

    # Key / Banker wheel: Key = [1]
    # Remaining C(4, 2) = 6
    key_wheel = WheelingSolver.generate_full_wheel(pool, pick, key_numbers=[1])
    assert len(key_wheel) == 6
    for ticket in key_wheel:
        assert 1 in ticket


def test_wheeling_solver_abbreviated_and_coverage():
    """Verifies abbreviated covering wheel generation and coverage certification."""
    pool = list(range(1, 11)) # v = 10
    pick = 5                  # k = 5
    guarantee_t = 3           # t = 3
    condition_m = 4           # m = 4

    abbrev_tickets = WheelingSolver.generate_abbreviated_wheel(
        pool=pool,
        pick_count=pick,
        guarantee_t=guarantee_t,
        condition_m=condition_m,
        max_tickets=50
    )
    assert len(abbrev_tickets) > 0
    for ticket in abbrev_tickets:
        assert len(ticket) == pick
        assert set(ticket).issubset(set(pool))

    # Evaluate coverage
    coverage_pct = WheelingSolver.evaluate_coverage(
        tickets=abbrev_tickets,
        pool=pool,
        t=guarantee_t,
        m=condition_m
    )
    assert coverage_pct >= 90.0, f"Expected high coverage, got {coverage_pct:.1f}%"


def test_hamming_redundancy_pruning():
    """Verifies that Hamming redundancy pruning drops lines with excessive overlap."""
    tickets = [
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 7],  # Overlap = 5 (diff = 1) -> should be pruned if min_distance = 2
        [10, 11, 12, 13, 14, 15] # Completely disjoint (diff = 6) -> kept
    ]

    pruned = WheelingSolver.prune_hamming_redundancy(tickets, min_distance=2)
    assert len(pruned) == 2
    assert tickets[0] in pruned
    assert tickets[2] in pruned


def test_condition_optimizer_backtest(lotofacil_game: GameSchema):
    """Verifies historical condition backtest report and choke point detection."""
    optimizer = ConditionOptimizer()
    filters = [
        FilterNode(id="structural_odd_count", name="Odd Count", category="Structural / Count", min_val=7, max_val=9, enabled=True),
        FilterNode(id="structural_number_sum", name="Number Sum", category="Sums & Averages", min_val=180, max_val=220, enabled=True),
        # Artificially strict filter that will fail on real historical draws
        FilterNode(id="structural_prime_count", name="Prime Count", category="Structural / Count", min_val=0, max_val=1, enabled=True)
    ]
    tolerance = ToleranceRule(mode=ToleranceMode.AND)

    report = optimizer.run_historical_backtest(
        game_id=lotofacil_game.id,
        filters=filters,
        tolerance=tolerance,
        draws_limit=30
    )

    assert report.total_draws_evaluated > 0
    assert 0.0 <= report.historical_hit_rate_pct <= 100.0
    assert 0.0 <= report.estimated_reduction_rate_pct <= 100.0
    # Prime count [0, 1] should be detected as a choke point for Lotofácil (which usually has 5-7 primes)
    choke_ids = [cp.filter_id for cp in report.choke_points]
    assert "structural_prime_count" in choke_ids


def test_streaming_combinatorial_worker(lotofacil_game: GameSchema):
    """Verifies background streaming worker chunk execution and cooperative cancellation."""
    pool = list(range(1, 18)) # 17 numbers -> C(17, 15) = 136 combinations
    filters = [
        FilterNode(id="structural_odd_count", name="Odd Count", category="Structural / Count", min_val=6, max_val=10, enabled=True)
    ]
    tolerance = ToleranceRule(mode=ToleranceMode.AND)

    worker = StreamingCombinatorialWorker(
        game=lotofacil_game,
        pool=pool,
        filters=filters,
        tolerance=tolerance,
        chunk_size=50,
        max_survivors_cap=100
    )

    captured_telemetry = []
    captured_survivors = []

    def on_progress(t: GenerationTelemetry):
        captured_telemetry.append(t)

    def on_finished(t: GenerationTelemetry, s: List[TicketReceipt]):
        captured_survivors.extend(s)

    worker.signals.progress.connect(on_progress)
    worker.signals.finished.connect(on_finished)

    # Run synchronously
    worker.run()

    assert len(captured_telemetry) > 0
    assert len(captured_survivors) > 0
    assert worker.is_cancelled is False

    # Test cooperative cancellation
    worker_cancel = StreamingCombinatorialWorker(
        game=lotofacil_game,
        pool=pool,
        filters=filters,
        tolerance=tolerance,
        chunk_size=10
    )
    worker_cancel.cancel()
    assert worker_cancel.is_cancelled is True
