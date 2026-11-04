"""Unit tests for Fringe Visualizer Widget & Dialog ⚛

Verifies PySide6 visual widget creation, physics mode switching,
and ticket recommendation logic across Mega-Sena and Quina.
"""

from __future__ import annotations

import os

# Enforce offscreen QPA for headless Linux CI environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pandas as pd
import pytest
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from desktop.src.widgets.fringe_visualizer import (
    FringeCanvasWidget,
    FringeVisualizerDialog,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_fringe_canvas_modes(qapp):
    canvas = FringeCanvasWidget()

    # Test all 4 physics modes on Mega-Sena
    for mode in ["ising", "lorenz", "tda", "multiverse"]:
        canvas.set_data("br/mega-sena", mode, df=pd.DataFrame())
        assert canvas.mode == mode
        assert len(canvas.scores) == 60

        # Verify QPainter paintEvent executes cleanly in memory
        img = QImage(500, 400, QImage.Format_ARGB32)
        img.fill(0)
        p = QPainter(img)
        canvas.paintEvent(None)
        p.end()


def test_fringe_dialog_initialization_and_ticket_generation(qapp):
    dialog = FringeVisualizerDialog(lottery_id="br/mega-sena")

    assert dialog.lottery_id == "br/mega-sena"
    assert hasattr(dialog, "current_ticket")
    assert len(dialog.current_ticket) == 6
    for num in dialog.current_ticket:
        assert 1 <= num <= 60


def test_fringe_dialog_quina_adaptation(qapp):
    dialog = FringeVisualizerDialog(lottery_id="br/quina")

    assert dialog.lottery_id == "br/quina"
    assert len(dialog.current_ticket) == 5
    for num in dialog.current_ticket:
        assert 1 <= num <= 80


def test_fringe_dialog_ticket_signal_emission(qapp):
    dialog = FringeVisualizerDialog(lottery_id="br/mega-sena")
    received_tickets = []

    dialog.ticket_selected.connect(lambda t: received_tickets.append(t))
    dialog._push_ticket()

    assert len(received_tickets) == 1
    assert len(received_tickets[0]) == 6
