"""
Multi-Regressor ML Hub 🤖
=========================
Ported from LottoProphet. Integrates XGBoost, LightGBM, and CatBoost
into a unified regressor ensemble for maximum predictive lift.
"""

from __future__ import annotations

import logging
import os
import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional

from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules.feature_engineering import prepare_regressor_data, get_rolling_features

logger = logging.getLogger(__name__)

@register
class RegressorHubStrategy(BaseStrategy):
    name = "ml_regressor"
    description = "🤖 Multi-Regressor ML Hub (XGB/LGBM/CAT Ensemble)"
    tier = "ml"
    requires_history = 100

    def __init__(self, model_type: str = "ensemble", window_size: int = 10):
        self.model_type = model_type
        self.window_size = window_size
        self.models = {}
        self.feature_cols = []

    def _get_base_model(self, m_type: str):
        if m_type == "xgboost":
            return XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=6, verbosity=0)
        if m_type == "lightgbm":
            return LGBMRegressor(n_estimators=100, learning_rate=0.05, num_leaves=31, verbose=-1)
        if m_type == "catboost":
            return CatBoostRegressor(iterations=100, learning_rate=0.05, depth=6, verbose=0)
        return None

    def train(self, df: pd.DataFrame, rules: DrawRules):
        """Fits the selected regressors and serializes them."""
        X, y, self.feature_cols = prepare_regressor_data(df, self.window_size)
        
        types = ["xgboost", "lightgbm", "catboost"] if self.model_type == "ensemble" else [self.model_type]
        
        os.makedirs("data/model_cache", exist_ok=True)
        game_slug = rules.name.lower().replace(" ", "_")
        
        from engine.modules.telemetry import pulse
        for t in types:
            pulse(f"Training {t} regressor for {rules.name}...", "INFO")
            logger.info(f"Training {t} regressor for {rules.name}...")
            base = self._get_base_model(t)
            # Use MultiOutputRegressor to handle multiple numbers in a single ticket
            model = MultiOutputRegressor(base)
            model.fit(X, y)
            
            self.models[t] = model
            pulse(f"{t} regressor training COMPLETE.", "SUCCESS")
            
            # Serialize (Story 5.3.5)
            cache_path = f"data/model_cache/{t}_{game_slug}.pkl"
            joblib.dump({
                "model": model,
                "feature_cols": self.feature_cols,
                "window_size": self.window_size
            }, cache_path)
            logger.info(f"Model saved to {cache_path}")

    def load(self, rules: DrawRules) -> bool:
        """Loads cached models if they exist."""
        game_slug = rules.name.lower().replace(" ", "_")
        types = ["xgboost", "lightgbm", "catboost"] if self.model_type == "ensemble" else [self.model_type]
        
        loaded_count = 0
        for t in types:
            cache_path = f"data/model_cache/{t}_{game_slug}.pkl"
            if os.path.exists(cache_path):
                checkpoint = joblib.load(cache_path)
                self.models[t] = checkpoint["model"]
                self.feature_cols = checkpoint["feature_cols"]
                self.window_size = checkpoint["window_size"]
                loaded_count += 1
                
        return loaded_count > 0

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        """Generates consensus scores using the regressor ensemble."""
        if not self.models:
            if not self.load(rules):
                self.train(df, rules)
                
        # Prepare latest features
        feat_df = get_rolling_features(df, self.window_size).tail(1)
        if feat_df.empty:
            return {n: 1.0 for n in range(rules.number_range[0], rules.number_range[1] + 1)}
            
        X = feat_df[self.feature_cols].values
        
        consensus_preds = []
        for t, model in self.models.items():
            preds = model.predict(X) # (1, pool_size)
            consensus_preds.append(preds[0])
            
        # Average predictions
        avg_preds = np.mean(consensus_preds, axis=0)
        
        lo, hi = rules.number_range
        scores = {}
        all_nums = list(range(lo, hi + 1))
        
        for i, n in enumerate(all_nums):
            # Regressor outputs might be slightly outside [0, 1] due to fit
            scores[n] = float(np.clip(avg_preds[i], 0.0, 1.0))
            
        return scores
