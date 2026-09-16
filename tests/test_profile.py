"""
Profile CLI Tests 💾
====================
All tests monkeypatch PROFILES_FILE to a tmp_path so the real
data/profiles.json is never touched.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from engine.cli.main import app
import engine.cli.commands.profile as profile_mod

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_profiles(tmp_path, monkeypatch):
    monkeypatch.setattr(profile_mod, "PROFILES_FILE", tmp_path / "profiles.json")
    monkeypatch.setattr(profile_mod, "DATA_DIR", tmp_path)


def test_save_list_show_roundtrip():
    save_result = runner.invoke(app, ["profile", "save", "mega3", "--command", "suggest br/mega-sena --count 3", "--description", "quick 3"])
    assert save_result.exit_code == 0, save_result.output

    list_result = runner.invoke(app, ["profile", "list"])
    assert list_result.exit_code == 0
    assert "mega3" in list_result.output

    show_result = runner.invoke(app, ["profile", "show", "mega3"])
    assert show_result.exit_code == 0
    assert "suggest br/mega-sena --count 3" in show_result.output


def test_show_unknown_profile_fails():
    result = runner.invoke(app, ["profile", "show", "does-not-exist"])
    assert result.exit_code != 0


def test_delete_profile():
    runner.invoke(app, ["profile", "save", "temp", "--command", "games"])
    delete_result = runner.invoke(app, ["profile", "delete", "temp"])
    assert delete_result.exit_code == 0

    show_result = runner.invoke(app, ["profile", "show", "temp"])
    assert show_result.exit_code != 0


def test_save_rejects_empty_command():
    result = runner.invoke(app, ["profile", "save", "bad", "--command", "   "])
    assert result.exit_code != 0


def test_run_replays_saved_command():
    runner.invoke(app, ["profile", "save", "list-games", "--command", "games"])
    result = runner.invoke(app, ["profile", "run", "list-games"])
    assert result.exit_code == 0, result.output
    # `games` lists the registered lotteries; mega-sena should appear either
    # way, proving the nested invocation actually ran the real command.
    assert "mega" in result.output.lower()
