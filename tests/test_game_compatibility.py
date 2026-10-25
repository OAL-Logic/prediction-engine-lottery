"""
Game Compatibility & Global Lottery Architecture Verification 🌐
================================================================
Validates that core engine features (geometry, patterns, hedging, filtering,
and winnings resolution) operate seamlessly across diverse global lottery archetypes:
1. Standard Sparse (e.g. Mega-Sena 6/60, Quina 5/80)
2. High-Density (e.g. Lotofácil 15/25)
3. Zero-Indexed (e.g. Lotomania 00-99)
4. Multi-Pool / Bonus Ball (e.g. US Powerball 5/69 + 1/26, +Milionária 6/50 + 2/6)
"""

from __future__ import annotations

import pytest
from engine.adapters import DrawRules
from engine.adapters.registry import registry
from engine.modules.geometry import BoardGeometry
from engine.modules.patterns import get_frame_center_logic, get_line_column_distribution
from engine.modules.hedging import CombinatorialHedger
from engine.cli.commands.expert_suggest import apply_universal_filters, calculate_winnings, resolve_scenario_config


def test_board_geometry_zero_and_one_indexed():
    """Verify BoardGeometry handles both 1-indexed and 0-indexed lotteries."""
    # Mega-Sena (1-60, 10 cols)
    geo_mega = BoardGeometry(max_n=60, cols=10, min_n=1)
    assert geo_mega.get_coords(1) == (1, 1)
    assert geo_mega.get_coords(60) == (6, 10)
    assert geo_mega.is_frame(1) is True
    assert geo_mega.is_frame(60) is True
    assert 2 in geo_mega.get_neighbors(1)
    assert 11 in geo_mega.get_neighbors(1)
    assert 12 in geo_mega.get_neighbors(1)

    # Lotomania (0-99, 10 cols)
    geo_mania = BoardGeometry(max_n=99, cols=10, min_n=0)
    assert geo_mania.get_coords(0) == (1, 1)
    assert geo_mania.get_coords(99) == (10, 10)
    assert geo_mania.is_frame(0) is True
    assert geo_mania.is_frame(99) is True
    assert 0 in geo_mania.get_neighbors(1)
    assert 10 in geo_mania.get_neighbors(0)
    assert 11 in geo_mania.get_neighbors(0)


def test_frame_center_logic_compatibility():
    """Verify get_frame_center_logic respects min_n and cols."""
    # Lotofácil: 25 numbers, 5 cols
    res_lf = get_frame_center_logic([1, 7, 13, 19, 25], cols=5, max_n=25, min_n=1)
    # 13 is row 3 col 3 (center)
    assert 13 in res_lf["center"]
    assert 1 in res_lf["frame"]
    assert 25 in res_lf["frame"]

    # Lotomania: 0-99
    res_mania = get_frame_center_logic([0, 55, 99], cols=10, max_n=99, min_n=0)
    assert 0 in res_mania["frame"]
    assert 99 in res_mania["frame"]
    assert 55 in res_mania["center"]


def test_hedging_monte_carlo_global_game():
    """Verify HedgingEngine works with any custom DrawRules without IndexError."""
    custom_rules = DrawRules(
        name="Custom Global Lotto",
        pick_count=7,
        number_range=(1, 49),
        ticket_price=2.5,
        currency="EUR",
        prize_tiers=[4, 5, 6, 7],
    )
    engine = CombinatorialHedger(custom_rules)
    portfolio = {
        "jackpot_tickets": [[1, 2, 3, 4, 5, 6, 7]],
        "hedge_tickets": [[10, 11, 12, 13, 14, 15, 16]],
    }
    metrics = engine.simulate_portfolio_payouts(portfolio, trials=200)
    assert metrics is not None
    assert metrics.total_budget == 5.0
    assert metrics.jackpot_tickets_count == 1
    assert metrics.hedge_tickets_count == 1


def test_universal_filters_cross_game():
    """Verify apply_universal_filters scales across sparse, dense, and US lotteries."""
    # Sparse game (Mega-Sena, 3 odds, 1 prime, sum=181)
    assert apply_universal_filters([10, 15, 23, 34, 42, 57], "br/mega-sena") is True
    # Extreme unbalanced all-odd ticket
    assert apply_universal_filters([1, 3, 5, 7, 9, 11], "br/mega-sena") is False

    # High-density (Lotofácil 15 numbers)
    lf_ticket = list(range(1, 16))
    # Sum = 120 (too low for Lotofácil which expects 175-225)
    assert apply_universal_filters(lf_ticket, "br/lotofacil") is False
    # Balanced Lotofácil ticket (sum = 195)
    lf_balanced = [1, 2, 4, 6, 7, 9, 11, 13, 15, 17, 18, 20, 22, 24, 25]
    assert apply_universal_filters(lf_balanced, "br/lotofacil") is True

    # Global lottery (Powerball 5 numbers)
    pb_ticket = [5, 18, 33, 47, 62]
    assert apply_universal_filters(pb_ticket, "us/powerball") is True


def test_scenario_resolution_global_lottery():
    """Verify scenario resolver formats currency and picks correctly for international games."""
    # US Powerball
    picks, count, cost, desc = resolve_scenario_config("us/powerball", budget=20.0)
    assert picks == 5
    assert count == 10
    assert cost == 20.0
    assert "USD" in desc

    # Brazilian Lotofácil
    picks_lf, count_lf, cost_lf, desc_lf = resolve_scenario_config("br/lotofacil", budget=50.0)
    assert picks_lf == 15
    assert "BRL" in desc_lf


def test_dodecahedron_zero_indexed_and_large_pool():
    """Verify dodecahedron neighbor calculation handles 0-indexed lotteries and pools > 60."""
    from engine.modules.geometry import get_dodecahedron_neighbors

    # Ball 0 in 0-99 pool (Lotomania)
    n0_neighbors = get_dodecahedron_neighbors(0, max_n=99, min_n=0)
    assert len(n0_neighbors) > 0
    assert all(0 <= nb <= 99 for nb in n0_neighbors)

    # Ball 50 in 0-99 pool
    n50_neighbors = get_dodecahedron_neighbors(50, max_n=99, min_n=0)
    assert len(n50_neighbors) > 0
    assert all(0 <= nb <= 99 for nb in n50_neighbors)


def test_multipool_bonus_ball_generation():
    """Verify strategy ticket generation populates valid secondary bonus pool balls."""
    import pandas as pd
    from engine.strategies.statistical.weighted import WeightedStrategy

    rules = DrawRules(
        name="Test MultiPool Lotto",
        pick_count=5,
        number_range=(1, 50),
        ticket_price=2.0,
        currency="USD",
        prize_tiers=[3, 4, 5],
        bonus_count=1,
        bonus_range=(1, 20),
    )

    import random
    rng = random.Random(42)
    rows = []
    for i in range(1, 36):
        main_nums = sorted(rng.sample(range(1, 51), 5))
        b_num = rng.randint(1, 20)
        rows.append({"draw": i, "numbers": main_nums, "bonus": [b_num]})
    df = pd.DataFrame(rows)

    strat = WeightedStrategy()
    result = strat.suggest(df, rules, count=3)

    assert len(result.tickets) == 3
    assert len(result.bonus_tickets) == 3
    for b_ticket in result.bonus_tickets:
        assert len(b_ticket) == 1
        assert 1 <= b_ticket[0] <= 20

