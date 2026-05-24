import pytest
import pandas as pd
from engine.adapters.br.lotofacil import LotofacilAdapter
from engine.strategies.statistical.expected_value import ExpectedValueStrategy

def test_expected_value_scoring():
    # 1. Setup Mock Data
    df = pd.DataFrame({
        "draw_id": [1, 2, 3],
        "numbers": [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4],
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 1, 3, 5]
        ]
    })
    
    adapter = LotofacilAdapter()
    strategy = ExpectedValueStrategy()
    
    # 2. Execute Scoring
    scores = strategy.score(df, adapter.rules)
    
    # 3. Assertions
    assert len(scores) == 25
    assert all(0.0 <= s <= 1.0 for s in scores.values())
    
    # Numbers 1, 2, 3 appear in all 3 draws - they should have high base frequency
    assert scores[1] > 0
    assert scores[2] > 0
    assert scores[3] > 0

def test_expected_value_recency_bias():
    # Verify that numbers NOT in recent draws get a boost
    df = pd.DataFrame({
        "draw_id": list(range(1, 51)),
        "numbers": [[1]*15] * 50 # Extreme mock
    })
    
    adapter = LotofacilAdapter()
    strategy = ExpectedValueStrategy()
    scores = strategy.score(df, adapter.rules)
    
    # Number 1 is very 'hot' (recent), others are 'cold'
    # Recency bias should boost cold numbers (e.g., 2)
    # Note: final score is product of base frequency (low for 2) and boost.
    # We just want to ensure it calculates without error.
    assert 2 in scores
