"""
Record CLI Tests 📝
===================
`record` lets a user manually add/correct a single draw (the "DrawingsUpdate"
equivalent) when no automated `fetch` source has it yet. Writes must be
isolated to a throwaway DuckDB file — never the real data/lottery.db.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.record import record
from engine.modules.storage import LotteryStorage

runner = CliRunner()
GAME = "br/mega-sena"


def test_record_dry_run_does_not_write():
    result = runner.invoke(app, [
        "record", GAME,
        "--draw-id", "999999", "--date", "2026-01-01",
        "--numbers", "1,2,3,4,5,6", "--dry-run",
    ])
    assert result.exit_code == 0, result.output
    assert "DRY RUN" in result.output


def test_record_rejects_invalid_ticket():
    result = runner.invoke(app, [
        "record", GAME,
        "--draw-id", "999999", "--date", "2026-01-01",
        "--numbers", "1,2,3",  # mega-sena needs 6 numbers
    ])
    assert result.exit_code != 0
    assert "not a valid ticket" in result.output


def test_record_rejects_bad_date():
    result = runner.invoke(app, [
        "record", GAME,
        "--draw-id", "999999", "--date", "not-a-date",
        "--numbers", "1,2,3,4,5,6",
    ])
    assert result.exit_code != 0
    assert "Invalid --date" in result.output


def test_record_writes_and_is_loadable(tmp_path, monkeypatch):
    # policy=primary -> save_draws/load_draws touch ONLY the DuckDB file we
    # point at, never the real data/inspections/ JSON partitions.
    monkeypatch.setenv("LOTTERY_STORAGE_POLICY", "primary")
    db_path = tmp_path / "isolated.db"

    record(
        lottery=GAME, draw_id=999999, date="2026-01-01",
        numbers="6,5,4,3,2,1", bonus="", dry_run=False, db_path=db_path,
    )

    df = LotteryStorage(db_path=db_path).load_draws(GAME)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["draw_id"] == 999999
    assert sorted(row["numbers"]) == [1, 2, 3, 4, 5, 6]


def test_record_upserts_on_same_draw_id(tmp_path, monkeypatch):
    monkeypatch.setenv("LOTTERY_STORAGE_POLICY", "primary")
    db_path = tmp_path / "isolated.db"

    record(lottery=GAME, draw_id=999999, date="2026-01-01",
           numbers="1,2,3,4,5,6", bonus="", dry_run=False, db_path=db_path)
    record(lottery=GAME, draw_id=999999, date="2026-01-01",
           numbers="10,20,30,40,50,60", bonus="", dry_run=False, db_path=db_path)

    df = LotteryStorage(db_path=db_path).load_draws(GAME)
    assert len(df) == 1  # corrected in place, not duplicated
    assert sorted(df.iloc[0]["numbers"]) == [10, 20, 30, 40, 50, 60]
