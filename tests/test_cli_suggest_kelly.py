import pytest
from typer.testing import CliRunner
from engine.cli.main import app
from unittest.mock import patch, MagicMock
import pandas as pd

runner = CliRunner()

def test_suggest_kelly_smoke():
    """Smoke test to ensure suggest command with --kelly doesn't crash."""
    with patch("engine.cli.utils.get_adapter") as mock_get_adapter:
        # Mock adapter
        mock_adapter = MagicMock()
        mock_adapter.rules.name = "Test Lottery"
        mock_adapter.rules.number_range = (1, 60)
        mock_adapter.rules.pick_count = 6
        mock_adapter.rules.jackpot_odds = 1000000
        mock_adapter.rules.ticket_price = 5.0
        mock_adapter.rules.currency = "BRL"
        mock_adapter.rules.prize_tiers = [4, 5, 6]
        
        # Mock fetch data
        mock_df = pd.DataFrame({
            "draw_id": range(1, 101),
            "date": pd.date_range("2026-01-01", periods=100),
            "numbers": [[1, 2, 3, 4, 5, 6]] * 100
        })
        mock_adapter.fetch.return_value = mock_df
        mock_get_adapter.return_value = mock_adapter

        # Run command
        result = runner.invoke(app, ["suggest", "br/mega-sena", "--kelly", "1000"])
        print(f"DEBUG CLI OUTPUT: {result.stdout}")
        assert result.exit_code == 0
        assert "Bankroll Optimization (Kelly)" in result.stdout
        assert "Recommended Bet" in result.stdout
        assert "tickets" in result.stdout
