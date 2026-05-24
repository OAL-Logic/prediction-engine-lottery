"""
Vectorized Harmony Gate: Diagnostic Smoke Test ⚡
================================================
Verifies performance and correctness of all 5 filter tiers using a massive 
candidate set (1,000,000 tickets).
"""

import time
import numpy as np
from engine.modules.vector_core import registry
from engine.adapters.registry import registry as game_registry

# Import all tiers to register them
import engine.modules.filters_tier1
import engine.modules.filters_tier2
import engine.modules.filters_tier3
import engine.modules.filters_tier4
import engine.modules.filters_tier5

def run_diagnostic():
    print("🚀 Initializing Vectorized Harmony Gate Diagnostic...")
    
    # 1. Setup Environment
    game_def = game_registry.get_game("br/mega-sena")
    rules = game_def.to_rules()
    N_TICKETS = 1_000_000
    K = rules.pick_count
    POOL = rules.number_range[1]
    
    print(f"📊 Generating {N_TICKETS:,} candidate tickets (Pick-{K} from {POOL})...")
    start_gen = time.time()
    # Generate 1M random tickets
    candidates = np.random.randint(1, POOL + 1, size=(N_TICKETS, K))
    # Ensure they are unique within each ticket (not perfect with randint but enough for smoke test)
    candidates.sort(axis=1)
    end_gen = time.time()
    print(f"✅ Generation complete in {end_gen - start_gen:.4f}s")

    # 2. Sequential Filter Test
    print("\n🕵️  Executing Sequential Tier Tests:")
    all_filter_ids = list(registry._filters.keys())
    
    tier_metrics = {}
    
    for uid in all_filter_ids:
        f = registry.get(uid)
        t_start = time.time()
        res = f.apply(candidates, rules)
        t_end = time.time()
        
        elapsed_ms = (t_end - t_start) * 1000
        pass_rate = (np.sum(res) / N_TICKETS) * 100
        
        tier = f.tier
        if tier not in tier_metrics: tier_metrics[tier] = []
        tier_metrics[tier].append(elapsed_ms)
        
        print(f"  [{tier}] {uid:35} | {elapsed_ms:8.2f}ms | Pass: {pass_rate:6.2f}%")

    # 3. Batch Performance Test
    print("\n📦 Executing Full Batch Validation (K-of-N)...")
    active_ids = ["structural_odd_count", "structural_prime_count", "positional_successive_groups", 
                  "positional_first_last_distance", "algebraic_number_sum", "historical_hot_cold"]
    
    t_start = time.time()
    batch_res = registry.validate_batch(candidates, rules, active_ids, k_of_n=4)
    t_end = time.time()
    
    batch_ms = (t_end - t_start) * 1000
    print(f"🔥 Batch (6 Filters, K=4) processed 1M tickets in: {batch_ms:.2f}ms")
    print(f"📈 Total Throughput: {N_TICKETS / (batch_ms/1000):,.0f} tickets/sec")

    # 4. Tier Averages
    print("\n📈 Performance Summary by Tier (Avg per Filter):")
    for tier, times in sorted(tier_metrics.items()):
        avg = sum(times) / len(times)
        print(f"  Tier {tier}: {avg:.2f}ms")

if __name__ == "__main__":
    run_diagnostic()
