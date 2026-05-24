from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class TelemetryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 1. Header
        header = QLabel("Real-time Swarm Telemetry & Engine Logs")
        header.setStyleSheet("color: #00ff41; font-weight: bold;")
        layout.addWidget(header)

        # 2. Log Viewport
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFontFamily("JetBrains Mono")
        self.log_viewer.setStyleSheet("background-color: #000000; border: 1px solid #333333;")
        self.log_viewer.setPlaceholderText("Connecting to Telemetry Hub...")
        layout.addWidget(self.log_viewer)

        # 3. Controls
        btn_layout = QHBoxLayout()
        self.clear_button = QPushButton("CLEAR CONSOLE")
        self.pause_button = QPushButton("PAUSE STREAM")
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_button)
        btn_layout.addWidget(self.pause_button)
        layout.addLayout(btn_layout)

    def append_log(self, message: str, level: str = "INFO"):
        color = "#00ff41" # Default green
        if level == "ERROR": color = "#ff3131"
        if level == "RESONANCE": color = "#8a2be2"
        if level == "WARN": color = "#ffea00"

        formatted = f'<span style="color: {color}">[{level}] {message}</span>'
        self.log_viewer.append(formatted)
        
        # Auto-scroll
        self.log_viewer.verticalScrollBar().setValue(
            self.log_viewer.verticalScrollBar().maximum()
        )
