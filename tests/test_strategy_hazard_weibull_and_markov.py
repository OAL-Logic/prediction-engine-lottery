import numpy as np
import pandas as pd
import pytest
from engine.adapters import DrawRules
from engine.strategies import get_strategy


@pytest.fixture
def sample_draw_data():
    rules = DrawRules(
        name="test_lotto",
        pick_count=5,
        number_range=(1, 20),
        bonus_count=0,
        bonus_range=None,
    )
    rng = np.random.default_rng(42)
    draws = []
    for _ in range(60):
        drawn = sorted(rng.choice(np.arange(1, 21), size=5, replace=False).tolist())
        draws.append(drawn)
    df = pd.DataFrame({"draw_id": np.arange(1, 61), "numbers": draws})
    return df, rules


def test_markov_dirichlet_smoothing(sample_draw_data):
    df, rules = sample_draw_data
    strategy = get_strategy("markov")
    scores = strategy.score(df, rules)

    assert len(scores) == 20
    assert all(0.0 <= v <= 1.0 for v in scores.values())
    assert max(scores.values()) == 1.0


def test_hazard_weibull_strategy(sample_draw_data):
    df, rules = sample_draw_data
    strategy = get_strategy("hazard_weibull")
    scores = strategy.score(df, rules)

    assert len(scores) == 20
    assert all(0.0 <= v <= 1.0 for v in scores.values())
    assert max(scores.values()) == 1.0
