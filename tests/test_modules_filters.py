"""
Tests for the engine.modules.filters module.
"""

import pytest
from engine.modules import filters

def test_get_odd_even_count():
    nums = [1, 2, 3, 4, 5, 6]
    assert filters.get_odd_count(nums) == 3
    assert filters.get_even_count(nums) == 3

def test_get_high_low_counts():
    nums = [1, 10, 20, 31, 40, 50]
    # pool_size = 60, mid = 30
    counts = filters.get_high_low_counts(nums, 60)
    assert counts["low"] == 3
    assert counts["high"] == 3

def test_get_prime_composite_count():
    nums = [2, 3, 4, 5, 6, 7]
    assert filters.get_prime_count(nums) == 4 # 2, 3, 5, 7
    assert filters.get_composite_count(nums) == 2 # 4, 6

def test_get_average_value():
    assert filters.get_average_value([10, 20, 30]) == 20.0
    assert filters.get_average_value([]) == 0.0

def test_get_unit_metrics():
    nums = [12, 23, 34]
    metrics = filters.get_unit_metrics(nums)
    assert metrics["sum"] == 2 + 3 + 4
    assert metrics["different"] == 3
    assert metrics["units"] == [2, 3, 4]

def test_get_successive_metrics():
    nums = [1, 2, 10, 11, 12, 20]
    metrics = filters.get_successive_metrics(nums)
    assert metrics["max_successive"] == 3 # 10, 11, 12
    assert metrics["groups"] == 2 # (1,2) and (10,11,12)

def test_get_distance_metrics():
    nums = [1, 5, 10]
    metrics = filters.get_distance_metrics(nums)
    # gaps: [4, 5]
    assert metrics["min"] == 4
    assert metrics["max"] == 5
    assert metrics["avg"] == 4.5
    assert metrics["different"] == 2
    assert metrics["spread"] == 9

def test_get_ac_value():
    # Example from some source: [3, 11, 12, 14, 21, 26]
    # Diffs:
    # 11-3=8, 12-3=9, 14-3=11, 21-3=18, 26-3=23
    # 12-11=1, 14-11=3, 21-11=10, 26-11=15
    # 14-12=2, 21-12=9 (repeat), 26-12=14
    # 21-14=7, 26-14=12 (repeat)
    # 26-21=5
    # Unique diffs: {8, 9, 11, 18, 23, 1, 3, 10, 15, 2, 14, 7, 12, 5}
    # Count: 14
    # AC = 14 - (6 - 1) = 9
    nums = [3, 11, 12, 14, 21, 26]
    assert filters.get_ac_value(nums) == 9

def test_get_root_sum():
    assert filters.get_root_sum([12, 34, 56]) == 3 # 1+2+3+4+5+6 = 21 -> 2+1 = 3

def test_get_decade_metrics():
    nums = [1, 5, 12, 25, 33, 50]
    metrics = filters.get_decade_metrics(nums)
    assert metrics["different"] == 5 # 0, 1, 2, 3, 5
    # sorted_decades: [0, 1, 2, 3, 5]
    # (0,1,2,3) is one group of adjacent decades. (5) is another.
    assert metrics["groups"] == 2

def test_get_advanced_sums():
    nums = [1, 10, 20, 31, 40, 50]
    # pool_size = 60, mid = 30
    sums = filters.get_advanced_sums(nums, 60)
    assert sums["high"] == 31 + 40 + 50
    assert sums["low"] == 1 + 10 + 20

def test_get_exact_successive_counts():
    nums = [1, 2, 5, 6, 7, 10]
    counts = filters.get_exact_successive_counts(nums)
    assert counts[2] == 1 # (1,2)
    assert counts[3] == 1 # (5,6,7)
    assert counts[4] == 0

def test_get_modulo_distribution():
    nums = [1, 11, 21, 5, 15]
    dist = filters.get_modulo_distribution(nums, 10)
    assert dist[1] == 3
    assert dist[5] == 2

def test_get_multiples_count():
    nums = [7, 14, 21, 5, 10]
    assert filters.get_multiples_count(nums, 7) == 3
    assert filters.get_multiples_count(nums, 5) == 2

def test_get_successive_end_units():
    nums = [1, 12, 23, 5, 16]
    # units: [1, 2, 3, 5, 6]
    # successive: (1,2,3) -> 3, (5,6) -> 2
    assert filters.get_successive_end_units(nums) == 3

def test_get_digit_parity_pairs():
    # 12: d1=1 (O), d2=2 (E) -> Mixed
    # 24: d1=2 (E), d2=4 (E) -> Even Only
    # 13: d1=1 (O), d2=3 (O) -> Odd Only
    nums = [12, 24, 13]
    metrics = filters.get_digit_parity_pairs(nums)
    assert metrics["mixed"] == 1
    assert metrics["even_only"] == 1
    assert metrics["odd_only"] == 1

def test_get_restricted_digit_space_count():
    # allowed: {0, 1, 2}
    # 1: 01 -> {0, 1} (Yes)
    # 12: {1, 2} (Yes)
    # 23: {2, 3} (No)
    nums = [1, 12, 23]
    assert filters.get_restricted_digit_space_count(nums, {0, 1, 2}) == 2
