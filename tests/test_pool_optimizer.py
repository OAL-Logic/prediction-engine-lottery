"""Tests for engine.modules.pool_optimizer — structural-envelope pool engine."""

from __future__ import annotations

import pandas as pd
import pytest

from engine.adapters.br.lotofacil import LotofacilAdapter
from engine.modules.pool_optimizer import (
    DrawRepository,
    FeatureExtractor,
    FilterPipeline,
    PoolOptimizer,
)

RULES = LotofacilAdapter.rules

# Real, historically-grounded fixtures (draw 3779 and a compliant 15-number
# core derived from it — see the draw-3780 pool report for provenance).
DRAW_3779 = [3, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 23, 24, 25]
CORE_COMBO = (1, 2, 5, 7, 8, 10, 12, 13, 14, 15, 19, 20, 22, 23, 24)
POOL_18 = (1, 2, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24)
POOL_19 = (1, 2, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24)


@pytest.fixture(scope="module")
def extractor() -> FeatureExtractor:
    return FeatureExtractor(RULES)


@pytest.fixture(scope="module")
def pipeline() -> FilterPipeline:
    return FilterPipeline.default_for(RULES)


def _synthetic_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"draw_id": 1, "date": pd.NaT, "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "bonus": []},
            {"draw_id": 2, "date": pd.NaT, "numbers": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 1, 3, 5], "bonus": []},
            {"draw_id": 3, "date": pd.NaT, "numbers": DRAW_3779, "bonus": []},
        ]
    )


# ---------------------------------------------------------------------------
# DrawRepository
# ---------------------------------------------------------------------------


def test_draw_repository_from_frame_roundtrip():
    repo = DrawRepository.from_frame(_synthetic_frame(), RULES)
    assert repo.rules is RULES
    assert repo.draw(3) == sorted(DRAW_3779)
    draw_id, numbers = repo.latest()
    assert draw_id == 3
    assert numbers == sorted(DRAW_3779)


def test_draw_repository_unknown_draw_raises():
    repo = DrawRepository.from_frame(_synthetic_frame(), RULES)
    with pytest.raises(KeyError):
        repo.draw(999)


@pytest.mark.usefixtures("mock_fetch_cooldown")
def test_draw_repository_against_real_adapter_no_network():
    """Cooldown files (written by the session-scoped autouse fixture) force
    the adapter to read from local storage instead of the network."""
    repo = DrawRepository(adapter=LotofacilAdapter())
    df = repo.history()
    assert not df.empty
    assert repo.draw(3779) == sorted(DRAW_3779)


# ---------------------------------------------------------------------------
# FeatureExtractor
# ---------------------------------------------------------------------------


def test_row_col_mapping_matches_5x5_board(extractor: FeatureExtractor):
    assert (extractor.row_of(1), extractor.col_of(1)) == (0, 0)
    assert (extractor.row_of(25), extractor.col_of(25)) == (4, 4)
    assert (extractor.row_of(13), extractor.col_of(13)) == (2, 2)
    assert extractor.n_rows == 5


def test_combo_features_known_core_combo(extractor: FeatureExtractor):
    feats = extractor.combo_features(CORE_COMBO, DRAW_3779)
    assert feats["sum"] == 195
    assert feats["odd"] == 7
    assert feats["even"] == 8
    assert feats["primes"] == 6
    assert feats["repeats_vs_reference"] == 9
    assert feats["row_spread"] == 2
    assert feats["col_spread"] == 3
    assert feats["empty_row"] is False
    assert feats["empty_col"] is False


def test_number_profiles_cover_full_universe(extractor: FeatureExtractor):
    profiles = extractor.number_profiles(_synthetic_frame(), window=2)
    assert set(profiles) == set(range(1, 26))
    # Number 1 appears in 2 of the 3 synthetic draws (all but DRAW_3779).
    assert profiles[1].freq_all == 2


# ---------------------------------------------------------------------------
# FilterPipeline
# ---------------------------------------------------------------------------


def test_default_pipeline_accepts_core_combo(extractor: FeatureExtractor, pipeline: FilterPipeline):
    feats = extractor.combo_features(CORE_COMBO, DRAW_3779)
    report = pipeline.evaluate(feats)
    assert report.compliant
    assert report.score == len(pipeline.rules) == 5


def test_default_pipeline_rejects_extreme_combo(extractor: FeatureExtractor, pipeline: FilterPipeline):
    # 1-15: minimum possible sum, all in the top-left of the board -> fails
    # sum, spatial, and (likely) repeats simultaneously.
    feats = extractor.combo_features(list(range(1, 16)), DRAW_3779)
    report = pipeline.evaluate(feats)
    assert not report.compliant
    assert report.passed["spatial"] is False


# ---------------------------------------------------------------------------
# PoolOptimizer
# ---------------------------------------------------------------------------


def test_core_by_rejection_sampling_finds_compliant_combo(extractor: FeatureExtractor, pipeline: FilterPipeline):
    optimizer = PoolOptimizer(extractor, pipeline)
    combo = optimizer.core_by_rejection_sampling(DRAW_3779, n_samples=20_000, seed=3780)
    feats = extractor.combo_features(combo, DRAW_3779)
    assert pipeline.evaluate(feats).compliant


def test_evaluate_pool_matches_known_compliance(extractor: FeatureExtractor, pipeline: FilterPipeline):
    optimizer = PoolOptimizer(extractor, pipeline)
    report_18 = optimizer.evaluate_pool(POOL_18, DRAW_3779)
    report_19 = optimizer.evaluate_pool(POOL_19, DRAW_3779)

    assert report_18.n_nested_combos == 816
    assert report_18.n_joint_compliant == 500
    assert report_18.joint_compliance == pytest.approx(500 / 816)

    assert report_19.n_nested_combos == 3876
    assert report_19.n_joint_compliant == 1823
    assert report_19.joint_compliance == pytest.approx(1823 / 3876)


def test_extend_pool_recovers_optimal_additions(extractor: FeatureExtractor, pipeline: FilterPipeline):
    optimizer = PoolOptimizer(extractor, pipeline)
    pool, score = optimizer.extend_pool(
        core=CORE_COMBO, additions=3, candidates=(11, 16, 18, 21), reference_draw=DRAW_3779
    )
    assert pool == POOL_18
    assert score == 500


def test_omission_rationale_covers_every_excluded_number(extractor: FeatureExtractor, pipeline: FilterPipeline):
    optimizer = PoolOptimizer(extractor, pipeline)
    profiles = extractor.number_profiles(_synthetic_frame(), window=2)
    reasons = optimizer.omission_rationale(POOL_19, profiles)

    omitted_numbers = {r.number for r in reasons}
    assert omitted_numbers == set(range(1, 26)) - set(POOL_19)
    assert all(r.reasons for r in reasons)  # every omission is explained
