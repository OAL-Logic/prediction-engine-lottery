import sys
import os
import duckdb
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations

sys.path.append(os.getcwd())

def run_analysis():
    db_path = os.path.join(os.getcwd(), "data", "lottery.db")
    con = duckdb.connect(db_path)
    
    # Load all Quina draws
    df = con.execute("""
        SELECT draw_id, draw_date, numbers 
        FROM draws 
        WHERE lottery_id = 'br/quina' 
        ORDER BY draw_id ASC
    """).df()
    
    total_draws = len(df)
    print(f"Total draws loaded: {total_draws}")
    
    # 1. Quina de São João Draws
    sao_joao_draw_ids = [2627, 2925, 3221, 3517, 3814, 4114, 4412, 4706, 5002, 5299, 5590, 5881, 6172, 6462, 6760]
    df_sj = df[df['draw_id'].isin(sao_joao_draw_ids)].copy()
    
    print("\n--- LAYER 1: COMPARATIVE MACRO-CYCLE ANALYSIS ---")
    print(f"Analyzing {len(df_sj)} past Quina de São João draws...")
    
    # Frequency of numbers in Quina de São João
    sj_numbers = []
    for nums in df_sj['numbers']:
        sj_numbers.extend(nums)
    sj_freq = Counter(sj_numbers)
    
    print("\nMost frequent numbers in Quina de São João:")
    for num, count in sj_freq.most_common(10):
        print(f"Number {num:02d}: drawn {count} times ({(count/15)*100:.1f}%)")
        
    # Global frequency
    global_numbers = []
    for nums in df['numbers']:
        global_numbers.extend(nums)
    global_freq = Counter(global_numbers)
    
    # Overdue/Gaps as of draw 7050
    # Matrix of draws
    matrix = np.zeros((total_draws, 81))
    for i, row in enumerate(df["numbers"]):
        matrix[i, row] = 1.0
        
    current_gaps = {}
    mean_gaps = {}
    for n in range(1, 81):
        indices = np.where(matrix[:, n] == 1)[0]
        if len(indices) > 0:
            last_seen_idx = indices[-1]
            current_gaps[n] = (total_draws - 1) - last_seen_idx
            if len(indices) >= 2:
                gaps = np.diff(indices)
                mean_gaps[n] = np.mean(gaps)
            else:
                mean_gaps[n] = total_draws
        else:
            current_gaps[n] = total_draws
            mean_gaps[n] = total_draws
            
    # Print top overdue numbers
    overdue_sorted = sorted(current_gaps.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 10 Overdue Numbers (highest gap as of draw 7050):")
    for num, gap in overdue_sorted[:10]:
        print(f"Number {num:02d}: gap of {gap} draws (mean gap: {mean_gaps[num]:.1f})")
        
    # Quadrant analysis of Quina de São João
    # Q1: 1-20, Q2: 21-40, Q3: 41-60, Q4: 61-80
    print("\nQuadrant Distribution of Quina de São João draws:")
    quadrant_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for idx, row in df_sj.iterrows():
        draw_quads = []
        for n in row['numbers']:
            if 1 <= n <= 20: draw_quads.append(1)
            elif 21 <= n <= 40: draw_quads.append(2)
            elif 41 <= n <= 60: draw_quads.append(3)
            elif 61 <= n <= 80: draw_quads.append(4)
        counts = Counter(draw_quads)
        print(f"Draw {row['draw_id']} ({row['draw_date'].strftime('%Y')}): Q1:{counts[1]}, Q2:{counts[2]}, Q3:{counts[3]}, Q4:{counts[4]} -> {row['numbers']}")
        for q in draw_quads:
            quadrant_counts[q] += 1
            
    print("\nAggregate Quadrant Counts across all Quina de São João:")
    total_sj_balls = len(df_sj) * 5
    for q, count in quadrant_counts.items():
        print(f"Quadrant {q} ({(q-1)*20+1}-{q*20}): {count} balls ({count/total_sj_balls*100:.1f}%)")
        
    # Parity and Sum analysis of Quina de São João
    sums = []
    parities = []
    consecutives = []
    primes_set = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79}
    primes_counts = []
    
    print("\nStructure of past Quina de São João draws:")
    for idx, row in df_sj.iterrows():
        nums = sorted(row['numbers'])
        soma = sum(nums)
        sums.append(soma)
        
        odds = sum(1 for n in nums if n % 2 != 0)
        evens = 5 - odds
        parities.append((odds, evens))
        
        consec = sum(1 for i in range(len(nums)-1) if nums[i+1] - nums[i] == 1)
        consecutives.append(consec)
        
        primes = sum(1 for n in nums if n in primes_set)
        primes_counts.append(primes)
        
        print(f"Draw {row['draw_id']}: Sum={soma:3d}, Parity={odds:1d}O/{evens:1d}E, Consecutives={consec}, Primes={primes} -> {nums}")
        
    print(f"\nAverage Sum in São João: {np.mean(sums):.1f} (std: {np.std(sums):.1f})")
    print(f"Parity distribution in São João:")
    parity_counts = Counter(parities)
    for parity, count in parity_counts.items():
        print(f"  {parity[0]} Odds / {parity[1]} Evens: {count} times ({count/15*100:.1f}%)")
        
    con.close()

if __name__ == "__main__":
    run_analysis()
