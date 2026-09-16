"""Config Check CLI Tests 🩺"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.config_check import check_environment

runner = CliRunner()


def test_check_environment_reports_real_registry():
    result = check_environment()
    assert result["registry_ok"] is True
    assert result["game_count"] > 0
    assert "duckdb" in result["packages"]
    assert isinstance(result["local_configs"], list)


def test_check_environment_is_read_only(tmp_path, monkeypatch):
    # Confirm this never writes anything, regardless of data dir state.
    before = list(tmp_path.iterdir())
    monkeypatch.chdir(tmp_path)
    check_environment()
    after = list(tmp_path.iterdir())
    assert before == after


def test_config_check_registered_and_runs():
    result = runner.invoke(app, ["config-check"])
    assert result.exit_code == 0, result.output
    assert "CONFIG CHECK" in result.output
    assert "healthy" in result.output.lower()
