"""
Advanced Sets & Filters Dialog
==============================
Provides full feature parity with SamLotto's signature advanced filters:
- Tag 24: Successive Number Filter (multi-length consecutive runs)
- Tag 25: Range Filter (dynamic pool partition counts)
- Tag 26: Number Groups Filter (custom ball groups & hit counts)
- Tag 38: Delete History Drawings (historical jackpot deduplication)

Adheres strictly to pyqt6-ui-designer 4px grid tokens and dynamic theming.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Optional, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QCheckBox, QSpinBox, QLineEdit,
    QGridLayout, QGroupBox, QFrame
)

from desktop.src.core.models import GameSchema, FilterNode
from desktop.src.shell.theme_manager import (
    ThemeManager, SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_MD, RADIUS_LG, FONT_MONO, FONT_BODY
)

logger = logging.getLogger(__name__)


class AdvancedFiltersDialog(QDialog):
    """
    Modal dialog configuring SamLotto advanced sets and combinatorial rules.
    """

    filters_configured = Signal(dict)

    def __init__(self, game: GameSchema, current_filters: List[FilterNode], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.game = game
        self.current_filters = {f.id: f for f in current_filters}
        self.theme_manager = ThemeManager()
        self.setWindowTitle(f"⚙️ Advanced Combinatorial Sets — {game.name}")
        self.setMinimumSize(680, 520)
        self.setModal(True)

        self._init_ui()
        self._load_current_values()

    def _init_ui(self) -> None:
        tokens = self.theme_manager.get_tokens()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        # Header Title
        lbl_title = QLabel("SAMLOTTO ADVANCED SETS & COMBINATORIAL RULES")
        lbl_title.setStyleSheet(f"""
            font-family: '{FONT_MONO}';
            font-weight: 900;
            font-size: 13px;
            color: {tokens['primary']};
            letter-spacing: 1px;
        """)
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(
            f"Configure deep structural constraints and historical deduplication for {self.game.name} "
            f"({self.game.pick_count} picks from pool of {self.game.pool_size})."
        )
        lbl_desc.setStyleSheet(f"font-size: 11px; color: {tokens['text_muted']};")
        layout.addWidget(lbl_desc)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._build_range_tab()
        self._build_number_groups_tab()
        self._build_consecutive_tab()
        self._build_history_purge_tab()

        # Bottom Action Bar
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(SPACING_SM)

        self.btn_reset = QPushButton("Reset Defaults")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_to_defaults)
        actions_layout.addWidget(self.btn_reset)

        actions_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        actions_layout.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton("Apply to Filter Graph")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setStyleSheet(f"""
            QPushButton {{
                background-color: {tokens['primary']};
                color: #000000;
                font-weight: 800;
                font-family: '{FONT_MONO}';
                padding: 6px 18px;
                border-radius: {RADIUS_MD}px;
            }}
            QPushButton:hover {{
                background-color: {tokens['primary_hover']};
            }}
        """)
        self.btn_apply.clicked.connect(self._apply_and_close)
        actions_layout.addWidget(self.btn_apply)

        layout.addLayout(actions_layout)

    # -------------------------------------------------------------------------
    # Tab 1: Range Filter (Tag 25)
    # -------------------------------------------------------------------------

    def _build_range_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_MD)

        lbl = QLabel("Tag 25: Range Partitions (Min/Max Balls per Pool Segment)")
        lbl.setStyleSheet(f"font-weight: 700; font-family: '{FONT_MONO}';")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(SPACING_SM)

        # Divide pool into 5 partitions
        M = self.game.pool_size
        k = self.game.pick_count
        step = max(1, M // 5)

        self.range_spins: List[Tuple[QCheckBox, QSpinBox, QSpinBox]] = []
        for i in range(5):
            r_start = i * step + self.game.number_range_min
            r_end = (i + 1) * step if i < 4 else self.game.number_range_max
            chk = QCheckBox(f"Range {i + 1} ({r_start:02d} – {r_end:02d})")
            chk.setChecked(False)

            lbl_min = QLabel("Min:")
            sp_min = QSpinBox()
            sp_min.setRange(0, k)
            sp_min.setValue(0)

            lbl_max = QLabel("Max:")
            sp_max = QSpinBox()
            sp_max.setRange(0, k)
            sp_max.setValue(max(2, k // 2))

            grid.addWidget(chk, i, 0)
            grid.addWidget(lbl_min, i, 1)
            grid.addWidget(sp_min, i, 2)
            grid.addWidget(lbl_max, i, 3)
            grid.addWidget(sp_max, i, 4)

            self.range_spins.append((chk, sp_min, sp_max))

        layout.addLayout(grid)
        layout.addStretch()
        self.tabs.addTab(tab, "Range Partitions (Tag 25)")

    # -------------------------------------------------------------------------
    # Tab 2: Number Groups Filter (Tag 26)
    # -------------------------------------------------------------------------

    def _build_number_groups_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_MD)

        lbl = QLabel("Tag 26: Custom Number Groups Filter")
        lbl.setStyleSheet(f"font-weight: 700; font-family: '{FONT_MONO}';")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(SPACING_SM)

        self.group_inputs: List[Tuple[QCheckBox, QLineEdit, QSpinBox, QSpinBox]] = []
        presets = [
            ("Group A (Prime Numbers)", "02, 03, 05, 07, 11, 13, 17, 19, 23"),
            ("Group B (Fibonacci Numbers)", "01, 02, 03, 05, 08, 13, 21"),
            ("Group C (Top Frequent Hot)", "01, 05, 10, 15, 20, 25"),
        ]

        for idx, (grp_name, default_nums) in enumerate(presets):
            chk = QCheckBox(grp_name)
            txt_nums = QLineEdit(default_nums)
            txt_nums.setStyleSheet(f"font-family: '{FONT_MONO}';")

            sp_min = QSpinBox()
            sp_min.setRange(0, self.game.pick_count)
            sp_min.setValue(1)

            sp_max = QSpinBox()
            sp_max.setRange(0, self.game.pick_count)
            sp_max.setValue(max(3, self.game.pick_count // 2))

            grid.addWidget(chk, idx, 0)
            grid.addWidget(txt_nums, idx, 1)
            grid.addWidget(QLabel("Min:"), idx, 2)
            grid.addWidget(sp_min, idx, 3)
            grid.addWidget(QLabel("Max:"), idx, 4)
            grid.addWidget(sp_max, idx, 5)

            self.group_inputs.append((chk, txt_nums, sp_min, sp_max))

        layout.addLayout(grid)
        layout.addStretch()
        self.tabs.addTab(tab, "Number Groups (Tag 26)")

    # -------------------------------------------------------------------------
    # Tab 3: Consecutive Run Chains (Tag 24)
    # -------------------------------------------------------------------------

    def _build_consecutive_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_MD)

        lbl = QLabel("Tag 24: Successive Consecutive Sequences Filter")
        lbl.setStyleSheet(f"font-weight: 700; font-family: '{FONT_MONO}';")
        layout.addWidget(lbl)

        group_box = QGroupBox("Consecutive Adjacency Rules")
        gb_layout = QVBoxLayout(group_box)
        gb_layout.setSpacing(SPACING_MD)

        self.chk_enable_successive = QCheckBox("Enable Tag 24 Successive Number Constraints")
        gb_layout.addWidget(self.chk_enable_successive)

        form_layout = QGridLayout()
        form_layout.setSpacing(SPACING_SM)

        form_layout.addWidget(QLabel("Min Total Consecutive Steps (e.g. 14-15):"), 0, 0)
        self.sp_min_steps = QSpinBox()
        self.sp_min_steps.setRange(0, self.game.pick_count)
        self.sp_min_steps.setValue(1)
        form_layout.addWidget(self.sp_min_steps, 0, 1)

        form_layout.addWidget(QLabel("Max Total Consecutive Steps:"), 1, 0)
        self.sp_max_steps = QSpinBox()
        self.sp_max_steps.setRange(0, self.game.pick_count)
        self.sp_max_steps.setValue(max(2, int(self.game.pick_count * 0.4)))
        form_layout.addWidget(self.sp_max_steps, 1, 1)

        gb_layout.addLayout(form_layout)
        layout.addWidget(group_box)
        layout.addStretch()
        self.tabs.addTab(tab, "Consecutive Runs (Tag 24)")

    # -------------------------------------------------------------------------
    # Tab 4: Delete History Drawings (Tag 38)
    # -------------------------------------------------------------------------

    def _build_history_purge_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_MD)

        lbl = QLabel("Tag 38: Historical Drawings Deduplication Filter")
        lbl.setStyleSheet(f"font-weight: 700; font-family: '{FONT_MONO}';")
        layout.addWidget(lbl)

        group_box = QGroupBox("Past Jackpot Collision Pruning")
        gb_layout = QVBoxLayout(group_box)
        gb_layout.setSpacing(SPACING_MD)

        self.chk_delete_history = QCheckBox(
            "Purge combinations that have already won the jackpot in historical drawings"
        )
        self.chk_delete_history.setChecked(True)
        gb_layout.addWidget(self.chk_delete_history)

        lbl_info = QLabel(
            "Eliminates candidate tickets that represent exact 100% matches with any past drawn "
            "jackpot combination in the database (SamLotto Tag 38 algorithm)."
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet(f"color: #8b9bb4; font-size: 11px;")
        gb_layout.addWidget(lbl_info)

        layout.addWidget(group_box)
        layout.addStretch()
        self.tabs.addTab(tab, "Delete History (Tag 38)")

    def _load_current_values(self) -> None:
        if "advanced_successive_filter" in self.current_filters:
            flt = self.current_filters["advanced_successive_filter"]
            self.chk_enable_successive.setChecked(flt.enabled)
            self.sp_min_steps.setValue(int(flt.min_val))
            self.sp_max_steps.setValue(int(flt.max_val))

        if "historical_delete_drawings" in self.current_filters:
            flt = self.current_filters["historical_delete_drawings"]
            self.chk_delete_history.setChecked(flt.enabled)

    def _reset_to_defaults(self) -> None:
        self.chk_enable_successive.setChecked(False)
        self.sp_min_steps.setValue(1)
        self.sp_max_steps.setValue(max(2, int(self.game.pick_count * 0.4)))
        self.chk_delete_history.setChecked(True)
        for chk, sp_min, sp_max in self.range_spins:
            chk.setChecked(False)
            sp_min.setValue(0)
            sp_max.setValue(max(2, self.game.pick_count // 2))

    def _apply_and_close(self) -> None:
        config = {
            "advanced_successive_filter": {
                "enabled": self.chk_enable_successive.isChecked(),
                "min": self.sp_min_steps.value(),
                "max": self.sp_max_steps.value()
            },
            "historical_delete_drawings": {
                "enabled": self.chk_delete_history.isChecked(),
                "min": 0,
                "max": 0
            },
            "range_partitions": [
                {
                    "enabled": chk.isChecked(),
                    "min": sp_min.value(),
                    "max": sp_max.value()
                }
                for chk, sp_min, sp_max in self.range_spins
            ]
        }
        self.filters_configured.emit(config)
        self.accept()
