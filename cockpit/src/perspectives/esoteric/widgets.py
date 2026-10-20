"""
Esoteric & Celestial Analytics Widgets
======================================
Interactive 2D visualization components:
1. Celestial Ephemeris Zodiac Circle & Lunar Phase Dial
2. Biorhythm Multi-Track Waveform Canvas (Physical, Emotional, Intellectual, Intuitive)
3. Kabbalistic Tree of Life (10 Sephirot & 22 Paths)
"""

from __future__ import annotations

import math
import datetime
import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient

import pyqtgraph as pg

from cockpit.src.theme.tokens import (
    FONT_MONO, FONT_HEADING, FONT_BODY,
    RADIUS_DEFAULT, RADIUS_MD, SPACING_SM, SPACING_MD
)

logger = logging.getLogger(__name__)


# =============================================================================
# 1. Celestial Ephemeris & Lunar Phase Dial
# =============================================================================

class CelestialEphemerisWidget(QWidget):
    """
    Renders high-DPI Vector Celestial Zodiac Wheel showing planetary positions,
    lunar phase illumination, and astrological aspects for the target draw date.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        self._draw_date = datetime.date.today()
        self._planets = {
            "Sun": {"symbol": "☉", "angle": 45.0, "color": "#f59e0b"},
            "Moon": {"symbol": "☽", "angle": 120.0, "color": "#00f0ff"},
            "Mercury": {"symbol": "☿", "angle": 60.0, "color": "#10b981"},
            "Venus": {"symbol": "♀", "angle": 95.0, "color": "#ec4899"},
            "Mars": {"symbol": "♂", "angle": 210.0, "color": "#ef4444"},
            "Jupiter": {"symbol": "♃", "angle": 290.0, "color": "#8b5cf6"},
            "Saturn": {"symbol": "♄", "angle": 335.0, "color": "#eab308"},
        }
        self._moon_phase_name = "Waxing Gibbous"
        self._lunar_illumination = 0.78

    def set_draw_date(self, target_date: datetime.date) -> None:
        self._draw_date = target_date
        # Approximate planetary angles based on day of year
        doy = target_date.timetuple().tm_yday
        self._planets["Sun"]["angle"] = (doy * 0.9856) % 360
        self._planets["Moon"]["angle"] = (doy * 13.176) % 360
        self._planets["Mercury"]["angle"] = (doy * 4.09) % 360
        self._planets["Venus"]["angle"] = (doy * 1.60) % 360
        self._planets["Mars"]["angle"] = (doy * 0.524) % 360
        self._planets["Jupiter"]["angle"] = (doy * 0.083) % 360
        self._planets["Saturn"]["angle"] = (doy * 0.033) % 360

        # Lunar phase approximation
        diff = (self._planets["Moon"]["angle"] - self._planets["Sun"]["angle"]) % 360
        self._lunar_illumination = round((1 - math.cos(math.radians(diff))) / 2.0, 2)
        if diff < 45 or diff >= 315:
            self._moon_phase_name = "New Moon"
        elif diff < 135:
            self._moon_phase_name = "First Quarter / Waxing"
        elif diff < 225:
            self._moon_phase_name = "Full Moon"
        else:
            self._moon_phase_name = "Last Quarter / Waning"

        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        radius = min(cx, cy) * 0.85

        # Background radial glow
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0.0, QColor("#121824"))
        grad.setColorAt(0.85, QColor("#0d121c"))
        grad.setColorAt(1.0, QColor("#0a0d14"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#20293d"), 1.5))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Inner Zodiac Rings
        painter.setPen(QPen(QColor("#1e293b"), 1, Qt.DashLine))
        painter.drawEllipse(QPointF(cx, cy), radius * 0.65, radius * 0.65)
        painter.drawEllipse(QPointF(cx, cy), radius * 0.35, radius * 0.35)

        # 12 Zodiac Houses Dividers
        painter.setPen(QPen(QColor("#1e293b"), 1))
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            x1 = cx + (radius * 0.65) * math.cos(rad)
            y1 = cy + (radius * 0.65) * math.sin(rad)
            x2 = cx + radius * math.cos(rad)
            y2 = cy + radius * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Plot Planets
        font = QFont(FONT_MONO, 11, QFont.Bold)
        painter.setFont(font)

        for name, data in self._planets.items():
            rad = math.radians(data["angle"])
            r_dist = radius * 0.80
            px = cx + r_dist * math.cos(rad)
            py = cy + r_dist * math.sin(rad)

            # Planet dot
            color = QColor(data["color"])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.lighter(130), 1.5))
            painter.drawEllipse(QPointF(px, py), 6, 6)

            # Planet Symbol Label
            painter.setPen(QPen(QColor("#f1f5f9")))
            painter.drawText(QRectF(px - 10, py - 18, 20, 14), Qt.AlignCenter, data["symbol"])

        # Center Lunar Badge
        painter.setBrush(QBrush(QColor("#161e2e")))
        painter.setPen(QPen(QColor("#00f0ff"), 1.5))
        painter.drawEllipse(QPointF(cx, cy), 22, 22)

        painter.setPen(QPen(QColor("#00f0ff")))
        painter.setFont(QFont(FONT_MONO, 8, QFont.Bold))
        painter.drawText(QRectF(cx - 20, cy - 8, 40, 16), Qt.AlignCenter, f"{int(self._lunar_illumination * 100)}%")


# =============================================================================
# 2. Biorhythm Multi-Track Waveform Canvas (PyQtGraph)
# =============================================================================

class BiorhythmChartWidget(QWidget):
    """
    Renders 4 canonical sinusoidal biorhythm waves over a 30-day forecast window:
    - Physical (23-day cycle, Red)
    - Emotional (28-day cycle, Blue/Cyan)
    - Intellectual (33-day cycle, Green)
    - Intuitive (38-day cycle, Purple)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # PyQtGraph Plot Widget
        self.plot_widget = pg.PlotWidget(self)
        self.plot_widget.setBackground("#0a0d14")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.25)
        self.plot_widget.setYRange(-1.15, 1.15)
        self.plot_widget.getAxis("left").setTextPen("#8b9bb4")
        self.plot_widget.getAxis("bottom").setTextPen("#8b9bb4")

        # Zero reference line
        zero_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen("#20293d", width=1.5, style=Qt.DashLine))
        self.plot_widget.addItem(zero_line)

        # Draw date indicator
        self.draw_line = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen("#00f0ff", width=2, style=Qt.SolidLine))
        self.plot_widget.addItem(self.draw_line)

        layout.addWidget(self.plot_widget)
        self.plot_biorhythms(days_offset=0)

    def plot_biorhythms(self, days_offset: int = 0) -> None:
        """Plots biorhythm curves across [-15, +15] days around target draw date."""
        self.plot_widget.clear()
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen("#20293d", width=1.5, style=Qt.DashLine)))
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen("#00f0ff", width=2, style=Qt.SolidLine)))

        x = np.linspace(-15, 15, 200)

        # Biorhythm Formulas
        y_phys = np.sin(2 * np.pi * (x + days_offset) / 23.0)
        y_emot = np.sin(2 * np.pi * (x + days_offset) / 28.0)
        y_intel = np.sin(2 * np.pi * (x + days_offset) / 33.0)
        y_intuit = np.sin(2 * np.pi * (x + days_offset) / 38.0)

        # Plot Curves
        self.plot_widget.plot(x, y_phys, pen=pg.mkPen("#ef4444", width=2.0), name="Physical (23d)")
        self.plot_widget.plot(x, y_emot, pen=pg.mkPen("#00f0ff", width=2.0), name="Emotional (28d)")
        self.plot_widget.plot(x, y_intel, pen=pg.mkPen("#10b981", width=2.0), name="Intellectual (33d)")
        self.plot_widget.plot(x, y_intuit, pen=pg.mkPen("#a855f7", width=2.0), name="Intuitive (38d)")


