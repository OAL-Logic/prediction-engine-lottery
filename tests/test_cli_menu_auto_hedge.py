"""
Unit Tests for CLI Menu and Auto-Hedge Commands
===============================================
Verifies that ./p4lottery menu and ./p4lottery auto-hedge execute cleanly.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from engine.cli.main import app

runner = CliRunner()


def test_cli_menu_help():
    """Verify ./p4lottery menu --help."""
    result = runner.invoke(app, ["menu", "--help"])
    assert result.exit_code == 0
    assert "Interactive CLI Command Center" in result.output


def test_cli_menu_quit_input():
    """Verify selecting 'q' exits menu cleanly."""
    result = runner.invoke(app, ["menu"], input="q\n")
    assert result.exit_code == 0
    assert "P4LOTTERY: UNIFIED COMMAND CENTER" in result.output
    assert "Exiting command center" in result.output


def test_cli_auto_hedge_help():
    """Verify ./p4lottery auto-hedge --help."""
    result = runner.invoke(app, ["auto-hedge", "--help"])
    assert result.exit_code == 0
    assert "Optimize betting surface area" in result.output
    assert "--budget" in result.output
    assert "--zx" in result.output
    assert "--zy" in result.output


def test_cli_auto_hedge_execution():
    """Verify ./p4lottery auto-hedge runs for Mega-Sena."""
    result = runner.invoke(app, ["auto-hedge", "br/mega-sena", "--budget", "30.0", "--zx", "2", "--zy", "2"])
    assert result.exit_code == 0
