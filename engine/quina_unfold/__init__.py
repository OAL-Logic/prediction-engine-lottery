"""
Quina Unfolded-Bet Optimization Pipeline 🎯
============================================
End-to-end architecture for building a high-count (6-15 number) unfolded
candidate pool against empirical macro-structural filters.

    DrawRepository   -> FeatureExtractor -> FilterPipeline -> PoolOptimizer

Every stage operates on the existing engine.adapters / engine.modules stack
(QuinaAdapter, storage, frequency, skips, sum_range) — nothing here re-fetches
or re-implements draw ingestion.

This pipeline filters against empirical *macro-structural* distributions
(parity, sum band, decile/quadrant spread, prior-draw telemetry, frequency
z-scores). It does not, and cannot, change the fact that every 5-number
combination from 1-80 has an identical 1-in-24,040,016 draw probability —
see engine.modules.quina_financial for the exact combinatorics.
"""

from __future__ import annotations

from engine.quina_unfold.repository import DrawRepository
from engine.quina_unfold.features import FeatureExtractor, NumberFeatures
from engine.quina_unfold.filters import FilterPipeline, FilterRule, FilterReport
from engine.quina_unfold.optimizer import PoolOptimizer, PoolResult

__all__ = [
    "DrawRepository",
    "FeatureExtractor",
    "NumberFeatures",
    "FilterPipeline",
    "FilterRule",
    "FilterReport",
    "PoolOptimizer",
    "PoolResult",
]
