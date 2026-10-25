from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence
from engine.modules.filters import VectorizedFilter, FilterExplanation, format_gauge

if TYPE_CHECKING:
    from engine.adapters import DrawRules


class SuccessiveGroupsFilter(VectorizedFilter):
    """Counts the number of contiguous successive groups."""
    unique_id = "positional_successive_groups"
    display_name = "Successive Groups Count"
    tier = 2
    category = "Consecutive Runs"
    description = "Counts contiguous consecutive runs (e.g. 14-15 or 32-33-34) and restricts the ticket to at most 2 such runs."
    formula = "∑ [run_start(x_{i+1} - x_i == 1)] ≤ 2"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Sort Ticket -> Compute Adjacent Differences: x[i+1]-x[i]|\n"
        "| Identify Consecutive Runs (diff == 1)                 |\n"
        "| Condition: Number of distinct runs <= 2               |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Diffs = x[i+1] - x[i]]\n"
        "    B --> C[Count Runs with Diff == 1]\n"
        "    C --> D{Runs <= 2?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        is_succ = (diffs == 1)
        starts = np.zeros_like(is_succ, dtype=bool)
        starts[:, 0] = is_succ[:, 0]
        starts[:, 1:] = is_succ[:, 1:] & ~is_succ[:, :-1]
        return np.sum(starts, axis=1) <= 2

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        diffs = np.diff(comb_arr)
        is_succ = (diffs == 1)
        runs = 0
        if len(is_succ) > 0:
            runs = int(is_succ[0])
            for i in range(1, len(is_succ)):
                if is_succ[i] and not is_succ[i - 1]:
                    runs += 1
        passed = runs <= 2
        gauge = format_gauge(runs, 0, 2, passed)
        summary = f"Successive consecutive runs count is {runs} (max: 2) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=runs,
            allowed_range="≤ 2 runs",
            summary=summary,
            details={"successive_runs": runs, "adjacent_diffs": list(map(int, diffs))},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class FirstLastDistanceFilter(VectorizedFilter):
    """First-Last Distance (Total Ticket Span)."""
    unique_id = "positional_first_last_distance"
    display_name = "First-Last Distance (Span)"
    tier = 2
    category = "Span & Spread"
    description = "Checks that the span between the lowest and highest number on the ticket is sufficiently wide (span >= 25 for 6-ball, >= 15 for 5-ball)."
    formula = "span = max(X) - min(X) ≥ min_span (25 for k=6, 15 for k=5)"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Span = max(numbers) - min(numbers)                    |\n"
        "| Threshold: >= 25 (6-ball games) or >= 15 (5-ball)     |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Span = Last - First]\n"
        "    B --> C{Span >= min_span?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        span = np.max(combinations, axis=1) - np.min(combinations, axis=1)
        min_span = 25 if combinations.shape[1] == 6 else 15
        return span >= min_span

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        span = int(np.max(comb_arr) - np.min(comb_arr))
        min_span = 25 if len(comb_arr) == 6 else 15
        passed = span >= min_span
        gauge = format_gauge(span, min_span, min_span + 25, passed)
        summary = f"Total span (last - first) is {span} (min required: {min_span}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=span,
            allowed_range=f"≥ {min_span}",
            summary=summary,
            details={"span": span, "first": int(np.min(comb_arr)), "last": int(np.max(comb_arr))},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MinDistanceFilter(VectorizedFilter):
    """Minimum gap between any adjacent numbers."""
    unique_id = "positional_min_distance"
    display_name = "Minimum Distance"
    tier = 2
    category = "Span & Spread"
    description = "Ensures no duplicate numbers exist by requiring minimum distance min(x[i+1] - x[i]) >= 1."
    formula = "min_{i} (x_{i+1} - x_i) ≥ 1"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Min Distance = min(x[i+1] - x[i])                      |\n"
        "| Condition    : min_distance >= 1 (strictly distinct)  |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Min Gap = min(x[i+1] - x[i])]\n"
        "    B --> C{Min Gap >= 1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        min_dist = np.min(diffs, axis=1)
        return min_dist >= 1

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        diffs = np.diff(comb_arr)
        min_dist = int(np.min(diffs)) if len(diffs) > 0 else 1
        passed = min_dist >= 1
        gauge = format_gauge(min_dist, 1, 5, passed)
        summary = f"Minimum adjacent distance is {min_dist} (required: >= 1) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=min_dist,
            allowed_range="≥ 1",
            summary=summary,
            details={"min_distance": min_dist},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MaxDistanceFilter(VectorizedFilter):
    """Maximum gap between any adjacent numbers."""
    unique_id = "positional_max_distance"
    display_name = "Maximum Distance"
    tier = 2
    category = "Span & Spread"
    description = "Guards against excessive gaps between adjacent sorted numbers (max distance <= 25), preventing massive voids."
    formula = "max_{i} (x_{i+1} - x_i) ≤ 25"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Max Distance = max(x[i+1] - x[i])                      |\n"
        "| Condition    : max_distance <= 25                     |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Max Gap = max(x[i+1] - x[i])]\n"
        "    B --> C{Max Gap <= 25?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        max_dist = np.max(diffs, axis=1)
        return max_dist <= 25

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        diffs = np.diff(comb_arr)
        max_dist = int(np.max(diffs)) if len(diffs) > 0 else 0
        passed = max_dist <= 25
        gauge = format_gauge(max_dist, 1, 25, passed)
        summary = f"Maximum adjacent distance is {max_dist} (max allowed: 25) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=max_dist,
            allowed_range="≤ 25",
            summary=summary,
            details={"max_distance": max_dist},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


