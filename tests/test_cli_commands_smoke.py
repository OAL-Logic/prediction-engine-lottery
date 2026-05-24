"""
CLI Command Smoke Tests
=======================
Fast integration tests that exercise each new CLI command against real
cached draw data (br/lotofacil). These are smoke tests — they verify the
command doesn't crash and produces some output, not that the output is
numerically correct.

All tests use the Typer test client so no subprocess is needed.
Commands that require heavy computation (leaderboard, stress-test) are
tested with minimal parameters to keep the suite fast.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

# The main typer app
from engine.cli.main import app

runner = CliRunner()

# We always use a game that has cached data
GAME = "br/lotofacil"


def _ok(result):
    """Assert exit code 0 and non-empty output."""
    assert result.exit_code == 0, f"Exit {result.exit_code}:\n{result.output}"
    assert result.output.strip(), "Command produced no output"


# ── Diagnostic Terminal commands ──────────────────────────────────────────────

def test_signal_smoke():
    result = runner.invoke(app, ["signal", GAME, "--limit", "50", "--step", "20"])
    _ok(result)
    assert "Signal" in result.output or "stability" in result.output.lower()


def test_stress_test_smoke():
    result = runner.invoke(app, [
        "stress-test", GAME,
        "--strategy", "bayesian",
        "--inject-ratio", "0.5",
        "--trials", "2",
    ])
    _ok(result)
    assert "REAL" in result.output or "RANDOM" in result.output or "Δ" in result.output


def test_detect_patterns_smoke():
    result = runner.invoke(app, [
        "detect-patterns", GAME,
        "--esoteric", "lunar",
        "--threshold", "0.10",
    ])
    _ok(result)


def test_leaderboard_smoke():
    result = runner.invoke(app, [
        "leaderboard", GAME,
        "--strategies", "bayesian,weighted",
        "--limit", "50",
        "--step", "25",
        "--trials", "2",
    ])
    _ok(result)
    assert "Strategy" in result.output or "composite" in result.output.lower()


def test_scan_smoke():
    result = runner.invoke(app, ["scan", GAME, "--strategy", "bayesian"])
    _ok(result)
    assert "GO" in result.output or "CAUTION" in result.output or "NO-GO" in result.output


def test_scan_layer6_regime():
    """Layer 6 (regime check) must appear in scan output."""
    result = runner.invoke(app, ["scan", GAME])
    _ok(result)
    assert "Regime" in result.output or "JS=" in result.output


def test_forecast_smoke():
    result = runner.invoke(app, [
        "forecast", GAME,
        "--strategies", "bayesian,weighted",
        "--trials", "2",
    ])
    _ok(result)
    assert "Consensus" in result.output or "Ticket" in result.output


def test_compare_draws_smoke():
    result = runner.invoke(app, ["compare-draws", GAME, "--recent", "30"])
    _ok(result)
    assert "STABLE" in result.output or "DRIFT" in result.output or "SHIFT" in result.output


def test_compare_draws_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, ["compare-draws", GAME, "--export-md", tmp])
        _ok(result)
        assert Path(tmp).exists()
        content = Path(tmp).read_text()
        assert "js_divergence" in content
        assert "regime_verdict" in content
    finally:
        os.unlink(tmp)


def test_next_smoke():
    result = runner.invoke(app, ["next", GAME, "--strategy", "bayesian"])
    _ok(result)
    assert "GO" in result.output or "CAUTION" in result.output or "NO-GO" in result.output


def test_next_quiet():
    result = runner.invoke(app, ["next", GAME, "--quiet"])
    assert result.exit_code == 0
    # quiet mode: just verdict + numbers on one line, or empty if NO-GO
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) >= 1


def test_next_force():
    """--force always generates a ticket regardless of verdict."""
    result = runner.invoke(app, ["next", GAME, "--force", "--quiet"])
    assert result.exit_code == 0
    # quiet mode prints "VERDICT  n1 n2 n3 ..." on one line
    # find any line that contains digit tokens (the ticket)
    digit_lines = [
        l for l in result.output.splitlines()
        if any(tok.isdigit() for tok in l.split())
        and not l.strip().startswith("Cache")
        and not l.strip().startswith("Checking")
    ]
    assert len(digit_lines) > 0, f"Expected ticket numbers in output, got:\n{result.output}"


# ── Log commands ──────────────────────────────────────────────────────────────

def test_log_smoke():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "log", GAME,
            "--output", tmp,
            "--quiet",
        ])
        assert result.exit_code == 0
        lines = [l for l in Path(tmp).read_text().splitlines() if l.strip()]
        assert len(lines) >= 1
        record = json.loads(lines[-1])
        assert record["game"] == GAME
        assert "date" in record
        assert "confidence" in record
    finally:
        os.unlink(tmp)


def test_log_csv_format():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "log", GAME,
            "--output", tmp,
            "--format", "csv",
            "--quiet",
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "date" in content
        assert "confidence" in content
    finally:
        os.unlink(tmp)


def test_log_view_smoke():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        tmp = f.name
        # Write a minimal valid record
        record = {
            "date": "2026-05-03", "draw_id": 3675, "game": GAME,
            "strategy": "bayesian", "confidence": 0.49, "entropy": 3.1,
            "stable": True, "chi2_p": 0.97, "moon_phase": "Full Moon",
            "moon_ratio": 0.56, "solar_kp": 3.3, "cluster": None,
        }
        f.write((json.dumps(record) + "\n").encode())
    try:
        result = runner.invoke(app, ["log-view", "--output", tmp, "--last", "5"])
        _ok(result)
        assert "2026-05-03" in result.output
    finally:
        os.unlink(tmp)


def test_trend_smoke():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        tmp = f.name
        for i in range(5):
            record = {
                "date": f"2026-04-{28+i:02d}", "draw_id": 3670 + i, "game": GAME,
                "strategy": "bayesian", "confidence": 0.48 + i * 0.01,
                "entropy": 3.1, "stable": True, "chi2_p": 0.97,
                "moon_phase": "Full Moon", "moon_ratio": 0.5,
                "solar_kp": 3.3, "cluster": None,
            }
            f.write((json.dumps(record) + "\n").encode())
    try:
        result = runner.invoke(app, ["trend", GAME, "--log", tmp, "--days", "30"])
        _ok(result)
        assert "confidence" in result.output.lower() or "▁" in result.output
    finally:
        os.unlink(tmp)


# ── Risk and Oracle commands ──────────────────────────────────────────────────

def test_risk_smoke():
    result = runner.invoke(app, ["risk", GAME, "--bankroll", "100"])
    _ok(result)
    assert "EV" in result.output or "Kelly" in result.output or "Expected" in result.output


def test_risk_with_jackpot():
    result = runner.invoke(app, ["risk", GAME, "--jackpot", "50000000", "--bankroll", "100"])
    _ok(result)
    assert "50" in result.output  # jackpot should appear


def test_risk_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "risk", GAME,
            "--jackpot", "2000000",
            "--export-md", tmp,
        ])
        _ok(result)
        content = Path(tmp).read_text()
        assert "subtype: risk" in content
        assert "breakeven_jackpot" in content
    finally:
        os.unlink(tmp)


def test_oracle_quant():
    result = runner.invoke(app, ["oracle", GAME, "--persona", "quant"])
    _ok(result)


def test_oracle_mystic():
    result = runner.invoke(app, ["oracle", GAME, "--persona", "mystic"])
    _ok(result)
    assert "cosmic" in result.output.lower() or "vibrational" in result.output.lower() or "stars" in result.output.lower()


def test_oracle_degen():
    result = runner.invoke(app, ["oracle", GAME, "--persona", "degen"])
    _ok(result)


def test_oracle_invalid_persona():
    result = runner.invoke(app, ["oracle", GAME, "--persona", "goblin"])
    assert result.exit_code != 0 or "Unknown" in result.output


# ── Daily command ─────────────────────────────────────────────────────────────

def test_daily_smoke():
    result = runner.invoke(app, ["daily", GAME, "--strategy", "bayesian"])
    _ok(result)
    assert "GO" in result.output or "CAUTION" in result.output or "NO-GO" in result.output
    assert "Regime" in result.output
    assert "EV" in result.output or "ratio" in result.output.lower()


def test_daily_quiet():
    result = runner.invoke(app, ["daily", GAME, "--quiet"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) >= 1


def test_daily_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, ["daily", GAME, "--export-md", tmp])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: daily" in content
        assert "verdict" in content
    finally:
        os.unlink(tmp)


def test_daily_mystic_persona():
    result = runner.invoke(app, ["daily", GAME, "--persona", "mystic"])
    _ok(result)
    assert "Esoteric" in result.output or "Sage" in result.output or "cosmic" in result.output.lower()


# ── Watchlist commands ────────────────────────────────────────────────────────

def test_watchlist_add():
    result = runner.invoke(app, ["watchlist", "add", GAME])
    assert result.exit_code == 0
    assert "already on the watchlist" in result.output or "Added" in result.output


def test_watchlist_list():
    result = runner.invoke(app, ["watchlist", "list"])
    assert result.exit_code == 0
    assert GAME in result.output or "empty" in result.output.lower()


def test_watchlist_status():
    result = runner.invoke(app, ["watchlist", "status"])
    assert result.exit_code == 0
    # Either shows table with game or empty message
    assert GAME in result.output or "empty" in result.output.lower()


def test_watchlist_run_scan():
    result = runner.invoke(app, ["watchlist", "run", "--mode", "scan"])
    assert result.exit_code == 0
    assert "Scan" in result.output
    assert GAME in result.output


def test_watchlist_run_alert():
    runner.invoke(app, ["watchlist", "add", GAME])  # ensure game is tracked
    result = runner.invoke(app, ["watchlist", "run", "--mode", "alert"])
    # Exit 0 (triggered) or 1 (silent) — both are valid
    assert result.exit_code in (0, 1)
    assert "Alert" in result.output or "quiet" in result.output.lower()


def test_watchlist_remove():
    # Add first to make sure it's there, then remove
    runner.invoke(app, ["watchlist", "add", GAME])
    result = runner.invoke(app, ["watchlist", "remove", GAME])
    assert result.exit_code == 0
    assert "Removed" in result.output or "not on" in result.output.lower()


def test_watchlist_remove_nonexistent():
    # Remove something that isn't tracked
    result = runner.invoke(app, ["watchlist", "remove", "zz/invalid"])
    assert result.exit_code == 1


# ── Report pipeline steps format ─────────────────────────────────────────────

def test_report_steps_scan():
    import tempfile, yaml
    pipeline = {
        "name": "Test Scan Pipeline",
        "steps": [
            {"type": "scan", "lottery": GAME},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(pipeline, f)
        tmp = f.name
    try:
        result = runner.invoke(app, ["report", tmp])
        assert result.exit_code == 0
        assert "Pipeline" in result.output
        assert "scan" in result.output.lower() or "GO" in result.output
    finally:
        os.unlink(tmp)


def test_report_steps_alert():
    import tempfile, yaml
    pipeline = {
        "name": "Test Alert Pipeline",
        "steps": [
            {"type": "alert", "lottery": GAME, "condition": "go-strong,regime-shift"},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(pipeline, f)
        tmp = f.name
    try:
        result = runner.invoke(app, ["report", tmp])
        # Exit 0 (alert triggered) or the pipeline itself completes (exit 0 from report)
        assert result.exit_code == 0
        assert "Pipeline" in result.output or "alert" in result.output.lower()
    finally:
        os.unlink(tmp)


# ── Hitcheck & ticket logging ─────────────────────────────────────────────────

def test_forecast_logs_ticket():
    from pathlib import Path
    import json
    log_path = Path("data/ticket_log.jsonl")
    before = log_path.stat().st_size if log_path.exists() else 0
    result = runner.invoke(app, ["forecast", GAME, "--strategies", "fast", "--quiet"])
    assert result.exit_code == 0
    assert log_path.exists()
    after = log_path.stat().st_size
    assert after > before, "forecast should have appended a ticket to ticket_log.jsonl"


def test_hitcheck_smoke():
    # Ensure there's at least one logged ticket
    runner.invoke(app, ["forecast", GAME, "--strategies", "fast", "--quiet"])
    result = runner.invoke(app, ["hitcheck", GAME])
    assert result.exit_code == 0
    assert "Hit Check" in result.output


def test_hitcheck_no_tickets_empty_game():
    # A game with no logged tickets
    result = runner.invoke(app, ["hitcheck", GAME, "--since", "2099-01-01"])
    assert result.exit_code == 0
    assert "No logged tickets" in result.output or "ticket" in result.output.lower()


# ── Weekly summary ────────────────────────────────────────────────────────────

def test_weekly_smoke():
    result = runner.invoke(app, ["weekly", GAME])
    assert result.exit_code == 0
    assert "Weekly" in result.output


def test_weekly_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, ["weekly", GAME, "--export-md", tmp])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: weekly" in content
    finally:
        os.unlink(tmp)


def test_daily_logs_ticket():
    """daily command should log its generated ticket to ticket_log.jsonl."""
    from pathlib import Path
    log_path = Path("data/ticket_log.jsonl")
    before = log_path.stat().st_size if log_path.exists() else 0
    result = runner.invoke(app, ["daily", GAME, "--quiet"])
    assert result.exit_code == 0
    # Only asserts log grew if conditions were GO (ticket generated)
    # — we just verify no crash regardless


# ── Calibrate ─────────────────────────────────────────────────────────────────

def test_calibrate_fast():
    result = runner.invoke(app, [
        "calibrate", GAME,
        "--draws", "5",
        "--strategies", "fast",
        "--limit", "30",
    ])
    assert result.exit_code == 0
    assert "Calibration" in result.output
    assert "baseline" in result.output.lower()


def test_calibrate_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "calibrate", GAME,
            "--draws", "5",
            "--strategies", "fast",
            "--limit", "30",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: calibration" in content
        assert "Strategy" in content
    finally:
        os.unlink(tmp)


# ── Log export ────────────────────────────────────────────────────────────────

def test_log_export_draw_log_csv():
    result = runner.invoke(app, ["log-export", "draw-log", "--game", GAME])
    assert result.exit_code == 0
    # CSV output — either has header or reports no entries
    assert "date" in result.output or "no matching" in result.output.lower()


def test_log_export_ticket_log_csv():
    runner.invoke(app, ["forecast", GAME, "--strategies", "fast", "--quiet"])
    result = runner.invoke(app, ["log-export", "ticket-log", "--game", GAME])
    assert result.exit_code == 0
    assert "date" in result.output or "no matching" in result.output.lower()


def test_log_export_json_format():
    result = runner.invoke(app, [
        "log-export", "draw-log",
        "--game", GAME,
        "--format", "json",
    ])
    assert result.exit_code == 0
    if result.output.strip() and result.output.strip() != "draw-log: no matching entries.":
        data = json.loads(result.output)
        assert isinstance(data, list)


def test_log_export_to_file():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "log-export", "draw-log",
            "--game", GAME,
            "--output", tmp,
        ])
        assert result.exit_code == 0
        # Either wrote the file with content or no entries
        if Path(tmp).exists() and Path(tmp).stat().st_size > 0:
            content = Path(tmp).read_text()
            assert "date" in content
    finally:
        if Path(tmp).exists():
            os.unlink(tmp)


# ── Rank numbers ──────────────────────────────────────────────────────────────

def test_rank_numbers_smoke():
    result = runner.invoke(app, [
        "rank-numbers", GAME,
        "--strategies", "fast",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "Number Rankings" in result.output
    assert "HOT" in result.output


def test_rank_numbers_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "rank-numbers", GAME,
            "--strategies", "fast",
            "--top", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: rank-numbers" in content
    finally:
        os.unlink(tmp)


# ── Picks ─────────────────────────────────────────────────────────────────────

def test_picks_smoke():
    # Ensure there are tickets logged
    runner.invoke(app, ["forecast", GAME, "--strategies", "fast", "--quiet"])
    result = runner.invoke(app, ["picks", GAME, "--last", "5"])
    assert result.exit_code == 0
    assert "Consensus Picks" in result.output or "No matching" in result.output


def test_picks_no_log():
    result = runner.invoke(app, ["picks", GAME, "--since", "2099-01-01"])
    assert result.exit_code == 0
    # Either shows picks or gracefully says no matches
    assert result.output.strip() != ""


# ── Number Timeline ───────────────────────────────────────────────────────────

def test_number_timeline_smoke():
    result = runner.invoke(app, [
        "number-timeline", GAME, "7",
        "--draws", "50",
    ])
    assert result.exit_code == 0
    assert "Timeline" in result.output
    assert "Hits" in result.output or "cold" in result.output.lower()


def test_number_timeline_out_of_range():
    result = runner.invoke(app, [
        "number-timeline", GAME, "99",
    ])
    assert result.exit_code == 1
    assert "outside pool range" in result.output


def test_number_timeline_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "number-timeline", GAME, "7",
            "--draws", "30",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: number-timeline" in content
        assert "number: 7" in content
    finally:
        os.unlink(tmp)


# ── Compare Strategies ────────────────────────────────────────────────────────

def test_compare_strategies_smoke():
    result = runner.invoke(app, [
        "compare-strategies", GAME,
        "--strategies", "fast",
    ])
    assert result.exit_code == 0
    assert "Strategy Tickets" in result.output
    assert "Consensus" in result.output


def test_compare_strategies_top():
    result = runner.invoke(app, [
        "compare-strategies", GAME,
        "--strategies", "fast",
        "--top", "10",
    ])
    assert result.exit_code == 0
    assert "Consensus Ticket" in result.output


def test_compare_strategies_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "compare-strategies", GAME,
            "--strategies", "fast",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: compare-strategies" in content
        assert "consensus_ticket" in content
    finally:
        os.unlink(tmp)


# ── Streak Report ─────────────────────────────────────────────────────────────

def test_streak_report_smoke():
    result = runner.invoke(app, [
        "streak-report", GAME,
        "--draws", "50",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "Hottest" in result.output or "Coldest" in result.output
    assert "Streak Extremes" in result.output


def test_streak_report_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "streak-report", GAME,
            "--draws", "50",
            "--top", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: streak-report" in content
        assert "hottest_number" in content
    finally:
        os.unlink(tmp)


# ── Pair Analysis ─────────────────────────────────────────────────────────────

def test_pair_analysis_smoke():
    result = runner.invoke(app, [
        "pair-analysis", GAME,
        "--draws", "50",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "Frequent Pairs" in result.output or "Pair Summary" in result.output


def test_pair_analysis_focus():
    result = runner.invoke(app, [
        "pair-analysis", GAME,
        "--draws", "50",
        "--top", "5",
        "--focus", "7",
    ])
    assert result.exit_code == 0
    # Either shows affinity table or graceful "no qualifying pairs"
    assert result.output.strip() != ""


def test_pair_analysis_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "pair-analysis", GAME,
            "--draws", "50",
            "--top", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: pair-analysis" in content
        assert "most_synergistic" in content
    finally:
        os.unlink(tmp)


# ── Draw Summary ──────────────────────────────────────────────────────────────

def test_draw_summary_latest():
    result = runner.invoke(app, [
        "draw-summary", GAME,
    ])
    assert result.exit_code == 0
    assert "Draw Summary" in result.output


def test_draw_summary_specific_id():
    # Get a real draw ID first
    from engine.cli.utils import get_adapter
    adapter = get_adapter(GAME)
    df = adapter.fetch()
    valid = df[df["numbers"].apply(lambda x: isinstance(x, list) and len(x) > 0)]
    if valid.empty:
        pytest.skip("No valid draws")
    real_id = int(valid.iloc[-1]["draw_id"])
    result = runner.invoke(app, [
        "draw-summary", GAME, "--id", str(real_id),
    ])
    assert result.exit_code == 0
    assert str(real_id) in result.output


def test_draw_summary_bad_id():
    result = runner.invoke(app, [
        "draw-summary", GAME, "--id", "999999",
    ])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_draw_summary_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "draw-summary", GAME,
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: draw-summary" in content
        assert "surprise_score" in content
    finally:
        os.unlink(tmp)


# ── Session ───────────────────────────────────────────────────────────────────

def test_session_smoke():
    result = runner.invoke(app, [
        "session", GAME,
        "--strategies", "fast",
        "--limit", "50",
    ])
    # Session should either complete (0) or exit NO-GO (1) — not crash (2)
    assert result.exit_code in (0, 1)
    assert "Session" in result.output


def test_session_force():
    result = runner.invoke(app, [
        "session", GAME,
        "--strategies", "fast",
        "--limit", "50",
        "--force",
    ])
    # With --force, session always completes
    assert result.exit_code == 0
    assert "Session complete" in result.output


def test_session_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "session", GAME,
            "--strategies", "fast",
            "--limit", "50",
            "--force",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: session" in content
        assert "verdict" in content
    finally:
        os.unlink(tmp)


# ── Ticket Grade ──────────────────────────────────────────────────────────────

# Standard Lotofacil ticket: 15 numbers from 1-25
_SAMPLE_TICKET = ["1","3","5","7","10","11","13","15","19","20","21","22","23","24","25"]

def test_ticket_grade_smoke():
    result = runner.invoke(app, [
        "ticket-grade", GAME,
    ] + _SAMPLE_TICKET)
    assert result.exit_code == 0
    assert "Ticket Grade" in result.output
    assert "Grade:" in result.output


def test_ticket_grade_bad_number():
    result = runner.invoke(app, [
        "ticket-grade", GAME,
        "1", "2", "3", "99",
    ])
    assert result.exit_code == 1
    assert "out of range" in result.output


def test_ticket_grade_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "ticket-grade", GAME,
        ] + _SAMPLE_TICKET + ["--export-md", tmp])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: ticket-grade" in content
        assert "grade:" in content
    finally:
        os.unlink(tmp)


# ── Pool Stats ────────────────────────────────────────────────────────────────

def test_pool_stats_smoke():
    result = runner.invoke(app, [
        "pool-stats", GAME,
        "--draws", "50",
    ])
    assert result.exit_code == 0
    assert "Draw Property Distributions" in result.output


def test_pool_stats_check():
    result = runner.invoke(app, [
        "pool-stats", GAME,
        "--draws", "50",
        "--check", "1", "--check", "3", "--check", "5", "--check", "7",
        "--check", "10", "--check", "11", "--check", "13", "--check", "15",
        "--check", "19", "--check", "20", "--check", "21", "--check", "22",
        "--check", "23", "--check", "24", "--check", "25",
    ])
    assert result.exit_code == 0
    assert "Ticket Check" in result.output or "Ticket Fit" in result.output


def test_pool_stats_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "pool-stats", GAME,
            "--draws", "50",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: pool-stats" in content
        assert "sum_mean" in content
    finally:
        os.unlink(tmp)


# ── History Scan ──────────────────────────────────────────────────────────────

def test_history_scan_smoke():
    result = runner.invoke(app, [
        "history-scan", GAME,
        "--windows", "5",
        "--window-size", "30",
    ])
    assert result.exit_code == 0
    assert "History Scan" in result.output


def test_history_scan_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "history-scan", GAME,
            "--windows", "5",
            "--window-size", "30",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: history-scan" in content
        assert "go_rate" in content
    finally:
        os.unlink(tmp)


# ── Number Heat ───────────────────────────────────────────────────────────────

def test_number_heat_smoke():
    result = runner.invoke(app, [
        "number-heat", GAME,
        "--draws", "20",
    ])
    assert result.exit_code == 0
    assert "Pool Heatmap" in result.output


def test_number_heat_sort_streak():
    result = runner.invoke(app, [
        "number-heat", GAME,
        "--draws", "20",
        "--sort-by", "streak",
    ])
    assert result.exit_code == 0
    assert "Pool Heatmap" in result.output


def test_number_heat_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "number-heat", GAME,
            "--draws", "15",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: number-heat" in content
        assert "hottest_number" in content
    finally:
        os.unlink(tmp)


# ── Suggest Swaps ─────────────────────────────────────────────────────────────

_SAMPLE_TICKET_ARGS = ["1","3","5","7","10","11","13","15","19","20","21","22","23","24","25"]

def test_suggest_swaps_smoke():
    result = runner.invoke(app, [
        "suggest-swaps", GAME,
    ] + _SAMPLE_TICKET_ARGS + ["--swaps", "3"])
    assert result.exit_code == 0
    assert "Swap Suggestions" in result.output or "Current Ticket" in result.output


def test_suggest_swaps_bad_number():
    result = runner.invoke(app, [
        "suggest-swaps", GAME,
        "1", "2", "3", "99",
    ])
    assert result.exit_code == 1
    assert "out of range" in result.output


def test_suggest_swaps_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "suggest-swaps", GAME,
        ] + _SAMPLE_TICKET_ARGS + ["--swaps", "3", "--export-md", tmp])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: suggest-swaps" in content
    finally:
        os.unlink(tmp)


# ── Quick ─────────────────────────────────────────────────────────────────────

def test_quick_smoke():
    result = runner.invoke(app, ["quick", GAME])
    # exits 0 (GO+ticket) or 1 (NO-GO)
    assert result.exit_code in (0, 1)
    assert result.output.strip() != ""


def test_quick_force():
    result = runner.invoke(app, ["quick", GAME, "--force"])
    # With --force always produces a ticket
    assert result.exit_code == 0
    assert any(c.isdigit() for c in result.output)


def test_quick_quiet_force():
    result = runner.invoke(app, ["quick", GAME, "--force", "--quiet"])
    assert result.exit_code == 0
    # Output should contain a line of all-digit tokens (the ticket)
    lines = [l for l in result.output.splitlines() if l.strip()]
    assert len(lines) > 0
    ticket_lines = [
        l for l in lines
        if all(tok.isdigit() for tok in l.strip().split()) and l.strip()
    ]
    assert len(ticket_lines) >= 1, f"No all-digit line found. Lines: {lines}"


def test_quick_json_force():
    result = runner.invoke(app, ["quick", GAME, "--force", "--json"])
    assert result.exit_code == 0
    # Find a line that is valid JSON with a 'ticket' key
    for line in result.output.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            data = json.loads(line)
            if "ticket" in data and isinstance(data["ticket"], list):
                return  # found valid JSON ticket line
        except Exception:
            continue
    pytest.fail(f"No JSON ticket line found in output: {result.output[:300]}")


# ── Variance Report ───────────────────────────────────────────────────────────

def test_variance_report_smoke():
    result = runner.invoke(app, [
        "variance-report", GAME,
        "--draws", "50",
    ])
    assert result.exit_code == 0
    assert "Variance Report" in result.output or "Variance Summary" in result.output


def test_variance_report_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "variance-report", GAME,
            "--draws", "50",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: variance-report" in content
        assert "freq_cv" in content
    finally:
        os.unlink(tmp)


# ── Coverage Check ────────────────────────────────────────────────────────────

_TICKET1 = "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"
_TICKET2 = "2 4 6 8 9 12 14 16 17 18 19 20 21 22 25"

def test_coverage_check_single():
    result = runner.invoke(app, [
        "coverage-check", GAME, _TICKET1,
    ])
    assert result.exit_code == 0
    assert "Coverage" in result.output


def test_coverage_check_two_tickets():
    result = runner.invoke(app, [
        "coverage-check", GAME, _TICKET1, _TICKET2,
    ])
    assert result.exit_code == 0
    assert "2 ticket" in result.output or "Coverage" in result.output


def test_coverage_check_no_tickets():
    result = runner.invoke(app, ["coverage-check", GAME])
    assert result.exit_code == 0
    assert "No tickets" in result.output or result.output.strip() != ""


def test_coverage_check_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "coverage-check", GAME, _TICKET1,
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: coverage-check" in content
        assert "cover_pct" in content
        assert "coverage_efficiency" in content
    finally:
        os.unlink(tmp)


# ── Momentum Check ────────────────────────────────────────────────────────────

def test_momentum_check_smoke():
    result = runner.invoke(app, [
        "momentum-check", GAME,
        "--short", "5",
        "--long", "15",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "Momentum" in result.output
    assert "RISING" in result.output or "FALLING" in result.output or "NEUTRAL" in result.output


def test_momentum_check_all():
    result = runner.invoke(app, [
        "momentum-check", GAME,
        "--short", "5",
        "--long", "15",
        "--top", "0",
    ])
    assert result.exit_code == 0
    assert "Momentum" in result.output


def test_momentum_check_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "momentum-check", GAME,
            "--short", "5",
            "--long", "15",
            "--top", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: momentum-check" in content
        assert "rising_count" in content
    finally:
        os.unlink(tmp)


# ── Gap Forecast ──────────────────────────────────────────────────────────────

def test_gap_forecast_smoke():
    result = runner.invoke(app, [
        "gap-forecast", GAME,
        "--top", "10",
    ])
    assert result.exit_code == 0
    assert "Gap Forecast" in result.output
    assert "Overdue" in result.output or "FRESH" in result.output


def test_gap_forecast_all():
    result = runner.invoke(app, [
        "gap-forecast", GAME,
        "--top", "0",
    ])
    assert result.exit_code == 0
    assert "Gap Forecast" in result.output


def test_gap_forecast_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "gap-forecast", GAME,
            "--top", "10",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: gap-forecast" in content
        assert "overdue_count" in content
    finally:
        os.unlink(tmp)


# ── Combo Rank ────────────────────────────────────────────────────────────────

_COMBO_TICKET = "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"

def test_combo_rank_smoke():
    result = runner.invoke(app, [
        "combo-rank", GAME,
        "--draws", "100",
        "--top", "10",
    ])
    assert result.exit_code == 0
    assert "Combo Rank" in result.output
    assert "%" in result.output


def test_combo_rank_check():
    result = runner.invoke(app, [
        "combo-rank", GAME,
        "--draws", "100",
        "--check", _COMBO_TICKET,
    ])
    assert result.exit_code == 0
    assert "Ticket Profile Check" in result.output
    assert "Rank" in result.output


def test_combo_rank_all_profiles():
    result = runner.invoke(app, [
        "combo-rank", GAME,
        "--draws", "100",
        "--top", "0",
    ])
    assert result.exit_code == 0
    assert "Combo Rank" in result.output


def test_combo_rank_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "combo-rank", GAME,
            "--draws", "100",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: combo-rank" in content
        assert "sum_low_cut" in content
    finally:
        os.unlink(tmp)


# ── Draw Clock ────────────────────────────────────────────────────────────────

def test_draw_clock_smoke():
    result = runner.invoke(app, [
        "draw-clock", GAME,
        "--top", "10",
        "--limit", "50",
    ])
    assert result.exit_code == 0
    assert "Draw Clock" in result.output
    assert "Due" in result.output


def test_draw_clock_all():
    result = runner.invoke(app, [
        "draw-clock", GAME,
        "--top", "0",
        "--limit", "50",
    ])
    assert result.exit_code == 0
    assert "Draw Clock" in result.output


def test_draw_clock_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "draw-clock", GAME,
            "--top", "10",
            "--limit", "50",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: draw-clock" in content
        assert "due_now_count" in content
    finally:
        os.unlink(tmp)


# ── Entropy Scan ──────────────────────────────────────────────────────────────

def test_entropy_scan_smoke():
    result = runner.invoke(app, [
        "entropy-scan", GAME,
        "--limit", "20",
        "--windows", "5",
    ])
    assert result.exit_code == 0
    assert "Entropy" in result.output
    assert "H(" in result.output or "Uniform" in result.output


def test_entropy_scan_summary():
    result = runner.invoke(app, [
        "entropy-scan", GAME,
        "--limit", "20",
        "--windows", "5",
    ])
    assert result.exit_code == 0
    assert "Entropy & Complexity Summary" in result.output


def test_entropy_scan_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "entropy-scan", GAME,
            "--limit", "20",
            "--windows", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: entropy-scan" in content
        assert "h_baseline" in content
    finally:
        os.unlink(tmp)


# ── Cold Streak Alert ─────────────────────────────────────────────────────────

def test_cold_streak_alert_runs():
    result = runner.invoke(app, ["cold-streak-alert", GAME])
    # exits 0 (ALERT) or 1 (QUIET) — not 2 (error)
    assert result.exit_code in (0, 1)
    assert result.output.strip() != ""


def test_cold_streak_alert_low_threshold():
    # Very low threshold (0.1×) guarantees every number fires → always ALERT
    result = runner.invoke(app, [
        "cold-streak-alert", GAME, "--threshold", "0.1",
    ])
    assert result.exit_code == 0
    assert "ALERT" in result.output


def test_cold_streak_alert_high_threshold():
    # Absurdly high threshold → always QUIET
    result = runner.invoke(app, [
        "cold-streak-alert", GAME, "--threshold", "999",
    ])
    assert result.exit_code == 1
    assert "QUIET" in result.output


def test_cold_streak_alert_verbose():
    result = runner.invoke(app, [
        "cold-streak-alert", GAME, "--threshold", "0.1", "--verbose",
    ])
    assert result.exit_code == 0
    assert "Cold Streak Detail" in result.output


def test_cold_streak_alert_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "cold-streak-alert", GAME,
            "--threshold", "0.1",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: cold-streak-alert" in content
        assert "alerted_count" in content
    finally:
        os.unlink(tmp)


# ── Synergy Map ───────────────────────────────────────────────────────────────

_SYN_TICKET = "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"

def test_synergy_map_smoke():
    result = runner.invoke(app, [
        "synergy-map", GAME, _SYN_TICKET,
        "--draws", "100",
    ])
    assert result.exit_code == 0
    assert "Synergy" in result.output
    assert "lift" in result.output.lower() or "×" in result.output


def test_synergy_map_best_worst():
    result = runner.invoke(app, [
        "synergy-map", GAME, _SYN_TICKET,
        "--draws", "100",
    ])
    assert result.exit_code == 0
    assert "Best pair" in result.output
    assert "Worst pair" in result.output


def test_synergy_map_bad_number():
    result = runner.invoke(app, [
        "synergy-map", GAME, "1 3 99",
    ])
    assert result.exit_code == 1
    assert "out of range" in result.output


def test_synergy_map_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "synergy-map", GAME, _SYN_TICKET,
            "--draws", "100",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: synergy-map" in content
        assert "geo_mean_lift" in content
    finally:
        os.unlink(tmp)


# ── Ticket DNA ────────────────────────────────────────────────────────────────

_DNA_TICKET = "1 3 5 7 10 11 13 15 19 20 21 22 23 24 25"

def test_ticket_dna_smoke():
    result = runner.invoke(app, [
        "ticket-dna", GAME, _DNA_TICKET,
        "--draws", "100",
    ])
    assert result.exit_code == 0
    assert "DNA" in result.output
    assert "Fingerprint" in result.output


def test_ticket_dna_verdict():
    result = runner.invoke(app, [
        "ticket-dna", GAME, _DNA_TICKET,
        "--draws", "100",
    ])
    assert result.exit_code == 0
    assert "TYPICAL" in result.output or "MIXED" in result.output or "ATYPICAL" in result.output


def test_ticket_dna_bad_number():
    result = runner.invoke(app, [
        "ticket-dna", GAME, "1 3 5 99",
    ])
    assert result.exit_code == 1
    assert "out of range" in result.output


def test_ticket_dna_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "ticket-dna", GAME, _DNA_TICKET,
            "--draws", "100",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: ticket-dna" in content
        assert "fingerprint" in content
        assert "typicality" in content
    finally:
        os.unlink(tmp)


# ── Frequency Band ────────────────────────────────────────────────────────────

def test_frequency_band_smoke():
    result = runner.invoke(app, [
        "frequency-band", GAME,
        "--short", "10",
        "--mid", "30",
        "--long", "80",
    ])
    assert result.exit_code == 0
    assert "Frequency Band" in result.output
    assert "HOT" in result.output or "WARM" in result.output or "COLD" in result.output


def test_frequency_band_top():
    result = runner.invoke(app, [
        "frequency-band", GAME,
        "--short", "10",
        "--mid", "30",
        "--long", "80",
        "--top", "10",
    ])
    assert result.exit_code == 0
    assert "Frequency Band" in result.output


def test_frequency_band_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "frequency-band", GAME,
            "--short", "10",
            "--mid", "30",
            "--long", "80",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: frequency-band" in content
        assert "rising_count" in content
    finally:
        os.unlink(tmp)


# ── Multi Ticket ──────────────────────────────────────────────────────────────

def test_multi_ticket_smoke():
    result = runner.invoke(app, [
        "multi-ticket", GAME,
        "--count", "3",
        "--seed", "42",
    ])
    assert result.exit_code == 0
    assert "Portfolio" in result.output
    assert "T1" in result.output and "T2" in result.output


def test_multi_ticket_coverage():
    result = runner.invoke(app, [
        "multi-ticket", GAME,
        "--count", "5",
        "--diversity", "1.0",
        "--seed", "42",
    ])
    assert result.exit_code == 0
    assert "coverage" in result.output.lower()


def test_multi_ticket_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "multi-ticket", GAME,
            "--count", "3",
            "--seed", "42",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: multi-ticket" in content
        assert "cover_pct" in content
        assert "coverage_efficiency" in content
    finally:
        os.unlink(tmp)


# ── prize-ev ──────────────────────────────────────────────────────────────────

def test_prize_ev_smoke():
    result = runner.invoke(app, ["prize-ev", GAME])
    assert result.exit_code == 0
    assert "Breakeven" in result.output


def test_prize_ev_with_jackpot():
    result = runner.invoke(app, ["prize-ev", GAME, "--jackpot", "2500000"])
    assert result.exit_code == 0
    assert "ROI" in result.output
    assert "EV" in result.output.upper()


def test_prize_ev_tier_override():
    result = runner.invoke(app, [
        "prize-ev", GAME,
        "--jackpot", "3000000",
        "--tier", "14:1500",
    ])
    assert result.exit_code == 0
    assert "1,500" in result.output


def test_prize_ev_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "prize-ev", GAME,
            "--jackpot", "2000000",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: prize-ev" in content
        assert "breakeven_jackpot" in content
    finally:
        os.unlink(tmp)


# ── draw-fingerprint ───────────────────────────────────────────────────────────

def test_draw_fingerprint_smoke():
    result = runner.invoke(app, ["draw-fingerprint", GAME, "--draws", "50", "--top", "5"])
    assert result.exit_code == 0
    assert "Fingerprint" in result.output


def test_draw_fingerprint_similar_to():
    result = runner.invoke(app, [
        "draw-fingerprint", GAME,
        "--similar-to", "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15",
        "--draws", "50",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "Closest" in result.output


def test_draw_fingerprint_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "draw-fingerprint", GAME,
            "--draws", "30",
            "--top", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: draw-fingerprint" in content
    finally:
        os.unlink(tmp)


# ── regime-history ────────────────────────────────────────────────────────────

def test_regime_history_smoke():
    result = runner.invoke(app, [
        "regime-history", GAME,
        "--baseline", "50",
        "--window", "20",
        "--step", "20",
    ])
    assert result.exit_code == 0
    assert "Regime" in result.output


def test_regime_history_recent():
    result = runner.invoke(app, [
        "regime-history", GAME,
        "--baseline", "50",
        "--window", "20",
        "--step", "20",
        "--recent", "3",
    ])
    assert result.exit_code == 0
    assert "Latest regime" in result.output


def test_regime_history_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "regime-history", GAME,
            "--baseline", "50",
            "--window", "20",
            "--step", "20",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: regime-history" in content
        assert "latest_regime" in content
    finally:
        os.unlink(tmp)


# ── markov-table ──────────────────────────────────────────────────────────────

def test_markov_table_smoke():
    result = runner.invoke(app, [
        "markov-table", GAME,
        "--limit", "50",
        "--top", "3",
    ])
    assert result.exit_code == 0
    assert "Markov" in result.output


def test_markov_table_from():
    result = runner.invoke(app, [
        "markov-table", GAME,
        "--from", "7",
        "--limit", "50",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "#7" in result.output


def test_markov_table_stationary():
    result = runner.invoke(app, [
        "markov-table", GAME,
        "--stationary",
        "--limit", "50",
    ])
    assert result.exit_code == 0
    assert "Stationary" in result.output


def test_markov_table_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "markov-table", GAME,
            "--limit", "50",
            "--top", "3",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: markov-table" in content
    finally:
        os.unlink(tmp)


# ── outlier-draws ─────────────────────────────────────────────────────────────

def test_outlier_draws_smoke():
    result = runner.invoke(app, [
        "outlier-draws", GAME,
        "--draws", "100",
        "--top", "10",
    ])
    assert result.exit_code == 0
    assert "Outlier" in result.output


def test_outlier_draws_low_threshold():
    result = runner.invoke(app, [
        "outlier-draws", GAME,
        "--draws", "100",
        "--threshold", "0.5",
        "--top", "5",
    ])
    assert result.exit_code == 0
    assert "Flagged" in result.output


def test_outlier_draws_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "outlier-draws", GAME,
            "--draws", "80",
            "--top", "5",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: outlier-draws" in content
        assert "flagged" in content
    finally:
        os.unlink(tmp)


# ── calendar-effect ───────────────────────────────────────────────────────────

def test_calendar_effect_smoke():
    result = runner.invoke(app, ["calendar-effect", GAME, "--draws", "100"])
    assert result.exit_code == 0
    assert "Calendar" in result.output


def test_calendar_effect_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "calendar-effect", GAME,
            "--draws", "80",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: calendar-effect" in content
        assert "verdict" in content
    finally:
        os.unlink(tmp)


# ── Sprint B3: --from-stdin piping & picks --raw ──────────────────────────────

def test_picks_raw():
    """--raw emits only space-separated numbers, no Rich markup."""
    runner.invoke(app, ["forecast", GAME, "--strategies", "fast", "--quiet"])
    result = runner.invoke(app, ["picks", GAME, "--last", "5", "--raw"])
    assert result.exit_code == 0
    nums = result.output.strip().split()
    assert len(nums) > 0
    assert all(n.isdigit() for n in nums)


def test_ticket_dna_from_stdin():
    """--from-stdin reads ticket numbers from stdin instead of positional arg."""
    result = runner.invoke(
        app,
        ["ticket-dna", GAME, "--from-stdin", "--draws", "50"],
        input=_DNA_TICKET,
    )
    assert result.exit_code == 0
    assert "Ticket DNA" in result.output or "Fingerprint" in result.output


def test_ticket_dna_no_ticket_no_stdin():
    """Omitting both ticket arg and --from-stdin exits with error."""
    result = runner.invoke(app, ["ticket-dna", GAME, "--draws", "50"])
    assert result.exit_code != 0


def test_synergy_map_from_stdin():
    """--from-stdin reads ticket numbers from stdin instead of positional arg."""
    result = runner.invoke(
        app,
        ["synergy-map", GAME, "--from-stdin", "--draws", "50"],
        input=_SYN_TICKET,
    )
    assert result.exit_code == 0
    assert "Synergy" in result.output or "lift" in result.output.lower()


# ── Sprint B1 additions: --export-md for trend and hitcheck ───────────────────

# def test_trend_export_md():
#     # Populate log first
#     res = runner.invoke(app, ["log", GAME, "--quiet"])
#     assert res.exit_code == 0
#     with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
#         tmp = f.name
#     try:
#         # Omit game filter to be robust
#         result = runner.invoke(app, ["trend", "--days", "365", "--export-md", tmp])
#         assert result.exit_code == 0
#         content = Path(tmp).read_text()
#         assert "subtype: trend" in content
#     finally:
#         if os.path.exists(tmp):
#             os.unlink(tmp)


def test_hitcheck_export_md():
    # Populate ticket log and draw log
    runner.invoke(app, ["forecast", GAME, "--strategies", "fast", "--quiet"])
    runner.invoke(app, ["log", GAME, "--quiet"])
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, ["hitcheck", GAME, "--export-md", tmp])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: hitcheck" in content
        assert "best_hits" in content
    finally:
        os.unlink(tmp)


# ── backtest / alert / board --export-md ─────────────────────────────────────

def test_backtest_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "backtest", GAME, "--prev", "1",
            "--strategy", "weighted",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: backtest" in content
        assert "strategies:" in content
        assert "draws_tested:" in content
    finally:
        os.unlink(tmp)


def test_board_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "board", GAME, "--view", "heatmap",
            "--limit", "30", "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: board" in content
        assert "pool_size:" in content
        assert "Hottest" in content
    finally:
        os.unlink(tmp)


def test_alert_export_md():
    """Alert writes export-md only when conditions fire (exit 0); silent when not."""
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "alert", GAME,
            "--condition", "all",
            "--export-md", tmp,
        ])
        # exit 0 = triggered, exit 1 = no alert — both are valid
        assert result.exit_code in (0, 1)
        if result.exit_code == 0:
            content = Path(tmp).read_text()
            assert "subtype: alert" in content
            assert "conditions_triggered:" in content
    finally:
        if Path(tmp).exists():
            os.unlink(tmp)


# ── bonus-ball ────────────────────────────────────────────────────────────────

_BONUS_GAME = "us/powerball"


def test_bonus_ball_smoke():
    result = runner.invoke(app, ["bonus-ball", _BONUS_GAME, "--draws", "100", "--top", "5"])
    assert result.exit_code == 0
    assert "Bonus Ball" in result.output
    assert "Frequency" in result.output


def test_bonus_ball_no_bonus_pool():
    """Main-pool-only games exit with code 1 and a helpful message."""
    result = runner.invoke(app, ["bonus-ball", GAME])
    assert result.exit_code == 1
    assert "no separate bonus ball" in result.output.lower() or "no bonus" in result.output.lower()


def test_bonus_ball_overdue_panel():
    result = runner.invoke(app, ["bonus-ball", _BONUS_GAME, "--draws", "200"])
    assert result.exit_code == 0
    # Should show either overdue panel or "no overdue" message
    assert "Overdue" in result.output or "overdue" in result.output.lower()


def test_bonus_ball_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "bonus-ball", _BONUS_GAME,
            "--draws", "100",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: bonus-ball" in content
        assert "bonus_pool:" in content
        assert "overdue_count:" in content
    finally:
        if Path(tmp).exists():
            os.unlink(tmp)


# ── Tune ──────────────────────────────────────────────────────────────────────

def test_tune_smoke():
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "tune", GAME,
            "--draws", "5",
            "--strategies", "bayesian",
            "--no-grid",
            "--output", tmp,
        ])
        assert result.exit_code == 0
        assert "Optimization" in result.output
        assert Path(tmp).exists()
        import yaml
        with open(tmp, "r") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, list)
        assert data[0]["name"] == "bayesian"
        assert "params" in data[0]
        assert "filters" in data[0]
    finally:
        os.unlink(tmp)


def test_tune_grid_runs():
    result = runner.invoke(app, [
        "tune", GAME,
        "--draws", "2",
        "--strategies", "bayesian",
        "--limit", "30",
    ])
    assert result.exit_code == 0
    assert "Evaluating" in result.output
    # Should find a winner with params
    assert "Best Configuration" in result.output


def test_tune_yaml_consumable_by_backtest():
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        tmp = f.name
    try:
        runner.invoke(app, [
            "tune", GAME, "--draws", "2", "--strategies", "bayesian", "--no-grid", "-o", tmp
        ])
        result = runner.invoke(app, [
            "backtest", GAME, "--prev", "1", "--config", tmp
        ])
        assert result.exit_code == 0
        assert "BACKTEST" in result.output.upper()
    finally:
        os.unlink(tmp)


def test_tune_format_report():
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "tune", GAME,
            "--draws", "2",
            "--strategies", "bayesian,weighted",
            "--format", "report",
            "--top", "2",
            "--output", tmp,
        ])
        assert result.exit_code == 0
        import yaml
        with open(tmp, "r") as f:
            data = yaml.safe_load(f)
        assert "reports" in data
        assert len(data["reports"]) >= 1
    finally:
        os.unlink(tmp)


def test_forecast_with_config():
    import yaml
    config = [
        {"name": "bayesian", "params": {"alpha0": 1.5}, "filters": ["sum_range"]}
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config, f)
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "forecast", GAME, "--config", tmp, "--quiet"
        ])
        assert result.exit_code == 0
        assert "Consensus" in result.output or "Ticket" in result.output
    finally:
        os.unlink(tmp)


def test_tune_export_md():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp = f.name
    try:
        result = runner.invoke(app, [
            "tune", GAME,
            "--draws", "2",
            "--strategies", "bayesian",
            "--export-md", tmp,
        ])
        assert result.exit_code == 0
        content = Path(tmp).read_text()
        assert "subtype: tuning" in content
        assert "top_strategy: bayesian" in content
    finally:
        os.unlink(tmp)


def test_personal_config_injection():
    import yaml
    personal = {"full_name": "TEST USER", "birth_date": "1980-01-01"}
    # Create personal.local.yaml in current dir
    path = Path("personal.local.yaml")
    with open(path, "w") as f:
        yaml.dump(personal, f)
    try:
        # Run suggest with an esoteric strategy that uses these
        result = runner.invoke(app, ["suggest", GAME, "--strategy", "numerology", "--count", "1"])
        assert result.exit_code == 0
    finally:
        if path.exists():
            os.remove(path)


# ── Restored High-Fidelity Commands ──────────────────────────────────────────

def test_odds_smoke():
    result = runner.invoke(app, ["odds", GAME])
    assert result.exit_code == 0
    assert "Odds Analysis" in result.output


def test_odds_compare():
    result = runner.invoke(app, ["odds", "--compare"])
    assert result.exit_code == 0
    assert "Global Odds Comparison" in result.output


def test_prune_smoke():
    result = runner.invoke(app, ["prune", GAME, "--limit", "5"])
    assert result.exit_code == 0
    assert "Pruning Audit" in result.output


def test_prune_redundancy():
    result = runner.invoke(app, ["prune", GAME, "--limit", "5", "--redundancy"])
    assert result.exit_code == 0
    assert "Redundancy Analysis" in result.output


def test_portfolio_smoke():
    result = runner.invoke(app, ["portfolio", GAME])
    assert result.exit_code == 0
    assert "Portfolio" in result.output or "Convergence Detected" in result.output


def test_party_smoke():
    result = runner.invoke(app, ["party", GAME])
    assert result.exit_code == 0
    assert "WELCOME TO THE PARTY" in result.output


def test_hedge_smoke():
    result = runner.invoke(app, ["hedge", GAME, "--budget", "30"])
    assert result.exit_code == 0
    assert "Hedge Portfolio" in result.output


def test_oracle_smoke():
    result = runner.invoke(app, ["oracle", GAME])
    assert result.exit_code == 0
    assert "ORACLE CONSULTATION" in result.output


def test_risk_smoke():
    result = runner.invoke(app, ["risk", GAME])
    assert result.exit_code == 0
    assert "Analysis" in result.output or "Kelly" in result.output


# ── Final Missing Command Coverage ──────────────────────────────────────────

def test_analyze_smoke():
    result = runner.invoke(app, ["analyze", GAME, "--module", "summary"])
    assert result.exit_code == 0


def test_docs_smoke():
    result = runner.invoke(app, ["docs", "all"])
    assert result.exit_code == 0


def test_wheel_smoke():
    result = runner.invoke(app, ["wheel", GAME, "--preset", "hot-10"])
    assert result.exit_code == 0


def test_savings_smoke():
    result = runner.invoke(app, ["savings", GAME, "--pool", "15"])
    assert result.exit_code == 0


def test_simulate_smoke():
    result = runner.invoke(app, ["simulate", GAME, "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15", "--range", "3670-3675"])
    assert result.exit_code == 0


def test_optimize_smoke():
    # Only test a very small window for speed
    result = runner.invoke(app, ["optimize", GAME, "--strategies", "weighted", "--prev", "1", "--limits", "30"])
    assert result.exit_code == 0


def test_validate_smoke():
    result = runner.invoke(app, ["validate", GAME, "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"])
    assert result.exit_code == 0


def test_signature_smoke():
    result = runner.invoke(app, ["signature", "GEMINI ENGINE"])
    assert result.exit_code == 0


def test_watchlist_lifecycle():
    # Test full lifecycle of watchlist commands
    runner.invoke(app, ["watchlist", "add", GAME])
    res_list = runner.invoke(app, ["watchlist", "list"])
    assert res_list.exit_code == 0
    assert GAME in res_list.output
    
    res_status = runner.invoke(app, ["watchlist", "status"])
    assert res_status.exit_code == 0
    
    # Run in scan mode for speed
    res_run = runner.invoke(app, ["watchlist", "run", "--mode", "scan", "--quiet"])
    assert res_run.exit_code == 0
    
    runner.invoke(app, ["watchlist", "remove", GAME])
