"""
Unit & Regression Tests for Stefan Mandel Strategy 🧪💼
======================================================
"""

from __future__ import annotations

import pandas as pd
from engine.adapters import DrawRules
from engine.strategies.statistical.stefan_mandel import StefanMandelCombinatorialCondensationStrategy

def test_stefan_mandel_strategy():
    """Verify that Stefan Mandel strategy correctly calculates combinations and scores."""
    rules = DrawRules(
        name="Test Pick 5",
        number_range=(1, 10),
        pick_count=5,
        ticket_price=2.0,
        currency="USD",
        prize_tiers=[3, 4, 5],
        odds={5: 252},  # 10 choose 5 is the jackpot tier
    )
    
    # Empty history
    df = pd.DataFrame(columns=["draw_id", "draw_date", "numbers"])
    
    strat = StefanMandelCombinatorialCondensationStrategy()
    scores = strat.score(df, rules, jackpot=600.0)
    
    assert len(scores) == 10
    assert strat._meta["total_combinations"] == 252  # 10 choose 5
    assert strat._meta["combinatorial_cost"] == 504.0  # 252 * 2.0
    assert strat._meta["arbitrage_ratio"] == round(600.0 / 504.0, 3)
    assert strat._meta["arbitrage_verdict"] == "FEASIBLE (+EV)"
