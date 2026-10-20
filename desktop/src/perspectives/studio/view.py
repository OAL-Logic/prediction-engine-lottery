"""
Advanced Studio Mode Perspective
================================
Power-user combinatorial laboratory featuring:
1. Searchable multi-column node/filter graph builder (Complete 68-vector Lottery Studio catalog)
2. Fault Tolerance Engine (Error Allowance sliders & N-of-M combinatorial survival)
3. Full & Abbreviated Wheeling Studio (covering designs, Banker keys, Hamming pruning)
4. High-performance native QPainter ball matrix pool selector
5. Vectorized background streaming worker with real-time throughput metrics
Complies strictly with Modern Enterprise Design System (4px grid, design tokens).
"""

from __future__ import annotations

import logging
from typing import List, Dict, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QFrame, QSplitter, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QSpinBox,
    QDoubleSpinBox, QSlider, QProgressBar, QMessageBox, QScrollArea,
    QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QThreadPool, Slot
from PySide6.QtGui import QFont, QCursor

from desktop.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, ToleranceMode,
    WheelingConfig, WheelType, TicketReceipt, GenerationTelemetry,
    ProfileBundle
)
from desktop.src.shell.theme_manager import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_DEFAULT, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
    FONT_MONO, FONT_HEADING, FONT_BODY
)
from desktop.src.services.engine_bridge import EngineBridge
from desktop.src.services.wheeling_solver import WheelingSolver
from desktop.src.services.streaming_worker import StreamingCombinatorialWorker
from desktop.src.widgets.ball_matrix import BallMatrixWidget

logger = logging.getLogger(__name__)


