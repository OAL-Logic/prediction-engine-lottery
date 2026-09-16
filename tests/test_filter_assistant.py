"""
Filter Assistant CLI Tests 🧙‍♂️
================================
Drives the interactive prompts via CliRunner's `input=` stdin simulation.
"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
import engine.cli.commands.profile as profile_mod

runner = CliRunner()
GAME = "br/mega-sena"


def test_no_filters_selected_exits_cleanly():
    # Blank at every one of the 5 tier prompts.
    result = runner.invoke(app, ["filter-assistant", GAME], input="\n\n\n\n\n")
    assert result.exit_code == 0, result.output
    assert "No filters selected" in result.output


def test_picks_one_filter_and_runs_funnel_without_saving():
    inputs = "structural_odd_count\n\n\n\n\n1,2,3,4,5,6,7,8,9,10,11\nn\n"
    result = runner.invoke(app, ["filter-assistant", GAME], input=inputs)
    assert result.exit_code == 0, result.output
    assert "Selected filters:" in result.output
    assert "FILTER FUNNEL" in result.output


def test_unknown_filter_id_warns_but_continues():
    inputs = "not_a_real_id\n\n\n\n\n1,2,3,4,5,6,7,8,9,10,11\nn\n"
    result = runner.invoke(app, ["filter-assistant", GAME], input=inputs)
    assert result.exit_code == 0, result.output
    assert "Unknown filter id" in result.output
    assert "No filters selected" in result.output  # the unknown id never got added


def test_save_as_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(profile_mod, "PROFILES_FILE", tmp_path / "profiles.json")
    monkeypatch.setattr(profile_mod, "DATA_DIR", tmp_path)

    inputs = "structural_odd_count\n\n\n\n\n1,2,3,4,5,6,7,8,9,10,11\ny\nmy-recipe\n"
    result = runner.invoke(app, ["filter-assistant", GAME], input=inputs)
    assert result.exit_code == 0, result.output
    assert "Saved profile" in result.output

    show_result = runner.invoke(app, ["profile", "show", "my-recipe"])
    assert show_result.exit_code == 0
    assert "filter-funnel" in show_result.output
