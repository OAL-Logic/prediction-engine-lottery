from __future__ import annotations
import numpy as np
import pandas as pd

def compute_skip_profile(df: pd.DataFrame, number: int) -> dict:
    """
    Computes skip statistics (Actual Skips, Average Skip, Now Skip) for a given number.
    df: draws ordered oldest -> newest (draw_id ascending), containing a 'numbers' column of lists/arrays.
    """
    total_draws = len(df)
    if total_draws == 0:
        return {
            "number": number,
            "actual_skips": [],
            "average_skip": 0.0,
            "now_skip": 0,
            "total_draws": 0,
            "draw_ids": [],
        }

    # Identify occurrences of the target number
    hit_mask = df["numbers"].apply(lambda nums: number in nums).to_numpy()
    appearances = np.flatnonzero(hit_mask)

    if appearances.size == 0:
        return {
            "number": number,
            "actual_skips": [],
            "average_skip": float(total_draws),
            "now_skip": total_draws,
            "total_draws": total_draws,
            "draw_ids": [],
        }

    # Skip/gaps between consecutive hits
    gaps = np.diff(appearances) - 1
    now_skip = int(total_draws - 1 - appearances[-1])

    # Draw IDs when the hits occurred
    draw_ids = df["draw_id"].iloc[appearances].tolist()

    return {
        "number": number,
        "actual_skips": gaps.tolist(),
        "average_skip": float(gaps.mean()) if gaps.size > 0 else 0.0,
        "now_skip": now_skip,
        "total_draws": total_draws,
        "draw_ids": draw_ids,
    }
