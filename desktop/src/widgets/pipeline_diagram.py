"""
Prediction Pipeline Diagram & Telemetry Widget.

Renders an interactive, visually stunning diagram showing what is happening
inside the multi-stage prediction engine:
1. Data Ingestion & Sanity Checks (DuckDB columnar draws)
2. Diagnostic & Regime Scan (Entropy, Chi-square uniformity, Drift state)
3. Multi-Model Ensemble Synthesis (Stacking, LSTM-CRF, Markov, Ephemeris)
4. Harmony Gate Filter Funnel (105+ filters elimination)
5. Combinatorial Overlap Optimization (Hamming distance reduction & block reserves)
6. Final Golden Assets (Confidence-calibrated tickets)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen


class PipelineStageNode(QFrame):
    """Visual card representing a single pipeline stage in the engine."""
    
    def __init__(self, step_number: int, title: str, subtitle: str):
        super().__init__()
        self.step_number = step_number
        self.title = title
        self.subtitle = subtitle
        self.is_active = False
        self.is_completed = False
        self.metric_text = "Idle"
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumWidth(130)
        self.setMaximumHeight(85)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        # Step header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        self.badge_label = QLabel(f"STAGE {step_number}")
        self.badge_label.setStyleSheet("font-size: 9px; font-weight: bold; opacity: 0.8;")
        header_layout.addWidget(self.badge_label)
        
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("font-size: 10px; color: #6b7280;")
        header_layout.addWidget(self.status_icon, alignment=Qt.AlignRight)
        layout.addLayout(header_layout)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Metric / Description
        self.metric_label = QLabel(subtitle)
        self.metric_label.setStyleSheet("font-size: 10px; color: #9ca3af;")
        layout.addWidget(self.metric_label)

    def set_state(self, state: str, metric: str = ""):
        """State: 'idle', 'running', 'done', 'error'."""
        self.is_active = (state == "running")
        self.is_completed = (state == "done")
        if metric:
            self.metric_label.setText(metric)
            
        if state == "running":
            self.status_icon.setText("⏳")
            self.status_icon.setStyleSheet("font-size: 10px; color: #3b82f6;")
        elif state == "done":
            self.status_icon.setText("✓")
            self.status_icon.setStyleSheet("font-size: 10px; color: #10b981; font-weight: bold;")
        elif state == "error":
            self.status_icon.setText("✗")
            self.status_icon.setStyleSheet("font-size: 10px; color: #ef4444; font-weight: bold;")
        else:
            self.status_icon.setText("●")
            self.status_icon.setStyleSheet("font-size: 10px; color: #6b7280;")

    def update_style(self, colors: dict):
        bg = colors.get("panel", "#1c2230")
        border = colors.get("border", "#282f3e")
        text = colors.get("text", "#f3f4f6")
        text_dim = colors.get("text_dim", "#9ca3af")
        primary = colors.get("primary", "#3b82f6")
        
        border_style = f"2px solid {primary}" if self.is_active else f"1px solid {border}"
        if self.is_completed:
            border_style = f"1px solid {colors.get('success', '#10b981')}"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: {border_style};
                border-radius: 6px;
            }}
        """)
        self.title_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {text}; border: none; background: transparent;")
        self.metric_label.setStyleSheet(f"font-size: 10px; color: {text_dim}; border: none; background: transparent;")
        self.badge_label.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {primary}; border: none; background: transparent;")


