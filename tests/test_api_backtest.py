"""
API Backtest Endpoint Tests 🔬
==============================
POST /games/{name}/backtest used to always return a canned
{"message": "Backtest completed"} regardless of what was computed —
the real per-draw and per-strategy results were only ever printed to
stdout by the CLI function it called. These tests lock in that the
endpoint now returns the actual structured result.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from engine.api.main import app

client = TestClient(app)
GAME = "br/lotofacil"


def test_backtest_returns_structured_result():
    response = client.post(f"/games/{GAME}/backtest", json={"strategy": "weighted", "prev": "1", "count": 1})
    assert response.status_code == 200

    data = response.json()
    assert data["lottery"] == GAME
    assert len(data["draws"]) == 1

    draw = data["draws"][0]
    assert "winning_numbers" in draw
    assert "weighted" in draw["strategies"]
    assert "avg_rank" in draw["strategies"]["weighted"]

    assert "weighted" in data["summary"]
    assert "avg_rank" in data["summary"]["weighted"]


def test_backtest_multiple_strategies_all_present():
    response = client.post(f"/games/{GAME}/backtest", json={"strategy": "markov,weighted", "prev": "1"})
    assert response.status_code == 200

    data = response.json()
    assert set(data["summary"].keys()) == {"markov", "weighted"}


def test_backtest_unknown_strategy_returns_400():
    response = client.post(f"/games/{GAME}/backtest", json={"strategy": "not-a-real-strategy", "prev": "1"})
    assert response.status_code == 400


def test_backtest_no_matching_draws_returns_404():
    response = client.post(f"/games/{GAME}/backtest", json={"strategy": "weighted", "draw_ids": "999999"})
    assert response.status_code == 404
