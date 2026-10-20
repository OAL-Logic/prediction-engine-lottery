"""
Batch Condition Backtest & Optimizer Dialog
===========================================
Interactive diagnostic modal evaluating candidate filter configurations
against historical official drawings to identify choke points and optimize recall.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGroupBox,
    QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from cockpit.src.core.models import FilterNode, ToleranceRule, GameSchema
from cockpit.src.services.condition_optimizer import ConditionOptimizer, BacktestReport
from cockpit.src.theme.manager import ThemeManager
from cockpit.src.theme.tokens import (
    SPACING_SM, SPACING_MD, SPACING_LG, RADIUS_DEFAULT,
    FONT_MONO, FONT_HEADING, FONT_BODY
)

logger = logging.getLogger(__name__)


class BacktestOptimizerDialog(QDialog):
    """
    Diagnostic modal displaying historical recall, combinatorial reduction,
    and filter choke points with one-click relaxation.
    """

    filters_optimized = Signal(list)  # Emits relaxed List[FilterNode]

    def __init__(
        self,
        game: GameSchema,
        filters: List[FilterNode],
        tolerance: ToleranceRule,
        parent: Optional[QDialog] = None
    ):
        super().__init__(parent)
        self.game = game
        self.filters = filters
        self.tolerance = tolerance
        self.optimizer = ConditionOptimizer()
        self.report: Optional[BacktestReport] = None

        self.setWindowTitle(f"Batch Condition Optimizer — {game.name}")
        self.setMinimumSize(850, 580)
        self.setModal(True)

        self.setStyleSheet(ThemeManager().generate_stylesheet())
        self._init_ui()
        self._run_backtest(draws_count=50)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_MD)

        # Header with draw limit selector
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Historical Condition Validation — {self.game.name}")
        title_label.setStyleSheet(f"font-family: '{FONT_HEADING}'; font-size: 16px; font-weight: 700; color: #00f0ff;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        header_layout.addWidget(QLabel("Sample Horizon:"))
        self.combo_draws = QComboBox()
        self.combo_draws.addItems(["Last 30 Draws", "Last 50 Draws", "Last 100 Draws"])
        self.combo_draws.setCurrentIndex(1)
        self.combo_draws.currentIndexChanged.connect(self._on_draws_changed)
        header_layout.addWidget(self.combo_draws)

        layout.addLayout(header_layout)

        # KPI Dashboard Cards
        kpi_frame = QFrame()
        kpi_layout = QHBoxLayout(kpi_frame)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(SPACING_MD)

        self.card_hit_rate = self._create_kpi_card("HISTORICAL HIT RATE", "0.0%", "Winning draws surviving criteria", "#10b981")
        self.card_reduction = self._create_kpi_card("EST. POOL REDUCTION", "0.0%", "Theoretical combinations pruned", "#00f0ff")
        self.card_efficiency = self._create_kpi_card("EFFICIENCY INDEX", "0.00", "Recall × Reduction Tradeoff", "#a855f7")
        self.card_verdict = self._create_kpi_card("OPTIMIZATION VERDICT", "TESTING", "Configuration Profile Status", "#f59e0b")

        kpi_layout.addWidget(self.card_hit_rate)
        kpi_layout.addWidget(self.card_reduction)
        kpi_layout.addWidget(self.card_efficiency)
        kpi_layout.addWidget(self.card_verdict)
        layout.addWidget(kpi_frame)

        # Choke Points Table
        choke_group = QGroupBox("IDENTIFIED CHOKE POINTS (FILTERS ELIMINATING OFFICIAL WINNERS)")
        choke_layout = QVBoxLayout(choke_group)
        choke_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)

        self.table_choke = QTableWidget()
        self.table_choke.setColumnCount(5)
        self.table_choke.setHorizontalHeaderLabels([
            "Filter Name", "Rejections", "Rejection %", "Configured Bounds", "Observed Bounds"
        ])
        header = self.table_choke.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.table_choke.setColumnWidth(1, 100)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_choke.setColumnWidth(2, 110)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_choke.setColumnWidth(3, 150)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_choke.setColumnWidth(4, 150)
        self.table_choke.verticalHeader().setVisible(False)
        self.table_choke.setAlternatingRowColors(True)

        choke_layout.addWidget(self.table_choke)
        layout.addWidget(choke_group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING_SM)

        self.btn_auto_relax = QPushButton("⚡ Auto-Relax Choke Points (Target 85% Recall)")
        self.btn_auto_relax.setObjectName("btn_primary")
        self.btn_auto_relax.setCursor(Qt.PointingHandCursor)
        self.btn_auto_relax.clicked.connect(self._auto_relax_choke_points)

        btn_retest = QPushButton("🔄 Re-Test")
        btn_retest.setCursor(Qt.PointingHandCursor)
        btn_retest.clicked.connect(lambda: self._run_backtest(self._get_selected_draws()))

        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_auto_relax, stretch=2)
        btn_layout.addWidget(btn_retest, stretch=1)
        btn_layout.addWidget(btn_close, stretch=1)
        layout.addLayout(btn_layout)

    def _create_kpi_card(self, title: str, value: str, subtext: str, color_hex: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: {RADIUS_DEFAULT}px;
                padding: 10px;
            }}
        """)
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(6, 6, 6, 6)
        vbox.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 10px; font-weight: 700; color: #8b9bb4;")
        vbox.addWidget(lbl_title)

        lbl_val = QLabel(value)
        lbl_val.setObjectName("card_val")
        lbl_val.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 15px; font-weight: 900; color: {color_hex};")
        vbox.addWidget(lbl_val)

        lbl_sub = QLabel(subtext)
        lbl_sub.setStyleSheet(f"font-size: 10px; color: #64748b;")
        vbox.addWidget(lbl_sub)

        return card

    def _get_selected_draws(self) -> int:
        idx = self.combo_draws.currentIndex()
        return 30 if idx == 0 else (50 if idx == 1 else 100)

    def _on_draws_changed(self) -> None:
        self._run_backtest(self._get_selected_draws())

    def _run_backtest(self, draws_count: int) -> None:
        self.report = self.optimizer.run_historical_backtest(
            game_id=self.game.id,
            filters=self.filters,
            tolerance=self.tolerance,
            draws_limit=draws_count
        )

        # Update KPI Cards
        lbl_hit = self.card_hit_rate.findChild(QLabel, "card_val")
        if lbl_hit:
            lbl_hit.setText(f"{self.report.historical_hit_rate_pct:.1f}%")

        lbl_red = self.card_reduction.findChild(QLabel, "card_val")
        if lbl_red:
            lbl_red.setText(f"{self.report.estimated_reduction_rate_pct:.1f}%")

        lbl_eff = self.card_efficiency.findChild(QLabel, "card_val")
        if lbl_eff:
            lbl_eff.setText(f"{self.report.efficiency_index:.2f}")

        lbl_verd = self.card_verdict.findChild(QLabel, "card_val")
        if lbl_verd:
            lbl_verd.setText(self.report.verdict)

        # Populate Choke Points Table
        self.table_choke.clearContents()
        self.table_choke.setRowCount(len(self.report.choke_points))

        fitted = self.optimizer.bridge.compute_auto_fit_ranges(
            self.game.id, self.filters, last_n_draws=draws_count
        )

        for row, cp in enumerate(self.report.choke_points):
            item_name = QTableWidgetItem(cp.filter_name)
            item_name.setFlags(item_name.flags() ^ Qt.ItemIsEditable)
            self.table_choke.setItem(row, 0, item_name)

            item_count = QTableWidgetItem(f"{cp.rejection_count} / {self.report.total_draws_evaluated}")
            item_count.setTextAlignment(Qt.AlignCenter)
            item_count.setFlags(item_count.flags() ^ Qt.ItemIsEditable)
            self.table_choke.setItem(row, 1, item_count)

            item_rate = QTableWidgetItem(f"{cp.rejection_rate_pct:.1f}%")
            item_rate.setTextAlignment(Qt.AlignCenter)
            item_rate.setFlags(item_rate.flags() ^ Qt.ItemIsEditable)
            item_rate.setForeground(QColor("#ef4444"))
            self.table_choke.setItem(row, 2, item_rate)

            item_cfg = QTableWidgetItem(f"[{cp.configured_min:g} – {cp.configured_max:g}]")
            item_cfg.setTextAlignment(Qt.AlignCenter)
            item_cfg.setFlags(item_cfg.flags() ^ Qt.ItemIsEditable)
            self.table_choke.setItem(row, 3, item_cfg)

            obs_bounds = fitted.get(cp.filter_id, (cp.configured_min, cp.configured_max))
            item_obs = QTableWidgetItem(f"[{obs_bounds[0]:g} – {obs_bounds[1]:g}]")
            item_obs.setTextAlignment(Qt.AlignCenter)
            item_obs.setFlags(item_obs.flags() ^ Qt.ItemIsEditable)
            item_obs.setForeground(QColor("#00f0ff"))
            self.table_choke.setItem(row, 4, item_obs)

    def _auto_relax_choke_points(self) -> None:
        if not self.report or not self.report.choke_points:
            QMessageBox.information(self, "Optimizer Status", "No choke points detected in the current profile.")
            return

        relaxed_filters, new_report = self.optimizer.auto_optimize_choke_points(
            game_id=self.game.id,
            filters=self.filters,
            tolerance=self.tolerance,
            target_hit_rate=85.0
        )

        self.filters = relaxed_filters
        self.report = new_report
        self.filters_optimized.emit(self.filters)
        self._run_backtest(self._get_selected_draws())

        QMessageBox.information(
            self,
            "Optimization Complete",
            f"Choke points successfully relaxed.\n\n"
            f"Historical Hit Rate: {new_report.historical_hit_rate_pct:.1f}%\n"
            f"Estimated Reduction: {new_report.estimated_reduction_rate_pct:.1f}%\n"
            f"Efficiency Index: {new_report.efficiency_index:.2f}"
        )
