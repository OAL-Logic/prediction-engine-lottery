"""
Predict Center Tab.

Formula -> Algorithm drill-down, adapted from SamLotto's fixed Formula-1..6
picker onto this engine's registry of 150+ strategies (see
docs/wayfinder/tickets/106-prediction-verification-gui.md): "Formula" is a
strategy family/preset (engine.strategies.STRATEGY_PRESETS — tiers like
statistical/ml/deep/fun/foundation plus curated groups like default/fast/
chaos/esoteric), "Algorithm" is one concrete strategy within that family. A
fixed 6-item dropdown doesn't fit an engine this size; family-then-algorithm
is the same two-step "pick a method" flow SamLotto offers, sized to what's
actually here — and it's driven live from the registry, so new strategies
(and new families/tiers, like `tabfm` in `foundation`) show up with no
changes to this file.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QTextEdit, QProgressBar, QSplitter
)
from PySide6.QtCore import Signal
from desktop.src.widgets.pipeline_diagram import PredictionPipelineWidget


class PredictionTab(QWidget):
    # Emitted by "Push to Pool" with the last predicted ticket's numbers —
    # ProphetDashboard connects this to NumberGrid.select_numbers().
    numbers_recommended = Signal(list)

    def __init__(self):
        super().__init__()
        self.last_ticket: list[int] = []
        self.initUI()

    def apply_theme(self, colors: dict):
        self.status_label.setStyleSheet(f"font-size: 10px; color: {colors.get('text_dim', '#9ca3af')};")
        if hasattr(self, 'pipeline_widget'):
            self.pipeline_widget.apply_theme(colors)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Top Pipeline Visual Diagram
        self.pipeline_widget = PredictionPipelineWidget()
        layout.addWidget(self.pipeline_widget)

        # 1. Configuration Group
        config_group = QGroupBox("Engine Configuration")
        config_layout = QFormLayout(config_group)

        self.lottery_combo = QComboBox()
        self._populate_lotteries()

        self.formula_combo = QComboBox()
        self.algorithm_combo = QComboBox()
        self._populate_formulas()
        self.formula_combo.currentTextChanged.connect(self._populate_algorithms)
        self._populate_algorithms(self.formula_combo.currentText())

        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(0, 500)
        self.offset_spin.setValue(0)
        self.offset_spin.setToolTip("Predict as of N draws ago instead of the latest draw (0 = latest draw).")

        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(20, 2000)
        self.depth_spin.setValue(100)
        self.depth_spin.setSingleStep(10)
        self.depth_spin.setToolTip("How many historical draws to feed the algorithm.")

        self.prediction_spin = QSpinBox()
        self.prediction_spin.setRange(1, 10)
        self.prediction_spin.setValue(5)

        self.gpu_checkbox = QCheckBox("Enable CUDA Acceleration")

        config_layout.addRow("Lottery Asset:", self.lottery_combo)
        config_layout.addRow("Formula:", self.formula_combo)
        config_layout.addRow("Algorithm:", self.algorithm_combo)
        config_layout.addRow("Offset (draws back):", self.offset_spin)
        config_layout.addRow("Depth (history window):", self.depth_spin)
        config_layout.addRow("Asset Quantity:", self.prediction_spin)
        config_layout.addRow("Hardware:", self.gpu_checkbox)

        layout.addWidget(config_group)

        # 2. Action Controls
        control_layout = QHBoxLayout()
        self.predict_button = QPushButton("GENERATE JUSTIFIED ASSET")
        self.predict_button.setStyleSheet("font-size: 14px; padding: 10px;")

        self.train_button = QPushButton("RETRAIN SWARM")
        self.train_button.setToolTip("Retrains the MARL agents with latest historical data")

        control_layout.addWidget(self.predict_button, 2)
        control_layout.addWidget(self.train_button, 1)
        layout.addLayout(control_layout)

        # 3. Progress Section
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        layout.addWidget(self.progress_bar)

        # 4. Result Area
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Awaiting Resonance Scan...")
        self.result_box.setFontFamily("JetBrains Mono")
        layout.addWidget(self.result_box)

        # 5. Push to Pool
        self.push_pool_button = QPushButton("→ PUSH RECOMMENDATION TO POOL BUILDER")
        self.push_pool_button.setEnabled(False)
        self.push_pool_button.setToolTip("Send the last generated ticket to the main NumberGrid as the active pool.")
        self.push_pool_button.clicked.connect(self._emit_push_to_pool)
        layout.addWidget(self.push_pool_button)

        # 6. Status Footer
        self.status_label = QLabel("Engine State: IDLE | PQC: ACTIVE")
        self.status_label.setStyleSheet("font-size: 10px;")
        layout.addWidget(self.status_label)

    # ------------------------------------------------------------------
    # Formula / Algorithm drill-down
    # ------------------------------------------------------------------

    def _populate_lotteries(self):
        from engine.adapters.registry import registry
        games = registry.list_games(only_available=True)
        self.lottery_combo.addItems([g.id for g in games] or ["br/lotofacil"])

    def _populate_formulas(self):
        from engine.strategies import STRATEGY_PRESETS
        families = sorted(STRATEGY_PRESETS.keys())
        self.formula_combo.addItems(families)
        if "default" in families:
            self.formula_combo.setCurrentText("default")

    def _populate_algorithms(self, family: str):
        from engine.strategies import STRATEGY_PRESETS
        self.algorithm_combo.clear()
        members = STRATEGY_PRESETS.get(family, [])
        self.algorithm_combo.addItems(sorted(members) if members else ["weighted"])

    def selected_strategy(self) -> str:
        """The concrete strategy name to run — the Algorithm combo's current value."""
        return self.algorithm_combo.currentText() or "weighted"

    # ------------------------------------------------------------------
    # Push to Pool
    # ------------------------------------------------------------------

    def set_last_ticket(self, ticket: list[int]):
        """Called by ProphetDashboard once a prediction finishes."""
        self.last_ticket = list(ticket)
        self.push_pool_button.setEnabled(bool(ticket))

    def _emit_push_to_pool(self):
        if self.last_ticket:
            self.numbers_recommended.emit(self.last_ticket)
