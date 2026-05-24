from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class ExpectedValueTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 1. Header Information
        info_label = QLabel("Advantage Principle Analysis — Game Theory Model")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff41;")
        layout.addWidget(info_label)

        # 2. Heatmap Canvas
        chart_group = QGroupBox("Combination Value Heatmap")
        chart_layout = QVBoxLayout(chart_group)
        
        self.figure = Figure(figsize=(10, 6), facecolor='#000000')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#000000')
        
        # Initial Placeholder Data
        self.update_heatmap()
        
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_group)

        # 3. Controls
        btn_layout = QHBoxLayout()
        self.refresh_button = QPushButton("RECALCULATE ADVANTAGE")
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_button)
        layout.addLayout(btn_layout)

    def update_heatmap(self):
        self.ax.clear()
        data = np.random.rand(5, 5)
        im = self.ax.imshow(data, cmap='viridis', interpolation='nearest')
        self.ax.set_title("Probability Resonance Clusters", color='#00ff41')
        self.ax.tick_params(colors='#008f11')
        self.figure.tight_layout()
        self.canvas.draw()
