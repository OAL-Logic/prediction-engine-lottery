import json
import itertools

# Load the latest rankings
# Top 20 from rank-numbers: 7, 22, 12, 20, 3, 11, 23, 16, 1, 21, 10, 25, 2, 8, 19, 4, 15, 17, 24, 6
top_ranks = [7, 22, 12, 20, 3, 11, 23, 16, 1, 21, 10, 25, 2, 8, 19, 4, 15, 17, 24, 6]

with open('data/inspections/br_lotofacil/2026.json', 'r') as f:
    draws_2026 = json.load(f)
with open('data/inspections/br_lotofacil/2025.json', 'r') as f:
    draws_2025 = json.load(f)

all_draws = draws_2026 + draws_2025

def check_15(pool_16):
    s_pool = set(pool_16)
    for draw in all_draws:
        hits = len(s_pool.intersection(draw['numbers']))
        if hits == 15:
            return draw['draw_id'], draw['numbers']
    return None, None

# Try different 16-number combinations from the top 20 ranks
# This is a bit brute force but focused on high-probability numbers
for combo in itertools.combinations(top_ranks, 16):
    draw_id, win_nums = check_15(combo)
    if draw_id:
        print(f"FOUND! Combo {sorted(combo)} hit 15 points in Draw {draw_id}")
        break
else:
    print("No 15-hit combo found in top 20 ranks for 2025-2026.")
