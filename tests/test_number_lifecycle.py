"""Number Lifecycle CLI Tests 🧬"""

from __future__ import annotations

import pandas as pd
from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.number_lifecycle import compute_lifecycle

runner = CliRunner()
GAME = "br/mega-sena"


def _df(rows):
    return pd.DataFrame([{"draw_id": i + 1, "date": f"2026-01-{i+1:02d}", "numbers": nums} for i, nums in enumerate(rows)])


def test_compute_lifecycle_never_hit():
    df = _df([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    stats = compute_lifecycle(df, 99)
    assert stats["total_hits"] == 0
    assert stats["hit_rate"] == 0.0


def test_compute_lifecycle_gaps_and_streak():
    # number 5 hits at indices 1, 2, 4 (0-based) out of 5 draws
    df = _df([[1], [5], [5], [9], [5]])
    stats = compute_lifecycle(df, 5)
    assert stats["total_hits"] == 3
    assert stats["first_draw"] == 2  # draw_id at index 1
    assert stats["last_draw"] == 5
    assert stats["current_gap"] == 0  # hit in the very last draw
    assert stats["longest_streak"] == 2  # indices 1,2 are consecutive


def test_number_lifecycle_registered_and_runs():
    result = runner.invoke(app, ["number-lifecycle", GAME, "10"])
    assert result.exit_code == 0, result.output
    assert "NUMBER LIFECYCLE" in result.output


def test_number_lifecycle_rejects_out_of_range():
    result = runner.invoke(app, ["number-lifecycle", GAME, "999"])
    assert result.exit_code != 0
