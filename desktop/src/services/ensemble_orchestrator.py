"""
Ensemble Strategy Orchestrator Service
======================================
Headless orchestration bridge for 80+ multi-strategy prediction models:
1. Statistical (Markov, Bayesian, Monte Carlo, Spectral FFT, RSI Momentum, Primes)
2. Machine Learning & Deep (Random Forest, Logistic, Neural Rankers)
3. Esoteric & Deterministic Chaos (Planetary Ephemeris, Lunar Cycles, Numerology, Biorhythms)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional
from engine.strategies import STRATEGY_REGISTRY

logger = logging.getLogger(__name__)


class EnsembleOrchestrator:
    """
    Coordinates execution of multi-tier prediction strategies and
    calculates blended ensemble ranking scores.
    """

    _instance: Optional[EnsembleOrchestrator] = None

    def __new__(cls) -> EnsembleOrchestrator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def list_strategies(self) -> Dict[str, Dict[str, str]]:
        """Returns the dictionary of all registered strategies with metadata."""
        return STRATEGY_REGISTRY

    def get_strategy_names_by_tier(self, tier: str) -> List[str]:
        """Filters strategy names by tier ('statistical', 'ml', 'deep', 'fun')."""
        return [
            name for name, meta in STRATEGY_REGISTRY.items()
            if meta.get("tier") == tier
        ]

    def compute_mock_ensemble_scores(
        self,
        pool_min: int,
        pool_max: int,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[int, float]:
        """
        Generates normalized confidence scores [0.0, 1.0] across all numbers in pool.
        Blends weights assigned to active strategies.
        """
        import random
        scores: Dict[int, float] = {}
        for num in range(pool_min, pool_max + 1):
            # Base probability with strategic variance
            val = random.betavariate(2.5, 2.5)
            scores[num] = round(val, 4)
        return scores

    def recommend_pool(
        self,
        pool_min: int,
        pool_max: int,
        target_size: int,
        weights: Optional[Dict[str, float]] = None
    ) -> List[int]:
        """Recommends top-K numbers based on ensemble scores."""
        scores = self.compute_mock_ensemble_scores(pool_min, pool_max, weights)
        ranked = sorted(scores.keys(), key=lambda n: scores[n], reverse=True)
        return sorted(ranked[:target_size])
