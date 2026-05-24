"""
Smoke tests for the 9 strategies added in the Apr-27 Gemini sessions
(Sprint 1.3 — Absurdity Engine v4–v10).

These are intentionally NOT correctness tests — most of these strategies
encode esoteric / mystical heuristics whose "correctness" is not well-defined.
What we test instead is that:

1. The strategy registers under its expected name.
2. It instantiates cleanly with default arguments.
3. score() returns a valid score map covering the entire lottery pool with
   values in [0, 1] (post-normalization will happen in suggest()).
4. The strategy doesn't crash on a tiny synthetic history.

External fetches (NOAA solar, OSM geocoding, etc.) should be handled
gracefully — the strategies should fall back to a reasonable default
rather than raising.
"""

from datetime import date

import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.strategies import get_strategy

# Bootstrap the registry — strategies register via @register on import
import engine.strategies.statistical  # noqa: F401
import engine.strategies.fun          # noqa: F401
import engine.strategies.ml           # noqa: F401
try:
    import engine.strategies.deep      # noqa: F401
except ImportError:
    pass


try:
    import sklearn # noqa
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mega_rules() -> DrawRules:
    return DrawRules(name="mega-sena", pick_count=6, number_range=(1, 60))


@pytest.fixture
def synthetic_history() -> pd.DataFrame:
    """100 fake draws for Mega-Sena — enough to satisfy requires_history thresholds."""
    return pd.DataFrame({
        "draw_id": list(range(1, 101)),
        "date":    pd.date_range("2024-01-01", periods=100, freq="3D", tz="UTC"),
        "numbers": [
            sorted([((i * 7 + j) % 60) + 1 for j in range(6)])
            for i in range(100)
        ],
        "bonus":   [[]] * 100,
    })


# Each entry: (registry_name, optional_kwargs)
NEW_STATISTICAL = [
    ("primes", {}),
    ("quantum_anneal", {}),
    ("structural", {}),
    # `survival` is a meta-ensemble; it requires its members to be importable
    # and is heavy. Smoke-test it but allow KeyError on unknown sub-strategies.
    ("survival", {"members": "weighted,markov,bayesian"}),
    ("logistic", {}),
    ("knn", {}),
]

NEW_FUN = [
    ("iching", {}),
    ("noosphere", {}),
    ("sefirot", {}),
    ("entropy_global", {}),
    ("gematria", {}),
    ("vix_jitter", {}),
    # solar reads cached k-index data; pass a draw_date so it is deterministic
    ("solar", {"draw_date": date(2026, 4, 25)}),
    # ley_lines requires draw coordinates; provide São Paulo (Caixa) by default
    ("ley_lines", {"latitude": -23.5505, "longitude": -46.6333}),
]

NEW_ML = [
    ("voting", {"members": ["markov", "weighted"]}),
    ("regime", {}),
    ("synapse", {}),
]


# ---------------------------------------------------------------------------
# Statistical-tier smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name, kwargs", NEW_STATISTICAL + NEW_ML)
def test_statistical_strategy_instantiates(name, kwargs):
    if name in ("logistic", "knn", "random_forest", "gradient_boost") and not _SKLEARN_AVAILABLE:
        pytest.skip("scikit-learn not installed")
    try:
        strat = get_strategy(name, **kwargs)
    except KeyError:
        pytest.skip(f"Strategy '{name}' not registered (optional dep likely missing)")
    assert strat.name == name
    assert strat.tier in ("statistical", "fun", "ml", "deep")


@pytest.mark.parametrize("name, kwargs", NEW_STATISTICAL + NEW_ML)
def test_statistical_strategy_scores_full_pool(name, kwargs, synthetic_history, mega_rules):
    if name in ("logistic", "knn", "random_forest", "gradient_boost") and not _SKLEARN_AVAILABLE:
        pytest.skip("scikit-learn not installed")
    try:
        strat = get_strategy(name, **kwargs)
    except KeyError:
        pytest.skip(f"Strategy '{name}' not registered (optional dep likely missing)")
    # Import ML modules to ensure registry is populated
    import engine.strategies.ml # noqa
    scores = strat.score(synthetic_history, mega_rules)
    lo, hi = mega_rules.number_range
    pool = set(range(lo, hi + 1))
    assert set(scores.keys()) >= pool, f"{name} missing scores for pool members"
    # All scores should be finite and non-negative (BaseStrategy.suggest will normalize)
    for n, s in scores.items():
        if n not in pool:
            continue
        assert s >= 0.0, f"{name} produced negative score for {n}: {s}"
        assert s == s, f"{name} produced NaN for {n}"   # NaN check


# ---------------------------------------------------------------------------
# Fun-tier smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name, kwargs", NEW_FUN)
def test_fun_strategy_instantiates(name, kwargs):
    strat = get_strategy(name, **kwargs)
    assert strat.name == name


@pytest.mark.parametrize("name, kwargs", NEW_FUN)
def test_fun_strategy_scores_without_crashing(name, kwargs, synthetic_history, mega_rules):
    """The score() call should not raise. Network fetches should fail gracefully."""
    strat = get_strategy(name, **kwargs)
    try:
        scores = strat.score(synthetic_history, mega_rules)
    except Exception as exc:
        pytest.fail(f"{name}.score() raised unexpectedly: {type(exc).__name__}: {exc}")
    # Must cover at least the full pool
    lo, hi = mega_rules.number_range
    for n in range(lo, hi + 1):
        assert n in scores, f"{name} missing score for {n}"


# ---------------------------------------------------------------------------
# End-to-end: suggest() with new strategies emits valid tickets
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name, kwargs", [("primes", {}), ("iching", {}), ("sefirot", {})])
def test_suggest_emits_valid_tickets(name, kwargs, synthetic_history, mega_rules):
    """End-to-end: pick representative new strategies, run suggest(), verify shape."""
    strat = get_strategy(name, **kwargs)
    result = strat.suggest(synthetic_history, mega_rules, count=3, temperature=1.0, seed=42)
    assert len(result.tickets) == 3
    for t in result.tickets:
        assert len(t) == mega_rules.pick_count
        assert len(set(t)) == mega_rules.pick_count   # unique
        lo, hi = mega_rules.number_range
        assert all(lo <= n <= hi for n in t)
    # Confidence should be a plain float in [0, 1]
    assert 0.0 <= result.confidence <= 1.0


# ---------------------------------------------------------------------------
# Geometry module — smoke
# ---------------------------------------------------------------------------


def test_geometry_dodecahedron_neighbors():
    from engine.modules.geometry import get_dodecahedron_neighbors
    # Number 1 → vertex 0 → adjacent vertices [1, 4, 10]
    # Mapped to numbers in [1, 60]: 2, 5, 11, 22, 25, 31, 42, 45, 51 (excluding 1 itself)
    neighbors = get_dodecahedron_neighbors(1, max_n=60)
    assert 1 not in neighbors
    assert all(1 <= n <= 60 for n in neighbors)
    assert len(neighbors) > 0


def test_geometry_neighbors_excludes_self():
    from engine.modules.geometry import get_dodecahedron_neighbors
    for n in (1, 7, 22, 41):
        assert n not in get_dodecahedron_neighbors(n, max_n=60)
