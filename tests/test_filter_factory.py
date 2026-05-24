import os
import json
import pytest
import numpy as np
from pathlib import Path
from engine.modules.filters import registry
from engine.adapters.registry import registry as game_registry

KGV_DIR = Path(__file__).parent / "factory"
GENERATE_KGV = os.getenv("GENERATE_KGV", "false").lower() == "true"

@pytest.fixture
def test_context():
    game_def = game_registry.get_game("br/mega-sena")
    return game_def.to_rules()

# Force discovery
registry._discover()
all_filter_ids = list(registry._module_map.keys())

# Add factory filters (Div-by-N 2-20)
for n in range(2, 21):
    uid = f"algebraic_div_by_{n}"
    if uid not in all_filter_ids:
        all_filter_ids.append(uid)

# Add any instances already registered
for uid in registry._instances.keys():
    if uid not in all_filter_ids:
        all_filter_ids.append(uid)

@pytest.mark.parametrize("filter_id", sorted(all_filter_ids))
def test_filter_factory_kgv(filter_id, test_context):
    """STORY 5.1: Validate filter output against Known Good Vector (KGV)."""
    f = registry.get(filter_id)
    assert f is not None, f"Filter {filter_id} could not be loaded."
    
    # 1. Deterministic Input Generation
    # Use a fixed seed for reproducible test vectors
    np.random.seed(42)
    N_TEST = 1000
    K = test_context.pick_count
    POOL = test_context.number_range[1]
    candidates = np.random.randint(1, POOL + 1, size=(N_TEST, K))
    candidates.sort(axis=1)
    
    # 2. Execute Filter
    current_result = f.apply(candidates, test_context)
    
    # 3. KGV Management
    kgv_path = KGV_DIR / f"{filter_id}.json"
    
    if GENERATE_KGV:
        # Generate baseline
        kgv_data = {
            "filter_id": filter_id,
            "pass_count": int(np.sum(current_result)),
            "mask_sum": int(np.sum(current_result.astype(int) * np.arange(N_TEST))), # Deterministic fingerprint
            "version": "1.0"
        }
        with open(kgv_path, "w") as out:
            json.dump(kgv_data, out, indent=2)
        pytest.skip(f"Generated KGV for {filter_id}")
        
    # 4. Validation
    if not kgv_path.exists():
        pytest.fail(f"KGV baseline missing for {filter_id}. Run with GENERATE_KGV=true to create it.")
        
    with open(kgv_path, "r") as f_kgv:
        baseline = json.load(f_kgv)
        
    # Check PASS count
    actual_pass = int(np.sum(current_result))
    assert actual_pass == baseline["pass_count"], f"Logic drift in {filter_id}: Pass count mismatch."
    
    # Check fingerprint (weighted sum of mask)
    actual_fingerprint = int(np.sum(current_result.astype(int) * np.arange(N_TEST)))
    assert actual_fingerprint == baseline["mask_sum"], f"Logic drift in {filter_id}: Fingerprint mismatch (semantic change)."
