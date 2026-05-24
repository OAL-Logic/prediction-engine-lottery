import pytest
import random
from unittest.mock import MagicMock
from engine.modules.cosmic import simulate_muon_strike

@pytest.fixture
def mock_rules():
    rules = MagicMock()
    rules.number_range = (1, 60)
    return rules

def test_muon_strike_no_mutation(mock_rules):
    # Set seed to ensure no mutation for high threshold
    local_rng = random.Random(42)
    ticket = [1, 2, 3, 4, 5, 6]
    # We need to mock EnvironmentalService or rely on default
    mutated, struck = simulate_muon_strike(ticket, mock_rules, local_rng)
    # With 0.5% chance, seed 42 likely won't hit
    if not struck:
        assert mutated == ticket
    else:
        assert len(mutated) == 6
        assert all(1 <= n <= 60 for n in mutated)

def test_muon_strike_force_mutation(mock_rules):
    local_rng = MagicMock()
    # Force strike (local_rng.random() < 0.005)
    local_rng.random.return_value = 0.001
    local_rng.randint.side_effect = [0, 2] # mutate index 0, bit_mask 4
    
    ticket = [10, 20, 30, 40, 50, 60]
    # 10 ^ 4 = 14
    mutated, struck = simulate_muon_strike(ticket, mock_rules, local_rng)
    
    assert struck is True
    assert 14 in mutated
    assert len(mutated) == 6
    assert all(1 <= n <= 60 for n in mutated)

def test_muon_strike_boundary_safety(mock_rules):
    local_rng = MagicMock()
    local_rng.random.return_value = 0.001
    local_rng.randint.side_effect = [0, 5] # mutate index 0, bit_mask 32
    
    # 60 ^ 32 = 28
    ticket = [60, 20, 30, 40, 50, 59]
    mutated, struck = simulate_muon_strike(ticket, mock_rules, local_rng)
    assert struck is True
    assert all(1 <= n <= 60 for n in mutated)
    assert len(set(mutated)) == 6 # No collisions
