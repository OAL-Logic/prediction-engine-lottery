"""Data Status CLI Tests 📡📋"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app

runner = CliRunner()


def test_data_status_registered_and_runs():
    result = runner.invoke(app, ["data-status"])
    assert result.exit_code == 0, result.output
    assert "DATA STATUS" in result.output
    assert "mega-sena" in result.output.lower() or "mega_sena" in result.output.lower()


def test_data_status_all_flag_does_not_crash():
    result = runner.invoke(app, ["data-status", "--all"])
    assert result.exit_code == 0, result.output
    assert "DATA STATUS" in result.output
