"""Strategy Roster & Meta-Selection tests 🗳️

Covers engine/modules/strategy_roster.py (the policy from MDR-003) and the
`select-strategies` CLI command (MDR-004). See
docs/wayfinder/strategy-pruning-meta-selection-map.md for the design trail.
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.modules.pruning import PruningMetrics
import engine.modules.strategy_roster as roster_mod
from engine.modules.strategy_roster import compute_roster, load_roster, save_roster

runner = CliRunner()


class _FakeAdapter:
    """Only `.fetch()` is touched by compute_roster (for the history-length
    guard) once run_pruning_audit itself is monkeypatched away."""

    def __init__(self, n_draws: int = 200):
        self._n_draws = n_draws

    def fetch(self):
        return list(range(self._n_draws))


@pytest.fixture(autouse=True)
def _isolate_data_files(tmp_path, monkeypatch):
    """Every test here gets its own calibration cache / roster file — never
    touches the real data/ directory."""
    monkeypatch.setattr(roster_mod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(roster_mod, "ROSTER_PATH", tmp_path / "strategy_roster.json")
    monkeypatch.setattr(roster_mod, "CALIBRATION_CACHE_PATH", tmp_path / "calibration_cache.json")
    yield


def _write_calibration(tmp_path, lottery_id: str, lifts: dict) -> None:
    path = tmp_path / "calibration_cache.json"
    path.write_text(json.dumps({lottery_id: {"date": "2026-09-16", "strategies": lifts}}))


# ── calibration-sourced classification ───────────────────────────────────────

def test_calibrated_strategy_above_threshold_is_active(tmp_path):
    _write_calibration(tmp_path, "br/lotofacil", {"weighted": 1.2})
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["weighted"], min_lift=1.0)
    assert result.active_strategies == ["weighted"]
    assert result.entries[0].source == "calibration"
    assert result.exclusions == {}


def test_calibrated_strategy_below_threshold_is_excluded_with_reason(tmp_path):
    _write_calibration(tmp_path, "br/lotofacil", {"bayesian": 0.9})
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["bayesian"], min_lift=1.0)
    assert result.active_strategies == []
    assert "0.900" in result.exclusions["bayesian"]["reason"]
    assert result.exclusions["bayesian"]["metrics"]["lift"] == 0.9


# ── live pruning-audit fallback + 0-baseline -> 1.0-baseline normalization ──

def test_uncalibrated_strategy_falls_back_to_pruning_audit(monkeypatch):
    def fake_audit(adapter, names, window, threshold):
        # 0-baseline: 0.10 == "10% better than random" == 1.10 on the
        # 1.0-baseline scale compute_roster normalizes onto.
        return [PruningMetrics(strategy_name=n, lift_over_random=0.10, avg_rank=1.0, best_hit=3)
                for n in names]

    monkeypatch.setattr("engine.modules.pruning.run_pruning_audit", fake_audit)
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["monte_carlo"], min_lift=1.0, window=20)
    assert result.entries[0].source == "pruning"
    assert result.entries[0].lift == pytest.approx(1.10)
    assert result.active_strategies == ["monte_carlo"]


def test_insufficient_history_vs_audit_failure_are_distinguished(monkeypatch):
    # Audit returns nothing for either strategy (as if both failed to run).
    monkeypatch.setattr("engine.modules.pruning.run_pruning_audit", lambda *a, **k: [])

    short_result = compute_roster(_FakeAdapter(n_draws=5), "br/lotofacil", ["monte_carlo"], window=20)
    long_result = compute_roster(_FakeAdapter(n_draws=500), "br/lotofacil", ["weighted"], window=20)

    assert "insufficient history" in short_result.exclusions["monte_carlo"]["reason"]
    assert "insufficient history" not in long_result.exclusions["weighted"]["reason"]
    assert "missing optional dependency" in long_result.exclusions["weighted"]["reason"]


# ── load-failure guard ────────────────────────────────────────────────────────

def test_unknown_strategy_name_is_excluded_as_failed_to_load():
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["not_a_real_strategy_xyz"], min_lift=1.0)
    assert result.active_strategies == []
    assert "failed to load" in result.exclusions["not_a_real_strategy_xyz"]["reason"]


# ── pin / exclude overrides ───────────────────────────────────────────────────

def test_pin_forces_active_even_below_threshold(tmp_path):
    _write_calibration(tmp_path, "br/lotofacil", {"bayesian": 0.5})
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["bayesian"], min_lift=1.0, pin=["bayesian"])
    assert result.active_strategies == ["bayesian"]


def test_exclude_wins_over_pin_on_conflict(tmp_path):
    _write_calibration(tmp_path, "br/lotofacil", {"weighted": 1.5})
    result = compute_roster(
        _FakeAdapter(), "br/lotofacil", ["weighted"], min_lift=1.0,
        pin=["weighted"], exclude=["weighted"],
    )
    assert result.active_strategies == []
    assert result.exclusions["weighted"]["reason"] == "excluded by user (--exclude)"


def test_pin_outside_candidate_pool_is_still_recorded():
    result = compute_roster(_FakeAdapter(), "br/lotofacil", [], min_lift=1.0, pin=["weighted"])
    assert result.active_strategies == ["weighted"]


# ── save_roster / load_roster round-trip ─────────────────────────────────────

def test_save_and_load_roster_round_trip(tmp_path):
    _write_calibration(tmp_path, "br/lotofacil", {"weighted": 1.3, "bayesian": 0.8})
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["weighted", "bayesian"], min_lift=1.0)
    save_roster(result)

    assert roster_mod.ROSTER_PATH.exists()
    loaded = load_roster("br/lotofacil")
    assert loaded["active_strategies"] == ["weighted"]
    assert "bayesian" in loaded["exclusions"]
    assert loaded["policy_id"] == "calibration-lift-threshold-v1"
    assert load_roster("br/mega-sena") is None  # never written


def test_save_roster_preserves_existing_regime_overrides(tmp_path):
    roster_mod.ROSTER_PATH.write_text(json.dumps({
        "br/lotofacil": {
            "game_id": "br/lotofacil", "updated_at": "x", "policy_id": "old",
            "active_strategies": [], "exclusions": {},
            "regime_overrides": {"STABLE": ["weighted"]},
        }
    }))
    _write_calibration(tmp_path, "br/lotofacil", {"weighted": 1.3})
    result = compute_roster(_FakeAdapter(), "br/lotofacil", ["weighted"], min_lift=1.0)
    save_roster(result)
    loaded = load_roster("br/lotofacil")
    assert loaded["regime_overrides"] == {"STABLE": ["weighted"]}


# ── CLI smoke test ─────────────────────────────────────────────────────────────

def test_select_strategies_registered_and_dry_run_completes():
    result = runner.invoke(app, ["select-strategies", "br/lotofacil", "--strategies", "fast", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Strategy Roster" in result.output
    assert "not saved" in result.output
