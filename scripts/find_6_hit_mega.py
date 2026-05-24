import json
import itertools
import random

# Top 25 from rank-numbers for Mega-Sena
top_ranks = [27, 32, 28, 50, 6, 46, 42, 43, 15, 1, 47, 3, 48, 60, 52, 8, 13, 24, 17, 10, 2, 7, 9, 39, 41]

# Load historical data
draw_files = ['data/inspections/br_mega-sena/2026.json', 'data/inspections/br_mega-sena/2025.json', 'data/inspections/br_mega-sena/2024.json']
all_draws = []
for f_path in draw_files:
    with open(f_path, 'r') as f:
        all_draws.extend(json.load(f))

def find():
    print(f"Searching for 6-hit combo in top 25 ranks (subset 16) across {len(all_draws)} draws...")
    best_hits = 0
    best_combo = None
    
    # Using random sampling to cover more ground in the combination space
    for _ in range(200000):
        combo = random.sample(top_ranks, 16)
        s_pool = set(combo)
        for draw in all_draws:
            hits = len(s_pool.intersection(draw['numbers']))
            if hits >= 6:
                print(f"FOUND! Combo {sorted(combo)} hit {hits} points in Draw {draw['draw_id']} on {draw.get('draw_date', draw.get('date'))}")
                return sorted(combo)
            if hits > best_hits:
                best_hits = hits
                best_combo = combo
    
    print(f"Best found in 200k random samples: {best_hits} hits with combo {sorted(best_combo)}")
    return sorted(best_combo)

find()
