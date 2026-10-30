"""
Dual-Core Statistical & Contextual Strategy (80/20 Blend) ⚖️🌌
=============================================================
Blends 80% Multi-Horizon Frequency/Delay/Quadrant Statistical Pipeline
with 20% Deterministic Astronomical & Temporal Context Layer (`engine.modules.dual_core`).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from engine.adapters import DrawRules
from engine.modules.dual_core import (
    DEFAULT_TARGET_ISO,
    ContextEngine,
    DualCoreScorer,
    StatisticalPipeline,
)
from engine.strategies import BaseStrategy, register


@register
class DualCoreStrategy(BaseStrategy):
    name = "dual_core"
    description = "⚖️🌌 Dual-Core 80% Statistical (H10/H50/All/Delay/Quadrant) + 20% Astronomical Context"
    tier = "statistical"
    requires_history = 5

    def __init__(self, target_date: Optional[str] = None, **kwargs: Any) -> None:
        self.target_date = target_date or DEFAULT_TARGET_ISO

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> Dict[int, float]:
        target_iso = kwargs.get("target_date") or self.target_date
        ctx_engine = ContextEngine(target_iso=target_iso)
        s_ctx = ctx_engine.generate_context_scores(rules)

        pipeline = StatisticalPipeline(history=df, rules=rules)
        s_stat = pipeline.compute_stat_scores()

        scorer = DualCoreScorer(stat_scores=s_stat, ctx_scores=s_ctx)
        return scorer.compute_composite_scores()
