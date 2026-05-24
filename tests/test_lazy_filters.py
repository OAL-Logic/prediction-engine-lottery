import sys
import pytest

def test_lazy_loading_registry():
    """AC 2.2.1: Ensure filters are not imported at module level."""
    # Ensure engine.modules.filters.tier1_structural is NOT in sys.modules
    assert "engine.modules.filters.tier1_structural" not in sys.modules
    
    from engine.modules.filters import registry
    
    # Still shouldn't be loaded after importing registry
    assert "engine.modules.filters.tier1_structural" not in sys.modules
    
    # Request a filter
    f = registry.get("structural_odd_count")
    assert f is not None
    assert f.unique_id == "structural_odd_count"
    
    # NOW it should be in sys.modules
    assert "engine.modules.filters.tier1_structural" in sys.modules

def test_registry_resolution_speed():
    """AC 2.2.3: Registry resolution should be < 50ms."""
    import time
    from engine.modules.filters import registry
    
    start = time.perf_counter()
    f = registry.get("positional_successive_groups")
    end = time.perf_counter()
    
    elapsed_ms = (end - start) * 1000
    assert elapsed_ms < 50.0
    assert f is not None
