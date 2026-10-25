from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence
from engine.modules.filters import VectorizedFilter, FilterExplanation, format_gauge

if TYPE_CHECKING:
    from engine.adapters import DrawRules


class HotColdFilter(VectorizedFilter):
    """Hot-Cold number distribution check."""
    unique_id = "historical_hot_cold"
    display_name = "Hot-Cold Distribution"
    tier = 4
    category = "Frequency Partitioning"
    description = "Checks that the ticket contains between 2 and 5 hot numbers from recent frequency analysis."
    formula = "2 ≤ ∑ [x_i ∈ HotNumbers] ≤ 5"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Hot Numbers Set: Top 25-33% most frequent numbers     |\n"
        "| Allowed Range  : [2 .. 5] hot numbers per ticket      |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Hot: sum(x in HotNumbers)]\n"
        "    B --> C{2 <= Hot Count <= 5?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        hot_nums = getattr(rules, 'hot_numbers', [])
        if not hot_nums: return np.ones(combinations.shape[0], dtype=bool)
        hot_counts = np.sum(np.isin(combinations, hot_nums), axis=1)
        return (hot_counts >= 2) & (hot_counts <= 5)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        hot_nums = getattr(rules, 'hot_numbers', []) if rules is not None else []
        if not hot_nums:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="No context",
                allowed_range="[2..5]",
                summary="No historical hot numbers context supplied -> PASS.",
            )
        found = [int(x) for x in comb_arr if x in hot_nums]
        cnt = len(found)
        passed = 2 <= cnt <= 5
        gauge = format_gauge(cnt, 2, 5, passed)
        summary = f"Hot numbers count is {cnt} {found} (allowed: 2..5) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="[2..5]",
            summary=summary,
            details={"hot_numbers": found, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalRepeatFilter(VectorizedFilter):
    """Historical repeat from immediately preceding draw."""
    unique_id = "historical_repeat"
    display_name = "Historical Repeat"
    tier = 4
    category = "Temporal Memory"
    description = "Checks that the ticket repeats between 0 and 2 numbers from the most recent draw (draw t-1)."
    formula = "0 ≤ ∑ [x_i ∈ Draw_{t-1}] ≤ 2"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Last Draw Set: Numbers drawn in previous contest      |\n"
        "| Allowed Range: [0 .. 2] repeats                       |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Last Draw Matches]\n"
        "    B --> C{0 <= Matches <= 2?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        last_draw = getattr(rules, 'last_draw', [])
        if not last_draw: return np.ones(combinations.shape[0], dtype=bool)
        repeats = np.sum(np.isin(combinations, last_draw), axis=1)
        return (repeats >= 0) & (repeats <= 2)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        last_draw = getattr(rules, 'last_draw', []) if rules is not None else []
        if not last_draw:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="No context",
                allowed_range="[0..2]",
                summary="No last draw context provided -> PASS.",
            )
        repeats = [int(x) for x in comb_arr if x in last_draw]
        cnt = len(repeats)
        passed = 0 <= cnt <= 2
        gauge = format_gauge(cnt, 0, 2, passed)
        summary = f"Repeats from last draw is {cnt} {repeats} (allowed: 0..2) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="[0..2]",
            summary=summary,
            details={"repeats": repeats, "count": cnt, "last_draw": list(last_draw)},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class ColdNumbersFilter(VectorizedFilter):
    """Cold numbers count check."""
    unique_id = "historical_cold_numbers"
    display_name = "Cold Numbers Count"
    tier = 4
    category = "Frequency Partitioning"
    description = "Restricts the count of cold (infrequently drawn) numbers to at most 2 per ticket."
    formula = "0 ≤ ∑ [x_i ∈ ColdNumbers] ≤ 2"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Cold Numbers Set: Infrequently drawn / bottom tier    |\n"
        "| Allowed Range   : [0 .. 2]                            |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Cold: sum(x in ColdNumbers)]\n"
        "    B --> C{Count <= 2?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        cold_nums = getattr(rules, 'cold_numbers', [])
        if not cold_nums: return np.ones(combinations.shape[0], dtype=bool)
        counts = np.sum(np.isin(combinations, cold_nums), axis=1)
        return (counts >= 0) & (counts <= 2)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        cold_nums = getattr(rules, 'cold_numbers', []) if rules is not None else []
        if not cold_nums:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="No context",
                allowed_range="[0..2]",
                summary="No cold numbers context supplied -> PASS.",
            )
        colds = [int(x) for x in comb_arr if x in cold_nums]
        cnt = len(colds)
        passed = 0 <= cnt <= 2
        gauge = format_gauge(cnt, 0, 2, passed)
        summary = f"Cold numbers count is {cnt} {colds} (allowed: 0..2) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="[0..2]",
            summary=summary,
            details={"cold_numbers": colds, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class OverdueNumbersFilter(VectorizedFilter):
    """Overdue numbers count check."""
    unique_id = "historical_overdue"
    display_name = "Overdue Numbers"
    tier = 4
    category = "Temporal Skips"
    description = "Requires that the ticket includes at least 1 overdue number whose current skip exceeds expected interval."
    formula = "∑ [x_i ∈ OverdueNumbers] ≥ 1"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Overdue Set: Numbers with skip > expected return span |\n"
        "| Condition  : Count >= 1 (must include overdue ball)   |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Overdue Numbers]\n"
        "    B --> C{Count >= 1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        overdue = getattr(rules, 'overdue_numbers', [])
        if not overdue: return np.ones(combinations.shape[0], dtype=bool)
        counts = np.sum(np.isin(combinations, overdue), axis=1)
        return (counts >= 1)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        overdue = getattr(rules, 'overdue_numbers', []) if rules is not None else []
        if not overdue:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="No context",
                allowed_range="≥ 1",
                summary="No overdue numbers context supplied -> PASS.",
            )
        found = [int(x) for x in comb_arr if x in overdue]
        cnt = len(found)
        passed = cnt >= 1
        gauge = format_gauge(cnt, 1, max(cnt, 3), passed)
        summary = f"Overdue numbers count is {cnt} {found} (required: >= 1) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="≥ 1",
            summary=summary,
            details={"overdue_numbers": found, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalSumRangeFilter(VectorizedFilter):
    """Historical sum range with hypergeometric theoretical fallback."""
    unique_id = "historical_sum_range"
    display_name = "Historical Sum Range"
    tier = 4
    category = "Empirical Distribution"
    description = "Constrains ticket sum to historical ±2.8σ bounds, with baseline fallback."
    formula = "μ_{hist} - 2.8σ_{hist} ≤ ∑ x_i ≤ μ_{hist} + 2.8σ_{hist}"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Sum Distribution: Gaussian bell curve around mean    |\n"
        "| Allowed Range   : [mean - 2.8*std .. mean + 2.8*std]  |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Ticket Sum]\n"
        "    B --> C{min_sum <= Sum <= max_sum?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        sums = np.sum(combinations, axis=1)
        k = combinations.shape[1]
        lo, hi = getattr(rules, "number_range", (1, 60))
        n_pool = hi - lo + 1

        hist_mean = getattr(rules, "purged_sum_mean", None)
        hist_std = getattr(rules, "purged_sum_std", None)

        if hist_mean is not None and hist_std is not None and hist_std > 0:
            min_sum = float(hist_mean - 2.8 * hist_std)
            max_sum = float(hist_mean + 2.8 * hist_std)
        elif lo == 1 and hi == 60 and k == 6:
            min_sum, max_sum = 100.0, 250.0
        else:
            expected_sum = k * (lo + hi) / 2.0
            if n_pool > 1:
                var_sum = (k * (n_pool - k) / (n_pool - 1)) * ((n_pool ** 2 - 1) / 12.0)
                std_sum = np.sqrt(max(var_sum, 1.0))
            else:
                std_sum = 10.0
            min_sum = float(expected_sum - 2.8 * std_sum)
            max_sum = float(expected_sum + 2.8 * std_sum)

        return (sums >= min_sum) & (sums <= max_sum)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        actual_sum = int(np.sum(comb_arr))
        k = len(comb_arr)
        lo, hi = (1, 60) if rules is None else rules.number_range
        hist_mean = getattr(rules, "purged_sum_mean", None) if rules else None
        hist_std = getattr(rules, "purged_sum_std", None) if rules else None

        if hist_mean is not None and hist_std is not None and hist_std > 0:
            min_s = int(round(hist_mean - 2.8 * hist_std))
            max_s = int(round(hist_mean + 2.8 * hist_std))
        elif lo == 1 and hi == 60 and k == 6:
            min_s, max_s = 100, 250
        else:
            n_pool = hi - lo + 1
            expected = k * (lo + hi) / 2.0
            var_sum = (k * (n_pool - k) / (n_pool - 1)) * ((n_pool ** 2 - 1) / 12.0) if n_pool > 1 else 100.0
            std_s = float(np.sqrt(max(var_sum, 1.0)))
            min_s = int(round(expected - 2.8 * std_s))
            max_s = int(round(expected + 2.8 * std_s))

        passed = min_s <= actual_sum <= max_s
        gauge = format_gauge(actual_sum, min_s, max_s, passed)
        summary = f"Historical sum is {actual_sum} (target range: {min_s}..{max_s}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=actual_sum,
            allowed_range=f"[{min_s}..{max_s}]",
            summary=summary,
            details={"sum": actual_sum, "min_sum": min_s, "max_sum": max_s},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class RecentDrawsExclusionFilter(VectorizedFilter):
    """Exclusion of tickets identical to recent draws."""
    unique_id = "historical_recent_exclusion"
    display_name = "Recent Draws Exclusion"
    tier = 4
    category = "History Exclusion"
    description = "Rejects tickets that exactly duplicate any draw from recent history (e.g. past 10 draws)."
    formula = "∀ d ∈ RecentDraws: X ≠ d"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Recent Draws History: Past N official results         |\n"
        "| Condition           : Ticket must not exactly match   |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Check Match with Recent Draws]\n"
        "    B --> C{Exact Match Found?}\n"
        "    C -->|No| P[Pass]\n"
        "    C -->|Yes| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        recent = getattr(rules, 'recent_draws', [])
        if not recent: return np.ones(combinations.shape[0], dtype=bool)
        mask = np.ones(combinations.shape[0], dtype=bool)
        for draw in recent:
            match = np.all(np.isin(combinations, draw), axis=1)
            mask &= ~match
        return mask

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = set(np.asarray(combination, dtype=int).ravel())
        recent = getattr(rules, 'recent_draws', []) if rules is not None else []
        matched = False
        for draw in recent:
            if set(draw) == comb_arr:
                matched = True
                break
        passed = not matched
        gauge = "[✓ PASS]" if passed else "[✗ DUPLICATE]"
        summary = "No duplicate match in recent history -> PASS." if passed else "Matches an exact recent draw -> FAIL."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value="Unique" if passed else "Duplicate",
            allowed_range="No Exact Match",
            summary=summary,
            details={"is_duplicate": matched, "recent_draws_checked": len(recent)},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalOddEvenPatternFilter(VectorizedFilter):
    """Historical Odd/Even pattern check."""
    unique_id = "historical_oe_pattern"
    display_name = "Historical O/E Pattern"
    tier = 4
    category = "Historical Empirical"
    description = "Restricts the count of odd numbers to the central empirical band for the active draw rules."
    formula = "min_odds ≤ ∑ (x_i mod 2 ≠ 0) ≤ max_odds"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Common O/E Patterns: Adaptive band around expected    |\n"
        "| Allowed Odd Count  : [min_odds .. max_odds]           |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Odds]\n"
        "    B --> C{min_odds <= Odds <= max_odds?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[int, int]:
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = hi - lo + 1
        n_odds = sum(1 for x in range(lo, hi + 1) if x % 2 != 0)
        p = n_odds / max(1, n_pool)
        mu = k * p
        sigma = np.sqrt(k * p * (1 - p) * ((n_pool - k) / max(1, n_pool - 1))) if n_pool > 1 else 1.0
        min_odds = max(0, int(round(mu - 1.2 * sigma)))
        max_odds = min(k, int(round(mu + 1.2 * sigma)))
        return min_odds, max_odds

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_odds, max_odds = self._compute_bounds(rules, k)
        odd_counts = np.sum(combinations % 2 != 0, axis=1)
        return (odd_counts >= min_odds) & (odd_counts <= max_odds)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_odds, max_odds = self._compute_bounds(rules, k)
        odds = int(np.sum(comb_arr % 2 != 0))
        passed = min_odds <= odds <= max_odds
        gauge = format_gauge(odds, min_odds, max_odds, passed)
        summary = f"Historical O/E odd count is {odds} (allowed: {min_odds}..{max_odds}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=odds,
            allowed_range=f"[{min_odds}..{max_odds}]",
            summary=summary,
            details={"odds": odds, "evens": len(comb_arr) - odds, "min_odds": min_odds, "max_odds": max_odds},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalHighLowPatternFilter(VectorizedFilter):
    """Historical High/Low pattern check."""
    unique_id = "historical_hl_pattern"
    display_name = "Historical H/L Pattern"
    tier = 4
    category = "Historical Empirical"
    description = "Restricts high number counts (x > mid) to the adaptive empirical pattern band."
    formula = "min_highs ≤ ∑ (x_i > mid) ≤ max_highs"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Common H/L Patterns: Adaptive band around expected    |\n"
        "| Allowed High Count : [min_highs .. max_highs]         |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count High Numbers: x > mid]\n"
        "    B --> C{min_highs <= High Count <= max_highs?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[int, int, int]:
        lo, hi = (1, 60) if rules is None else rules.number_range
        mid = (lo + hi) // 2
        n_pool = hi - lo + 1
        n_high = hi - mid
        p = n_high / max(1, n_pool)
        mu = k * p
        sigma = np.sqrt(k * p * (1 - p) * ((n_pool - k) / max(1, n_pool - 1))) if n_pool > 1 else 1.0
        min_highs = max(0, int(round(mu - 1.2 * sigma)))
        max_highs = min(k, int(round(mu + 1.2 * sigma)))
        return mid, min_highs, max_highs

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        mid, min_highs, max_highs = self._compute_bounds(rules, k)
        high_counts = np.sum(combinations > mid, axis=1)
        return (high_counts >= min_highs) & (high_counts <= max_highs)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        mid, min_highs, max_highs = self._compute_bounds(rules, k)
        highs = int(np.sum(comb_arr > mid))
        passed = min_highs <= highs <= max_highs
        gauge = format_gauge(highs, min_highs, max_highs, passed)
        summary = f"Historical H/L high count (> {mid}) is {highs} (allowed: {min_highs}..{max_highs}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=highs,
            allowed_range=f"[{min_highs}..{max_highs}]",
            summary=summary,
            details={"highs": highs, "midpoint": mid, "min_highs": min_highs, "max_highs": max_highs},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalDecadePatternFilter(VectorizedFilter):
    """Ensures distinct decades are adequately represented."""
    unique_id = "historical_decade_pattern"
    display_name = "Historical Decade Pattern"
    tier = 4
    category = "Historical Empirical"
    description = "Requires that numbers span across an adaptive number of distinct decades."
    formula = "|{⌊(x_i - 1)/10⌋}| ≥ min_decades"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Decades Covered = count(distinct decade buckets)      |\n"
        "| Condition       : Decades Covered >= min_decades      |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Distinct Decades]\n"
        "    B --> C{Decades >= min_decades?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_min_decades(rules: Optional[DrawRules], k: int) -> int:
        lo, hi = (1, 60) if rules is None else rules.number_range
        total_decades = (hi - 1) // 10 - (lo - 1) // 10 + 1
        if total_decades <= 3:
            return max(1, total_decades)
        return min(total_decades, max(2, min(3, int(np.ceil(0.5 * k)))))

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_decades = self._compute_min_decades(rules, k)
        decades = (combinations - 1) // 10
        sorted_decades = np.sort(decades, axis=1)
        diffs = np.diff(sorted_decades, axis=1) > 0
        unique_counts = 1 + np.sum(diffs, axis=1)
        return unique_counts >= min_decades

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_decades = self._compute_min_decades(rules, k)
        decades = {(x - 1) // 10 for x in comb_arr}
        cnt = len(decades)
        passed = cnt >= min_decades
        gauge = format_gauge(cnt, min_decades, max(cnt, min_decades + 2), passed)
        summary = f"Distinct decades covered is {cnt} {sorted(list(decades))} (required: >= {min_decades}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"≥ {min_decades} decades",
            summary=summary,
            details={"decades": sorted(list(decades)), "count": cnt, "min_decades": min_decades},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalUnitPatternFilter(VectorizedFilter):
    """Requires distinct unit digits matching game scale."""
    unique_id = "historical_unit_pattern"
    display_name = "Historical Unit Pattern"
    tier = 4
    category = "Historical Empirical"
    description = "Ensures sufficient terminal digit dispersion by requiring an adaptive number of unique unit digits."
    formula = "|{x_i mod 10}| ≥ min_units"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Unique Units = count(distinct x mod 10)               |\n"
        "| Condition    : Unique Units >= min_units              |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Distinct Unit Digits]\n"
        "    B --> C{Distinct Units >= min_units?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_min_units(rules: Optional[DrawRules], k: int) -> int:
        if k <= 4:
            return max(1, k - 1)
        if k <= 6:
            return 4
        return min(10, max(4, int(np.ceil(0.6 * k))))

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_units = self._compute_min_units(rules, k)
        units = combinations % 10
        sorted_units = np.sort(units, axis=1)
        unique_counts = 1 + np.sum(np.diff(sorted_units, axis=1) > 0, axis=1)
        return unique_counts >= min_units

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_units = self._compute_min_units(rules, k)
        units = {x % 10 for x in comb_arr}
        cnt = len(units)
        passed = cnt >= min_units
        gauge = format_gauge(cnt, min_units, max(cnt, 10), passed)
        summary = f"Distinct unit digits is {cnt} {sorted(list(units))} (required: >= {min_units}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"≥ {min_units} unique units",
            summary=summary,
            details={"units": sorted(list(units)), "count": cnt, "min_units": min_units},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalConsecutivePatternFilter(VectorizedFilter):
    """Limits consecutive number pairs adaptively."""
    unique_id = "historical_consecutive_pattern"
    display_name = "Historical Consecutive Pattern"
    tier = 4
    category = "Historical Empirical"
    description = "Restricts the count of adjacent consecutive pairs (x[i+1] - x[i] == 1) to an adaptive threshold."
    formula = "∑ [x_{i+1} - x_i == 1] ≤ max_pairs"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Adjacent Consecutive Pairs: sum(diff == 1)            |\n"
        "| Condition                 : Pairs <= max_pairs        |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Count Diffs == 1]\n"
        "    B --> C{Consecutive Pairs <= max_pairs?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_max_pairs(rules: Optional[DrawRules], k: int) -> int:
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = max(1, hi - lo + 1)
        if n_pool == 60 and k == 6:
            return 2
        exp_consec = (k * (k - 1)) / (2.0 * n_pool) if n_pool > 0 else 0.5
        return max(2, int(np.ceil(exp_consec + 2.0 * np.sqrt(max(0.5, exp_consec)))))

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        max_pairs = self._compute_max_pairs(rules, k)
        diffs = np.diff(np.sort(combinations, axis=1), axis=1)
        return np.sum(diffs == 1, axis=1) <= max_pairs

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        k = len(comb_arr)
        max_pairs = self._compute_max_pairs(rules, k)
        diffs = np.diff(comb_arr)
        pairs_cnt = int(np.sum(diffs == 1))
        passed = pairs_cnt <= max_pairs
        gauge = format_gauge(pairs_cnt, 0, max_pairs, passed)
        summary = f"Consecutive pairs count is {pairs_cnt} (allowed: <= {max_pairs}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=pairs_cnt,
            allowed_range=f"≤ {max_pairs} pairs",
            summary=summary,
            details={"consecutive_pairs": pairs_cnt, "max_allowed": max_pairs},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class CommonPairFilter(VectorizedFilter):
    """Validates presence of historically frequent pairs."""
    unique_id = "historical_common_pair"
    display_name = "Common Pair"
    tier = 4
    category = "Co-occurrence"
    description = "Checks that combination contains at least one historically frequent co-occurring pair."
    formula = "∃ (a, b) ⊆ X : PairFrequency(a, b) ≥ Threshold"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Co-occurrence Graph: High-lift historical edges       |\n"
        "| Condition          : At least one common pair present |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Check Top Co-occurrence Pairs]\n"
        "    B --> C{Pair Found?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _get_common_pairs(rules: Optional[DrawRules]) -> set[tuple[int, int]] | None:
        if rules is None:
            return None
        cp = getattr(rules, 'common_pairs', None)
        if cp:
            return {tuple(sorted(p)) for p in cp}
        history = getattr(rules, 'historical_draws', None)
        if history is not None and len(history) >= 20:
            from collections import Counter
            import itertools
            pair_counts = Counter()
            for draw in history[-100:]:
                for p in itertools.combinations(sorted(draw), 2):
                    pair_counts[p] += 1
            if pair_counts:
                top_n = max(5, len(pair_counts) // 10)
                return {p for p, _ in pair_counts.most_common(top_n)}
        return None

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        cp = self._get_common_pairs(rules)
        if not cp:
            return np.ones(combinations.shape[0], dtype=bool)
        M, k = combinations.shape
        has_pair = np.zeros(M, dtype=bool)
        for (a, b) in cp:
            pass_pair = np.isin(combinations, a).any(axis=1) & np.isin(combinations, b).any(axis=1)
            has_pair |= pass_pair
        return has_pair

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        cp = self._get_common_pairs(rules)
        if not cp:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="Pass-through",
                allowed_range="Valid Co-occurrence",
                summary="No common pairs context available; graceful pass-through -> PASS.",
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge="[✓ PASS]",
            )
        comb_set = set(np.asarray(combination, dtype=int).ravel())
        found = [p for p in cp if p[0] in comb_set and p[1] in comb_set]
        passed = len(found) > 0
        summary = f"Common pairs present: {len(found)} {found[:3]} -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=len(found),
            allowed_range="≥ 1 common pair",
            summary=summary,
            details={"common_pairs_found": found},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge="[✓ PASS]" if passed else "[✗ FAIL]",
        )


class CommonTripletFilter(VectorizedFilter):
    """Validates presence of historically frequent triplets."""
    unique_id = "historical_common_triplet"
    display_name = "Common Triplet"
    tier = 4
    category = "Co-occurrence"
    description = "Checks that combination contains at least one historically frequent co-occurring triplet."
    formula = "∃ (a, b, c) ⊆ X : TripletFrequency(a, b, c) ≥ Threshold"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Triplet Hypergraph: High-lift historical 3-cliques    |\n"
        "| Condition         : At least one common triplet       |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Check Top Co-occurrence Triplets]\n"
        "    B --> C{Triplet Found?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _get_common_triplets(rules: Optional[DrawRules]) -> set[tuple[int, int, int]] | None:
        if rules is None:
            return None
        ct = getattr(rules, 'common_triplets', None)
        if ct:
            return {tuple(sorted(t)) for t in ct}
        history = getattr(rules, 'historical_draws', None)
        if history is not None and len(history) >= 20:
            from collections import Counter
            import itertools
            triplet_counts = Counter()
            for draw in history[-100:]:
                for t in itertools.combinations(sorted(draw), 3):
                    triplet_counts[t] += 1
            if triplet_counts:
                top_n = max(3, len(triplet_counts) // 20)
                return {t for t, _ in triplet_counts.most_common(top_n)}
        return None

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ct = self._get_common_triplets(rules)
        if not ct:
            return np.ones(combinations.shape[0], dtype=bool)
        M, k = combinations.shape
        has_triplet = np.zeros(M, dtype=bool)
        for (a, b, c) in ct:
            pass_triplet = (
                np.isin(combinations, a).any(axis=1)
                & np.isin(combinations, b).any(axis=1)
                & np.isin(combinations, c).any(axis=1)
            )
            has_triplet |= pass_triplet
        return has_triplet

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        ct = self._get_common_triplets(rules)
        if not ct:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="Pass-through",
                allowed_range="Valid Triplet",
                summary="No common triplets context available; graceful pass-through -> PASS.",
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge="[✓ PASS]",
            )
        comb_set = set(np.asarray(combination, dtype=int).ravel())
        found = [t for t in ct if t[0] in comb_set and t[1] in comb_set and t[2] in comb_set]
        passed = len(found) > 0
        summary = f"Common triplets present: {len(found)} {found[:2]} -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=len(found),
            allowed_range="≥ 1 common triplet",
            summary=summary,
            details={"common_triplets_found": found},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge="[✓ PASS]" if passed else "[✗ FAIL]",
        )


