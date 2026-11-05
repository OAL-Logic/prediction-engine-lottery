"""
Unit Tests for Fractional Kelly Allocator & Watcher Daemon (Track R & Issue 19)
================================================================================
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.modules.kelly_bankroll import (
    compute_fractional_kelly,
    compute_solo_equity_factor,
    format_kelly_report,
)

runner = CliRunner()


def test_solo_equity_factor():
    """Verify anti-popular subspace yields higher solo equity than popular."""
    anti_factor = compute_solo_equity_factor(subspace="anti-popular")
    pop_factor = compute_solo_equity_factor(subspace="popular")
    assert anti_factor > pop_factor
    assert anti_factor >= 1.0


def test_positive_ev_kelly_allocation():
    """Verify Kelly behavior when Expected Value > 0 (e.g. Mega da Virada 600M)."""
    res = compute_fractional_kelly(
        lottery="br/mega-sena",
        jackpot=600_000_000.0,
        bankroll=2000.0,
        fraction=0.05,
    )
    assert res.expected_value > 0
    assert "FAVORABLE" in res.verdict
    assert res.recommended_capital == 100.0  # 5% of 2000
    assert res.recommended_tickets == 20     # 100 / 5


def test_negative_ev_kelly_allocation():
    """Verify Kelly strictly allocates 0 tickets when Expected Value <= 0."""
    res = compute_fractional_kelly(
        lottery="br/mega-sena",
        jackpot=30_000_000.0,
        bankroll=2000.0,
        fraction=0.05,
    )
    assert res.expected_value < 0
    assert "UNFAVORABLE" in res.verdict
    assert res.recommended_capital == 0.0
    assert res.recommended_tickets == 0


def test_kelly_cli_command(tmp_path):
    """Test CLI `./p4lottery kelly` execution and markdown report export."""
    export_file = tmp_path / "kelly_report.md"
    result = runner.invoke(app, [
        "kelly",
        "br/mega-sena",
        "--jackpot", "600000000",
        "--bankroll", "1500",
        "--fraction", "0.05",
        "--export-md", str(export_file),
    ])
    assert result.exit_code == 0
    assert "FRACTIONAL KELLY BANKROLL ALLOCATOR" in result.output
    assert "BR/MEGA-SENA" in result.output
    assert export_file.is_file()
    assert "FRACTIONAL KELLY" in export_file.read_text(encoding="utf-8")


def test_watch_cli_command_once():
    """Test CLI `./p4lottery watch --once` execution."""
    result = runner.invoke(app, [
        "watch",
        "br/mega-sena",
        "--once",
        "--no-notify",
    ])
    assert result.exit_code == 0
    assert "P4LOTTERY LIVE WATCHER DAEMON" in result.output
    assert "Concurso #" in result.output
    assert "Ciclo de verificação #1 concluído" in result.output
