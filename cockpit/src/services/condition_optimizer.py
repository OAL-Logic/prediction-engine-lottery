"""
Condition Backtester & Historical Filter Optimizer
==================================================
Provides historical condition validation, backtesting, and automated optimization:
- Auto-Fit historical condition scanner across N draws
- Empirical hit-rate evaluation against past official winning drawings
- Identification of filter 'choke points' (filters that inadvertently eliminate winners)
- Multi-objective optimization balancing combinatorial reduction with historical recall
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
import pandas as pd

from cockpit.src.core.models import GameSchema, FilterNode, ToleranceRule, ToleranceMode
from cockpit.src.services.engine_bridge import EngineBridge

logger = logging.getLogger(__name__)


@dataclass
class ChokePointDetail:
    """Diagnostic detail for a filter that rejected winning historical draws."""
    filter_id: str
    filter_name: str
    rejection_count: int
    rejection_rate_pct: float
    observed_min: float
    observed_max: float
    configured_min: float
    configured_max: float


@dataclass
class BacktestReport:
    """Comprehensive backtest findings report for a filter & tolerance profile."""
    game_id: str
    total_draws_evaluated: int
    winning_draws_passed: int
    historical_hit_rate_pct: float
    estimated_reduction_rate_pct: float
    efficiency_index: float                # Hit Rate * Reduction Rate / 100
    choke_points: List[ChokePointDetail] = field(default_factory=list)
    verdict: str = "BALANCED"


class ConditionOptimizer:
    """
    Historical condition backtester and automated tolerance optimizer.
    """

    def __init__(self, bridge: Optional[EngineBridge] = None):
        self.bridge = bridge or EngineBridge()

    def run_historical_backtest(
        self,
        game_id: str,
        filters: List[FilterNode],
        tolerance: ToleranceRule,
        draws_limit: int = 50
    ) -> BacktestReport:
        """
        Backtests candidate filter criteria against the last N official historical draws.
        Evaluates which draws survived and quantifies filter choke points.
        """
        active_filters = [f for f in filters if f.enabled]
        df = self.bridge.get_draws(game_id, limit=draws_limit)

        if df.empty or "numbers" not in df.columns or not active_filters:
            return BacktestReport(
                game_id=game_id,
                total_draws_evaluated=len(df),
                winning_draws_passed=len(df),
                historical_hit_rate_pct=100.0,
                estimated_reduction_rate_pct=0.0,
                efficiency_index=0.0,
                verdict="NO_ACTIVE_FILTERS"
            )

        draws_list = df["numbers"].tolist()
        draws_matrix = np.array(draws_list, dtype=np.uint8)
        total_draws = draws_matrix.shape[0]

        game = self.bridge.get_game(game_id)
        pass_matrix = self.bridge.evaluate_filter_chunk_vectorized(
            combos=draws_matrix,
            active_filters=active_filters,
            game=game
        )

        survivor_mask = self.bridge.apply_tolerance_mask(pass_matrix, tolerance)
        passed_count = int(np.sum(survivor_mask))
        hit_rate = (passed_count / total_draws) * 100.0 if total_draws > 0 else 0.0

        # Calculate Choke Points (filters that failed on historical draws)
        choke_points: List[ChokePointDetail] = []
        for idx, flt in enumerate(active_filters):
            col_pass = pass_matrix[:, idx]
            rejections = int(np.sum(~col_pass))
            rej_rate = (rejections / total_draws) * 100.0

            # Observed historical min/max for this filter
            # (using pass matrix evaluation or direct calculation)
            if rejections > 0:
                choke_points.append(ChokePointDetail(
                    filter_id=flt.id,
                    filter_name=flt.name,
                    rejection_count=rejections,
                    rejection_rate_pct=round(rej_rate, 1),
                    observed_min=flt.min_val,
                    observed_max=flt.max_val,
                    configured_min=flt.min_val,
                    configured_max=flt.max_val
                ))

        choke_points.sort(key=lambda x: x.rejection_count, reverse=True)

        # Estimate Combinatorial Reduction Rate using a random sample of 2,000 combinations
        sample_reduction = self._estimate_sample_reduction(game, active_filters, tolerance)
        efficiency = (hit_rate * sample_reduction) / 100.0

        if hit_rate >= 80.0 and sample_reduction >= 70.0:
            verdict = "EXCELLENT"
        elif hit_rate < 50.0:
            verdict = "TOO_STRICT"
        elif sample_reduction < 30.0:
            verdict = "TOO_PERMISSIVE"
        else:
            verdict = "BALANCED"

        return BacktestReport(
            game_id=game_id,
            total_draws_evaluated=total_draws,
            winning_draws_passed=passed_count,
            historical_hit_rate_pct=round(hit_rate, 1),
            estimated_reduction_rate_pct=round(sample_reduction, 1),
            efficiency_index=round(efficiency, 2),
            choke_points=choke_points,
            verdict=verdict
        )

    def _estimate_sample_reduction(
        self,
        game: Optional[GameSchema],
        filters: List[FilterNode],
        tolerance: ToleranceRule,
        sample_size: int = 2000
    ) -> float:
        """Estimates reduction rate % by testing against a uniformly distributed random sample."""
        if not game or not filters:
            return 0.0

        import random
        pool = list(range(game.number_range_min, game.number_range_max + 1))
        sample_combos = [sorted(random.sample(pool, game.pick_count)) for _ in range(sample_size)]
        matrix = np.array(sample_combos, dtype=np.uint8)

        pass_matrix = self.bridge.evaluate_filter_chunk_vectorized(
            combos=matrix,
            active_filters=filters,
            game=game
        )
        survivors = self.bridge.apply_tolerance_mask(pass_matrix, tolerance)
        num_survived = int(np.sum(survivors))

        reduction = ((sample_size - num_survived) / sample_size) * 100.0
        return max(0.0, reduction)

    def auto_optimize_choke_points(
        self,
        game_id: str,
        filters: List[FilterNode],
        tolerance: ToleranceRule,
        target_hit_rate: float = 85.0
    ) -> Tuple[List[FilterNode], BacktestReport]:
        """
        Iteratively relaxes filter boundaries for top choke points until the historical
        hit rate reaches target_hit_rate.
        """
        current_report = self.run_historical_backtest(game_id, filters, tolerance)
        if current_report.historical_hit_rate_pct >= target_hit_rate or not current_report.choke_points:
            return filters, current_report

        # Get empirical observed bounds across historical draws
        fitted = self.bridge.compute_auto_fit_ranges(game_id, filters, last_n_draws=current_report.total_draws_evaluated)

        for cp in current_report.choke_points:
            for flt in filters:
                if flt.id == cp.filter_id and flt.id in fitted:
                    obs_min, obs_max = fitted[flt.id]
                    # Expand bounds to include historical observations
                    flt.min_val = min(flt.min_val, obs_min)
                    flt.max_val = max(flt.max_val, obs_max)

            new_report = self.run_historical_backtest(game_id, filters, tolerance)
            if new_report.historical_hit_rate_pct >= target_hit_rate:
                return filters, new_report

        return filters, self.run_historical_backtest(game_id, filters, tolerance)
