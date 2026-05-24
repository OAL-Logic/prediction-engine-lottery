"""
Full Wheel Generator — combinatorial expansion.
"""

from __future__ import annotations

import itertools
from typing import List


def generate_full_wheel(pool: List[int], pick: int) -> List[List[int]]:
    """
    Generate all possible combinations of size 'pick' from 'pool'.
    Mathematically: C(len(pool), pick).
    """
    if pick > len(pool):
        return []
    
    return [sorted(list(comb)) for comb in itertools.combinations(sorted(pool), pick)]
