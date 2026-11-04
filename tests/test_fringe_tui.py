"""
Tests for Fringe Physics Terminal Inspector (`engine.tui.fringe_inspector` & `engine.cli.commands.fringe_inspect`).
"""

import math
from pathlib import Path
import pytest
from rich.layout import Layout
from rich.panel import Panel

from engine.adapters import DrawRules
from engine.tui.fringe_inspector import (
    BrailleCanvas,
    LorenzSimulator,
    IsingModelSimulator,
    render_lorenz_panel,
    render_ising_panel,
    render_tda_panel,
    render_noosphere_panel,
    render_quantum_panel,
    FringeTUIApp,
    export_markdown_snapshot,
)
from engine.cli.commands.fringe_inspect import fringe_inspect


def test_braille_canvas():
    canvas = BrailleCanvas(char_width=20, char_height=8)
    assert canvas.pixel_width == 40
    assert canvas.pixel_height == 32

    # Draw diagonal line
    canvas.draw_line(0, 0, 39, 31)
    text = canvas.render_text()
    lines = text.split("\n")
    assert len(lines) == 8
    assert all(len(line) == 20 for line in lines)
    # Check that braille characters were rendered
    assert any(ord(ch) > 0x2800 for line in lines for ch in line)


def test_lorenz_simulator():
    sim = LorenzSimulator()
    state = sim.step_rk4(dt=0.01)
    assert len(state) == 3
    assert all(isinstance(v, float) for v in state)

    orbit = sim.generate_orbit(steps=100)
    assert orbit.shape == (100, 3)
    assert not math.isnan(orbit[-1, 0])


def test_ising_simulator_archetypes():
    rules_mega = DrawRules("Mega-Sena", 6, (1, 60), board_cols=10)
    sim_mega = IsingModelSimulator(rules_mega)
    assert sim_mega.rows == 6
    assert sim_mega.cols == 10

    rules_quina = DrawRules("Quina", 5, (1, 80), board_cols=10)
    sim_quina = IsingModelSimulator(rules_quina)
    assert sim_quina.rows == 8
    assert sim_quina.cols == 10

    rules_loto = DrawRules("Lotofácil", 15, (1, 25), board_cols=5)
    sim_loto = IsingModelSimulator(rules_loto)
    assert sim_loto.rows == 5
    assert sim_loto.cols == 5

    # Run Metropolis sweep
    sim_mega.step_metropolis(sweeps=2)
    mag = sim_mega.magnetization()
    assert -1.0 <= mag <= 1.0
    energy = sim_mega.total_energy()
    assert isinstance(energy, float)


def test_render_all_panels():
    rules = DrawRules("Mega-Sena", 6, (1, 60))
    sim = IsingModelSimulator(rules)

    p_lorenz = render_lorenz_panel(rules)
    assert isinstance(p_lorenz, Panel)

    p_ising = render_ising_panel(rules, sim)
    assert isinstance(p_ising, Panel)

    p_tda = render_tda_panel(rules)
    assert isinstance(p_tda, Panel)

    p_noosphere = render_noosphere_panel(step=5)
    assert isinstance(p_noosphere, Panel)

    p_quantum = render_quantum_panel(rules)
    assert isinstance(p_quantum, Panel)


def test_fringe_tui_app_modes():
    rules = DrawRules("Quina", 5, (1, 80))
    for mode in ["all", "lorenz", "ising", "tda", "noosphere", "quantum"]:
        app = FringeTUIApp(rules=rules, mode=mode)
        layout = app.render_snapshot()
        assert isinstance(layout, Layout)


def test_export_markdown_snapshot(tmp_path):
    rules = DrawRules("Mega-Sena", 6, (1, 60))
    app = FringeTUIApp(rules=rules, mode="all")
    export_file = tmp_path / "snapshot.md"
    export_markdown_snapshot(app, export_file)
    assert export_file.exists()
    content = export_file.read_text(encoding="utf-8")
    assert "Atrator Caótico de Lorenz" in content
    assert "Rede Ferromagnética de Ising" in content
    assert "Zero-PII Auditado" in content


def test_cli_fringe_inspect_command(tmp_path):
    report_file = tmp_path / "cli_snap.md"
    fringe_inspect(
        lottery="br/mega-sena",
        mode="all",
        draws=10,
        live=False,
        export_md=str(report_file),
    )
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Mega-Sena" in content
