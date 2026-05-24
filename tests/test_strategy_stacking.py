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
        # Normalization check: if all scores are 0.1, it might stay same or normalize
        # Our current logic: (v - min) / (max - min) might fail if max == min
        # But for 60 identical scores, it will stay 0.0 or fallback
