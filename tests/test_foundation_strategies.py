"""
Foundation-tier strategy tests 🔭📊
Covers engine/strategies/foundation/timesfm_forecast.py and
engine/strategies/foundation/tabfm_forecast.py — see those modules'
docstrings and TODO.md's "Integration Plan for Google Research Foundation
Models" for context.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.strategies import STRATEGY_REGISTRY, get_strategy

try:
    import timesfm  # noqa: F401
    _TIMESFM_AVAILABLE = True
except ImportError:
    _TIMESFM_AVAILABLE = False

try:
    import tabpfn  # noqa: F401
    _TABPFN_AVAILABLE = True
except ImportError:
    _TABPFN_AVAILABLE = False


def _synthetic_df(n_draws: int = 80, pick: int = 6, lo: int = 1, hi: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    for i in range(n_draws):
        nums = sorted(rng.choice(np.arange(lo, hi + 1), size=pick, replace=False).tolist())
        rows.append({"draw_id": i, "numbers": nums})
    return pd.DataFrame(rows)


def _rules() -> DrawRules:
    return DrawRules(name="Test Game", pick_count=6, number_range=(1, 60))


# ── Registry wiring (always runs, no optional dependency needed) ────────────

def test_timesfm_registered_in_strategy_registry():
    assert "timesfm" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["timesfm"]["tier"] == "foundation"
    assert STRATEGY_REGISTRY["timesfm"]["module"] == "engine.strategies.foundation.timesfm_forecast"


def test_timesfm_instantiates_without_the_optional_dependency():
    # get_strategy() only loads the module and instantiates the class; the
    # lazy-import contract (same as every ml/deep strategy) means this must
    # succeed even when `timesfm` itself isn't installed.
    strat = get_strategy("timesfm")
    assert strat.tier == "foundation"
    assert strat.name == "timesfm"


# ── Missing-dependency path (this is the path that actually runs in CI/dev,
#    since `timesfm` is an opt-in extra) ─────────────────────────────────────

@pytest.mark.skipif(_TIMESFM_AVAILABLE, reason="only meaningful when timesfm is NOT installed")
def test_timesfm_score_raises_friendly_error_without_dependency():
    strat = get_strategy("timesfm")
    with pytest.raises(ImportError, match=r"pip install 'lottery-engine\[foundation\]'"):
        strat.score(_synthetic_df(), _rules())


# ── Real forward pass (only when the optional dependency is installed) ──────

@pytest.mark.skipif(not _TIMESFM_AVAILABLE, reason="timesfm is required for this test")
def test_timesfm_score_returns_valid_distribution():
    strat = get_strategy("timesfm")
    scores = strat.score(_synthetic_df(), _rules())
    assert set(scores.keys()) == set(range(1, 61))
    assert all(0.0 <= v <= 1.0 for v in scores.values())
    assert abs(sum(scores.values()) - 1.0) < 1e-6


# ── TabFM: registry wiring (always runs, no optional dependency needed) ─────

def test_tabfm_registered_in_strategy_registry():
    assert "tabfm" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["tabfm"]["tier"] == "foundation"
    assert STRATEGY_REGISTRY["tabfm"]["module"] == "engine.strategies.foundation.tabfm_forecast"


def test_tabfm_instantiates_without_the_optional_dependency():
    strat = get_strategy("tabfm")
    assert strat.tier == "foundation"
    assert strat.name == "tabfm"


@pytest.mark.skipif(_TABPFN_AVAILABLE, reason="only meaningful when tabpfn is NOT installed")
def test_tabfm_score_raises_friendly_error_without_dependency():
    strat = get_strategy("tabfm")
    with pytest.raises(ImportError, match=r"pip install 'lottery-engine\[foundation\]'"):
        strat.score(_synthetic_df(), _rules())


@pytest.mark.skipif(not _TABPFN_AVAILABLE, reason="tabpfn is required for this test")
def test_tabfm_score_returns_valid_distribution():
    strat = get_strategy("tabfm")
    scores = strat.score(_synthetic_df(), _rules())
    assert set(scores.keys()) == set(range(1, 61))
    assert all(0.0 <= v <= 1.0 for v in scores.values())
    assert abs(sum(scores.values()) - 1.0) < 1e-6


# ── TabFM: pure feature-table builder (no optional dependency needed) ───────

def test_tabfm_build_table_shapes_and_no_leakage():
    from engine.strategies.foundation.tabfm_forecast import _build_table

    df = _synthetic_df(n_draws=50, pick=6, lo=1, hi=60)
    pool = list(range(1, 61))
    X_context, y_context, X_query = _build_table(df, pool, lo=1, hi=60, context_draws=15, rolling_window=10)

    assert X_context.shape == (15 * len(pool), 5)
    assert y_context.shape == (15 * len(pool),)
    assert set(np.unique(y_context).tolist()) <= {0, 1}
    assert X_query.shape == (len(pool), 5)
    # gap/rolling_freq/mean_gap columns must be non-negative
    assert np.all(X_context[:, 0] >= 0) and np.all(X_query[:, 0] >= 0)
    assert np.all(X_context[:, 1] >= 0) and np.all(X_query[:, 1] >= 0)
