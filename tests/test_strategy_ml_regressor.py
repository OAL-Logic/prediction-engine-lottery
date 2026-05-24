import pytest
import pandas as pd
import numpy as np
import os
from engine.adapters.br.lotofacil import LotofacilAdapter
from engine.strategies.ml.regressor_hub import RegressorHubStrategy
from engine.modules.feature_engineering import get_rolling_features, prepare_regressor_data

def test_feature_engineering_rolling_features():
    df = pd.DataFrame({
        "draw_id": list(range(1, 21)),
        "numbers": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]] * 20
    })
    
    feat_df = get_rolling_features(df, window_size=5)
    assert len(feat_df) == 15 # 20 - 5
    assert "freq_1" in feat_df.columns
    assert "gap_1" in feat_df.columns
    assert "mean_sum" in feat_df.columns

def test_prepare_regressor_data():
    df = pd.DataFrame({
        "draw_id": list(range(1, 21)),
        "numbers": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]] * 20
    })
    
    X, y, cols = prepare_regressor_data(df, window_size=5)
    assert X.shape[0] == 15
    assert y.shape[1] == 15 # Unique numbers in pool
    assert len(cols) > 0

def test_ml_regressor_hub_save_load():
    # Need enough data for regressor fit
    df = pd.DataFrame({
        "draw_id": list(range(1, 121)),
        "numbers": [sorted(np.random.choice(range(1, 26), 15, replace=False).tolist()) for _ in range(120)]
    })
    adapter = LotofacilAdapter()
    strategy = RegressorHubStrategy(window_size=10)
    
    # Train
    strategy.train(df, adapter.rules)
    
    game_slug = adapter.rules.name.lower().replace(" ", "_")
    assert os.path.exists(f"data/model_cache/xgboost_{game_slug}.pkl")
    
    # Load
    strategy2 = RegressorHubStrategy()
    loaded = strategy2.load(adapter.rules)
    assert loaded is True
    assert "xgboost" in strategy2.models
    assert len(strategy2.feature_cols) > 0

def test_ml_regressor_hub_scoring():
    df = pd.DataFrame({
        "draw_id": list(range(1, 121)),
        "numbers": [sorted(np.random.choice(range(1, 26), 15, replace=False).tolist()) for _ in range(120)]
    })
    adapter = LotofacilAdapter()
    strategy = RegressorHubStrategy(window_size=10)
    
    scores = strategy.score(df, adapter.rules)
    assert len(scores) == 25
    assert all(0.0 <= s <= 1.0 for s in scores.values())
