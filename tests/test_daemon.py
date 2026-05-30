"""
Unit and integration tests for the AutoML Background Daemon and its closed-loop ensemble integration.
"""

import json
from pathlib import Path
import pytest
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import get_strategy


@pytest.fixture
def mega_rules() -> DrawRules:
    return DrawRules(
        name="mega-sena",
        pick_count=6,
        number_range=(1, 60),
        prize_tiers=[4, 5, 6],
        ticket_price=5.0,
        currency="BRL"
    )


@pytest.fixture
def synthetic_history() -> pd.DataFrame:
    return pd.DataFrame({
        "draw_id": list(range(1, 101)),
        "date":    pd.date_range("2024-01-01", periods=100, freq="3D", tz="UTC"),
        "numbers": [
            sorted([((i * 7 + j) % 60) + 1 for j in range(6)])
            for i in range(100)
        ],
        "bonus":   [[]] * 100,
    })


def test_daemon_optimization_cycle(synthetic_history):
    from engine.cli.commands.daemon import _run_optimization_cycle
    
    # We mock get_adapter to return a custom adapter with our synthetic history
    from unittest.mock import patch, MagicMock
    mock_adapter = MagicMock()
    mock_adapter.rules = DrawRules(name="mega-sena", pick_count=6, number_range=(1, 60))
    mock_adapter.fetch.return_value = synthetic_history
    
    with patch("engine.cli.commands.daemon.get_adapter", return_value=mock_adapter):
        best_config, strat_weights = _run_optimization_cycle(
            lottery="mega-sena",
            limit=50,
            history_windows=[30, 40],
            prev=3
        )
        
        assert "strategy" in best_config
        assert "capture_rate" in best_config
        assert len(strat_weights) > 0
        assert all(isinstance(v, float) for v in strat_weights.values())


def test_voting_ensemble_closed_loop_weights(synthetic_history, mega_rules):
    # Ensure any previous state is ignored
    state_file = Path("data/daemon_state.json")
    original_content = None
    if state_file.exists():
        original_content = state_file.read_text()

    try:
        # Create a mock daemon_state.json with skewed weights
        state_file.parent.mkdir(parents=True, exist_ok=True)
        mock_state = {
            "mega-sena": {
                "last_optimized": "2026-05-30 00:00:00",
                "best_strategy": "weighted",
                "optimal_limit": 50,
                "optimal_temp": 0.0,
                "capture_rate": 80.0,
                "strategy_weights": {
                    "weighted": 100.0,
                    "markov": 0.0,
                    "bayesian": 0.0,
                    "momentum": 0.0
                }
            }
        }
        state_file.write_text(json.dumps(mock_state))

        # Instantiate voting ensemble
        voting = get_strategy("voting", members=["weighted", "markov", "bayesian", "momentum"])
        
        # When we score, it should load the daemon state and apply weight 100.0 to 'weighted'
        # and 0.0 to the rest, meaning the scores should equal the 'weighted' strategy scores exactly!
        weighted_strat = get_strategy("weighted")
        
        scores_voting = voting.score(synthetic_history, mega_rules)
        scores_weighted = weighted_strat.score(synthetic_history, mega_rules)
        
        # Verify they are very close / identical because all other strategy weights were zeroed out
        for n in scores_voting:
            assert abs(scores_voting[n] - scores_weighted[n]) < 1e-4

    finally:
        # Restore original daemon state
        if original_content is not None:
            state_file.write_text(original_content)
        elif state_file.exists():
            state_file.unlink()
