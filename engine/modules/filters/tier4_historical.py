from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING
from engine.modules.filters import VectorizedFilter

if TYPE_CHECKING:
    from engine.adapters import DrawRules

class HotColdFilter(VectorizedFilter):
    unique_id = "historical_hot_cold"
    display_name = "Hot-Cold Distribution"
    tier = 4

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        hot_nums = getattr(rules, 'hot_numbers', [])
        if not hot_nums: return np.ones(combinations.shape[0], dtype=bool)
        hot_counts = np.sum(np.isin(combinations, hot_nums), axis=1)
        return (hot_counts >= 2) & (hot_counts <= 5)

class HistoricalRepeatFilter(VectorizedFilter):
    unique_id = "historical_repeat"
    display_name = "Historical Repeat"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        last_draw = getattr(rules, 'last_draw', [])
        if not last_draw: return np.ones(combinations.shape[0], dtype=bool)
        repeats = np.sum(np.isin(combinations, last_draw), axis=1)
        return (repeats >= 0) & (repeats <= 2)

class ColdNumbersFilter(VectorizedFilter):
    unique_id = "historical_cold_numbers"
    display_name = "Cold Numbers Count"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        cold_nums = getattr(rules, 'cold_numbers', [])
        if not cold_nums: return np.ones(combinations.shape[0], dtype=bool)
        counts = np.sum(np.isin(combinations, cold_nums), axis=1)
        return (counts >= 0) & (counts <= 2)

class OverdueNumbersFilter(VectorizedFilter):
    unique_id = "historical_overdue"
    display_name = "Overdue Numbers"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        overdue = getattr(rules, 'overdue_numbers', [])
        if not overdue: return np.ones(combinations.shape[0], dtype=bool)
        counts = np.sum(np.isin(combinations, overdue), axis=1)
        return (counts >= 1)

class HistoricalSumRangeFilter(VectorizedFilter):
    unique_id = "historical_sum_range"
    display_name = "Historical Sum Range"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sums = np.sum(combinations, axis=1)
        # Typically sums fall in a bell curve
        return (sums >= 100) & (sums <= 250)

class RecentDrawsExclusionFilter(VectorizedFilter):
    unique_id = "historical_recent_exclusion"
    display_name = "Recent Draws Exclusion"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Exclude exactly matching any of the last 10 draws (placeholder)
        recent = getattr(rules, 'recent_draws', [])
        if not recent: return np.ones(combinations.shape[0], dtype=bool)
        # This would be slow if not vectorized properly, but for small 'recent' it's fine
        mask = np.ones(combinations.shape[0], dtype=bool)
        for draw in recent:
            match = np.all(np.isin(combinations, draw), axis=1)
            mask &= ~match
        return mask

class HistoricalOddEvenPatternFilter(VectorizedFilter):
    unique_id = "historical_oe_pattern"
    display_name = "Historical O/E Pattern"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_counts = np.sum(combinations % 2 != 0, axis=1)
        # Most common are 3:3, 2:4, 4:2
        return (odd_counts >= 2) & (odd_counts <= 4)

class HistoricalHighLowPatternFilter(VectorizedFilter):
    unique_id = "historical_hl_pattern"
    display_name = "Historical H/L Pattern"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        high_counts = np.sum(combinations > mid, axis=1)
        return (high_counts >= 2) & (high_counts <= 4)

class HistoricalDecadePatternFilter(VectorizedFilter):
    unique_id = "historical_decade_pattern"
    display_name = "Historical Decade Pattern"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Check if at least 3 decades are covered
        decades = (combinations - 1) // 10
        unique_decades = [np.unique(decades[i]) for i in range(min(100, combinations.shape[0]))] # Sampled or full?
        # Vectorized unique count per row
        sorted_decades = np.sort(decades, axis=1)
        diffs = np.diff(sorted_decades, axis=1) > 0
        unique_counts = 1 + np.sum(diffs, axis=1)
        return unique_counts >= 3

class HistoricalUnitPatternFilter(VectorizedFilter):
    unique_id = "historical_unit_pattern"
    display_name = "Historical Unit Pattern"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        units = combinations % 10
        sorted_units = np.sort(units, axis=1)
        unique_counts = 1 + np.sum(np.diff(sorted_units, axis=1) > 0, axis=1)
        return unique_counts >= 4

class HistoricalConsecutivePatternFilter(VectorizedFilter):
    unique_id = "historical_consecutive_pattern"
    display_name = "Historical Consecutive Pattern"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        max_consecutive = np.max(np.concatenate([np.zeros((diffs.shape[0], 1)), (diffs == 1)], axis=1), axis=1) # Simplified
        # Real version would need a bit more logic for length of streaks
        return np.sum(diffs == 1, axis=1) <= 2

class CommonPairFilter(VectorizedFilter):
    unique_id = "historical_common_pair"
    display_name = "Common Pair"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # At least one common pair (placeholder)
        return np.ones(combinations.shape[0], dtype=bool)

class CommonTripletFilter(VectorizedFilter):
    unique_id = "historical_common_triplet"
    display_name = "Common Triplet"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class HistoricalACRangeFilter(VectorizedFilter):
    unique_id = "historical_ac_range"
    display_name = "Historical AC Range"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Placeholder for AC logic similar to Tier 1 but with different bounds
        return np.ones(combinations.shape[0], dtype=bool)

class HistoricalMedianRangeFilter(VectorizedFilter):
    unique_id = "historical_median_range"
    display_name = "Historical Median Range"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        medians = np.median(combinations, axis=1)
        return (medians >= 20) & (medians <= 40)

class HistoricalStdDevRangeFilter(VectorizedFilter):
    unique_id = "historical_std_dev_range"
    display_name = "Historical StdDev Range"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        std = np.std(combinations, axis=1)
        return (std >= 10) & (std <= 20)

class HistoricalSpreadRangeFilter(VectorizedFilter):
    unique_id = "historical_spread_range"
    display_name = "Historical Spread Range"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        spread = np.max(combinations, axis=1) - np.min(combinations, axis=1)
        return (spread >= 30) & (spread <= 55)

class HistoricalDigitSumPatternFilter(VectorizedFilter):
    unique_id = "historical_digit_sum_pattern"
    display_name = "Historical Digit Sum Pattern"
    tier = 4
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        digit_sums = np.sum((combinations // 10) + (combinations % 10), axis=1)
        return (digit_sums >= 25) & (digit_sums <= 55)