class HistoricalACRangeFilter(VectorizedFilter):
    """Historical arithmetic complexity range."""
    unique_id = "historical_ac_range"
    display_name = "Historical AC Range"
    tier = 4
    category = "Historical Empirical"
    description = "Checks that ticket Arithmetic Complexity matches empirical historical bounds."
    formula = "min_ac ≤ AC ≤ max_ac"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Arithmetic Complexity: AC = D(k) - (k - 1)            |\n"
        "| Empirical Range      : Matched against past winners   |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute AC]\n"
        "    B --> C{Historical AC Bounds Met?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[int, int]:
        lo, hi = (1, 60) if rules is None else rules.number_range
        max_possible_diffs = min((k * (k - 1)) // 2, max(1, hi - lo))
        ac_max = max(1, max_possible_diffs - (k - 1))
        min_ac = getattr(rules, 'min_ac', max(1, int(round(0.35 * ac_max)))) if rules is not None else max(1, int(round(0.35 * ac_max)))
        max_ac = getattr(rules, 'max_ac', ac_max) if rules is not None else ac_max
        return int(min_ac), int(max_ac)

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        n_rows, k = combinations.shape
        if k < 3:
            return np.ones(n_rows, dtype=bool)
        min_ac, max_ac = self._compute_bounds(rules, k)
        sorted_combs = np.sort(combinations, axis=1)
        hi = rules.number_range[1] if rules is not None else 60
        if hi <= 64:
            bitmasks = np.zeros(n_rows, dtype=np.uint64)
            for i in range(k):
                for j in range(i + 1, k):
                    diffs = (sorted_combs[:, j] - sorted_combs[:, i]).astype(np.uint64)
                    valid = (diffs > 0) & (diffs < 64)
                    shifts = np.where(valid, np.uint64(1) << diffs, np.uint64(0))
                    bitmasks |= shifts
            from engine.modules.filters import count_bits_64
            d_k = count_bits_64(bitmasks)
        else:
            d_k = np.array([len(set(c[j] - c[i] for i in range(k) for j in range(i + 1, k))) for c in sorted_combs])
        ac_values = d_k - (k - 1)
        return (ac_values >= min_ac) & (ac_values <= max_ac)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        k = len(comb_arr)
        min_ac, max_ac = self._compute_bounds(rules, k)
        if k < 3:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value=0,
                allowed_range="N/A",
                summary="Pick count too small for AC evaluation -> PASS.",
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge="[✓ PASS]",
            )
        diffs = set(comb_arr[j] - comb_arr[i] for i in range(k) for j in range(i + 1, k))
        ac_val = len(diffs) - (k - 1)
        passed = min_ac <= ac_val <= max_ac
        gauge = format_gauge(ac_val, min_ac, max_ac, passed)
        summary = f"Ticket Arithmetic Complexity is {ac_val} (allowed: {min_ac}..{max_ac}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=ac_val,
            allowed_range=f"[{min_ac}..{max_ac}]",
            summary=summary,
            details={"ac": ac_val, "unique_diffs": len(diffs)},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalMedianRangeFilter(VectorizedFilter):
    """Historical median range check with adaptive bounds."""
    unique_id = "historical_median_range"
    display_name = "Historical Median Range"
    tier = 4
    category = "Historical Empirical"
    description = "Restricts the median value to the adaptive historical corridor."
    formula = "min_med ≤ median(X) ≤ max_med"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Ticket Median = median(numbers)                       |\n"
        "| Allowed Range : [min_med .. max_med]                  |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Median]\n"
        "    B --> C{min_med <= Median <= max_med?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[float, float]:
        hist_median_min = getattr(rules, 'hist_median_min', None) if rules is not None else None
        hist_median_max = getattr(rules, 'hist_median_max', None) if rules is not None else None
        if hist_median_min is not None and hist_median_max is not None:
            return float(hist_median_min), float(hist_median_max)
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = hi - lo + 1
        if n_pool == 60 and k == 6:
            return 20.0, 40.0
        mu_med = (lo + hi) / 2.0
        sigma_med = (hi - lo + 1) / (2.0 * np.sqrt(3.0 * (k + 2)))
        min_med = float(np.round(mu_med - 1.68 * sigma_med))
        max_med = float(np.round(mu_med + 1.68 * sigma_med))
        return min_med, max_med

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_med, max_med = self._compute_bounds(rules, k)
        medians = np.median(combinations, axis=1)
        return (medians >= min_med) & (medians <= max_med)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_med, max_med = self._compute_bounds(rules, k)
        med = float(np.median(comb_arr))
        passed = min_med <= med <= max_med
        gauge = format_gauge(round(med, 1), min_med, max_med, passed)
        summary = f"Historical median is {med:.1f} (allowed: {min_med}..{max_med}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=med,
            allowed_range=f"[{min_med}..{max_med}]",
            summary=summary,
            details={"median": med, "min_med": min_med, "max_med": max_med},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalStdDevRangeFilter(VectorizedFilter):
    """Historical standard deviation range with adaptive corridor."""
    unique_id = "historical_std_dev_range"
    display_name = "Historical StdDev Range"
    tier = 4
    category = "Historical Empirical"
    description = "Restricts standard deviation to the empirical historical corridor."
    formula = "min_std ≤ σ(X) ≤ max_std"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Standard Deviation: sigma(X)                          |\n"
        "| Allowed Range     : [min_std .. max_std]              |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute StdDev]\n"
        "    B --> C{min_std <= Std <= max_std?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[float, float]:
        hist_std_min = getattr(rules, 'hist_std_min', None) if rules is not None else None
        hist_std_max = getattr(rules, 'hist_std_max', None) if rules is not None else None
        if hist_std_min is not None and hist_std_max is not None:
            return float(hist_std_min), float(hist_std_max)
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = hi - lo + 1
        sigma_0 = np.sqrt(max(1.0, (n_pool ** 2 - 1) / 12.0))
        min_std = max(1.0, float(np.round(0.58 * sigma_0)))
        max_std = float(np.round(1.18 * sigma_0))
        return min_std, max_std

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_std, max_std = self._compute_bounds(rules, k)
        std = np.std(combinations, axis=1)
        return (std >= min_std) & (std <= max_std)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=float).ravel()
        k = len(comb_arr)
        min_std, max_std = self._compute_bounds(rules, k)
        std_val = float(np.std(comb_arr))
        passed = min_std <= std_val <= max_std
        gauge = format_gauge(round(std_val, 2), min_std, max_std, passed)
        summary = f"Historical StdDev is {std_val:.2f} (allowed: {min_std}..{max_std}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(std_val, 2),
            allowed_range=f"[{min_std}..{max_std}]",
            summary=summary,
            details={"std_dev": std_val, "min_std": min_std, "max_std": max_std},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalSpreadRangeFilter(VectorizedFilter):
    """Historical spread range with adaptive bounds."""
    unique_id = "historical_spread_range"
    display_name = "Historical Spread Range"
    tier = 4
    category = "Historical Empirical"
    description = "Restricts the total spread (max - min) to empirical bounds."
    formula = "min_spread ≤ max(X) - min(X) ≤ max_spread"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Total Spread = max(X) - min(X)                        |\n"
        "| Allowed Range: [min_spread .. max_spread]             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Spread = max(X) - min(X)]\n"
        "    B --> C{min_spread <= Spread <= max_spread?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[int, int]:
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = hi - lo + 1
        exp_spread = n_pool * ((k - 1) / max(1, k + 1))
        min_spread = max(1, int(np.floor(0.70 * exp_spread)))
        max_spread = min(hi - lo, int(np.ceil(1.28 * exp_spread)))
        return min_spread, max_spread

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_spread, max_spread = self._compute_bounds(rules, k)
        spread = np.max(combinations, axis=1) - np.min(combinations, axis=1)
        return (spread >= min_spread) & (spread <= max_spread)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_spread, max_spread = self._compute_bounds(rules, k)
        spread = int(np.max(comb_arr) - np.min(comb_arr))
        passed = min_spread <= spread <= max_spread
        gauge = format_gauge(spread, min_spread, max_spread, passed)
        summary = f"Historical spread (max - min) is {spread} (allowed: {min_spread}..{max_spread}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=spread,
            allowed_range=f"[{min_spread}..{max_spread}]",
            summary=summary,
            details={"spread": spread, "min_spread": min_spread, "max_spread": max_spread},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HistoricalDigitSumPatternFilter(VectorizedFilter):
    """Historical digit sum pattern with adaptive bounds."""
    unique_id = "historical_digit_sum_pattern"
    display_name = "Historical Digit Sum Pattern"
    tier = 4
    category = "Historical Empirical"
    description = "Constrains total digit sum to the central historical interval."
    formula = "min_dsum ≤ ∑ (⌊x_i/10⌋ + (x_i mod 10)) ≤ max_dsum"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Historical Digit Sum = sum(tens + units)              |\n"
        "| Allowed Range        : [min_dsum .. max_dsum]         |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Digit Sum]\n"
        "    B --> C{min_dsum <= Digit Sum <= max_dsum?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    @staticmethod
    def _compute_bounds(rules: Optional[DrawRules], k: int) -> tuple[int, int]:
        lo, hi = (1, 60) if rules is None else rules.number_range
        n_pool = hi - lo + 1
        if n_pool == 60 and k == 6:
            return 25, 55
        vals = np.arange(lo, hi + 1)
        dsums = (vals // 10) + (vals % 10)
        mu_1 = float(np.mean(dsums))
        var_1 = float(np.var(dsums))
        finite_correction = (n_pool - k) / max(1, n_pool - 1) if n_pool > 1 else 1.0
        sigma_k = np.sqrt(max(1.0, k * var_1 * finite_correction))
        mu_k = k * mu_1
        min_dsum = max(1, int(round(mu_k - 1.93 * sigma_k)))
        max_dsum = int(round(mu_k + 1.72 * sigma_k))
        return min_dsum, max_dsum

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_dsum, max_dsum = self._compute_bounds(rules, k)
        digit_sums = np.sum((combinations // 10) + (combinations % 10), axis=1)
        return (digit_sums >= min_dsum) & (digit_sums <= max_dsum)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_dsum, max_dsum = self._compute_bounds(rules, k)
        d_sum = int(np.sum((comb_arr // 10) + (comb_arr % 10)))
        passed = min_dsum <= d_sum <= max_dsum
        gauge = format_gauge(d_sum, min_dsum, max_dsum, passed)
        summary = f"Historical digit sum is {d_sum} (allowed: {min_dsum}..{max_dsum}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=d_sum,
            allowed_range=f"[{min_dsum}..{max_dsum}]",
            summary=summary,
            details={"digit_sum": d_sum, "min_dsum": min_dsum, "max_dsum": max_dsum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MaxSkipsFilter(VectorizedFilter):
    """Vetoes tickets containing balls exceeding historical skip threshold."""
    unique_id = "historical_max_skips"
    display_name = "Maximum Historical Draw Skip"
    tier = 4
    category = "Temporal Skips"
    description = "Vetoes tickets containing numbers that have exceeded a maximum historical skip interval threshold (deep-cold exclusion)."
    formula = "\\forall x_i \\in \\text{Ticket}, \\quad \\text{Skip}(x_i) \\le S_{\\text{max}}"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Maximum Historical Draw Skip Threshold               |\n"
        "| Target    : Skip(x_i) = Draws elapsed since last win  |\n"
        "| Condition : max(Skip(x_i)) <= Threshold (default 50)  |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Lookup Current Skip for Each Ball]\n"
        "    B --> C[Find Max Skip: max(Skip(x_i))]\n"
        "    C --> D{Max Skip <= Threshold?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject Deep-Cold Balls]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        skips = getattr(rules, 'current_skips', {})
        threshold = getattr(rules, 'max_skip_threshold', 50)
        if not skips:
            return np.ones(combinations.shape[0], dtype=bool)
        violating_balls = [int(n) for n, s in skips.items() if s > threshold]
        if not violating_balls:
            return np.ones(combinations.shape[0], dtype=bool)
        return np.sum(np.isin(combinations, violating_balls), axis=1) == 0

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        skips = getattr(rules, 'current_skips', {}) if rules is not None else {}
        threshold = getattr(rules, 'max_skip_threshold', 50) if rules is not None else 50
        if not skips:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="No skip context",
                allowed_range=f"Skip <= {threshold}",
                summary="No historical skips context supplied -> PASS.",
                details={"max_skip_threshold": threshold},
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge="[✓ PASS]",
            )
        violators = [int(x) for x in comb_arr if skips.get(int(x), 0) > threshold]
        passed = (len(violators) == 0)
        max_found_skip = max((skips.get(int(x), 0) for x in comb_arr), default=0)
        gauge = format_gauge(max_found_skip, 0, threshold, passed)
        summary = f"Max skip in ticket is {max_found_skip} (threshold: <= {threshold}, violators: {violators}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=max_found_skip,
            allowed_range=f"[0..{threshold}]",
            summary=summary,
            details={"max_found_skip": max_found_skip, "violators": violators, "threshold": threshold},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )

