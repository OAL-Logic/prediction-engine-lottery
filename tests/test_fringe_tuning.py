"""
Tests for Fringe Strategy Hyperparameter Tuning (Track E).
"""

import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.cli.commands.tune import PARAM_GRIDS
from engine.strategies import get_strategy


@pytest.fixture
def sample_history():
    rules = DrawRules("Mega-Sena", 6, (1, 60))
    rows = []
    for i in range(1, 40):
        # Deterministic synthetic draw
        nums = sorted([(i * 7 + j * 5) % 60 + 1 for j in range(6)])
        if len(set(nums)) < 6:
            nums = sorted(list(range(1, 7)))
        rows.append({"draw_id": i, "date": "2026-01-01", "numbers": nums})
    return pd.DataFrame(rows), rules


def test_param_grids_contains_fringe_strategies():
    fringe_keys = [
        "ising_model",
        "lorentz",
        "zeno_quantum",
        "quantum_multiverse",
        "tda_topology",
        "sacred_grid",
        "retrocausality",
    ]
    for key in fringe_keys:
        assert key in PARAM_GRIDS
        assert isinstance(PARAM_GRIDS[key], dict)
        assert len(PARAM_GRIDS[key]) > 0


def test_ising_model_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_default = get_strategy("ising_model")
    assert strat_default.coupling_j == 1.0

    strat_custom = get_strategy("ising_model", temperature=3.5, coupling_j=2.0, steps=1000)
    assert strat_custom.sim_temp == 3.5
    assert strat_custom.coupling_j == 2.0
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60
    assert all(0.0 <= v <= 1.0 for v in scores.values())


def test_lorentz_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_custom = get_strategy("lorentz", sigma=14.0, rho=35.0, dt=0.02)
    assert strat_custom.sigma == 14.0
    assert strat_custom.rho == 35.0
    assert strat_custom.dt == 0.02
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60


def test_zeno_quantum_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_custom = get_strategy("zeno_quantum", observation_window=25, zeno_threshold=0.90)
    assert strat_custom.observation_window == 25
    assert strat_custom.zeno_threshold == 0.90
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60


def test_quantum_multiverse_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_custom = get_strategy("quantum_multiverse", coherence_decay=0.95, branches=500, seed=42)
    assert strat_custom.coherence_decay == 0.95
    assert strat_custom.branches == 500
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60


def test_tda_topology_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_custom = get_strategy("tda_topology", core_percentile=70.0)
    assert strat_custom.core_percentile == 70.0
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60


def test_retrocausality_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_custom = get_strategy("retrocausality", extrapolation_window=8, echo_boost=0.35)
    assert strat_custom.extrapolation_window == 8
    assert strat_custom.echo_boost == 0.35
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60


def test_sacred_grid_hyperparameter_tuning(sample_history):
    df, rules = sample_history
    strat_custom = get_strategy("sacred_grid", scale_a=0.8, turns=5.0)
    assert strat_custom.scale_a == 0.8
    assert strat_custom.turns == 5.0
    scores = strat_custom.score(df, rules)
    assert len(scores) == 60
