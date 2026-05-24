from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QFormLayout, 
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt

class PredictionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 1. Configuration Group
        config_group = QGroupBox("Engine Configuration")
        config_layout = QFormLayout(config_group)
        
        self.lottery_combo = QComboBox()
        self.lottery_combo.addItems(["br/mega-sena", "br/lotofacil", "us/powerball"])
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Stacking AI", "LSTM-CRF", "XGBoost", "Zeno Quantum", "Ensemble Pro"])
        
        self.prediction_spin = QSpinBox()
        self.prediction_spin.setRange(1, 10)
        self.prediction_spin.setValue(5)
        
        self.gpu_checkbox = QCheckBox("Enable CUDA Acceleration")
        
        config_layout.addRow("Lottery Asset:", self.lottery_combo)
        config_layout.addRow("Intelligence Tier:", self.model_combo)
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

        # 5. Status Footer
        self.status_label = QLabel("Engine State: IDLE | PQC: ACTIVE")
        self.status_label.setStyleSheet("font-size: 10px; color: #008f11;")
        layout.addWidget(self.status_label)
