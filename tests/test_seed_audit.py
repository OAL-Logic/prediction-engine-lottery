"""Seed Audit CLI Tests 🌍🔍"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app

runner = CliRunner()
GAME = "br/mega-sena"


def test_seed_audit_registered_and_runs():
    result = runner.invoke(app, ["seed-audit", GAME])
    assert result.exit_code == 0, result.output
    assert "Seed Audit" in result.output
    assert "Deterministic seed" in result.output


def test_seed_audit_is_reproducible_for_same_date():
    r1 = runner.invoke(app, ["seed-audit", GAME, "--date", "2026-06-15"])
    r2 = runner.invoke(app, ["seed-audit", GAME, "--date", "2026-06-15"])
    assert r1.exit_code == 0 and r2.exit_code == 0
    assert r1.output == r2.output


def test_seed_audit_rejects_bad_date():
    result = runner.invoke(app, ["seed-audit", GAME, "--date", "not-a-date"])
    assert result.exit_code != 0
    assert "Invalid --date" in result.output


def test_seed_audit_matches_build_environmental_seed_directly():
    """The audit command must surface exactly the seed build_environmental_seed() computes."""
    import re
    from datetime import date
    from engine.cli.utils import get_adapter
    from engine.modules.esoteric_pipeline import build_environmental_seed

    adapter = get_adapter(GAME)
    coords = adapter.get_draw_location() if hasattr(adapter, "get_draw_location") else (-23.5505, -46.6333)
    expected_seed, _ = build_environmental_seed(coords, target_date=date(2026, 7, 1))

    result = runner.invoke(app, ["seed-audit", GAME, "--date", "2026-07-01"])
    assert result.exit_code == 0, result.output
    m = re.search(r"Deterministic seed:\s*(\d+)", result.output)
    assert m is not None, result.output
    assert int(m.group(1)) == expected_seed
