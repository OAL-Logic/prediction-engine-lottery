from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING
from engine.modules.filters import VectorizedFilter

if TYPE_CHECKING:
    from engine.adapters import DrawRules

class SuccessiveGroupsFilter(VectorizedFilter):
    unique_id = "positional_successive_groups"
    display_name = "Successive Groups Count"
    tier = 2
    description = "Counts the number of contiguous groups."

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        is_succ = (diffs == 1)
        starts = np.zeros_like(is_succ, dtype=bool)
        starts[:, 0] = is_succ[:, 0]
        starts[:, 1:] = is_succ[:, 1:] & ~is_succ[:, :-1]
        return np.sum(starts, axis=1) <= 2

class FirstLastDistanceFilter(VectorizedFilter):
    unique_id = "positional_first_last_distance"
    display_name = "First-Last Distance (Span)"
    tier = 2

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        span = np.max(combinations, axis=1) - np.min(combinations, axis=1)
        min_span = 25 if combinations.shape[1] == 6 else 15
        return span >= min_span

class MinDistanceFilter(VectorizedFilter):
    unique_id = "positional_min_distance"
    display_name = "Minimum Distance"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        min_dist = np.min(diffs, axis=1)
        return min_dist >= 1

class MaxDistanceFilter(VectorizedFilter):
    unique_id = "positional_max_distance"
    display_name = "Maximum Distance"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        max_dist = np.max(diffs, axis=1)
        return max_dist <= 25

class Ball1RangeFilter(VectorizedFilter):
    unique_id = "positional_ball_1_range"
    display_name = "Ball 1 Range"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ball1 = np.sort(combinations, axis=1)[:, 0]
        return (ball1 >= 1) & (ball1 <= 15)

class Ball2RangeFilter(VectorizedFilter):
    unique_id = "positional_ball_2_range"
    display_name = "Ball 2 Range"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ball2 = np.sort(combinations, axis=1)[:, 1]
        return (ball2 >= 2) & (ball2 <= 25)

class Ball3RangeFilter(VectorizedFilter):
    unique_id = "positional_ball_3_range"
    display_name = "Ball 3 Range"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ball3 = np.sort(combinations, axis=1)[:, 2]
        return (ball3 >= 5) & (ball3 <= 40)

class Ball4RangeFilter(VectorizedFilter):
    unique_id = "positional_ball_4_range"
    display_name = "Ball 4 Range"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 4: return np.ones(combinations.shape[0], dtype=bool)
        ball4 = sorted_combs[:, 3]
        return (ball4 >= 10) & (ball4 <= 50)

class Ball5RangeFilter(VectorizedFilter):
    unique_id = "positional_ball_5_range"
    display_name = "Ball 5 Range"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 5: return np.ones(combinations.shape[0], dtype=bool)
        ball5 = sorted_combs[:, 4]
        return (ball5 >= 20) & (ball5 <= 58)

class Ball6RangeFilter(VectorizedFilter):
    unique_id = "positional_ball_6_range"
    display_name = "Ball 6 Range"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 6: return np.ones(combinations.shape[0], dtype=bool)
        ball6 = sorted_combs[:, 5]
        return (ball6 >= 30) & (ball6 <= 60)

class Gap1_2Filter(VectorizedFilter):
    unique_id = "positional_gap_1_2"
    display_name = "Gap Ball 1-2"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        gap = sorted_combs[:, 1] - sorted_combs[:, 0]
        return (gap >= 1) & (gap <= 15)

class Gap2_3Filter(VectorizedFilter):
    unique_id = "positional_gap_2_3"
    display_name = "Gap Ball 2-3"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        gap = sorted_combs[:, 2] - sorted_combs[:, 1]
        return (gap >= 1) & (gap <= 15)

class Gap3_4Filter(VectorizedFilter):
    unique_id = "positional_gap_3_4"
    display_name = "Gap Ball 3-4"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 4: return np.ones(combinations.shape[0], dtype=bool)
        gap = sorted_combs[:, 3] - sorted_combs[:, 2]
        return (gap >= 1) & (gap <= 15)

class Gap4_5Filter(VectorizedFilter):
    unique_id = "positional_gap_4_5"
    display_name = "Gap Ball 4-5"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 5: return np.ones(combinations.shape[0], dtype=bool)
        gap = sorted_combs[:, 4] - sorted_combs[:, 3]
        return (gap >= 1) & (gap <= 15)

class Gap5_6Filter(VectorizedFilter):
    unique_id = "positional_gap_5_6"
    display_name = "Gap Ball 5-6"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 6: return np.ones(combinations.shape[0], dtype=bool)
        gap = sorted_combs[:, 5] - sorted_combs[:, 4]
        return (gap >= 1) & (gap <= 15)

class VarianceFilter(VectorizedFilter):
    unique_id = "positional_variance"
    display_name = "Ticket Variance"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        var = np.var(combinations, axis=1)
        return (var >= 50) & (var <= 500)

class StandardDeviationFilter(VectorizedFilter):
    unique_id = "positional_std_dev"
    display_name = "Standard Deviation"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        std = np.std(combinations, axis=1)
        return (std >= 7) & (std <= 25)

class MeanAbsoluteDeviationFilter(VectorizedFilter):
    unique_id = "positional_mad"
    display_name = "Mean Absolute Deviation"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mean = np.mean(combinations, axis=1)[:, np.newaxis]
        mad = np.mean(np.abs(combinations - mean), axis=1)
        return (mad >= 5) & (mad <= 20)

class MedianValueFilter(VectorizedFilter):
    unique_id = "positional_median"
    display_name = "Median Value"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        median = np.median(combinations, axis=1)
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        return (median >= mid - 10) & (median <= mid + 10)

class Ball1_2SumFilter(VectorizedFilter):
    unique_id = "positional_ball_1_2_sum"
    display_name = "Ball 1+2 Sum"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        pair_sum = sorted_combs[:, 0] + sorted_combs[:, 1]
        return (pair_sum >= 3) & (pair_sum <= 40)

class Ball5_6SumFilter(VectorizedFilter):
    unique_id = "positional_ball_5_6_sum"
    display_name = "Ball 5+6 Sum"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 6: return np.ones(combinations.shape[0], dtype=bool)
        pair_sum = sorted_combs[:, 4] + sorted_combs[:, 5]
        return (pair_sum >= 60) & (pair_sum <= 119)

class InnerSpreadFilter(VectorizedFilter):
    unique_id = "positional_inner_spread"
    display_name = "Inner Spread (B2 to B5)"
    tier = 2
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 5: return np.ones(combinations.shape[0], dtype=bool)
        spread = sorted_combs[:, 4] - sorted_combs[:, 1]
        return (spread >= 10) & (spread <= 45)
