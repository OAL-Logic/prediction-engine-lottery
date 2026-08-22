import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from engine.strategies.ml.stacking_ai import StackingAIStrategy

@pytest.fixture
def mock_adapter():
    adapter = MagicMock()
    adapter.rules.name = "Mega Sena"
    adapter.rules.number_range = (1, 60)
    adapter.rules.pick_count = 6
    
    # 10 draws for training
    data = []
    for i in range(10):
        data.append({"draw_id": i+1, "numbers": list(range(1, 7))})
    adapter.fetch.return_value = pd.DataFrame(data)
    return adapter

def test_stacking_ai_training(mock_adapter):
    # Use a small set of strategies to avoid excessive mocking
    strat = StackingAIStrategy(base_strategies=["weighted", "bayesian"])
    
    # We need to mock get_strategy to avoid actual heavy execution during test
    with pytest.MonkeyPatch().context() as mp:
        mock_strat_obj = MagicMock()
        mock_strat_obj.score.return_value = {n: 0.5 for n in range(1, 61)}
        mp.setattr("engine.strategies.ml.stacking_ai.get_strategy", lambda x: mock_strat_obj)
        
        weights = strat.train(mock_adapter, window=5)
        
        assert isinstance(weights, dict)
        assert "weighted" in weights
        assert "bayesian" in weights
        assert strat.weights is not None

def test_stacking_ai_scoring(mock_adapter):
    strat = StackingAIStrategy(base_strategies=["weighted"])
    strat.weights = {"weighted": 1.0}
    
    with pytest.MonkeyPatch().context() as mp:
        mock_strat_obj = MagicMock()
        mock_strat_obj.score.return_value = {n: 0.1 for n in range(1, 61)}
        mp.setattr("engine.strategies.ml.stacking_ai.get_strategy", lambda x: mock_strat_obj)
        
        scores = strat.score(mock_adapter.fetch(), mock_adapter.rules)
        assert isinstance(scores, dict)
        assert len(scores) == 60


def test_stacking_vs_weighted_benchmark(mock_adapter):
    # We want to benchmark Stacking AI against simple Weighted Average
    strat_stacking = StackingAIStrategy(base_strategies=["weighted", "bayesian"])
    
    with pytest.MonkeyPatch().context() as mp:
        # Mock sub-strategies to return specific scores
        weighted_mock = MagicMock()
        weighted_mock.requires_history = 0
        weighted_mock.score.return_value = {n: 0.9 if n % 2 == 0 else 0.1 for n in range(1, 61)}
        
        bayesian_mock = MagicMock()
        bayesian_mock.requires_history = 0
        bayesian_mock.score.return_value = {n: 0.1 if n % 2 == 0 else 0.9 for n in range(1, 61)}
        
        strats_map = {
            "weighted": weighted_mock,
            "bayesian": bayesian_mock
        }
        mp.setattr("engine.strategies.ml.stacking_ai.get_strategy", lambda x: strats_map[x])
        
        # Setup actual draws to have only even numbers
        data = []
        for i in range(20):
            data.append({"draw_id": i+1, "numbers": [2, 4, 6, 8, 10, 12]})
        mock_adapter.fetch.return_value = pd.DataFrame(data)
        
        # Train stacking strategy
        weights = strat_stacking.train(mock_adapter, window=10)
        
        # Stacking AI should assign a positive and higher weight to 'weighted' strategy
        assert weights["weighted"] > weights["bayesian"]
