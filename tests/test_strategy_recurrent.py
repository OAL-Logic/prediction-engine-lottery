import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from engine.strategies.deep.lstm_gru import LSTMStrategy, GRUStrategy

@pytest.fixture
def mock_rules():
    rules = MagicMock()
    rules.name = "Mega Sena"
    rules.number_range = (1, 60)
    rules.pick_count = 6
    return rules

@pytest.fixture
def mock_df():
    data = []
    for i in range(210):
        data.append({
            "draw_id": i + 1,
            "date": pd.Timestamp(2026, 1, 1) + pd.Timedelta(days=i),
            "numbers": list(range(1, 7))
        })
    return pd.DataFrame(data)

def test_lstm_strategy_scoring(mock_rules, mock_df):
    strat = LSTMStrategy(epochs=1)
    scores = strat.score(mock_df, mock_rules)
    assert isinstance(scores, dict)
    assert len(scores) == 60
    assert all(0 <= s <= 1 for s in scores.values())

def test_gru_strategy_scoring(mock_rules, mock_df):
    strat = GRUStrategy(epochs=1)
    scores = strat.score(mock_df, mock_rules)
    assert isinstance(scores, dict)
    assert len(scores) == 60
    assert all(0 <= s <= 1 for s in scores.values())

def test_recurrent_lazy_torch():
    import sys
    import importlib
    
    # If torch is already in sys.modules, we can't easily test "not in"
    # but we can check if importing our module triggers it if we unload both.
    if "torch" in sys.modules:
        pytest.skip("Torch already in sys.modules - run this test in isolation for full verification")
    
    if "engine.strategies.deep.lstm_gru" in sys.modules:
        del sys.modules["engine.strategies.deep.lstm_gru"]
    
    # Importing the module shouldn't import torch
    importlib.import_module("engine.strategies.deep.lstm_gru")
    assert "torch" not in sys.modules
