"""
Tendency Module — pattern frequency and delay statistics.
=========================================================
Calculates Occurrence, Average, Delay, and Trend for structural patterns.
Strictly decoupled from UI rendering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
import pandas as pd
import numpy as np

@dataclass
class PatternQtyStats:
    qty: int
    occurrence: int
    average_pct: float
    avg_frequency: float  # 1 in N
    last_seen_id: int
    last_seen_date: str
    delay: int
    trend: List[int]      # Occurrence streak in last N draws

@dataclass
class TendencyResult:
    pattern_name: str
    stats: List[PatternQtyStats]
    total_draws: int

def analyze_pattern_tendency(
    df: pd.DataFrame,
    pattern_func: Callable[[List[int], Optional[List[int]]], int],
    name: str,
    window: int = 20
) -> TendencyResult:
    """
    Analyze the tendency of a pattern across historical draws.
    
    Parameters
    ----------
    df : pd.DataFrame
        Canonical draw DataFrame with 'draw_id', 'draw_date', and 'numbers'.
    pattern_func : Callable
        Function that takes (current_numbers, previous_numbers) and returns an int qty.
    name : str
        Human-readable name of the pattern.
    window : int
        Window size for trend calculation.
    """
    if df.empty:
        return TendencyResult(name, [], 0)

    # Calculate quantities for each draw
    qtys = []
    prev_numbers = None
    for _, row in df.iterrows():
        qty = pattern_func(row["numbers"], prev_numbers)
        qtys.append(qty)
        prev_numbers = row["numbers"]

    df_qtys = df.copy()
    df_qtys["qty"] = qtys

    total_draws = len(df_qtys)
    unique_qtys = sorted(df_qtys["qty"].unique())
    
    results = []
    for q in unique_qtys:
        q_mask = df_qtys["qty"] == q
        occurrence = int(q_mask.sum())
        average_pct = (occurrence / total_draws) * 100
        avg_frequency = total_draws / occurrence if occurrence > 0 else 0
        
        # Last seen info
        hits = df_qtys[q_mask]
        if not hits.empty:
            last_row = hits.iloc[-1]
            last_seen_id = int(last_row["draw_id"])
            last_seen_date = str(last_row["draw_date"])
            delay = int(df_qtys["draw_id"].iloc[-1] - last_seen_id) # Simplistic delay based on ID difference
            # Better delay: count of draws since last seen in sequence
            last_index = hits.index[-1]
            delay = total_draws - 1 - last_index
        else:
            last_seen_id = 0
            last_seen_date = "N/A"
            delay = total_draws

        # Trend (last N draws)
        trend = [1 if val == q else 0 for val in qtys[-window:]]
        
        results.append(PatternQtyStats(
            qty=int(q),
            occurrence=occurrence,
            average_pct=round(average_pct, 2),
            avg_frequency=round(avg_frequency, 2),
            last_seen_id=last_seen_id,
            last_seen_date=last_seen_date,
            delay=delay,
            trend=trend
        ))
        
    return TendencyResult(name, results, total_draws)
