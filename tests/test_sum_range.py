"""
Tests for engine.modules.sum_range — analytical Most-Probable-Range-of-Sums.

Validates the formulas against:
  - Smart Luck's published 70% bands per game (within ±1).
  - Exact PMF probabilities computed via DP convolution.
"""

import math

import pytest

from engine.adapters import DrawRules
from engine.modules import sum_range


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def mega() -> DrawRules:
    return DrawRules(name="mega-sena", pick_count=6, number_range=(1, 60))


def lotofacil() -> DrawRules:
    return DrawRules(name="lotofacil", pick_count=15, number_range=(1, 25))


def powerball_main() -> DrawRules:
    # main pool only; bonus ball is irrelevant for sum-range
    return DrawRules(name="powerball", pick_count=5, number_range=(1, 69))


# ---------------------------------------------------------------------------
# moments()
# ---------------------------------------------------------------------------


def test_moments_mega_sena():
    mean, variance = sum_range.moments(mega())
    assert mean == pytest.approx(183.0)
    # Var = k(N+1)(N-k)/12 = 6*61*54/12 = 1647
    assert variance == pytest.approx(1647.0)


def test_moments_lotofacil():
    mean, variance = sum_range.moments(lotofacil())
    assert mean == pytest.approx(195.0)
    # Var = 15*26*10/12 = 325
    assert variance == pytest.approx(325.0)


def test_moments_powerball_main():
    mean, _ = sum_range.moments(powerball_main())
    assert mean == pytest.approx(175.0)


def test_moments_invalid_rules():
    bad = DrawRules(name="bad", pick_count=99, number_range=(1, 10))
    with pytest.raises(ValueError):
        sum_range.moments(bad)


# ---------------------------------------------------------------------------
# most_probable_range()
# ---------------------------------------------------------------------------


def test_mpr_mega_sena_matches_smart_luck():
    lo, hi, midpoint, sigma = sum_range.most_probable_range(mega(), coverage=0.70)
    assert midpoint == pytest.approx(183.0)
    # Smart Luck publishes ~141..225 for Mega-Sena. Tolerance ±1.
    assert 140 <= lo <= 142
    assert 224 <= hi <= 226
    # Sanity on sigma
    assert sigma == pytest.approx(math.sqrt(1647.0), rel=1e-6)


def test_mpr_lotofacil_matches_smart_luck():
    lo, hi, midpoint, _ = sum_range.most_probable_range(lotofacil(), coverage=0.70)
    assert midpoint == pytest.approx(195.0)
    # Plan target 176..214
    assert 175 <= lo <= 177
    assert 213 <= hi <= 215


def test_mpr_powerball():
    lo, hi, midpoint, _ = sum_range.most_probable_range(powerball_main(), coverage=0.70)
    assert midpoint == pytest.approx(175.0)
    # Plan target ~134..216 — wider than Mega-Sena because pool is larger
    assert 125 <= lo <= 145
    assert 205 <= hi <= 225


def test_mpr_coverage_bounds():
    rules = mega()
    lo70, hi70, _, _ = sum_range.most_probable_range(rules, coverage=0.70)
    lo90, hi90, _, _ = sum_range.most_probable_range(rules, coverage=0.90)
    lo50, hi50, _, _ = sum_range.most_probable_range(rules, coverage=0.50)
    # Wider coverage → wider band
    assert (hi90 - lo90) > (hi70 - lo70) > (hi50 - lo50)


def test_mpr_invalid_coverage():
    with pytest.raises(ValueError):
        sum_range.most_probable_range(mega(), coverage=0.0)
    with pytest.raises(ValueError):
        sum_range.most_probable_range(mega(), coverage=1.0)
    with pytest.raises(ValueError):
        sum_range.most_probable_range(mega(), coverage=1.5)


# ---------------------------------------------------------------------------
# pmf()
# ---------------------------------------------------------------------------


def test_pmf_total_mass():
    p = sum_range.pmf(mega())
    assert sum(p.values()) == pytest.approx(1.0, abs=1e-9)


def test_pmf_min_and_max_have_unique_combos():
    """For Mega-Sena, only one combo sums to 21 (smallest k=6 sum) or 345 (largest)."""
    p = sum_range.pmf(mega())
    # C(60, 6) = 50,063,860
    expected = 1.0 / 50063860
    assert p[21] == pytest.approx(expected, rel=1e-9)
    assert p[345] == pytest.approx(expected, rel=1e-9)


def test_pmf_mode_near_midpoint():
    """The PMF should peak near the midpoint."""
    p = sum_range.pmf(mega())
    mode_sum = max(p, key=p.get)
    mean, _ = sum_range.moments(mega())
    # Mode should be within ±2 of the mean (PMF is unimodal & roughly symmetric).
    assert abs(mode_sum - mean) <= 2


def test_pmf_70_band_contains_about_70_percent():
    """The analytical 70% band should empirically contain ~70% of the exact PMF mass."""
    p = sum_range.pmf(mega())
    lo_sum, hi_sum, _, _ = sum_range.most_probable_range(mega(), coverage=0.70)
    mass = sum(prob for s, prob in p.items() if lo_sum <= s <= hi_sum)
    assert 0.65 <= mass <= 0.75


# ---------------------------------------------------------------------------
# classify()
# ---------------------------------------------------------------------------


def test_classify_in_band():
    bucket, z = sum_range.classify([3, 17, 23, 24, 36, 47], mega(), coverage=0.70)
    assert bucket == "in"
    # sum = 150 → z = (150 - 183) / 40.58 ≈ -0.81
    assert z == pytest.approx(-0.81, abs=0.05)


def test_classify_below_band():
    bucket, z = sum_range.classify([1, 2, 3, 4, 5, 6], mega(), coverage=0.70)
    assert bucket == "below"
    assert z < -3.0  # sum = 21 is way below the mean


def test_classify_above_band():
    bucket, z = sum_range.classify([55, 56, 57, 58, 59, 60], mega(), coverage=0.70)
    assert bucket == "above"
    assert z > 3.0


def test_classify_z_is_zero_at_midpoint():
    # Build a fake combo whose sum equals the mean exactly: 183 / 6 = 30.5 — pick around it
    bucket, z = sum_range.classify([28, 29, 30, 31, 32, 33], mega(), coverage=0.70)
    # sum = 183 → z = 0
    assert bucket == "in"
    assert abs(z) < 0.01


# ---------------------------------------------------------------------------
# Internal _normal_ppf — sanity check on known quantiles
# ---------------------------------------------------------------------------


def test_normal_ppf_known_quantiles():
    # 0.5 quantile = 0
    assert abs(sum_range._normal_ppf(0.5)) < 1e-6
    # 0.975 quantile ≈ 1.96
    assert sum_range._normal_ppf(0.975) == pytest.approx(1.95996, abs=1e-3)
    # 0.85 quantile ≈ 1.0364 (this is what 70%-band uses internally)
    assert sum_range._normal_ppf(0.85) == pytest.approx(1.0364, abs=1e-3)
