"""
Abbreviated Wheel Generator — covering designs (t if k).
"""

from __future__ import annotations

import itertools
import random
from typing import List, Set


def generate_abbreviated_wheel(
    pool: List[int], 
    pick: int, 
    guarantee: int, 
    max_tickets: int = 500
) -> List[List[int]]:
    """
    Greedy solver to find a near-minimal set of tickets that cover 
    every 'guarantee'-sized subset of the 'pool'.
    
    This is an approximation of a Steiner System / Covering Design.
    """
    v_pool = sorted(pool)
    v = len(v_pool)
    k = pick
    t = guarantee

    if t > k:
        t = k
        
    # 1. Generate all subsets that MUST be covered
    all_t_subsets = set(itertools.combinations(v_pool, t))
    
    # 2. Generate all possible blocks (tickets) we can use
    # If the pool is too large, we can't enumerate all blocks.
    # We'll cap it and use a randomized greedy approach.
    if v > 20:
        # For large pools, we'd need a different algorithm (e.g. simulated annealing)
        # For now, we cap for safety.
        v_pool = v_pool[:20]
        all_t_subsets = set(itertools.combinations(v_pool, t))

    all_k_blocks = list(itertools.combinations(v_pool, k))
    random.shuffle(all_k_blocks)
            
    tickets = []
    
    # 3. Greedy cover
    while all_t_subsets and len(tickets) < max_tickets:
        best_block = None
        best_cover = set()
        
        # To stay fast, check a sample if the combination list is huge
        sample_size = 2000
        sample_blocks = all_k_blocks[:sample_size]
        
        for block in sample_blocks:
            covered = set(itertools.combinations(block, t))
            new_cover = covered.intersection(all_t_subsets)
            
            if len(new_cover) > len(best_cover):
                best_block = block
                best_cover = new_cover
                # Early exit if it's the maximum mathematically possible
                if len(best_cover) == len(list(itertools.combinations(range(k), t))):
                    break
        
        if not best_block:
            break
            
        tickets.append(sorted(list(best_block)))
        all_t_subsets -= best_cover
        all_k_blocks.remove(best_block)

    return tickets
