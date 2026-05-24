from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Optional, List
from engine.modules.filters import VectorizedFilter

if TYPE_CHECKING:
    from engine.adapters import DrawRules

class LockedNumbersFilter(VectorizedFilter):
    unique_id = "custom_locked_numbers"
    display_name = "Locked Numbers"
    tier = 5

    def __init__(self, locked_set: Optional[List[int]] = None):
        self.locked_set = np.array(locked_set) if locked_set else np.array([])

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        if self.locked_set.size == 0: return np.ones(combinations.shape[0], dtype=bool)
        return np.sum(np.isin(combinations, self.locked_set), axis=1) == self.locked_set.size

class ExcludeSetFilter(VectorizedFilter):
    unique_id = "custom_exclude_set"
    display_name = "Exclude Set"
    tier = 5
    def __init__(self, exclude_set: Optional[List[int]] = None):
        self.exclude_set = np.array(exclude_set) if exclude_set else np.array([])
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        if self.exclude_set.size == 0: return np.ones(combinations.shape[0], dtype=bool)
        return np.sum(np.isin(combinations, self.exclude_set), axis=1) == 0

class IncludeAtLeastOneFilter(VectorizedFilter):
    unique_id = "custom_include_at_least_one"
    display_name = "Include At Least One"
    tier = 5
    def __init__(self, include_set: Optional[List[int]] = None):
        self.include_set = np.array(include_set) if include_set else np.array([])
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        if self.include_set.size == 0: return np.ones(combinations.shape[0], dtype=bool)
        return np.sum(np.isin(combinations, self.include_set), axis=1) >= 1

class RangeExclusionFilter(VectorizedFilter):
    unique_id = "custom_range_exclusion"
    display_name = "Range Exclusion"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Exclude numbers in 13-17 range for example
        counts = np.sum((combinations >= 13) & (combinations <= 17), axis=1)
        return counts == 0

class PatternABFilter(VectorizedFilter):
    unique_id = "custom_pattern_ab"
    display_name = "Pattern A-B"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class SpecificSumFilter(VectorizedFilter):
    unique_id = "custom_specific_sum"
    display_name = "Specific Sum"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sums = np.sum(combinations, axis=1)
        return sums != 150 # Example: exclude exact middle sum

class SpecificUnitSumFilter(VectorizedFilter):
    unique_id = "custom_specific_unit_sum"
    display_name = "Specific Unit Sum"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        unit_sums = np.sum(combinations % 10, axis=1)
        return unit_sums >= 15

class ForbiddenPairsFilter(VectorizedFilter):
    unique_id = "custom_forbidden_pairs"
    display_name = "Forbidden Pairs"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        # Example: 1 and 2 together
        has_1 = np.any(combinations == 1, axis=1)
        has_2 = np.any(combinations == 2, axis=1)
        return ~(has_1 & has_2)

class RequiredPairsFilter(VectorizedFilter):
    unique_id = "custom_required_pairs"
    display_name = "Required Pairs"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class MagicSquareSumFilter(VectorizedFilter):
    unique_id = "custom_magic_square"
    display_name = "Magic Square Sum"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class GoldenRatioFilter(VectorizedFilter):
    unique_id = "custom_golden_ratio"
    display_name = "Golden Ratio Distribution"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class ExtremeValueFilter(VectorizedFilter):
    unique_id = "custom_extreme_value"
    display_name = "Extreme Value Check"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class InnerCoreFilter(VectorizedFilter):
    unique_id = "custom_inner_core"
    display_name = "Inner Core (20-40)"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations >= 20) & (combinations <= 40), axis=1)
        return counts >= 2

class OuterShellFilter(VectorizedFilter):
    unique_id = "custom_outer_shell"
    display_name = "Outer Shell (1-10, 50-60)"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        counts = np.sum((combinations <= 10) | (combinations >= 50), axis=1)
        return counts >= 1

class CustomRange1Filter(VectorizedFilter):
    unique_id = "custom_range_1"
    display_name = "Custom Range 1"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class CustomRange2Filter(VectorizedFilter):
    unique_id = "custom_range_2"
    display_name = "Custom Range 2"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class CustomRange3Filter(VectorizedFilter):
    unique_id = "custom_range_3"
    display_name = "Custom Range 3"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class CustomRange4Filter(VectorizedFilter):
    unique_id = "custom_range_4"
    display_name = "Custom Range 4"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class CustomRange5Filter(VectorizedFilter):
    unique_id = "custom_range_5"
    display_name = "Custom Range 5"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)

class CustomRange6Filter(VectorizedFilter):
    unique_id = "custom_range_6"
    display_name = "Custom Range 6"
    tier = 5
    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        return np.ones(combinations.shape[0], dtype=bool)
