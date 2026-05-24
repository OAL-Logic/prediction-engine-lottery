import os
import json
import numpy as np
import pandas as pd
from engine.modules.filters import registry
from engine.adapters import DrawRules

def audit_filters():
    print("🛡️ LOTTERY ENGINE FILTER AUDIT")
    print("=============================")
    
    registry._discover()
    
    filters = []
    # Regular filters
    for uid in registry._module_map.keys():
        f = registry.get(uid)
        if f:
            filters.append(f)
            
    # Factory filters (Div by N)
    for n in range(2, 11):
        uid = f"algebraic_div_by_{n}"
        f = registry.get(uid)
        if f:
            filters.append(f)

    print(f"Found {len(filters)} filters in registry.")
    
    rules = DrawRules(
        name="Test Rules",
        number_range=(1, 60),
        pick_count=6,
        ticket_price=5.0,
        currency="BRL",
        odds={6: 50000000}
    )
    
    # KGV Check
    kgv_dir = "tests/factory"
    kgv_files = [f for f in os.listdir(kgv_dir) if f.endswith(".json")]
    print(f"Found {len(kgv_files)} KGV files in {kgv_dir}.")
    
    missing_kgv = []
    for f in filters:
        kgv_path = os.path.join(kgv_dir, f"{f.unique_id}.json")
        if not os.path.exists(kgv_path):
            missing_kgv.append(f.unique_id)
            
    if missing_kgv:
        print(f"\n⚠️ MISSING KGVs ({len(missing_kgv)}):")
        for uid in missing_kgv:
            print(f" - {uid}")
    else:
        print("\n✅ All filters have KGV baselines.")

    # Coverage Breakdown
    tiers = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for f in filters:
        tiers[f.tier] = tiers.get(f.tier, 0) + 1
        
    print("\n📊 TIER COVERAGE:")
    for t, count in tiers.items():
        print(f" Tier {t}: {count} filters")
        
    print("\nCONCLUSION:")
    if len(filters) < 100:
        print(f"❌ GAP: Only {len(filters)} filters implemented (PRD requires 100+).")
    else:
        print("✅ PRD Quantity target met.")

if __name__ == "__main__":
    audit_filters()
