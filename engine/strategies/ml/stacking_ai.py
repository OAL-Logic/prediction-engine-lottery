from __future__ import annotations

import pandas as pd
import numpy as np
import hashlib
import joblib
from pathlib import Path
from typing import List, Dict, Any, Optional

from engine.adapters import DrawRules, LotteryAdapter
from engine.strategies import BaseStrategy, register, get_strategy

def _get_ml_classes():
    """Deferred loading of sklearn-dependent logic."""
    from sklearn.linear_model import Ridge
    return Ridge

@register
class StackingAIStrategy(BaseStrategy):
    """
    Stacking AI Strategy 🧠 (Meta-Learner)
    ========================================
    Learns optimal voting weights for sub-models based on historical 
    performance (Lift over Random). 
    """
    name = "stacking_ai"
    description = "🧠 Stacking AI (Neural Meta-Learner for optimal strategy weights)"
    tier = "ml"
    requires_history = 100

    def __init__(self, base_strategies: Optional[List[str]] = None):
        self.base_strategies = base_strategies or ["weighted", "momentum", "bayesian", "markov", "kabbalistic"]
        self.weights: Optional[Dict[str, float]] = None

    def _get_cache_path(self, rules: DrawRules) -> Path:
        slug = rules.name.replace(" ", "_").lower()
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"stacking_weights_{slug}.joblib"

    def train(self, adapter: LotteryAdapter, window: int = 50):
        """
        Trains the meta-learner to find optimal weights.
        """
        Ridge = _get_ml_classes()
        df = adapter.fetch()
        rules = adapter.rules
        
        # 1. Generate Training Data
        # X: [Samples * Numbers, Strategies] - scores for each number
        # y: [Samples * Numbers] - 1 if number hit, 0 otherwise
        X, y = [], []
        
        # Limit window for speed
        df_target = df.iloc[:window]
        
        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        
        for i in range(len(df_target) - 1):
            past_df = df.iloc[i+1:]
            real_draw = set(df.iloc[i]['numbers'])
            
            # Get scores from all sub-models for this past draw
            row_scores = []
            for name in self.base_strategies:
                try:
                    strat = get_strategy(name)
                    scores = strat.score(past_df, rules)
                    # Convert dict to sorted array for consistent matrix alignment
                    row_scores.append([scores.get(n, 0.0) for n in range(lo, hi + 1)])
                except:
                    row_scores.append([0.0] * pool_size)
            
            # Stack strategies as columns
            X_draw = np.column_stack(row_scores) # [Numbers, Strategies]
            X.append(X_draw)
            
            # Create labels for each number
            y_draw = [1.0 if n in real_draw else 0.0 for n in range(lo, hi + 1)]
            y.extend(y_draw)

        X_final = np.vstack(X)
        y_final = np.array(y)

        # 2. Fit Ridge Regression (Linear Stacking)
        model = Ridge(alpha=1.0, fit_intercept=False)
        model.fit(X_final, y_final)
        
        # 3. Save Weights
        self.weights = dict(zip(self.base_strategies, model.coef_))
        joblib.dump(self.weights, self._get_cache_path(rules))
        return self.weights

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        cache_path = self._get_cache_path(rules)
        
        # Load weights if not in memory
        if self.weights is None:
            if cache_path.exists():
                self.weights = joblib.load(cache_path)
            else:
                # Fallback: Uniform weights
                self.weights = {name: 1.0/len(self.base_strategies) for name in self.base_strategies}

        # Combine scores
        lo, hi = rules.number_range
        final_scores = {n: 0.0 for n in range(lo, hi + 1)}
        
        for name, weight in self.weights.items():
            try:
                strat = get_strategy(name)
                scores = strat.score(df, rules)
                for num, score in scores.items():
                    final_scores[num] += score * weight
            except:
                continue

        # Normalize 0-1
        vals = list(final_scores.values())
        min_v, max_v = min(vals), max(vals)
        if max_v > min_v:
            final_scores = {k: (v - min_v) / (max_v - min_v) for k, v in final_scores.items()}
            
        return final_scores
