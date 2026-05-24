"""
Structural Harmony & Filter Engine ⚖️
====================================
Modular registry for lottery combination validators.
Supports K-of-N fault tolerance and dynamic parameter injection.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any, Callable, Dict, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from engine.adapters import DrawRules

# Type for a filter function: (ticket, rules, **kwargs) -> bool
FilterFunc = Callable[[List[int], 'DrawRules', Any], bool]

class FilterRegistry:
    def __init__(self):
        self._filters: Dict[str, FilterFunc] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, name: str, description: str = ""):
        def decorator(func: FilterFunc):
            self._filters[name] = func
            self._descriptions[name] = description
            return func
        return decorator

    def get(self, name: str) -> FilterFunc | None:
        return self._filters.get(name)

    def list_available(self) -> Set[str]:
        return set(self._filters.keys())

    def validate(
        self, 
        ticket: List[int], 
        rules: DrawRules, 
        active_filters: List[str], 
        k_of_n: int | None = None, 
        **kwargs: Any
    ) -> bool:
        if not active_filters:
            return True
            
        results = []
        for name in active_filters:
            func = self.get(name)
            if func:
                try:
                    results.append(func(ticket, rules, **kwargs))
                except Exception as e:
                    logging.debug(f"Filter '{name}' crashed: {e}")
                    results.append(True) # Fail open on logic error
            else:
                logging.warning(f"Unknown filter: {name}")

        if not results:
            return True
            
        if k_of_n:
            return sum(1 for r in results if r) >= k_of_n
        return all(results)

# Global singleton
registry = FilterRegistry()

# ── 1. Basic Statistical Filters ─────────────────────────────────────────────

@registry.register("sum_range", "Dynamic sum range check (30-40% tolerance)")
def filter_sum_range(ticket, rules, **kwargs):
    n_picked = len(ticket)
    lo, hi = rules.number_range
    expected_avg = (lo + hi) / 2
    ideal_sum = expected_avg * n_picked
    tolerance = 0.3 if n_picked == rules.pick_count else 0.4
    return ideal_sum * (1.0 - tolerance) <= sum(ticket) <= ideal_sum * (1.0 + tolerance)

@registry.register("parity", "Odd/Even distribution balance")
def filter_parity(ticket, rules, **kwargs):
    n_picked = len(ticket)
    odds = sum(1 for n in ticket if n % 2 != 0)
    if n_picked >= 10:
        return 0.2 * n_picked <= odds <= 0.8 * n_picked
    return 0 < odds < n_picked

@registry.register("breadth", "Numbers must span multiple decades")
def filter_breadth(ticket, rules, **kwargs):
    n_picked = len(ticket)
    decades = {n // 10 for n in ticket}
    min_decades = 3 if n_picked < 10 else 4
    return len(decades) >= min_decades

# ── 2. Howard Strategy Filters (Gail Howard delta) ───────────────────────────

@registry.register("no_consecutive", "Avoid long consecutive runs (4+)")
def filter_no_consecutive(ticket, rules, **kwargs):
    sorted_t = sorted(ticket)
    consecutive = 1
    max_c = 1
    for i in range(len(sorted_t) - 1):
        if sorted_t[i+1] == sorted_t[i] + 1:
            consecutive += 1
        else:
            max_c = max(max_c, consecutive)
            consecutive = 1
    max_c = max(max_c, consecutive)
    return max_c < 4

@registry.register("no_arithmetic", "Avoid arithmetic sequences (e.g. 2, 4, 6)")
def filter_no_arithmetic(ticket, rules, **kwargs):
    if len(ticket) < 3: return True
    sorted_t = sorted(ticket)
    for i in range(len(sorted_t) - 2):
        diff = sorted_t[i+1] - sorted_t[i]
        if diff > 1:
            if sorted_t[i+2] == sorted_t[i+1] + diff:
                return False
    return True

@registry.register("birthday_bias", "Avoid heavy clustering in 1-31 range")
def filter_birthday_bias(ticket, rules, **kwargs):
    n_picked = len(ticket)
    birthdays = sum(1 for n in ticket if n <= 31)
    limit = 4 if n_picked <= 6 else int(n_picked * 0.8)
    return not (birthdays >= limit and n_picked <= 31)

@registry.register("no_same_last_digit", "Avoid too many numbers with same last digit")
def filter_same_last_digit(ticket, rules, **kwargs):
    last_digits = [n % 10 for n in ticket]
    counts = Counter(last_digits)
    threshold = 3 if len(ticket) <= 10 else 5
    return not any(c >= threshold for c in counts.values())

# ── 3. Advanced Modules Integration ──────────────────────────────────────────

@registry.register("prime_count", "Balance of prime numbers")
def filter_prime_count(ticket, rules, **kwargs):
    from engine.modules import filters as f_mod
    target = kwargs.get("prime_count")
    p_count = f_mod.get_prime_count(ticket)
    if target is not None:
        return p_count == target
    return 1 <= p_count <= (3 if len(ticket) <= 6 else 7)

@registry.register("fibonacci_count", "Balance of Fibonacci numbers")
def filter_fibonacci_count(ticket, rules, **kwargs):
    target = kwargs.get("fibonacci_count")
    from engine.modules.patterns import get_fibonacci_in_set
    f_set = get_fibonacci_in_set(ticket)
    if target is not None:
        return len(f_set) == target
    return True # Passive check

@registry.register("magic_count", "Balance of 'Magic' numbers")
def filter_magic_count(ticket, rules, **kwargs):
    target = kwargs.get("magic_count")
    from engine.modules.patterns import get_magic_in_set
    m_set = get_magic_in_set(ticket)
    if target is not None:
        return len(m_set) == target
    return True

@registry.register("multiples_3_count", "Balance of multiples of 3")
def filter_multiples_3_count(ticket, rules, **kwargs):
    target = kwargs.get("multiples_3_count")
    from engine.modules.patterns import get_multiples_3_in_set
    m3_set = get_multiples_3_in_set(ticket)
    if target is not None:
        return len(m3_set) == target
    return True

@registry.register("density", "Frame/Center density ratio")
def filter_density(ticket, rules, **kwargs):
    density_param = kwargs.get("density")
    if not density_param: return True
    try:
        f_target, c_target = map(int, density_param.split(":"))
        from engine.modules.patterns import get_frame_center_logic
        cols = 5 if "lotofacil" in rules.name.lower() else 10
        res = get_frame_center_logic(ticket, cols=cols, max_n=rules.number_range[1])
        return len(res["frame"]) == f_target and len(res["center"]) == c_target
    except Exception:
        return True

@registry.register("ac_value", "Minimum Complexity (Arithmetic Complexity)")
def filter_ac_value(ticket, rules, **kwargs):
    from engine.modules import filters as f_mod
    ac = f_mod.get_ac_value(ticket)
    return ac >= (7 if len(ticket) == 6 else 10)

@registry.register("hot_cold", "Balance of hot and cold numbers")
def filter_hot_cold(ticket, rules, **kwargs):
    df_hist = kwargs.get("df")
    if df_hist is None: return True
    flat = [n for d in df_hist.tail(30)["numbers"] for n in d]
    counts = Counter(flat)
    n_pool = rules.number_range[1] - rules.number_range[0] + 1
    hot_set = set(sorted(counts, key=counts.get, reverse=True)[:n_pool // 4])
    hot_count = len(set(ticket) & hot_set)
    return hot_count >= (2 if len(ticket) <= 6 else 4)

@registry.register("no_historical_dupes", "Ticket must not be an exact duplicate of any past draw")
def filter_no_dupes(ticket, rules, **kwargs):
    df_hist = kwargs.get("df")
    if df_hist is None: return True
    t_set = set(ticket)
    return not any(t_set == set(prev) for prev in df_hist["numbers"])

@registry.register("pos_1_low", "First number must be in the lower 25% of the pool")
def filter_pos_1(ticket, rules, **kwargs):
    lo, hi = rules.number_range
    return sorted(ticket)[0] <= (hi - lo) * 0.25 + lo

@registry.register("pos_last_high", "Last number must be in the upper 25% of the pool")
def filter_pos_last(ticket, rules, **kwargs):
    lo, hi = rules.number_range
    return sorted(ticket)[-1] >= hi - (hi - lo) * 0.25

# ── 4. SamLotto Advanced Metrics ─────────────────────────────────────────────

@registry.register("high_low_sums", "Sum of High vs Low numbers")
def filter_high_low_sums(ticket, rules, **kwargs):
    lo, hi = rules.number_range
    mid = (lo + hi) / 2
    highs = [n for n in ticket if n > mid]
    lows = [n for n in ticket if n <= mid]
    h_sum, l_sum = sum(highs), sum(lows)
    # Heuristic: neither sum should be 0 unless it's a very small pick
    if len(ticket) > 5:
        return h_sum > 0 and l_sum > 0
    return True

@registry.register("odd_even_sums", "Sum of Odd vs Even numbers")
def filter_odd_even_sums(ticket, rules, **kwargs):
    odds = [n for n in ticket if n % 2 != 0]
    evens = [n for n in ticket if n % 2 == 0]
    o_sum, e_sum = sum(odds), sum(evens)
    if len(ticket) > 5:
        return o_sum > 0 and e_sum > 0
    return True

@registry.register("prime_sum", "Total sum of prime numbers in combination")
def filter_prime_sum(ticket, rules, **kwargs):
    from engine.modules.filters import get_prime_count
    # This filter is usually a range check, we'll ensure it's not 0 for large picks
    primes = [n for n in ticket if n in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}]
    p_sum = sum(primes)
    return p_sum > 0 if len(ticket) > 6 else True

@registry.register("successive_2", "Count of groups of 2 consecutive numbers")
def filter_successive_2(ticket, rules, **kwargs):
    from engine.modules.filters import get_successive_metrics
    return get_successive_metrics(ticket)["groups_of_2"] <= (2 if len(ticket) <= 6 else 4)

@registry.register("successive_3", "Count of groups of 3 consecutive numbers")
def filter_successive_3(ticket, rules, **kwargs):
    from engine.modules.filters import get_successive_metrics
    return get_successive_metrics(ticket)["groups_of_3"] <= 1

@registry.register("successive_4", "Count of groups of 4 consecutive numbers")
def filter_successive_4(ticket, rules, **kwargs):
    from engine.modules.filters import get_successive_metrics
    return get_successive_metrics(ticket)["groups_of_4"] == 0

# ── 5. Modular Remainder & Multiple Filters ──────────────────────────────────

@registry.register("remainders", "Count of numbers for specific divisors (Divided by 3..10)")
def filter_remainders(ticket, rules, **kwargs):
    divisor = kwargs.get("remainder_divisor", 3)
    target_rem = kwargs.get("remainder_target", 0)
    limit_min = kwargs.get("remainder_min", 0)
    limit_max = kwargs.get("remainder_max", rules.pick_count)
    
    count = sum(1 for n in ticket if n % divisor == target_rem)
    return limit_min <= count <= limit_max

@registry.register("multiples", "Count of numbers being multiples of X")
def filter_multiples(ticket, rules, **kwargs):
    divisor = kwargs.get("multiple_of", 3)
    limit_min = kwargs.get("multiple_min", 0)
    limit_max = kwargs.get("multiple_max", rules.pick_count)
    
    count = sum(1 for n in ticket if n % divisor == 0)
    return limit_min <= count <= limit_max

@registry.register("must_contain", "Ticket must contain specific numbers")
def filter_must_contain(ticket, rules, **kwargs):
    required = kwargs.get("must_contain_list")
    if not required: return True
    t_set = set(ticket)
    return all(n in t_set for n in required)

@registry.register("max_skips", "No number in ticket can exceed X historical skips (avoid deep cold)")
def filter_max_skips(ticket, rules, **kwargs):
    df_hist = kwargs.get("df")
    if df_hist is None or df_hist.empty: return True
    max_allowed = kwargs.get("max_skip_threshold", 50)
    
    # Calculate current skips for all numbers in the ticket
    last_id = df_hist.iloc[-1]["draw_id"]
    for n in ticket:
        # Find last draw containing n
        mask = df_hist["numbers"].apply(lambda x: n in x)
        if not mask.any():
            # Never appeared in history? Treat as high skip
            current_skip = len(df_hist)
        else:
            last_hit_id = df_hist[mask].iloc[-1]["draw_id"]
            current_skip = last_id - last_hit_id
            
        if current_skip > max_allowed:
            return False
    return True

# ── 6. Gap & Distance Metrics ────────────────────────────────────────────────

@registry.register("unit_different", "Count of distinct end-units (0-9)")
def filter_unit_different(ticket, rules, **kwargs):
    units = {n % 10 for n in ticket}
    return len(units) >= (4 if len(ticket) <= 6 else 6)

@registry.register("first_last_distance", "Difference between highest and lowest number")
def filter_first_last_distance(ticket, rules, **kwargs):
    sorted_t = sorted(ticket)
    dist = sorted_t[-1] - sorted_t[0]
    lo, hi = rules.number_range
    # Heuristic: distance should usually be > 50% of pool range
    return dist >= (hi - lo) * 0.5

@registry.register("max_distance", "Maximum gap between adjacent numbers in ticket")
def filter_max_distance(ticket, rules, **kwargs):
    sorted_t = sorted(ticket)
    gaps = [sorted_t[i+1] - sorted_t[i] for i in range(len(sorted_t)-1)]
    return max(gaps) <= (rules.number_range[1] - rules.number_range[0]) // 2

@registry.register("avg_distance", "Average gap between adjacent numbers")
def filter_avg_distance(ticket, rules, **kwargs):
    sorted_t = sorted(ticket)
    gaps = [sorted_t[i+1] - sorted_t[i] for i in range(len(sorted_t)-1)]
    avg = sum(gaps) / len(gaps)
    ideal = (rules.number_range[1] - rules.number_range[0]) / len(ticket)
    return ideal * 0.5 <= avg <= ideal * 1.5

# ── 7. Graph Connectivity & Clusters ─────────────────────────────────────────

def _count_groups(values: List[int], is_cyclic: bool = False, max_val: int = 10) -> int:
    """Helper to count connected components in a set of integers."""
    if not values: return 0
    s_vals = sorted(list(set(values)))
    groups = 1
    for i in range(len(s_vals) - 1):
        if s_vals[i+1] > s_vals[i] + 1:
            groups += 1
            
    # Cyclic check for unit digits (9 and 0 are adjacent)
    if is_cyclic and groups > 1:
        if 0 in s_vals and (max_val - 1) in s_vals:
            # Check if 0 and max_val-1 are part of different 'linear' groups
            # This is a simplification but usually correct for units
            groups -= 1
    return groups

@registry.register("decade_groups", "Count of contiguous decade sequences (0s, 10s, 20s...)")
def filter_decade_groups(ticket, rules, **kwargs):
    decades = [n // 10 for n in ticket]
    groups = _count_groups(decades, is_cyclic=False)
    # Typical winners have 2-4 groups
    return 1 <= groups <= (4 if len(ticket) <= 6 else 6)

@registry.register("unit_groups", "Count of contiguous unit-digit sequences (9 and 0 are adjacent)")
def filter_unit_groups(ticket, rules, **kwargs):
    units = [n % 10 for n in ticket]
    groups = _count_groups(units, is_cyclic=True, max_val=10)
    return 1 <= groups <= (4 if len(ticket) <= 6 else 6)

# ── 8. Digital & Modular Succession ──────────────────────────────────────────

@registry.register("mixed_parity_digits", "Count of numbers with mixed parity in their digits (e.g. 12)")
def filter_mixed_parity_digits(ticket, rules, **kwargs):
    mixed = 0
    for n in ticket:
        d1, d2 = n // 10, n % 10
        if d1 % 2 != d2 % 2: mixed += 1
    return mixed >= (1 if len(ticket) <= 6 else 3)

@registry.register("digit_space_123", "Count of numbers formed using only digits {0,1,2,3}")
def filter_digit_space_123(ticket, rules, **kwargs):
    allowed = {0, 1, 2, 3}
    count = 0
    for n in ticket:
        digits = {int(d) for d in str(n)}
        if n < 10: digits.add(0)
        if digits.issubset(allowed): count += 1
    return count < len(ticket)

@registry.register("successive_end_units", "Maximum sequence of successive end-units (modular succession)")
def filter_successive_end_units(ticket, rules, **kwargs):
    units = sorted(list(set(n % 10 for n in ticket)))
    if not units: return True
    max_c = 1
    curr_c = 1
    for i in range(len(units) - 1):
        if units[i+1] == units[i] + 1:
            curr_c += 1
        else:
            max_c = max(max_c, curr_c)
            curr_c = 1
    max_c = max(max_c, curr_c)
    return max_c < (4 if len(ticket) <= 6 else 6)
