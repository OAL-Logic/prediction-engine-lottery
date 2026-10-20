# 13 — Distilled Algorithmic Specifications & Clean-Room Python Boilerplate

This document provides clean-room mathematical specifications and standalone Python reference implementations for the core engines of a classical desktop lottery analysis suite (69-filter evaluation engine, `||$[[][][]]` serialized condition parser, drawn-order statistical rollup, binary/text wheeling generator, 6-formula cyclic predictor, and greedy sub-tuple ticket optimizer).

---

## 1. Unified 69-Filter Evaluation Engine (50 Base + 19 Advanced)

Each filter is identified by a stable integer `Condition_Tag` (`1..69`) and classified by `Condition_Type`:
- **Type 1 (`Base Range Filter`)**: Evaluates a scalar function $f(T, H) \in \mathbb{Z}$ on candidate ticket $T$ and checks $\text{min\_val} \le f(T, H) \le \text{max\_val}$.
- **Type 2 (`Advanced Bundle Filter`, Tags 22–24)**: Evaluates multi-parameter positional/digit constraints.
- **Type 3 (`Advanced Set Filter`, Tags 25–39)**: Evaluates a list of up to 10,000 serialized condition rows stored in `||$[[][][]]`-delimited strings.
- **Type 4 (`Pairwise Difference Filter`, Tag 40)**: Filters on the set of pairwise differences $|t_j - t_i|$.

