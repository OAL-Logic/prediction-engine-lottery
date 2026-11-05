"""
Unit Tests for Fringe Swarm & Telemetry Engine (Track K)
=======================================================
Validates multi-modal consensus polling, Jensen-Shannon divergence calculations,
dynamic counter-hedging tickets, and CLI command execution.
"""

from __future__ import annotations

import numpy as np
import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.modules.fringe_swarm import (
    compute_jensen_shannon_divergence,
    run_fringe_swarm_telemetry,
    export_swarm_report_md,
    SwarmConsensusReport,
)

runner = CliRunner()


def test_jensen_shannon_divergence_properties():
    """Verify mathematical properties of Jensen-Shannon divergence."""
    p = np.array([0.2, 0.3, 0.5])
    q = np.array([0.2, 0.3, 0.5])
    # Identical distributions have JSD = 0
    assert abs(compute_jensen_shannon_divergence(p, q)) < 1e-6

    # Completely disjoint distributions have JSD = 1.0
    p_disjoint = np.array([1.0, 0.0, 0.0])
    q_disjoint = np.array([0.0, 1.0, 0.0])
    jsd_disjoint = compute_jensen_shannon_divergence(p_disjoint, q_disjoint)
    assert abs(jsd_disjoint - 1.0) < 1e-4

    # Symmetry: JSD(P || Q) == JSD(Q || P)
    p_asym = np.array([0.1, 0.7, 0.2])
    q_asym = np.array([0.4, 0.3, 0.3])
    jsd_1 = compute_jensen_shannon_divergence(p_asym, q_asym)
    jsd_2 = compute_jensen_shannon_divergence(q_asym, p_asym)
    assert abs(jsd_1 - jsd_2) < 1e-9
    assert 0.0 <= jsd_1 <= 1.0


def test_run_fringe_swarm_telemetry_structure():
    """Verify execution of fringe swarm telemetry for Mega-Sena."""
    report = run_fringe_swarm_telemetry(
        lottery="br/mega-sena",
        draws_window=40,
        num_tickets=4,
        hedge_ratio=0.5,
        emit_telemetry=False,
        seed=123,
    )

    assert isinstance(report, SwarmConsensusReport)
    assert report.lottery == "br/mega-sena"
    assert report.total_fringe_strategies == 9
    assert report.total_orthodox_strategies >= 1
    assert 0.0 <= report.disagreement_index <= 1.0
    assert len(report.consensus_numbers) > 0

    # Validate ticket constraints
    all_tickets = report.core_tickets + report.hedged_tickets
    assert len(all_tickets) == 4
    for ticket in all_tickets:
        assert len(ticket) == 6
        assert len(set(ticket)) == 6  # All distinct
        for n in ticket:
            assert 1 <= n <= 60

    # Telemetry payload
    payload = report.telemetry_payload
    assert payload["event"] == "fringe_swarm_pulse"
    assert "disagreement_index" in payload
    assert "epistemic_regime" in payload


def test_export_swarm_report_md(tmp_path):
    """Verify markdown report generation adhering to Zero-PII."""
    report = run_fringe_swarm_telemetry(
        lottery="br/mega-sena",
        draws_window=30,
        num_tickets=3,
        seed=42,
    )
    out_file = tmp_path / "test_telemetry.md"
    export_swarm_report_md(report, str(out_file))

    assert out_file.is_file()
    text = out_file.read_text(encoding="utf-8")
    assert "Autonomous Fringe Swarm & Telemetry Report (Track K)" in text
    assert "Consensus Disagreement Index" in text
    assert "fringe_swarm_pulse" in text


def test_cli_fringe_swarm_command():
    """Verify ./p4lottery fringe-swarm CLI invocation."""
    result = runner.invoke(app, [
        "fringe-swarm",
        "br/mega-sena",
        "--draws", "30",
        "--tickets", "3",
        "--hedge-ratio", "0.33",
        "--quiet",
    ])
    assert result.exit_code == 0
