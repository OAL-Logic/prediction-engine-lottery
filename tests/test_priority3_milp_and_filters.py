import numpy as np
import pytest
from itertools import combinations
from engine.adapters import DrawRules
from engine.modules.wheels_wrg import WheelingEngine
from engine.modules.filters.tier4_historical import HistoricalSumRangeFilter


def test_wheeling_engine_milp_reduction():
    # 10 numbers pool, ticket size 6, guarantee 4-if-6
    n, k, t, m = 10, 6, 4, 6
    we = WheelingEngine(n, k)
    tickets = np.array(list(combinations(range(1, n + 1), k)))

    reduced_milp = we.reduce_tickets_milp(tickets, t=t, m=m)
    assert len(reduced_milp) > 0
    assert len(reduced_milp) <= len(tickets)
    # Coverage verification
    coverage = we.evaluate_coverage(reduced_milp, t=t, m=m)
    assert coverage == 1.0


def test_historical_sum_range_filter_hypergeometric_bounds():
    # Test for Mega-Sena: 6 numbers from 1 to 60 (mean = 183.0)
    rules_mega = DrawRules(
        name="test_mega",
        pick_count=6,
        number_range=(1, 60),
    )
    filter_inst = HistoricalSumRangeFilter()

    # Valid balanced ticket
    valid_comb = np.array([[6, 14, 27, 34, 43, 58]])  # sum = 182
    passed = filter_inst.apply(valid_comb, rules_mega)
    assert passed[0] == True

    # Extreme invalid tickets (sum 21 or sum 345)
    invalid_low = np.array([[1, 2, 3, 4, 5, 6]])  # sum = 21
    invalid_high = np.array([[55, 56, 57, 58, 59, 60]])  # sum = 345
    assert filter_inst.apply(invalid_low, rules_mega)[0] == False
    assert filter_inst.apply(invalid_high, rules_mega)[0] == False
