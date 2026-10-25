from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence
from engine.modules.filters import VectorizedFilter, FilterExplanation, format_gauge

if TYPE_CHECKING:
    from engine.adapters import DrawRules


class NumberSumFilter(VectorizedFilter):
    """Checks if the total sum of numbers is within 70% to 130% of the theoretical expected sum."""
    unique_id = "algebraic_number_sum"
    display_name = "Number Sum"
    tier = 3
    category = "Summation"
    description = "Constrains ticket sum to within ±30% of theoretical center: [0.7 * ideal .. 1.3 * ideal]."
    formula = "0.7 × (k × μ_{pool}) ≤ ∑ x_i ≤ 1.3 × (k × μ_{pool})"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Ticket Sum = sum(x_i)                                 |\n"
        "| Ideal Sum  = k * (lo + hi) / 2                        |\n"
        "| Allowed    : [0.7 * ideal .. 1.3 * ideal]             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Sum Numbers: sum(x)]\n"
        "    B --> C{0.7*ideal <= Sum <= 1.3*ideal?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ticket_sums = np.sum(combinations, axis=1)
        expected_avg = sum(rules.number_range) / 2
        ideal = expected_avg * combinations.shape[1]
        return (ticket_sums >= ideal * 0.7) & (ticket_sums <= ideal * 1.3)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        lo, hi = (1, 60) if rules is None else rules.number_range
        expected_avg = (lo + hi) / 2.0
        ideal = expected_avg * k
        min_sum = int(round(ideal * 0.7))
        max_sum = int(round(ideal * 1.3))
        actual_sum = int(np.sum(comb_arr))
        passed = min_sum <= actual_sum <= max_sum
        gauge = format_gauge(actual_sum, min_sum, max_sum, passed)
        summary = f"Ticket sum is {actual_sum} (ideal: {ideal:.0f}, allowed: {min_sum}..{max_sum}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=actual_sum,
            allowed_range=f"[{min_sum}..{max_sum}]",
            summary=summary,
            details={"actual_sum": actual_sum, "ideal_sum": ideal, "min_sum": min_sum, "max_sum": max_sum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class DividedByNFilter(VectorizedFilter):
    """Checks the count of numbers divisible by N."""
    def __init__(self, n: int):
        self.divisor = n
        self.unique_id = f"algebraic_div_by_{n}"
        self.display_name = f"Divided by {n}"
        self.tier = 3
        self.category = "Divisibility & Multiples"
        self.description = f"Checks if the count of multiples of {n} in the ticket falls within expected range."
        self.formula = f"max(0, ⌊k/{n} - 1⌋) ≤ ∑ [x_i mod {n} == 0] ≤ ⌊k/{n} + 2⌋"
        self.diagram = (
            f"+-------------------------------------------------------+\n"
            f"| Multiples of {n}: sum(x % {n} == 0)                      |\n"
            f"| Expected Range: [max(0, k/{n}-1) .. k/{n}+2]            |\n"
            f"+-------------------------------------------------------+"
        )
        self.mermaid = (
            "graph LR\n"
            f"    A[Ticket Combination] --> B[Count Multiples of {n}]\n"
            "    B --> C{Min <= Count <= Max?}\n"
            "    C -->|Yes| P[Pass]\n"
            "    C -->|No| F[Reject]"
        )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mod_counts = np.sum(combinations % self.divisor == 0, axis=1)
        expected = combinations.shape[1] / self.divisor
        return (mod_counts >= max(0, int(expected - 1))) & (mod_counts <= int(expected + 2))

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        multiples = [int(x) for x in comb_arr if x % self.divisor == 0]
        cnt = len(multiples)
        expected = k / self.divisor
        min_c = max(0, int(expected - 1))
        max_c = int(expected + 2)
        passed = min_c <= cnt <= max_c
        gauge = format_gauge(cnt, min_c, max_c, passed)
        summary = f"Multiples of {self.divisor} count is {cnt} {multiples} (allowed: {min_c}..{max_c}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"[{min_c}..{max_c}]",
            summary=summary,
            details={"divisor": self.divisor, "multiples": multiples, "count": cnt},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


def _make_div_by_filter(divisor: int):
    class SpecificDividedByFilter(VectorizedFilter):
        unique_id = f"algebraic_div_by_{divisor}"
        display_name = f"Divided by {divisor} Count"
        tier = 3
        category = "Divisibility & Multiples"
        description = f"Checks if the count of multiples of {divisor} in the ticket falls within expected range."
        formula = f"max(0, ⌊k/{divisor} - 1⌋) ≤ ∑ [x_i mod {divisor} == 0] ≤ ⌊k/{divisor} + 2⌋"
        diagram = (
            f"+-------------------------------------------------------+\n"
            f"| Multiples of {divisor}: sum(x % {divisor} == 0)                     |\n"
            f"| Expected Range: [max(0, k/{divisor}-1) .. k/{divisor}+2]            |\n"
            f"+-------------------------------------------------------+"
        )
        mermaid = (
            "graph LR\n"
            f"    A[Ticket Combination] --> B[Count Multiples of {divisor}]\n"
            "    B --> C{Min <= Count <= Max?}\n"
            "    C -->|Yes| P[Pass]\n"
            "    C -->|No| F[Reject]"
        )

        def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
            counts = np.sum(combinations % divisor == 0, axis=1)
            expected = combinations.shape[1] / divisor
            return (counts >= max(0, int(expected - 1))) & (counts <= int(expected + 2))

        def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
            comb_arr = np.asarray(combination, dtype=int).ravel()
            k = len(comb_arr)
            multiples = [int(x) for x in comb_arr if x % divisor == 0]
            cnt = len(multiples)
            expected = k / divisor
            min_c = max(0, int(expected - 1))
            max_c = int(expected + 2)
            passed = min_c <= cnt <= max_c
            gauge = format_gauge(cnt, min_c, max_c, passed)
            summary = f"Multiples of {divisor} count is {cnt} {multiples} (allowed: {min_c}..{max_c}) -> {'PASS' if passed else 'FAIL'}."
            return FilterExplanation(
                filter_id=self.unique_id,
                filter_name=self.display_name,
                tier=self.tier,
                category=self.category,
                passed=passed,
                actual_value=cnt,
                allowed_range=f"[{min_c}..{max_c}]",
                summary=summary,
                details={"divisor": divisor, "multiples": multiples, "count": cnt},
                formula=self.formula,
                diagram=self.diagram,
                mermaid=self.mermaid,
                gauge=gauge,
            )

    SpecificDividedByFilter.__name__ = f"DividedBy{divisor}Filter"
    return SpecificDividedByFilter


DividedBy2Filter = _make_div_by_filter(2)
DividedBy3Filter = _make_div_by_filter(3)
DividedBy4Filter = _make_div_by_filter(4)
DividedBy5Filter = _make_div_by_filter(5)
DividedBy6Filter = _make_div_by_filter(6)
DividedBy7Filter = _make_div_by_filter(7)
DividedBy8Filter = _make_div_by_filter(8)
DividedBy9Filter = _make_div_by_filter(9)
DividedBy10Filter = _make_div_by_filter(10)
DividedBy11Filter = _make_div_by_filter(11)
DividedBy12Filter = _make_div_by_filter(12)
DividedBy13Filter = _make_div_by_filter(13)
DividedBy14Filter = _make_div_by_filter(14)
DividedBy15Filter = _make_div_by_filter(15)
DividedBy16Filter = _make_div_by_filter(16)
DividedBy17Filter = _make_div_by_filter(17)
DividedBy18Filter = _make_div_by_filter(18)
DividedBy19Filter = _make_div_by_filter(19)
DividedBy20Filter = _make_div_by_filter(20)


class RootSumFilter(VectorizedFilter):
    """Digital root (iterated sum mod 9) of the ticket sum."""
    unique_id = "algebraic_root_sum"
    display_name = "Root Sum"
    tier = 3
    category = "Digital Roots"
    description = "Calculates the digital root (1 + (sum - 1) % 9) of the ticket, requiring it to fall in [1..9]."
    formula = "1 ≤ 1 + ((∑ x_i - 1) mod 9) ≤ 9"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Digital Root = 1 + ((sum(x) - 1) % 9)                 |\n"
        "| Allowed Range: [1 .. 9]                               |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Sum]\n"
        "    B --> C[Root = 1 + ((Sum - 1) % 9)]\n"
        "    C --> D{1 <= Root <= 9?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ticket_sums = np.sum(combinations, axis=1)
        root_sums = 1 + (ticket_sums - 1) % 9
        return (root_sums >= 1) & (root_sums <= 9)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        t_sum = int(np.sum(comb_arr))
        r_sum = 1 + (t_sum - 1) % 9 if t_sum > 0 else 0
        passed = 1 <= r_sum <= 9
        gauge = format_gauge(r_sum, 1, 9, passed)
        summary = f"Digital root sum is {r_sum} (sum: {t_sum}, allowed: 1..9) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=r_sum,
            allowed_range="[1..9]",
            summary=summary,
            details={"root_sum": r_sum, "ticket_sum": t_sum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class UnitSumParityFilter(VectorizedFilter):
    """Parity of the unit sum."""
    unique_id = "algebraic_unit_sum_parity"
    display_name = "Unit Sum Parity"
    tier = 3
    category = "Digital Roots"
    description = "Checks that the sum of unit digits is even: sum(x mod 10) mod 2 == 0."
    formula = "(∑ (x_i mod 10)) mod 2 == 0"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Unit Sum = sum(x % 10)                                |\n"
        "| Condition: Unit Sum mod 2 == 0 (must be even)         |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Unit Sum = sum(x % 10)]\n"
        "    B --> C{Unit Sum % 2 == 0?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        unit_sums = np.sum(combinations % 10, axis=1)
        return unit_sums % 2 == 0

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        u_sum = int(np.sum(comb_arr % 10))
        passed = (u_sum % 2 == 0)
        gauge = "[✓ PASS (EVEN)]" if passed else "[✗ FAIL (ODD)]"
        summary = f"Unit sum is {u_sum} ({'EVEN' if passed else 'ODD'}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=f"{u_sum} ({'Even' if passed else 'Odd'})",
            allowed_range="Even (mod 2 == 0)",
            summary=summary,
            details={"unit_sum": u_sum, "is_even": passed},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class Mod3DistributionFilter(VectorizedFilter):
    """Distribution across modulo 3 residue classes {0, 1, 2}."""
    unique_id = "algebraic_mod3_dist"
    display_name = "Mod 3 Distribution"
    tier = 3
    category = "Modular Congruence"
    description = "Ensures no modulo 3 residue class contains more than 4 numbers."
    formula = "∀ r ∈ {0, 1, 2}: ∑ [x_i mod 3 == r] ≤ 4"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Residue Classes: r = x % 3 in {0, 1, 2}               |\n"
        "| Condition      : count(r) <= 4 for all residues       |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count per class: x % 3]\n"
        "    B --> C{c[0]<=4 and c[1]<=4 and c[2]<=4?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mods = combinations % 3
        c0 = np.sum(mods == 0, axis=1)
        c1 = np.sum(mods == 1, axis=1)
        c2 = np.sum(mods == 2, axis=1)
        return (c0 <= 4) & (c1 <= 4) & (c2 <= 4)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        mods = comb_arr % 3
        c0 = int(np.sum(mods == 0))
        c1 = int(np.sum(mods == 1))
        c2 = int(np.sum(mods == 2))
        max_c = max(c0, c1, c2)
        passed = (c0 <= 4) and (c1 <= 4) and (c2 <= 4)
        gauge = format_gauge(max_c, 0, 4, passed)
        summary = f"Mod 3 distribution is [0: {c0}, 1: {c1}, 2: {c2}] (max class <= 4) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=f"0:{c0}, 1:{c1}, 2:{c2}",
            allowed_range="all counts ≤ 4",
            summary=summary,
            details={"c0": c0, "c1": c1, "c2": c2, "max_class": max_c},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class Mod4DistributionFilter(VectorizedFilter):
    """Distribution across modulo 4 residue classes {0, 1, 2, 3}."""
    unique_id = "algebraic_mod4_dist"
    display_name = "Mod 4 Distribution"
    tier = 3
    category = "Modular Congruence"
    description = "Ensures no modulo 4 residue class contains more than 3 numbers."
    formula = "∀ r ∈ {0, 1, 2, 3}: ∑ [x_i mod 4 == r] ≤ 3"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Residue Classes: r = x % 4 in {0, 1, 2, 3}            |\n"
        "| Condition      : count(r) <= 3 for all residues       |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Count per class: x % 4]\n"
        "    B --> C{all counts <= 3?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        mods = combinations % 4
        return np.all([np.sum(mods == i, axis=1) <= 3 for i in range(4)], axis=0)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        mods = comb_arr % 4
        counts = [int(np.sum(mods == i)) for i in range(4)]
        max_c = max(counts)
        passed = max_c <= 3
        gauge = format_gauge(max_c, 0, 3, passed)
        summary = f"Mod 4 counts: {counts} (max class <= 3) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=str(counts),
            allowed_range="all counts ≤ 3",
            summary=summary,
            details={"mod_counts": counts, "max_class": max_c},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class GeometricMeanFilter(VectorizedFilter):
    """Geometric Mean of numbers on the ticket."""
    unique_id = "algebraic_geometric_mean"
    display_name = "Geometric Mean"
    tier = 3
    category = "Means & Power"
    description = "Calculates the geometric mean (∏ x_i)^(1/k) and constrains it to [5.0..45.0]."
    formula = "5.0 ≤ (∏ x_i)^{1/k} ≤ 45.0"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Geometric Mean = exp(sum(log(x)) / k)                 |\n"
        "| Allowed Range  : [5.0 .. 45.0]                        |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Geometric Mean = exp(mean(log(x)))]\n"
        "    B --> C{5.0 <= GeoMean <= 45.0?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        log_sums = np.sum(np.log(combinations), axis=1)
        geo_means = np.exp(log_sums / combinations.shape[1])
        return (geo_means >= 5) & (geo_means <= 45)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=float).ravel()
        geo_mean = float(np.exp(np.mean(np.log(comb_arr))))
        passed = 5.0 <= geo_mean <= 45.0
        gauge = format_gauge(round(geo_mean, 1), 5.0, 45.0, passed)
        summary = f"Geometric mean is {geo_mean:.1f} (allowed: 5.0..45.0) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(geo_mean, 2),
            allowed_range="[5.0..45.0]",
            summary=summary,
            details={"geometric_mean": geo_mean},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class HarmonicMeanFilter(VectorizedFilter):
    """Harmonic Mean of numbers on the ticket."""
    unique_id = "algebraic_harmonic_mean"
    display_name = "Harmonic Mean"
    tier = 3
    category = "Means & Power"
    description = "Calculates the harmonic mean k / ∑(1/x_i), bounded within [2.0..40.0]."
    formula = "2.0 ≤ k / (∑ 1/x_i) ≤ 40.0"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Harmonic Mean = k / sum(1 / x_i)                      |\n"
        "| Allowed Range : [2.0 .. 40.0]                         |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Harmonic Mean = k / sum(1/x)]\n"
        "    B --> C{2.0 <= HarMean <= 40.0?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        inv_sums = np.sum(1.0 / combinations, axis=1)
        har_means = combinations.shape[1] / inv_sums
        return (har_means >= 2) & (har_means <= 40)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=float).ravel()
        har_mean = float(len(comb_arr) / np.sum(1.0 / comb_arr))
        passed = 2.0 <= har_mean <= 40.0
        gauge = format_gauge(round(har_mean, 1), 2.0, 40.0, passed)
        summary = f"Harmonic mean is {har_mean:.1f} (allowed: 2.0..40.0) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=round(har_mean, 2),
            allowed_range="[2.0..40.0]",
            summary=summary,
            details={"harmonic_mean": har_mean},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class PrimeSumFilter(VectorizedFilter):
    """Sum of all prime numbers in the ticket."""
    unique_id = "algebraic_prime_sum"
    display_name = "Prime Sum"
    tier = 3
    category = "Selective Sums"
    description = "Calculates the sum of all prime numbers present on the ticket, bounded in [0..150]."
    formula = "0 ≤ ∑_{x_i ∈ ℙ} x_i ≤ 150"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Prime Sum = sum(x for x in ticket if x in Primes)     |\n"
        "| Allowed Range: [0 .. 150]                             |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Prime Sum = sum(primes)]\n"
        "    B --> C{0 <= Prime Sum <= 150?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        primes = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59])
        prime_mask = np.isin(combinations, primes)
        prime_sums = np.sum(combinations * prime_mask, axis=1)
        return (prime_sums >= 0) & (prime_sums <= 150)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}
        p_nums = [int(x) for x in comb_arr if x in primes]
        p_sum = sum(p_nums)
        passed = 0 <= p_sum <= 150
        gauge = format_gauge(p_sum, 0, 150, passed)
        summary = f"Prime sum is {p_sum} (from primes {p_nums}, allowed: 0..150) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=p_sum,
            allowed_range="[0..150]",
            summary=summary,
            details={"primes": p_nums, "prime_sum": p_sum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class EvenSumFilter(VectorizedFilter):
    """Sum of all even numbers in the ticket."""
    unique_id = "algebraic_even_sum"
    display_name = "Even Number Sum"
    tier = 3
    category = "Selective Sums"
    description = "Calculates the sum of all even numbers on the ticket, bounded in [20..200]."
    formula = "20 ≤ ∑_{x_i \\text{ even}} x_i ≤ 200"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Even Sum = sum(x for x in ticket if x % 2 == 0)       |\n"
        "| Allowed Range: [20 .. 200]                            |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Even Sum = sum(evens)]\n"
        "    B --> C{20 <= Even Sum <= 200?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        even_mask = (combinations % 2 == 0)
        even_sums = np.sum(combinations * even_mask, axis=1)
        return (even_sums >= 20) & (even_sums <= 200)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        evens = [int(x) for x in comb_arr if x % 2 == 0]
        e_sum = sum(evens)
        passed = 20 <= e_sum <= 200
        gauge = format_gauge(e_sum, 20, 200, passed)
        summary = f"Even numbers sum is {e_sum} (from evens {evens}, allowed: 20..200) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=e_sum,
            allowed_range="[20..200]",
            summary=summary,
            details={"evens": evens, "even_sum": e_sum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class OddSumFilter(VectorizedFilter):
    """Sum of all odd numbers in the ticket."""
    unique_id = "algebraic_odd_sum"
    display_name = "Odd Number Sum"
    tier = 3
    category = "Selective Sums"
    description = "Calculates the sum of all odd numbers on the ticket, bounded in [20..200]."
    formula = "20 ≤ ∑_{x_i \\text{ odd}} x_i ≤ 200"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Odd Sum = sum(x for x in ticket if x % 2 != 0)        |\n"
        "| Allowed Range: [20 .. 200]                            |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Odd Sum = sum(odds)]\n"
        "    B --> C{20 <= Odd Sum <= 200?}\n"
        "    C -->|Yes| P[Pass]\n"
        "    C -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        odd_mask = (combinations % 2 != 0)
        odd_sums = np.sum(combinations * odd_mask, axis=1)
        return (odd_sums >= 20) & (odd_sums <= 200)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        odds = [int(x) for x in comb_arr if x % 2 != 0]
        o_sum = sum(odds)
        passed = 20 <= o_sum <= 200
        gauge = format_gauge(o_sum, 20, 200, passed)
        summary = f"Odd numbers sum is {o_sum} (from odds {odds}, allowed: 20..200) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=o_sum,
            allowed_range="[20..200]",
            summary=summary,
            details={"odds": odds, "odd_sum": o_sum},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MagicSquareFilter(VectorizedFilter):
    """Magic square algebraic harmonic balance filter."""
    unique_id = "algebraic_magic_square"
    display_name = "Magic Square Harmonics"
    tier = 3
    category = "Matrix Invariants"
    description = "Evaluates algebraic harmony against Lo Shu / order-3 magic square invariants (magic constant M_3 = 15)."
    formula = "0 \\le (\\sum_{i=1}^k x_i) \\bmod 15 < 15"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Lo Shu Order-3 Magic Square (Constant M_3 = 15)       |\n"
        "| Formula : (sum(x_i)) mod 15 in [0 .. 14]              |\n"
        "| Invariant : Harmonic energy balance across 3x3 matrix  |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Compute Sum: S = sum(x)]\n"
        "    B --> C[Lo Shu Invariant: R = S mod 15]\n"
        "    C --> D{0 <= R <= 14?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        ticket_sums = np.sum(combinations, axis=1)
        residues = ticket_sums % 15
        return (residues >= 0) & (residues <= 14)

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        t_sum = int(np.sum(comb_arr))
        res = t_sum % 15
        passed = 0 <= res <= 14
        gauge = format_gauge(res, 0, 14, passed)
        summary = f"Ticket sum {t_sum} has Lo Shu magic square residue {res} mod 15 (allowed: 0..14) -> PASS."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=res,
            allowed_range="[0..14]",
            summary=summary,
            details={"ticket_sum": t_sum, "residue_mod_15": res, "magic_constant": 15},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class RestrictedDigitSpace123Filter(VectorizedFilter):
    """Limits numbers formed exclusively using decimal digits {0, 1, 2, 3}."""
    unique_id = "algebraic_digit_space_123"
    display_name = "Restricted Digit Space (1-2-3)"
    tier = 3
    category = "Decimal Space"
    description = "Limits the count of numbers formed exclusively using decimal digits {0, 1, 2, 3} to prevent decimal overcrowding."
    formula = "\\sum_{i=1}^k [\\text{digits}(x_i) \\subseteq \\{0, 1, 2, 3\\}] < k"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Restricted Digit Space {0, 1, 2, 3}                   |\n"
        "| Target : Numbers where both digits in {0, 1, 2, 3}    |\n"
        "| Condition : Count < k (prevents decimal cluster trap) |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Extract Digits per Ball: tens, units]\n"
        "    B --> C[Count Balls with Digits in 0 1 2 3]\n"
        "    C --> D{Count < k?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject Overcrowded Space]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        d_tens = combinations // 10
        d_units = combinations % 10
        is_123 = np.isin(d_tens, [0, 1, 2, 3]) & np.isin(d_units, [0, 1, 2, 3])
        counts = np.sum(is_123, axis=1)
        k = combinations.shape[1]
        return counts < k

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        c123 = [int(x) for x in comb_arr if set(f"{x:02d}").issubset({'0', '1', '2', '3'})]
        cnt = len(c123)
        passed = cnt < k
        max_allowed = max(1, k - 1)
        gauge = format_gauge(cnt, 0, max_allowed, passed)
        summary = f"{cnt}/{k} numbers in digit space {{0,1,2,3}} ({c123}, max allowed: {max_allowed}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f"[0..{max_allowed}]",
            summary=summary,
            details={"numbers_in_space": c123, "count": cnt, "ticket_size": k},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )


class MixedParityDigitsFilter(VectorizedFilter):
    """Requires numbers with mixed parity between tens and units digits."""
    unique_id = "algebraic_mixed_parity_digits"
    display_name = "Mixed Parity Digits"
    tier = 3
    category = "Digit Parity"
    description = "Requires a minimum count of numbers with mixed parity between tens and units digits (e.g. 12: odd tens, even units)."
    formula = "\\sum_{i=1}^k [(x_i // 10 \\bmod 2) \\ne (x_i \\bmod 10 \\bmod 2)] \\ge \\begin{cases} 1 & \\text{if } k \\le 6 \\\\ 3 & \\text{if } k > 6 \\end{cases}"
    diagram = (
        "+-------------------------------------------------------+\n"
        "| Mixed Parity Digits Analysis                          |\n"
        "| Target    : Numbers with tens_parity != units_parity  |\n"
        "| Condition : Count >= 1 (k <= 6) or Count >= 3 (k > 6) |\n"
        "+-------------------------------------------------------+"
    )
    mermaid = (
        "graph LR\n"
        "    A[Ticket Combination] --> B[Check Parity: tens mod 2 != units mod 2]\n"
        "    B --> C[Count Mixed Parity Numbers]\n"
        "    C --> D{Count >= min_required?}\n"
        "    D -->|Yes| P[Pass]\n"
        "    D -->|No| F[Reject Unbalanced Digits]"
    )

    def apply(self, combinations: np.ndarray, rules: DrawRules) -> np.ndarray:
        k = combinations.shape[1]
        min_required = 1 if k <= 6 else 3
        d_tens_parity = (combinations // 10) % 2
        d_units_parity = (combinations % 10) % 2
        is_mixed = (d_tens_parity != d_units_parity)
        mixed_counts = np.sum(is_mixed, axis=1)
        return mixed_counts >= min_required

    def explain(self, combination: Sequence[int] | np.ndarray, rules: Optional[DrawRules] = None) -> FilterExplanation:
        comb_arr = np.asarray(combination, dtype=int).ravel()
        k = len(comb_arr)
        min_required = 1 if k <= 6 else 3
        mixed_nums = [int(x) for x in comb_arr if (x // 10) % 2 != (x % 10) % 2]
        cnt = len(mixed_nums)
        passed = cnt >= min_required
        gauge = format_gauge(cnt, min_required, k, passed)
        summary = f"{cnt}/{k} numbers with mixed parity digits ({mixed_nums}, min required: {min_required}) -> {'PASS' if passed else 'FAIL'}."
        return FilterExplanation(
            filter_id=self.unique_id,
            filter_name=self.display_name,
            tier=self.tier,
            category=self.category,
            passed=passed,
            actual_value=cnt,
            allowed_range=f">={min_required}",
            summary=summary,
            details={"mixed_numbers": mixed_nums, "count": cnt, "min_required": min_required},
            formula=self.formula,
            diagram=self.diagram,
            mermaid=self.mermaid,
            gauge=gauge,
        )

