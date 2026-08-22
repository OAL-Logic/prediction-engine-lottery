import pandas as pd
import numpy as np
from engine.modules.skips import compute_skip_profile

def test_compute_skip_profile_empty():
    df = pd.DataFrame(columns=["draw_id", "numbers"])
    res = compute_skip_profile(df, 7)
    assert res["number"] == 7
    assert res["actual_skips"] == []
    assert res["average_skip"] == 0.0
    assert res["now_skip"] == 0
    assert res["total_draws"] == 0
    assert res["draw_ids"] == []

def test_compute_skip_profile_no_hits():
    df = pd.DataFrame([
        {"draw_id": 1, "numbers": [1, 2, 3, 4, 5, 6]},
        {"draw_id": 2, "numbers": [8, 9, 10, 11, 12, 13]}
    ])
    res = compute_skip_profile(df, 7)
    assert res["number"] == 7
    assert res["actual_skips"] == []
    assert res["average_skip"] == 2.0
    assert res["now_skip"] == 2
    assert res["total_draws"] == 2
    assert res["draw_ids"] == []

def test_compute_skip_profile_with_hits():
    df = pd.DataFrame([
        {"draw_id": 10, "numbers": [1, 2, 7, 4, 5, 6]},  # appearance 1 (index 0)
        {"draw_id": 11, "numbers": [8, 9, 10, 11, 12, 13]}, # gap = 0 (index 1)
        {"draw_id": 12, "numbers": [8, 9, 10, 11, 12, 13]}, # gap = 1
        {"draw_id": 13, "numbers": [1, 2, 7, 4, 5, 6]},  # appearance 2 (index 3)
        {"draw_id": 14, "numbers": [8, 9, 10, 11, 12, 13]}, # gap = 0
        {"draw_id": 15, "numbers": [8, 9, 10, 11, 12, 13]}, # gap = 1
        {"draw_id": 16, "numbers": [8, 9, 10, 11, 12, 13]}, # gap = 2
        {"draw_id": 17, "numbers": [1, 2, 7, 4, 5, 6]},  # appearance 3 (index 7)
        {"draw_id": 18, "numbers": [8, 9, 10, 11, 12, 13]}  # now_skip = 1
    ])
    res = compute_skip_profile(df, 7)
    assert res["number"] == 7
    # appearances at indices 0, 3, 7.
    # gaps between appearances:
    # 3 - 0 - 1 = 2 (draws 11, 12)
    # 7 - 3 - 1 = 3 (draws 14, 15, 16)
    assert res["actual_skips"] == [2, 3]
    assert res["average_skip"] == 2.5
    # total draws = 9. Last appearance at index 7. now_skip = 9 - 1 - 7 = 1 (draw 18)
    assert res["now_skip"] == 1
    assert res["draw_ids"] == [10, 13, 17]