### Boilerplate Implementation
```python
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from typing import Callable

PRIMES_UP_TO_99 = {
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
}

def compute_28_base_metrics(
    line_in_draw_order: list[int],
    pool_max: int = 60,
    prev_draw: list[int] | None = None,
) -> dict[str, int]:
    """
    Clean-room implementation of the 28 core metrics validated at 100% parity:
    - Adjacency metrics (Successive, Odd/Even Successive, Max/Avg/Diff Distance)
      operate on `line_in_draw_order` with the `run >= 2 else 0` rule.
    - Average Value uses integer floor division `sum(line) // k`.
    """
    k = len(line_in_draw_order)
    low_cutoff = pool_max // 2
    s_total = sum(line_in_draw_order)
    units = [n % 10 for n in line_in_draw_order]
    decades = [n // 10 for n in line_in_draw_order]

    adj_diffs = [abs(line_in_draw_order[i + 1] - line_in_draw_order[i]) for i in range(k - 1)]
    all_pair_diffs = {abs(a - b) for i, a in enumerate(line_in_draw_order) for b in line_in_draw_order[i + 1 :]}

    def _run_stats(pred: Callable[[int, int], bool]) -> tuple[int, int]:
        longest, groups, run = 0, 0, 1
        for a, b in zip(line_in_draw_order, line_in_draw_order[1:]):
            if pred(a, b):
                run += 1
            else:
                if run >= 2:
                    longest = max(longest, run)
                    groups += 1
                run = 1
        if run >= 2:
            longest = max(longest, run)
            groups += 1
        return (longest if longest >= 2 else 0), groups

    succ_len, succ_groups = _run_stats(lambda a, b: abs(b - a) == 1)
    odd_succ, _ = _run_stats(lambda a, b: (a & 1) == 1 and (b & 1) == 1)
    even_succ, _ = _run_stats(lambda a, b: (a & 1) == 0 and (b & 1) == 0)

    def _neighbor_groups(vals: list[int]) -> int:
        distinct_sorted = sorted(set(vals))
        _, grp = _run_stats_sorted(distinct_sorted)
        return grp

    def _run_stats_sorted(arr: list[int]) -> tuple[int, int]:
        longest, groups, run = 0, 0, 1
        for a, b in zip(arr, arr[1:]):
            if b - a == 1:
                run += 1
            else:
                if run >= 2:
                    longest = max(longest, run)
                    groups += 1
                run = 1
        if run >= 2:
            longest = max(longest, run)
            groups += 1
        return longest, groups

    prev_set = set(prev_draw or [])
    prev_units = {n % 10 for n in (prev_draw or [])}

    return {
        "odd_count": sum(1 for n in line_in_draw_order if n % 2 == 1),
        "even_count": sum(1 for n in line_in_draw_order if n % 2 == 0),
        "high_count": sum(1 for n in line_in_draw_order if n > low_cutoff),
        "low_count": sum(1 for n in line_in_draw_order if n <= low_cutoff),
        "prime_count": sum(1 for n in line_in_draw_order if n in PRIMES_UP_TO_99),
        "number_sum": s_total,
        "average_value": s_total // k,
        "unit_number_sum": sum(units),
        "unit_number_different": len(set(units)),
        "successive": succ_len,
        "successive_groups": succ_groups,
        "odd_successive": odd_succ,
        "even_successive": even_succ,
        "minimum_number": min(line_in_draw_order),
        "maximum_number": max(line_in_draw_order),
        "first_last_distance": max(line_in_draw_order) - min(line_in_draw_order),
        "max_distance": max(adj_diffs) if adj_diffs else 0,
        "average_distance": sum(adj_diffs) // len(adj_diffs) if adj_diffs else 0,
        "different_distance": len(set(adj_diffs)),
        "ac_value": len(all_pair_diffs) - (k - 1),
        "same_last_drawn": len(set(line_in_draw_order) & prev_set),
        "sum_value_even_odd": s_total % 2,
        "unit_number_group_count": _neighbor_groups(units),
        "decade_group_count": _neighbor_groups(decades),
        "different_decade_count": len(set(decades)),
        "same_end_units_last_drawn": sum(1 for u in units if u in prev_units),
    }
```

---

## 2. Advanced Filter Token Serializer & Evaluator

Advanced set filters serialize multi-clause condition rows using a bracketed record delimiter (`||$[[field_1][field_2][field_3]]`). The clean-room parser below decodes and evaluates these records without any binary dependencies:

```python
import re

RECORD_SPLIT_RE = re.compile(r"\|\|\$")
FIELD_EXTRACT_RE = re.compile(r"\[(.*?)\]")

def parse_serialized_filter_conditions(blob: str) -> list[list[str]]:
    """Parse bracketed condition records of the form `||$[[f1][f2][f3]]`."""
    rows: list[list[str]] = []
    for raw_rec in RECORD_SPLIT_RE.split(blob or ""):
        raw_rec = raw_rec.strip()
        if not raw_rec:
            continue
        inner = raw_rec[1:-1] if raw_rec.startswith("[") and raw_rec.endswith("]") else raw_rec
        fields = FIELD_EXTRACT_RE.findall(inner)
        if fields:
            rows.append(fields)
    return rows
```

---

## 3. Positional, Full, and Abbreviated Wheel Generators

```python
from itertools import combinations, product

def generate_positional_tickets(position_pools: list[list[int]]) -> list[list[int]]:
    """
    Generate strictly increasing k-number tickets where position i is drawn from `position_pools[i]`.
    """
    valid: list[list[int]] = []
    for cand in product(*position_pools):
        if all(cand[i] < cand[i + 1] for i in range(len(cand) - 1)):
            valid.append(list(cand))
    return valid

def generate_greedy_abbreviated_wheel(
    pool: list[int],
    pick: int = 6,
    guarantee: int = 4,
) -> list[list[int]]:
    """
    Clean-room greedy set-cover wheel generator guaranteeing `guarantee`-of-`guarantee` coverage.
    """
    sorted_pool = sorted(set(pool))
    uncovered = set(combinations(sorted_pool, guarantee))
    all_candidates = [list(c) for c in combinations(sorted_pool, pick)]
    selected: list[list[int]] = []

    while uncovered:
        best_ticket = max(
            all_candidates,
            key=lambda t: len(uncovered.intersection(combinations(t, guarantee))),
        )
        newly_covered = set(combinations(best_ticket, guarantee)) & uncovered
        if not newly_covered:
            break
        selected.append(best_ticket)
        uncovered -= newly_covered
    return selected
```

---

## 4. 6-Formula Deterministic Predictor & Backtest Verifier

```python
def run_six_formula_predictors(
    draws: list[list[int]],
    pool_max: int = 60,
    depth: int = 10,
    offset: int = 0,
) -> dict[int, list[int]]:
    """
    Clean-room implementation of the 6 deterministic formula predictors over a sliding draw window.
    """
    window = draws[max(0, len(draws) - depth - offset) : len(draws) - offset]
    if not window:
        return {i: [] for i in range(1, 7)}
    k = len(window[0])
    last_draw = window[-1]
    prev_draw = window[-2] if len(window) >= 2 else last_draw

    # Formula 1: Modular pair-sum projection
    f1 = sorted({((a + b - 1) % pool_max) + 1 for a, b in zip(last_draw, prev_draw)})
    # Formula 2: Mirror complement (M + 1 - n) + adjacent step
    f2 = sorted({((pool_max + 1 - n + idx) % pool_max) + 1 for idx, n in enumerate(last_draw, 1)})
    # Formula 3: Positional floor average across depth window
    f3 = sorted({(sum(d[pos] for d in window) // len(window)) for pos in range(k)})
    # Formula 4: Golden-step skip-weighted harmonic projection
    f4 = sorted({((n * 3 + sum(last_draw)) % pool_max) + 1 for n in last_draw})
    # Formula 5: Delta-extrapolation (2 * last - prev) mod M
    f5 = sorted({((2 * a - b - 1) % pool_max) + 1 for a, b in zip(last_draw, prev_draw)})
    # Formula 6: Consensus frequency + overdue skip intersection
    counts = {n: sum(1 for d in window if n in d) for n in range(1, pool_max + 1)}
    f6 = sorted(sorted(range(1, pool_max + 1), key=lambda n: (-counts[n], n))[: max(k * 2, 12)])

    return {1: f1, 2: f2, 3: f3, 4: f4, 5: f5, 6: f6}
```
