"""
Tests for the engine.modules.patterns module.
"""

import pytest
from engine.modules import patterns

def test_get_primes_fibonacci_in_set():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 13]
    assert patterns.get_primes_in_set(nums) == [2, 3, 5, 7, 13]
    assert patterns.get_fibonacci_in_set(nums) == [1, 2, 3, 5, 8, 13]

def test_get_frame_center_logic():
    # 10x6 board (1-60)
    # Row 1: 1-10
    # Row 6: 51-60
    # Col 1: 1, 11, 21, 31, 41, 51
    # Col 10: 10, 20, 30, 40, 50, 60
    nums = [1, 11, 51, 60, 25, 34]
    # Frame: 1, 11, 51, 60
    # Center: 25, 34
    res = patterns.get_frame_center_logic(nums, cols=10, max_n=60)
    assert set(res["frame"]) == {1, 11, 51, 60}
    assert set(res["center"]) == {25, 34}

def test_get_line_column_distribution():
    nums = [1, 2, 11, 21, 22]
    # 1, 2 -> Row 1
    # 11 -> Row 2
    # 21, 22 -> Row 3
    # 1, 11, 21 -> Col 1
    # 2, 22 -> Col 2
    res = patterns.get_line_column_distribution(nums, cols=10)
    assert res["rows"][1] == 2
    assert res["rows"][2] == 1
    assert res["rows"][3] == 2
    assert res["cols"][1] == 3
    assert res["cols"][2] == 2

def test_get_pattern_string():
    nums = [1, 2, 11, 21, 22]
    # Rows: 1:2, 2:1, 3:2, 4:0, 5:0, 6:0
    # Pattern: 2-1-2-0-0-0
    s = patterns.get_pattern_string(nums, cols=10, max_n=60)
    assert s == "2-1-2-0-0-0"

def test_analyze_voids():
    draws = [
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
    ]
    # Only Row 1 and Cols 1-6 are hit.
    # Rows 2-6 and Cols 7-10 are voids.
    res = patterns.analyze_voids(draws, cols=10, max_n=60, window=5)
    assert 2 in res["cold_rows"]
    assert 6 in res["cold_rows"]
    assert 7 in res["cold_cols"]
    assert 10 in res["cold_cols"]
    assert 1 not in res["cold_rows"]
    assert 1 not in res["cold_cols"]

def test_analyze_cycle():
    total_range = list(range(1, 4)) # Small pool for testing
    draws = [
        [1, 2],
        [2, 3], # Cycle 1 complete (1,2,3) at index 1
        [1],
        [2],
        [3], # Cycle 2 complete at index 4
        [1, 2]
    ]
    res = patterns.analyze_cycle(draws, total_range)
    assert len(res["completed_cycles"]) == 2
    assert res["completed_cycles"][0]["length"] == 2
    assert res["completed_cycles"][1]["length"] == 3
    assert res["current_cycle_progress"] == 2/3
    assert res["missing_in_current"] == [3]

def test_get_z_score():
    assert patterns.get_z_score(10, 5, 2) == 2.5
    assert patterns.get_z_score(10, 10, 0) == 0.0
