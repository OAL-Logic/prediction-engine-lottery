"""
Prophet Feature Engineering 🧬
=============================
Ported from LottoProphet. Extracts sliding-window time-series features
for high-performance regressor ensembles (XGBoost, LightGBM, CatBoost).
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any

def get_rolling_features(df: pd.DataFrame, window_size: int = 10) -> pd.DataFrame:
    """
    Extracts rolling features for each draw based on the previous N draws.
    """
    # Sort by draw_id to ensure time-series integrity
    df = df.sort_values("draw_id").reset_index(drop=True)
    
    # Identify all possible numbers in the pool
    all_nums = sorted(list(set(n for sublist in df["numbers"] for n in sublist)))
    
    feature_list = []
    
    for i in range(window_size, len(df)):
        # Lookback window
        window = df.iloc[i-window_size : i]
        target_draw = df.iloc[i]
        
        features = {"draw_id": target_draw["draw_id"]}
        
        # 1. Individual Number Frequencies
        flat_window = [n for sublist in window["numbers"] for n in sublist]
        for n in all_nums:
            features[f"freq_{n}"] = flat_window.count(n) / window_size
            
        # 2. Rolling Gaps (Draws since last seen)
        for n in all_nums:
            last_seen = -1
            for j in range(i-1, -1, -1):
                if n in df.iloc[j]["numbers"]:
                    last_seen = df.iloc[j]["draw_id"]
                    break
            features[f"gap_{n}"] = (target_draw["draw_id"] - last_seen) if last_seen != -1 else 100
            
        # 3. Structural Stats of the window
        # Mean Sum, Mean Span, Mean Primes
        sums = [sum(nums) for nums in window["numbers"]]
        features["mean_sum"] = np.mean(sums)
        features["std_sum"] = np.std(sums)
        
        spans = [max(nums) - min(nums) for nums in window["numbers"]]
        features["mean_span"] = np.mean(spans)
        
        feature_list.append(features)
        
    return pd.DataFrame(feature_list)

def prepare_regressor_data(df: pd.DataFrame, window_size: int = 10) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Prepares X (features) and y (targets) for training multi-regressor models.
    Target: One-hot encoded next draw numbers or multi-target regression.
    """
    feat_df = get_rolling_features(df, window_size)
    
    # Target: The actual numbers drawn in the 'next' period
    # We join back with original df to get the target labels
    merged = pd.merge(feat_df, df[["draw_id", "numbers"]], on="draw_id")
    
    all_nums = sorted(list(set(n for sublist in df["numbers"] for n in sublist)))
    
    # X: Everything except draw_id and numbers
    feature_cols = [col for col in feat_df.columns if col not in ["draw_id", "numbers"]]
    X = merged[feature_cols].values
    
    # y: Multi-label binary vector (size of pool)
    y = np.zeros((len(merged), len(all_nums)))
    for idx, row in merged.iterrows():
        for n in row["numbers"]:
            y[idx, all_nums.index(n)] = 1
            
    return X, y, feature_cols
