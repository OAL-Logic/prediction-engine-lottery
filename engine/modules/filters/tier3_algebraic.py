from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING
from engine.modules.filters import VectorizedFilter

if TYPE_CHECKING:
    from engine.adapters import DrawRules

class NumberSumFilter(VectorizedFilter):
    unique_id = "algebraic_number_sum"
    display_name = "Number Sum"
    tier = 3

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ticket_sums = np.sum(combinations, axis=1)
        expected_avg = sum(rules.number_range) / 2
        ideal = expected_avg * combinations.shape[1]
        return (ticket_sums >= ideal * 0.7) & (ticket_sums <= ideal * 1.3)

class DividedByNFilter(VectorizedFilter):
    def __init__(self, n: int):
        self.divisor = n
        self.unique_id = f"algebraic_div_by_{n}"
        self.display_name = f"Divided by {n}"
        self.tier = 3

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mod_counts = np.sum(combinations % self.divisor == 0, axis=1)
        expected = combinations.shape[1] / self.divisor
        return (mod_counts >= max(0, int(expected - 1))) & (mod_counts <= int(expected + 2))

class DividedBy11Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_11"
    display_name = "Divided by 11 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 11 == 0, axis=1)
        return counts <= 2

class DividedBy12Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_12"
    display_name = "Divided by 12 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 12 == 0, axis=1)
        return counts <= 2

class DividedBy13Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_13"
    display_name = "Divided by 13 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 13 == 0, axis=1)
        return counts <= 2

class DividedBy14Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_14"
    display_name = "Divided by 14 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 14 == 0, axis=1)
        return counts <= 2

class DividedBy15Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_15"
    display_name = "Divided by 15 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 15 == 0, axis=1)
        return counts <= 2

class DividedBy16Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_16"
    display_name = "Divided by 16 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 16 == 0, axis=1)
        return counts <= 2

class DividedBy17Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_17"
    display_name = "Divided by 17 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 17 == 0, axis=1)
        return counts <= 2

class DividedBy18Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_18"
    display_name = "Divided by 18 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 18 == 0, axis=1)
        return counts <= 2

class DividedBy19Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_19"
    display_name = "Divided by 19 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 19 == 0, axis=1)
        return counts <= 2

class DividedBy20Filter(VectorizedFilter):
    unique_id = "algebraic_div_by_20"
    display_name = "Divided by 20 Count"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum(combinations % 20 == 0, axis=1)
        return counts <= 2

class RootSumFilter(VectorizedFilter):
    unique_id = "algebraic_root_sum"
    display_name = "Root Sum"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ticket_sums = np.sum(combinations, axis=1)
        root_sums = 1 + (ticket_sums - 1) % 9
        return (root_sums >= 1) & (root_sums <= 9)

class UnitSumParityFilter(VectorizedFilter):
    unique_id = "algebraic_unit_sum_parity"
    display_name = "Unit Sum Parity"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        unit_sums = np.sum(combinations % 10, axis=1)
        return unit_sums % 2 == 0

class Mod3DistributionFilter(VectorizedFilter):
    unique_id = "algebraic_mod3_dist"
    display_name = "Mod 3 Distribution"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mods = combinations % 3
        c0 = np.sum(mods == 0, axis=1)
        c1 = np.sum(mods == 1, axis=1)
        c2 = np.sum(mods == 2, axis=1)
        return (c0 <= 4) & (c1 <= 4) & (c2 <= 4)

class Mod4DistributionFilter(VectorizedFilter):
    unique_id = "algebraic_mod4_dist"
    display_name = "Mod 4 Distribution"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mods = combinations % 4
        return np.all([np.sum(mods == i, axis=1) <= 3 for i in range(4)], axis=0)

class GeometricMeanFilter(VectorizedFilter):
    unique_id = "algebraic_geometric_mean"
    display_name = "Geometric Mean"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Product can overflow, use log sum
        log_sums = np.sum(np.log(combinations), axis=1)
        geo_means = np.exp(log_sums / combinations.shape[1])
        return (geo_means >= 5) & (geo_means <= 45)

class HarmonicMeanFilter(VectorizedFilter):
    unique_id = "algebraic_harmonic_mean"
    display_name = "Harmonic Mean"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        inv_sums = np.sum(1.0 / combinations, axis=1)
        har_means = combinations.shape[1] / inv_sums
        return (har_means >= 2) & (har_means <= 40)

class PrimeSumFilter(VectorizedFilter):
    unique_id = "algebraic_prime_sum"
    display_name = "Prime Sum"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        primes = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59])
        prime_mask = np.isin(combinations, primes)
        prime_sums = np.sum(combinations * prime_mask, axis=1)
        return (prime_sums >= 0) & (prime_sums <= 150)

class EvenSumFilter(VectorizedFilter):
    unique_id = "algebraic_even_sum"
    display_name = "Even Number Sum"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        even_mask = (combinations % 2 == 0)
        even_sums = np.sum(combinations * even_mask, axis=1)
        return (even_sums >= 20) & (even_sums <= 200)

class OddSumFilter(VectorizedFilter):
    unique_id = "algebraic_odd_sum"
    display_name = "Odd Number Sum"
    tier = 3
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_mask = (combinations % 2 != 0)
        odd_sums = np.sum(combinations * odd_mask, axis=1)
        return (odd_sums >= 20) & (odd_sums <= 200)
