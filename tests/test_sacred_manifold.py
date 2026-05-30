"""
Smoke and unit tests for the Sacred Manifold Strategy and Grid visualizer.
"""

from datetime import date
import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.strategies import get_strategy
from engine.modules.geometry import get_manifold_coords, calculate_symmetry_metrics
from engine.cli.commands.board import _render_sacred_view

@pytest.fixture
def lotofacil_rules() -> DrawRules:
    return DrawRules(name="lotofacil", pick_count=15, number_range=(1, 25), board_cols=5)

@pytest.fixture
def synthetic_history() -> pd.DataFrame:
    """10 draws for LotoFácil."""
    return pd.DataFrame({
        "draw_id": list(range(1, 11)),
        "date":    pd.date_range("2026-01-01", periods=10, freq="1D", tz="UTC"),
        "numbers": [
            sorted([((i * 3 + j) % 25) + 1 for j in range(15)])
            for i in range(10)
        ],
        "bonus":   [[]] * 10,
    })

def test_get_manifold_coords(lotofacil_rules):
    # Test sphere coordinates
    x, y, z = get_manifold_coords(1, lotofacil_rules, "sphere")
    assert isinstance(x, float)
    assert isinstance(y, float)
    assert isinstance(z, float)
    
    # Test cylinder coordinates
    x, y, z = get_manifold_coords(5, lotofacil_rules, "cylinder")
    assert isinstance(x, float)
    assert isinstance(y, float)
    assert isinstance(z, float)

    # Test hexagonal coordinates
    x, y, z = get_manifold_coords(10, lotofacil_rules, "hexagonal")
    assert isinstance(x, float)
    assert isinstance(y, float)
    assert z == 0.0

def test_calculate_symmetry_metrics(lotofacil_rules):
    ticket = [2, 3, 4, 5, 10, 12, 15, 16, 17, 18, 20, 21, 23, 24, 25]
    metrics = calculate_symmetry_metrics(ticket, lotofacil_rules, "sphere")
    
    assert "center_of_mass" in metrics
    assert "resonance" in metrics
    assert "reflection_h" in metrics
    assert "reflection_v" in metrics
    assert "symmetry_grade" in metrics
    
    assert isinstance(metrics["resonance"], float)
    assert 0.0 <= metrics["resonance"] <= 1.0
    assert 0.0 <= metrics["symmetry_grade"] <= 100.0

def test_sacred_manifold_strategy(synthetic_history, lotofacil_rules):
    # Retrieve strategy from registry
    strat = get_strategy("sacred_manifold")
    assert strat.name == "sacred_manifold"
    assert strat.tier == "fun"
    
    # Generate scores
    scores = strat.score(synthetic_history, lotofacil_rules)
    assert len(scores) == 25
    for num, s in scores.items():
        assert 1 <= num <= 25
        assert 0.0 <= s <= 1.0

def test_render_sacred_view_smoke(lotofacil_rules):
    # Basic smoke test for grid visualizer output rendering
    ticket = {2, 3, 4, 5, 10, 12, 15, 16, 17, 18, 20, 21, 23, 24, 25}
    try:
        _render_sacred_view(ticket, lotofacil_rules.board_cols, lotofacil_rules)
    except Exception as e:
        pytest.fail(f"_render_sacred_view failed with exception: {e}")
