import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from engine.modules.regime import analyze_stability, RegimeResult

@pytest.fixture
def mock_rules():
    rules = MagicMock()
    rules.name = "Mega Sena"
    rules.number_range = (1, 60)
    return rules

@pytest.fixture
def mock_df():
    # Clear shift between windows
    data = []
    for i in range(100):
        # Window A (first 20) gets set 1
        # Window B (next 50) gets set 2
        if i < 20:
            nums = list(range(1, 7))
        else:
            nums = list(range(10, 16))
        data.append({"draw_id": i + 1, "numbers": nums})
    return pd.DataFrame(data)

def test_analyze_stability_metrics(mock_rules, mock_df):
    res = analyze_stability(mock_df, mock_rules, window_a=20, window_b=50)
    
    assert isinstance(res, RegimeResult)
    assert res.js_divergence > 0
    assert res.shannon_entropy > 0
    assert res.regime_verdict in ["STABLE", "DRIFTING", "DECOUPLED"]
    assert len(res.js_trend) > 0
