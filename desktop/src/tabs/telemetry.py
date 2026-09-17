from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

from desktop.src.theme.manager import THEMES, DEFAULT_THEME

class TelemetryTab(QWidget):
    def __init__(self):
        super().__init__()
        # Default-theme fallback; apply_theme() overwrites these once ThemeManager
        # is wired up, so the very first paint before that call still looks right.
        self.colors = THEMES[DEFAULT_THEME]
        self._paused = False
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 1. Header
        self.header = QLabel("Real-time Swarm Telemetry & Engine Logs")
        self.header.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.header)

        # 2. Log Viewport
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFontFamily("JetBrains Mono")
        self.log_viewer.setPlaceholderText("Connecting to Telemetry Hub...")
        layout.addWidget(self.log_viewer)

        # 3. Controls
        btn_layout = QHBoxLayout()
        self.clear_button = QPushButton("CLEAR CONSOLE")
        self.clear_button.clicked.connect(self.log_viewer.clear)
        self.pause_button = QPushButton("PAUSE STREAM")
        self.pause_button.setCheckable(True)
        self.pause_button.toggled.connect(self._toggle_pause)
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_button)
        btn_layout.addWidget(self.pause_button)
        layout.addLayout(btn_layout)

    def _toggle_pause(self, checked: bool):
        self._paused = checked
        self.pause_button.setText("RESUME STREAM" if checked else "PAUSE STREAM")

    def apply_theme(self, colors: dict):
        self.colors = colors
        self.header.setStyleSheet(f"color: {colors['primary']}; font-weight: bold;")
        self.log_viewer.setStyleSheet(
            f"background-color: {colors['background']}; border: 1px solid {colors['border']};"
        )

    def append_log(self, message: str, level: str = "INFO"):
        if self._paused:
            return

        color = self.colors["primary"]  # Default
        if level == "ERROR": color = self.colors["error"]
        if level == "RESONANCE": color = self.colors["accent"]
        if level == "WARN": color = self.colors["warning"]

        formatted = f'<span style="color: {color}">[{level}] {message}</span>'
        self.log_viewer.append(formatted)

        # Auto-scroll
        self.log_viewer.verticalScrollBar().setValue(
            self.log_viewer.verticalScrollBar().maximum()
        )
