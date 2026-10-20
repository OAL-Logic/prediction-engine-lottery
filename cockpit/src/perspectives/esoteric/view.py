"""
Esoteric & Deterministic Chaos Observatory Perspective
======================================================
Multi-dimensional laboratory combining:
1. 60fps GPU-Accelerated 3D OpenGL Strange Attractor Visualizer
2. 3D Kinetic Lottery Drum simulation
3. Historical Draw Phase-Space Trajectory mapping
4. Celestial Ephemeris Zodiac & Lunar Phase Dial
5. Multi-Track Biorhythm Waveform Forecaster
6. Kabbalistic Tree of Life (10 Sephirot & 22 Paths)
7. Esoteric Chaos Ticket Synthesis Engine
"""

from __future__ import annotations

import logging
import datetime
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QFrame, QSplitter, QComboBox, QSlider,
    QTabWidget, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

from cockpit.src.core.models import GameSchema, TicketReceipt
from cockpit.src.charts.opengl_3d import OpenGLChaosCanvas
from cockpit.src.perspectives.esoteric.widgets import (
    CelestialEphemerisWidget, BiorhythmChartWidget, KabbalahTreeWidget
)
from cockpit.src.widgets.ticket_receipt import TicketReceiptWidget
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.theme.tokens import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_DEFAULT, RADIUS_MD, FONT_MONO, FONT_HEADING, FONT_BODY
)

logger = logging.getLogger(__name__)


