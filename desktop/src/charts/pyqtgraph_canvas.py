"""
PyQtGraph Real-Time Analytical Canvas
=====================================
Primary GPU/Qt-accelerated visualization engine for:
1. Actual Skips & Gap Sequences
2. Gap Histogram Distributions
3. Winning Rate Graph (WRG)
"""

from __future__ import annotations

import logging
from typing import List, Optional, Dict
import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QFont
import pyqtgraph as pg

logger = logging.getLogger(__name__)

# Configure pyqtgraph global defaults for dark trading aesthetic
pg.setConfigOption('background', '#0a0c10')
pg.setConfigOption('foreground', '#8692a6')
pg.setConfigOption('antialias', True)


class SkipsAnalyticsCanvas(QWidget):
    """Real-time PyQtGraph plot for Actual Skips sequences and Now-Skip status."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget(title="ACTUAL SKIPS TRAJECTORY (Lottery Studio SIGNATURE)")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', "Draw Sequence (Historical Miss Events)")
        self.plot_widget.setLabel('left', "Skip Gap Length (Draws)")

        # Curves & Items
        self.skip_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#00f0ff', width=2),
            symbol='o',
            symbolSize=6,
            symbolBrush=pg.mkBrush('#00ff66'),
            name="Actual Skips"
        )
        self.avg_line = pg.InfiniteLine(
            angle=0,
            pen=pg.mkPen(color='#ffb700', width=1.5, style=pg.QtCore.Qt.DashLine),
            label="Avg Skip: {value:.1f}",
            labelOpts={'color': '#ffb700', 'position': 0.85}
        )
        self.plot_widget.addItem(self.avg_line)

        layout.addWidget(self.plot_widget)

    def update_skips(self, skips: List[int], now_skip: int = 0) -> None:
        """Updates the skips trajectory plot."""
        if not skips:
            self.skip_curve.clear()
            return

        x = np.arange(len(skips))
        y = np.array(skips)
        self.skip_curve.setData(x, y)

        avg = float(np.mean(y)) if len(y) > 0 else 0.0
        self.avg_line.setValue(avg)


class GapHistogramCanvas(QWidget):
    """PyQtGraph bar chart displaying the frequency distribution of gap intervals."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget(title="GAP DISTRIBUTION HISTOGRAM")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', "Gap Size")
        self.plot_widget.setLabel('left', "Occurrence Frequency")

        self.bar_item = None
        layout.addWidget(self.plot_widget)

    def update_histogram(self, gaps: List[int]) -> None:
        if not gaps:
            return
        if self.bar_item:
            self.plot_widget.removeItem(self.bar_item)

        hist, bin_edges = np.histogram(gaps, bins=min(15, max(3, len(set(gaps)))))
        x = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        width = (bin_edges[1] - bin_edges[0]) * 0.8

        self.bar_item = pg.BarGraphItem(
            x=x, height=hist, width=width,
            brush=pg.mkBrush('#00f0ff'),
            pen=pg.mkPen('#00ff66', width=1)
        )
        self.plot_widget.addItem(self.bar_item)


class WinningRateGraphCanvas(QWidget):
    """Winning Rate Graph (WRG) tracking cumulative performance and draw hit ratios."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget(title="WINNING RATE GRAPH (WRG)")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', "Draws Evaluated")
        self.plot_widget.setLabel('left', "Cumulative Hit Rate %")

        self.curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#00ff66', width=2),
            name="Hit Rate"
        )
        layout.addWidget(self.plot_widget)

    def update_wrg(self, hit_rates: List[float]) -> None:
        if not hit_rates:
            self.curve.clear()
            return
        x = np.arange(len(hit_rates))
        self.curve.setData(x, np.array(hit_rates))
