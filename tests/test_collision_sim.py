"""
Unit & Integration Tests for Collision Simulator 🧪🎱
===================================================
"""

from __future__ import annotations

from typer.testing import CliRunner
from engine.cli.commands.collision_sim import run_simulation
from engine.cli.main import app

runner = CliRunner()

def test_run_simulation():
    """Verify that core simulation produces correctly normalized scores."""
    scores = run_simulation(
        number_range=(1, 25),
        trials=1,
        steps=20,
        dt=0.01,
        g_val=-9.8,
        ink_delta=0.001,
        rotation_speed=1.0,
    )
    assert len(scores) == 25
    for num, score in scores.items():
        assert 0.0 <= score <= 1.0

def test_collision_sim_cli():
    """Verify that collision-sim command runs without errors."""
    result = runner.invoke(app, ["collision-sim", "br/lotofacil", "--trials", "1", "--steps", "10"])
    assert result.exit_code == 0
    assert "Pseudo-Kinetic Fluid Simulator" in result.stdout
    assert "Kinetic Chute Candidates" in result.stdout
    assert "Kinetic Alpha Ticket" in result.stdout
