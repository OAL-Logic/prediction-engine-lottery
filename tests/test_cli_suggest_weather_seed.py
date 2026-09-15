"""
Weather-Seed / Esoteric-Mode CLI Tests 🌍
==========================================
Verifies `suggest --weather-seed` and `suggest --esoteric-mode` on real
br/lotofacil data (same convention as test_cli_suggest.py): don't crash,
print the transparent ingredient/seed panel, and — the actual point of the
feature — are reproducible across runs.
"""

from __future__ import annotations

from typer.testing import CliRunner
from engine.cli.main import app

runner = CliRunner()
GAME = "br/lotofacil"


def _ok(result):
    assert result.exit_code == 0, f"Exit {result.exit_code}:\n{result.output}"
    assert result.output.strip(), "Command produced no output"


def test_weather_seed_smoke():
    """--weather-seed must not crash and must print the environmental seed panel."""
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "weighted", "--limit", "200", "--weather-seed"])
    _ok(result)
    assert "Environmental Seed" in result.output
    assert "Deterministic seed" in result.output


def test_weather_seed_is_reproducible():
    """Same day, same location -> same seed and same ticket across independent runs."""
    r1 = runner.invoke(app, ["suggest", GAME, "--strategy", "weighted", "--limit", "200", "--weather-seed"])
    r2 = runner.invoke(app, ["suggest", GAME, "--strategy", "weighted", "--limit", "200", "--weather-seed"])
    _ok(r1)
    _ok(r2)

    def _seed_line(output: str) -> str:
        return next(line for line in output.splitlines() if "Deterministic seed" in line)

    def _ticket_line(output: str) -> str:
        return next(line for line in output.splitlines() if "Ticket 1:" in line)

    assert _seed_line(r1.output) == _seed_line(r2.output)
    assert _ticket_line(r1.output) == _ticket_line(r2.output)


def test_esoteric_mode_smoke():
    """--esoteric-mode must not crash, implies --weather-seed, and prints an honest significance verdict."""
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "weighted", "--limit", "200", "--esoteric-mode"])
    _ok(result)
    assert "Environmental Seed" in result.output          # implied --weather-seed
    assert "Esoteric Significance Check" in result.output
    assert ("significant" in result.output.lower())        # either "SIGNIFICANT" or "not significant"


def test_esoteric_mode_does_not_change_selected_strategy():
    """--esoteric-mode must only add reporting; it must not silently swap the requested strategy."""
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "weighted", "--limit", "200", "--esoteric-mode"])
    _ok(result)
    assert "WEIGHTED PREDICTION" in result.output


def test_suggest_without_new_flags_is_unaffected():
    """Baseline: omitting both new flags must behave exactly as before (no seed panel, no crash)."""
    result = runner.invoke(app, ["suggest", GAME, "--strategy", "weighted", "--limit", "200"])
    _ok(result)
    assert "Environmental Seed" not in result.output
    assert "Esoteric Significance Check" not in result.output
