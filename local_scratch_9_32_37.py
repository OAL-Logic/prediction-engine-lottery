import duckdb
import numpy as np
from itertools import combinations
import pandas as pd

# Load historical draws
conn = duckdb.connect('data/lottery.db')
df_draws = conn.execute("""
    SELECT numbers 
    FROM draws 
    WHERE lottery_id = 'br/mega-sena' 
    ORDER BY draw_id ASC
""").df()
conn.close()

draws = df_draws["numbers"].tolist()
N_DRAWS = len(draws)

# Precompute one-hot matrix of all historical draws (N_DRAWS x 60)
draw_mat = np.zeros((N_DRAWS, 60), dtype=np.int8)
for i, draw in enumerate(draws):
    for num in draw:
        draw_mat[i, num-1] = 1

def get_ac_value(combination):
    diffs = set()
    for i in range(len(combination)):
        for j in range(i+1, len(combination)):
            diffs.add(abs(combination[i] - combination[j]))
    return len(diffs) - (len(combination) - 1)

def structural_check(combo):
    sum_c = sum(combo)
    if not (130 <= sum_c <= 220):
        return False
    
    evens = sum(1 for x in combo if x % 2 == 0)
    if evens not in [2, 3, 4]:
        return False
        
    highs = sum(1 for x in combo if x > 30)
    if highs not in [2, 3, 4]:
        return False
        
    # AC check
    if get_ac_value(combo) < 7:
        return False
        
    # Max per decade
    decades = [0]*6
    for x in combo:
        decades[(x-1)//10] += 1
    if any(d > 2 for d in decades):
        return False
        
    return True

fixed = [9, 32, 37]

candidate_pool = [x for x in range(1, 61) if x not in fixed]

# Important Cycle 65 missing numbers
cycle_missing = {7, 12, 19, 28, 34, 41, 45, 56, 59}

valid_combos = []
for p in combinations(candidate_pool, 3):
    combo = sorted(fixed + list(p))
    if structural_check(combo):
        valid_combos.append(combo)

print(f"Generated {len(valid_combos)} structurally valid combinations.")

# Evaluate Quadras and cycle score
valid_mat = np.zeros((len(valid_combos), 60), dtype=np.int8)
for i, combo in enumerate(valid_combos):
    for num in combo:
        valid_mat[i, num-1] = 1

matches = draw_mat @ valid_mat.T
quadras = (matches == 4).sum(axis=0)
quinas = (matches == 5).sum(axis=0)
senas = (matches == 6).sum(axis=0)

# 12-game rolling Quadra/Quina prize win pct
cumsum_p = np.vstack([np.zeros((1, len(valid_combos)), dtype=np.int32), np.cumsum((matches >= 4).astype(np.int32), axis=0)])
rolling_p = cumsum_p[12:] - cumsum_p[:-12]
prize_pct = (rolling_p >= 1).mean(axis=0) * 100

results = []
for i, combo in enumerate(valid_combos):
    miss_c = sum(1 for x in combo if x in cycle_missing)
    results.append({
        'combo': combo,
        'quadras': quadras[i],
        'quinas': quinas[i],
        'senas': senas[i],
        'prize_pct': prize_pct[i],
        'cycle_matches': miss_c,
        'sum': sum(combo),
        'evens': sum(1 for x in combo if x % 2 == 0)
    })

df_res = pd.DataFrame(results)

df_res_q = df_res[df_res['quadras'] >= 1].copy()

# Sort by cycle_matches (desc), then prize_pct, then quadras (desc)
df_res_c = df_res_q.sort_values(['cycle_matches', 'prize_pct', 'quadras'], ascending=[False, False, False])

print("\nTop Candidates (Optimized for Cycle 65 & Historical 12-game %):")
print(df_res_c.head(15).to_string(index=False))

df_res_max_q = df_res.sort_values(['quadras', 'prize_pct'], ascending=[False, False])
print("\nTop Candidates (Optimized purely for Quadras):")
print(df_res_max_q.head(15).to_string(index=False))
