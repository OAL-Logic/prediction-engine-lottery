"""
Wheeling Engine Diagnostic Test 🧪
==================================
Verifies bit-packed coverage evaluation and gap matrix generation.
"""

import time
import numpy as np
from engine.modules.wheels_wrg import WheelingEngine

def run_wheel_diagnostic():
    print("🚀 Initializing Wheeling Engine Diagnostic...")
    
    # 1. Setup Environment
    # v=12, k=6, t=4, m=6 (A small abbreviated wheel)
    N_POOL = 12
    K = 6
    T = 4
    M = 6
    
    engine = WheelingEngine(n=N_POOL, k=K)
    
    # A sample "Known Good" wheel set for 12, 6, 4, 6 (approx 6 tickets)
    # This is a dummy set for testing the math
    tickets = np.array([
        [1, 2, 3, 4, 5, 6],
        [7, 8, 9, 10, 11, 12],
        [1, 2, 7, 8, 11, 12],
        [3, 4, 9, 10, 1, 7],
        [5, 6, 8, 11, 2, 9],
        [1, 3, 5, 7, 9, 11]
    ])
    
    print(f"📊 Evaluating {tickets.shape[0]} tickets for {T}-if-{M} guarantee in pool of {N_POOL}...")
    
    t_start = time.time()
    coverage = engine.evaluate_coverage(tickets, T, M)
    t_end = time.time()
    
    print(f"✅ Coverage: {coverage:.2%}")
    print(f"⏱️  Evaluation Time: {(t_end - t_start)*1000:.2f}ms")
    
    # 2. Gap Matrix Test
    print("\n🔍 Generating Gap Matrix (Coverage Density)...")
    matrix = engine.get_gap_matrix(tickets)
    
    # Print a small section of the matrix
    print("  ASCII Visualization (Partial 8x8):")
    for i in range(min(8, N_POOL)):
        row = ""
        for j in range(min(8, N_POOL)):
            val = matrix[i, j]
            if val == 0: row += " . "
            elif val == 1: row += " ░ "
            elif val == 2: row += " ▒ "
            else: row += " █ "
        print(f"  {i+1:02} {row}")

if __name__ == "__main__":
    run_wheel_diagnostic()
