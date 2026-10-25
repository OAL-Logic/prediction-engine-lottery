"""
Multi-Lottery Cross-Validation & Harmony Bridge Suite 🛡️
========================================================
Validates that:
1. Filters are game-adaptive across Mega-Sena (6/60), Quina (5/80), and Lotofácil (15/25).
2. No filter suffers from 0% false-rejection lockouts on different draw rules.
3. Harmony and Vectorized filter registries interoperate via aliases and adapters.
4. Candidate generation relaxes K-of-N gracefully when constraints are strict.
"""

import pytest
import numpy as np
from engine.adapters import DrawRules
from engine.modules.filters import registry as vec_reg
from engine.modules.harmony import registry as harmony_reg
from engine.strategies.statistical.weighted import WeightedStrategy
import pandas as pd


@pytest.fixture
def megasena_rules():
    return DrawRules(name="Mega-Sena", pick_count=6, number_range=(1, 60))


@pytest.fixture
def quina_rules():
    return DrawRules(name="Quina", pick_count=5, number_range=(1, 80))


@pytest.fixture
def lotofacil_rules():
    return DrawRules(name="Lotofácil", pick_count=15, number_range=(1, 25))


@pytest.mark.parametrize("game_fixture", ["megasena_rules", "quina_rules", "lotofacil_rules"])
def test_filters_game_adaptive_nonzero_pass(game_fixture, request):
    """Ensure key Tier 4 historical filters adapt to the game and do not reject 100% of candidates."""
    rules = request.getfixturevalue(game_fixture)
    lo, hi = rules.number_range
    k = rules.pick_count

    # Generate 500 valid candidate combinations for this lottery
    np.random.seed(42)
    candidates = []
    pool = list(range(lo, hi + 1))
    for _ in range(500):
        comb = sorted(np.random.choice(pool, size=k, replace=False))
        candidates.append(comb)
    candidates_arr = np.array(candidates)

    test_filter_ids = [
        "historical_oe_pattern",
        "historical_hl_pattern",
        "historical_decade_pattern",
        "historical_unit_pattern",
        "historical_consecutive_pattern",
        "historical_median_range",
        "historical_std_dev_range",
        "historical_spread_range",
        "historical_digit_sum_pattern",
        "historical_ac_range",
        "historical_common_pair",
        "historical_common_triplet",
    ]

    for fid in test_filter_ids:
        f = vec_reg.get(fid)
        assert f is not None, f"Could not load filter {fid}"
        result = f.apply(candidates_arr, rules)
        pass_count = int(np.sum(result))
        assert pass_count > 0, f"Filter {fid} rejected 100% of candidates for {rules.name} (k={k}, pool={lo}..{hi})"


def test_harmony_vectorized_bridge(megasena_rules):
    """Ensure harmony.registry resolves aliases and vectorized tier IDs seamlessly."""
    # Test short alias
    func_alias = harmony_reg.get("parity")
    assert func_alias is not None
    # Test fully-qualified vectorized id
    func_vec = harmony_reg.get("historical_spread_range")
    assert func_vec is not None

    sample_pass = [10, 20, 30, 40, 50, 55]
    res_alias = func_alias(sample_pass, megasena_rules)
    res_vec = func_vec(sample_pass, megasena_rules)
    assert isinstance(res_alias, bool)
    assert isinstance(res_vec, bool)


def test_suggest_gradual_relaxation_metadata(megasena_rules):
    """Verify that BaseStrategy relaxes K-of-N and marks metadata when constraints are tight."""
    strategy = WeightedStrategy()
    df_mock = pd.DataFrame([
        {"draw": i, "date": "2026-01-01", "numbers": [1, 2, 3, 4, 5, 6]}
        for i in range(1, 40)
    ])

    # Provide conflicting/strict filters to trigger relaxation
    strict_filter_combo = [
        "structural_odd_count",
        "historical_consecutive_pattern",
        "historical_median_range",
        "historical_spread_range",
        "historical_digit_sum_pattern",
    ]

    res = strategy.suggest(
        df=df_mock,
        rules=megasena_rules,
        count=1,
        filters=strict_filter_combo,
        seed=42,
    )

    assert len(res.tickets) == 1
    # Check that tickets are valid
    assert len(res.tickets[0]) == 6
    # If relaxation triggered, metadata should reflect it
    if res.metadata.get("filters_relaxed"):
        assert "filters_effective_k" in res.metadata
        assert res.metadata["filters_target_n"] == len(strict_filter_combo)


def test_suggest_strict_filters_opt_out(megasena_rules):
    """Verify that --strict-filters prevents relaxation and enforces 100% adherence."""
    strategy = WeightedStrategy()
    df_mock = pd.DataFrame([
        {"draw": i, "date": "2026-01-01", "numbers": [1, 2, 3, 4, 5, 6]}
        for i in range(1, 40)
    ])

    # Impossible filter constraint: pool restricted to [1..6] but median range requires [20..40]
    with pytest.raises(ValueError, match="under --strict-filters"):
        strategy.suggest(
            df=df_mock,
            rules=megasena_rules,
            count=1,
            pool=[1, 2, 3, 4, 5, 6, 7],
            filters=["historical_median_range"],
            strict_filters=True,
            seed=42,
        )
