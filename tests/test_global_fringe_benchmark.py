"""
Tests for Global Multi-Jurisdiction Fringe Benchmark Engine 🌐🔬
================================================================
Validates:
1. Physical machine archetype taxonomy and mapping.
2. Cross-jurisdiction blind backtesting execution.
3. Theoretical EV calculation across different pick/pool matrix sizes.
4. H_0 hypothesis retention verification.
5. CLI command execution and report export.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from engine.modules.global_fringe_benchmark import (
    CANONICAL_FRINGE_THEORIES,
    LOTTERY_MACHINE_MAP,
    PhysicalMachineArchetype,
    run_global_fringe_benchmark,
)
from engine.cli.commands.global_fringe_bench import global_fringe_bench


def test_machine_archetype_mapping():
    """Verify physical machine archetypes are properly assigned."""
    assert LOTTERY_MACHINE_MAP["br/mega-sena"][0] == PhysicalMachineArchetype.AIR_MIX
    assert LOTTERY_MACHINE_MAP["us/powerball"][0] == PhysicalMachineArchetype.GRAVITY_PICK
    assert LOTTERY_MACHINE_MAP["eu/euro-millions"][0] == PhysicalMachineArchetype.PNEUMATIC_CHAMBER


def test_run_global_fringe_benchmark_execution():
    """Execute mini benchmark across Mega-Sena and Powerball."""
    result = run_global_fringe_benchmark(
        lotteries=["br/mega-sena", "us/powerball"],
        draws=10,
        seed=42,
    )
    assert result.total_lotteries == 2
    assert result.total_draws_evaluated == 20
    assert "BR" in result.jurisdictions
    assert "US" in result.jurisdictions
    assert result.all_h0_retained is True
    assert "GLOBAL H_0 RETAINED" in result.cross_machine_verdict

    # Check Mega-Sena metrics
    ms = result.lottery_summaries["br/mega-sena"]
    assert ms.pool_n == 60
    assert ms.pick_k == 6
    assert abs(ms.theoretical_ev - 0.60) < 1e-4
    assert len(ms.strategies) == len(CANONICAL_FRINGE_THEORIES)

    # Check Powerball metrics
    pb = result.lottery_summaries["us/powerball"]
    assert pb.pool_n == 69
    assert pb.pick_k == 5
    assert abs(pb.theoretical_ev - (25 / 69)) < 1e-4
    assert len(pb.strategies) == len(CANONICAL_FRINGE_THEORIES)


def test_cli_global_fringe_bench_and_report_export(tmp_path: Path):
    """Verify CLI command executes and produces valid global report."""
    report_file = tmp_path / "global_report.md"
    global_fringe_bench(
        lotteries="br/mega-sena,us/powerball",
        draws=10,
        seed=42,
        export_md=str(report_file),
        quiet=True,
    )
    assert report_file.is_file()
    content = report_file.read_text(encoding="utf-8")
    assert "Avaliação Internacional de Teorias Marginais" in content
    assert "GRAVITY_PICK" in content
    assert "AIR_MIX" in content
    assert "flowchart LR" in content
