import logging
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QComboBox, QSplitter
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import scipy.stats as stats

from engine.modules.storage import storage
from engine.cli.utils import get_adapter

logger = logging.getLogger(__name__)

class AnalysisTab(QWidget):
    """
    Statistical Cockpit Tab.
    Provides live high-density Matplotlib analytics matching the dark neon theme,
    linked directly to the active DuckDB history backend.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self.df_draws = pd.DataFrame()
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
            "Positional Matrix Heatmap"
        ])
        self.combo_analysis_type.currentTextChanged.connect(self.on_analysis_changed)
        
        top_layout.addWidget(QLabel("Select Forensic View:"))
        top_layout.addWidget(self.combo_analysis_type)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)

        # 2. Main Analytics Splitter (Chart Canvas vs Tabular Summary card)
        splitter = QSplitter(Qt.Vertical)

        # 2.1 Matplotlib Chart Canvas
        self.figure = Figure(figsize=(10, 6), facecolor='#000000')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#000000')
        
        splitter.addWidget(self.canvas)

        # 2.2 Diagnostic Summary Box
        self.stats_box = QGroupBox("Diagnostic Summary")
        stats_layout = QVBoxLayout(self.stats_box)
        
        self.summary_label = QLabel("Awaiting database load...")
        self.summary_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 12px; color: #00ff41;")
        stats_layout.addWidget(self.summary_label)
        
        splitter.addWidget(self.stats_box)
        
        # Ratio: 4 parts chart, 1 part diagnostic card
        splitter.setSizes([600, 150])
        layout.addWidget(splitter)

        # Initial load
        self.load_data()

    def set_lottery(self, lottery_id: str):
        """Called globally when active lottery swaps."""
        self.active_lottery = lottery_id
        self.load_data()

    def load_data(self):
        """Queries DuckDB storage for the latest 200 draws to perform fast real-time analytics."""
        try:
            # Query last 200 draws for high quality stats without slowing down GUI
            self.df_draws = storage.load_draws(self.active_lottery, limit=200)
            self.update_chart()
        except Exception as e:
            logger.exception("Failed to query DuckDB in AnalysisTab.")
            self.summary_label.setText(f"Database Query Error: {str(e)}")

    def on_analysis_changed(self, text: str):
        self.update_chart()

    def update_chart(self):
        """Clears figure and redraws using DuckDB data according to chosen selector view."""
        self.ax.clear()
        
        if self.df_draws.empty or len(self.df_draws) < 3:
            self.ax.text(0.5, 0.5, "Insufficient drawings in database to perform analysis.", 
                         color='#ff3131', ha='center', va='center', transform=self.ax.transAxes)
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

        if view_type == "Frequency Distribution":
            # 1. Frequency Bar Chart
            counts = pd.Series(all_numbers).value_counts()
            # Ensure all numbers are represented
            freqs = [counts.get(n, 0) for n in range(min_n, max_n + 1)]
            x_vals = list(range(min_n, max_n + 1))
            
            # Sort to identify Hot / Cold
            sorted_counts = counts.sort_values(ascending=False)
            hot_balls = list(sorted_counts.index[:3])
            cold_balls = list(sorted_counts.index[-3:])
            
            # Set bar colors (Matrix Green for standard, Cyan for Hot, Astro Violet for Cold)
            colors = []
            for n in x_vals:
                if n in hot_balls:
                    colors.append("#00B0FF") # Hot cyan
                elif n in cold_balls:
                    colors.append("#8a2be2") # Cold violet
                else:
                    colors.append("#00ff41") # Standard green
            
            self.ax.bar(x_vals, freqs, color=colors, edgecolor='#333333', linewidth=1)
            self.ax.set_title(f"Historical Frequency Distribution (Last {total_draws} Draws)", color='#00ff41', fontsize=12)
            self.ax.set_xlabel("Lottery Ball Number", color='#008f11')
            self.ax.set_ylabel("Occurrence Count", color='#008f11')
            self.ax.tick_params(colors='#008f11')
            self.ax.set_xticks(x_vals)
            
            # Diagnostic Summary Text
            summary = (
                f"📊 Frequency Diagnostic (Lookback: {total_draws} drawings):\n"
                f"  ➔ Hottest Swarm Numbers (Cyan)   : " + ", ".join(f"{b:02d}" for b in hot_balls) + f" (Freq: {counts.get(hot_balls[0],0)}, {counts.get(hot_balls[1],0)}, {counts.get(hot_balls[2],0)})\n"
                f"  ➔ Coldest Frozen Numbers (Violet) : " + ", ".join(f"{b:02d}" for b in cold_balls) + f" (Freq: {counts.get(cold_balls[0],0)}, {counts.get(cold_balls[1],0)}, {counts.get(cold_balls[2],0)})"
            )
            self.summary_label.setText(summary)

        elif view_type == "Actual Skips Statistics":
            # 2. Skips Statistics (Current vs Average Skips side-by-side)
            # We calculate skips for each number in history
            curr_skips = {}
            avg_skips = {}
            max_skips = {}
            
            for n in range(min_n, max_n + 1):
                # Trace indices where n appeared
                appearances = []
                for idx, row in self.df_draws.iterrows():
                    if n in row["numbers"]:
                        appearances.append(idx)
                
                if appearances:
                    # Calculate gaps between indices
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
            
            # Plot side by side bars
            currents = [curr_skips[n] for n in x_vals]
            averages = [avg_skips[n] for n in x_vals]
            
            self.ax.bar(x_vals - width/2, currents, width, label='Current Skip', color='#ffea00') # Yellow warning alert
            self.ax.bar(x_vals + width/2, averages, width, label='Average Skip', color='#00ff41')  # Neon Green
            
            self.ax.set_title("Actual Skips Cockpit (Current vs Average Skips)", color='#00ff41', fontsize=12)
            self.ax.set_xlabel("Lottery Ball Number", color='#008f11')
            self.ax.set_ylabel("Drawing Gaps (Draws)", color='#008f11')
            self.ax.tick_params(colors='#008f11')
            self.ax.set_xticks(x_vals)
            self.ax.legend(facecolor='#000000', labelcolor='#00ff41', edgecolor='#333333')
            
            # Find extreme overdue number
            overdue_n = max(x_vals, key=lambda n: curr_skips[n] - avg_skips[n])
            summary = (
                f"⏳ Actual Skips Diagnostic Ledger:\n"
                f"  ➔ Average Skip Range : {min(averages):.1f} to {max(averages):.1f} draws\n"
                f"  ➔ Most Overdue Ball (Current Skip > Average Skip) : Ball {overdue_n:02d} (Current: {curr_skips[overdue_n]} draws vs Avg: {avg_skips[overdue_n]:.1f})"
            )
            self.summary_label.setText(summary)

        elif view_type == "Sum Range Bell Curve":
            # 3. Sum Range curve
            sums = self.df_draws["numbers"].apply(sum).values
            
            # Plot histogram
            n_bins = min(20, len(np.unique(sums)))
            self.ax.hist(sums, bins=n_bins, density=True, color='#008f11', alpha=0.6, edgecolor='#00ff41')
            
            # Overlay normal curve fit
            mu, std = stats.norm.fit(sums)
            xmin, xmax = self.ax.get_xlim()
            x = np.linspace(xmin, xmax, 100)
            p = stats.norm.pdf(x, mu, std)
            self.ax.plot(x, p, '#00B0FF', linewidth=2, linestyle='--', label='Gaussian Normal Fit')
            
            self.ax.set_title(f"Ticket Sum Range Bell Curve (Mean: {mu:.1f}, StdDev: {std:.1f})", color='#00ff41', fontsize=12)
            self.ax.set_xlabel("Drawing Ticket Sum Value", color='#008f11')
            self.ax.set_ylabel("Probability Density", color='#008f11')
            self.ax.tick_params(colors='#008f11')
            self.ax.legend(facecolor='#000000', labelcolor='#00ff41', edgecolor='#333333')
            
            # Find how many draws are within 1.5 standard deviation (The golden "Resonance zone")
            resonance_lower = mu - 1.5 * std
            resonance_upper = mu + 1.5 * std
            inside_resonance = np.sum((sums >= resonance_lower) & (sums <= resonance_upper))
            resonance_pct = (inside_resonance / len(sums)) * 100
            
            summary = (
                f"🔔 Sum Range Normal Curve Fit:\n"
                f"  ➔ Mathematical Mean Sum : {mu:.2f} | Standard Deviation: {std:.2f}\n"
                f"  ➔ Golden Resonance Zone [mu - 1.5*std, mu + 1.5*std] : {int(resonance_lower)} to {int(resonance_upper)} sum value\n"
                f"  ➔ Drawings inside Resonance Zone : {inside_resonance} / {total_draws} ({resonance_pct:.2f}% of draws)"
            )
            self.summary_label.setText(summary)

        elif view_type == "Positional Matrix Heatmap":
            # 4. Positional Density Heatmap
            # Build index position counts: pick_k rows, max_n columns
            pos_matrix = np.zeros((pick_k, max_n - min_n + 1), dtype=np.int32)
            
            for _, row in self.df_draws.iterrows():
                sorted_nums = sorted(row["numbers"])
                for pos, num in enumerate(sorted_nums):
                    if pos < pick_k and min_n <= num <= max_n:
                        pos_matrix[pos, num - min_n] += 1
            
            # Draw matrix using imshow
            im = self.ax.imshow(pos_matrix, cmap='viridis', aspect='auto', interpolation='nearest')
            
            # Style titles & labels
            self.ax.set_title("Positional Index Frequency Heatmap", color='#00ff41', fontsize=12)
            self.ax.set_ylabel("Ball Sort Index (Pos 1..Pos K)", color='#008f11')
            self.ax.set_xlabel("Ball Number value", color='#008f11')
            
            self.ax.set_yticks(range(pick_k))
            self.ax.set_yticklabels([f"Pos {i+1}" for i in range(pick_k)], color='#008f11')
            
            x_ticks = list(range(0, max_n - min_n + 1, max(1, (max_n - min_n) // 10)))
            self.ax.set_xticks(x_ticks)
            self.ax.set_xticklabels([f"{x + min_n:02d}" for x in x_ticks], color='#008f11')
            self.ax.tick_params(colors='#008f11')
            
            # Find the most locked ball (highest position frequency)
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

        self.figure.tight_layout()
        self.canvas.draw()
