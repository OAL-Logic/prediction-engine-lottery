"""
Analyze Command Tests 📊
========================
Verifies all modules of the 'analyze' command work correctly.
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

def test_analyze_frequency_smoke():
    """Verify frequency analysis module."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "frequency"])
    _ok(result)
    assert "Frequency Analysis" in result.output
    assert "Hot:" in result.output
    assert "Cold:" in result.output
    assert "Chi-squared P-value" in result.output

def test_analyze_deviation_smoke():
    """Verify deviation (overdue) analysis module."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "deviation"])
    _ok(result)
    assert "Deviation Analysis" in result.output
    assert "Overdue" in result.output
    assert "Last Seen" in result.output

def test_analyze_correlation_smoke():
    """Verify correlation analysis module."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "correlation"])
    _ok(result)
    assert "Top Associated Pairs" in result.output
    assert "Top Avoided Pairs" in result.output
    assert "Top Triplets" in result.output

def test_analyze_dashboard_smoke():
    """Verify dashboard module."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "dashboard"])
    _ok(result)
    assert "Statistical Anomalies & Alerts" in result.output
    assert "Automated Insight Ribbon" in result.output

def test_analyze_summary_smoke():
    """Verify summary module (minimalist output)."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "summary"])
    _ok(result)
    assert "Hot Numbers:" in result.output
    assert "Cold Numbers:" in result.output
    assert "Overdue:" in result.output

def test_analyze_limit():
    """Verify --limit works."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "frequency", "--limit", "10"])
    _ok(result)
    assert "Frequency Analysis" in result.output

def test_analyze_top():
    """Verify --top works."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "frequency", "--top", "5"])
    _ok(result)
    assert "Rank" in result.output

def test_analyze_unknown_module():
    """Verify error on unknown module."""
    result = runner.invoke(app, ["analyze", GAME, "-m", "nonexistent"])
    assert result.exit_code == 1
    assert "Unknown module 'nonexistent'" in result.output

def test_standalone_dashboard_smoke():
    """Verify standalone 'dashboard' command works."""
    result = runner.invoke(app, ["dashboard", GAME])
    _ok(result)
    assert "Statistical Anomalies & Alerts" in result.output
