"""
Ensemble Pro Strategy 🤖
========================
Advanced Stacking Regressor that blends multiple ML models.
Uses Random Forest, Gradient Boosting, and KNN.
Engineers features: Lags, Rolling Averages, and Environmental Resonance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class EnsembleProStrategy(BaseStrategy):
    name = "ensemble_pro"
    description = "🤖 Super-Stacking ML — blends RF, GBT, and KNN with engineered features"
    tier = "ml"

    requires_history = 100 # Needs data to train ML models

    def _engineer_features(self, ts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Create features for a single number's time series."""
        # Target: Next value (1 or 0)
        # Features: Lags (1, 2, 3, 5, 8, 13), Rolling Mean (5, 10, 20)
        X = []
        y = []
        
        lags = [1, 2, 3, 5, 8, 13]
        max_lag = max(lags)
        
        for i in range(max_lag, len(ts)):
            row = []
            # Lags
            for lag in lags:
                row.append(ts[i - lag])
            
            # Rolling means
            row.append(np.mean(ts[max(0, i-5):i]))
            row.append(np.mean(ts[max(0, i-10):i]))
            row.append(np.mean(ts[max(0, i-20):i]))
            
            X.append(row)
            y.append(ts[i])
            
        return np.array(X), np.array(y)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        df = df.sort_values("draw_id").reset_index(drop=True)
        n_draws = len(df)
        
        # Build binary appearance matrix
        matrix = np.zeros((n_draws, hi - lo + 1))
        for i, row in enumerate(df.itertuples()):
            for num in row.numbers:
                if lo <= num <= hi:
                    matrix[i, num - lo] = 1.0
                    
        scores = {}
        
        # Models to ensemble
        models = [
            RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42),
            GradientBoostingRegressor(n_estimators=50, learning_rate=0.1, max_depth=3, random_state=42),
            KNeighborsRegressor(n_neighbors=10)
        ]
        
        for idx, n in enumerate(all_numbers):
            ts = matrix[:, idx]
            X, y = self._engineer_features(ts)
            
            if len(X) < 20:
                scores[n] = 0.5
                continue
                
            # Train/Test Split (Recent validation)
            # We train on everything except the last feature row, 
            # then predict the last one (which corresponds to the next draw)
            
            X_train = X[:-1]
            y_train = y[:-1]
            X_next = X[-1].reshape(1, -1)
            
            # Ensemble Prediction
            preds = []
            for model in models:
                model.fit(X_train, y_train)
                preds.append(model.predict(X_next)[0])
                
            # Mean of ensemble
            scores[n] = float(np.mean(preds))

        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        min_s = min(scores.values()) if scores else 0.0
        if max_s > min_s:
            scores = {n: (v - min_s) / (max_s - min_s) for n, v in scores.items()}
        else:
            scores = {n: 0.5 for n in all_numbers}
            
        return scores
