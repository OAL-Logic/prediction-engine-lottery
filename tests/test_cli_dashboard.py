"""
Dashboard Command Tests 📈
==========================
Verifies the unified dashboard command and its integration with the analysis modules.
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

def test_dashboard_smoke():
    """Basic smoke test for the dashboard command."""
    result = runner.invoke(app, ["dashboard", GAME, "--view", "legacy"])
    _ok(result)
    assert "LottoLogic Terminal Dashboard" in result.output
    assert "Market Overview" in result.output
    assert "Automated Insight Ribbon" in result.output
    assert "Top Performers" in result.output

def test_dashboard_limit():
    """Verify the --limit option in dashboard."""
    result = runner.invoke(app, ["dashboard", GAME, "--limit", "50", "--view", "legacy"])
    _ok(result)
    assert "Window: last 50" in result.output

def test_dashboard_invalid_lottery():
    """Verify error handling for invalid lottery."""
    result = runner.invoke(app, ["dashboard", "nonexistent/lottery"])
    assert result.exit_code == 1
    assert "is not available" in result.output

def test_dashboard_small_limit():
    """Verify dashboard works with a very small limit."""
    result = runner.invoke(app, ["dashboard", GAME, "--limit", "5", "--view", "legacy"])
    _ok(result)
    assert "Window: last 5" in result.output

def test_analyze_vs_dashboard_integration():
    """Verify that 'analyze -m dashboard' produces similar output to 'dashboard'."""
    res_analyze = runner.invoke(app, ["analyze", GAME, "-m", "dashboard", "--view", "legacy"])
    res_dash = runner.invoke(app, ["dashboard", GAME, "--view", "legacy"])
    
    _ok(res_analyze)
    _ok(res_dash)
    
    # Both should contain the core dashboard markers
    assert "LottoLogic Terminal Dashboard" in res_analyze.output
    assert "LottoLogic Terminal Dashboard" in res_dash.output
    assert "Automated Insight Ribbon" in res_analyze.output
    assert "Automated Insight Ribbon" in res_dash.output
