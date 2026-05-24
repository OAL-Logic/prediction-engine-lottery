"""
Gradient Boosting Strategy  🚀
================================
LightGBM classifier — the de-facto strongest algorithm for tabular data.

Uses the same feature set as Logistic / Random Forest so the strategies
are directly comparable, but gradient-boosted trees learn non-linear
feature interactions far more efficiently than Random Forest.

Why LightGBM over XGBoost?
---------------------------
  • Leaf-wise growth (vs XGBoost's level-wise) → faster, lower memory
  • Native handling of class imbalance via scale_pos_weight or is_unbalance
  • Arrow/pandas support out of the box
  • Single dependency: pip install lightgbm

Architecture
------------
  Features      : same 9 features as logistic / random_forest (reused from
                  engine.strategies.ml.logistic._build_features)
  Model         : LGBMClassifier with binary objective
  Class balance : is_unbalance=True — automatically adjusts for the fact
                  that ~95%+ of labels are 0 (number did not appear)
  Training      : rolling lookback window
  Inference     : predict_proba for each number on the next draw

Requires: pip install "lottery-engine[ml]"
          (lightgbm is included in the [ml] optional dep group)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.strategies.ml.logistic import _build_features, build_ml_dataset

try:
    from lightgbm import LGBMClassifier
    import joblib
    _LGB = True
except ImportError:
    _LGB = False


@register
class GradientBoostStrategy(BaseStrategy):
    name        = "gradient_boost"
    description = "🚀 LightGBM gradient boosting — strongest tabular ML classifier"
    tier        = "ml"
    requires_history = 80

    def __init__(
        self,
        n_estimators:  int   = 200,
        learning_rate: float = 0.05,
        max_depth:     int   = 6,
        num_leaves:    int   = 31,
        lookback:      int   = 30,
    ) -> None:
        self.n_estimators  = n_estimators
        self.learning_rate = learning_rate
        self.max_depth     = max_depth
        self.num_leaves    = num_leaves
        self.lookback      = lookback

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        if not _LGB:
            raise ImportError(
                "LightGBM not installed.\n"
                "Run: pip install lightgbm\n"
                "Or:  pip install 'lottery-engine[ml]'"
            )

        df = df.sort_values("draw_id").reset_index(drop=True)
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        n = len(df)

        import hashlib
        from pathlib import Path
        
        slug = rules.name.replace(" ", "_").lower()
        last_draw_str = str(df.iloc[-1]["numbers"])
        last_draw_hash = hashlib.md5(last_draw_str.encode()).hexdigest()
        
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        params_str = f"{self.n_estimators}_{self.learning_rate}_{self.max_depth}_{self.num_leaves}_{self.lookback}"
        cache_key = f"{self.name}_{slug}_{len(df)}_{last_draw_hash}_{params_str}.joblib"
        cache_path = cache_dir / cache_key

        # Build vectorized dataset
        X, y, X_pred = build_ml_dataset(df, rules, self.lookback)

        if cache_path.exists():
            model = joblib.load(cache_path)
        else:
            model = LGBMClassifier(
                n_estimators  = self.n_estimators,
                learning_rate = self.learning_rate,
                max_depth     = self.max_depth,
                num_leaves    = self.num_leaves,
                is_unbalance  = True,       # handle class imbalance natively
                verbosity     = -1,         # suppress training output
                random_state  = 42,
            )
            model.fit(X, y)
            joblib.dump(model, cache_path)

        probs = model.predict_proba(X_pred)[:, 1]

        return {num: float(p) for num, p in zip(all_numbers, probs)}
