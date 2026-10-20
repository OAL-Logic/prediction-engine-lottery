"""
Matplotlib Econometric & Distribution Canvas
============================================
Secondary visualization engine utilizing `FigureCanvasQTAgg` for:
1. Walk-forward backtest ROI equity curves
2. Prize tier match probability distributions
3. High-resolution econometric charts
"""

from __future__ import annotations

import logging
from typing import List, Dict, Optional, Any
import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class EconometricDistributionCanvas(QWidget):
    """
    Publication-grade Matplotlib canvas for econometric lottery distributions.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Initialize Matplotlib Figure with dark trading terminal palette
        self.figure = Figure(figsize=(5, 3), facecolor='#0a0c10')
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self._style_axes()

    def _style_axes(self) -> None:
        self.ax.set_facecolor('#12161f')
        self.ax.tick_params(colors='#8692a6', labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color('#232938')
        self.ax.grid(True, color='#232938', linestyle='--', alpha=0.5)

    def plot_prize_distribution(self, match_counts: Dict[str, int]) -> None:
        """Renders prize tier match bar chart."""
        self.ax.clear()
        self._style_axes()

        if not match_counts:
            self.canvas.draw()
            return

        categories = list(match_counts.keys())
        values = list(match_counts.values())

        bars = self.ax.bar(categories, values, color='#00f0ff', edgecolor='#00ff66', alpha=0.85)
        self.ax.set_title("PRIZE TIER MATCH DISTRIBUTION", color='#f3f6fa', fontsize=10, fontweight='bold', fontname='DejaVu Sans')
        self.ax.set_ylabel("Occurrences", color='#8692a6', fontsize=9)

        # Annotate bar values
        for bar in bars:
            height = bar.get_height()
            self.ax.annotate(
                f'{height}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                color='#00ff66', fontsize=8, fontweight='bold'
            )

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_equity_curve(self, returns_pct: List[float]) -> None:
        """Renders cumulative simulated ROI equity trajectory."""
        self.ax.clear()
        self._style_axes()

        if not returns_pct:
            self.canvas.draw()
            return

        x = np.arange(len(returns_pct))
        y = np.cumsum(returns_pct)

        self.ax.plot(x, y, color='#00ff66', linewidth=2, label="Cumulative ROI %")
        self.ax.axhline(0, color='#ff3355', linestyle=':', linewidth=1)
        self.ax.set_title("WALK-FORWARD ROI EQUITY TRAJECTORY", color='#f3f6fa', fontsize=10, fontweight='bold')
        self.ax.set_xlabel("Draw Index", color='#8692a6', fontsize=9)
        self.ax.set_ylabel("Net ROI %", color='#8692a6', fontsize=9)

        self.figure.tight_layout()
        self.canvas.draw()
