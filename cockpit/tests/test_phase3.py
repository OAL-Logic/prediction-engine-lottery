"""
Phase 3 Test Suite: 3D Chaos Observatory & Esoteric Analytics
=============================================================
Comprehensive verification for Phase 3:
1. OpenGL 3D Strange Attractor Generation (Lorenz, Rössler, Aizawa)
2. 3D Kinetic Lottery Drum Particle Simulation
3. 3D Historical Draw Phase-Space Mapping
4. Celestial Ephemeris Zodiac & Lunar Illumination Calculations
5. Biorhythm Multi-Track Waveform Generators
6. Kabbalistic Tree of Life Sephirot Digital Root Mapping
7. Esoteric Chaos Ticket Synthesis Engine
8. Shell Perspective Switching for Esoteric Workspace
"""

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
import datetime
import numpy as np
from PySide6.QtWidgets import QApplication

from cockpit.src.core.models import GameSchema, PerspectiveType
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.charts.opengl_3d import OpenGLChaosCanvas, HAS_OPENGL
from cockpit.src.perspectives.esoteric.widgets import (
    CelestialEphemerisWidget, BiorhythmChartWidget, KabbalahTreeWidget
)
from cockpit.src.perspectives.esoteric.view import EsotericPerspectiveView
from cockpit.src.shell.main_window import CockpitMainWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def bridge() -> EngineBridge:
    return EngineBridge()


@pytest.fixture
def lotofacil_game(bridge: EngineBridge) -> GameSchema:
    game = bridge.get_game("br/lotofacil")
    assert game is not None
    return game


def test_opengl_attractor_generators(app):
    """Verifies strange attractor mathematical calculations and item allocation."""
    canvas = OpenGLChaosCanvas()
    assert canvas is not None

    # Test Lorenz
    canvas.load_attractor("lorenz", steps=500)
    assert canvas._current_mode == "lorenz"

    # Test Rössler
    canvas.load_attractor("rossler", steps=500)
    assert canvas._current_mode == "rossler"

    # Test Aizawa
    canvas.load_attractor("aizawa", steps=500)
    assert canvas._current_mode == "aizawa"

    # Test Kinetic Drum
    canvas.load_attractor("kinetic_drum", ball_count=15)
    assert canvas._current_mode == "kinetic_drum"
    assert canvas._particle_pos is not None
    assert canvas._particle_pos.shape == (15, 3)

    # Test Particle Physics Step
    canvas._update_kinetic_particles()
    assert canvas._particle_pos.shape == (15, 3)


def test_draws_phase_space_mapping(app):
    """Verifies that historical drawings map to valid 3D points."""
    canvas = OpenGLChaosCanvas()
    sample_draws = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4]
    ]

    canvas.load_draws_phase_space(sample_draws)
    assert canvas._current_mode == "phase_space"


def test_celestial_ephemeris_calculations(app):
    """Verifies planetary angle and lunar illumination calculations."""
    widget = CelestialEphemerisWidget()
    test_date = datetime.date(2026, 10, 15)
    widget.set_draw_date(test_date)

    for planet, data in widget._planets.items():
        assert 0.0 <= data["angle"] < 360.0, f"Angle out of range for {planet}: {data['angle']}"

    assert 0.0 <= widget._lunar_illumination <= 1.0
    assert widget._moon_phase_name in ["New Moon", "First Quarter / Waxing", "Full Moon", "Last Quarter / Waning"]


def test_biorhythm_chart_waveforms(app):
    """Verifies that biorhythm sinusoidal curves are generated for the 4 tracks."""
    chart = BiorhythmChartWidget()
    chart.plot_biorhythms(days_offset=5)
    # Check that curves were added
    items = chart.plot_widget.listDataItems()
    assert len(items) == 4, f"Expected 4 biorhythm tracks, got {len(items)}"


def test_kabbalah_tree_digital_roots(app):
    """Verifies mapping of lottery numbers into Sephirot nodes via digital roots."""
    tree = KabbalahTreeWidget()
    numbers = [10, 19, 28] # Digital roots: 10->1, 19->1, 28->1 (Keter)
    tree.set_active_numbers(numbers)
    assert 1 in tree._highlighted_nodes


def test_esoteric_perspective_synthesis(lotofacil_game: GameSchema, app):
    """Verifies ticket synthesis from esoteric and chaos state."""
    view = EsotericPerspectiveView()
    view.set_active_game(lotofacil_game)

    captured_tickets = []
    view.tickets_synthesized.connect(lambda t: captured_tickets.extend(t))

    view._synthesize_chaos_prediction(show_dialog=False)
    assert len(captured_tickets) == 10
    for ticket in captured_tickets:
        assert len(ticket.numbers) == lotofacil_game.pick_count
        assert ticket.strategy_source == "Chaos & Cosmic Observatory"
        assert ticket.confidence_score > 0.0


def test_shell_perspective_switching(app):
    """Verifies that the shell switches smoothly between Express, Studio, and Esoteric perspectives."""
    window = CockpitMainWindow()
    assert window.view_esoteric is not None

    # Switch to Esoteric
    window.perspective_manager.switch_perspective(PerspectiveType.ESOTERIC)
    assert window.perspective_manager.current_perspective == PerspectiveType.ESOTERIC
    assert window.central_stack.currentWidget() == window.view_esoteric

    # Switch back to Studio
    window.perspective_manager.switch_perspective(PerspectiveType.STUDIO)
    assert window.perspective_manager.current_perspective == PerspectiveType.STUDIO
    assert window.central_stack.currentWidget() == window.view_studio

    # Switch back to Express
    window.perspective_manager.switch_perspective(PerspectiveType.EXPRESS)
    assert window.perspective_manager.current_perspective == PerspectiveType.EXPRESS
    assert window.central_stack.currentWidget() == window.view_express
