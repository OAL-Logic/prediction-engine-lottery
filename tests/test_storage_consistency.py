"""
Storage Consistency CLI Tests 🗄️🔍
===================================
Uses the real LotteryStorage against an isolated tmp DB/JSON dir so the
real data/lottery.db and data/inspections/ are never touched.
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.modules.storage import LotteryStorage
import engine.cli.commands.storage_consistency as sc_mod

runner = CliRunner()
GAME = "br/mega-sena"


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    db_path = tmp_path / "iso.db"
    inspection_dir = tmp_path / "inspections"
    monkeypatch.setattr(sc_mod, "DB_PATH", db_path)
    monkeypatch.setattr(sc_mod, "INSPECTION_DIR", inspection_dir)
    storage = LotteryStorage(db_path=db_path)
    # save_draws' JSON side always writes under the real module's INSPECTION_DIR
    # unless we also monkeypatch the storage module itself.
    import engine.modules.storage as storage_mod
    monkeypatch.setattr(storage_mod, "INSPECTION_DIR", inspection_dir)
    return storage, db_path, inspection_dir


def test_no_data_reports_empty(isolated):
    result = runner.invoke(app, ["storage-consistency", GAME])
    assert result.exit_code != 0


def test_consistent_when_written_together(isolated):
    storage, db_path, inspection_dir = isolated
    storage.save_draws(GAME, [{"draw_id": 1, "draw_date": "2026-01-01", "numbers": [1, 2, 3, 4, 5, 6], "bonus": []}])

    result = runner.invoke(app, ["storage-consistency", GAME])
    assert result.exit_code == 0, result.output
    assert "Consistent" in result.output


def test_detects_json_only_draw(isolated):
    storage, db_path, inspection_dir = isolated
    storage.save_draws(GAME, [{"draw_id": 1, "draw_date": "2026-01-01", "numbers": [1, 2, 3, 4, 5, 6], "bonus": []}])

    # Manually inject an extra draw into the JSON side only.
    out_dir = inspection_dir / GAME.replace("/", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "2026.json"
    data = json.loads(path.read_text())
    data.append({"draw_id": 2, "draw_date": "2026-01-08", "numbers": [7, 8, 9, 10, 11, 12], "bonus": []})
    path.write_text(json.dumps(data))

    result = runner.invoke(app, ["storage-consistency", GAME])
    assert result.exit_code != 0
    assert "Only in JSON" in result.output


def test_detects_mismatched_numbers(isolated):
    storage, db_path, inspection_dir = isolated
    storage.save_draws(GAME, [{"draw_id": 1, "draw_date": "2026-01-01", "numbers": [1, 2, 3, 4, 5, 6], "bonus": []}])

    out_dir = inspection_dir / GAME.replace("/", "_")
    path = out_dir / "2026.json"
    data = json.loads(path.read_text())
    data[0]["numbers"] = [10, 20, 30, 40, 50, 60]  # tamper with the JSON copy
    path.write_text(json.dumps(data))

    result = runner.invoke(app, ["storage-consistency", GAME])
    assert result.exit_code != 0
    assert "Numbers differ" in result.output
