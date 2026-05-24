import pytest
import pandas as pd
from unittest.mock import MagicMock
from engine.modules.decision_matrix import get_sentiment_label, get_full_strategy_matrix

def test_sentiment_labels():
    assert "Strong Buy" in get_sentiment_label(0.15, False)
    assert "Buy" in get_sentiment_label(0.05, False)
    assert "Neutral" in get_sentiment_label(0.0, False)
    assert "Sell" in get_sentiment_label(-0.05, False)
    assert "Strong Sell" in get_sentiment_label(-0.05, True)

def test_strategy_matrix_mock(monkeypatch):
    mock_metrics = [
        MagicMock(strategy_name="weighted", lift_over_random=0.12, avg_rank=2.5, is_hibernated=False),
        MagicMock(strategy_name="markov", lift_over_random=-0.05, avg_rank=8.2, is_hibernated=True)
    ]
    
    # Mock run_pruning_audit to return our controlled metrics
    def mock_audit(*args, **kwargs):
        return mock_metrics
    
    monkeypatch.setattr("engine.modules.decision_matrix.run_pruning_audit", mock_audit)
    
    adapter = MagicMock()
    matrix = get_full_strategy_matrix(adapter)
    
    assert "weighted" in matrix
    assert "markov" in matrix
    assert "Strong Buy" in matrix["weighted"].sentiment
    assert "Strong Sell" in matrix["markov"].sentiment
    assert matrix["weighted"].lift == 0.12
