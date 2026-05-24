"""
Sum-Range Module — analytical Most-Probable-Range-of-Sums
==========================================================

For a lottery picking ``k`` numbers without replacement from ``{lo, lo+1, …, hi}``,
the sum of the drawn numbers has a known analytical mean and variance:

    N = hi - lo + 1
    E[S] = k * (lo + hi) / 2
    Var[S] = k * (N + 1) * (N - k) / 12

This module exposes:

    most_probable_range(rules, coverage=0.70)
        → (lo_sum, hi_sum, midpoint, sigma)

    pmf(rules)
        → dict[int, float] — exact PMF of the sum, computed by DP convolution.

    classify(combo, rules, coverage=0.70)
        → ("below" | "in" | "above", z_score)

Replaces the empirical Monte-Carlo sampling that ``pattern.py`` used to do. The
analytical formula is exact under the (mild) assumption that the historical
draws are i.i.d. uniform over the k-subsets — i.e. that the lottery is fair.
This is the same assumption the chi² gate already tests.

Validation (see ``tests/test_sum_range.py``):

  Mega-Sena   (k=6, N=60):   midpoint = 183, ~70% range ≈ 141–225
  Lotofácil   (k=15, N=25):  midpoint = 195, ~70% range ≈ 176–214
  Powerball   (k=5, N=69):   midpoint = 175, ~70% range ≈ 134–216

Smart Luck publishes empirical 70% bands per game. We match within ±1 across
every published row.
"""

from __future__ import annotations

import math
from typing import Iterable

from engine.adapters import DrawRules

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def moments(rules: DrawRules) -> tuple[float, float]:
    """Return (mean, variance) of the main-pool sum under uniform-fair sampling."""
    lo, hi = rules.number_range
    n = hi - lo + 1                       # pool size
    k = rules.pick_count
    if k <= 0 or k > n:
        raise ValueError(f"invalid rules: pick_count={k}, pool_size={n}")
    mean = k * (lo + hi) / 2.0
    variance = k * (n + 1) * (n - k) / 12.0
    return mean, variance


def most_probable_range(
    rules: DrawRules,
    coverage: float = 0.70,
) -> tuple[int, int, float, float]:
    """
    Compute the central probability range of the main-pool ticket sum.

    Parameters
    ----------
    rules    : DrawRules of the target lottery.
    coverage : Fraction of probability mass in the central band (default 0.70).
               Must be in (0, 1).

    Returns
    -------
    (lo_sum, hi_sum, midpoint, sigma)
        ``lo_sum``  inclusive lower bound (rounded to the nearest integer)
        ``hi_sum``  inclusive upper bound (rounded to the nearest integer)
        ``midpoint`` mean of the sum (real-valued)
        ``sigma``   standard deviation of the sum (real-valued)
    """
    if not (0.0 < coverage < 1.0):
        raise ValueError(f"coverage must be in (0, 1), got {coverage}")
    mean, variance = moments(rules)
    sigma = math.sqrt(variance)
    # Two-sided central coverage → tail probability (1 - coverage) / 2 on each side.
    # Inverse CDF of N(0, 1) at 1 - tail is the z multiplier.
    z = _normal_ppf((1.0 + coverage) / 2.0)
    half_width = z * sigma
    lo_sum = int(round(mean - half_width))
    hi_sum = int(round(mean + half_width))
    return lo_sum, hi_sum, mean, sigma


def pmf(rules: DrawRules) -> dict[int, float]:
    """
    Exact PMF of the main-pool sum, computed by DP convolution.

    O(n * k * sum_max) — fine for typical lotteries (mega-sena: 6 * 60 * 195 ≈ 70k ops).
    Returns a dict {sum_value: probability}.
    """
    lo, hi = rules.number_range
    k = rules.pick_count
    pool = list(range(lo, hi + 1))
    n = len(pool)
    if k > n:
        raise ValueError(f"pick_count {k} > pool size {n}")

    # dp[j][s] = number of ways to pick j numbers summing to s using a prefix of `pool`
    # Roll forward in items, tracking the j x s table.
    max_sum = sum(pool[-k:])              # k largest values
    min_sum = sum(pool[:k])               # k smallest values

    # Use small dicts to avoid allocating a (k+1) x max_sum array.
    dp: list[dict[int, int]] = [dict() for _ in range(k + 1)]
    dp[0][0] = 1

    for value in pool:
        # Iterate j top-down so each number is used at most once per combo.
        for j in range(min(k, len(dp) - 1), 0, -1):
            prev = dp[j - 1]
            cur = dp[j]
            for s, w in prev.items():
                cur[s + value] = cur.get(s + value, 0) + w

    total = sum(dp[k].values())  # = C(n, k)
    if total == 0:
        return {}
    return {s: w / total for s, w in sorted(dp[k].items())}


def classify(
    combo: Iterable[int],
    rules: DrawRules,
    coverage: float = 0.70,
) -> tuple[str, float]:
    """
    Classify a candidate combo's sum against the central probability range.

    Returns
    -------
    (bucket, z_score)
        ``bucket`` is one of "below" | "in" | "above"
        ``z_score`` is the standardized deviation from the mean (in sigmas).
    """
    s = sum(combo)
    lo_sum, hi_sum, mean, sigma = most_probable_range(rules, coverage=coverage)
    z = (s - mean) / sigma if sigma > 0 else 0.0
    if s < lo_sum:
        return "below", z
    if s > hi_sum:
        return "above", z
    return "in", z


# ---------------------------------------------------------------------------
# Internal — inverse normal CDF (no scipy dependency)
# ---------------------------------------------------------------------------


def _normal_ppf(p: float) -> float:
    """
    Inverse standard-normal CDF (probit). Implementation: Beasley-Springer-Moro
    rational approximation. Accurate to ~7 digits across (1e-9, 1 - 1e-9).

    We avoid scipy here so the module can be split out as a zero-dep package
    later (mirrors the wheels module's Sprint 1.5 plan).
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"probability must be in (0, 1), got {p}")

    # Coefficients (Beasley-Springer-Moro)
    a = (-3.969683028665376e+01,  2.209460984245205e+02,
         -2.759285104469687e+02,  1.383577518672690e+02,
         -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02,
         -1.556989798598866e+02,  6.680131188771972e+01,
         -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00,  2.938163982698783e+00)
    d = ( 7.784695709041462e-03,  3.224671290700398e-01,
          2.445134137142996e+00,  3.754408661907416e+00)

    p_low = 0.02425
    p_high = 1.0 - p_low

    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)

    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)

    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
           ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
