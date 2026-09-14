"""
Tests for the Quina unfolded-bet pipeline (engine.quina_unfold) and the
financial/combinatorial baseline (engine.modules.quina_financial).

All tests run offline against the cached draw history (source="cache") —
no network calls.
"""

from __future__ import annotations

from math import comb

import pytest

from engine.modules import quina_financial as qf
from engine.quina_unfold import DrawRepository, FeatureExtractor, FilterPipeline, PoolOptimizer


# ---------------------------------------------------------------------------
# Financial baseline — pure combinatorics, no historical data needed
# ---------------------------------------------------------------------------


def test_base_bet_odds_match_published_figure():
    assert comb(80, 5) == 24_040_016


def test_ticket_cost_scales_by_combinations():
    from engine.adapters.br.quina import QuinaAdapter

    rules = QuinaAdapter().rules
    assert qf.ticket_cost(10, rules) == pytest.approx(252 * 2.5)
    assert qf.ticket_cost(15, rules) == pytest.approx(3003 * 2.5)


def test_lines_at_tier_is_exact_partition_of_all_combinations():
    # Every one of the N-choose-5 lines scores at exactly one tier (0..5 hits);
    # summing lines_at_tier over tier=0..5 must equal C(N,5) for any hit count.
    n, hits = 12, 4
    total = sum(qf.lines_at_tier(n, hits, t) for t in range(0, 6))
    assert total == comb(n, 5)


def test_odds_monotonically_improve_with_more_numbers():
    p10 = qf.prob_at_least_hits(10, min_hits=2)
    p15 = qf.prob_at_least_hits(15, min_hits=2)
    assert p15 > p10


# ---------------------------------------------------------------------------
# Pipeline — DrawRepository -> FeatureExtractor -> FilterPipeline -> PoolOptimizer
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def repo():
    r = DrawRepository()
    r.load_history(source="cache")
    return r


@pytest.fixture(scope="module")
def features(repo):
    df = repo.load_history(refresh=False)
    prior = repo.get_prior_draw()
    return FeatureExtractor(repo.rules).compute(df, prior_draw=prior.numbers)


def test_feature_table_covers_full_range(repo, features):
    lo, hi = repo.rules.number_range
    assert sorted(features["number"]) == list(range(lo, hi + 1))


def test_feature_table_decile_and_quadrant_are_within_bounds(features):
    assert features["decile"].between(1, 10).all()
    assert features["quadrant"].between(1, 4).all()


@pytest.mark.parametrize("pool_size", [6, 10, 12, 15])
def test_optimizer_produces_valid_pool_of_requested_size(repo, features, pool_size):
    pipeline = FilterPipeline.default_envelope()
    result = PoolOptimizer(repo.rules, features, pipeline, pool_size=pool_size).optimize()

    assert len(result.numbers) == pool_size
    assert len(set(result.numbers)) == pool_size
    lo, hi = repo.rules.number_range
    assert all(lo <= n <= hi for n in result.numbers)


def test_optimizer_pool_satisfies_default_envelope(repo, features):
    pipeline = FilterPipeline.default_envelope()
    result = PoolOptimizer(repo.rules, features, pipeline, pool_size=10).optimize()
    assert result.filter_report.passed, result.filter_report.failures


def test_optimizer_rejects_out_of_range_pool_size(repo, features):
    pipeline = FilterPipeline.default_envelope()
    with pytest.raises(ValueError):
        PoolOptimizer(repo.rules, features, pipeline, pool_size=3)
    with pytest.raises(ValueError):
        PoolOptimizer(repo.rules, features, pipeline, pool_size=20)


def test_omission_rationale_covers_every_excluded_number(repo, features):
    pipeline = FilterPipeline.default_envelope()
    result = PoolOptimizer(repo.rules, features, pipeline, pool_size=10).optimize()
    lo, hi = repo.rules.number_range
    excluded = set(range(lo, hi + 1)) - set(result.numbers)
    assert excluded == set(result.omission_rationale.keys())
    assert all(isinstance(v, str) and v for v in result.omission_rationale.values())