def _make_ball_range_filter(ball_idx: int, min_v: int, max_v: int):
    class BallRangeFilter(VectorizedFilter):
        unique_id = f"positional_ball_{ball_idx}_range"
        display_name = f"Ball {ball_idx} Range"
        tier = 2
        category = "Positional Bounds"
        description = f"Constrains sorted ball #{ball_idx} to its typical empirical range [{min_v}..{max_v}]."
        formula = f"{min_v} ≤ x_{{{ball_idx}}} ≤ {max_v}"
        diagram = (
            f"+-------------------------------------------------------+\n"
            f"| Sorted Ball #{ball_idx}: x[{ball_idx - 1}]                                  |\n"
            f"| Expected Range: [{min_v} .. {max_v}]                          |\n"
            f"+-------------------------------------------------------+"
        )
        mermaid = (
            "graph LR\n"
            f"    A[Sorted Ball #{ball_idx}] --> B{{{min_v} <= x <= {max_v}?}}\n"
            "    B -->|Yes| P[Pass]\n"
            "    B -->|No| F[Reject]"
        )

        def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
            sorted_combs = np.sort(combinations, axis=1)
            if sorted_combs.shape[1] < ball_idx:
                return np.ones(combinations.shape[0], dtype=bool)
            ball = sorted_combs[:, ball_idx - 1]
            return (ball >= min_v) & (ball <= max_v)

        def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
            sorted_arr = np.sort(np.asarray(combination, dtype=int).ravel())
            if len(sorted_arr) < ball_idx:
                return FilterExplanation(
                    filter_id=self.unique_id,
                    filter_name=self.display_name,
                    tier=self.tier,
                    category=self.category,
                    passed=True,
                    actual_value="N/A",
                    allowed_range=f"[{min_v}..{max_v}]",
                    summary=f"Combination has fewer than {ball_idx} balls -> PASS.",
                )
            val = int(sorted_arr[ball_idx - 1])
            passed = min_v <= val <= max_v
            gauge = format_gauge(val, min_v, max_v, passed)
            summary = f"Sorted ball #{ball_idx} value is {val} (allowed: {min_v}..{max_v}) -> {'PASS' if passed else 'FAIL'}."
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=passed,
                actual_value=val,
                allowed_range=f"[{min_v}..{max_v}]",
                summary=summary,
                details={"ball_index": ball_idx, "value": val},
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge=gauge,
            )

    BallRangeFilter.__name__ = f"Ball{ball_idx}RangeFilter"
    return BallRangeFilter


Ball1RangeFilter = _make_ball_range_filter(1, 1, 15)
Ball2RangeFilter = _make_ball_range_filter(2, 2, 25)
Ball3RangeFilter = _make_ball_range_filter(3, 5, 40)
Ball4RangeFilter = _make_ball_range_filter(4, 10, 50)
Ball5RangeFilter = _make_ball_range_filter(5, 20, 58)
Ball6RangeFilter = _make_ball_range_filter(6, 30, 60)


