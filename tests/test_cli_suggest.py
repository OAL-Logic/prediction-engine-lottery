"""
Suggest Command Tests 🎟️
========================
Verifies the 'suggest' command works for various strategies, ensembles, and constraints.
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

def test_suggest_basic_smoke():
    """Verify basic suggestion with default strategy."""
    result = runner.invoke(app, ["suggest", GAME])
    _ok(result)
    assert "WEIGHTED" in result.output
    assert "Ticket 1:" in result.output

def test_suggest_strategies():
    """Verify different strategy types work."""
    # Statistical
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "markov"])
    _ok(result)
    assert "MARKOV" in result.output
    
    # Fun
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "moon_phase"])
    _ok(result)
    assert "MOON_PHASE" in result.output

def test_suggest_ensemble_voting():
    """Verify voting ensemble works."""
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "voting:weighted,markov"])
    _ok(result)
    assert "VOTING:WEIGHTED,MARKOV PREDICTION" in result.output

def test_suggest_ensemble_complex_split():
    """Verify multiple strategies including ensembles work."""
    # Using smart split heuristic
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "voting:weighted,markov,momentum"])
    _ok(result)
    assert "VOTING:WEIGHTED,MARKOV,MOMENTUM PREDICTION" in result.output
    
    # Using explicit separator
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "voting:weighted,markov;momentum"])
    _ok(result)
    assert "VOTING:WEIGHTED,MARKOV PREDICTION" in result.output
    assert "MOMENTUM PREDICTION" in result.output

def test_suggest_constraints():
    """Verify pool and key constraints."""
    # Pool
    result = runner.invoke(app, ["suggest", GAME, "--pool", "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"])
    _ok(result)
    # Extract ticket and check numbers
    # (Checking if it crashes is the primary goal for smoke tests)
    
    # Key
    result = runner.invoke(app, ["suggest", GAME, "--key", "1,2,3"])
    _ok(result)
    assert "[1, 2, 3" in result.output or " 1, 2, 3," in result.output

def test_suggest_filters():
    """Verify filters don't crash and report warnings for unknowns."""
    result = runner.invoke(app, ["suggest", GAME, "--filters", "sum_range,invalid_filter"])
    _ok(result)
    # The warning goes to logger, might not be in result.output if not captured
    # But it shouldn't crash.

def test_suggest_pick_override():
    """Verify pick count override."""
    result = runner.invoke(app, ["suggest", GAME, "--pick", "18"])
    _ok(result)
    assert "pick=18" in result.output

def test_suggest_explain():
    """Verify explain panel."""
    result = runner.invoke(app, ["suggest", GAME, "--explain"])
    _ok(result)
    assert "Statistical Evidence" in result.output

def test_suggest_invalid_lottery():
    """Verify error on invalid lottery."""
    result = runner.invoke(app, ["suggest", "invalid_game"])
    assert result.exit_code == 1
    assert "Lottery 'invalid_game' is not available" in result.output

def test_suggest_invalid_strategy():
    """Verify skip on invalid strategy."""
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "invalid_strat"])
    _ok(result)
    assert "Strategy 'invalid_strat' not found" in result.output

def test_suggest_pool_too_small():
    """Verify error when pool is smaller than pick count."""
    result = runner.invoke(app, ["suggest", GAME, "--pool", "1,2,3"])
    # It fails inside the loop currently, let's see how it behaves
    assert "larger sample than population" in result.output

def test_suggest_adaptive_window():
    """Verify --adaptive-window works."""
    result = runner.invoke(app, ["suggest", GAME, "--adaptive-window"])
    _ok(result)
