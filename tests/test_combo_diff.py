"""Combo Diff CLI Tests 🆚"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app

runner = CliRunner()
GAME = "br/mega-sena"


def test_combo_diff_registered_and_runs():
    result = runner.invoke(app, ["combo-diff", GAME, "--a", "1,2,3,4,5,6", "--b", "4,5,6,7,8,9"])
    assert result.exit_code == 0, result.output
    assert "COMBO DIFF" in result.output


def test_combo_diff_shared_and_unique_sets():
    result = runner.invoke(app, ["combo-diff", GAME, "--a", "1,2,3,4,5,6", "--b", "4,5,6,7,8,9"])
    assert "[4, 5, 6]" in result.output  # shared
    assert "[1, 2, 3]" in result.output  # only in A
    assert "[7, 8, 9]" in result.output  # only in B


def test_combo_diff_sum_delta():
    result = runner.invoke(app, ["combo-diff", GAME, "--a", "1,2,3,4,5,6", "--b", "10,20,30,40,50,60"])
    assert result.exit_code == 0
    assert "+189" in result.output  # sum(B)=210, sum(A)=21, delta=+189


def test_combo_diff_rejects_empty_ticket():
    result = runner.invoke(app, ["combo-diff", GAME, "--a", "", "--b", "1,2,3"])
    assert result.exit_code != 0
