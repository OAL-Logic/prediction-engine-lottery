"""
Tests for the Combinatorial Hedging & Portfolio Balance module and CLI command.
"""

import pytest
import pandas as pd

from engine.adapters import DrawRules
from engine.modules.hedging import CombinatorialHedger


@pytest.fixture
def mega_rules() -> DrawRules:
    return DrawRules(
        name="mega-sena",
        pick_count=6,
        number_range=(1, 60),
        prize_tiers=[4, 5, 6],
        ticket_price=5.0,
        currency="BRL"
    )


@pytest.fixture
def synthetic_history() -> pd.DataFrame:
    return pd.DataFrame({
        "draw_id": list(range(1, 51)),
        "date":    pd.date_range("2024-01-01", periods=50, freq="3D", tz="UTC"),
        "numbers": [
            sorted([((i * 7 + j) % 60) + 1 for j in range(6)])
            for i in range(50)
        ],
        "bonus":   [[]] * 50,
    })


def test_hedger_allocation(mega_rules):
    hedger = CombinatorialHedger(mega_rules)
    
    # Conservative: 30% Jackpot / 70% Hedge
    # For 10 tickets (50 BRL budget), should be roughly 3 Jackpot and 7 Hedge
    j_alloc, h_alloc, j_count, h_count = hedger.calculate_allocation(50.0, "conservative")
    assert j_count == 3
    assert h_count == 7
    assert j_alloc == 15.0
    assert h_alloc == 35.0

    # Balanced: 50% Jackpot / 50% Hedge
    # For 10 tickets, should be 5 and 5
    j_alloc, h_alloc, j_count, h_count = hedger.calculate_allocation(50.0, "balanced")
    assert j_count == 5
    assert h_count == 5
    assert j_alloc == 25.0
    assert h_alloc == 25.0


def test_hedger_portfolio_generation(mega_rules):
    hedger = CombinatorialHedger(mega_rules)
    
    # Mock strategy scores
    scores = {i: float(i) / 60.0 for i in range(1, 61)}
    
    portfolio = hedger.generate_balanced_portfolio(scores, scores, budget=50.0, risk_profile="balanced")
    
    assert portfolio["jackpot_count"] == 5
    assert portfolio["hedge_count"] == 5
    assert len(portfolio["jackpot_tickets"]) == 5
    assert len(portfolio["hedge_tickets"]) == 5
    
    # Check ticket pick count
    for t in portfolio["jackpot_tickets"] + portfolio["hedge_tickets"]:
        assert len(t) == mega_rules.pick_count
        assert len(set(t)) == mega_rules.pick_count  # unique numbers


def test_hedger_simulation(mega_rules):
    hedger = CombinatorialHedger(mega_rules)
    scores = {i: float(i) / 60.0 for i in range(1, 61)}
    portfolio = hedger.generate_balanced_portfolio(scores, scores, budget=50.0, risk_profile="balanced")
    
    # Run a short simulation of 200 trials to verify it returns non-negative metrics
    metrics = hedger.simulate_portfolio_payouts(portfolio, trials=200)
    
    assert metrics.total_budget == 50.0
    assert metrics.expected_payout >= 0.0
    assert metrics.hedge_coverage_ratio >= 0.0
    assert metrics.self_sustainability_score >= 0.0
    assert metrics.max_drawdown <= 50.0


def test_hedge_cli_import():
    """Verify that the CLI command can be imported cleanly."""
    from engine.cli.commands.hedge import hedge as hedge_cmd
    assert callable(hedge_cmd)
