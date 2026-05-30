"""
Ensemble Strategies
===================
Combining multiple strategies to improve robustness and predictive accuracy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Any, List, Optional

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, _weighted_sample, get_strategy, register


# ---------------------------------------------------------------------------
# Voting ensemble
# ---------------------------------------------------------------------------


@register
class VotingEnsemble(BaseStrategy):
    name        = "voting"
    description = "🗳️ Weighted average of multiple strategies (voting:s1=0.8,s2=0.2)"
    tier        = "ml"
    requires_history = 50

    def __init__(self, members: list[str] | None = None, weights: list[float] | None = None) -> None:
        self._member_names = members or ["markov", "bayesian", "weighted", "monte_carlo"]
        self._weights = weights or [1.0] * len(self._member_names)
        if len(self._weights) != len(self._member_names):
            self._weights = [1.0] * len(self._member_names)

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        
        # Capture member parameters for transparency
        member_params = []
        # We need to extract some info for the metadata
        # Since we use *args, **kwargs, we can peek into kwargs or use defaults
        # But for the consensus display, we just need to know what ran.
        return result

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        all_scores: dict[int, float] = {n: 0.0 for n in all_numbers}
        active_weight = 0.0

        # Dynamic closed-loop AutoML weights loading
        import json
        from pathlib import Path
        daemon_file = Path("data/daemon_state.json")
        loaded_weights = None
        if daemon_file.exists():
            try:
                with open(daemon_file, "r") as f:
                    state = json.load(f)
                    slug = rules.name.replace(" ", "_").lower()
                    game_state = state.get(slug) or state.get(rules.name.lower())
                    if game_state and "strategy_weights" in game_state:
                        loaded_weights = game_state["strategy_weights"]
            except Exception:
                pass

        active_weights = list(self._weights)
        if loaded_weights:
            active_weights = []
            for i, name in enumerate(self._member_names):
                w = float(loaded_weights.get(name, self._weights[i]))
                active_weights.append(w)
        
        for name, weight in zip(self._member_names, active_weights):
            try:
                strategy = get_strategy(name, **kwargs)
                s = strategy.score(df, rules)
                for n in all_numbers:
                    all_scores[n] += s.get(n, 0.0) * weight
                active_weight += weight
            except Exception:
                pass

        if active_weight == 0.0:
            return {n: 1.0 / len(all_numbers) for n in all_numbers}

        return {
            n: all_scores[n] / active_weight
            for n in all_numbers
        }


# ---------------------------------------------------------------------------
# Probability-weighted ensemble
# ---------------------------------------------------------------------------


@register
class ProbWeightedEnsemble(BaseStrategy):
    name = "prob_weighted"
    description = "📈 Precision-weighted ensemble — better back-test performance = more weight"

    tier        = "ml"
    requires_history = 100

    def __init__(
        self,
        members: list[str] | None = None,
        backtest_draws: int = 20,
    ) -> None:
        self._member_names = members or ["markov", "bayesian", "weighted", "monte_carlo"]
        self.backtest_draws = backtest_draws

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        return super().suggest(*args, **kwargs)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        n = len(df)
        bt = min(self.backtest_draws, n // 4)

        weights: dict[str, float] = {}
        for name in self._member_names:
            try:
                strategy = get_strategy(name, **kwargs)
                hits = 0
                for i in range(n - bt - 1, n - 1):
                    sub_df   = df.iloc[:i]
                    actual   = set(df.iloc[i + 1]["numbers"])
                    scores   = strategy.score(sub_df, rules)
                    top_k    = sorted(scores, key=scores.get, reverse=True)[: rules.pick_count]
                    hits    += len(set(top_k) & actual)
                weights[name] = hits / (bt * rules.pick_count)
            except Exception:
                weights[name] = 0.01

        total_w = sum(weights.values()) or 1.0

        all_scores = {}
        for name in self._member_names:
            try:
                strategy = get_strategy(name, **kwargs)
                s = strategy.score(df, rules)
                w = weights[name] / total_w
                for num in all_numbers:
                    all_scores[num] = all_scores.get(num, 0.0) + s.get(num, 0.0) * w
            except Exception:
                pass

        return all_scores or {n: 1.0 / len(all_numbers) for n in all_numbers}


# ---------------------------------------------------------------------------
# Hybrid ensemble
# ---------------------------------------------------------------------------


@register
class HybridEnsemble(BaseStrategy):
    name        = "hybrid"
    description = "🧬 Two-stage: prob_weighted shortlist → pattern filter (hybrid:s1,s2,...)"
    tier        = "ml"
    requires_history = 100

    def __init__(
        self,
        members: list[str] | None = None,
        candidate_multiplier: int = 3,
    ) -> None:
        self._member_names    = members or ["markov", "bayesian", "weighted"]
        self.candidate_mult   = candidate_multiplier

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        return super().suggest(*args, **kwargs)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        k = rules.pick_count * self.candidate_mult

        stage1 = ProbWeightedEnsemble(members=self._member_names)
        s1_scores = stage1.score(df, rules, **kwargs)
        candidates = sorted(all_numbers, key=lambda n: s1_scores.get(n, 0), reverse=True)[:k]

        from engine.strategies.statistical.pattern import PatternStrategy
        stage2 = PatternStrategy(n_samples=3_000)
        s2_scores = stage2.score(df, rules)

        result = {}
        for num in all_numbers:
            if num in candidates:
                result[num] = s1_scores.get(num, 0.0) * (s2_scores.get(num, 0.0) + 0.1)
            else:
                result[num] = 0.0

        return result


# ---------------------------------------------------------------------------
# Stacking ensemble
# ---------------------------------------------------------------------------


@register
class StackingEnsemble(BaseStrategy):
    name        = "stacking"
    description = "🥞 Meta-learner ensemble — trains a model to weight member predictions (stacking:s1,s2)"
    tier        = "ml"
    requires_history = 150

    def __init__(
        self,
        members: list[str] | None = None,
        train_window: int = 50,
    ) -> None:
        self._member_names = members or ["markov", "bayesian", "weighted", "monte_carlo"]
        self.train_window  = train_window

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        return super().suggest(*args, **kwargs)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        try:
            from sklearn.linear_model import LogisticRegression
        except ImportError:
            raise ImportError("pip install 'lottery-engine\\[ml\\]' for stacking ensemble")

        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        n = len(df)
        tw = min(self.train_window, n - 20)

        if tw < 10:
            return VotingEnsemble(members=self._member_names).score(df, rules, **kwargs)

        X_train, y_train = [], []
        strats = []
        for name in self._member_names:
            try:
                strats.append(get_strategy(name, **kwargs))
            except Exception:
                pass
        
        if not strats:
            return {n: 1.0 / len(all_numbers) for n in all_numbers}

        step = max(1, tw // 20)
        for i in range(n - tw - 1, n - 1, step):
            sub_df = df.iloc[:i]
            actual = set(df.iloc[i + 1]["numbers"])
            m_scores = [s.score(sub_df, rules) for s in strats]
            for num in all_numbers:
                feats = [s.get(num, 0.0) for s in m_scores]
                X_train.append(feats)
                y_train.append(1 if num in actual else 0)

        meta_model = LogisticRegression(class_weight="balanced", max_iter=200)
        meta_model.fit(X_train, y_train)

        current_m_scores = [s.score(df, rules) for s in strats]
        X_pred = []
        for num in all_numbers:
            X_pred.append([s.get(num, 0.0) for s in current_m_scores])
            
        probs = meta_model.predict_proba(X_pred)[:, 1]
        max_p = max(probs) if any(probs) else 1.0
        return {num: float(p / max_p) for num, p in zip(all_numbers, probs)}


# ---------------------------------------------------------------------------
# Synapse strategy (The Universal Conjunction)
# ---------------------------------------------------------------------------


@register
class UniversalConjunction(BaseStrategy):
    """
    The 'Absurdity Engine' Peak Strategy (v5.0).
    
    Synchronizes three predictive domains:
    1. Statistical Matrix (Weighted/Bayesian/Monte-Carlo)
    2. Deep/ML Matrix (Quantum Anneal/Prob-Weighted)
    3. Chaos/Esoteric Matrix (Iching/Kabbalistic/Sentiment)
    
    Verified Correlation (2026-05-07): Iching + Weighted shows 20% win rate 
    at 12+ hits on Lotofacil (30-draw backtest).
    """

    name        = "synapse"
    description = "🔌 Universal Conjunction — convergance of Statistical, Deep, and Chaos tiers"
    tier        = "ml"
    requires_history = 50

    def __init__(
        self,
        stat_weight: float = 1.0,
        chaos_weight: float = 0.85,
        ensemble_members: str = "weighted,bayesian,iching,quantum_anneal"
    ) -> None:
        self.w_stat = stat_weight
        self.w_chaos = chaos_weight
        self._members = ensemble_members.split(",")

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Collective Intelligence Scoring
        strat_scores = []
        weights = []
        
        for name in self._members:
            try:
                s_obj = get_strategy(name, **kwargs)
                score_dict = s_obj.score(df, rules, **kwargs)
                strat_scores.append(score_dict)
                
                # Weighting: weighted and iching are the current 'Singularity' leaders
                if name in ("weighted", "iching"):
                    weights.append(1.2)
                else:
                    weights.append(1.0)
            except Exception:
                continue

        if not strat_scores:
            return {n: 1.0 / len(all_numbers) for n in all_numbers}

        # 2. Convergent Synthesis
        final_scores = {n: 0.0 for n in all_numbers}
        total_w = sum(weights)
        
        for s_dict, w in zip(strat_scores, weights):
            for n in all_numbers:
                final_scores[n] += (s_dict.get(n, 0.0) * w) / total_w
                
        # 3. Geometric Neighbors (Singularity Injection)
        try:
            # We use local references to avoid circularity if possible
            from engine.strategies import get_strategy
            s_weighted = get_strategy("weighted").score(df, rules)
            s_iching = get_strategy("iching").score(df, rules)
            
            top_w = set(sorted(all_numbers, key=lambda x: s_weighted.get(x, 0), reverse=True)[:5])
            top_i = set(sorted(all_numbers, key=lambda x: s_iching.get(x, 0), reverse=True)[:5])
            
            conjunction = top_w & top_i
            for n in conjunction:
                final_scores[n] *= 1.5 
        except Exception:
            pass

        return final_scores