class StudioPerspective(QWidget):
    """Advanced Studio perspective for deep combinatorial filtering & wheeling."""

    stream_completed = Signal(list, dict)  # Emits (survivors, summary)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("workspace_root")
        self.bridge = EngineBridge()
        self.active_game: Optional[GameSchema] = None
        self._all_filters: List[FilterNode] = self.bridge.load_catalog_filters()
        self._active_worker: Optional[StreamingCombinatorialWorker] = None
        self._surviving_tickets: List[TicketReceipt] = []
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        main_layout.setSpacing(SPACING_SM)

        splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Rail: Searchable Multi-Column Filter Graph Builder
        # -------------------------------------------------------------
        filter_box = QGroupBox("COMBINATORIAL FILTER GRAPH (68 Lottery Studio VECTORS)")
        filter_layout = QVBoxLayout(filter_box)
        filter_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        filter_layout.setSpacing(SPACING_SM)

        # Search & Category Filter Bar
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

        # Filter Counter Chip
        filter_status_layout = QHBoxLayout()
        self.lbl_filter_counts = QLabel(f"Active Filters: 0 / {len(self._all_filters)}")
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
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.filter_table.verticalHeader().setVisible(False)
        self.filter_table.setAlternatingRowColors(True)
        filter_layout.addWidget(self.filter_table)

        # Filter Action Buttons
        filter_actions = QHBoxLayout()
        filter_actions.setSpacing(SPACING_SM)

        btn_select_all = QPushButton("Select All")
        btn_clear_all = QPushButton("Deselect All")
        btn_auto_params = QPushButton("⚡ Auto-Fit (Last 30 Draws)")
        btn_advanced_sets = QPushButton("⚙️ Advanced Sets...")
        btn_save_preset = QPushButton("💾 Save Preset (.yaml)")
        btn_load_preset = QPushButton("📂 Load Preset")
        btn_reset_defs = QPushButton("Reset Defaults")

        btn_select_all.clicked.connect(lambda: self._set_all_filter_checks(True))
        btn_clear_all.clicked.connect(lambda: self._set_all_filter_checks(False))
        btn_auto_params.clicked.connect(self._auto_fit_parameters)
        btn_advanced_sets.clicked.connect(self._open_advanced_sets_dialog)
        btn_save_preset.clicked.connect(self._export_yaml_preset)
        btn_load_preset.clicked.connect(self._import_yaml_preset)
        btn_reset_defs.clicked.connect(self._reset_defaults)

        filter_actions.addWidget(btn_select_all)
        filter_actions.addWidget(btn_clear_all)
        filter_actions.addWidget(btn_auto_params)
        filter_actions.addWidget(btn_advanced_sets)
        filter_actions.addWidget(btn_save_preset)
        filter_actions.addWidget(btn_load_preset)
        filter_actions.addWidget(btn_reset_defs)
        filter_layout.addLayout(filter_actions)

        splitter.addWidget(filter_box)

        # -------------------------------------------------------------
        # Right Rail: Fault Tolerance, Wheeling Studio & Execution
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
        self.spin_min_pass.setRange(0, 100)
        self.spin_min_pass.setValue(5)
        self.spin_min_pass.valueChanged.connect(self._on_tolerance_spin_changed)
        range_layout.addWidget(self.spin_min_pass, 0, 1)

        range_layout.addWidget(QLabel("Max Matching Filters:"), 1, 0)
        self.spin_max_pass = QSpinBox()
        self.spin_max_pass.setRange(0, 100)
        self.spin_max_pass.setValue(10)
        self.spin_max_pass.valueChanged.connect(self._on_tolerance_spin_changed)
        range_layout.addWidget(self.spin_max_pass, 1, 1)

        self.lbl_tol_summary = QLabel("Survivor Rule: Pass if between 5 and 10 active filters match.")
        self.lbl_tol_summary.setStyleSheet(f"color: #00f0ff; font-family: '{FONT_MONO}'; font-size: 11px;")
        range_layout.addWidget(self.lbl_tol_summary, 2, 0, 1, 2)
        tol_layout.addWidget(self.range_control_frame)

        right_layout.addWidget(tolerance_group)

        # 2. Wheeling Studio & Ball Matrix Selector
        wheel_group = QGroupBox("FULL && ABBREVIATED WHEELING STUDIO")
        wheel_layout = QVBoxLayout(wheel_group)
        wheel_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        wheel_layout.setSpacing(SPACING_SM)

        # Interactive Native Ball Matrix
        self.ball_matrix = BallMatrixWidget()
        self.ball_matrix.setMinimumHeight(130)
        self.ball_matrix.selection_changed.connect(self._on_pool_selection_changed)
        wheel_layout.addWidget(self.ball_matrix)

        # Wheeling Parameters Grid
        wheel_grid = QGridLayout()
        wheel_grid.setContentsMargins(0, SPACING_XS, 0, SPACING_XS)
        wheel_grid.setSpacing(SPACING_SM)

        wheel_grid.addWidget(QLabel("System Type:"), 0, 0)
        self.combo_wheel_type = QComboBox()
        self.combo_wheel_type.addItems(["Abbreviated Covering (t-if-m)", "Full Wheel C(n, k)", "Key/Banker Numbers"])
        self.combo_wheel_type.currentIndexChanged.connect(lambda _: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        wheel_grid.addWidget(self.combo_wheel_type, 0, 1)

        wheel_grid.addWidget(QLabel("Guarantee Tier:"), 1, 0)
        self.combo_guarantee = QComboBox()
        self.combo_guarantee.addItems([
            "Guarantee 4 if 5 (t=4, m=5)",
            "Guarantee 5 if 6 (t=5, m=6)",
            "Guarantee 3 if 4 (t=3, m=4)",
            "Guarantee 5 if 5 (t=5, m=5)"
        ])
        self.combo_guarantee.currentIndexChanged.connect(lambda _: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        wheel_grid.addWidget(self.combo_guarantee, 1, 1)

        # Banker Keys Input
        wheel_grid.addWidget(QLabel("Banker Keys (Fixed):"), 2, 0)
        self.txt_bankers = QLineEdit()
        self.txt_bankers.setPlaceholderText("e.g. 05, 12, 23 (must appear in all tickets)")
        self.txt_bankers.textChanged.connect(lambda _: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        wheel_grid.addWidget(self.txt_bankers, 2, 1)

        self.chk_pruning = QCheckBox("Hamming Redundancy Pruning")
        self.chk_pruning.setChecked(True)
        self.chk_pruning.stateChanged.connect(lambda _: self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers)))
        wheel_grid.addWidget(self.chk_pruning, 3, 0, 1, 2)

        wheel_layout.addLayout(wheel_grid)

        # Cost Calculator Status
        self.lbl_wheel_cost = QLabel("Selected: 0 | Lines: 0 | Reduction: 0% | Est. Cost: $0.00")
        self.lbl_wheel_cost.setStyleSheet(f"color: #10b981; font-family: '{FONT_MONO}'; font-weight: 700; font-size: 11px;")
        wheel_layout.addWidget(self.lbl_wheel_cost)

        right_layout.addWidget(wheel_group)

        # 3. Vectorized Streaming Pipeline Controls
        pipeline_group = QGroupBox("VECTORIZED STREAMING ENGINE (QTHREADPOOL)")
        pipe_layout = QVBoxLayout(pipeline_group)
        pipe_layout.setContentsMargins(SPACING_SM, SPACING_MD, SPACING_SM, SPACING_SM)
        pipe_layout.setSpacing(SPACING_SM)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        pipe_layout.addWidget(self.progress_bar)

        self.lbl_pipeline_rate = QLabel("Throughput: Idle (0 combos/sec) | Survived: 0 lines")
        self.lbl_pipeline_rate.setStyleSheet(f"font-family: '{FONT_MONO}'; color: #8b9bb4; font-size: 11px;")
        pipe_layout.addWidget(self.lbl_pipeline_rate)

        pipe_btn_layout = QHBoxLayout()
        pipe_btn_layout.setSpacing(SPACING_SM)

        self.btn_run_stream = QPushButton("▶ EXECUTE COMBINATORIAL PIPELINE")
        self.btn_run_stream.setMinimumHeight(38)
        self.btn_run_stream.setStyleSheet("background-color: #10b981; color: #ffffff; font-weight: 800; border-radius: 4px;")
        self.btn_run_stream.clicked.connect(self._start_streaming_pipeline)

        self.btn_stop_stream = QPushButton("⏹ CANCEL")
        self.btn_stop_stream.setEnabled(False)
        self.btn_stop_stream.clicked.connect(self._cancel_streaming_pipeline)

        pipe_btn_layout.addWidget(self.btn_run_stream, stretch=3)
        pipe_btn_layout.addWidget(self.btn_stop_stream, stretch=1)
        pipe_layout.addLayout(pipe_btn_layout)

        right_layout.addWidget(pipeline_group)
        right_layout.addStretch()

        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        right_scroll.setWidget(right_container)

        splitter.addWidget(right_scroll)
        splitter.setSizes([600, 480])
        main_layout.addWidget(splitter)

        self._populate_filter_table()

    # -------------------------------------------------------------------------
    # Filter Table Population & Filtering
    # -------------------------------------------------------------------------

    def _populate_filter_table(self) -> None:
        self.filter_table.clearContents()
        self.filter_table.setRowCount(len(self._all_filters))
        self.filter_table.setColumnWidth(0, 54)
        self.filter_table.setColumnWidth(1, 160)
        self.filter_table.setColumnWidth(3, 95)
        self.filter_table.setColumnWidth(4, 95)
        self.filter_table.setColumnWidth(5, 75)

        for row, f in enumerate(self._all_filters):
            # Column 0: Active Checkbox
            chk = QCheckBox()
            chk.setChecked(f.enabled)
            chk.stateChanged.connect(lambda state, node=f: self._on_filter_checked(node, state))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(SPACING_XS, 0, SPACING_XS, 0)
            chk_layout.addWidget(chk, alignment=Qt.AlignCenter)
            self.filter_table.setCellWidget(row, 0, chk_widget)

            # Column 1: Category Tag
            item_cat = QTableWidgetItem(f.category)
            item_cat.setFlags(item_cat.flags() & ~Qt.ItemIsEditable)
            self.filter_table.setItem(row, 1, item_cat)

            # Column 2: Filter Name + Tooltip
            item_name = QTableWidgetItem(f.name)
            item_name.setToolTip(f"{f.description}\nEngine ID: {f.id}")
            item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
            self.filter_table.setItem(row, 2, item_name)

            # Column 3: Min Bound SpinBox
            spin_min = QDoubleSpinBox()
            spin_min.setRange(0, 5000)
            spin_min.setDecimals(1 if f.step < 1 else 0)
            spin_min.setValue(f.min_val)
            spin_min.valueChanged.connect(lambda v, node=f: setattr(node, "min_val", v))
            self.filter_table.setCellWidget(row, 3, spin_min)

            # Column 4: Max Bound SpinBox
            spin_max = QDoubleSpinBox()
            spin_max.setRange(0, 5000)
            spin_max.setDecimals(1 if f.step < 1 else 0)
            spin_max.setValue(f.max_val)
            spin_max.valueChanged.connect(lambda v, node=f: setattr(node, "max_val", v))
            self.filter_table.setCellWidget(row, 4, spin_max)

            # Column 5: Pruned Count
            item_pruned = QTableWidgetItem(f"{f.eliminated_count:,}")
            item_pruned.setFlags(item_pruned.flags() & ~Qt.ItemIsEditable)
            item_pruned.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.filter_table.setItem(row, 5, item_pruned)

        self._update_tolerance_bounds()

    def _on_filter_checked(self, node: FilterNode, state: int) -> None:
        node.enabled = (state == Qt.Checked.value or state == 2)
        self._update_tolerance_bounds()

    def _update_tolerance_bounds(self) -> None:
        active_count = sum(1 for f in self._all_filters if f.enabled)
        self.lbl_filter_counts.setText(f"Active Filters: {active_count} / {len(self._all_filters)}")
        self.spin_min_pass.setMaximum(max(1, active_count))
        self.spin_max_pass.setMaximum(max(1, active_count))

        if self.spin_min_pass.value() > active_count:
            self.spin_min_pass.setValue(active_count)
        if self.spin_max_pass.value() > active_count:
            self.spin_max_pass.setValue(active_count)

        self.lbl_tol_summary.setText(
            f"Survivor Rule: Pass if between {self.spin_min_pass.value()} and "
            f"{self.spin_max_pass.value()} active filters match out of {active_count} active."
        )

    def _on_tolerance_spin_changed(self) -> None:
        active_count = sum(1 for f in self._all_filters if f.enabled)
        self.lbl_tol_summary.setText(
            f"Survivor Rule: Pass if between {self.spin_min_pass.value()} and "
            f"{self.spin_max_pass.value()} active filters match out of {active_count} active."
        )

    def _set_all_filter_checks(self, checked: bool) -> None:
        for row in range(self.filter_table.rowCount()):
            chk_widget = self.filter_table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk:
                    chk.setChecked(checked)

    def _filter_table_rows(self) -> None:
        search_txt = self.search_input.text().lower()
        cat_filter = self.category_combo.currentText()

        for row, f in enumerate(self._all_filters):
            match_txt = (search_txt in f.name.lower()) or (search_txt in f.category.lower()) or any(search_txt in t.lower() for t in f.tags)
            match_cat = (cat_filter == "All Categories") or (f.category == cat_filter)
            self.filter_table.setRowHidden(row, not (match_txt and match_cat))

    def _on_tolerance_mode_changed(self, idx: int) -> None:
        self.range_control_frame.setEnabled(idx == 2)

    def _reset_defaults(self) -> None:
        """Restores original default min and max bounds for all filters."""
        for row, f in enumerate(self._all_filters):
            f.min_val = f.default_min
            f.max_val = f.default_max
            spin_min = self.filter_table.cellWidget(row, 3)
            spin_max = self.filter_table.cellWidget(row, 4)
            if isinstance(spin_min, QDoubleSpinBox):
                spin_min.setValue(f.default_min)
            if isinstance(spin_max, QDoubleSpinBox):
                spin_max.setValue(f.default_max)
        self._update_tolerance_bounds()

    def _auto_fit_parameters(self) -> None:
        """
        Calculates observed historical parameter bounds across the last 30 draws
        for the active game and updates the UI spinboxes.
        """
        if not self.active_game:
            QMessageBox.warning(self, "No Active Game", "Please select a lottery game first.")
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
                # Provide a slight margin to prevent over-pruning winning lines
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
            f"Successfully auto-fitted {updated_count} filters using observed bounds "
            f"across previous 30 historical draws of {self.active_game.name}."
        )

    def _open_advanced_sets_dialog(self) -> None:
        if not self.active_game:
            return
        from desktop.src.widgets.advanced_filters_dialog import AdvancedFiltersDialog
        dlg = AdvancedFiltersDialog(self.active_game, self._all_filters, self)
        dlg.filters_configured.connect(self._on_advanced_filters_configured)
        dlg.exec()

    def _on_advanced_filters_configured(self, config: dict) -> None:
        if "advanced_successive_filter" in config:
            s_cfg = config["advanced_successive_filter"]
            for flt in self._all_filters:
                if flt.id == "advanced_successive_filter":
                    flt.enabled = s_cfg["enabled"]
                    flt.min_val = float(s_cfg["min"])
                    flt.max_val = float(s_cfg["max"])
                    break

        if "historical_delete_drawings" in config:
            h_cfg = config["historical_delete_drawings"]
            for flt in self._all_filters:
                if flt.id == "historical_delete_drawings":
                    flt.enabled = h_cfg["enabled"]
                    break

        self._populate_filter_table()
        QMessageBox.information(
            self,
            "Advanced Sets Applied",
            "Advanced combinatorial sets and historical deduplication rules configured successfully."
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
            tolerance=ToleranceRule(
                mode=ToleranceMode.AND if self.combo_tol_mode.currentIndex() == 0 else (
                    ToleranceMode.OR if self.combo_tol_mode.currentIndex() == 1 else ToleranceMode.RANGE
                ),
                min_pass=self.spin_min_pass.value(),
                max_pass=self.spin_max_pass.value()
            ),
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

    def _on_pool_selection_changed(self, selected: List[int]) -> None:
        if not self.active_game:
            return
        k = self.active_game.pick_count
        price = self.active_game.ticket_price
        curr = self.active_game.currency

        # Parse banker key numbers
        raw_keys = self.txt_bankers.text().replace(",", " ").split()
        bankers = []
        for x in raw_keys:
            if x.isdigit():
                val = int(x)
                if val in selected:
                    bankers.append(val)

        mode_idx = self.combo_wheel_type.currentIndex()
        if mode_idx == 0:
            w_type = WheelType.ABBREVIATED
        elif mode_idx == 1:
            w_type = WheelType.FULL
        else:
            w_type = WheelType.KEY_BANKER

        cfg = WheelingConfig(
            wheel_type=w_type,
            pool_numbers=selected,
            guarantee=4 if self.combo_guarantee.currentIndex() in (0, 2) else 5,
            condition_match=5 if self.combo_guarantee.currentIndex() == 0 else 6,
            pick_size=k,
            key_numbers=bankers,
            pruning_enabled=self.chk_pruning.isChecked()
        )
        report = WheelingSolver.compute_guarantee_report(
            lines=WheelingSolver.generate_tickets(cfg, self.active_game),
            pool=selected,
            k=k,
            price_per_ticket=price,
            currency=curr
        )
        self.lbl_wheel_cost.setText(
            f"Selected: {len(selected)} | Lines: {report['generated_lines']:,} | "
            f"Reduction: {report['reduction_rate_pct']}% | Est. Cost: {report['formatted_cost']}"
        )

    def set_active_game(self, game: GameSchema) -> None:
        self.active_game = game
        self.ball_matrix.configure_game(game)
        # Reload catalog with game-specific defaults
        self._all_filters = self.bridge.load_catalog_filters(game)
        self._populate_filter_table()
        self._on_pool_selection_changed(list(self.ball_matrix.selected_numbers))

    # -------------------------------------------------------------------------
    # Background Streaming Pipeline
    # -------------------------------------------------------------------------

    def _start_streaming_pipeline(self) -> None:
        if not self.active_game:
            return

        selected_pool = list(self.ball_matrix.selected_numbers)
        if len(selected_pool) < self.active_game.pick_count:
            # Fallback to standard pool sample if none explicitly selected
            selected_pool = list(range(
                self.active_game.number_range_min,
                self.active_game.number_range_min + min(18, self.active_game.pool_size)
            ))

        active_filters = [f for f in self._all_filters if f.enabled]

        # Build Tolerance Rule
        mode_idx = self.combo_tol_mode.currentIndex()
        if mode_idx == 0:
            mode = ToleranceMode.AND
        elif mode_idx == 1:
            mode = ToleranceMode.OR
        else:
            mode = ToleranceMode.RANGE

        tolerance = ToleranceRule(
            mode=mode,
            min_pass=self.spin_min_pass.value(),
            max_pass=self.spin_max_pass.value()
        )

        # Get last draw for repeat filters
        df_draws = self.bridge.get_draws(self.active_game.id, limit=1)
        last_draw = df_draws.iloc[-1]["numbers"] if not df_draws.empty else None

        # Instantiate background worker
        self._active_worker = StreamingCombinatorialWorker(
            pool=selected_pool,
            pick_count=self.active_game.pick_count,
            active_filters=active_filters,
            tolerance=tolerance,
            chunk_size=100_000,
            max_survivors_cap=1_000,
            last_draw=last_draw
        )

        self._active_worker.signals.started.connect(self._on_stream_started)
        self._active_worker.signals.progress.connect(self._on_stream_progress)
        self._active_worker.signals.finished.connect(self._on_stream_finished)
        self._active_worker.signals.cancelled.connect(self._on_stream_cancelled)
        self._active_worker.signals.error.connect(self._on_stream_error)

        QThreadPool.globalInstance().start(self._active_worker)

    def _cancel_streaming_pipeline(self) -> None:
        if self._active_worker:
            self._active_worker.cancel()
            self.btn_stop_stream.setEnabled(False)

    @Slot()
    def _on_stream_started(self) -> None:
        self.btn_run_stream.setEnabled(False)
        self.btn_stop_stream.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_pipeline_rate.setText("Throughput: Initializing SIMD chunks...")

    @Slot(object)
    def _on_stream_progress(self, telemetry: GenerationTelemetry) -> None:
        self.lbl_pipeline_rate.setText(
            f"Throughput: {telemetry.scan_rate_per_sec:,.0f} combos/sec | "
            f"Scanned: {telemetry.combinations_scanned:,} | Survived: {telemetry.combinations_survived:,} "
            f"(-{telemetry.reduction_rate_pct}%)"
        )
        cur = self.progress_bar.value()
        self.progress_bar.setValue((cur + 15) % 100)

    @Slot(list, dict)
    def _on_stream_finished(self, survivors: List[TicketReceipt], summary: dict) -> None:
        self.btn_run_stream.setEnabled(True)
        self.btn_stop_stream.setEnabled(False)
        self.progress_bar.setValue(100)
        self._surviving_tickets = survivors
        self.lbl_pipeline_rate.setText(
            f"Complete: {summary['total_scanned']:,} scanned in {summary['elapsed_seconds']}s "
            f"({summary['throughput_combos_sec']:,.0f} combos/sec). {summary['total_survived']} survivors (-{summary['reduction_rate_pct']}%)."
        )
        self.stream_completed.emit(survivors, summary)

    @Slot()
    def _on_stream_cancelled(self) -> None:
        self.btn_run_stream.setEnabled(True)
        self.btn_stop_stream.setEnabled(False)
        self.lbl_pipeline_rate.setText("Execution cancelled by operator.")

    @Slot(str)
    def _on_stream_error(self, err: str) -> None:
        self.btn_run_stream.setEnabled(True)
        self.btn_stop_stream.setEnabled(False)
        self.lbl_pipeline_rate.setText(f"Error: {err}")
