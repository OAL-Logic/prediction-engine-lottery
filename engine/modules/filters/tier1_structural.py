from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING
from engine.modules.filters import VectorizedFilter, PRIMES, count_bits_64

if TYPE_CHECKING:
    from engine.adapters import DrawRules

class OddCountFilter(VectorizedFilter):
    unique_id = "structural_odd_count"
    display_name = "Odd Number Count"
    tier = 1
    description = "Checks if the number of odd balls is within 30-70% range."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_counts = np.sum(combinations % 2, axis=1)
        n_picked = combinations.shape[1]
        return (odd_counts >= max(1, int(0.3 * n_picked))) & (odd_counts <= min(n_picked - 1, int(0.7 * n_picked)))

class PrimeCountFilter(VectorizedFilter):
    unique_id = "structural_prime_count"
    display_name = "Prime Number Count"
    tier = 1
    description = "Checks if the number of prime balls matches expected frequency."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        prime_counts = np.sum(np.isin(combinations, PRIMES), axis=1)
        return (prime_counts >= 1) & (prime_counts <= int(0.7 * combinations.shape[1]))

class ACValueFilter(VectorizedFilter):
    unique_id = "structural_ac_value"
    display_name = "Arithmetic Complexity (AC)"
    tier = 1
    description = "Calculates the variation of differences. AC = (UniqueDiffs) - (k-1)."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        n_rows, k = combinations.shape
        if k < 2: return np.ones(n_rows, dtype=bool)
        sorted_combs = np.sort(combinations, axis=1)
        bitmasks = np.zeros(n_rows, dtype=np.uint64)
        for i in range(k):
            for j in range(i + 1, k):
                diff = sorted_combs[:, j] - sorted_combs[:, i]
                bitmasks |= (np.uint64(1) << (diff.astype(np.uint64) - 1))
        unique_counts = count_bits_64(bitmasks)
        min_ac = 7 if k == 6 else (k - 1)
        return (unique_counts - (k - 1)) >= min_ac

class EvenCountFilter(VectorizedFilter):
    unique_id = "structural_even_count"
    display_name = "Even Number Count"
    tier = 1
    description = "Checks if the number of even balls is within expected range."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        even_counts = np.sum(combinations % 2 == 0, axis=1)
        n_picked = combinations.shape[1]
        return (even_counts >= 1) & (even_counts <= n_picked - 1)

class HighCountFilter(VectorizedFilter):
    unique_id = "structural_high_count"
    display_name = "High Number Count"
    tier = 1
    description = "Numbers in the upper half of the range."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        high_counts = np.sum(combinations > mid, axis=1)
        return (high_counts >= 1) & (high_counts <= combinations.shape[1] - 1)

class LowCountFilter(VectorizedFilter):
    unique_id = "structural_low_count"
    display_name = "Low Number Count"
    tier = 1
    description = "Numbers in the lower half of the range."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        low_counts = np.sum(combinations <= mid, axis=1)
        return (low_counts >= 1) & (low_counts <= combinations.shape[1] - 1)

class DigitSumFilter(VectorizedFilter):
    unique_id = "structural_digit_sum"
    display_name = "Total Digit Sum"
    tier = 1
    description = "Sum of all digits of all numbers in the ticket."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Vectorized digit sum: (n // 10) + (n % 10) for numbers < 100
        digit_sums = np.sum((combinations // 10) + (combinations % 10), axis=1)
        return (digit_sums >= 20) & (digit_sums <= 60)

class UnitSumFilter(VectorizedFilter):
    unique_id = "structural_unit_sum"
    display_name = "Total Unit Sum"
    tier = 1
    description = "Sum of the last digits (units) of all numbers."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        unit_sums = np.sum(combinations % 10, axis=1)
        return (unit_sums >= 10) & (unit_sums <= 45)

class CompositeCountFilter(VectorizedFilter):
    unique_id = "structural_composite_count"
    display_name = "Composite Number Count"
    tier = 1

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        is_composite = (combinations > 1) & ~np.isin(combinations, PRIMES)
        counts = np.sum(is_composite, axis=1)
        return counts >= 1

class SquareCountFilter(VectorizedFilter):
    unique_id = "structural_square_count"
    display_name = "Square Number Count"
    tier = 1
    
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        squares = np.array([1, 4, 9, 16, 25, 36, 49, 64, 81, 100])
        counts = np.sum(np.isin(combinations, squares), axis=1)
        return counts <= 2

class FibonacciCountFilter(VectorizedFilter):
    unique_id = "structural_fibonacci_count"
    display_name = "Fibonacci Number Count"
    tier = 1

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        fibs = np.array([1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
        counts = np.sum(np.isin(combinations, fibs), axis=1)
        return counts <= 3

class Decade1CountFilter(VectorizedFilter):
    unique_id = "structural_decade_1"
    display_name = "Decade 1 (1-10) Count"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 1) & (combinations <= 10), axis=1)
        return counts <= 3

class Decade2CountFilter(VectorizedFilter):
    unique_id = "structural_decade_2"
    display_name = "Decade 2 (11-20) Count"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 11) & (combinations <= 20), axis=1)
        return counts <= 3

class Decade3CountFilter(VectorizedFilter):
    unique_id = "structural_decade_3"
    display_name = "Decade 3 (21-30) Count"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 21) & (combinations <= 30), axis=1)
        return counts <= 3

class Decade4CountFilter(VectorizedFilter):
    unique_id = "structural_decade_4"
    display_name = "Decade 4 (31-40) Count"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 31) & (combinations <= 40), axis=1)
        return counts <= 3

class Decade5CountFilter(VectorizedFilter):
    unique_id = "structural_decade_5"
    display_name = "Decade 5 (41-50) Count"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 41) & (combinations <= 50), axis=1)
        return counts <= 3

class Decade6CountFilter(VectorizedFilter):
    unique_id = "structural_decade_6"
    display_name = "Decade 6 (51-60) Count"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 51) & (combinations <= 60), axis=1)
        return counts <= 3

class OddEvenRatioFilter(VectorizedFilter):
    unique_id = "structural_odd_even_ratio"
    display_name = "Odd/Even Ratio"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_counts = np.sum(combinations % 2 != 0, axis=1)
        even_counts = combinations.shape[1] - odd_counts
        # Balanced ratio: e.g. 3:3, 2:4, 4:2 for 6 picked
        return (np.abs(odd_counts - even_counts) <= 2)

class LowHighRatioFilter(VectorizedFilter):
    unique_id = "structural_low_high_ratio"
    display_name = "Low/High Ratio"
    tier = 1
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        low_counts = np.sum(combinations <= mid, axis=1)
        high_counts = combinations.shape[1] - low_counts
        return (np.abs(low_counts - high_counts) <= 2)
