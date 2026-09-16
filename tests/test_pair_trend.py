"""Pair Trend CLI Tests 📈"""

from __future__ import annotations

import pandas as pd
from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.pair_trend import rolling_cooccurrence

runner = CliRunner()
GAME = "br/mega-sena"


def _df(rows):
    return pd.DataFrame([{"draw_id": i + 1, "numbers": nums} for i, nums in enumerate(rows)])


def test_rolling_cooccurrence_basic_windows():
    # 6 draws, window=2, step=2 -> 3 windows
    rows = [[1, 2], [1, 2], [3, 4], [1, 2], [5, 6], [7, 8]]
    df = _df(rows)
    points = rolling_cooccurrence(df, 1, 2, window=2, step=2)
    assert len(points) == 3
    assert points[0][2] == 1.0  # both draws in first window have 1&2
    assert points[1][2] == 0.5  # only one of the two draws in second window
    assert points[2][2] == 0.0


def test_pair_trend_registered_and_runs():
    result = runner.invoke(app, ["pair-trend", GAME, "1", "2", "--window", "50", "--step", "25"])
    assert result.exit_code == 0, result.output
    assert "PAIR TREND" in result.output


def test_pair_trend_rejects_same_number():
    result = runner.invoke(app, ["pair-trend", GAME, "5", "5"])
    assert result.exit_code != 0


def test_pair_trend_rejects_out_of_range():
    result = runner.invoke(app, ["pair-trend", GAME, "1", "999"])
    assert result.exit_code != 0