def _make_gap_filter(b1: int, b2: int):
    class GapFilter(VectorizedFilter):
        unique_id = f"positional_gap_{b1}_{b2}"
        display_name = f"Gap Ball {b1}-{b2}"
        tier = 2
        category = "Adjacent Gaps"
        description = f"Constrains the difference between sorted ball #{b1} and sorted ball #{b2} to [1..15]."
        formula = f"1 ≤ x_{{{b2}}} - x_{{{b1}}} ≤ 15"
        diagram = (
            f"+-------------------------------------------------------+\n"
            f"| Gap(#{b1}, #{b2}) = x[{b2-1}] - x[{b1-1}]                     |\n"
            f"| Allowed Range: [1 .. 15]                              |\n"
            f"+-------------------------------------------------------+"
        )
        mermaid = (
            "graph LR\n"
            f"    A[Sorted Ticket] --> B[Gap = x[{b2}] - x[{b1}]]\n"
            "    B --> C{1 <= Gap <= 15?}\n"
            "    C -->|Yes| P[Pass]\n"
            "    C -->|No| F[Reject]"
        )

        def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
            sorted_combs = np.sort(combinations, axis=1)
            if sorted_combs.shape[1] < b2:
                return np.ones(combinations.shape[0], dtype=bool)
            gap = sorted_combs[:, b2 - 1] - sorted_combs[:, b1 - 1]
            return (gap >= 1) & (gap <= 15)

        def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
            sorted_arr = np.sort(np.asarray(combination, dtype=int).ravel())
            if len(sorted_arr) < b2:
                return FilterExplanation(
                    filter_id=self.unique_id,
                    filter_name=self.display_name,
                    tier=self.tier,
                    category=self.category,
                    passed=True,
                    actual_value="N/A",
                    allowed_range="[1..15]",
                    summary=f"Combination has fewer than {b2} balls -> PASS.",
                )
            gap = int(sorted_arr[b2 - 1] - sorted_arr[b1 - 1])
            passed = 1 <= gap <= 15
            gauge = format_gauge(gap, 1, 15, passed)
            summary = f"Gap between ball #{b1} and ball #{b2} is {gap} (allowed: 1..15) -> {'PASS' if passed else 'FAIL'}."
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=passed,
                actual_value=gap,
                allowed_range="[1..15]",
                summary=summary,
                details={"ball_a": b1, "ball_b": b2, "gap": gap},
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge=gauge,
            )

    GapFilter.__name__ = f"Gap{b1}_{b2}Filter"
    return GapFilter


Gap1_2Filter = _make_gap_filter(1, 2)
Gap2_3Filter = _make_gap_filter(2, 3)
Gap3_4Filter = _make_gap_filter(3, 4)
Gap4_5Filter = _make_gap_filter(4, 5)
Gap5_6Filter = _make_gap_filter(5, 6)


