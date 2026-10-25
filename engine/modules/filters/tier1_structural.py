from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence
from engine.modules.filters import VectorizedFilter, FilterExplanation, format_gauge, PRIMES, count_bits_64

if TYPE_CHECKING:
    from engine.adapters import DrawRules


class OddCountFilter(VectorizedFilter):
    """Evaluates whether the count of odd numbers falls within the 30% to 70% envelope."""
    unique_id = "structural_odd_count"
    display_name = "Odd Number Count"
    tier = 1
    category = "Parity & Balance"
    description = "Checks if the count of odd balls is within 30-70% of picked numbers, avoiding extreme all-odd or all-even combinations."
    formula = "max(1, ⌊0.3 × k⌋) ≤ ∑ (x_i mod 2) ≤ min(k - 1, ⌊0.7 × k⌋)"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Ticket -> Count Odd Balls: sum(x % 2 != 0)            |\n"
        "| Bounds : [max(1, 0.3*k) .. min(k-1, 0.7*k)]           |\n"
        "| Verdict: [======|=====●=====|======] PASS             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Odds: sum(x % 2 != 0)]\n"
        "    B --> C{30% <= Odds <= 70%?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_counts = np.sum(combinations % 2, axis=1)
        n_picked = combinations.shape[1]
        return (odd_counts >= max(1, int(0.3 * n_picked))) & (odd_counts <= min(n_picked - 1, int(0.7 * n_picked)))

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_odd = max(1, int(0.3 * k))
        max_odd = min(k - 1, int(0.7 * k))
        odds = int(np.sum(comb_arr % 2 != 0))
        passed = min_odd <= odds <= max_odd
        gauge = format_gauge(odds, min_odd, max_odd, passed)
        summary = f"Odd count is {odds}/{k} (allowed: {min_odd}..{max_odd}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=odds,
            allowed_range=f"[{min_odd}..{max_odd}]",
            summary=summary,
            details={"odd_count": odds, "even_count": k - odds, "total_balls": k},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class EvenCountFilter(VectorizedFilter):
    """Ensures combination contains at least one even number and at most k-1 even numbers."""
    unique_id = "structural_even_count"
    display_name = "Even Number Count"
    tier = 1
    category = "Parity & Balance"
    description = "Checks if the number of even balls is balanced within [1 .. k-1], eliminating homogenous odd-only tickets."
    formula = "1 ≤ ∑ (x_i mod 2 == 0) ≤ k - 1"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Ticket -> Count Even Balls: sum(x % 2 == 0)           |\n"
        "| Bounds : [1 .. k - 1]                                 |\n"
        "| Flow   : 0 Evens -> REJECT | >=1 & <=k-1 -> PASS      |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Evens: sum(x % 2 == 0)]\n"
        "    B --> C{1 <= Evens <= k-1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        even_counts = np.sum(combinations % 2 == 0, axis=1)
        n_picked = combinations.shape[1]
        return (even_counts >= 1) & (even_counts <= n_picked - 1)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        evens = int(np.sum(comb_arr % 2 == 0))
        passed = 1 <= evens <= (k - 1)
        gauge = format_gauge(evens, 1, k - 1, passed)
        summary = f"Even count is {evens}/{k} (allowed: 1..{k - 1}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=evens,
            allowed_range=f"[1..{k - 1}]",
            summary=summary,
            details={"even_count": evens, "odd_count": k - evens},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class OddEvenRatioFilter(VectorizedFilter):
    """Verifies that odd vs even balls remain balanced within a tolerance difference of 2."""
    unique_id = "structural_odd_even_ratio"
    display_name = "Odd/Even Ratio"
    tier = 1
    category = "Parity & Balance"
    description = "Enforces parity balance (|odds - evens| <= 2), favoring common 3:3, 4:2, 2:4 distributions."
    formula = "|odd_count - even_count| ≤ 2"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Abs Diff: |odds - evens|                              |\n"
        "| Bounds  : <= 2                                        |\n"
        "| Split   : 3:3 (diff 0), 4:2 / 2:4 (diff 2) -> PASS    |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Diff = abs(odds - evens)]\n"
        "    B --> C{Diff <= 2?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_counts = np.sum(combinations % 2 != 0, axis=1)
        even_counts = combinations.shape[1] - odd_counts
        return np.abs(odd_counts - even_counts) <= 2

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        odds = int(np.sum(comb_arr % 2 != 0))
        evens = len(comb_arr) - odds
        diff = abs(odds - evens)
        passed = diff <= 2
        gauge = format_gauge(diff, 0, 2, passed)
        summary = f"Parity split is {odds} odds : {evens} evens (diff {diff}, max 2) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=f"{odds}:{evens} (diff={diff})",
            allowed_range="diff ≤ 2",
            summary=summary,
            details={"odds": odds, "evens": evens, "diff": diff},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HighCountFilter(VectorizedFilter):
    """Numbers in the upper half of the lottery pool."""
    unique_id = "structural_high_count"
    display_name = "High Number Count"
    tier = 1
    category = "Magnitude & Range"
    description = "Checks that the ticket contains at least 1 and at most k-1 high numbers (numbers > mid-point)."
    formula = "1 ≤ ∑ (x_i > ⌊(lo + hi)/2⌋) ≤ k - 1"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Midpoint: (lo + hi) // 2                              |\n"
        "| High Ball Count: sum(x > mid)                         |\n"
        "| Target  : [1 .. k - 1]                                |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Highs: sum(x > mid)]\n"
        "    B --> C{1 <= Highs <= k-1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        high_counts = np.sum(combinations > mid, axis=1)
        return (high_counts >= 1) & (high_counts <= combinations.shape[1] - 1)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        lo, hi = (1, 60) if rules is None else rules.number_range
        mid = (lo + hi) // 2
        highs = int(np.sum(comb_arr > mid))
        passed = 1 <= highs <= (k - 1)
        gauge = format_gauge(highs, 1, k - 1, passed)
        summary = f"High number count (> {mid}) is {highs}/{k} (allowed: 1..{k - 1}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=highs,
            allowed_range=f"[1..{k - 1}]",
            summary=summary,
            details={"midpoint": mid, "highs": highs, "lows": k - highs},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class LowCountFilter(VectorizedFilter):
    """Numbers in the lower half of the lottery pool."""
    unique_id = "structural_low_count"
    display_name = "Low Number Count"
    tier = 1
    category = "Magnitude & Range"
    description = "Checks that the ticket contains at least 1 and at most k-1 low numbers (numbers <= mid-point)."
    formula = "1 ≤ ∑ (x_i ≤ ⌊(lo + hi)/2⌋) ≤ k - 1"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Midpoint: (lo + hi) // 2                              |\n"
        "| Low Ball Count: sum(x <= mid)                         |\n"
        "| Target  : [1 .. k - 1]                                |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Lows: sum(x <= mid)]\n"
        "    B --> C{1 <= Lows <= k-1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        low_counts = np.sum(combinations <= mid, axis=1)
        return (low_counts >= 1) & (low_counts <= combinations.shape[1] - 1)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        lo, hi = (1, 60) if rules is None else rules.number_range
        mid = (lo + hi) // 2
        lows = int(np.sum(comb_arr <= mid))
        passed = 1 <= lows <= (k - 1)
        gauge = format_gauge(lows, 1, k - 1, passed)
        summary = f"Low number count (<= {mid}) is {lows}/{k} (allowed: 1..{k - 1}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=lows,
            allowed_range=f"[1..{k - 1}]",
            summary=summary,
            details={"midpoint": mid, "lows": lows, "highs": k - lows},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class LowHighRatioFilter(VectorizedFilter):
    """Ratio between low and high halves."""
    unique_id = "structural_low_high_ratio"
    display_name = "Low/High Ratio"
    tier = 1
    category = "Magnitude & Range"
    description = "Enforces balance between low and high balls (|lows - highs| <= 2)."
    formula = "|low_count - high_count| ≤ 2"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Abs Diff: |lows - highs|                              |\n"
        "| Bounds  : <= 2                                        |\n"
        "| Ensures balanced spatial coverage across board halves |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Diff = abs(lows - highs)]\n"
        "    B --> C{Diff <= 2?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mid = (rules.number_range[0] + rules.number_range[1]) // 2
        low_counts = np.sum(combinations <= mid, axis=1)
        high_counts = combinations.shape[1] - low_counts
        return np.abs(low_counts - high_counts) <= 2

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        lo, hi = (1, 60) if rules is None else rules.number_range
        mid = (lo + hi) // 2
        lows = int(np.sum(comb_arr <= mid))
        highs = len(comb_arr) - lows
        diff = abs(lows - highs)
        passed = diff <= 2
        gauge = format_gauge(diff, 0, 2, passed)
        summary = f"Low/High split is {lows} lows : {highs} highs (diff {diff}, max 2) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=f"{lows}:{highs} (diff={diff})",
            allowed_range="diff ≤ 2",
            summary=summary,
            details={"lows": lows, "highs": highs, "diff": diff, "midpoint": mid},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class PrimeCountFilter(VectorizedFilter):
    """Prime number count within expected frequencies."""
    unique_id = "structural_prime_count"
    display_name = "Prime Number Count"
    tier = 1
    category = "Number Theory"
    description = "Checks if prime count is between 1 and 70% of picked numbers, reflecting natural prime density."
    formula = "1 ≤ ∑ [x_i ∈ ℙ] ≤ ⌊0.7 × k⌋"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Primes Set: {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...} |\n"
        "| Count: sum(x in Primes)                               |\n"
        "| Range: [1 .. 0.7 * k]                                 |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Primes: sum(x in Primes)]\n"
        "    B --> C{1 <= Primes <= 0.7*k?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        prime_counts = np.sum(np.isin(combinations, PRIMES), axis=1)
        return (prime_counts >= 1) & (prime_counts <= int(0.7 * combinations.shape[1]))

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        max_primes = int(0.7 * k)
        primes_found = [int(x) for x in comb_arr if x in PRIMES]
        prime_cnt = len(primes_found)
        passed = 1 <= prime_cnt <= max_primes
        gauge = format_gauge(prime_cnt, 1, max_primes, passed)
        summary = f"Prime count is {prime_cnt}/{k} {primes_found} (allowed: 1..{max_primes}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=prime_cnt,
            allowed_range=f"[1..{max_primes}]",
            summary=summary,
            details={"primes": primes_found, "count": prime_cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class CompositeCountFilter(VectorizedFilter):
    """Composite number count check."""
    unique_id = "structural_composite_count"
    display_name = "Composite Number Count"
    tier = 1
    category = "Number Theory"
    description = "Ensures the ticket contains at least one composite number (x > 1 and x not in Primes)."
    formula = "∑ [x_i > 1 ∧ x_i ∉ ℙ] ≥ 1"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Composites: numbers > 1 that are not prime            |\n"
        "| Condition : Count >= 1                                |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Composites]\n"
        "    B --> C{Composites >= 1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        is_composite = (combinations > 1) & ~np.isin(combinations, PRIMES)
        counts = np.sum(is_composite, axis=1)
        return counts >= 1

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        composites = [int(x) for x in comb_arr if x > 1 and x not in PRIMES]
        cnt = len(composites)
        passed = cnt >= 1
        gauge = format_gauge(cnt, 1, max(cnt, 5), passed)
        summary = f"Composite count is {cnt} {composites} (required: >= 1) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="≥ 1",
            summary=summary,
            details={"composites": composites, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class SquareCountFilter(VectorizedFilter):
    """Limits perfect squares."""
    unique_id = "structural_square_count"
    display_name = "Square Number Count"
    tier = 1
    category = "Number Theory"
    description = "Limits perfect square numbers (1, 4, 9, 16, 25, 36, 49, 64, 81, 100) to at most 2 per ticket."
    formula = "∑ [x_i ∈ {n²}] ≤ 2"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Squares Set: {1, 4, 9, 16, 25, 36, 49, 64, 81, 100}  |\n"
        "| Condition  : Count <= 2                               |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Squares: sum(x in Squares)]\n"
        "    B --> C{Count <= 2?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        squares = np.array([1, 4, 9, 16, 25, 36, 49, 64, 81, 100])
        counts = np.sum(np.isin(combinations, squares), axis=1)
        return counts <= 2

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        squares = {1, 4, 9, 16, 25, 36, 49, 64, 81, 100}
        found = [int(x) for x in comb_arr if x in squares]
        cnt = len(found)
        passed = cnt <= 2
        gauge = format_gauge(cnt, 0, 2, passed)
        summary = f"Square number count is {cnt} {found} (max allowed: 2) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="≤ 2",
            summary=summary,
            details={"squares": found, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class FibonacciCountFilter(VectorizedFilter):
    """Fibonacci number count."""
    unique_id = "structural_fibonacci_count"
    display_name = "Fibonacci Number Count"
    tier = 1
    category = "Number Theory"
    description = "Restricts the count of Fibonacci numbers (1, 2, 3, 5, 8, 13, 21, 34, 55, 89) to no more than 3."
    formula = "∑ [x_i ∈ Fib] ≤ 3"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Fib Set  : {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}        |\n"
        "| Condition: Count <= 3                                 |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count Fibs: sum(x in Fib)]\n"
        "    B --> C{Count <= 3?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        fibs = np.array([1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
        counts = np.sum(np.isin(combinations, fibs), axis=1)
        return counts <= 3

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        fibs = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
        found = [int(x) for x in comb_arr if x in fibs]
        cnt = len(found)
        passed = cnt <= 3
        gauge = format_gauge(cnt, 0, 3, passed)
        summary = f"Fibonacci count is {cnt} {found} (max allowed: 3) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range="≤ 3",
            summary=summary,
            details={"fibs": found, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class ACValueFilter(VectorizedFilter):
    """Arithmetic Complexity filter."""
    unique_id = "structural_ac_value"
    display_name = "Arithmetic Complexity (AC)"
    tier = 1
    category = "Complexity & Entropy"
    description = "Calculates the variation of differences: AC = |{x_j - x_i}| - (k - 1). Rejects simple arithmetic patterns."
    formula = "AC = |{x_j - x_i ∣ j > i}| - (k - 1) ≥ min_ac"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Distinct Pairwise Differences: D(k)                   |\n"
        "| Arithmetic Complexity: AC = D(k) - (k - 1)            |\n"
        "| Thresholds: k<=5 -> AC>=4 | k=6 -> AC>=7 | k>=7 -> 10 |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute All Pair Differences]\n"
        "    B --> C[AC = Count(Unique Diffs) - (k - 1)]\n"
        "    C --> D{AC >= min_ac?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject]"
    )

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
        min_ac = 4 if k <= 5 else (7 if k == 6 else 10)
        return (unique_counts - (k - 1)) >= min_ac

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        k = len(comb_arr)
        if k < 2:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value=0,
                allowed_range="N/A",
                summary="Insufficient balls for AC calculation -> PASS.",
            )
        diffs = set()
        for i in range(k):
            for j in range(i + 1, k):
                diffs.add(int(comb_arr[j] - comb_arr[i]))
        ac = len(diffs) - (k - 1)
        min_ac = 4 if k <= 5 else (7 if k == 6 else 10)
        passed = ac >= min_ac
        gauge = format_gauge(ac, min_ac, min_ac + 8, passed)
        summary = f"Arithmetic Complexity is {ac} (unique diffs={len(diffs)}, required min_ac={min_ac}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=ac,
            allowed_range=f"≥ {min_ac}",
            summary=summary,
            details={"unique_diffs": len(diffs), "ac": ac, "min_ac": min_ac},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class DigitSumFilter(VectorizedFilter):
    """Total sum of decimal digits."""
    unique_id = "structural_digit_sum"
    display_name = "Total Digit Sum"
    tier = 1
    category = "Digital Topology"
    description = "Sum of all decimal digits of all numbers in the ticket, bounded in [20..60]."
    formula = "20 ≤ ∑ (⌊x_i/10⌋ + (x_i mod 10)) ≤ 60"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Digit Sum: sum(tens_digit + unit_digit)               |\n"
        "| Allowed Range: [20 .. 60]                             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Sum Digits: tens + units]\n"
        "    B --> C{20 <= DigitSum <= 60?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        digit_sums = np.sum((combinations // 10) + (combinations % 10), axis=1)
        return (digit_sums >= 20) & (digit_sums <= 60)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        d_sum = int(np.sum((comb_arr // 10) + (comb_arr % 10)))
        passed = 20 <= d_sum <= 60
        gauge = format_gauge(d_sum, 20, 60, passed)
        summary = f"Total digit sum is {d_sum} (allowed: 20..60) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=d_sum,
            allowed_range="[20..60]",
            summary=summary,
            details={"digit_sum": d_sum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class UnitSumFilter(VectorizedFilter):
    """Sum of terminal units."""
    unique_id = "structural_unit_sum"
    display_name = "Total Unit Sum"
    tier = 1
    category = "Digital Topology"
    description = "Sum of the terminal unit digits (x mod 10) of all numbers, constrained to [10..45]."
    formula = "10 ≤ ∑ (x_i mod 10) ≤ 45"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Unit Sum: sum(x % 10)                                 |\n"
        "| Allowed Range: [10 .. 45]                             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Sum Units: sum(x % 10)]\n"
        "    B --> C{10 <= UnitSum <= 45?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        unit_sums = np.sum(combinations % 10, axis=1)
        return (unit_sums >= 10) & (unit_sums <= 45)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        u_sum = int(np.sum(comb_arr % 10))
        passed = 10 <= u_sum <= 45
        gauge = format_gauge(u_sum, 10, 45, passed)
        summary = f"Total unit sum is {u_sum} (allowed: 10..45) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=u_sum,
            allowed_range="[10..45]",
            summary=summary,
            details={"unit_sum": u_sum, "units": [int(x % 10) for x in comb_arr]},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


def _make_decade_class(decade_num: int, start_val: int, end_val: int):
    class DecadeCountFilter(VectorizedFilter):
        unique_id = f"structural_decade_{decade_num}"
        display_name = f"Decade {decade_num} ({start_val}-{end_val}) Count"
        tier = 1
        category = "Decade Distribution"
        description = f"Limits numbers in Decade {decade_num} ({start_val}–{end_val}) to at most 3."
        formula = f"∑ [{start_val} ≤ x_i ≤ {end_val}] ≤ 3"
        diagram = (
            f"+-------------------------------------------------------+\n"
            f"| Decade {decade_num} Range: [{start_val} .. {end_val}]                      |\n"
            f"| Condition     : Count <= 3                            |\n"
            f"+-------------------------------------------------------+"
        )
        mermaid = (
            "graph LR\n"
            f"    A[Ticket Combination] --> B[Count in {start_val}..{end_val}]\n"
            "    B --> C{Count <= 3?}\n"
            "    C -->|Yes| P[Pass]\n"
            "    C -->|No| F[Reject]"
        )

        def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
            counts = np.sum((combinations >= start_val) & (combinations <= end_val), axis=1)
            return counts <= 3

        def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
            comb_arr = np.asarray(combination, dtype=int).ravel()
            in_decade = [int(x) for x in comb_arr if start_val <= x <= end_val]
            cnt = len(in_decade)
            passed = cnt <= 3
            gauge = format_gauge(cnt, 0, 3, passed)
            summary = f"Decade {decade_num} ({start_val}-{end_val}) count is {cnt} {in_decade} (max: 3) -> {'PASS' if passed else 'FAIL'}."
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=passed,
                actual_value=cnt,
                allowed_range="≤ 3",
                summary=summary,
                details={"numbers": in_decade, "count": cnt, "decade": decade_num},
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge=gauge,
            )
    DecadeCountFilter.__name__ = f"Decade{decade_num}CountFilter"
    return DecadeCountFilter


Decade1CountFilter = _make_decade_class(1, 1, 10)
Decade2CountFilter = _make_decade_class(2, 11, 20)
Decade3CountFilter = _make_decade_class(3, 21, 30)
Decade4CountFilter = _make_decade_class(4, 31, 40)
Decade5CountFilter = _make_decade_class(5, 41, 50)
Decade6CountFilter = _make_decade_class(6, 51, 60)


class BirthdayBiasFilter(VectorizedFilter):
    """Restricts excessive clustering in calendar date range 1-31."""
    unique_id = "structural_birthday_bias"
    display_name = "Birthday Bias Avoidance"
    tier = 1
    category = "Crowd Avoidance"
    description = "Limits balls in the calendar date range (1-31) to prevent shared public split jackpots."
    formula = "∑ [1 ≤ x_i ≤ 31] ≤ max_birthday"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Calendar Birthday Zone : Numbers in [1 .. 31]         |\n"
        "| Condition              : Count <= max_birthday        |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count in 1..31]\n"
        "    B --> C{Count <= max_birthday?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject (Crowd Clustered)]"
    )

    @staticmethod
    def _compute_max(k: int) -> int:
        return max(1, min(k - 1, int(round(0.68 * k))))

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        max_bday = self._compute_max(k)
        counts = np.sum((combinations >= 1) & (combinations <= 31), axis=1)
        return counts <= max_bday

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        max_bday = self._compute_max(k)
        in_bday = [int(x) for x in comb_arr if 1 <= x <= 31]
        cnt = len(in_bday)
        passed = cnt <= max_bday
        gauge = format_gauge(cnt, 0, max_bday, passed)
        summary = f"Birthday numbers count is {cnt} {in_bday} (allowed: <= {max_bday}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"≤ {max_bday}",
            summary=summary,
            details={"birthday_numbers": in_bday, "count": cnt, "max_allowed": max_bday},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class NoArithmeticProgressionFilter(VectorizedFilter):
    """Vetoes exact arithmetic progressions."""
    unique_id = "structural_no_arithmetic"
    display_name = "No Arithmetic Progression"
    tier = 1
    category = "Pattern Avoidance"
    description = "Rejects tickets that form exact arithmetic progressions with constant steps (e.g. 2,4,6,8 or 5,10,15,20)."
    formula = "¬ ∃ d : x_{i+1} - x_i = d ∀ i"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Arithmetic Sequence : Equal step d between all balls  |\n"
        "| Condition           : At least 2 distinct diff values |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Sorted Ticket] --> B[Diffs = diff(X)]\n"
        "    B --> C{Unique Diffs > 1?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject (Linear AP)]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        n_rows, k = combinations.shape
        if k < 3:
            return np.ones(n_rows, dtype=bool)
        sorted_combs = np.sort(combinations, axis=1)
        diffs = np.diff(sorted_combs, axis=1)
        # Check if all diffs are identical in any row
        all_equal = np.all(diffs == diffs[:, [0]], axis=1)
        return ~all_equal

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.sort(np.asarray(combination, dtype=int).ravel())
        k = len(comb_arr)
        if k < 3:
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=True,
                actual_value="N/A",
                allowed_range="k >= 3 required",
                summary="Pick count too small for AP check -> PASS.",
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge="[✓ PASS]",
            )
        diffs = np.diff(comb_arr)
        is_ap = bool(np.all(diffs == diffs[0]))
        passed = not is_ap
        summary = f"Differences are {list(diffs)} ({'Pure AP with step ' + str(diffs[0]) if is_ap else 'Non-linear sequence'}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value="Linear AP" if is_ap else "Non-linear",
            allowed_range="No Exact AP",
            summary=summary,
            details={"diffs": list(map(int, diffs)), "is_ap": is_ap},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge="[✓ PASS]" if passed else "[✗ FAIL]",
        )


class NoSameLastDigitFilter(VectorizedFilter):
    """Limits frequency of identical terminal unit digits."""
    unique_id = "structural_no_same_last_digit"
    display_name = "Terminal Digit Diversity"
    tier = 1
    category = "Terminal Digits"
    description = "Prevents tickets from containing too many numbers ending with the exact same unit digit."
    formula = "max_d count(x_i mod 10 == d) ≤ max_same_units"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Terminal Units : x_i mod 10                           |\n"
        "| Condition      : Max count of any single digit <= max |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Group by Units (x % 10)]\n"
        "    B --> C{Max Same Unit <= Allowed?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject (Terminal Clustering)]"
    )

    @staticmethod
    def _compute_max_same(k: int) -> int:
        return max(2, int(np.ceil(0.38 * k)))

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        max_same = self._compute_max_same(k)
        units = combinations % 10
        sorted_units = np.sort(units, axis=1)
        # Vectorized check: does any unit appear more than max_same times?
        # A unit appears > max_same times iff sorted_units[:, i + max_same] == sorted_units[:, i] for some i
        exceeds = np.zeros(combinations.shape[0], dtype=bool)
        for i in range(k - max_same):
            exceeds |= (sorted_units[:, i + max_same] == sorted_units[:, i])
        return ~exceeds

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        max_same = self._compute_max_same(k)
        from collections import Counter
        unit_counts = Counter(x % 10 for x in comb_arr)
        max_found = max(unit_counts.values()) if unit_counts else 0
        most_common_digit, count = unit_counts.most_common(1)[0] if unit_counts else (0, 0)
        passed = max_found <= max_same
        gauge = format_gauge(max_found, 1, max_same, passed)
        summary = f"Max identical terminal unit is {count} (ending in {most_common_digit}, allowed: <= {max_same}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=count,
            allowed_range=f"≤ {max_same} per unit",
            summary=summary,
            details={"unit_counts": dict(unit_counts), "max_frequency": count},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class StructuralBreadthFilter(VectorizedFilter):
    """Numbers must span multiple distinct decades."""
    unique_id = "structural_breadth"
    display_name = "Decade Breadth / Span"
    tier = 1
    category = "Decade & Distribution"
    description = "Ensures numbers span multiple distinct decades (at least 3 decades for k < 10, at least 4 for k >= 10)."
    formula = "|{⌊x_i / 10⌋}| ≥ (3 if k < 10 else 4)"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Decades Spanned: |{x // 10}|                          |\n"
        "| Requirement    : >= 3 decades (k < 10), >= 4 (k >= 10)|\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Distinct Decades: set(x // 10)]\n"
        "    B --> C{Count >= Min Decades?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject Decadally Clustered Ticket]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_decades = 3 if k < 10 else 4
        decades = combinations // 10
        sorted_dec = np.sort(decades, axis=1)
        unique_counts = 1 + np.sum(sorted_dec[:, 1:] != sorted_dec[:, :-1], axis=1)
        return unique_counts >= min_decades

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_decades = 3 if k < 10 else 4
        decades = {x // 10 for x in comb_arr}
        cnt = len(decades)
        passed = cnt >= min_decades
        gauge = format_gauge(cnt, min_decades, max(min_decades, min(6, k)), passed)
        summary = f"Distinct decades spanned is {cnt} (decades: {sorted(decades)}, required: >= {min_decades}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"≥ {min_decades}",
            summary=summary,
            details={"decades": sorted(decades), "count": cnt, "min_required": min_decades},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class StructuralDistinctUnitsFilter(VectorizedFilter):
    """Requires a minimum number of distinct terminal unit digits."""
    unique_id = "structural_distinct_units"
    display_name = "Distinct Terminal Units Count"
    tier = 1
    category = "Unit / Last Digit"
    description = "Requires a minimum number of distinct terminal digits (at least 4 for k <= 6, at least 6 for k > 6)."
    formula = "|{x_i mod 10}| ≥ (4 if k ≤ 6 else 6)"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Terminal Units: |{x % 10}|                            |\n"
        "| Requirement   : >= 4 distinct (k <= 6), >= 6 (k > 6)  |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Unique Units: set(x % 10)]\n"
        "    B --> C{Unique Count >= Min Allowed?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject Monotonous Unit Digits]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_distinct = 4 if k <= 6 else 6
        units = combinations % 10
        sorted_units = np.sort(units, axis=1)
        distinct_counts = 1 + np.sum(sorted_units[:, 1:] != sorted_units[:, :-1], axis=1)
        return distinct_counts >= min_distinct

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_distinct = 4 if k <= 6 else 6
        units = {x % 10 for x in comb_arr}
        cnt = len(units)
        passed = cnt >= min_distinct
        gauge = format_gauge(cnt, min_distinct, min(10, k), passed)
        summary = f"Distinct terminal units count is {cnt} (units: {sorted(units)}, required: >= {min_distinct}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"≥ {min_distinct}",
            summary=summary,
            details={"units": sorted(units), "count": cnt, "min_required": min_distinct},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class StructuralAverageValueFilter(VectorizedFilter):
    """Ticket arithmetic mean must fall within expected central bounds."""
    unique_id = "structural_average_value"
    display_name = "Arithmetic Mean / Average Value"
    tier = 1
    category = "Central Tendency"
    description = "Checks that the ticket arithmetic average falls within expected central boundaries."
    formula = "μ - 0.25·R ≤ Mean(X) ≤ μ + 0.25·R"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Arithmetic Average: Mean(X) = (1/k) * sum(x_i)        |\n"
        "| Expected Range    : Center +/- 25% of pool span       |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Mean(X)]\n"
        "    B --> C{Min Mean <= Mean <= Max Mean?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject Skewed Average]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        means = np.mean(combinations, axis=1)
        lo, hi = (1, 60) if rules is None else rules.number_range
        expected_mean = (lo + hi) / 2.0
        margin = (hi - lo) * 0.25
        return (means >= expected_mean - margin) & (means <= expected_mean + margin)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        mean_val = float(np.mean(comb_arr))
        lo, hi = (1, 60) if rules is None else rules.number_range
        expected_mean = (lo + hi) / 2.0
        margin = (hi - lo) * 0.25
        min_m, max_m = round(expected_mean - margin, 1), round(expected_mean + margin, 1)
        passed = min_m <= mean_val <= max_m
        gauge = format_gauge(mean_val, min_m, max_m, passed)
        summary = f"Arithmetic mean value is {mean_val:.2f} (allowed: {min_m}..{max_m}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(mean_val, 2),
            allowed_range=f"[{min_m}..{max_m}]",
            summary=summary,
            details={"mean": mean_val, "min_mean": min_m, "max_mean": max_m},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )
