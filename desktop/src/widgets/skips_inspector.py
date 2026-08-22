from __future__ import annotations
import logging
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QGridLayout
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

SLEEK_DARK = {
    "background": "#121214",
    "primary":    "#00F0FF",   # cyan
    "accent":     "#FF3366",   # active-red: "now skip" / overdue markers
    "success":    "#39FF14",   # green: average-skip reference line
    "warning":    "#FFEA00",   # gold: cautionary skip state
    "panel":      "#1A1A1E",
    "border":     "#222226",
    "text":       "#E0E0E5",
    "text_dim":   "#8A8A95",
}

class SkipsInspectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Skips Inspector")
        self.resize(900, 550)
        self.setStyleSheet(f"background-color: {SLEEK_DARK['background']}; color: {SLEEK_DARK['text']};")
        
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Title/Header label
        self.title_label = QLabel("Skips Inspector — Select a ball")
        self.title_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 16px; font-weight: bold; color: #00F0FF;")
        main_layout.addWidget(self.title_label)

        # Splitter to divide left ledger and right chart
        splitter = QSplitter(Qt.Horizontal)

        # Left Container
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Summary box
        self.summary_box = QGroupBox("Skips Summary")
        self.summary_box.setStyleSheet(
            f"QGroupBox {{ font-weight: bold; color: {SLEEK_DARK['primary']}; border: 1px solid {SLEEK_DARK['border']}; margin-top: 6px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 7px; padding: 0 3px; }}"
        )
        summary_grid = QGridLayout(self.summary_box)
        summary_grid.setContentsMargins(10, 15, 10, 10)
        summary_grid.setSpacing(8)

        lbl_avg_title = QLabel("Average Skip:")
        lbl_avg_title.setStyleSheet(f"color: {SLEEK_DARK['text_dim']}; font-family: 'JetBrains Mono';")
        self.lbl_avg_val = QLabel("N/A")
        self.lbl_avg_val.setStyleSheet(f"color: {SLEEK_DARK['success']}; font-family: 'JetBrains Mono'; font-weight: bold; font-size: 14px;")

        lbl_now_title = QLabel("Now Skip:")
        lbl_now_title.setStyleSheet(f"color: {SLEEK_DARK['text_dim']}; font-family: 'JetBrains Mono';")
        self.lbl_now_val = QLabel("N/A")
        self.lbl_now_val.setStyleSheet(f"font-family: 'JetBrains Mono'; font-weight: bold; font-size: 14px;")

        summary_grid.addWidget(lbl_avg_title, 0, 0)
        summary_grid.addWidget(self.lbl_avg_val, 0, 1)
        summary_grid.addWidget(lbl_now_title, 1, 0)
        summary_grid.addWidget(self.lbl_now_val, 1, 1)

        left_layout.addWidget(self.summary_box)

        # Skip Ledger Table
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(3)
        self.ledger_table.setHorizontalHeaderLabels(["Hit Index", "Draw ID", "Skip Interval"])
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ledger_table.verticalHeader().setVisible(False)
        self.ledger_table.setStyleSheet(
            f"QTableWidget {{ background-color: {SLEEK_DARK['panel']}; border: 1px solid {SLEEK_DARK['border']}; font-family: 'JetBrains Mono'; font-size: 11px; }}"
            f"QHeaderView::section {{ background-color: {SLEEK_DARK['border']}; color: {SLEEK_DARK['text_dim']}; border: none; padding: 4px; }}"
        )
        left_layout.addWidget(self.ledger_table)
        
        splitter.addWidget(left_widget)

        # Right Container - Matplotlib Canvas
        self.figure = Figure(figsize=(6, 4), facecolor=SLEEK_DARK["background"])
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(SLEEK_DARK["panel"])
        
        splitter.addWidget(self.canvas)

        # Ratio: 35% left, 65% right
        splitter.setSizes([315, 585])
        main_layout.addWidget(splitter)

        # Setup tooltip annotation
        self.annotation = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc=SLEEK_DARK["panel"], ec=SLEEK_DARK["primary"], alpha=0.9),
            color=SLEEK_DARK["text"], fontproperties={'family': 'JetBrains Mono', 'size': 9}
        )
        self.annotation.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

        self.bars = []
        self.draw_ids_for_bars = []
        self.skips_for_bars = []

    def update_data(self, payload: dict):
        """Populates fields and redraws chart using the result dict from SkipsJob."""
        number = payload["number"]
        actual_skips = payload["actual_skips"]
        average_skip = payload["average_skip"]
        now_skip = payload["now_skip"]
        draw_ids = payload["draw_ids"]

        self.title_label.setText(f"Skips Inspector — Ball {number:02d}")
        self.lbl_avg_val.setText(f"{average_skip:.2f} draws")
        
        # Color Now Skip based on overdue status
        if now_skip > average_skip:
            self.lbl_now_val.setText(f"{now_skip} draws (OVERDUE)")
            self.lbl_now_val.setStyleSheet(f"color: {SLEEK_DARK['accent']}; font-family: 'JetBrains Mono'; font-weight: bold; font-size: 14px;")
        else:
            self.lbl_now_val.setText(f"{now_skip} draws")
            self.lbl_now_val.setStyleSheet(f"color: {SLEEK_DARK['warning']}; font-family: 'JetBrains Mono'; font-weight: bold; font-size: 14px;")

        # Populate ledger table (most-recent-gap first)
        ledger_items = []
        
        # Add open gap (Now Skip) first
        if len(draw_ids) > 0:
            last_hit_id = draw_ids[-1]
            ledger_items.append(("Current", f"Open (Last: {last_hit_id})", f"{now_skip}"))
            
        # Add historical gaps in reverse order
        for idx in range(len(actual_skips) - 1, -1, -1):
            hit_idx = idx + 1
            draw_id = draw_ids[idx + 1]
            gap_val = actual_skips[idx]
            ledger_items.append((f"Hit {hit_idx}", f"{draw_id}", f"{gap_val}"))

        self.ledger_table.setRowCount(len(ledger_items))
        for row, item in enumerate(ledger_items):
            self.ledger_table.setItem(row, 0, QTableWidgetItem(item[0]))
            self.ledger_table.setItem(row, 1, QTableWidgetItem(item[1]))
            self.ledger_table.setItem(row, 2, QTableWidgetItem(item[2]))

        # Redraw chart
        self.ax.clear()
        self.ax.set_facecolor(SLEEK_DARK["panel"])
        self.ax.tick_params(colors=SLEEK_DARK["text_dim"])
        for spine in self.ax.spines.values():
            spine.set_color(SLEEK_DARK["border"])
        self.ax.grid(True, color=SLEEK_DARK["border"], linestyle=":", alpha=0.5)

        # Clear active tooltip
        self.annotation = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc=SLEEK_DARK["panel"], ec=SLEEK_DARK["primary"], alpha=0.9),
            color=SLEEK_DARK["text"], fontproperties={'family': 'JetBrains Mono', 'size': 9}
        )
        self.annotation.set_visible(False)

        x_vals = list(range(len(actual_skips)))
        
        # Historical gaps
        self.bars = []
        self.draw_ids_for_bars = []
        self.skips_for_bars = []

        if actual_skips:
            h_bars = self.ax.bar(x_vals, actual_skips, color=SLEEK_DARK["primary"], edgecolor=SLEEK_DARK["border"], width=0.6, picker=True)
            self.bars.extend(h_bars)
            self.draw_ids_for_bars.extend(draw_ids[1:])
            self.skips_for_bars.extend(actual_skips)

        # Current open gap
        now_idx = len(actual_skips)
        n_bar = self.ax.bar([now_idx], [now_skip], color=SLEEK_DARK["accent"], hatch="//", edgecolor=SLEEK_DARK["border"], width=0.6, picker=True)
        self.bars.extend(n_bar)
        self.draw_ids_for_bars.append("Current Open")
        self.skips_for_bars.append(now_skip)

        # Average skip line
        self.ax.axhline(average_skip, color=SLEEK_DARK["success"], linestyle="--", linewidth=1.5, label=f"Avg Skip ({average_skip:.2f})")

        self.ax.set_title(f"Historical Skip Intervals — Ball {number:02d}", color=SLEEK_DARK["primary"], fontsize=11, fontproperties={'family': 'JetBrains Mono'})
        self.ax.set_xlabel("Sequential Hits (Oldest ➔ Newest)", color=SLEEK_DARK["text_dim"], fontproperties={'family': 'JetBrains Mono'})
        self.ax.set_ylabel("Skip Distance (Draws)", color=SLEEK_DARK["text_dim"], fontproperties={'family': 'JetBrains Mono'})
        self.ax.legend(facecolor=SLEEK_DARK["panel"], labelcolor=SLEEK_DARK["text"], edgecolor=SLEEK_DARK["border"])

        self.figure.tight_layout()
        self.canvas.draw()

    def on_hover(self, event):
        if event.inaxes == self.ax:
            for bar, draw_id, skip_val in zip(self.bars, self.draw_ids_for_bars, self.skips_for_bars):
                contained, _ = bar.contains(event)
                if contained:
                    # Position tooltip at the top-middle of the hovered bar
                    self.annotation.xy = (bar.get_x() + bar.get_width() / 2, bar.get_height())
                    self.annotation.set_text(f"Draw: {draw_id}\nGap: {skip_val}")
                    self.annotation.set_visible(True)
                    self.canvas.draw_idle()
                    return
            if self.annotation.get_visible():
                self.annotation.set_visible(False)
                self.canvas.draw_idle()
