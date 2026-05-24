"""
Patterns Module — structural lottery patterns.
==============================================
Handles Primes, Fibonacci, and Frame (Perimeter) logic.
"""

from __future__ import annotations

import math
from typing import List, Set

# --- Constants ---

PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
MAGIC = {5, 6, 7, 12, 13, 14, 19, 20, 21}
MULTIPLES_3 = {3, 6, 9, 12, 15, 18, 21, 24}

def get_primes_in_set(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n in PRIMES]

def get_fibonacci_in_set(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n in FIBONACCI]

def get_magic_in_set(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n in MAGIC]

def get_multiples_3_in_set(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n in MULTIPLES_3]

def get_repeated_count(current_draw: List[int], previous_draw: List[int]) -> int:
    """Calculate how many numbers are repeated from the previous draw."""
    return len(set(current_draw) & set(previous_draw))

def get_frame_center_logic(numbers: List[int], cols: int = 10, max_n: int = 60) -> dict:
    """
    Calculate Frame (Perimeter) vs Center distribution.
    Numbers on the edges of the board are 'Frame'.
    """
    rows = math.ceil(max_n / cols)
    frame = []
    center = []
    
    for n in numbers:
        # 1-based coordinates
        row = (n - 1) // cols + 1
        col = (n - 1) % cols + 1
        
        is_edge = (row == 1 or row == rows or col == 1 or col == cols)
        if is_edge:
            frame.append(n)
        else:
            center.append(n)
            
    return {"frame": frame, "center": center}

def get_line_column_distribution(numbers: List[int], cols: int = 10) -> dict:
    """
    Count how many numbers fall into each row and column.
    """
    row_counts = {}
    col_counts = {}
    
    for n in numbers:
        row = (n - 1) // cols + 1
        col = (n - 1) % cols + 1
        row_counts[row] = row_counts.get(row, 0) + 1
        col_counts[col] = col_counts.get(col, 0) + 1
        
    return {"rows": row_counts, "cols": col_counts}

def get_pattern_string(numbers: List[int], cols: int = 10, max_n: int = 60) -> str:
    """Returns a string like '3-3-3-3-3' representing the row distribution."""
    lc = get_line_column_distribution(numbers, cols)
    rows = math.ceil(max_n / cols)
    return "-".join(str(lc["rows"].get(r, 0)) for r in range(1, rows + 1))

def analyze_voids(draws: List[List[int]], cols: int = 10, max_n: int = 60, window: int = 5) -> dict:
    """
    Identify sectors (rows, columns, quadrants) that have been empty for a number of draws.
    """
    recent_draws = draws[-window:] if len(draws) >= window else draws
    rows = math.ceil(max_n / cols)
    
    row_last_seen = {r: 0 for r in range(1, rows + 1)}
    col_last_seen = {c: 0 for c in range(1, cols + 1)}
    
    # Track when each row/col was last 'hit'
    for i, draw in enumerate(draws):
        for n in draw:
            r = (n - 1) // cols + 1
            c = (n - 1) % cols + 1
            row_last_seen[r] = i + 1
            col_last_seen[c] = i + 1
            
    total_draws = len(draws)
    row_delays = {r: total_draws - last for r, last in row_last_seen.items()}
    col_delays = {c: total_draws - last for c, last in col_last_seen.items()}
    
    return {
        "row_delays": row_delays,
        "col_delays": col_delays,
        "cold_rows": [r for r, d in row_delays.items() if d >= window],
        "cold_cols": [c for c, d in col_delays.items() if d >= window]
    }

def analyze_cycle(draws: List[List[int]], total_range: List[int]) -> dict:
    """
    Analyze the 'Cycle' of numbers.
    A cycle is complete when all numbers in the total_range have appeared at least once.
    """
    total_set = set(total_range)
    seen = set()
    cycles = []
    current_cycle_start = 0
    
    for i, draw in enumerate(draws):
        seen.update(draw)
        if total_set.issubset(seen):
            cycles.append({
                "start_index": current_cycle_start,
                "end_index": i,
                "length": i - current_cycle_start + 1
            })
            seen = set()
            current_cycle_start = i + 1
            
    return {
        "completed_cycles": cycles,
        "current_cycle_progress": len(seen) / len(total_range),
        "missing_in_current": sorted(list(total_set - seen))
    }

def get_z_score(observed: int, expected: float, std_dev: float) -> float:
    """Standardize the anomaly: (Observed - Expected) / StdDev"""
    if std_dev == 0: return 0.0
    return (observed - expected) / std_dev
