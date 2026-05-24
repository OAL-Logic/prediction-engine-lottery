import pytest
from engine.modules.risk import calculate_kelly_bet, KellyResult

def test_calculate_kelly_bet_logic():
    # bankroll=1000, price=5, odds=1000000, confidence=0.5
    res = calculate_kelly_bet(1000.0, 5.0, 1000000.0, 0.5)
    
    assert isinstance(res, KellyResult)
    assert res.tickets >= 1
    assert res.bet_amount >= 5.0
    assert res.fraction > 0
    assert res.is_safe is True

def test_calculate_kelly_bet_low_confidence():
    # confidence=0.1 (below 0.2 threshold)
    res = calculate_kelly_bet(1000.0, 5.0, 1000000.0, 0.1, min_confidence=0.2)
    assert res.is_safe is False
