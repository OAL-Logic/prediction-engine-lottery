import pytest
import pandas as pd
from datetime import date
from unittest.mock import MagicMock
from engine.modules.narrative import NarrativeGenerator

@pytest.fixture
def mock_adapter():
    adapter = MagicMock()
    adapter.rules.name = "Mega Sena"
    adapter.rules.number_range = (1, 60)
    adapter.rules.pick_count = 6
    adapter.rules.bonus_count = 0
    return adapter

@pytest.fixture
def mock_df():
    # Need columns that frequency.analyze expects, like 'numbers'
    return pd.DataFrame({
        "draw_id": [1, 2], 
        "date": [pd.Timestamp(2026, 5, 1), pd.Timestamp(2026, 5, 2)],
        "numbers": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]
    })

@pytest.fixture
def mock_scan_results():
    return {
        "scan": {"score": 8, "max": 10, "verdict": "GO"},
        "regime": {"js": 0.01, "verdict": "STABLE"},
    }

def test_generate_briefing_v10_structure(mock_adapter, mock_df, mock_scan_results):
    gen = NarrativeGenerator(mock_adapter, mock_df, mock_scan_results)
    briefing = gen.generate_briefing_v10()
    
    assert "# Synapse Architect Report" in briefing
    assert "## 🌌 Physics (Regime Stability)" in briefing
    assert "## 🧠 Intelligence (Signal Synthesis)" in briefing
    assert "Leading Strategy Signals" in briefing
    assert "JS Divergence" in briefing
    assert "Mega Sena" in briefing

def test_generate_briefing_v10_persona(mock_adapter, mock_df, mock_scan_results):
    # Test default persona
    gen = NarrativeGenerator(mock_adapter, mock_df, mock_scan_results)
    briefing = gen.generate_briefing_v10()
    assert "Synapse Architect" in briefing