class PredictionPipelineWidget(QWidget):
    """
    Visual dashboard widget displaying the live prediction engine state,
    pipeline flowchart, and strategy contribution breakdown.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = {}
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(10)

        # 1. Pipeline Flow Group
        pipeline_group = QGroupBox("Prediction Engine Execution Pipeline")
        pipeline_layout = QVBoxLayout(pipeline_group)
        pipeline_layout.setContentsMargins(8, 12, 8, 8)
        pipeline_layout.setSpacing(6)

        # Flow nodes row
        nodes_layout = QHBoxLayout()
        nodes_layout.setSpacing(4)
        
        self.node_ingest = PipelineStageNode(1, "Data Ingestion", "DuckDB Verified")
        self.node_scan = PipelineStageNode(2, "Diagnostic Scan", "Regime & Entropy")
        self.node_ensemble = PipelineStageNode(3, "Ensemble Weight", "Stacking Synthesis")
        self.node_filters = PipelineStageNode(4, "Harmony Gate", "105-Filter Funnel")
        self.node_optimize = PipelineStageNode(5, "Ticket Optimizer", "Overlap Reducer")
        self.node_assets = PipelineStageNode(6, "Golden Assets", "Ready for Play")

        nodes = [
            self.node_ingest, self.node_scan, self.node_ensemble,
            self.node_filters, self.node_optimize, self.node_assets
        ]

        for i, node in enumerate(nodes):
            nodes_layout.addWidget(node)
            if i < len(nodes) - 1:
                arrow = QLabel("➔")
                arrow.setAlignment(Qt.AlignCenter)
                arrow.setStyleSheet("font-size: 12px; color: #6b7280; font-weight: bold;")
                nodes_layout.addWidget(arrow)

        pipeline_layout.addLayout(nodes_layout)
        main_layout.addWidget(pipeline_group)

        # 2. Strategy Weight Distribution & Telemetry Row
        telemetry_group = QGroupBox("Active Strategy Contributions & Confidence Allocation")
        telemetry_layout = QGridLayout(telemetry_group)
        telemetry_layout.setContentsMargins(10, 12, 10, 10)
        telemetry_layout.setSpacing(8)

        # Strategy bars
        self.strategies = [
            ("CatBoost Gradient Trees", 35, "#3b82f6"),
            ("LSTM-CRF Neural Sequence", 25, "#8b5cf6"),
            ("Markov Gap Transitions", 20, "#10b981"),
            ("Harmonic & Root Resonance", 12, "#f59e0b"),
            ("Astro / Cosmic Aspects", 8, "#ec4899"),
        ]

        self.strategy_bars = []
        for row, (name, pct, color) in enumerate(self.strategies):
            label = QLabel(name)
            label.setStyleSheet("font-size: 11px; font-weight: 500;")
            
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(True)
            bar.setFormat(f"%p%")
            bar.setFixedHeight(12)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #282f3e;
                    border-radius: 4px;
                    background-color: #161a24;
                    text-align: center;
                    font-size: 10px;
                    font-weight: bold;
                    color: #f3f4f6;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
            
            telemetry_layout.addWidget(label, row, 0)
            telemetry_layout.addWidget(bar, row, 1)
            self.strategy_bars.append((label, bar))

        main_layout.addWidget(telemetry_group)

    def apply_theme(self, colors: dict):
        self.colors = colors
        for node in [
            self.node_ingest, self.node_scan, self.node_ensemble,
            self.node_filters, self.node_optimize, self.node_assets
        ]:
            node.update_style(colors)

    def set_pipeline_stage(self, stage: int, state: str = "running", metric: str = ""):
        """
        Advance or update the pipeline state:
        stage: 1 (Ingest), 2 (Scan), 3 (Ensemble), 4 (Filters), 5 (Optimize), 6 (Assets)
        state: 'idle', 'running', 'done', 'error'
        """
        nodes = [
            self.node_ingest, self.node_scan, self.node_ensemble,
            self.node_filters, self.node_optimize, self.node_assets
        ]
        for i, node in enumerate(nodes, start=1):
            if i < stage:
                node.set_state("done")
            elif i == stage:
                node.set_state(state, metric)
            else:
                node.set_state("idle")
            node.update_style(self.colors)

    def reset_pipeline(self):
        """Reset all nodes back to idle."""
        for node in [
            self.node_ingest, self.node_scan, self.node_ensemble,
            self.node_filters, self.node_optimize, self.node_assets
        ]:
            node.set_state("idle")
            node.update_style(self.colors)

    def set_strategy_weights(self, weights: list[tuple[str, int]]):
        """Dynamically update strategy bars with (name, weight_pct)."""
        for i, (name, pct) in enumerate(weights[:len(self.strategy_bars)]):
            label, bar = self.strategy_bars[i]
            label.setText(name)
            bar.setValue(int(pct))
