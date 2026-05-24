"""
Key Wheel Generator — fixed-number expansion.
"""

from __future__ import annotations

import itertools
from typing import List


def generate_key_wheel(pool: List[int], pick: int, keys: List[int]) -> List[List[int]]:
    """
    Generate all combinations of size 'pick' from 'pool' that MUST include 'keys'.
    """
    if pick > len(pool) or len(keys) > pick:
        return []
    
    # Numbers in pool that are not keys
    remaining_pool = sorted(list(set(pool) - set(keys)))
    n_needed = pick - len(keys)
    
    if n_needed == 0:
        return [sorted(keys)]
        
    results = []
    for comb in itertools.combinations(remaining_pool, n_needed):
        results.append(sorted(list(comb) + keys))
        
    return results
