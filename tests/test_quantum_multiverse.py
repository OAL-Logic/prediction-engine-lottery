"""Unit tests for Quantum Multiverse & Immortality Strategy 🌌

Validates game-agnostic compatibility across 3 archetypes:
1. Mega-Sena (6/60)
2. Quina (5/80)
3. Lotofácil (15/25)
"""

from __future__ import annotations

import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.strategies import get_strategy
from engine.strategies.fun.quantum_multiverse import QuantumMultiverseStrategy


def _mock_draws(numbers_pool: list[int], pick_count: int, n_draws: int = 15) -> pd.DataFrame:
    records = []
    for i in range(n_draws):
        # Deterministic sample for testing
        sampled = numbers_pool[(i * pick_count) % len(numbers_pool) : ((i + 1) * pick_count) % len(numbers_pool)]
        if len(sampled) < pick_count:
            sampled = numbers_pool[:pick_count]
        records.append({"draw_number": i + 1, "numbers": sampled})
    return pd.DataFrame(records)


def test_quantum_multiverse_metadata() -> None:
    strat = get_strategy("quantum_multiverse")
    assert isinstance(strat, QuantumMultiverseStrategy)
    assert strat.name == "quantum_multiverse"
    assert strat.tier == "fun"
    assert strat.requires_history == 5


@pytest.mark.parametrize(
    "name,lo,hi,pick",
    [
        ("megasena", 1, 60, 6),
        ("quina", 1, 80, 5),
        ("lotofacil", 1, 25, 15),
    ],
)
def test_quantum_multiverse_archetypes(name: str, lo: int, hi: int, pick: int) -> None:
    rules = DrawRules(
        name=name,
        number_range=(lo, hi),
        pick_count=pick,
        bonus_count=0,
    )
    pool = list(range(lo, hi + 1))
    df = _mock_draws(pool, pick, n_draws=20)

    strat = QuantumMultiverseStrategy(branches=300, seed=42)
    scores = strat.score(df, rules)

    # Check pool coverage
    assert len(scores) == len(pool)
    for n in pool:
        assert n in scores
        assert scores[n] >= 0.0

    # Probabilities should sum to approximately 1.0
    total_prob = sum(scores.values())
    assert pytest.approx(total_prob, abs=1e-5) == 1.0


def test_quantum_multiverse_seed_determinism() -> None:
    rules = DrawRules(
        name="megasena",
        number_range=(1, 60),
        pick_count=6,
        bonus_count=0,
    )
    df = _mock_draws(list(range(1, 61)), 6, n_draws=10)

    strat1 = QuantumMultiverseStrategy(branches=500, seed=12345)
    strat2 = QuantumMultiverseStrategy(branches=500, seed=12345)

    scores1 = strat1.score(df, rules)
    scores2 = strat2.score(df, rules)

    for n in range(1, 61):
        assert pytest.approx(scores1[n], abs=1e-9) == scores2[n]


def test_quantum_multiverse_handles_empty_or_minimal_history() -> None:
    rules = DrawRules(
        name="megasena",
        number_range=(1, 60),
        pick_count=6,
        bonus_count=0,
    )
    df_empty = pd.DataFrame(columns=["draw_number", "numbers"])

    strat = QuantumMultiverseStrategy(branches=200, seed=777)
    scores = strat.score(df_empty, rules)

    assert len(scores) == 60
    assert pytest.approx(sum(scores.values()), abs=1e-5) == 1.0


def test_quantum_multiverse_handles_numpy_array_numbers() -> None:
    rules = DrawRules(
        name="megasena",
        number_range=(1, 60),
        pick_count=6,
        bonus_count=0,
    )
    import numpy as np
    # Simulate df where 'numbers' column contains np.ndarray instead of list
    records = [{"draw_number": i + 1, "numbers": np.array([1, 2, 3, 4, 5, 6])} for i in range(10)]
    df_numpy = pd.DataFrame(records)

    strat = QuantumMultiverseStrategy(branches=150, seed=101)
    scores = strat.score(df_numpy, rules)
    assert len(scores) == 60
    assert pytest.approx(sum(scores.values()), abs=1e-5) == 1.0


def test_fringe_preset_registration_and_expansion() -> None:
    from engine.strategies import STRATEGY_PRESETS, get_strategy
    from engine.services.backtest import _resolve_strategy_names

    assert "fringe" in STRATEGY_PRESETS
    fringe_strats = STRATEGY_PRESETS["fringe"]
    assert len(fringe_strats) == 9
    assert "quantum_multiverse" in fringe_strats
    assert "ising_model" in fringe_strats
    assert "zeno_quantum" in fringe_strats

    # Verify each strategy can be instantiated
    for s_name in fringe_strats:
        strat = get_strategy(s_name)
        assert strat.name == s_name

    # Verify backtest resolver expands "fringe"
    expanded = _resolve_strategy_names(["fringe"])
    assert expanded == fringe_strats

