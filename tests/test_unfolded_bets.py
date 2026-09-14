"""Tests for engine.modules.unfolded_bets — desdobramento (unfolded ticket) economics."""

from __future__ import annotations

import pytest

from engine.adapters.br.lotofacil import LotofacilAdapter
from engine.modules import unfolded_bets as ub

RULES = LotofacilAdapter.rules

PRIZE_TABLE = {11: 6.0, 12: 12.0, 13: 30.0, 14: 1800.0, 15: 2_000_000.0}


def test_multiplier_matrix_totals_match_games_played():
    for n in (18, 19):
        matrix = ub.multiplier_matrix(RULES, n)
        # Every sub-game of a fully-hit ticket (hits == pick_count) is won at
        # *some* tier — rows for hits == pick_count must sum to C(n, pick).
        from math import comb

        assert sum(matrix[RULES.pick_count].values()) == comb(n, RULES.pick_count)


def test_multiplier_matrix_known_cells_18_and_19():
    # Values below are the standard, publicly documented Caixa "desdobramento"
    # multiplier table for Lotofácil (18 and 19-number single tickets).
    m18 = ub.multiplier_matrix(RULES, 18)
    assert m18[11] == {11: 35, 12: 0, 13: 0, 14: 0, 15: 0}
    assert m18[15] == {11: 0, 12: 455, 13: 315, 14: 45, 15: 1}

    m19 = ub.multiplier_matrix(RULES, 19)
    assert m19[11][11] == 70
    assert m19[15][15] == 1


def test_hit_probability_is_a_valid_distribution():
    for n in (18, 19):
        total = sum(ub.hit_probability(RULES, n, h) for h in range(0, RULES.pick_count + 1))
        assert total == pytest.approx(1.0, abs=1e-9)


def test_p_any_prize_matches_expected_ballpark():
    ev18 = ub.evaluate(RULES, 18, PRIZE_TABLE, ticket_price=3.5)
    ev19 = ub.evaluate(RULES, 19, PRIZE_TABLE, ticket_price=3.5)
    assert ev18.p_any_prize == pytest.approx(0.6014, abs=1e-3)
    assert ev19.p_any_prize == pytest.approx(0.8022, abs=1e-3)
    assert ev18.n_games == 816
    assert ev19.n_games == 3876


def test_roi_percent_is_invariant_to_unfold_size():
    """The core rigor claim of this module: unfolding buys more combinations
    (and thus a higher P(any prize) and higher variance) proportionally to
    cost, but does not change the expected ROI% — a direct consequence of the
    hypergeometric structure. Any regression that breaks this invariant is a
    correctness bug, not a modeling choice."""
    rois = [
        ub.evaluate(RULES, n, PRIZE_TABLE, ticket_price=3.5).roi_pct
        for n in RULES.allowed_picks
        if n <= 19
    ]
    assert len(rois) >= 2
    for r in rois[1:]:
        assert r == pytest.approx(rois[0], abs=1e-6)


def test_compare_configurations_cost_and_roi():
    configs = [
        ub.BetConfiguration(label="1x19", n_picked=19, copies=1),
        ub.BetConfiguration(label="4x18", n_picked=18, copies=4),
    ]
    results = ub.compare_configurations(RULES, configs, PRIZE_TABLE, ticket_price=3.5)
    by_label = {r.label: r for r in results}

    assert by_label["1x19"].total_cost == pytest.approx(3876 * 3.5)
    assert by_label["4x18"].total_cost == pytest.approx(4 * 816 * 3.5)
    # Both configurations face the same house edge.
    assert by_label["1x19"].roi_pct == pytest.approx(by_label["4x18"].roi_pct, abs=1e-6)