class EsotericPerspectiveView(QWidget):
    """
    Perspective view dedicated to 2D & 3D deterministic chaos analysis
    and celestial harmonics prediction.
    """

    tickets_synthesized = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.bridge = EngineBridge()
        self.active_game: Optional[GameSchema] = None
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        main_layout.setSpacing(SPACING_MD)

        # Splitter: Left 3D Chaos Canvas vs Right Esoteric Analytics Notebook
        splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Panel: 3D Strange Attractor & Kinetic Drum Canvas
        # -------------------------------------------------------------
        left_box = QGroupBox("3D DETERMINISTIC CHAOS OBSERVATORY (60 FPS GPU)")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        left_layout.setSpacing(SPACING_SM)

        # Top 3D Control Bar
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(SPACING_SM)

        ctrl_bar.addWidget(QLabel("Attractor System:"))
        self.combo_attractor = QComboBox()
        self.combo_attractor.addItems([
            "Lorenz Attractor (Butterfly Effect)",
            "Rössler Attractor (Hyperchaos)",
            "Aizawa Attractor (Spherical Invariant)",
            "3D Kinetic Ball Chamber (Drum Bounce)",
            "Draw Phase-Space Orbits (Historical)"
        ])
        self.combo_attractor.currentIndexChanged.connect(self._on_attractor_changed)
        ctrl_bar.addWidget(self.combo_attractor, stretch=2)

        self.chk_auto_rotate = QCheckBox("Auto-Orbit")
        self.chk_auto_rotate.setChecked(True)
        self.chk_auto_rotate.toggled.connect(self._on_auto_rotate_toggled)
        ctrl_bar.addWidget(self.chk_auto_rotate)

        ctrl_bar.addWidget(QLabel("Speed:"))
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(1, 20)
        self.slider_speed.setValue(5)
        self.slider_speed.valueChanged.connect(self._on_speed_changed)
        ctrl_bar.addWidget(self.slider_speed, stretch=1)

        left_layout.addLayout(ctrl_bar)

        # Primary 3D OpenGL Canvas
        self.canvas_3d = OpenGLChaosCanvas(self)
        self.canvas_3d.setMinimumSize(550, 480)
        left_layout.addWidget(self.canvas_3d, stretch=1)

        # Bottom Prediction Synthesis Action Bar
        bottom_action_layout = QHBoxLayout()
        bottom_action_layout.setSpacing(SPACING_SM)

        self.btn_synthesize = QPushButton("✨ SYNTHESIZE CHAOS PREDICTION (10 TICKETS)")
        self.btn_synthesize.setObjectName("btn_primary")
        self.btn_synthesize.setCursor(Qt.PointingHandCursor)
        self.btn_synthesize.setMinimumHeight(36)
        self.btn_synthesize.clicked.connect(self._synthesize_chaos_prediction)
        bottom_action_layout.addWidget(self.btn_synthesize, stretch=3)

        btn_reload = QPushButton("🔄 Reset Attractor")
        btn_reload.setCursor(Qt.PointingHandCursor)
        btn_reload.setMinimumHeight(36)
        btn_reload.clicked.connect(lambda: self._on_attractor_changed(self.combo_attractor.currentIndex()))
        bottom_action_layout.addWidget(btn_reload, stretch=1)

        left_layout.addLayout(bottom_action_layout)
        splitter.addWidget(left_box)

        # -------------------------------------------------------------
        # Right Panel: Multi-Tab Esoteric & Celestial Notebook
        # -------------------------------------------------------------
        right_box = QGroupBox("ESOTERIC & CELESTIAL ANALYTICS")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        right_layout.setSpacing(SPACING_SM)

        self.notebook = QTabWidget()

        # Tab 1: Celestial Ephemeris
        tab_ephemeris = QWidget()
        tab_e_layout = QVBoxLayout(tab_ephemeris)
        tab_e_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        self.ephemeris_widget = CelestialEphemerisWidget(self)
        tab_e_layout.addWidget(self.ephemeris_widget, stretch=1)

        lbl_lunar_info = QLabel("Zodiac Positions & Lunar Illuminations calibrated to Draw Horizon.")
        lbl_lunar_info.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 10px; color: #8b9bb4;")
        tab_e_layout.addWidget(lbl_lunar_info)
        self.notebook.addTab(tab_ephemeris, "🌙 Celestial Ephemeris")

        # Tab 2: Biorhythm Multi-Track
        tab_biorhythm = QWidget()
        tab_b_layout = QVBoxLayout(tab_biorhythm)
        tab_b_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        self.biorhythm_widget = BiorhythmChartWidget(self)
        tab_b_layout.addWidget(self.biorhythm_widget, stretch=1)

        lbl_bio_info = QLabel("Harmonic Crossover Points: Physical (23d), Emotional (28d), Intellectual (33d), Intuitive (38d).")
        lbl_bio_info.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 10px; color: #8b9bb4;")
        tab_b_layout.addWidget(lbl_bio_info)
        self.notebook.addTab(tab_biorhythm, "〰️ Biorhythm Waveforms")

        # Tab 3: Kabbalistic Tree of Life
        tab_kabbalah = QWidget()
        tab_k_layout = QVBoxLayout(tab_kabbalah)
        tab_k_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        self.kabbalah_widget = KabbalahTreeWidget(self)
        tab_k_layout.addWidget(self.kabbalah_widget, stretch=1)

        lbl_kab_info = QLabel("10 Sephirot Emanations mapped to Digital Roots & Gematria Reductions.")
        lbl_kab_info.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 10px; color: #8b9bb4;")
        tab_k_layout.addWidget(lbl_kab_info)
        self.notebook.addTab(tab_kabbalah, "🌳 Kabbalah Tree")

        # Tab 4: Synthesized Tickets
        tab_tickets = QWidget()
        tab_t_layout = QVBoxLayout(tab_tickets)
        tab_t_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        self.ticket_viewer = TicketReceiptWidget(self)
        tab_t_layout.addWidget(self.ticket_viewer, stretch=1)
        self.notebook.addTab(tab_tickets, "🎟️ Synthesized Tickets")

        right_layout.addWidget(self.notebook)
        splitter.addWidget(right_box)

        splitter.setSizes([750, 450])
        main_layout.addWidget(splitter)

    # -------------------------------------------------------------------------
    # Visualizer Coordination
    # -------------------------------------------------------------------------

    def _on_attractor_changed(self, idx: int) -> None:
        modes = ["lorenz", "rossler", "aizawa", "kinetic_drum", "phase_space"]
        mode = modes[idx]

        if mode == "phase_space":
            if self.active_game:
                df = self.bridge.get_draws(self.active_game.id, limit=60)
                if not df.empty and "numbers" in df.columns:
                    self.canvas_3d.load_draws_phase_space(df["numbers"].tolist())
                else:
                    self.canvas_3d.load_attractor("lorenz")
            else:
                self.canvas_3d.load_attractor("lorenz")
        else:
            self.canvas_3d.load_attractor(mode)

    def _on_auto_rotate_toggled(self, checked: bool) -> None:
        self.canvas_3d.set_auto_rotate(checked)

    def _on_speed_changed(self, val: int) -> None:
        self.canvas_3d.set_rotation_speed(val / 10.0)

    def set_active_game(self, game: GameSchema) -> None:
        self.active_game = game
        self.ephemeris_widget.set_draw_date(datetime.date.today())
        # Update Kabbalah nodes with hot numbers
        df = self.bridge.get_draws(game.id, limit=10)
        if not df.empty and "numbers" in df.columns:
            recent_balls = [num for sublist in df["numbers"].tolist() for num in sublist]
            self.kabbalah_widget.set_active_numbers(recent_balls)

    def _synthesize_chaos_prediction(self, show_dialog: bool = True) -> None:
        if not self.active_game:
            return

        tickets = self.bridge.generate_archetype_tickets(
            game_id=self.active_game.id,
            archetype_key="archetype_cosmic",
            count=10
        )

        for t in tickets:
            t.strategy_source = "Chaos & Cosmic Observatory"

        self.ticket_viewer.display_tickets(tickets)
        self.notebook.setCurrentIndex(3)  # Switch to Tickets tab
        self.tickets_synthesized.emit(tickets)

        if show_dialog:
            QMessageBox.information(
                self,
                "Chaos Synthesis Complete",
                f"Successfully synthesized {len(tickets)} candidate tickets from strange attractor intersections and celestial harmonics for {self.active_game.name}."
            )