class VarianceFilter(VectorizedFilter):
    """Ticket variance check."""
    unique_id = "positional_variance"
    display_name = "Ticket Variance"
    tier = 2
    category = "Statistical Dispersion"
    description = "Calculates the variance of numbers on the ticket, filtering outside the typical envelope [50..500]."
    formula = "50 ≤ σ²(X) ≤ 500"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Variance = sum((x_i - mean)^2) / k                    |\n"
        "| Allowed Range: [50 .. 500]                            |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Variance Var(X)]\n"
        "    B --> C{50 <= Var <= 500?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        var = np.var(combinations, axis=1)
        return (var >= 50) & (var <= 500)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=float).ravel()
        var_val = float(np.var(comb_arr))
        passed = 50.0 <= var_val <= 500.0
        gauge = format_gauge(round(var_val, 1), 50, 500, passed)
        summary = f"Ticket variance is {var_val:.1f} (allowed: 50..500) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(var_val, 2),
            allowed_range="[50..500]",
            summary=summary,
            details={"variance": var_val},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class StandardDeviationFilter(VectorizedFilter):
    """Standard deviation of numbers on the ticket."""
    unique_id = "positional_std_dev"
    display_name = "Standard Deviation"
    tier = 2
    category = "Statistical Dispersion"
    description = "Evaluates the standard deviation of numbers on the ticket, ensuring it falls within [7.0..25.0]."
    formula = "7.0 ≤ σ(X) ≤ 25.0"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Standard Deviation: std = sqrt(variance)              |\n"
        "| Allowed Range     : [7.0 .. 25.0]                     |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute StdDev sigma(X)]\n"
        "    B --> C{7.0 <= Std <= 25.0?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        std = np.std(combinations, axis=1)
        return (std >= 7) & (std <= 25)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=float).ravel()
        std_val = float(np.std(comb_arr))
        passed = 7.0 <= std_val <= 25.0
        gauge = format_gauge(round(std_val, 2), 7.0, 25.0, passed)
        summary = f"Standard deviation is {std_val:.2f} (allowed: 7.0..25.0) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(std_val, 2),
            allowed_range="[7.0..25.0]",
            summary=summary,
            details={"std_dev": std_val},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MeanAbsoluteDeviationFilter(VectorizedFilter):
    """Mean absolute deviation (MAD) from the mean."""
    unique_id = "positional_mad"
    display_name = "Mean Absolute Deviation"
    tier = 2
    category = "Statistical Dispersion"
    description = "Computes the Mean Absolute Deviation (MAD) of the ticket, constrained within [5.0..20.0]."
    formula = "5.0 ≤ (1/k) ∑ |x_i - μ| ≤ 20.0"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| MAD = sum(|x_i - mean|) / k                           |\n"
        "| Allowed Range: [5.0 .. 20.0]                          |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute MAD = mean(|x - mu|)]\n"
        "    B --> C{5.0 <= MAD <= 20.0?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mean = np.mean(combinations, axis=1)[:, np.newaxis]
        mad = np.mean(np.abs(combinations - mean), axis=1)
        return (mad >= 5) & (mad <= 20)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=float).ravel()
        mean_val = np.mean(comb_arr)
        mad_val = float(np.mean(np.abs(comb_arr - mean_val)))
        passed = 5.0 <= mad_val <= 20.0
        gauge = format_gauge(round(mad_val, 2), 5.0, 20.0, passed)
        summary = f"Mean Absolute Deviation is {mad_val:.2f} (allowed: 5.0..20.0) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(mad_val, 2),
            allowed_range="[5.0..20.0]",
            summary=summary,
            details={"mad": mad_val, "mean": float(mean_val)},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MedianValueFilter(VectorizedFilter):
    """Median value constraint."""
    unique_id = "positional_median"
    display_name = "Median Value"
    tier = 2
    category = "Central Tendency"
    description = "Checks that the median of the ticket is within ±10 of the lottery pool's center."
    formula = "|median(X) - mid_pool| ≤ 10"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Midpoint: (lo + hi) // 2                              |\n"
        "| Allowed Range: [mid - 10 .. mid + 10]                 |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Median]\n"
        "    B --> C{|Median - Mid| <= 10?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        median = np.median(combinations, axis=1)
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        return (median >= mid - 10) & (median <= mid + 10)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        lo, hi = (1, 60) if rules is None else rules.number_range
        mid = (lo + hi) // 2
        med_val = float(np.median(comb_arr))
        passed = (mid - 10) <= med_val <= (mid + 10)
        gauge = format_gauge(round(med_val, 1), mid - 10, mid + 10, passed)
        summary = f"Ticket median is {med_val:.1f} (allowed: {mid - 10}..{mid + 10}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=med_val,
            allowed_range=f"[{mid - 10}..{mid + 10}]",
            summary=summary,
            details={"median": med_val, "midpoint": mid},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class Ball1_2SumFilter(VectorizedFilter):
    """Sum of the first two sorted balls."""
    unique_id = "positional_ball_1_2_sum"
    display_name = "Ball 1+2 Sum"
    tier = 2
    category = "Positional Sums"
    description = "Checks that the sum of the first two sorted numbers falls within [3..40]."
    formula = "3 ≤ x_1 + x_2 ≤ 40"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Head Sum = sorted_ball[0] + sorted_ball[1]            |\n"
        "| Allowed Range: [3 .. 40]                              |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Head Sum = x[0] + x[1]]\n"
        "    B --> C{3 <= Head Sum <= 40?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        pair_sum = sorted_combs[:, 0] + sorted_combs[:, 1]
        return (pair_sum >= 3) & (pair_sum <= 40)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        if len(comb_arr) < 2:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value=0,
                allowed_range="[3..40]",
                summary="Insufficient balls -> PASS.",
            )
        s = int(comb_arr[0] + comb_arr[1])
        passed = 3 <= s <= 40
        gauge = format_gauge(s, 3, 40, passed)
        summary = f"Sum of ball 1 & 2 is {s} ({comb_arr[0]} + {comb_arr[1]}, allowed: 3..40) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=s,
            allowed_range="[3..40]",
            summary=summary,
            details={"ball1": int(comb_arr[0]), "ball2": int(comb_arr[1]), "sum": s},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class Ball5_6SumFilter(VectorizedFilter):
    """Sum of sorted balls 5 and 6."""
    unique_id = "positional_ball_5_6_sum"
    display_name = "Ball 5+6 Sum"
    tier = 2
    category = "Positional Sums"
    description = "Checks that the sum of sorted balls 5 and 6 falls within [60..119] for 6-ball games."
    formula = "60 ≤ x_5 + x_6 ≤ 119"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Tail Sum = sorted_ball[4] + sorted_ball[5]            |\n"
        "| Allowed Range: [60 .. 119]                            |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Tail Sum = x[4] + x[5]]\n"
        "    B --> C{60 <= Tail Sum <= 119?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 6: return np.ones(combinations.shape[0], dtype=bool)
        pair_sum = sorted_combs[:, 4] + sorted_combs[:, 5]
        return (pair_sum >= 60) & (pair_sum <= 119)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        if len(comb_arr) < 6:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="N/A",
                allowed_range="[60..119]",
                summary="Pick count < 6 -> PASS.",
            )
        s = int(comb_arr[4] + comb_arr[5])
        passed = 60 <= s <= 119
        gauge = format_gauge(s, 60, 119, passed)
        summary = f"Sum of ball 5 & 6 is {s} ({comb_arr[4]} + {comb_arr[5]}, allowed: 60..119) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=s,
            allowed_range="[60..119]",
            summary=summary,
            details={"ball5": int(comb_arr[4]), "ball6": int(comb_arr[5]), "sum": s},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class InnerSpreadFilter(VectorizedFilter):
    """Inner spread between ball 2 and ball 5."""
    unique_id = "positional_inner_spread"
    display_name = "Inner Spread (B2 to B5)"
    tier = 2
    category = "Span & Spread"
    description = "Checks that the spread between sorted ball 2 and sorted ball 5 is within [10..45]."
    formula = "10 ≤ x_5 - x_2 ≤ 45"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Inner Spread = sorted_ball[4] - sorted_ball[1]        |\n"
        "| Allowed Range: [10 .. 45]                             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Inner Spread = x[4] - x[1]]\n"
        "    B --> C{10 <= Spread <= 45?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sorted_combs = np.sort(combinations, axis=1)
        if sorted_combs.shape[1] < 5: return np.ones(combinations.shape[0], dtype=bool)
        spread = sorted_combs[:, 4] - sorted_combs[:, 1]
        return (spread >= 10) & (spread <= 45)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        if len(comb_arr) < 5:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="N/A",
                allowed_range="[10..45]",
                summary="Pick count < 5 -> PASS.",
            )
        spread = int(comb_arr[4] - comb_arr[1])
        passed = 10 <= spread <= 45
        gauge = format_gauge(spread, 10, 45, passed)
        summary = f"Inner spread (B5 - B2) is {spread} ({comb_arr[4]} - {comb_arr[1]}, allowed: 10..45) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=spread,
            allowed_range="[10..45]",
            summary=summary,
            details={"ball2": int(comb_arr[1]), "ball5": int(comb_arr[4]), "spread": spread},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class QuadrantBalanceFilter(VectorizedFilter):
    """Measures spatial spread across the 4 Cartesian quadrants of the betting slip."""
    unique_id = "positional_quadrant_balance"
    display_name = "Quadrant Balance"
    tier = 2
    category = "Slip Geometry"
    description = "Ensures numbers span across at least 3 physical Cartesian quadrants of the lottery slip."
    formula = "|{Quadrant(x_i)}| ≥ min_quadrants"
    diagram = (
        "+-----------------------------+-----------------------------+\n"
        "|  QUADRANT I (Top-Left)      |  QUADRANT II (Top-Right)    |\n"
        "|  [01] [02] [03] [04] [05]   |  [06] [07] [08] [09] [10]   |\n"
        "|  [11] [12] [13] [14] [15]   |  [16] [17] [18] [19] [20]   |\n"
        "+-----------------------------+-----------------------------+\n"
        "|  QUADRANT III (Bottom-Left) |  QUADRANT IV (Bottom-Right) |\n"
        "|  [31] [32] [33] [34] [35]   |  [36] [37] [38] [39] [40]   |\n"
        "|  [41] [42] [43] [44] [45]   |  [46] [47] [48] [49] [50]   |\n"
        "+-----------------------------+-----------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Map to 4 Cartesian Quadrants]\n"
        "    B --> C{Distinct Quadrants >= min_quadrants?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject (Corner Clustered)]"
    )

    @staticmethod
    def _compute_quadrants(combinations: np.ndarray, rules: Optional[DrawRules]) -> np.ndarray:
        board_cols = getattr(rules, 'board_cols', 10) if rules is not None else 10
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = hi - lo + 1
        n_rows = max(1, (n_pool + board_cols - 1) // board_cols)
        mid_row = max(1, n_rows // 2)
        mid_col = max(1, board_cols // 2)

        zero_based = np.maximum(0, combinations - lo)
        row_idx = zero_based // board_cols
        col_idx = zero_based % board_cols

        q1 = (row_idx < mid_row) & (col_idx < mid_col)
        q2 = (row_idx < mid_row) & (col_idx >= mid_col)
        q3 = (row_idx >= mid_row) & (col_idx < mid_col)
        q4 = (row_idx >= mid_row) & (col_idx >= mid_col)

        # 4-bit mask for quadrants touched
        q_mask = (q1.any(axis=1).astype(int)) | ((q2.any(axis=1).astype(int)) << 1) | ((q3.any(axis=1).astype(int)) << 2) | ((q4.any(axis=1).astype(int)) << 3)
        # Count bits set
        from engine.modules.filters import BIT_COUNT_TABLE
        return BIT_COUNT_TABLE[q_mask]

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_quads = 3 if k >= 4 else min(k, 2)
        quad_counts = self._compute_quadrants(combinations, rules)
        return quad_counts >= min_quads

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_quads = 3 if k >= 4 else min(k, 2)
        arr_2d = np.asarray([comb_arr], dtype=int)
        cnt = int(self._compute_quadrants(arr_2d, rules)[0])
        passed = cnt >= min_quads
        gauge = format_gauge(cnt, min_quads, 4, passed)
        summary = f"Distinct Cartesian quadrants touched is {cnt}/4 (required: >= {min_quads}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"≥ {min_quads} quadrants",
            summary=summary,
            details={"quadrants_touched": cnt, "min_required": min_quads},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MatrixSpatialFilter(VectorizedFilter):
    """Verifies grid balance across rows and columns of the game board."""
    unique_id = "positional_matrix_spatial"
    display_name = "Matrix Spatial Spread"
    tier = 2
    category = "Matrix Spread"
    description = "Restricts maximum numbers in any single row or column of the betting card."
    formula = "max(RowCount) ≤ max_row ∧ max(ColCount) ≤ max_col"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Matrix Board Grid : Mapping numbers to (row, col)     |\n"
        "| Condition         : Max balls in any row/col <= max   |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Project to Grid (Row, Col)]\n"
        "    B --> C{Max Row <= Allowed and Max Col <= Allowed?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject (Linear Grid Overload)]"
    )

    @staticmethod
    def _compute_max_allowed(k: int) -> int:
        return max(3, int(np.ceil(0.42 * k)))

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        board_cols = getattr(rules, 'board_cols', 10) if rules is not None else 10
        lo = rules.number_range[0] if rules is not None else 1
        k = combinations.shape[1]
        max_allowed = self._compute_max_allowed(k)

        zero_based = np.maximum(0, combinations - lo)
        row_indices = zero_based // board_cols
        col_indices = zero_based % board_cols

        # Vectorized check across rows and columns
        M = combinations.shape[0]
        exceeds = np.zeros(M, dtype=bool)

        # Check maximum row frequency
        sorted_rows = np.sort(row_indices, axis=1)
        for i in range(k - max_allowed):
            exceeds |= (sorted_rows[:, i + max_allowed] == sorted_rows[:, i])

        # Check maximum col frequency
        sorted_cols = np.sort(col_indices, axis=1)
        for i in range(k - max_allowed):
            exceeds |= (sorted_cols[:, i + max_allowed] == sorted_cols[:, i])

        return ~exceeds

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        max_allowed = self._compute_max_allowed(k)
        board_cols = getattr(rules, 'board_cols', 10) if rules is not None else 10
        lo = rules.number_range[0] if rules is not None else 1

        from collections import Counter
        row_counts = Counter((x - lo) // board_cols for x in comb_arr)
        col_counts = Counter((x - lo) % board_cols for x in comb_arr)
        max_row = max(row_counts.values()) if row_counts else 0
        max_col = max(col_counts.values()) if col_counts else 0
        passed = (max_row <= max_allowed) and (max_col <= max_allowed)
        summary = f"Max in single row: {max_row}, max in single col: {max_col} (allowed: <= {max_allowed}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=f"R:{max_row}/C:{max_col}",
            allowed_range=f"≤ {max_allowed}",
            summary=summary,
            details={"max_row": max_row, "max_col": max_col, "max_allowed": max_allowed},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge="[✓ PASS]" if passed else "[✗ FAIL]",
        )
