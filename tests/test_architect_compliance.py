import time
import numpy as np
import pytest
from engine.modules.filters import registry
from engine.adapters.registry import registry as game_registry

@pytest.fixture
def mock_context():
    game_def = game_registry.get_game("br/mega-sena")
    rules = game_def.to_rules()
    return rules

def test_filter_performance_threshold(mock_context):
    """AC 2.1.4: Individual filters must process 10,000 tickets in < 1ms."""
    N_TICKETS = 10_000
    K = mock_context.pick_count
    POOL = mock_context.number_range[1]
    
    # Generate tickets
    candidates = np.random.randint(1, POOL + 1, size=(N_TICKETS, K))
    candidates.sort(axis=1)
    
    all_filters = list(registry._filters.values())
    
    for f in all_filters:
        # Pre-warm (ignore first run if needed, but for 1ms we should be consistent)
        f.apply(candidates, mock_context)
        
        start = time.perf_counter()
        f.apply(candidates, mock_context)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        print(f"DEBUG: Filter {f.unique_id} took {elapsed_ms:.4f}ms")
        
        # AC 2.1.4 threshold
        assert elapsed_ms < 1.0, f"Filter {f.unique_id} failed 1ms threshold: {elapsed_ms:.4f}ms"

def test_shared_memory_compliance(mock_context):
    """AC 2.1.2: Ensure filters don't mutate input buffer."""
    N_TICKETS = 100
    K = mock_context.pick_count
    POOL = mock_context.number_range[1]
    
    candidates = np.random.randint(1, POOL + 1, size=(N_TICKETS, K))
    original_copy = candidates.copy()
    
    for f in registry._filters.values():
        f.apply(candidates, mock_context)
        # Check if candidates was mutated
        assert np.array_equal(candidates, original_copy), f"Filter {f.unique_id} mutated input buffer!"
