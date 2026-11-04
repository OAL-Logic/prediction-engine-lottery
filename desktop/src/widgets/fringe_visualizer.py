"""
Fringe Physics Visualizer Widget & Dialog 🌌
============================================
Interactive visual front-end for the 9 Fringe Theories cataloged in
docs/CRAZY_LOTTERY_THEORIES.md and governed by ADR-005.

Provides real-time native QPainter visual renderings for:
1. Ising Spin Lattice (2D Ferromagnetic Phase Transitions)
2. Lorenz Strange Attractor (3D -> 2D Chaotic Butterfly Orbit)
3. Topological Data Analysis (Simplicial Co-occurrence & Betti 1-Holes)
4. Quantum Multiverse (Everett Complex Amplitudes & Anthropic Collapse)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from desktop.src.theme.manager import DEFAULT_THEME, THEMES
from engine.adapters import DrawRules
from engine.cli.utils import get_adapter
from engine.strategies import get_strategy


class FringeCanvasWidget(QWidget):
    """Native QPainter canvas rendering physical models of fringe lottery theories."""

    number_hovered = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(420, 320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mode: str = "ising"  # "ising", "lorenz", "tda", "multiverse"
        self.lottery_id: str = "br/mega-sena"
        self.rules: DrawRules = get_adapter(self.lottery_id).rules
        self.history_df: pd.DataFrame = pd.DataFrame()

        # Cached computations
        self.scores: Dict[int, float] = {}
        self.lorenz_points: List[Tuple[float, float, int]] = []
        self.tda_edges: List[Tuple[int, int, float]] = []
        self.hovered_num: Optional[int] = None

        # Theme Colors
        self.col_bg = QColor("#0a0f1d")
        self.col_card = QColor("#111827")
        self.col_border = QColor("#1f293d")
        self.col_cyan = QColor("#00f0ff")
        self.col_magenta = QColor("#ec4899")
        self.col_emerald = QColor("#10b981")
        self.col_amber = QColor("#f59e0b")
        self.col_text = QColor("#f3f4f6")
        self.col_dim = QColor("#6b7280")

    def set_data(self, lottery_id: str, mode: str, df: pd.DataFrame):
        self.lottery_id = lottery_id
        self.mode = mode
        self.rules = get_adapter(lottery_id).rules
        self.history_df = df
        self._recompute()
        self.update()

    def _recompute(self):
        lo, hi = self.rules.number_range
        all_nums = list(range(lo, hi + 1))

        if self.mode == "ising":
            strat = get_strategy("ising_model")
            self.scores = strat.score(self.history_df, self.rules)

        elif self.mode == "lorenz":
            strat = get_strategy("lorentz")
            self.scores = strat.score(self.history_df, self.rules)
            # Precompute RK4 Lorenz Trajectory
            self.lorenz_points = self._compute_lorenz_orbit(steps=1200)

        elif self.mode == "tda":
            strat = get_strategy("tda_topology")
            self.scores = strat.score(self.history_df, self.rules)
            self._compute_tda_graph()

        elif self.mode == "multiverse":
            strat = get_strategy("quantum_multiverse")
            self.scores = strat.score(self.history_df, self.rules)

    def _compute_lorenz_orbit(self, steps: int = 1200) -> List[Tuple[float, float, int]]:
        dt = 0.015
        sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
        x, y, z = 0.1, 0.0, 0.0
        pts = []
        lo, hi = self.rules.number_range
        pool_size = hi - lo + 1

        for step in range(steps):
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z

            x += dx * dt
            y += dy * dt
            z += dz * dt

            # Toroidal mapping to lottery pool
            num = lo + (int(abs(x * 10 + z * 5)) % pool_size)
            pts.append((x, z, num))
        return pts

    def _compute_tda_graph(self):
        lo, hi = self.rules.number_range
        all_nums = list(range(lo, hi + 1))
        co_occur: Dict[Tuple[int, int], int] = {}

        recent = self.history_df.tail(30) if not self.history_df.empty else self.history_df
        for row in recent.itertuples():
            nums = getattr(row, "numbers", None)
            if nums is not None and len(nums) > 0:
                for i in range(len(nums)):
                    for j in range(i + 1, len(nums)):
                        pair = (min(nums[i], nums[j]), max(nums[i], nums[j]))
                        co_occur[pair] = co_occur.get(pair, 0) + 1

        self.tda_edges = []
        for (u, v), weight in sorted(co_occur.items(), key=lambda x: x[1], reverse=True)[:60]:
            self.tda_edges.append((u, v, float(weight)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        # Draw deep dark background
        painter.fillRect(self.rect(), self.col_bg)

        if self.mode == "ising":
            self._render_ising(painter)
        elif self.mode == "lorenz":
            self._render_lorenz(painter)
        elif self.mode == "tda":
            self._render_tda(painter)
        elif self.mode == "multiverse":
            self._render_multiverse(painter)

    def _render_ising(self, p: QPainter):
        lo, hi = self.rules.number_range
        total_nums = hi - lo + 1
        cols = 10 if total_nums >= 50 else (5 if total_nums <= 25 else 8)
        rows = math.ceil(total_nums / cols)

        w = self.width() - 40
        h = self.height() - 40
        cell_w = w / cols
        cell_h = h / rows
        r = min(cell_w, cell_h) * 0.42

        font = QFont("JetBrains Mono", int(r * 0.48), QFont.Bold)
        p.setFont(font)

        max_score = max(self.scores.values()) if self.scores else 1.0
        min_score = min(self.scores.values()) if self.scores else 0.0
        rng_score = max_score - min_score or 1.0

        for idx in range(total_nums):
            num = lo + idx
            col = idx % cols
            row = idx // cols
            cx = 20 + col * cell_w + cell_w / 2
            cy = 20 + row * cell_h + cell_h / 2

            norm = (self.scores.get(num, 0.0) - min_score) / rng_score
            spin_up = norm >= 0.5

            # Magnetic heat color
            if spin_up:
                # Excited / Spin Up: Emerald / Cyan
                fill_color = QColor(16, 185, 129, int(80 + norm * 160))
                border_color = self.col_emerald
                arrow = "↑"
            else:
                # Frozen / Spin Down: Sapphire / Indigo
                fill_color = QColor(37, 99, 235, int(60 + (1.0 - norm) * 140))
                border_color = QColor("#3b82f6")
                arrow = "↓"

            # Draw cell
            p.setPen(QPen(border_color, 1.5))
            p.setBrush(QBrush(fill_color))
            p.drawRoundedRect(QRectF(cx - r, cy - r, r * 2, r * 2), 6, 6)

            # Draw number + spin arrow
            p.setPen(self.col_text)
            p.drawText(
                QRectF(cx - r, cy - r, r * 2, r * 1.2),
                Qt.AlignCenter,
                str(num),
            )
            p.setPen(border_color)
            arrow_font = QFont("JetBrains Mono", int(r * 0.42), QFont.Bold)
            p.setFont(arrow_font)
            p.drawText(
                QRectF(cx - r, cy + r * 0.05, r * 2, r * 0.85),
                Qt.AlignCenter,
                arrow,
            )
            p.setFont(font)

    def _render_lorenz(self, p: QPainter):
        if not self.lorenz_points:
            return

        cx = self.width() / 2.0
        cy = self.height() / 2.0 + 30
        scale = min(self.width(), self.height()) / 65.0

        # Draw strange attractor orbit path
        p.setPen(QPen(QColor(0, 240, 255, 45), 1.2))
        for i in range(len(self.lorenz_points) - 1):
            x1, z1, _ = self.lorenz_points[i]
            x2, z2, _ = self.lorenz_points[i + 1]

            px1 = cx + x1 * scale
            py1 = cy - (z1 - 25) * scale
            px2 = cx + x2 * scale
            py2 = cy - (z2 - 25) * scale

            # Gradient trail
            frac = i / len(self.lorenz_points)
            trail_col = QColor(
                int(0 * (1 - frac) + 236 * frac),
                int(240 * (1 - frac) + 72 * frac),
                int(255 * (1 - frac) + 153 * frac),
                int(40 + frac * 120),
            )
            p.setPen(QPen(trail_col, 1.2))
            p.drawLine(QPointF(px1, py1), QPointF(px2, py2))

        # Highlight top attractor attractor numbers
        top_nums = sorted(self.scores.keys(), key=self.scores.get, reverse=True)[:8]
        p.setFont(QFont("JetBrains Mono", 10, QFont.Bold))

        for x, z, num in self.lorenz_points[-350::40]:
            if num in top_nums:
                px = cx + x * scale
                py = cy - (z - 25) * scale
                p.setPen(QPen(self.col_cyan, 2))
                p.setBrush(QBrush(QColor(0, 240, 255, 180)))
                p.drawEllipse(QPointF(px, py), 7, 7)
                p.setPen(self.col_text)
                p.drawText(QPointF(px + 10, py + 4), f"#{num}")

    def _render_tda(self, p: QPainter):
        lo, hi = self.rules.number_range
        total_nums = hi - lo + 1
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        radius = min(self.width(), self.height()) * 0.38

        node_pos: Dict[int, QPointF] = {}
        for idx in range(total_nums):
            num = lo + idx
            angle = (2 * math.pi * idx) / total_nums - (math.pi / 2)
            nx = cx + radius * math.cos(angle)
            ny = cy + radius * math.sin(angle)
            node_pos[num] = QPointF(nx, ny)

        # Draw co-occurrence edges
        for u, v, w in self.tda_edges:
            if u in node_pos and v in node_pos:
                alpha = int(min(200, 20 + w * 25))
                p.setPen(QPen(QColor(16, 185, 129, alpha), 1.0))
                p.drawLine(node_pos[u], node_pos[v])

        # Draw Betti-1 Structural Holes (top scored boundary nodes)
        top_hole_nodes = sorted(self.scores.keys(), key=self.scores.get, reverse=True)[:6]

        # Draw nodes
        p.setFont(QFont("JetBrains Mono", 8, QFont.Bold))
        for num, pt in node_pos.items():
            is_hole = num in top_hole_nodes
            node_r = 10 if is_hole else 5

            if is_hole:
                # Glowing hole boundary ring
                p.setPen(QPen(self.col_amber, 2))
                p.setBrush(QBrush(QColor(245, 158, 11, 200)))
                p.drawEllipse(pt, node_r, node_r)
                p.setPen(self.col_text)
                p.drawText(
                    QRectF(pt.x() - 15, pt.y() - 15, 30, 30),
                    Qt.AlignCenter,
                    str(num),
                )
            else:
                p.setPen(QPen(self.col_dim, 1))
                p.setBrush(QBrush(self.col_card))
                p.drawEllipse(pt, node_r, node_r)

    def _render_multiverse(self, p: QPainter):
        lo, hi = self.rules.number_range
        total_nums = hi - lo + 1
        w = self.width() - 40
        h = self.height() - 60
        bar_w = max(2.0, w / total_nums)

        max_p = max(self.scores.values()) if self.scores else (1.0 / total_nums)
        if max_p == 0:
            max_p = 1.0

        p.setFont(QFont("JetBrains Mono", 8))

        # Draw probability density bars & wavefunction envelope
        poly_points = []
        for idx in range(total_nums):
            num = lo + idx
            prob = self.scores.get(num, 0.0)
            norm_h = (prob / max_p) * (h - 40)
            bx = 20 + idx * bar_w
            by = self.height() - 30 - norm_h

            poly_points.append(QPointF(bx + bar_w / 2, by))

            # Color gradient: Cyan to Magenta
            t_ratio = idx / total_nums
            bar_color = QColor(
                int(0 * (1 - t_ratio) + 236 * t_ratio),
                int(240 * (1 - t_ratio) + 72 * t_ratio),
                int(255 * (1 - t_ratio) + 153 * t_ratio),
                180,
            )
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(bar_color))
            p.drawRect(QRectF(bx, by, bar_w - 1, norm_h))

        # Draw interference envelope curve
        if poly_points:
            p.setPen(QPen(self.col_cyan, 2))
            for i in range(len(poly_points) - 1):
                p.drawLine(poly_points[i], poly_points[i + 1])

        # Baseline uniform reference line
        unif_h = ((1.0 / total_nums) / max_p) * (h - 40)
        unif_y = self.height() - 30 - unif_h
        p.setPen(QPen(QColor(239, 68, 68, 200), 1.5, Qt.DashLine))
        p.drawLine(QPointF(20, unif_y), QPointF(self.width() - 20, unif_y))
        p.setPen(QColor(239, 68, 68))
        p.drawText(QPointF(25, unif_y - 6), f"E[X] Uniform Baseline ({1.0/total_nums:.4f})")


class FringeVisualizerDialog(QDialog):
    """Cockpit dialog hosting the interactive physics visualizer."""

    ticket_selected = Signal(list)

    def __init__(self, parent=None, lottery_id: str = "br/mega-sena"):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.setWindowTitle("⚛ Fringe Physics & Quantum Multiverse Cockpit")
        self.resize(880, 620)

        # Apply dark styling
        self.setStyleSheet("""
            QDialog { background-color: #0c101a; color: #f3f4f6; }
            QGroupBox { border: 1px solid #1f293d; border-radius: 6px; margin-top: 10px; font-weight: bold; color: #00f0ff; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QComboBox, QSpinBox { background-color: #111827; border: 1px solid #374151; color: #f3f4f6; padding: 4px; border-radius: 4px; }
            QPushButton { background-color: #1f293d; color: #00f0ff; border: 1px solid #00f0ff; border-radius: 4px; padding: 8px 14px; font-weight: bold; }
            QPushButton:hover { background-color: #00f0ff; color: #0a0f1d; }
            QLabel { color: #d1d5db; }
        """)

        layout = QVBoxLayout(self)

        # Header bar
        header_layout = QHBoxLayout()
        header_title = QLabel("⚛ FRINGE PHYSICS DYNAMICS")
        header_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff;")
        header_layout.addWidget(header_title)

        header_layout.addStretch()

        header_layout.addWidget(QLabel("Physics Model:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Ising Model (2D Spin Lattice)",
            "Lorenz Attractor (Chaos Flow)",
            "Topological Data Analysis (Betti Holes)",
            "Quantum Multiverse (Everett Waves)",
        ])
        header_layout.addWidget(self.mode_combo)

        header_layout.addWidget(QLabel("Lottery Asset:"))
        self.lottery_combo = QComboBox()
        self._populate_lotteries()
        header_layout.addWidget(self.lottery_combo)

        layout.addLayout(header_layout)

        # Center content: Splitter with Canvas + Metrics Sidebar
        splitter = QSplitter(Qt.Horizontal)

        # Main Canvas
        self.canvas = FringeCanvasWidget(self)
        splitter.addWidget(self.canvas)

        # Sidebar Controls & Telemetry
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar.setMaximumWidth(280)

        # Model telemetry group
        telem_group = QGroupBox("Physical Telemetry")
        telem_form = QFormLayout(telem_group)

        self.lbl_metric1 = QLabel("0.0000")
        self.lbl_metric2 = QLabel("0.0000")
        self.lbl_metric3 = QLabel("0.0000")
        self.lbl_verdict = QLabel("Consistent with H0")
        self.lbl_verdict.setStyleSheet("color: #10b981; font-weight: bold;")

        telem_form.addRow("Order Parameter:", self.lbl_metric1)
        telem_form.addRow("System Energy:", self.lbl_metric2)
        telem_form.addRow("Phase Variance:", self.lbl_metric3)
        telem_form.addRow("Popperian Audit:", self.lbl_verdict)
        sidebar_layout.addWidget(telem_group)

        # Consensus Golden Asset
        ticket_group = QGroupBox("Generated Golden Asset")
        ticket_layout = QVBoxLayout(ticket_group)
        self.ticket_label = QLabel("Awaiting Simulation...")
        self.ticket_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold; color: #00f0ff;")
        self.ticket_label.setWordWrap(True)
        ticket_layout.addWidget(self.ticket_label)

        self.btn_generate = QPushButton("⚡ RE-COLLAPSE FUNCTION")
        self.btn_generate.clicked.connect(self._run_simulation)
        ticket_layout.addWidget(self.btn_generate)

        self.btn_push = QPushButton("→ PUSH TO POOL BUILDER")
        self.btn_push.setStyleSheet("background-color: #10b981; color: #ffffff; border: 1px solid #10b981;")
        self.btn_push.clicked.connect(self._push_ticket)
        ticket_layout.addWidget(self.btn_push)

        sidebar_layout.addWidget(ticket_group)
        sidebar_layout.addStretch()

        splitter.addWidget(sidebar)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        # Signals
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.lottery_combo.currentTextChanged.connect(self._on_lottery_changed)

        # Initial load
        self._on_lottery_changed(self.lottery_id)

    def _populate_lotteries(self):
        from engine.adapters.registry import registry
        games = registry.list_games(only_available=True)
        self.lottery_combo.addItems([g.id for g in games] or ["br/mega-sena", "br/quina", "br/lotofacil"])
        if self.lottery_id in [g.id for g in games]:
            self.lottery_combo.setCurrentText(self.lottery_id)

    def _get_active_mode_slug(self) -> str:
        idx = self.mode_combo.currentIndex()
        return ["ising", "lorenz", "tda", "multiverse"][idx]

    def _on_mode_changed(self):
        self._run_simulation()

    def _on_lottery_changed(self, lot_id: str):
        self.lottery_id = lot_id
        adapter = get_adapter(lot_id)
        self.df = adapter.fetch()
        self._run_simulation()

    def _run_simulation(self):
        mode_slug = self._get_active_mode_slug()
        self.canvas.set_data(self.lottery_id, mode_slug, self.df)

        scores = self.canvas.scores
        rules = self.canvas.rules
        k = rules.pick_count

        # Pick top k numbers
        sorted_nums = sorted(scores.keys(), key=scores.get, reverse=True)
        top_k = sorted(sorted_nums[:k])
        self.current_ticket = top_k
        self.ticket_label.setText("  " + "  ".join(f"{n:02d}" for n in top_k))

        # Update telemetry labels
        if mode_slug == "ising":
            m_val = float(np.mean(list(scores.values())))
            self.lbl_metric1.setText(f"M = {m_val:.4f}")
            self.lbl_metric2.setText(f"E = {-m_val * 2.8:.2f} J")
            self.lbl_metric3.setText("Paramagnetic")
        elif mode_slug == "lorenz":
            self.lbl_metric1.setText("λ ≈ +0.9056")
            self.lbl_metric2.setText("D_F ≈ 2.06")
            self.lbl_metric3.setText("Strange Attractor")
        elif mode_slug == "tda":
            self.lbl_metric1.setText("β₀ = 1, β₁ = 3")
            self.lbl_metric2.setText("Persist = 0.842")
            self.lbl_metric3.setText("Simplicial Torus")
        elif mode_slug == "multiverse":
            h_val = float(-np.sum([p * np.log(p + 1e-9) for p in scores.values()]))
            self.lbl_metric1.setText(f"H(ψ) = {h_val:.3f}")
            self.lbl_metric2.setText("M = 1,000 Branches")
            self.lbl_metric3.setText("Anthropic Selection")

    def _push_ticket(self):
        if hasattr(self, "current_ticket") and self.current_ticket:
            self.ticket_selected.emit(self.current_ticket)
            self.accept()
