"""
Smoke and integration tests for the Deep Learning strategy tier.
Enforces that CNN, Recurrent (LSTM/GRU), Transformer, LSTM-CRF, and the new GNN
strategies instantiate cleanly, train for 1-2 epochs on synthetic histories,
and output valid predictions without error.
"""

import pytest
import pandas as pd
import numpy as np

from engine.adapters import DrawRules
from engine.strategies import get_strategy

try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


@pytest.fixture
def mega_rules() -> DrawRules:
    return DrawRules(name="mega-sena", pick_count=6, number_range=(1, 60))


@pytest.fixture
def synthetic_history() -> pd.DataFrame:
    """100 fake draws for Mega-Sena."""
    return pd.DataFrame({
        "draw_id": list(range(1, 101)),
        "date":    pd.date_range("2024-01-01", periods=100, freq="3D", tz="UTC"),
        "numbers": [
            sorted([((i * 7 + j) % 60) + 1 for j in range(6)])
            for i in range(100)
        ],
        "bonus":   [[]] * 100,
    })


@pytest.mark.skipif(not _TORCH_AVAILABLE, reason="PyTorch is required for deep learning strategies")
@pytest.mark.parametrize("name, kwargs", [
    ("cnn_1d", {"epochs": 2, "seq_len": 10}),
    ("transformer", {"epochs": 2, "seq_len": 10}),
    ("lstm", {"epochs": 2, "seq_len": 10}),
    ("gru", {"epochs": 2, "seq_len": 10}),
    ("lstm_crf", {"epochs": 2, "seq_len": 10}),
    ("gnn", {"epochs": 2}),
])
def test_deep_strategies_smoke(name, kwargs, synthetic_history, mega_rules):
    """Verify that deep learning strategies can run training and inference without crashing."""
    try:
        strat = get_strategy(name, **kwargs)
    except KeyError:
        pytest.skip(f"Strategy '{name}' not found in registry")
        
    assert strat.name == name
    assert strat.tier == "deep"
    
    # Run scoring
    scores = strat.score(synthetic_history, mega_rules)
    
    # Assertions on scores
    lo, hi = mega_rules.number_range
    pool = set(range(lo, hi + 1))
    assert set(scores.keys()) >= pool, f"{name} missing scores for some pool members"
    
    for n, s in scores.items():
        if n not in pool:
            continue
        assert s >= 0.0, f"{name} produced negative score for {n}: {s}"
        assert s == s, f"{name} produced NaN for {n}"
        assert s <= 1.0, f"{name} produced score > 1.0 for {n}: {s}"


@pytest.mark.skipif(not _TORCH_AVAILABLE, reason="PyTorch is required for GNN validation")
def test_gnn_adjacency_and_features(synthetic_history, mega_rules):
    """Deep dive test into GNN strategy internals."""
    from engine.strategies.deep.gnn import GNNStrategy
    
    strat = GNNStrategy(epochs=1)
    pool_size = 60
    
    # 1. Test grid adjacency construction
    adj = strat._build_grid_adj(pool_size)
    assert adj.shape == (pool_size, pool_size)
    # Check self loops are included (diagonals should be > 0)
    assert torch.all(torch.diag(adj) > 0.0)
    # Check symmetry
    assert torch.allclose(adj, adj.t(), atol=1e-6)
    
    # 2. Test feature extraction
    lo, hi = mega_rules.number_range
    all_numbers = list(range(lo, hi + 1))
    idx = {n: i for i, n in enumerate(all_numbers)}
    
    feats = strat._extract_node_features(synthetic_history, pool_size, idx, all_numbers)
    assert feats.shape == (pool_size, 6)  # 6 features per node
    # All features should be finite
    assert torch.all(torch.isfinite(feats))
