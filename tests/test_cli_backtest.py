"""
Backtest Command Tests 🔬
=========================
Verifies the 'backtest' command works for various draw selections and strategies.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner
from engine.cli.main import app

runner = CliRunner()
GAME = "br/lotofacil"

def _ok(result):
    assert result.exit_code == 0, f"Exit {result.exit_code}:\n{result.output}"
    assert result.output.strip(), "Command produced no output"

def test_backtest_prev_single():
    """Verify --prev 1 works."""
    result = runner.invoke(app, ["backtest", GAME, "--prev", "1", "--strategy", "weighted"])
    _ok(result)
    assert "BACKTEST — Lotofácil Draw" in result.output
    assert "Winning Numbers:" in result.output
    assert "Simulating strategy: weighted" in result.output

def test_backtest_prev_range():
    """Verify --prev range works."""
    # Using 2-3 to avoid hitting too many draws
    result = runner.invoke(app, ["backtest", GAME, "--prev", "1-2", "--strategy", "weighted"])
    _ok(result)
    # Should have two backtest sections
    assert result.output.count("BACKTEST — Lotofácil Draw") == 2

def test_backtest_draw_id_single():
    """Verify explicit draw_id works."""
    result = runner.invoke(app, ["backtest", GAME, "3670", "--strategy", "weighted"])
    _ok(result)
    assert "Draw 3670" in result.output

def test_backtest_draw_id_range():
    """Verify draw_id range works."""
    result = runner.invoke(app, ["backtest", GAME, "3660-3661", "--strategy", "weighted"])
    _ok(result)
    assert result.output.count("BACKTEST — Lotofácil Draw") == 2

def test_backtest_multiple_strategies():
    """Verify multiple strategies in backtest."""
    result = runner.invoke(app, ["backtest", GAME, "--prev", "1", "--strategy", "markov,weighted"])
    _ok(result)
    assert "Simulating strategy: markov" in result.output
    assert "Simulating strategy: weighted" in result.output

def test_backtest_limit():
    """Verify --limit in backtest."""
    result = runner.invoke(app, ["backtest", GAME, "--prev", "1", "--strategy", "weighted", "--limit", "50"])
    _ok(result)
    assert "Limit:  50" in result.output

def test_backtest_no_summary():
    """Verify --no-summary works."""
    result = runner.invoke(app, ["backtest", GAME, "--prev", "1", "--strategy", "weighted", "--no-summary"])
    _ok(result)
    assert "BACKTEST COMPARISON SUMMARY" not in result.output

def test_backtest_invalid_draw():
    """Verify error on invalid draw ID."""
    result = runner.invoke(app, ["backtest", GAME, "999999"])
    assert result.exit_code == 1
    assert "No draws found to test" in result.output

def test_backtest_no_input():
    """Verify error when neither draw_id nor --prev is provided."""
    result = runner.invoke(app, ["backtest", GAME])
    assert result.exit_code == 2
    assert "Provide either DRAW_ID(s) or use --prev/-p" in result.output
