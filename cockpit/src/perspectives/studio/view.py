"""
Advanced Studio Mode Perspective View
=====================================
Power-user combinatorial laboratory featuring:
1. Searchable multi-column node/filter graph builder (Complete 105+ Lottery Studio catalog)
2. Fault Tolerance Engine (Error Allowance sliders & N-of-M combinatorial survival)
3. Full & Abbreviated Wheeling Studio (covering designs, Banker keys, Hamming pruning)
4. High-performance native QPainter ball matrix pool selector
5. Vectorized background streaming worker with real-time throughput metrics
6. Batch Condition Backtester & Optimizer modal
"""

from __future__ import annotations

import logging
import math
from typing import List, Dict, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QFrame, QSplitter, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QSpinBox,
    QDoubleSpinBox, QSlider, QProgressBar, QMessageBox, QScrollArea,
    QSizePolicy, QFileDialog, QTabWidget, QDialog
)
from PySide6.QtCore import Qt, Signal, QThreadPool, Slot
from PySide6.QtGui import QFont, QCursor, QColor

from cockpit.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, ToleranceMode,
    WheelingConfig, WheelType, TicketReceipt, GenerationTelemetry,
    ProfileBundle
)
from cockpit.src.theme.tokens import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_SM, RADIUS_DEFAULT, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
    FONT_MONO, FONT_HEADING, FONT_BODY
)
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.services.wheeling_solver import WheelingSolver
from cockpit.src.services.streaming_worker import StreamingCombinatorialWorker
from cockpit.src.widgets.ball_matrix import BallMatrixWidget
from cockpit.src.widgets.ticket_receipt import TicketReceiptWidget
from cockpit.src.perspectives.studio.backtest_dialog import BacktestOptimizerDialog

logger = logging.getLogger(__name__)


