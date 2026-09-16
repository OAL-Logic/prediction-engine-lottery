"""
Twin Draws CLI Tests 👯
=======================
"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.twin_draws import _bitmask, find_twin_draws

runner = CliRunner()
GAME = "br/mega-sena"


def test_bitmask_roundtrip_via_popcount():
    assert _bitmask([1, 2, 3]).bit_count() == 3
    assert _bitmask([1, 2, 3]) & _bitmask([3, 4, 5]) == _bitmask([3])


def test_find_twin_draws_picks_highest_overlap():
    rows = [
        (1, _bitmask([1, 2, 3, 4, 5, 6])),
        (2, _bitmask([1, 2, 3, 4, 5, 7])),   # overlap 5 with draw 1
        (3, _bitmask([10, 11, 12, 13, 14, 15])),  # overlap 0 with everything
    ]
    top = find_twin_draws(rows, top=2)
    best_overlap, i, j = top[0]
    assert best_overlap == 5
    assert {rows[i][0], rows[j][0]} == {1, 2}


def test_twin_draws_registered_and_runs():
    result = runner.invoke(app, ["twin-draws", GAME, "--top", "3", "--limit", "150"])
    assert result.exit_code == 0, result.output
    assert "TWIN DRAWS" in result.output


def test_twin_draws_rejects_insufficient_history():
    result = runner.invoke(app, ["twin-draws", GAME, "--limit", "1"])
    assert result.exit_code != 0
