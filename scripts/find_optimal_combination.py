import sys
import os
import itertools
import numpy as np
import pandas as pd
import json

sys.path.append(os.getcwd())

from engine.modules.esoteric_pipeline import EsotericPipeline
from engine.adapters import DrawRules

def find_optimal():
    # 1. Define Quina Rules
    rules = DrawRules(
        name="Quina",
        pick_count=5,
        number_range=(1, 80),
        board_cols=10,
        ticket_price=2.5,
        currency="BRL"
    )
    
    # 2. Get Esoteric Weights for June 28, 2026
    pipeline = EsotericPipeline()
    context = pipeline.compile_context(
        full_name="JANE DOE",
        birth_date="1990-01-01",
        coords=(-23.5505, -46.6333),
        target_date="2026-06-28"
    )
    _, esoteric_weights = pipeline.generate_weights(context, 1, 80)
    
    # 3. Top Resonant Pool from Esoteric Matrix
    # We will pick the top 15 esoteric resonant numbers as our pool
    top_15_esoteric = sorted(esoteric_weights.keys(), key=esoteric_weights.get, reverse=True)[:15]
    print(f"Esoteric Pool: {top_15_esoteric}")
    
    # Let's add some historical Quina de São João hot numbers to the pool if they are not there:
    # SJ hot: 55, 14, 15, 28, 36, 17, 26, 79
    sj_hot = [55, 14, 15, 28, 36, 17, 26, 79]
    pool = list(set(top_15_esoteric + sj_hot))
    print(f"Combined Analysis Pool (size {len(pool)}): {sorted(pool)}")
    
    # 4. Compile historical statistics for scoring
    # Load past SJ draws
    sj_draws = [
        [14, 15, 28, 58, 68], # 2011
        [2, 4, 27, 36, 51],   # 2012
        [5, 17, 55, 63, 67],  # 2013
        [15, 26, 55, 71, 79], # 2014
        [1, 15, 22, 23, 47],  # 2015
        [14, 26, 28, 55, 79], # 2016
        [6, 7, 13, 14, 26],   # 2017
        [3, 29, 33, 53, 69],  # 2018
        [17, 27, 53, 78, 79], # 2019
        [7, 17, 29, 55, 78],  # 2020
        [25, 28, 36, 60, 61], # 2021
        [35, 36, 49, 75, 80], # 2022
        [12, 13, 45, 47, 70], # 2023
        [21, 38, 60, 64, 70], # 2024
        [12, 19, 20, 34, 35]  # 2025
    ]
    
    sj_flat = [n for draw in sj_draws for n in draw]
    sj_counts = {n: sj_flat.count(n) for n in range(1, 81)}
    
    # Dates/Contest direct resonances
    # June 28, 2026 -> 28, 6, 26, 8
    # Contest 7051 -> 7, 51, 11 (factor), 13 (sum), 4 (reduced sum)
    direct_esoteric_nums = {28, 6, 26, 8, 7, 51, 11, 13, 4, 16, 29, 55}
    
    candidates = []
    
    # 5. Generate and filter combinations
    for comb in itertools.combinations(pool, 5):
        ticket = sorted(list(comb))
        soma = sum(ticket)
        
        # Filter 1: Sum range
        # ideal_sum = 40.5 * 5 = 202.5. Tolerance 30%: [142, 263]
        if not (142 <= soma <= 263):
            continue
            
        # Filter 2: Parity (avoid all odd or all even)
        odds = sum(1 for n in ticket if n % 2 != 0)
        if odds == 0 or odds == 5:
            continue
            
        # Filter 3: Consecutive run limits (max consecutive size < 3 for safety, although 3 is sometimes okay, 2 is safer)
        consecutive = 1
        max_c = 1
        for i in range(len(ticket) - 1):
            if ticket[i+1] == ticket[i] + 1:
                consecutive += 1
            else:
                max_c = max(max_c, consecutive)
                consecutive = 1
        max_c = max(max_c, consecutive)
        if max_c >= 3: # Discard tickets with 3+ consecutive numbers
            continue
            
        # Filter 4: Decades (span at least 3 decades)
        decades = {n // 10 for n in ticket}
        if len(decades) < 3:
            continue
            
        # Filter 5: Same last digit (avoid too many matching last digits)
        last_digits = [n % 10 for n in ticket]
        if any(last_digits.count(d) >= 3 for d in last_digits):
            continue

        # 6. Scoring Metrics
        # - Esoteric weight (average)
        eso_score = np.mean([esoteric_weights.get(n, 0.0) for n in ticket])
        
        # - Past SJ draws hits count
        sj_score = sum(sj_counts.get(n, 0) for n in ticket) / 15.0 # Max normalized
        
        # - Direct esoteric alignment count (number of matches with date/contest digits)
        direct_matches = sum(1 for n in ticket if n in direct_esoteric_nums)
        direct_score = direct_matches / 5.0
        
        # - Consecutives check (Quina de São João has a 60% probability of 1 consecutive pair, so we give a bonus for exactly 1 consecutive pair)
        consec_bonus = 0.15 if max_c == 2 else 0.0
        
        # - Overdue check (proximity to cycle completion, based on current gaps)
        # We can write a quick lookup for gaps we got earlier:
        # Number 04: gap 35; Number 07: gap 57; Number 28: gap 3 (drawn in 2021 SJ, wait, gap since 7050)
        # Let's load the recent gaps from DB if needed, or simply calculate overall score.
        # Combined Score
        total_score = (eso_score * 0.4) + (sj_score * 0.3) + (direct_score * 0.2) + consec_bonus
        
        candidates.append({
            "ticket": ticket,
            "sum": soma,
            "parity": f"{odds}O/{5-odds}E",
            "consecutives": 1 if max_c == 2 else 0,
            "eso_score": eso_score,
            "sj_score": sj_score,
            "direct_score": direct_score,
            "total_score": total_score
        })
        
    # Sort candidates
    sorted_candidates = sorted(candidates, key=lambda x: x['total_score'], reverse=True)
    
    print(f"\nFound {len(sorted_candidates)} valid combinations.")
    print("\nTop 10 Optimal Combinations by Overlapping Resonance:")
    for idx, cand in enumerate(sorted_candidates[:10], 1):
        t_str = " ".join(f"{x:02d}" for x in cand["ticket"])
        print(f"Rank #{idx:02d} ➔ [ {t_str} ]  Score={cand['total_score']:.4f} (Sum={cand['sum']}, Parity={cand['parity']}, Consec={cand['consecutives']}, Eso={cand['eso_score']:.3f}, SJ={cand['sj_score']:.3f}, Direct={cand['direct_score']:.3f})")

if __name__ == "__main__":
    find_optimal()
