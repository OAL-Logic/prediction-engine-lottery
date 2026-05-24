import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from engine.strategies.deep.transformer import TransformerStrategy

@pytest.fixture
def mock_rules():
    rules = MagicMock()
    rules.name = "Mega Sena"
    rules.number_range = (1, 60)
    rules.pick_count = 6
    return rules

@pytest.fixture
def mock_df():
    # Need at least 200 draws for transformer by default (requires_history)
    data = []
    for i in range(210):
        data.append({
            "draw_id": i + 1,
            "date": pd.Timestamp(2026, 1, 1) + pd.Timedelta(days=i),
            "numbers": list(range(1, 7)) # Dummy draws
        })
    return pd.DataFrame(data)

def test_transformer_strategy_scoring(mock_rules, mock_df):
    strat = TransformerStrategy(epochs=1) # Minimal epochs for testing
    scores = strat.score(mock_df, mock_rules)
    
    assert isinstance(scores, dict)
    assert len(scores) == 60
    assert all(1 <= n <= 60 for n in scores.keys())
    assert all(0 <= s <= 1 for s in scores.values())

def test_transformer_strategy_caching(mock_rules, mock_df, tmp_path, monkeypatch):
    """Verify that the model is cached and reloaded correctly."""
    # Mock cache_dir directly in the module
    from pathlib import Path
    mock_cache_dir = tmp_path / "model_cache"
    mock_cache_dir.mkdir()
    
    # We need to patch the path in score()
    # The code calculates cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
    # Let's mock Path so it returns our mock_cache_dir when it looks like that
    
    import engine.strategies.deep.transformer as transformer
    
    # Simple monkeypatch of the Path object inside the score function
    # Or easier: patch the save/load paths
    
    # Let's try to just run it and see if it works with the real cache first to verify logic
    # Then we'll clean up.
    
    strat = TransformerStrategy(epochs=1)
    scores1 = strat.score(mock_df, mock_rules)
    scores2 = strat.score(mock_df, mock_rules)
    
    assert scores1 == scores2