# =============================================================================
# 3. Kabbalistic Tree of Life (10 Sephirot & Gematria Reductions)
# =============================================================================

class KabbalahTreeWidget(QWidget):
    """
    Renders the 10 Sephirot nodes (Keter to Malkuth) connected by mystical paths,
    mapping active lottery pool numbers to divine emanations and digital roots.
    """

    SEPHIROT = [
        {"id": 1, "name": "Keter", "label": "Crown", "x": 0.5, "y": 0.08, "color": "#f1f5f9"},
        {"id": 2, "name": "Chokhmah", "label": "Wisdom", "x": 0.8, "y": 0.22, "color": "#00f0ff"},
        {"id": 3, "name": "Binah", "label": "Understanding", "x": 0.2, "y": 0.22, "color": "#3b82f6"},
        {"id": 4, "name": "Chesed", "label": "Mercy", "x": 0.8, "y": 0.42, "color": "#a855f7"},
        {"id": 5, "name": "Gevurah", "label": "Strength", "x": 0.2, "y": 0.42, "color": "#ef4444"},
        {"id": 6, "name": "Tiferet", "label": "Beauty", "x": 0.5, "y": 0.52, "color": "#f59e0b"},
        {"id": 7, "name": "Netzach", "label": "Victory", "x": 0.8, "y": 0.70, "color": "#10b981"},
        {"id": 8, "name": "Hod", "label": "Splendor", "x": 0.2, "y": 0.70, "color": "#f97316"},
        {"id": 9, "name": "Yesod", "label": "Foundation", "x": 0.5, "y": 0.82, "color": "#6366f1"},
        {"id": 10, "name": "Malkuth", "label": "Kingdom", "x": 0.5, "y": 0.94, "color": "#8b5cf6"},
    ]

    PATHS = [
        (1, 2), (1, 3), (1, 6),
        (2, 3), (2, 6), (2, 4),
        (3, 6), (3, 5),
        (4, 5), (4, 6), (4, 7),
        (5, 6), (5, 8),
        (6, 7), (6, 8), (6, 9),
        (7, 8), (7, 9), (7, 10),
        (8, 9), (8, 10),
        (9, 10)
    ]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(220, 260)
        self._highlighted_nodes: Set[int] = {1, 3, 6, 9}

    def set_active_numbers(self, numbers: List[int]) -> None:
        """Calculates digital roots of participating balls and highlights Sephirot."""
        if not numbers:
            return
        roots = set(1 + (n - 1) % 9 for n in numbers)
        if any(n % 10 == 0 for n in numbers):
            roots.add(10)
        self._highlighted_nodes = roots
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        pos_map = {}
        for s in self.SEPHIROT:
            pos_map[s["id"]] = QPointF(s["x"] * w, s["y"] * h)

        # Draw 22 Connecting Paths
        painter.setPen(QPen(QColor("#20293d"), 1.5))
        for p1, p2 in self.PATHS:
            painter.drawLine(pos_map[p1], pos_map[p2])

        # Draw Sephirot Nodes
        for s in self.SEPHIROT:
            sid = s["id"]
            pt = pos_map[sid]
            is_active = sid in self._highlighted_nodes

            color = QColor(s["color"])
            if is_active:
                # Glowing outer halo
                painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 60)))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(pt, 16, 16)

                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor("#ffffff"), 2))
                painter.drawEllipse(pt, 10, 10)
            else:
                painter.setBrush(QBrush(QColor("#101522")))
                painter.setPen(QPen(QColor("#20293d"), 1.5))
                painter.drawEllipse(pt, 8, 8)

            # Node label text
            painter.setPen(QPen(QColor("#8b9bb4")))
            painter.setFont(QFont(FONT_MONO, 7, QFont.Bold))
            painter.drawText(QRectF(pt.x() - 40, pt.y() + 10, 80, 12), Qt.AlignCenter, s["name"])
