"""
Random Forest Strategy
=======================
Same feature set as the Logistic Regression strategy but uses a Random
Forest ensemble of decision trees instead.

Random Forest is more robust to non-linear feature interactions and doesn't
require feature scaling. It tends to be less overconfident than logistic
regression when classes are imbalanced (which they always are here —
most numbers don't appear in any given draw).

Hyperparameters
---------------
  n_estimators  Number of trees. Higher = more stable, slower to train.
  max_depth     Maximum tree depth. None = grow until leaves are pure.
  lookback      How many past draws to use as the training window.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.strategies.ml.logistic import _build_features, build_ml_dataset  # reuse feature builder

try:
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    _SKLEARN = True
except ImportError:
    _SKLEARN = False


@register
class RandomForestStrategy(BaseStrategy):
    name = "random_forest"
    description = "🌲 Random Forest classifier — non-linear per-number appearance probability"
    tier = "ml"

    requires_history = 100

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int | None = 8,
        lookback: int = 30,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth    = max_depth
        self.lookback     = lookback

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        if not _SKLEARN:
            raise ImportError("pip install 'lottery-engine[ml]'")

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
        
        params_str = f"{self.n_estimators}_{self.max_depth}_{self.lookback}"
        cache_key = f"{self.name}_{slug}_{len(df)}_{last_draw_hash}_{params_str}.joblib"
        cache_path = cache_dir / cache_key

        # Build vectorized dataset
        X, y, X_pred = build_ml_dataset(df, rules, self.lookback)

        if cache_path.exists():
            model = joblib.load(cache_path)
        else:
            model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            )
            model.fit(X, y)
            joblib.dump(model, cache_path)

        probs = model.predict_proba(X_pred)[:, 1]
        return {num: float(p) for num, p in zip(all_numbers, probs)}