class StudioPerspectiveView(QWidget):
    """
    Advanced studio view coordinating the 105+ filter table, fault tolerance engine,
    and native wheeling workbench.
    """

    stream_completed = Signal(list, dict)  # Emits (survivors, summary_metrics)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.bridge = EngineBridge()
        self.active_game: Optional[GameSchema] = None
        self._all_filters: List[FilterNode] = []
        self._surviving_tickets: List[TicketReceipt] = []
        self._worker: Optional[StreamingCombinatorialWorker] = None

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        main_layout.setSpacing(SPACING_MD)

        # Top Splitter: Left Filter Table vs Right Wheeling & Tolerance Studio
        splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Rail: Searchable Multi-Column Filter Graph Builder
        # -------------------------------------------------------------
        filter_box = QGroupBox("COMBINATORIAL FILTER GRAPH (105+ Lottery Studio VECTORS)")
        filter_layout = QVBoxLayout(filter_box)
        filter_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        filter_layout.setSpacing(SPACING_SM)

        # Search Bar & Category Filter
        search_layout = QHBoxLayout()
        search_layout.setSpacing(SPACING_SM)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search filters by name, tag or metric...")
        self.search_input.textChanged.connect(self._filter_table_rows)
        search_layout.addWidget(self.search_input, stretch=2)

        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All Categories",
            "Structural / Count",
            "Sums & Averages",
            "Positional & Distance",
            "Complexity & Repeats",
            "Algebraic Residue",
            "Decades & Units",
            "Advanced & Sets"
        ])
        self.category_combo.currentTextChanged.connect(self._filter_table_rows)
        search_layout.addWidget(self.category_combo, stretch=1)
        filter_layout.addLayout(search_layout)

        # Active Filters Counter Chip
        filter_status_layout = QHBoxLayout()
        self.lbl_filter_counts = QLabel("Active Filters: 0 / 107")
        self.lbl_filter_counts.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 11px; font-weight: 700; color: #00f0ff;")
        filter_status_layout.addWidget(self.lbl_filter_counts)
        filter_status_layout.addStretch()
        filter_layout.addLayout(filter_status_layout)

        # Filter Table
        self.filter_table = QTableWidget()
        self.filter_table.setColumnCount(6)
        self.filter_table.setHorizontalHeaderLabels([
            "Active", "Category", "Filter Name", "Min Bound", "Max Bound", "Pruned"
        ])
        header = self.filter_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.filter_table.setColumnWidth(0, 54)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.filter_table.setColumnWidth(1, 160)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.filter_table.setColumnWidth(3, 95)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.filter_table.setColumnWidth(4, 95)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.filter_table.setColumnWidth(5, 75)
        self.filter_table.verticalHeader().setVisible(False)
        self.filter_table.setAlternatingRowColors(True)
        filter_layout.addWidget(self.filter_table)

        # Filter Action Buttons (2 Rows)
        actions_vbox = QVBoxLayout()
        actions_vbox.setSpacing(SPACING_XS)

        row1 = QHBoxLayout()
        row1.setSpacing(SPACING_SM)
        btn_select_all = QPushButton("Select All")
        btn_clear_all = QPushButton("Deselect All")
        btn_auto_params = QPushButton("⚡ Auto-Fit (30 Draws)")
        btn_backtest = QPushButton("🎯 Batch Backtest & Optimize")

        btn_select_all.clicked.connect(lambda: self._set_all_filter_checks(True))
        btn_clear_all.clicked.connect(lambda: self._set_all_filter_checks(False))
        btn_auto_params.clicked.connect(self._auto_fit_parameters)
        btn_backtest.clicked.connect(self._open_backtest_dialog)

        row1.addWidget(btn_select_all)
        row1.addWidget(btn_clear_all)
        row1.addWidget(btn_auto_params)
        row1.addWidget(btn_backtest)
        actions_vbox.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(SPACING_SM)
        btn_save_preset = QPushButton("💾 Save Preset (.yaml)")
        btn_load_preset = QPushButton("📂 Load Preset")
        btn_reset_defs = QPushButton("Reset Defaults")

        btn_save_preset.clicked.connect(self._export_yaml_preset)
        btn_load_preset.clicked.connect(self._import_yaml_preset)
        btn_reset_defs.clicked.connect(self._reset_defaults)

        row2.addWidget(btn_save_preset)
        row2.addWidget(btn_load_preset)
        row2.addWidget(btn_reset_defs)
        row2.addStretch()
        actions_vbox.addLayout(row2)

        filter_layout.addLayout(actions_vbox)

        splitter.addWidget(filter_box)

        # -------------------------------------------------------------
        # Right Rail: Fault Tolerance & Wheeling Studio
        # -------------------------------------------------------------
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_SM)

        # 1. Fault Tolerance Engine (Error Allowance)
        tolerance_group = QGroupBox("FAULT TOLERANCE ENGINE (ERROR ALLOWANCE)")
        tol_layout = QVBoxLayout(tolerance_group)
        tol_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        tol_layout.setSpacing(SPACING_SM)

        tol_mode_layout = QHBoxLayout()
        tol_mode_layout.addWidget(QLabel("Combination Logic:"))
        self.combo_tol_mode = QComboBox()
        self.combo_tol_mode.addItems(["AND (Strict 100%)", "OR (Any Match)", "Fault-Tolerant (N-of-M Range)"])
        self.combo_tol_mode.currentIndexChanged.connect(self._on_tolerance_mode_changed)
        tol_mode_layout.addWidget(self.combo_tol_mode, stretch=1)
        tol_layout.addLayout(tol_mode_layout)

        # N-of-M Range Controls
        self.range_control_frame = QFrame()
        range_layout = QGridLayout(self.range_control_frame)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.setSpacing(SPACING_SM)

        range_layout.addWidget(QLabel("Min Matching Filters:"), 0, 0)
        self.spin_min_pass = QSpinBox()
        self.spin_min_pass.setRange(0, 150)
        self.spin_min_pass.setValue(5)
        self.spin_min_pass.valueChanged.connect(self._on_tolerance_spin_changed)
        range_layout.addWidget(self.spin_min_pass, 0, 1)

        range_layout.addWidget(QLabel("Max Matching Filters:"), 1, 0)
        self.spin_max_pass = QSpinBox()
        self.spin_max_pass.setRange(0, 150)
        self.spin_max_pass.setValue(25)
        self.spin_max_pass.valueChanged.connect(self._on_tolerance_spin_changed)
        range_layout.addWidget(self.spin_max_pass, 1, 1)

        tol_layout.addWidget(self.range_control_frame)
        self.range_control_frame.setVisible(False)

        self.lbl_tolerance_rule = QLabel("Survivor Rule: Candidate line must strictly satisfy 100% of active filters.")
        self.lbl_tolerance_rule.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 10px; color: #00f0ff;")
        tol_layout.addWidget(self.lbl_tolerance_rule)

        right_layout.addWidget(tolerance_group)

        # 2. Wheeling Studio (Covering Designs & Banker Keys)
        wheel_group = QGroupBox("FULL & ABBREVIATED WHEELING STUDIO")
        wheel_layout = QVBoxLayout(wheel_group)
        wheel_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        wheel_layout.setSpacing(SPACING_SM)

        # Embedded native ball matrix
        self.ball_matrix = BallMatrixWidget()
        self.ball_matrix.setMinimumHeight(150)
        self.ball_matrix.selection_changed.connect(self._on_pool_selection_changed)
        wheel_layout.addWidget(self.ball_matrix)

        # Matrix Presets toolbar
        btn_preset_layout = QHBoxLayout()
        btn_preset_layout.setSpacing(SPACING_XS)
        for label, func in [
            ("All", self.ball_matrix.select_all),
            ("Odd", self.ball_matrix.select_odd),
            ("Even", self.ball_matrix.select_even),
            ("Primes", self.ball_matrix.select_primes),
            ("High", self.ball_matrix.select_high),
            ("Low", self.ball_matrix.select_low),
            ("Clear", self.ball_matrix.clear_selection)
        ]:
            b = QPushButton(label)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"font-size: 10px; padding: 2px 6px; border-radius: {RADIUS_SM}px;")
            b.clicked.connect(func)
            btn_preset_layout.addWidget(b)
        wheel_layout.addLayout(btn_preset_layout)

        # Wheeling parameters
        grid_params = QGridLayout()
        grid_params.setSpacing(SPACING_SM)

        grid_params.addWidget(QLabel("System Type:"), 0, 0)
        self.combo_wheel_type = QComboBox()
        self.combo_wheel_type.addItems(["Abbreviated Covering (Minimal)", "Full Wheel C(n, k)", "Key/Banker Wheel"])
        self.combo_wheel_type.currentIndexChanged.connect(lambda: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        grid_params.addWidget(self.combo_wheel_type, 0, 1)

        grid_params.addWidget(QLabel("Guarantee Tier:"), 1, 0)
        self.combo_guarantee = QComboBox()
        self.combo_guarantee.addItems([
            "Guarantee 4 if 5 (t=4, m=5)",
            "Guarantee 5 if 5 (t=5, m=5)",
            "Guarantee 4 if 6 (t=4, m=6)",
            "Guarantee 3 if 4 (t=3, m=4)"
        ])
        self.combo_guarantee.currentIndexChanged.connect(lambda: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        grid_params.addWidget(self.combo_guarantee, 1, 1)

        grid_params.addWidget(QLabel("Banker Keys (Fixed):"), 2, 0)
        self.txt_bankers = QLineEdit()
        self.txt_bankers.setPlaceholderText("e.g. 05, 12, 23 (must be in pool)")
        self.txt_bankers.textChanged.connect(lambda: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        grid_params.addWidget(self.txt_bankers, 2, 1)

        wheel_layout.addLayout(grid_params)

        self.chk_pruning = QCheckBox("Hamming Redundancy Pruning (Min Distance = 2)")
        self.chk_pruning.setChecked(True)
        self.chk_pruning.toggled.connect(lambda: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        wheel_layout.addWidget(self.chk_pruning)

        self.lbl_wheel_cost = QLabel("Selected: 0 | Lines: 0 | Est. Cost: R$ 0.00")
        self.lbl_wheel_cost.setStyleSheet(f"font-family: '{FONT_MONO}'; font-weight: 700; font-size: 11px; color: #00f0ff;")
        wheel_layout.addWidget(self.lbl_wheel_cost)

        right_layout.addWidget(wheel_group)

        # 3. Vectorized Streaming Pipeline Gauge
        stream_group = QGroupBox("VECTORIZED STREAMING ENGINE (QTHREADPOOL)")
        stream_layout = QVBoxLayout(stream_group)
        stream_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        stream_layout.setSpacing(SPACING_SM)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        stream_layout.addWidget(self.progress_bar)

        self.lbl_pipeline_rate = QLabel("Throughput: Idle (0 combos/sec) | Survived: 0 lines")
        self.lbl_pipeline_rate.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 11px; color: #8b9bb4;")
        stream_layout.addWidget(self.lbl_pipeline_rate)

        stream_btns = QHBoxLayout()
        stream_btns.setSpacing(SPACING_SM)

        self.btn_run_stream = QPushButton("▶ EXECUTE COMBINATORIAL PIPELINE")
        self.btn_run_stream.setObjectName("btn_primary")
        self.btn_run_stream.setCursor(Qt.PointingHandCursor)
        self.btn_run_stream.setMinimumHeight(34)
        self.btn_run_stream.clicked.connect(self._start_streaming_pipeline)

        self.btn_stop_stream = QPushButton("⏹ CANCEL")
        self.btn_stop_stream.setCursor(Qt.PointingHandCursor)
        self.btn_stop_stream.setEnabled(False)
        self.btn_stop_stream.setMinimumHeight(34)
        self.btn_stop_stream.clicked.connect(self._stop_streaming_pipeline)

        stream_btns.addWidget(self.btn_run_stream, stretch=3)
        stream_btns.addWidget(self.btn_stop_stream, stretch=1)
        stream_layout.addLayout(stream_btns)

        right_layout.addWidget(stream_group)
        splitter.addWidget(right_container)

        splitter.setSizes([750, 450])
        main_layout.addWidget(splitter)

    # -------------------------------------------------------------------------
    # Filter Table Management
    # -------------------------------------------------------------------------

    def _populate_filter_table(self) -> None:
        """Populates the table with FilterNodes adhering to game pick count."""
        self.filter_table.blockSignals(True)
        self.filter_table.clearContents()
        self.filter_table.setRowCount(len(self._all_filters))

        for row, f in enumerate(self._all_filters):
            # Col 0: Active Checkbox
            chk = QCheckBox()
            chk.setChecked(f.enabled)
            chk.toggled.connect(lambda checked, idx=row: self._on_filter_checked(idx, checked))
            chk_frame = QWidget()
            chk_layout = QHBoxLayout(chk_frame)
            chk_layout.setContentsMargins(16, 0, 0, 0)
            chk_layout.addWidget(chk)
            self.filter_table.setCellWidget(row, 0, chk_frame)

            # Col 1: Category
            item_cat = QTableWidgetItem(f.category)
            item_cat.setFlags(item_cat.flags() ^ Qt.ItemIsEditable)
            item_cat.setForeground(QColor("#8b9bb4"))
            self.filter_table.setItem(row, 1, item_cat)

            # Col 2: Filter Name
            item_name = QTableWidgetItem(f.name)
            item_name.setToolTip(f.description)
            item_name.setFlags(item_name.flags() ^ Qt.ItemIsEditable)
            self.filter_table.setItem(row, 2, item_name)

            # Col 3: Min Bound SpinBox
            spin_min = QDoubleSpinBox()
            spin_min.setRange(0, 10_000)
            spin_min.setDecimals(1 if f.step < 1 else 0)
            spin_min.setSingleStep(f.step)
            spin_min.setValue(f.min_val)
            spin_min.valueChanged.connect(lambda val, idx=row: self._on_min_val_changed(idx, val))
            self.filter_table.setCellWidget(row, 3, spin_min)

            # Col 4: Max Bound SpinBox
            spin_max = QDoubleSpinBox()
            spin_max.setRange(0, 10_000)
            spin_max.setDecimals(1 if f.step < 1 else 0)
            spin_max.setSingleStep(f.step)
            spin_max.setValue(f.max_val)
            spin_max.valueChanged.connect(lambda val, idx=row: self._on_max_val_changed(idx, val))
            self.filter_table.setCellWidget(row, 4, spin_max)

            # Col 5: Pruned Count
            item_pruned = QTableWidgetItem(f"{f.eliminated_count:,}")
            item_pruned.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_pruned.setFlags(item_pruned.flags() ^ Qt.ItemIsEditable)
            item_pruned.setForeground(QColor("#ef4444"))
            self.filter_table.setItem(row, 5, item_pruned)

        self.filter_table.blockSignals(False)
        self._update_filter_counters()

    def _filter_table_rows(self) -> None:
        """Filters visible rows based on search query and category."""
        query = self.search_input.text().strip().lower()
        cat_sel = self.category_combo.currentText()

        for row, f in enumerate(self._all_filters):
            match_search = (
                not query or
                query in f.name.lower() or
                query in f.id.lower() or
                any(query in tag.lower() for tag in f.tags)
            )
            match_cat = (cat_sel == "All Categories" or f.category == cat_sel)
            self.filter_table.setRowHidden(row, not (match_search and match_cat))

    def _on_filter_checked(self, row: int, checked: bool) -> None:
        if 0 <= row < len(self._all_filters):
            self._all_filters[row].enabled = checked
            self._update_filter_counters()

    def _on_min_val_changed(self, row: int, val: float) -> None:
        if 0 <= row < len(self._all_filters):
            self._all_filters[row].min_val = val

    def _on_max_val_changed(self, row: int, val: float) -> None:
        if 0 <= row < len(self._all_filters):
            self._all_filters[row].max_val = val

    def _update_filter_counters(self) -> None:
        active_count = sum(1 for f in self._all_filters if f.enabled)
        total_count = len(self._all_filters)
        self.lbl_filter_counts.setText(f"Active Filters: {active_count} / {total_count}")
        self._update_tolerance_rule_text()

    def _set_all_filter_checks(self, check: bool) -> None:
        for row in range(self.filter_table.rowCount()):
            if not self.filter_table.isRowHidden(row):
                widget = self.filter_table.cellWidget(row, 0)
                if widget:
                    chk = widget.findChild(QCheckBox)
                    if chk:
                        chk.setChecked(check)
        self._update_filter_counters()

    def _reset_defaults(self) -> None:
        if not self.active_game:
            return
        self._all_filters = self.bridge.load_catalog_filters(self.active_game)
        self._populate_filter_table()

    # -------------------------------------------------------------------------
    # Fault Tolerance Updates
    # -------------------------------------------------------------------------

    def _on_tolerance_mode_changed(self, idx: int) -> None:
        self.range_control_frame.setVisible(idx == 2)
        self._update_tolerance_rule_text()

    def _on_tolerance_spin_changed(self) -> None:
        self._update_tolerance_rule_text()

    def _update_tolerance_rule_text(self) -> None:
        mode_idx = self.combo_tol_mode.currentIndex()
        active_count = sum(1 for f in self._all_filters if f.enabled)

        if mode_idx == 0:
            self.lbl_tolerance_rule.setText("Survivor Rule: Must strictly satisfy 100% of all active filters.")
        elif mode_idx == 1:
            self.lbl_tolerance_rule.setText("Survivor Rule: Candidate passes if ANY single active filter matches.")
        else:
            min_p = self.spin_min_pass.value()
            max_p = self.spin_max_pass.value()
            self.lbl_tolerance_rule.setText(
                f"Survivor Rule: Pass if between {min_p} and {max_p} active filters match (Total Active: {active_count})."
            )

    def _auto_fit_parameters(self) -> None:
        if not self.active_game:
            return

        fitted = self.bridge.compute_auto_fit_ranges(self.active_game.id, self._all_filters, last_n_draws=30)
        if not fitted:
            QMessageBox.information(
                self,
                "Auto-Fit Status",
                f"No historical draw files found for {self.active_game.name}. Using default bounds."
            )
            return

        updated_count = 0
        for row, f in enumerate(self._all_filters):
            if f.id in fitted:
                obs_min, obs_max = fitted[f.id]
                f.min_val = max(0.0, float(obs_min))
                f.max_val = float(obs_max)
                spin_min = self.filter_table.cellWidget(row, 3)
                spin_max = self.filter_table.cellWidget(row, 4)
                if isinstance(spin_min, QDoubleSpinBox):
                    spin_min.setValue(f.min_val)
                if isinstance(spin_max, QDoubleSpinBox):
                    spin_max.setValue(f.max_val)
                updated_count += 1

        QMessageBox.information(
            self,
            "Auto-Fit Complete",
            f"Successfully auto-fitted {updated_count} filters using observed bounds across previous 30 historical draws of {self.active_game.name}."
        )

    def _open_backtest_dialog(self) -> None:
        if not self.active_game:
            return
        tol = self._build_tolerance_rule()
        dialog = BacktestOptimizerDialog(
            game=self.active_game,
            filters=self._all_filters,
            tolerance=tol,
            parent=self
        )
        dialog.filters_optimized.connect(self._on_filters_optimized)
        dialog.exec()

    def _on_filters_optimized(self, relaxed_filters: List[FilterNode]) -> None:
        self._all_filters = relaxed_filters
        self._populate_filter_table()

    def _build_tolerance_rule(self) -> ToleranceRule:
        mode_idx = self.combo_tol_mode.currentIndex()
        if mode_idx == 0:
            mode = ToleranceMode.AND
        elif mode_idx == 1:
            mode = ToleranceMode.OR
        else:
            mode = ToleranceMode.RANGE

        return ToleranceRule(
            mode=mode,
            min_pass=self.spin_min_pass.value(),
            max_pass=self.spin_max_pass.value()
        )

    def _export_yaml_preset(self) -> None:
        if not self.active_game:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export CLI Preset", "strategy_preset.yaml", "YAML Presets (*.yaml)")
        if not path:
            return
        bundle = ProfileBundle(
            active_game_id=self.active_game.id,
            filters=self._all_filters,
            tolerance=self._build_tolerance_rule(),
            selected_pool=list(self.ball_matrix.selected_numbers)
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(bundle.to_cli_yaml())
        QMessageBox.information(self, "Preset Saved", f"Strategy preset exported successfully to:\n{path}")

    def _import_yaml_preset(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import CLI Preset", "", "YAML Presets (*.yaml)")
        if not path:
            return
        import yaml
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            filters_data = data.get("filters", {})
            for flt in self._all_filters:
                if flt.id in filters_data:
                    bounds = filters_data[flt.id]
                    flt.enabled = True
                    flt.min_val = float(bounds.get("min", flt.min_val))
                    flt.max_val = float(bounds.get("max", flt.max_val))

            tol_data = data.get("tolerance", {})
            if "min_pass" in tol_data:
                self.spin_min_pass.setValue(int(tol_data["min_pass"]))
            if "max_pass" in tol_data:
                self.spin_max_pass.setValue(int(tol_data["max_pass"]))

            self._populate_filter_table()
            QMessageBox.information(self, "Preset Loaded", f"Loaded preset with {len(filters_data)} configured filters.")
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Preset", f"Failed to parse YAML preset: {e}")

    # -------------------------------------------------------------------------
    # Wheeling Studio Coordination
    # -------------------------------------------------------------------------

    def _parse_bankers(self) -> List[int]:
        raw = self.txt_bankers.text().strip()
        if not raw:
            return []
        keys = []
        for part in raw.replace(",", " ").split():
            try:
                num = int(part)
                if self.active_game and self.active_game.number_range_min <= num <= self.active_game.number_range_max:
                    keys.append(num)
            except ValueError:
                pass
        return sorted(list(set(keys)))

    def _on_pool_selection_changed(self, selected: List[int]) -> None:
        if not self.active_game:
            return
        k = self.active_game.pick_count
        price = self.active_game.ticket_price
        curr = self.active_game.currency

        num_sel = len(selected)
        wheel_type_idx = self.combo_wheel_type.currentIndex()

        lines = 0
        if num_sel >= k:
            if wheel_type_idx == 1: # Full Wheel
                lines = math.comb(num_sel, k)
            elif wheel_type_idx == 2: # Key Banker
                bankers = self._parse_bankers()
                rem = num_sel - len(bankers)
                needed = k - len(bankers)
                if needed >= 0 and rem >= needed:
                    lines = math.comb(rem, needed)
                else:
                    lines = 0
            else: # Abbreviated
                # Estimated covering ticket density
                guar_idx = self.combo_guarantee.currentIndex()
                t = 4 if guar_idx == 0 else (5 if guar_idx == 1 else 3)
                lines = max(5, int(math.comb(num_sel, t) / max(1, math.comb(k, t))))
                lines = min(lines, 500)

        cost = lines * price
        cost_str = f"R$ {cost:,.2f}" if curr == "BRL" else f"${cost:,.2f}"
        self.lbl_wheel_cost.setText(
            f"Selected: {num_sel} | Est. Lines: {lines:,} | Est. Cost: {cost_str}"
        )

    def set_active_game(self, game: GameSchema) -> None:
        self.active_game = game
        self.ball_matrix.configure_game(game)
        self._all_filters = self.bridge.load_catalog_filters(game)
        self._populate_filter_table()
        self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers))

    # -------------------------------------------------------------------------
    # Streaming Pipeline Execution
    # -------------------------------------------------------------------------

    def _start_streaming_pipeline(self) -> None:
        if not self.active_game:
            return

        selected_pool = list(self.ball_matrix.selected_numbers)
        if len(selected_pool) < self.active_game.pick_count:
            selected_pool = list(range(self.active_game.number_range_min, self.active_game.number_range_max + 1))

        tol = self._build_tolerance_rule()
        bankers = self._parse_bankers()

        # Build WheelingConfig if applicable
        wheeling_cfg = None
        if self.combo_wheel_type.currentIndex() != 0 or bankers:
            w_type = WheelType.ABBREVIATED if self.combo_wheel_type.currentIndex() == 0 else (
                WheelType.FULL if self.combo_wheel_type.currentIndex() == 1 else WheelType.KEY_BANKER
            )
            wheeling_cfg = WheelingConfig(
                wheel_type=w_type,
                pool_numbers=selected_pool,
                guarantee=4,
                condition_match=5,
                key_numbers=bankers,
                pruning_enabled=self.chk_pruning.isChecked(),
                max_ticket_cap=1000
            )

        self._surviving_tickets = []
        self.btn_run_stream.setEnabled(False)
        self.btn_stop_stream.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_pipeline_rate.setText("Throughput: Initializing worker...")

        self._worker = StreamingCombinatorialWorker(
            game=self.active_game,
            pool=selected_pool,
            filters=self._all_filters,
            tolerance=tol,
            wheeling=wheeling_cfg,
            chunk_size=50_000,
            max_survivors_cap=1_000
        )

        self._worker.signals.progress.connect(self._on_worker_progress)
        self._worker.signals.finished.connect(self._on_worker_finished)
        self._worker.signals.error.connect(self._on_worker_error)

        QThreadPool.globalInstance().start(self._worker)

    def _stop_streaming_pipeline(self) -> None:
        if self._worker:
            self._worker.cancel()
            self.lbl_pipeline_rate.setText("Throughput: Cancelling pipeline execution...")

    @Slot(object)
    def _on_worker_progress(self, telemetry: GenerationTelemetry) -> None:
        self.progress_bar.setValue(min(100, int((telemetry.combinations_survived / 1000.0) * 100)))
        self.lbl_pipeline_rate.setText(
            f"Throughput: {telemetry.scan_rate_per_sec:,.0f} combos/sec | "
            f"Reduction: {telemetry.reduction_rate_pct:.1f}% | "
            f"Survived: {telemetry.combinations_survived:,} lines"
        )

    @Slot(object, list)
    def _on_worker_finished(self, telemetry: GenerationTelemetry, survivors: List[TicketReceipt]) -> None:
        self.btn_run_stream.setEnabled(True)
        self.btn_stop_stream.setEnabled(False)
        self.progress_bar.setValue(100)
        self._surviving_tickets = survivors

        status_txt = "Cancelled" if telemetry.cancelled else "Complete"
        self.lbl_pipeline_rate.setText(
            f"Pipeline {status_txt}! Scanned {telemetry.combinations_scanned:,} combos in {telemetry.elapsed_seconds:.2f}s "
            f"({telemetry.scan_rate_per_sec:,.0f}/sec). Survived: {len(survivors):,} tickets."
        )

        # Show surviving tickets modal dialog
        if survivors:
            self._show_survivors_dialog(survivors)
        else:
            QMessageBox.warning(
                self,
                "Pipeline Results",
                "No combinations survived the configured active filters.\nTry relaxing bounds or using Fault Tolerance RANGE mode."
            )

    @Slot(str)
    def _on_worker_error(self, err_msg: str) -> None:
        self.btn_run_stream.setEnabled(True)
        self.btn_stop_stream.setEnabled(False)
        QMessageBox.critical(self, "Pipeline Error", f"Worker encountered an unhandled exception:\n{err_msg}")

    def _show_survivors_dialog(self, tickets: List[TicketReceipt]) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Combinatorial Studio Results — {len(tickets)} Surviving Tickets")
        dlg.setMinimumSize(600, 500)
        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        dlg_layout.setSpacing(SPACING_SM)

        receipt_widget = TicketReceiptWidget(dlg)
        receipt_widget.display_tickets(tickets)
        dlg_layout.addWidget(receipt_widget)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dlg.accept)
        dlg_layout.addWidget(btn_close)

        dlg.exec()
