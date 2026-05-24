import logging
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QGroupBox, QFormLayout, QTextEdit, QRadioButton, 
    QButtonGroup, QSplitter, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from engine.wheels import generate_full_wheel, generate_key_wheel, generate_abbreviated_wheel
from engine.modules.wheels_wrg import WheelingEngine
from engine.cli.utils import get_adapter

logger = logging.getLogger(__name__)

class WheelingTab(QWidget):
    """
    Combinatorial Wheeling Workshop cockpit tab.
    Allows user to select a pool of numbers (and keys) and run full,
    abbreviated, or key wheels with a live coverage density heatmap.
    """
    
    # Broadcast generated tickets so that Verification Desk or other tabs can import them
    tickets_generated = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self.pool_numbers = []
        self.key_numbers = []
        self.generated_tickets = []
        self.buttons = {}
        
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Primary Splitter: Left (Pool Selection) vs Right (Config & Analytical Console)
        splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Panel: Number Pool Grid Selection
        # -------------------------------------------------------------
        pool_group = QGroupBox("Number Pool & Key Selector")
        pool_layout = QVBoxLayout(pool_group)
        pool_layout.setSpacing(10)

        # Selection Mode (Pool vs Keys)
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        
        self.radio_pool = QRadioButton("Select Pool")
        self.radio_pool.setChecked(True)
        self.radio_keys = QRadioButton("Select Keys")
        
        self.mode_group.addButton(self.radio_pool, 0)
        self.mode_group.addButton(self.radio_keys, 1)
        
        mode_layout.addWidget(QLabel("Selection Mode:"))
        mode_layout.addWidget(self.radio_pool)
        mode_layout.addWidget(self.radio_keys)
        mode_layout.addStretch()
        
        pool_layout.addLayout(mode_layout)

        # Scroll area containing the number grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #333333; background-color: #000000; }")
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: #000000;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(6)
        scroll_area.setWidget(self.grid_widget)
        
        pool_layout.addWidget(scroll_area, stretch=1)

        # Bottom grid helpers
        helpers_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.select_all_numbers)
        self.btn_clear = QPushButton("Clear Selection")
        self.btn_clear.clicked.connect(self.clear_selection)
        
        helpers_layout.addWidget(self.btn_select_all)
        helpers_layout.addWidget(self.btn_clear)
        pool_layout.addLayout(helpers_layout)

        # Selection counters status label
        self.lbl_status = QLabel("Pool: 0 selected | Keys: 0 selected")
        self.lbl_status.setStyleSheet("color: #008f11; font-weight: bold; font-size: 11px;")
        pool_layout.addWidget(self.lbl_status)

        splitter.addWidget(pool_group)

        # -------------------------------------------------------------
        # Right Panel: Split into Config Form and Output Analytics
        # -------------------------------------------------------------
        right_splitter = QSplitter(Qt.Vertical)

        # Right Top: Configuration Panel
        config_group = QGroupBox("Wheeling Configurator")
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(8)

        self.combo_wheel_type = QComboBox()
        self.combo_wheel_type.addItems(["Full Wheel", "Abbreviated Wheel", "Key Number Wheel"])
        self.combo_wheel_type.currentTextChanged.connect(self.on_wheel_type_changed)

        self.spin_pick = QSpinBox()
        self.spin_pick.setRange(2, 20)
        self.spin_pick.setValue(15) # Default for Lotofacil
        
        # Abbreviated Wheel settings (t if m)
        self.spin_guarantee = QSpinBox()
        self.spin_guarantee.setRange(2, 20)
        self.spin_guarantee.setValue(14)
        
        self.spin_if_hit = QSpinBox()
        self.spin_if_hit.setRange(2, 25)
        self.spin_if_hit.setValue(15)
        
        self.spin_max_tickets = QSpinBox()
        self.spin_max_tickets.setRange(10, 10000)
        self.spin_max_tickets.setValue(500)
        
        config_layout.addRow("Wheel Formula Class:", self.combo_wheel_type)
        config_layout.addRow("Ticket Size (k):", self.spin_pick)
        config_layout.addRow("Guarantee Match (t):", self.spin_guarantee)
        config_layout.addRow("If Drawn in Pool (m):", self.spin_if_hit)
        config_layout.addRow("Max Ticket Cap:", self.spin_max_tickets)

        # Action Button to generate
        self.btn_generate = QPushButton("⚡ GENERATE GOLDEN WHEEL")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #008f11;
                color: #ffffff;
                font-weight: bold;
                padding: 10px;
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #000000;
            }
        """)
        self.btn_generate.clicked.connect(self.generate_wheel)
        config_layout.addRow(self.btn_generate)

        right_splitter.addWidget(config_group)

        # Right Bottom: Output Area & Heatmap Splitter
        output_splitter = QSplitter(Qt.Horizontal)

        # Left: Ticket Monospace Viewport
        results_group = QGroupBox("Generated Ticket Lines")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(6, 6, 6, 6)
        
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setPlaceholderText("Generated wheel tickets will appear here...")
        self.txt_output.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px;")
        results_layout.addWidget(self.txt_output)

        # Payout ROI / Reduction efficiency Summary Card
        self.reduction_box = QGroupBox("Reduction Simulator Analytics")
        reduction_layout = QVBoxLayout(self.reduction_box)
        self.lbl_reduction_stats = QLabel(
            "Combinatorial Universe : 0\n"
            "Golden Reduced Bet Size : 0\n"
            "Bet Space Shrinkage    : 0.00%\n"
            "Estimated Capital Saved : $0.00"
        )
        self.lbl_reduction_stats.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px; color: #00ff41;")
        reduction_layout.addWidget(self.lbl_reduction_stats)
        
        self.btn_send_to_verify = QPushButton("🛡️ SEND TO VERIFICATION DESK")
        self.btn_send_to_verify.setEnabled(False)
        self.btn_send_to_verify.clicked.connect(self.send_to_verification)
        reduction_layout.addWidget(self.btn_send_to_verify)
        
        results_layout.addWidget(self.reduction_box)
        output_splitter.addWidget(results_group)

        # Right: Matplotlib Coverage Map Canvas
        heatmap_group = QGroupBox("Pair Coverage Density Heatmap")
        heatmap_layout = QVBoxLayout(heatmap_group)
        heatmap_layout.setContentsMargins(4, 4, 4, 4)
        
        self.figure = Figure(figsize=(6, 5), facecolor='#000000')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#000000')
        
        heatmap_layout.addWidget(self.canvas)
        output_splitter.addWidget(heatmap_group)

        right_splitter.addWidget(output_splitter)
        splitter.addWidget(right_splitter)

        # Set ratio: Pool selector gets 1 part, Config & Analytics gets 3 parts
        splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)

        # Build initial number grid for br/lotofacil
        self.build_number_grid()
        self.on_wheel_type_changed(self.combo_wheel_type.currentText())

    def set_lottery(self, lottery_id: str):
        """Updates UI elements and layout when the active game swaps globally."""
        self.active_lottery = lottery_id
        self.pool_numbers.clear()
        self.key_numbers.clear()
        self.generated_tickets.clear()
        self.txt_output.clear()
        self.btn_send_to_verify.setEnabled(False)
        self.lbl_reduction_stats.setText(
            "Combinatorial Universe : 0\n"
            "Golden Reduced Bet Size : 0\n"
            "Bet Space Shrinkage    : 0.00%\n"
            "Estimated Capital Saved : $0.00"
        )
        self.clear_heatmap()
        self.build_number_grid()
        
        # Adjust default limits based on adapter rules
        try:
            rules = get_adapter(self.active_lottery).rules
            self.spin_pick.setValue(rules.pick_count)
            self.spin_pick.setRange(2, rules.number_range[1])
            self.spin_guarantee.setRange(2, rules.pick_count)
            self.spin_guarantee.setValue(rules.pick_count - 1)
            self.spin_if_hit.setRange(2, rules.number_range[1])
            self.spin_if_hit.setValue(rules.pick_count)
        except Exception:
            pass
            
        self.update_status_label()

    def build_number_grid(self):
        """Generates the grid of numeric ball buttons based on current lottery constraints."""
        # Clean current layout
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.buttons.clear()

        # Fetch range
        try:
            rules = get_adapter(self.active_lottery).rules
            min_n, max_n = rules.number_range
        except Exception:
            min_n, max_n = 1, 25

        cols = 5 if max_n <= 30 else 10
        
        for n in range(min_n, max_n + 1):
            btn = QPushButton(f"{n:02d}")
            btn.setCheckable(False)
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(self.get_ball_style(n))
            btn.clicked.connect(lambda checked=False, val=n: self.on_ball_clicked(val))
            
            row = (n - min_n) // cols
            col = (n - min_n) % cols
            self.grid_layout.addWidget(btn, row, col)
            self.buttons[n] = btn

    def get_ball_style(self, num: int) -> str:
        """Returns the neon style sheet string depending on number selection state."""
        if num in self.key_numbers:
            # Selected as Key (Purple Astro Violet theme)
            return """
                QPushButton {
                    background-color: #8a2be2;
                    color: #ffffff;
                    border: 2px solid #ffffff;
                    border-radius: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b15dff;
                }
            """
        elif num in self.pool_numbers:
            # Selected in Pool (Matrix Green theme)
            return """
                QPushButton {
                    background-color: #00ff41;
                    color: #000000;
                    border: 2px solid #00ff41;
                    border-radius: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00e63a;
                }
            """
        else:
            # Unselected default state (Sleek obsidian border-only)
            return """
                QPushButton {
                    background-color: #000000;
                    color: #00ff41;
                    border: 1px solid #333333;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                    border: 1px solid #00ff41;
                }
            """

    def on_ball_clicked(self, num: int):
        """Toggles a ball between selected, unselected, or key state depending on selection mode."""
        is_key_mode = self.radio_keys.isChecked()

        if is_key_mode:
            # Key Selection Logic
            if num in self.key_numbers:
                self.key_numbers.remove(num)
            else:
                if num in self.pool_numbers:
                    self.pool_numbers.remove(num)
                self.key_numbers.append(num)
        else:
            # Pool Selection Logic
            if num in self.pool_numbers:
                self.pool_numbers.remove(num)
            else:
                if num in self.key_numbers:
                    self.key_numbers.remove(num)
                self.pool_numbers.append(num)

        # Update styling of the clicked button
        if num in self.buttons:
            self.buttons[num].setStyleSheet(self.get_ball_style(num))

        self.update_status_label()

    def select_all_numbers(self):
        """Helper to quickly select the entire number pool."""
        try:
            rules = get_adapter(self.active_lottery).rules
            min_n, max_n = rules.number_range
        except Exception:
            min_n, max_n = 1, 25

        self.key_numbers.clear()
        self.pool_numbers = list(range(min_n, max_n + 1))
        
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))
            
        self.update_status_label()

    def clear_selection(self):
        """Clears all selections."""
        self.pool_numbers.clear()
        self.key_numbers.clear()
        
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))
            
        self.update_status_label()
        self.clear_heatmap()

    def update_status_label(self):
        self.lbl_status.setText(
            f"Pool: {len(self.pool_numbers)} selected | Keys: {len(self.key_numbers)} selected"
        )

    def on_wheel_type_changed(self, text: str):
        """Enables or disables sub-controls based on wheel type chosen."""
        is_abbrev = (text == "Abbreviated Wheel")
        is_key = (text == "Key Number Wheel")

        self.spin_guarantee.setEnabled(is_abbrev)
        self.spin_if_hit.setEnabled(is_abbrev)
        self.spin_max_tickets.setEnabled(is_abbrev)
        
        self.radio_keys.setEnabled(is_key)
        if not is_key:
            # If leaving key mode, change selection mode back to Pool
            self.radio_pool.setChecked(True)
            if self.key_numbers:
                # Merge key numbers back into pool for normal wheels
                self.pool_numbers.extend(self.key_numbers)
                self.pool_numbers = sorted(list(set(self.pool_numbers)))
                self.key_numbers.clear()
                self.build_number_grid()
                self.update_status_label()

    def generate_wheel(self):
        """Invokes combinatorial wheel algorithms on background thread or locally and prints lines."""
        wheel_type = self.combo_wheel_type.currentText()
        pick = self.spin_pick.value()
        
        # Combine pool and key numbers for generation validation
        total_pool = sorted(list(set(self.pool_numbers + self.key_numbers)))
        
        if not total_pool:
            QMessageBox.warning(self, "Empty Pool", "Please select some numbers from the grid first.")
            return

        if len(total_pool) < pick:
            QMessageBox.warning(
                self, "Pool Too Small", 
                f"Your selected pool has {len(total_pool)} numbers, but tickets require {pick} numbers."
            )
            return

        # Perform wheels logic
        try:
            tickets = []
            
            if wheel_type == "Full Wheel":
                tickets = generate_full_wheel(total_pool, pick)
            elif wheel_type == "Key Number Wheel":
                if not self.key_numbers:
                    QMessageBox.warning(self, "No Keys", "Please select some Key Numbers first (use Select Keys mode).")
                    return
                tickets = generate_key_wheel(total_pool, pick, self.key_numbers)
            elif wheel_type == "Abbreviated Wheel":
                g = self.spin_guarantee.value()
                m = self.spin_if_hit.value()
                cap = self.spin_max_tickets.value()
                
                if g > pick:
                    QMessageBox.warning(self, "Invalid Guarantee", "Guarantee match (t) cannot exceed ticket size (k).")
                    return
                if m > len(total_pool):
                    QMessageBox.warning(self, "Invalid Bounds", "If drawn count (m) cannot exceed selected pool size.")
                    return
                    
                tickets = generate_abbreviated_wheel(total_pool, pick, guarantee=g, max_tickets=cap)

            self.generated_tickets = tickets
            
            # Print output
            output_str = ""
            for idx, t in enumerate(tickets):
                output_str += f"Ticket #{idx+1:03d} ➔ " + " ".join(f"{x:02d}" for x in t) + "\n"
            self.txt_output.setText(output_str)

            # Update reduction analytics
            from math import comb
            universe = comb(len(total_pool), pick)
            reduced = len(tickets)
            shrinkage = (1.0 - (reduced / universe)) * 100 if universe > 0 else 0.0
            
            try:
                rules = get_adapter(self.active_lottery).rules
                price = rules.ticket_price
                curr = rules.currency
            except Exception:
                price = 3.0
                curr = "R$"
                
            saved_cost = (universe - reduced) * price
            
            self.lbl_reduction_stats.setText(
                f"Combinatorial Universe : {universe:,}\n"
                f"Golden Reduced Bet Size : {reduced:,} lines\n"
                f"Bet Space Shrinkage    : {shrinkage:.4f}%\n"
                f"Estimated Capital Saved : {curr} {saved_cost:,.2f}"
            )
            
            self.btn_send_to_verify.setEnabled(True)
            self.tickets_generated.emit(self.generated_tickets)

            # Plot live gap coverage heatmap!
            self.plot_gap_heatmap(total_pool, tickets)

        except Exception as e:
            logger.exception("Failed to generate wheel.")
            QMessageBox.critical(self, "Generation Failure", f"Failed to calculate combinations:\n{str(e)}")

    def plot_gap_heatmap(self, pool: list[int], tickets: list[list[int]]):
        """Renders the mutual coverage heatmap of the selected pool using WheelingEngine."""
        try:
            self.ax.clear()
            
            if not tickets:
                self.clear_heatmap()
                return

            # Shift numbers from [1..max] to [1..len(pool)] indices for get_gap_matrix
            # Let's map numbers to consecutive index values [1..len(pool)]
            pool_map = {n: i+1 for i, n in enumerate(pool)}
            shifted_tickets = []
            for t in tickets:
                shifted_tickets.append([pool_map[num] for num in t if num in pool_map])
            
            # Compute gap matrix using WheelingEngine
            n_pool = len(pool)
            engine = WheelingEngine(n_pool, self.spin_pick.value())
            gap_matrix = engine.get_gap_matrix(np.array(shifted_tickets))
            
            # Plot matrix in Matplotlib
            im = self.ax.imshow(gap_matrix, cmap='viridis', interpolation='nearest')
            
            # Set labels
            self.ax.set_xticks(range(n_pool))
            self.ax.set_yticks(range(n_pool))
            self.ax.set_xticklabels([f"{n:02d}" for n in pool], color='#008f11', fontsize=8, rotation=90)
            self.ax.set_yticklabels([f"{n:02d}" for n in pool], color='#008f11', fontsize=8)
            
            self.ax.set_title("Mutual Pair Coverage Matrix", color='#00ff41', fontsize=10)
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.exception("Failed to plot gap matrix heatmap.")

    def clear_heatmap(self):
        self.ax.clear()
        self.ax.text(0.5, 0.5, "No Active Wheel Coverage Data", 
                     color='#008f11', ha='center', va='center', transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def send_to_verification(self):
        """Sends generated tickets list to Verification Desk."""
        if not self.generated_tickets:
            return
        QMessageBox.information(
            self, "Tickets Shared", 
            f"Successfully shared {len(self.generated_tickets)} wheel tickets with the Verification Desk."
        )

    def get_generated_tickets(self) -> list[list[int]]:
        return self.generated_tickets
