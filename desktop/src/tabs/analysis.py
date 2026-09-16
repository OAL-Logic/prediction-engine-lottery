import logging
import numpy as np
import pandas as pd
import scipy.stats as stats
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from engine.modules.storage import storage
from engine.cli.utils import get_adapter
from engine.modules.filters import (
    PRIMES, get_odd_count, get_high_low_counts, get_ac_value, get_root_sum,
    get_decade_metrics, get_successive_metrics, get_prime_count,
    get_composite_count, get_unit_metrics,
)
from desktop.src.telemetry.manager import SkipsJob

logger = logging.getLogger(__name__)

class AnalysisTab(QWidget):
    """
    Statistical Cockpit Tab.
    Provides live high-density Matplotlib analytics matching the dark neon theme,
    coupled with an interactive statistics ledger that supports click-to-drill-down
    skips analysis.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self.df_draws = pd.DataFrame()
        self.skips_dialog = None
        
        # Default fallback palette (Sleek Dark Mode)
        self.colors = {
            "background": "#121214",
            "primary":    "#00F0FF",   # Cyber Cyan
            "accent":     "#FF3366",   # Active Red
            "success":    "#39FF14",   # Radioactive Green
            "warning":    "#FFEA00",   # Supernova Gold
            "panel":      "#1A1A1E",
            "border":     "#222226",
            "text":       "#E0E0E5",
            "text_dim":   "#8A8A95",
        }
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 1. Header Control Panel
        top_layout = QHBoxLayout()
        
        self.combo_analysis_type = QComboBox()
        self.combo_analysis_type.addItems([
            "Frequency Distribution",
            "Actual Skips Statistics",
            "Sum Range Bell Curve",
            "Positional Matrix Heatmap",
            "Odd/Even & High/Low Balance",
            "Arithmetic Complexity (AC) Distribution",
            "Root Sum Distribution",
            "Decade Distribution",
            "Consecutive Groups Analysis",
            "Prime & Composite Balance",
            "Unit Digit Analysis",
        ])
        self.combo_analysis_type.currentTextChanged.connect(self.on_analysis_changed)
        
        top_layout.addWidget(QLabel("Select Forensic View:"))
        top_layout.addWidget(self.combo_analysis_type)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)

        # 2. Main Analytics Splitter (Upper Table + Chart vs Lower Summary card)
        main_splitter = QSplitter(Qt.Vertical)

        # Horizontal Splitter dividing Left Stats Table & Right Plot Canvas
        upper_splitter = QSplitter(Qt.Horizontal)

        # 2.1 QTableWidget for Statistics Data
        self.stats_table = QTableWidget()
        self.stats_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stats_table.setSelectionMode(QTableWidget.SingleSelection)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.cellClicked.connect(self.on_row_selected)
        upper_splitter.addWidget(self.stats_table)

        # 2.2 Matplotlib Chart Canvas
        self.figure = Figure(figsize=(8, 6), facecolor=self.colors["background"])
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.colors["panel"])
        upper_splitter.addWidget(self.canvas)

        # Set sizes (35% table, 65% chart)
        upper_splitter.setSizes([350, 650])
        main_splitter.addWidget(upper_splitter)

        # 2.3 Diagnostic Summary Box
        self.stats_box = QGroupBox("Diagnostic Summary")
        stats_layout = QVBoxLayout(self.stats_box)
        
        self.summary_label = QLabel("Awaiting database load...")
        self.summary_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 12px;")
        stats_layout.addWidget(self.summary_label)
        
        main_splitter.addWidget(self.stats_box)
        
        # Ratio: 4 parts upper workspace, 1 part diagnostic card
        main_splitter.setSizes([600, 150])
        layout.addWidget(main_splitter)

        # Initial load
        self.load_data()

    def sync_theme_colors(self):
        """Syncs local color map with the top-level main window theme settings."""
        main_win = self.window()
        if hasattr(main_win, "theme_manager") and main_win.theme_manager:
            theme_name = main_win.theme_manager.settings.value("theme", "Sleek Dark Mode")
            theme_palette = main_win.theme_manager.themes.get(theme_name)
            if theme_palette:
                for k, v in theme_palette.items():
                    self.colors[k] = v
        
        # Apply stylesheet to table to match theme
        self.stats_table.setStyleSheet(
            f"QTableWidget {{ background-color: {self.colors['panel']}; border: 1px solid {self.colors['border']}; font-family: 'JetBrains Mono'; font-size: 11px; color: {self.colors['text']}; }}"
            f"QTableWidget::item:selected {{ background-color: {self.colors['primary']}; color: {self.colors['background']}; }}"
            f"QHeaderView::section {{ background-color: {self.colors['border']}; color: {self.colors['text_dim']}; border: none; padding: 4px; }}"
        )
        self.summary_label.setStyleSheet(f"font-family: 'JetBrains Mono'; font-size: 12px; color: {self.colors['success']};")

    def set_lottery(self, lottery_id: str):
        """Called globally when active lottery swaps."""
        self.active_lottery = lottery_id
        self.load_data()

    def load_data(self):
        """Queries DuckDB storage for the latest 200 draws to perform fast real-time analytics."""
        try:
            self.df_draws = storage.load_draws(self.active_lottery, limit=200)
            self.update_chart()
        except Exception as e:
            logger.exception("Failed to query DuckDB in AnalysisTab.")
            self.summary_label.setText(f"Database Query Error: {str(e)}")

    def on_analysis_changed(self, text: str):
        self.update_chart()

    def update_chart(self):
        """Clears figure, populates stats table, and redraws chart using DuckDB data."""
        self.sync_theme_colors()
        self.ax.clear()
        self.stats_table.setRowCount(0)
        self.stats_table.setColumnCount(0)
        
        if self.df_draws.empty or len(self.df_draws) < 3:
            self.ax.text(0.5, 0.5, "Insufficient drawings in database to perform analysis.", 
                         color=self.colors["error"], ha='center', va='center', transform=self.ax.transAxes)
            self.figure.patch.set_facecolor(self.colors["background"])
            self.ax.set_facecolor(self.colors["panel"])
            self.canvas.draw()
            self.summary_label.setText("Diagnostician State: INSUFFICIENT DATA")
            return

        view_type = self.combo_analysis_type.currentText()
        
        try:
            rules = get_adapter(self.active_lottery).rules
            min_n, max_n = rules.number_range
            pick_k = rules.pick_count
        except Exception:
            min_n, max_n = 1, 25
            pick_k = 15

        all_numbers = np.concatenate(self.df_draws["numbers"].values)
        total_draws = len(self.df_draws)

        # Style standard chart background/axes
        self.figure.patch.set_facecolor(self.colors["background"])
        self.ax.set_facecolor(self.colors["panel"])
        self.ax.tick_params(colors=self.colors["text_dim"])
        for spine in self.ax.spines.values():
            spine.set_color(self.colors["border"])
        self.ax.grid(True, color=self.colors["border"], linestyle=":", alpha=0.5)

        if view_type == "Frequency Distribution":
            # Compute Frequencies
            counts = pd.Series(all_numbers).value_counts()
            freqs = [counts.get(n, 0) for n in range(min_n, max_n + 1)]
            x_vals = list(range(min_n, max_n + 1))
            
            sorted_counts = counts.sort_values(ascending=False)
            hot_balls = list(sorted_counts.index[:3])
            cold_balls = list(sorted_counts.index[-3:])
            
            colors = []
            for n in x_vals:
                if n in hot_balls:
                    colors.append(self.colors["primary"]) # Hot
                elif n in cold_balls:
                    colors.append(self.colors["accent"])  # Cold
                else:
                    colors.append(self.colors["success"]) # Standard
            
            # Plot
            self.ax.bar(x_vals, freqs, color=colors, edgecolor=self.colors["border"], linewidth=1)
            self.ax.set_title(f"Historical Frequency Distribution (Last {total_draws} Draws)", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Lottery Ball Number", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Occurrence Count", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(x_vals)
            
            # Populate Table
            self.stats_table.setColumnCount(4)
            self.stats_table.setHorizontalHeaderLabels(["Ball Number", "Occurrence Count", "Frequency %", "Status"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(max_n - min_n + 1)
            
            for row, n in enumerate(x_vals):
                cnt = counts.get(n, 0)
                pct = (cnt / total_draws) * 100
                status = "Normal"
                if n in hot_balls:
                    status = "Hot"
                elif n in cold_balls:
                    status = "Cold"
                
                self.stats_table.setItem(row, 0, QTableWidgetItem(f"Ball {n:02d}"))
                self.stats_table.setItem(row, 1, QTableWidgetItem(str(cnt)))
                self.stats_table.setItem(row, 2, QTableWidgetItem(f"{pct:.2f}%"))
                self.stats_table.setItem(row, 3, QTableWidgetItem(status))
                
                # Apply custom text color based on status
                for col in range(4):
                    item = self.stats_table.item(row, col)
                    if status == "Hot":
                        item.setForeground(QColor(self.colors["primary"]))
                    elif status == "Cold":
                        item.setForeground(QColor(self.colors["accent"]))
                    else:
                        item.setForeground(QColor(self.colors["text"]))

            # Diagnostic Summary Text
            summary = (
                f"📊 Frequency Diagnostic (Lookback: {total_draws} drawings):\n"
                f"  ➔ Hottest Swarm Numbers   : " + ", ".join(f"{b:02d}" for b in hot_balls) + f" (Freq: {counts.get(hot_balls[0],0)}, {counts.get(hot_balls[1],0)}, {counts.get(hot_balls[2],0)})\n"
                f"  ➔ Coldest Frozen Numbers : " + ", ".join(f"{b:02d}" for b in cold_balls) + f" (Freq: {counts.get(cold_balls[0],0)}, {counts.get(cold_balls[1],0)}, {counts.get(cold_balls[2],0)})"
            )
            self.summary_label.setText(summary)

        elif view_type == "Actual Skips Statistics":
            curr_skips = {}
            avg_skips = {}
            max_skips = {}
            
            for n in range(min_n, max_n + 1):
                appearances = []
                for idx, row in self.df_draws.iterrows():
                    if n in row["numbers"]:
                        appearances.append(idx)
                
                if appearances:
                    gaps = np.diff(appearances) - 1
                    avg_skips[n] = np.mean(gaps) if len(gaps) > 0 else 0.0
                    max_skips[n] = np.max(gaps) if len(gaps) > 0 else 0.0
                    curr_skips[n] = total_draws - 1 - appearances[-1]
                else:
                    avg_skips[n] = float(total_draws)
                    max_skips[n] = float(total_draws)
                    curr_skips[n] = float(total_draws)

            x_vals = np.arange(min_n, max_n + 1)
            width = 0.35
            currents = [curr_skips[n] for n in x_vals]
            averages = [avg_skips[n] for n in x_vals]
            
            # Plot
            self.ax.bar(x_vals - width/2, currents, width, label='Current Skip', color=self.colors["warning"])
            self.ax.bar(x_vals + width/2, averages, width, label='Average Skip', color=self.colors["success"])
            self.ax.set_title("Actual Skips Cockpit (Current vs Average Skips)", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Lottery Ball Number", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Drawing Gaps (Draws)", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(x_vals)
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])
            
            # Populate Table
            self.stats_table.setColumnCount(5)
            self.stats_table.setHorizontalHeaderLabels(["Ball Number", "Current Skip", "Average Skip", "Max Skip", "Status"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(max_n - min_n + 1)
            
            for row, n in enumerate(x_vals):
                c_skip = curr_skips[n]
                a_skip = avg_skips[n]
                m_skip = max_skips[n]
                status = "Overdue" if c_skip > a_skip else "Normal"
                
                self.stats_table.setItem(row, 0, QTableWidgetItem(f"Ball {n:02d}"))
                self.stats_table.setItem(row, 1, QTableWidgetItem(str(c_skip)))
                self.stats_table.setItem(row, 2, QTableWidgetItem(f"{a_skip:.2f}"))
                self.stats_table.setItem(row, 3, QTableWidgetItem(str(m_skip)))
                self.stats_table.setItem(row, 4, QTableWidgetItem(status))
                
                for col in range(5):
                    item = self.stats_table.item(row, col)
                    if status == "Overdue":
                        item.setForeground(QColor(self.colors["accent"]))
                    else:
                        item.setForeground(QColor(self.colors["text"]))

            overdue_n = max(x_vals, key=lambda n: curr_skips[n] - avg_skips[n])
            summary = (
                f"⏳ Actual Skips Diagnostic Ledger:\n"
                f"  ➔ Average Skip Range : {min(averages):.1f} to {max(averages):.1f} draws\n"
                f"  ➔ Most Overdue Ball  : Ball {overdue_n:02d} (Current: {curr_skips[overdue_n]} draws vs Avg: {avg_skips[overdue_n]:.1f})"
            )
            self.summary_label.setText(summary)

        elif view_type == "Sum Range Bell Curve":
            sums = self.df_draws["numbers"].apply(sum).values
            
            # Plot
            n_bins = min(20, len(np.unique(sums)))
            self.ax.hist(sums, bins=n_bins, density=True, color=self.colors["success"], alpha=0.4, edgecolor=self.colors["border"])
            
            mu, std = stats.norm.fit(sums)
            xmin, xmax = self.ax.get_xlim()
            x = np.linspace(xmin, xmax, 100)
            p = stats.norm.pdf(x, mu, std)
            self.ax.plot(x, p, self.colors["primary"], linewidth=2, linestyle='--', label='Gaussian Normal Fit')
            
            self.ax.set_title(f"Ticket Sum Range Bell Curve (Mean: {mu:.1f}, StdDev: {std:.1f})", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Drawing Ticket Sum Value", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Probability Density", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])
            
            # Populate Table (Recent draws and sums)
            self.stats_table.setColumnCount(5)
            self.stats_table.setHorizontalHeaderLabels(["Draw ID", "Draw Date", "Numbers", "Ticket Sum", "Deviation (z)"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(len(self.df_draws))
            
            # Reverse order (most recent first)
            for idx, (_, row_data) in enumerate(self.df_draws.iloc[::-1].iterrows()):
                d_sum = sum(row_data["numbers"])
                z_score = (d_sum - mu) / std if std > 0 else 0.0
                nums_str = ", ".join(map(str, sorted(row_data["numbers"])))
                
                self.stats_table.setItem(idx, 0, QTableWidgetItem(str(row_data["draw_id"])))
                self.stats_table.setItem(idx, 1, QTableWidgetItem(str(row_data["draw_date"])))
                self.stats_table.setItem(idx, 2, QTableWidgetItem(nums_str))
                self.stats_table.setItem(idx, 3, QTableWidgetItem(str(d_sum)))
                self.stats_table.setItem(idx, 4, QTableWidgetItem(f"{z_score:+.2f}"))
                
                # Check for extreme sums (z-score > 1.5 or < -1.5)
                for col in range(5):
                    item = self.stats_table.item(idx, col)
                    if abs(z_score) > 1.5:
                        item.setForeground(QColor(self.colors["warning"]))
                    else:
                        item.setForeground(QColor(self.colors["text"]))

            inside_resonance = np.sum((sums >= mu - 1.5 * std) & (sums <= mu + 1.5 * std))
            resonance_pct = (inside_resonance / len(sums)) * 100
            
            summary = (
                f"🔔 Sum Range Normal Curve Fit:\n"
                f"  ➔ Mathematical Mean Sum : {mu:.2f} | Standard Deviation: {std:.2f}\n"
                f"  ➔ Golden Resonance Zone [mu - 1.5*std, mu + 1.5*std] : {int(mu - 1.5*std)} to {int(mu + 1.5*std)} sum value\n"
                f"  ➔ Drawings inside Resonance Zone : {inside_resonance} / {total_draws} ({resonance_pct:.2f}% of draws)"
            )
            self.summary_label.setText(summary)

        elif view_type == "Positional Matrix Heatmap":
            pos_matrix = np.zeros((pick_k, max_n - min_n + 1), dtype=np.int32)
            for _, row_data in self.df_draws.iterrows():
                sorted_nums = sorted(row_data["numbers"])
                for pos, num in enumerate(sorted_nums):
                    if pos < pick_k and min_n <= num <= max_n:
                        pos_matrix[pos, num - min_n] += 1
            
            # Plot
            self.ax.imshow(pos_matrix, cmap='viridis', aspect='auto', interpolation='nearest')
            self.ax.set_title("Positional Index Frequency Heatmap", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Ball Sort Index (Pos 1..Pos K)", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Ball Number value", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_yticks(range(pick_k))
            self.ax.set_yticklabels([f"Pos {i+1}" for i in range(pick_k)])
            
            x_ticks = list(range(0, max_n - min_n + 1, max(1, (max_n - min_n) // 10)))
            self.ax.set_xticks(x_ticks)
            self.ax.set_xticklabels([f"{x + min_n:02d}" for x in x_ticks])
            
            # Populate Table
            self.stats_table.setColumnCount(4)
            self.stats_table.setHorizontalHeaderLabels(["Ball Number", "Sort Position", "Peak Count", "Peak %"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(max_n - min_n + 1)
            
            x_vals = list(range(min_n, max_n + 1))
            for row, n in enumerate(x_vals):
                pos_counts = pos_matrix[:, n - min_n]
                peak_pos = int(np.argmax(pos_counts))
                peak_cnt = int(pos_counts[peak_pos])
                peak_pct = (peak_cnt / total_draws) * 100
                
                self.stats_table.setItem(row, 0, QTableWidgetItem(f"Ball {n:02d}"))
                self.stats_table.setItem(row, 1, QTableWidgetItem(f"Pos {peak_pos + 1}"))
                self.stats_table.setItem(row, 2, QTableWidgetItem(str(peak_cnt)))
                self.stats_table.setItem(row, 3, QTableWidgetItem(f"{peak_pct:.2f}%"))
                
                for col in range(4):
                    item = self.stats_table.item(row, col)
                    item.setForeground(QColor(self.colors["text"]))

            max_idx = np.unravel_index(np.argmax(pos_matrix, axis=None), pos_matrix.shape)
            locked_pos = max_idx[0] + 1
            locked_val = max_idx[1] + min_n
            locked_cnt = pos_matrix[max_idx]
            
            summary = (
                f"🌡️ Positional Entropy & Density Analysis:\n"
                f"  ➔ High concentration shows digit limits and natural position caps.\n"
                f"  ➔ Most Concentrated Node: Ball {locked_val:02d} at Sort Position {locked_pos} (Count: {locked_cnt} occurrences)"
            )
            self.summary_label.setText(summary)

        elif view_type == "Odd/Even & High/Low Balance":
            odd_counts = [get_odd_count(r["numbers"]) for _, r in self.df_draws.iterrows()]
            high_counts = [get_high_low_counts(r["numbers"], max_n)["high"] for _, r in self.df_draws.iterrows()]
            x_vals = list(range(pick_k + 1))
            odd_dist = [odd_counts.count(v) for v in x_vals]
            high_dist = [high_counts.count(v) for v in x_vals]
            width = 0.35

            self.ax.bar([x - width / 2 for x in x_vals], odd_dist, width, label="Odd Count", color=self.colors["primary"])
            self.ax.bar([x + width / 2 for x in x_vals], high_dist, width, label="High Count", color=self.colors["accent"])
            self.ax.set_title("Odd/Even & High/Low Balance Distribution", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Count per Draw (of pick size)", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Number of Historical Draws", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(x_vals)
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])

            self.stats_table.setColumnCount(6)
            self.stats_table.setHorizontalHeaderLabels(["Draw ID", "Draw Date", "Odd", "Even", "High", "Low"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(total_draws)

            for idx, (_, row_data) in enumerate(self.df_draws.iloc[::-1].iterrows()):
                nums = row_data["numbers"]
                o = get_odd_count(nums)
                hl = get_high_low_counts(nums, max_n)
                for col, val in enumerate([row_data["draw_id"], row_data["draw_date"], o, len(nums) - o, hl["high"], hl["low"]]):
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(self.colors["text"]))
                    self.stats_table.setItem(idx, col, item)

            most_common_odd = max(x_vals, key=lambda v: odd_dist[v])
            summary = (
                f"⚖️ Odd/Even & High/Low Diagnostic:\n"
                f"  ➔ Most Common Odd Count : {most_common_odd} odds / {pick_k - most_common_odd} evens ({odd_dist[most_common_odd]} of {total_draws} draws)\n"
                f"  ➔ Balanced Draw Theory  : Ideal split is close to {pick_k // 2}/{pick_k - pick_k // 2}"
            )
            self.summary_label.setText(summary)

        elif view_type == "Arithmetic Complexity (AC) Distribution":
            ac_values = [get_ac_value(r["numbers"]) for _, r in self.df_draws.iterrows()]
            mean_ac = float(np.mean(ac_values)) if ac_values else 0.0
            max_possible_ac = (pick_k * (pick_k - 1)) // 2 - (pick_k - 1)
            n_bins = max(1, min(20, len(set(ac_values))))

            self.ax.hist(ac_values, bins=n_bins, color=self.colors["primary"], alpha=0.6, edgecolor=self.colors["border"])
            self.ax.axvline(mean_ac, color=self.colors["warning"], linestyle="--", linewidth=2, label=f"Mean AC: {mean_ac:.1f}")
            self.ax.set_title("Arithmetic Complexity (AC) Value Distribution", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("AC Value (Higher = More Random Spacing)", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Occurrence Count", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])

            self.stats_table.setColumnCount(4)
            self.stats_table.setHorizontalHeaderLabels(["Draw ID", "Draw Date", "Numbers", "AC Value"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(total_draws)

            for idx, (_, row_data) in enumerate(self.df_draws.iloc[::-1].iterrows()):
                nums = row_data["numbers"]
                ac = get_ac_value(nums)
                nums_str = ", ".join(map(str, sorted(nums)))
                is_low = max_possible_ac > 0 and ac < max_possible_ac * 0.5
                for col, val in enumerate([row_data["draw_id"], row_data["draw_date"], nums_str, ac]):
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(self.colors["warning"] if is_low else self.colors["text"]))
                    self.stats_table.setItem(idx, col, item)

            summary = (
                f"🧮 Arithmetic Complexity Diagnostic:\n"
                f"  ➔ Mean AC Value : {mean_ac:.2f} (Max possible: {max_possible_ac})\n"
                f"  ➔ Low-complexity draws (highlighted) suggest arithmetic/patterned number spacing."
            )
            self.summary_label.setText(summary)

        elif view_type == "Root Sum Distribution":
            root_sums = [get_root_sum(r["numbers"]) for _, r in self.df_draws.iterrows()]
            digits = list(range(1, 10))
            dist = [root_sums.count(v) for v in digits]
            expected = total_draws / 9.0

            self.ax.bar(digits, dist, color=self.colors["success"], edgecolor=self.colors["border"])
            self.ax.axhline(expected, color=self.colors["accent"], linestyle="--", linewidth=1.5, label=f"Uniform Expectation ({expected:.1f})")
            self.ax.set_title("Root Sum (Digital Root) Distribution", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Root Sum Digit (1-9)", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Historical Draw Count", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(digits)
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])

            self.stats_table.setColumnCount(3)
            self.stats_table.setHorizontalHeaderLabels(["Root Sum Digit", "Occurrence Count", "Frequency %"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(9)

            for row, digit in enumerate(digits):
                cnt = dist[row]
                pct = (cnt / total_draws) * 100 if total_draws else 0.0
                for col, val in enumerate([digit, cnt, f"{pct:.2f}%"]):
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(self.colors["text"]))
                    self.stats_table.setItem(row, col, item)

            peak_digit = int(np.argmax(dist)) + 1
            summary = (
                f"🔢 Root Sum (Digital Root) Diagnostic:\n"
                f"  ➔ Most Frequent Root Sum : {peak_digit} ({dist[peak_digit - 1]} of {total_draws} draws)\n"
                f"  ➔ Uniform Expectation    : ~{expected:.1f} draws per digit if perfectly random"
            )
            self.summary_label.setText(summary)

        elif view_type == "Decade Distribution":
            n_buckets = ((max_n - min_n) // 10) + 1
            bucket_counts = [0] * n_buckets
            for n in all_numbers:
                b = int((n - min_n) // 10)
                if 0 <= b < n_buckets:
                    bucket_counts[b] += 1
            bucket_labels = [f"{min_n + b * 10:02d}-{min(min_n + b * 10 + 9, max_n):02d}" for b in range(n_buckets)]
            peak_cnt, trough_cnt = max(bucket_counts), min(bucket_counts)

            bar_colors = [
                self.colors["primary"] if c == peak_cnt else (self.colors["accent"] if c == trough_cnt else self.colors["success"])
                for c in bucket_counts
            ]
            self.ax.bar(range(n_buckets), bucket_counts, color=bar_colors, edgecolor=self.colors["border"])
            self.ax.set_title(f"Decade Group Frequency (Last {total_draws} Draws)", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Decade Bucket", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Ball Appearances", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(range(n_buckets))
            self.ax.set_xticklabels(bucket_labels, rotation=45, ha="right")

            self.stats_table.setColumnCount(5)
            self.stats_table.setHorizontalHeaderLabels(["Decade Bucket", "Total Hits", "Frequency %", "Avg Hits/Draw", "Status"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(n_buckets)

            total_balls = len(all_numbers)
            for row in range(n_buckets):
                cnt = bucket_counts[row]
                pct = (cnt / total_balls) * 100 if total_balls else 0.0
                avg = cnt / total_draws if total_draws else 0.0
                status = "Hot" if cnt == peak_cnt else ("Cold" if cnt == trough_cnt else "Normal")
                for col, val in enumerate([bucket_labels[row], cnt, f"{pct:.2f}%", f"{avg:.2f}", status]):
                    item = QTableWidgetItem(str(val))
                    if status == "Hot":
                        item.setForeground(QColor(self.colors["primary"]))
                    elif status == "Cold":
                        item.setForeground(QColor(self.colors["accent"]))
                    else:
                        item.setForeground(QColor(self.colors["text"]))
                    self.stats_table.setItem(row, col, item)

            avg_groups = float(np.mean([get_decade_metrics(r["numbers"])["groups"] for _, r in self.df_draws.iterrows()]))
            hot_bucket = bucket_labels[int(np.argmax(bucket_counts))]
            summary = (
                f"🎚️ Decade Group Diagnostic:\n"
                f"  ➔ Hottest Decade Bucket : {hot_bucket} ({peak_cnt} hits)\n"
                f"  ➔ Avg Contiguous Decade Groups per Draw : {avg_groups:.2f}"
            )
            self.summary_label.setText(summary)

        elif view_type == "Consecutive Groups Analysis":
            run_lengths = [get_successive_metrics(r["numbers"])["max_successive"] for _, r in self.df_draws.iterrows()]
            max_run = max(run_lengths) if run_lengths else 0
            x_vals = list(range(max_run + 1))
            dist = [run_lengths.count(v) for v in x_vals]

            bar_colors = [self.colors["success"] if v == 0 else self.colors["warning"] for v in x_vals]
            self.ax.bar(x_vals, dist, color=bar_colors, edgecolor=self.colors["border"])
            self.ax.set_title("Longest Consecutive Run Length Distribution", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Max Consecutive Run Length (0 = none)", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Historical Draw Count", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(x_vals)

            self.stats_table.setColumnCount(5)
            self.stats_table.setHorizontalHeaderLabels(["Draw ID", "Draw Date", "Numbers", "Max Run Length", "Run Groups"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(total_draws)

            for idx, (_, row_data) in enumerate(self.df_draws.iloc[::-1].iterrows()):
                nums = row_data["numbers"]
                metrics = get_successive_metrics(nums)
                nums_str = ", ".join(map(str, sorted(nums)))
                has_run = metrics["max_successive"] > 0
                for col, val in enumerate([row_data["draw_id"], row_data["draw_date"], nums_str, metrics["max_successive"], metrics["groups"]]):
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(self.colors["warning"] if has_run else self.colors["text"]))
                    self.stats_table.setItem(idx, col, item)

            pct_with_run = (sum(1 for r in run_lengths if r > 0) / total_draws) * 100 if total_draws else 0.0
            summary = (
                f"🔗 Consecutive Groups Diagnostic:\n"
                f"  ➔ Draws with at least one consecutive pair : {pct_with_run:.1f}% of history\n"
                f"  ➔ Longest run ever observed : {max_run} consecutive numbers"
            )
            self.summary_label.setText(summary)

        elif view_type == "Prime & Composite Balance":
            prime_counts = [get_prime_count(r["numbers"]) for _, r in self.df_draws.iterrows()]
            x_vals = list(range(pick_k + 1))
            dist = [prime_counts.count(v) for v in x_vals]
            mean_p = float(np.mean(prime_counts)) if prime_counts else 0.0
            primes_in_pool = int(np.sum((PRIMES >= min_n) & (PRIMES <= max_n)))

            self.ax.bar(x_vals, dist, color=self.colors["primary"], edgecolor=self.colors["border"])
            self.ax.axvline(mean_p, color=self.colors["warning"], linestyle="--", linewidth=2, label=f"Mean: {mean_p:.2f}")
            self.ax.set_title("Prime Number Count Distribution", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Prime Numbers per Draw", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Historical Draw Count", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xticks(x_vals)
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])

            self.stats_table.setColumnCount(4)
            self.stats_table.setHorizontalHeaderLabels(["Draw ID", "Draw Date", "Prime Count", "Composite Count"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(total_draws)

            for idx, (_, row_data) in enumerate(self.df_draws.iloc[::-1].iterrows()):
                nums = row_data["numbers"]
                for col, val in enumerate([row_data["draw_id"], row_data["draw_date"], get_prime_count(nums), get_composite_count(nums)]):
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(self.colors["text"]))
                    self.stats_table.setItem(idx, col, item)

            summary = (
                f"🔷 Prime & Composite Diagnostic:\n"
                f"  ➔ Mean Prime Count per Draw : {mean_p:.2f} of {pick_k} balls\n"
                f"  ➔ Primes available in pool [{min_n}-{max_n}] : {primes_in_pool}"
            )
            self.summary_label.setText(summary)

        elif view_type == "Unit Digit Analysis":
            unit_sums = [get_unit_metrics(r["numbers"])["sum"] for _, r in self.df_draws.iterrows()]
            mean_u = float(np.mean(unit_sums)) if unit_sums else 0.0
            n_bins = max(1, min(20, len(set(unit_sums))))

            self.ax.hist(unit_sums, bins=n_bins, color=self.colors["success"], alpha=0.6, edgecolor=self.colors["border"])
            self.ax.axvline(mean_u, color=self.colors["primary"], linestyle="--", linewidth=2, label=f"Mean: {mean_u:.1f}")
            self.ax.set_title("Unit Digit Sum Distribution (Sum of Last Digits)", color=self.colors["primary"], fontsize=12, fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_xlabel("Unit Digit Sum", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.set_ylabel("Historical Draw Count", color=self.colors["text_dim"], fontproperties={'family': 'JetBrains Mono'})
            self.ax.legend(facecolor=self.colors["panel"], labelcolor=self.colors["text"], edgecolor=self.colors["border"])

            self.stats_table.setColumnCount(4)
            self.stats_table.setHorizontalHeaderLabels(["Draw ID", "Draw Date", "Unit Sum", "Distinct Units"])
            self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.stats_table.setRowCount(total_draws)

            for idx, (_, row_data) in enumerate(self.df_draws.iloc[::-1].iterrows()):
                um = get_unit_metrics(row_data["numbers"])
                for col, val in enumerate([row_data["draw_id"], row_data["draw_date"], um["sum"], um["different"]]):
                    item = QTableWidgetItem(str(val))
                    item.setForeground(QColor(self.colors["text"]))
                    self.stats_table.setItem(idx, col, item)

            summary = (
                f"🔟 Unit Digit Diagnostic:\n"
                f"  ➔ Mean Unit Digit Sum : {mean_u:.2f}\n"
                f"  ➔ Higher distinct-unit counts suggest broader last-digit spread (less digit clustering)."
            )
            self.summary_label.setText(summary)

        self.figure.tight_layout()
        self.canvas.draw()

    @Slot(int, int)
    def on_row_selected(self, row: int, col: int):
        """Triggered when a user clicks a row in the stats table. Parses target number and launches background skips calculations."""
        # Only allow clicks in views that represent per-ball statistics (first column "Ball NN").
        # All other views are keyed by Draw ID / bucket / digit, which would otherwise be
        # misparsed as a ball number by the int(text) fallback below.
        view_type = self.combo_analysis_type.currentText()
        NON_BALL_VIEWS = {
            "Sum Range Bell Curve",
            "Odd/Even & High/Low Balance",
            "Arithmetic Complexity (AC) Distribution",
            "Root Sum Distribution",
            "Decade Distribution",
            "Consecutive Groups Analysis",
            "Prime & Composite Balance",
            "Unit Digit Analysis",
        }
        if view_type in NON_BALL_VIEWS:
            return

        item = self.stats_table.item(row, 0)
        if not item:
            return
            
        text = item.text()
        try:
            if text.startswith("Ball "):
                number = int(text.split(" ")[-1])
            else:
                number = int(text)
            self.inspect_number_skips(number)
        except ValueError:
            # Clicking non-number rows (e.g. Draw IDs in Sum Range) is ignored
            pass

    def inspect_number_skips(self, number: int):
        """Launches QThread skips job for the target number."""
        main_win = self.window()
        if not hasattr(main_win, "thread_manager") or main_win.thread_manager is None:
            logger.warning("Main window thread manager not found, skipping skips drill-down.")
            return

        # Start background job using ThreadManager
        task_id = f"skips_{self.active_lottery}_{number}"
        job = main_win.thread_manager.start_job(
            task_id,
            SkipsJob(self.active_lottery, number, num_draws=200)
        )
        if job:
            job.signals.finished.connect(self.on_skips_job_finished)
            job.signals.failed.connect(self.on_skips_job_failed)

    @Slot(dict)
    def on_skips_job_finished(self, payload: dict):
        """Displays or updates the modeless SkipsInspectorDialog once calculations finish."""
        if not hasattr(self, "skips_dialog") or self.skips_dialog is None:
            from desktop.src.widgets.skips_inspector import SkipsInspectorDialog
            self.skips_dialog = SkipsInspectorDialog(self)
        
        self.skips_dialog.show()
        self.skips_dialog.raise_()
        self.skips_dialog.activateWindow()
        self.skips_dialog.update_data(payload)

    @Slot(str, str, str)
    def on_skips_job_failed(self, title: str, msg: str, tb: str):
        """Displays error details if skips calculations fail."""
        QMessageBox.critical(self, title, f"Failed to compute skips profile:\n{msg}")
