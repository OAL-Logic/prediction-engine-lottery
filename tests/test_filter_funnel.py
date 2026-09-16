"""
Filter Funnel CLI Tests 🕳️
==========================
"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app

runner = CliRunner()
GAME = "br/mega-sena"


def test_list_filters_shows_catalog():
    result = runner.invoke(app, ["filter-funnel", GAME, "--list-filters", "--tier", "1"])
    assert result.exit_code == 0, result.output
    assert "structural_odd_count" in result.output


def test_filter_funnel_requires_pool_and_filters():
    result = runner.invoke(app, ["filter-funnel", GAME])
    assert result.exit_code != 0


def test_filter_funnel_runs_and_narrows():
    result = runner.invoke(app, [
        "filter-funnel", GAME,
        "--pool", ",".join(str(n) for n in range(1, 16)),  # 15 numbers, pick 6 -> C(15,6)=5005
        "--filters", "algebraic_number_sum,structural_odd_even_ratio",
    ])
    assert result.exit_code == 0, result.output
    assert "FILTER FUNNEL" in result.output
    assert "5,005" in result.output


def test_filter_funnel_rejects_oversized_pool():
    result = runner.invoke(app, [
        "filter-funnel", GAME,
        "--pool", ",".join(str(n) for n in range(1, 61)),  # full pool, C(60,6) way over cap
        "--filters", "algebraic_number_sum",
    ])
    assert result.exit_code != 0
    assert "safety cap" in result.output


def test_filter_funnel_handles_unknown_filter_id_gracefully():
    result = runner.invoke(app, [
        "filter-funnel", GAME,
        "--pool", ",".join(str(n) for n in range(1, 12)),
        "--filters", "not_a_real_filter_id",
    ])
    assert result.exit_code == 0, result.output
    assert "not_a_real_filter_id" in result.output
    assert "462 / 462" in result.output  # unknown filter id is a no-op, not a crash
