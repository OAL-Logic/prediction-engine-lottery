"""Unit tests for engine/modules/hybrid_synthesis.py multi-modal models."""

import datetime as dt
import itertools
from pathlib import Path

from engine.modules.hybrid_synthesis import (
    BipartiteMarkovChain,
    BoardGeometryAndBoundaryBalancer,
    CoveringWheelCatalogAndSynthesizer,
    DeterministicWeatherCorrelator,
    LaplaceBayesianTracker,
    MasterNumerologyResonator,
    SynodicAstronomyModel,
    TriModalWeightedEnsemble,
)


SAMPLE_DRAWS_25 = [
    [1, 2, 3, 5, 7, 8, 10, 11, 13, 14, 16, 18, 20, 22, 25],
    [2, 4, 5, 6, 8, 9, 11, 12, 14, 15, 17, 19, 21, 23, 24],
    [1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 20, 22, 25],
    [2, 3, 5, 7, 8, 10, 11, 13, 14, 17, 19, 21, 22, 23, 25],
    [1, 4, 5, 6, 8, 9, 11, 12, 14, 16, 18, 20, 21, 24, 25],
]


def test_synodic_astronomy_model():
    model = SynodicAstronomyModel()
    epoch = dt.datetime(2000, 1, 6, 18, 14, 0)
    phase = model.get_moon_phase(epoch)
    assert abs(phase) < 1e-6
    assert model.get_phase_name(phase) == "New Moon"

    scores = model.score_lunar_resonance(pool_size=25, target_date=epoch)
    assert len(scores) == 25
    assert all(w > 0.0 for w in scores.values())
    # At New Moon (moon_dist=0.0), ball 1 has stronger resonance than ball 25
    assert scores[1] > scores[25]


def test_laplace_bayesian_tracker():
    tracker = LaplaceBayesianTracker(pool_size=25, alpha=1.0, decay_factor=1.0)
    tracker.fit(SAMPLE_DRAWS_25)
    probs = dict(tracker.get_probabilities())
    assert len(probs) == 25

    # Ball 25 appears in 4 of 5 draws -> higher posterior than ball 15 (2 of 5 draws)
    assert probs[25] > probs[15]
    hot, cold = tracker.get_hot_cold(top_n=5)
    assert len(hot) == 5
    assert len(cold) == 5

    tracker_decay = LaplaceBayesianTracker(pool_size=25, alpha=1.0, decay_factor=0.85)
    tracker_decay.fit(SAMPLE_DRAWS_25)
    probs_decay = dict(tracker_decay.get_probabilities())
    assert len(probs_decay) == 25


def test_bipartite_markov_chain():
    chain = BipartiteMarkovChain(pool_size=25, lag2_weight=0.25)
    chain.fit(SAMPLE_DRAWS_25)
    probs = dict(
        chain.get_probabilities(
            last_draw=SAMPLE_DRAWS_25[-1],
            prev_draw=SAMPLE_DRAWS_25[-2],
        )
    )
    assert len(probs) == 25
    assert max(probs.values()) > 0.0


def test_master_numerology_resonator():
    resonator = MasterNumerologyResonator()
    # "1990-01-01" -> 1+9+9+0+0+1+0+1 = 21 -> 2+1 = 3
    assert resonator.calculate_life_path(dt.date(1990, 1, 1)) == 3
    # "2000-04-16" -> 2+0+0+0+0+4+1+6 = 13 -> 4
    assert resonator.calculate_life_path(dt.date(2000, 4, 16)) == 4
    # Master number preservation: 1990-02-01 -> 1+9+9+0+0+2+0+1 = 22 (Master Number)
    assert resonator.calculate_life_path(dt.date(1990, 2, 1)) == 22

    scores = resonator.score_numerology_affinity(25, dt.date(1990, 2, 1))
    assert len(scores) == 25
    assert scores[22] > scores[1]


def test_deterministic_weather_correlator():
    correlator = DeterministicWeatherCorrelator()
    w1 = correlator.get_weather_for_date(dt.date(2026, 1, 15))
    w2 = correlator.get_weather_for_date(dt.date(2026, 1, 15))
    assert w1 == w2
    assert 15 <= w1["temperature"] <= 35
    assert 30 <= w1["humidity"] <= 90

    draws_with_dates = [
        {"date": dt.date(2026, 1, i + 1), "nums": draw}
        for i, draw in enumerate(SAMPLE_DRAWS_25)
    ]
    corr = correlator.compute_correlation_summary(draws_with_dates)
    assert "moon_vs_sum" in corr
    assert "temp_vs_sum" in corr
    assert "humidity_vs_even" in corr


def test_board_geometry_and_boundary_balancer():
    assert len(BoardGeometryAndBoundaryBalancer.FRAME_25) == 16
    assert len(BoardGeometryAndBoundaryBalancer.CENTER_25) == 9
    assert BoardGeometryAndBoundaryBalancer.FRAME_25.isdisjoint(
        BoardGeometryAndBoundaryBalancer.CENTER_25
    )

    # Low-sum candidate order: 1..25 -> top 15 is 1..15 (sum=120 < 170)
    ranked_candidates = list(range(1, 26))
    balanced = BoardGeometryAndBoundaryBalancer.balance_ticket_sum(
        ranked_candidates, pick_count=15, sum_min=170, sum_max=220
    )
    assert len(balanced) == 15
    assert len(set(balanced)) == 15
    assert 170 <= sum(balanced) <= 220

    profile = BoardGeometryAndBoundaryBalancer.calculate_lotofacil_profile(
        balanced, previous_draw=SAMPLE_DRAWS_25[-1], sum_bounds=(170, 220)
    )
    assert profile["sum"] == sum(balanced)
    assert profile["sum_balanced"] is True
    assert profile["frame"] + profile["center"] == 15


def test_tri_modal_weighted_ensemble():
    ensemble = TriModalWeightedEnsemble(
        pool_size=25, pick_count=15, sum_bounds=(170, 220)
    )
    result = ensemble.predict(
        draws=SAMPLE_DRAWS_25,
        target_date=dt.date(2026, 1, 15),
    )
    assert len(result.recommended_ticket) == 15
    assert len(set(result.recommended_ticket)) == 15
    assert 170 <= sum(result.recommended_ticket) <= 220
    assert result.profile["sum_balanced"] is True


def test_covering_wheel_catalog_and_synthesizer():
    catalog_path = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "reference"
        / "architecture"
        / "wheels-catalog.csv"
    )
    wheel_engine = CoveringWheelCatalogAndSynthesizer(csv_path=catalog_path)
    bound = wheel_engine.lookup_bound(pick_k=6, pool_v=12, guarantee_t=4, condition_m=4)
    assert bound is not None
    assert bound["tickets_count"] > 0

    # Synthesize a 4-from-8 wheel guaranteeing 3-if-3
    pool = [2, 5, 9, 12, 15, 19, 22, 25]
    tickets = CoveringWheelCatalogAndSynthesizer.synthesize_covering_wheel(
        pool_numbers=pool, pick_k=4, guarantee_t=3, condition_m=3, seed=42
    )
    assert len(tickets) > 0
    # Verify 100% 3-if-3 coverage across all C(8, 3) = 56 3-subsets
    for m_sub in itertools.combinations(pool, 3):
        m_set = set(m_sub)
        assert any(len(set(t) & m_set) >= 3 for t in tickets)
