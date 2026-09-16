"""Ticket Backtest CLI Tests ⏮️"""

from __future__ import annotations

import pandas as pd
from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.ticket_backtest import replay_ticket

runner = CliRunner()
GAME = "br/mega-sena"


def _df(rows):
    return pd.DataFrame([{"draw_id": i + 1, "date": f"2026-01-{i+1:02d}", "numbers": nums} for i, nums in enumerate(rows)])


def test_replay_ticket_counts_hits_per_tier():
    df = _df([
        [1, 2, 3, 10, 11, 12],   # 3 hits with {1,2,3,4,5,6}
        [1, 2, 3, 4, 5, 6],       # 6 hits (jackpot)
        [7, 8, 9, 10, 11, 12],    # 0 hits
    ])
    result = replay_ticket(df, {1, 2, 3, 4, 5, 6}, prize_tiers=[4, 5, 6])
    assert result["hit_counts"].get(6) == 1
    assert result["best_ever"] == 6
    assert result["best_draw"] == (2, "2026-01-02")
    assert result["total_draws"] == 3


def test_ticket_backtest_registered_and_runs():
    result = runner.invoke(app, ["ticket-backtest", GAME, "1,2,3,4,5,6"])
    assert result.exit_code == 0, result.output
    assert "TICKET BACKTEST" in result.output


def test_ticket_backtest_rejects_invalid_ticket():
    result = runner.invoke(app, ["ticket-backtest", GAME, "1,2,3"])
    assert result.exit_code != 0
