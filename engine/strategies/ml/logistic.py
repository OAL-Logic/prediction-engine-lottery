"""
Logistic Regression Strategy
==============================
Trains a binary classifier for each lottery number:
  label  = 1 if the number appeared in draw t+1, else 0
  features per (number, draw t) pair:

    freq_last_10     appearance rate in last 10 draws
    freq_last_30     appearance rate in last 30 draws
    freq_all         appearance rate across all draws
    draws_since      draws elapsed since last appearance (normalised)
    day_of_week      0–6 (normalised)
    draw_parity      draw number even/odd (0 or 1)
    position_mean    average sorted-position slot for this number (0–1)
    co_score         mean lift with the numbers most common in recent draws

We train a single shared model using all (number, draw) rows so the model
learns general patterns, then predict for each number for the next draw.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    import joblib
    _SKLEARN = True
except ImportError:
    _SKLEARN = False


@register
class LogisticStrategy(BaseStrategy):
    name = "logistic"
    description = "📊 Logistic Regression classifier — per-number appearance probability"
    tier = "ml"

    requires_history = 100

    def __init__(self, lookback: int = 30, C: float = 1.0) -> None:
        self.lookback = lookback
        self.C = C

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        if not _SKLEARN:
            raise ImportError("pip install 'lottery-engine[ml]'")

        df = df.sort_values("draw_id").reset_index(drop=True)
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        pick = rules.pick_count
        pool_size = hi - lo + 1
        n_draws = len(df)

        # 1. Build Draw Matrix (D x N)
        # matrix[d, n] = 1 if number n appeared in draw d
        matrix = np.zeros((n_draws, hi + 1), dtype=float)
        for i, row in enumerate(df["numbers"]):
            matrix[i, row] = 1.0

        import hashlib
        from pathlib import Path
        
        slug = rules.name.replace(" ", "_").lower()
        last_draw_str = str(df.iloc[-1]["numbers"])
        last_draw_hash = hashlib.md5(last_draw_str.encode()).hexdigest()
        
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        params_str = f"{self.C}_{self.lookback}"
        cache_key = f"{self.name}_{slug}_{len(df)}_{last_draw_hash}_{params_str}.joblib"
        cache_path = cache_dir / cache_key

        # 2. Vectorized Feature Preparation (Always needed for prediction)
        # Number-independent features (Day of week, Draw parity)
        if "date" in df.columns:
            dows = df["date"].dt.dayofweek.values / 6.0
        else:
            dows = np.zeros(n_draws)
        parities = np.arange(n_draws) % 2

        # Slot matrix for position features
        # slot_matrix[d, n] = normalized slot (0-1) if n in draw d
        slot_matrix = np.full((n_draws, hi + 1), 0.5)
        for i, row in enumerate(df["numbers"]):
            sorted_nums = sorted(row)
            for slot, num in enumerate(sorted_nums):
                slot_matrix[i, num] = slot / max(pick - 1, 1)

        n_norm = (all_numbers - lo) / max(pool_size - 1, 1)
        n_odd  = (all_numbers % 2 != 0).astype(float)

        if cache_path.exists():
            scaler, model = joblib.load(cache_path)
        else:
            # 2. Training Loop
            # We want to train on draws [lookback .. n-2] to predict [lookback+1 .. n-1]
            t_range = np.arange(self.lookback, n_draws - 1)
            X_list, y_list = [], []

            # Iterate over timesteps (this is the only loop, but it's now just T iterations)
            # Each iteration builds features for ALL N numbers at once
            for t in t_range:
                # Labels for draw t+1
                y_t = matrix[t + 1, all_numbers]
                
                # Features for all numbers at draw t
                # (A) Frequencies
                f_all = matrix[:t+1, all_numbers].mean(axis=0)
                f_w   = matrix[t-self.lookback+1:t+1, all_numbers].mean(axis=0)
                f_10  = matrix[max(0, t-9):t+1, all_numbers].mean(axis=0)
                
                # (B) Recency (Gap)
                # Find last index ≤ t for each number
                # We can use the pre-calculated matrix
                sub_matrix = matrix[:t+1, all_numbers]
                last_idx = np.array([np.where(sub_matrix[:, i] == 1)[0][-1] if np.any(sub_matrix[:, i] == 1) else -1 for i in range(pool_size)])
                draws_since = (t - last_idx) / max(t, 1)
                
                # (C) Position
                p_mean = slot_matrix[t-self.lookback+1:t+1, all_numbers].mean(axis=0)
                
                # (D) Contextual (Constant per timestep)
                dow = dows[t]
                par = parities[t]
                
                # (E) Number properties
                n_norm = (all_numbers - lo) / max(pool_size - 1, 1)
                n_odd  = (all_numbers % 2 != 0).astype(float)
                
                # Stack features for all N numbers
                # Each row is a number, columns are features
                feats = np.column_stack([
                    f_all, f_w, f_10, draws_since,
                    p_mean, n_norm, n_odd,
                    np.full(pool_size, dow), np.full(pool_size, par)
                ])
                
                X_list.append(feats)
                y_list.append(y_t)

            X = np.vstack(X_list)
            y = np.concatenate(y_list)

            scaler = StandardScaler()
            X_s = scaler.fit_transform(X)

            model = LogisticRegression(C=self.C, max_iter=500, class_weight="balanced")
            model.fit(X_s, y)
            joblib.dump((scaler, model), cache_path)

        # 3. Predict for draw N (using features at N-1)
        t_final = n_draws - 1
        f_all = matrix[:, all_numbers].mean(axis=0)
        f_w   = matrix[t_final-self.lookback+1:, all_numbers].mean(axis=0)
        f_10  = matrix[max(0, t_final-9):, all_numbers].mean(axis=0)
        
        sub_matrix = matrix[:, all_numbers]
        last_idx = np.array([np.where(sub_matrix[:, i] == 1)[0][-1] if np.any(sub_matrix[:, i] == 1) else -1 for i in range(pool_size)])
        draws_since = (t_final - last_idx) / max(t_final, 1)
        
        p_mean = slot_matrix[t_final-self.lookback+1:, all_numbers].mean(axis=0)
        
        X_pred = np.column_stack([
            f_all, f_w, f_10, draws_since,
            p_mean, n_norm, n_odd,
            np.full(pool_size, dows[t_final]), np.full(pool_size, parities[t_final])
        ])
        
        X_pred_s = scaler.transform(X_pred)
        probs = model.predict_proba(X_pred_s)[:, 1]

        return {int(num): float(p) for num, p in zip(all_numbers, probs)}


def _build_features(
    num: int,
    t: int,
    window: pd.DataFrame,
    df: pd.DataFrame,
    rules: DrawRules,
) -> list[float]:
    lo, hi   = rules.number_range
    pick     = rules.pick_count
    pool     = hi - lo + 1
    n_window = len(window)

    appearances = [1 if num in row["numbers"] else 0 for _, row in window.iterrows()]

    freq_all    = sum(1 if num in row["numbers"] else 0 for _, row in df.iloc[:t + 1].iterrows()) / (t + 1)
    freq_w      = sum(appearances) / n_window if n_window else 0.0
    freq_10     = sum(appearances[-10:]) / min(10, n_window) if n_window else 0.0

    # Draws since last appearance
    last_idx = next((t - i for i in range(t + 1) if num in df.iloc[t - i]["numbers"]), None)
    draws_since = (t - last_idx) / max(t, 1) if last_idx is not None else 1.0

    # Draw metadata
    day_of_week   = df.iloc[t]["date"].dayofweek / 6.0 if hasattr(df.iloc[t]["date"], "dayofweek") else 0.5
    draw_parity   = (t % 2)

    # Position tendency
    slots = []
    for _, row in window.iterrows():
        if num in row["numbers"]:
            slot = sorted(row["numbers"]).index(num) / max(pick - 1, 1)
            slots.append(slot)
    position_mean = float(np.mean(slots)) if slots else 0.5

    # Number features
    num_norm      = (num - lo) / max(pool - 1, 1)
    num_odd       = float(num % 2 != 0)

    return [
        freq_all, freq_w, freq_10, draws_since,
        day_of_week, draw_parity, position_mean,
        num_norm, num_odd,
    ]


def build_ml_dataset(
    df: pd.DataFrame,
    rules: DrawRules,
    lookback: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Builds the full training features X, labels y, and prediction features X_pred
    for ML strategies in a highly vectorized, extremely fast manner.
    """
    df = df.sort_values("draw_id").reset_index(drop=True)
    lo, hi = rules.number_range
    all_numbers = np.arange(lo, hi + 1)
    pick = rules.pick_count
    pool_size = hi - lo + 1
    n_draws = len(df)

    # 1. Build Draw Matrix (D x N)
    matrix = np.zeros((n_draws, hi + 1), dtype=float)
    for i, row in enumerate(df["numbers"]):
        matrix[i, row] = 1.0

    # 2. Precompute context features
    if "date" in df.columns:
        dows = df["date"].dt.dayofweek.values / 6.0
    else:
        dows = np.zeros(n_draws) + 0.5
    parities = (np.arange(n_draws) % 2).astype(float)

    # Slot matrix for position features
    slot_matrix = np.full((n_draws, hi + 1), 0.5)
    for i, row in enumerate(df["numbers"]):
        sorted_nums = sorted(row)
        for slot, num in enumerate(sorted_nums):
            slot_matrix[i, num] = slot / max(pick - 1, 1)

    n_norm = (all_numbers - lo) / max(pool_size - 1, 1)
    n_odd  = (all_numbers % 2 != 0).astype(float)

    X_list = []
    y_list = []

    t_range = np.arange(lookback, n_draws - 1)
    for t in t_range:
        # Labels for draw t+1
        y_t = matrix[t + 1, all_numbers]
        
        # Features for all numbers at draw t
        f_all = matrix[:t+1, all_numbers].mean(axis=0)
        f_w   = matrix[max(0, t - lookback + 1):t+1, all_numbers].mean(axis=0)
        f_10  = matrix[max(0, t - 9):t+1, all_numbers].mean(axis=0)
        
        # Recency (Gap)
        sub_matrix = matrix[:t+1, all_numbers]
        last_idx = np.array([
            np.where(sub_matrix[:, i] == 1)[0][-1] if np.any(sub_matrix[:, i] == 1) else -1
            for i in range(pool_size)
        ])
        draws_since = (t - last_idx) / max(t, 1)
        
        # Position mean for appearances in window
        apps_win = matrix[max(0, t - lookback + 1):t+1, all_numbers]
        slot_win = slot_matrix[max(0, t - lookback + 1):t+1, all_numbers]
        p_mean = np.zeros(pool_size)
        for i in range(pool_size):
            mask = apps_win[:, i] == 1.0
            p_mean[i] = slot_win[mask, i].mean() if np.any(mask) else 0.5

        dow = dows[t]
        par = parities[t]

        # Stack features in the exact order returned by _build_features
        feats = np.column_stack([
            f_all,
            f_w,
            f_10,
            draws_since,
            np.full(pool_size, dow),
            np.full(pool_size, par),
            p_mean,
            n_norm,
            n_odd
        ])
        X_list.append(feats)
        y_list.append(y_t)

    X = np.vstack(X_list) if X_list else np.empty((0, 9), dtype=np.float32)
    y = np.concatenate(y_list) if y_list else np.empty((0,), dtype=np.int32)

    # Prediction features at the final draw (t_final = n_draws - 1)
    t_final = n_draws - 1
    f_all = matrix[:, all_numbers].mean(axis=0)
    f_w   = matrix[max(0, t_final - lookback + 1):, all_numbers].mean(axis=0)
    f_10  = matrix[max(0, t_final - 9):, all_numbers].mean(axis=0)

    sub_matrix = matrix[:, all_numbers]
    last_idx = np.array([
        np.where(sub_matrix[:, i] == 1)[0][-1] if np.any(sub_matrix[:, i] == 1) else -1
        for i in range(pool_size)
    ])
    draws_since = (t_final - last_idx) / max(t_final, 1)

    apps_win = matrix[max(0, t_final - lookback + 1):, all_numbers]
    slot_win = slot_matrix[max(0, t_final - lookback + 1):, all_numbers]
    p_mean = np.zeros(pool_size)
    for i in range(pool_size):
        mask = apps_win[:, i] == 1.0
        p_mean[i] = slot_win[mask, i].mean() if np.any(mask) else 0.5

    dow = dows[t_final]
    par = parities[t_final]

    X_pred = np.column_stack([
        f_all,
        f_w,
        f_10,
        draws_since,
        np.full(pool_size, dow),
        np.full(pool_size, par),
        p_mean,
        n_norm,
        n_odd
    ])

    return X.astype(np.float32), y.astype(np.int32), X_pred.astype(np.float32)
