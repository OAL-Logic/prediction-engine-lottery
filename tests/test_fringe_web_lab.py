"""
Unit Test Suite for Interactive Fringe Synthesis Web Lab (Track J)
==================================================================
Tests offline HTML5 laboratory structure, interactive canvas/SVG visualizers,
JavaScript simulation functions, Popperian falsification table, and the CLI lab command.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.lab import lab

runner = CliRunner()


def test_frontier_synthesis_lab_html_exists():
    """Verify that frontier-synthesis-lab.html exists at docs/reference/."""
    lab_file = Path("docs/reference/frontier-synthesis-lab.html")
    assert lab_file.is_file(), f"Expected lab file at {lab_file}"
    content = lab_file.read_text(encoding="utf-8")
    assert len(content) > 10000, "Lab file should have extensive content"


def test_fringe_tab_and_canvas_elements():
    """Verify navigation button, panel ID, and all 4 quadrant visualizers."""
    lab_file = Path("docs/reference/frontier-synthesis-lab.html")
    content = lab_file.read_text(encoding="utf-8")

    # Tab navigation and panel
    assert 'onclick="openTab(\'tab-fringe\')"' in content
    assert 'id="tab-fringe"' in content

    # 4 Quadrant visualizer elements
    assert 'id="fringe-lorenz-canvas"' in content
    assert 'id="fringe-ising-canvas"' in content
    assert 'id="fringe-tda-svg"' in content
    assert 'id="fringe-multiverse-svg"' in content

    # Dynamic controls / sliders
    assert 'id="sl-lorenz-rho"' in content
    assert 'id="sl-lorenz-sigma"' in content
    assert 'id="sl-lorenz-rot"' in content
    assert 'id="sl-ising-temp"' in content
    assert 'id="sl-ising-j"' in content
    assert 'id="sl-tda-radius"' in content
    assert 'id="sl-multi-branches"' in content
    assert 'id="sl-multi-gamma"' in content


def test_popperian_falsification_table_all_9_theories():
    """Verify that all 9 fringe theories are documented in the synthesis table."""
    lab_file = Path("docs/reference/frontier-synthesis-lab.html")
    content = lab_file.read_text(encoding="utf-8")

    expected_theories = [
        "benford_illusion",
        "retrocausality",
        "quantum_multiverse",
        "ising_model",
        "zeno_quantum",
        "tda_topology",
        "sacred_grid",
        "lorentz",
        "noosphere",
    ]

    for theory_id in expected_theories:
        assert theory_id in content, f"Theory {theory_id} missing in synthesis lab table"

    # Verify physical machine archetypes
    assert "Mechanical Air-Mix" in content or "Air-Mix" in content
    assert "Gravity-Pick Drum" in content or "Gravity-Pick" in content
    assert "Pneumatic Chamber" in content


def test_javascript_simulation_functions():
    """Verify that all simulation logic and initializers are defined in JS."""
    lab_file = Path("docs/reference/frontier-synthesis-lab.html")
    content = lab_file.read_text(encoding="utf-8")

    # Lorenz Attractor functions
    assert "function updateFringeLorenzParams()" in content
    assert "function resetFringeLorenz()" in content
    assert "function drawFringeLorenz()" in content

    # Ising spin functions
    assert "function updateFringeIsingParams()" in content
    assert "function resetFringeIsing(" in content
    assert "function stepFringeIsing(" in content
    assert "function drawFringeIsing()" in content

    # TDA and Multiverse functions
    assert "function drawFringeTDA()" in content
    assert "function drawFringeMultiverse()" in content
    assert "function initFringeVisualizers()" in content

    # Hook into openTab
    assert 'if (tabId === "tab-fringe") initFringeVisualizers();' in content


def test_cli_lab_command_execution():
    """Verify ./p4lottery lab --no-browser runs cleanly via CliRunner."""
    result = runner.invoke(app, ["lab", "--no-browser", "--tab", "fringe", "--host"])
    assert result.exit_code == 0
    assert "INTERACTIVE SYNTHESIS LAB" in result.output
    assert "frontier-synthesis-lab.html" in result.output
    assert "fringe" in result.output
    assert "Disabled (--no-browser)" in result.output
    assert "Lorenz Chaotic Attractor" in result.output
    assert "Ising Spin Lattice" in result.output
    assert "Persistent Homology" in result.output
    assert "Everett Quantum Multiverse" in result.output
