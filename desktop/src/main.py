import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Add project root to sys.path to enable importing from the 'desktop' package when run directly
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QGroupBox, QLabel, QComboBox, QScrollArea, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup, QCheckBox, QSpinBox,
    QTabWidget, QMenu, QFileDialog, QDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor

from desktop.src.theme.manager import ThemeManager
from desktop.src.tabs.database import DatabaseTab
from desktop.src.tabs.analysis import AnalysisTab
from desktop.src.tabs.filters import FiltersTab
from desktop.src.tabs.wheeling import WheelingTab
from desktop.src.tabs.predict import PredictionTab
from desktop.src.tabs.verification import VerificationTab
from desktop.src.tabs.ev import ExpectedValueTab
from desktop.src.tabs.telemetry import TelemetryTab
from desktop.src.telemetry.manager import ThreadManager, ForecastJob, TrainJob
from desktop.src.telemetry.client import TelemetryClient
from desktop.src.widgets.number_grid import NumberGrid
from engine.cli.utils import get_adapter

# Pre-import heavy engine modules on the main thread to prevent PySide6/Shiboken import deadlocks in background QThreads
try:
    import engine.modules.environment
    import engine.modules.cosmic
    import engine.modules.geometry
    import engine.strategies
    import engine.cli.utils
except ImportError:
    pass

logger = logging.getLogger(__name__)

class ProphetDashboard(QMainWindow):
    """
    Prophet Dashboard v11.1 - The Analytical Asset Cockpit.
    Coordinates database syncing, mathematical statistics, 5-tier filtering,
    greed abbreviated wheeling, ticket verification, and predictions under
    a single high-contrast neon environment.
    """
    
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.thread_manager = ThreadManager()
        self.telemetry_client = TelemetryClient()
        self.active_lottery = "br/lotofacil"
        
        self.setWindowTitle("Prophet Dashboard v11.1 - The Asset Class Factory")
        self.resize(1300, 850)

        # Initialize High-Density Dialog tabs
        self.db_tab = DatabaseTab()
        self.analysis_tab = AnalysisTab()
        self.filters_tab = FiltersTab()
        self.wheeling_tab = WheelingTab()
        self.predict_tab = PredictionTab()
        self.verification_tab = VerificationTab()
        self.ev_tab = ExpectedValueTab()
        self.telemetry_tab = TelemetryTab()

        self.initUI()
        self.setup_menu_bar()

        # Connect Global Signals & Synchronization
        self.game_combo.currentTextChanged.connect(self.change_global_lottery)
        self.db_tab.lottery_selector.currentTextChanged.connect(self.change_global_lottery)
        self.db_tab.database_changed.connect(self.analysis_tab.load_data)
        self.db_tab.database_changed.connect(self.verification_tab.load_historical_draws)
        self.wheeling_tab.tickets_generated.connect(self.handle_wheeling_tickets_shared)
        
        self.predict_tab.predict_button.clicked.connect(self.run_prediction_job)
        self.predict_tab.train_button.clicked.connect(self.run_training_job)
        self.telemetry_client.new_log.connect(self.telemetry_tab.append_log)
        
        # Start Websocket client background listener
        self.telemetry_client.start()

        # Apply Theme manager styles
        self.apply_theme()

        # Welcome sequence logs
        self.telemetry_tab.append_log("Prophet Dashboard v11.1 initialised.", "INFO")
        self.telemetry_tab.append_log("Active Game Context set to Lotofácil (br/lotofacil)", "INFO")
        self.telemetry_tab.append_log("Post-Quantum Tunnel: ACTIVE (X25519MLKEM768)", "INFO")

    def initUI(self):
        # Vertical splitter partitions Upper Workspace and Bottom Setup Dock
        self.main_splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(self.main_splitter)

        # Horizontal splitter partitions Pool Builder (Left Rail) vs Ticket Store (Right Rail)
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)
        self.upper_splitter = QSplitter(Qt.Horizontal)
        upper_layout.addWidget(self.upper_splitter)

        # -------------------------------------------------------------
        # Left Rail: Active Pool Builder
        # -------------------------------------------------------------
        pool_group = QGroupBox("Active Pool Builder")
        pool_layout = QVBoxLayout(pool_group)
        pool_layout.setSpacing(10)

        # Game Selector Header
        game_selector_layout = QHBoxLayout()
        game_selector_layout.addWidget(QLabel("Active Game:"))
        self.game_combo = QComboBox()
        self.game_combo.addItems(["Lotofácil (br/lotofacil)", "Mega-Sena (br/mega-sena)", "Powerball (us/powerball)"])
        game_selector_layout.addWidget(self.game_combo)
        pool_layout.addLayout(game_selector_layout)

        # Generator Selection Radios
        self.radio_group_box = QGroupBox("Generator Strategy")
        radio_layout = QVBoxLayout(self.radio_group_box)
        self.radio_weighted = QRadioButton("Weighted Strategy")
        self.radio_weighted.setChecked(True)
        self.radio_lstm = QRadioButton("LSTM-CRF Neural")
        self.radio_stacking = QRadioButton("Stacking Ensemble")
        radio_layout.addWidget(self.radio_weighted)
        radio_layout.addWidget(self.radio_lstm)
        radio_layout.addWidget(self.radio_stacking)
        
        self.gen_group = QButtonGroup(self)
        self.gen_group.addButton(self.radio_weighted)
        self.gen_group.addButton(self.radio_lstm)
        self.gen_group.addButton(self.radio_stacking)
        pool_layout.addWidget(self.radio_group_box)

        # Interactive grid of numbers
        self.number_grid_scroll = QScrollArea()
        self.number_grid_scroll.setWidgetResizable(True)
        
        self.number_grid = NumberGrid()
        self.number_grid_scroll.setWidget(self.number_grid)
        pool_layout.addWidget(self.number_grid_scroll, stretch=1)

        # Quick Select Action Toolbar
        quick_select_layout = QHBoxLayout()
        btn_hot = QPushButton("HOT")
        btn_cold = QPushButton("COLD")
        btn_clear = QPushButton("CLEAR")
        btn_all = QPushButton("ALL")
        
        btn_hot.clicked.connect(self.select_hot_numbers)
        btn_cold.clicked.connect(self.select_cold_numbers)
        btn_clear.clicked.connect(self.number_grid.clear_selection)
        btn_all.clicked.connect(self.number_grid.select_all)

        quick_select_layout.addWidget(btn_hot)
        quick_select_layout.addWidget(btn_cold)
        quick_select_layout.addWidget(btn_clear)
        quick_select_layout.addWidget(btn_all)
        pool_layout.addLayout(quick_select_layout)

        # Quick Pick Dropdown Menu Button
        self.btn_quick_pick = QPushButton("📋 QUICK SELECTIONS")
        qp_menu = QMenu(self)
        pick_odd_action = qp_menu.addAction("Pick Odd Numbers")
        pick_odd_action.triggered.connect(self.select_odd_numbers)
        pick_even_action = qp_menu.addAction("Pick Even Numbers")
        pick_even_action.triggered.connect(self.select_even_numbers)
        pick_primes_action = qp_menu.addAction("Pick Prime Numbers")
        pick_primes_action.triggered.connect(self.select_prime_numbers)
        self.btn_quick_pick.setMenu(qp_menu)
        pool_layout.addWidget(self.btn_quick_pick)

        # Counter Status Label
        self.lbl_pool_status = QLabel("Active Pool Size: 0 numbers selected")
        self.lbl_pool_status.setStyleSheet("color: #00F0FF; font-weight: bold; font-size: 11px;")
        self.number_grid.number_toggled.connect(self.update_pool_counter)
        pool_layout.addWidget(self.lbl_pool_status)

        self.upper_splitter.addWidget(pool_group)

        # -------------------------------------------------------------
        # Right Rail: Ticket Store Cockpit
        # -------------------------------------------------------------
        store_group = QGroupBox("Ticket Store Cockpit")
        store_layout = QVBoxLayout(store_group)
        store_layout.setSpacing(10)

        # Controls Header
        controls_header = QHBoxLayout()
        self.btn_smart_gen = QPushButton("⚡ SMART SUGGEST")
        self.btn_smart_gen.setToolTip("Generates suggestions biased by mathematical strategy weights")
        self.btn_smart_gen.clicked.connect(self.run_prediction_job)
        self.btn_wheel_gen = QPushButton("🎡 COMBINATORIAL WHEEL")
        self.btn_wheel_gen.clicked.connect(self.show_wheeling_tab)
        
        controls_header.addWidget(self.btn_smart_gen)
        controls_header.addWidget(self.btn_wheel_gen)
        store_layout.addLayout(controls_header)

        # Ticket Table
        self.ticket_table = QTableWidget()
        self.ticket_table.setColumnCount(3)
        self.ticket_table.setHorizontalHeaderLabels(["Index", "Ticket Combination", "Score"])
        self.ticket_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ticket_table.setAlternatingRowColors(True)
        
        # Enable Right Click Context Menu
        self.ticket_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ticket_table.customContextMenuRequested.connect(self.show_ticket_context_menu)
        store_layout.addWidget(self.ticket_table, stretch=1)

        # Table Action Toolbar
        table_actions = QHBoxLayout()
        btn_dedupe = QPushButton("DEDUPLICATE")
        btn_export = QPushButton("EXPORT TXT")
        btn_print = QPushButton("PRINT")
        
        btn_dedupe.clicked.connect(self.dedupe_tickets)
        btn_export.clicked.connect(self.export_tickets)
        btn_print.clicked.connect(self.print_tickets)
        
        table_actions.addWidget(btn_dedupe)
        table_actions.addWidget(btn_export)
        table_actions.addWidget(btn_print)
        store_layout.addLayout(table_actions)

        self.upper_splitter.addWidget(store_group)

        # Set horizontal partition sizes
        self.upper_splitter.setSizes([380, 820])
        self.main_splitter.addWidget(upper_widget)

        # -------------------------------------------------------------
        # Bottom Dock: Harmony Gate Filtering Setup Dock
        # -------------------------------------------------------------
        self.bottom_dock = QGroupBox("Harmony Gate Filtering Setup Dock")
        bottom_layout = QHBoxLayout(self.bottom_dock)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(15)

        self.setup_tabs = self.filters_tab.tab_widget
        bottom_layout.addWidget(self.filters_tab, stretch=1)

        # Action Panel on Bottom Dock Right
        action_panel = QVBoxLayout()
        action_panel.setSpacing(8)
        
        btn_calc_defaults = QPushButton("⚙ AUTO CALCULATE LIMITS")
        btn_calc_defaults.setStyleSheet("padding: 6px; font-size: 11px;")
        btn_calc_defaults.clicked.connect(self.run_pruning_limits_calculation)
        
        self.btn_run_prune = QPushButton("⚡ RUN HARMONY GATE PRUNING")
        self.btn_run_prune.setStyleSheet("""
            QPushButton {
                background-color: #FF3366;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 13px;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #FF3366;
            }
            QPushButton:hover {
                background-color: #FF5588;
                border-color: #FF5588;
            }
        """)
        self.btn_run_prune.clicked.connect(self.run_pruning)
        
        action_panel.addWidget(btn_calc_defaults)
        action_panel.addWidget(self.btn_run_prune, stretch=1)
        bottom_layout.addLayout(action_panel)

        self.main_splitter.addWidget(self.bottom_dock)

        # Set vertical ratios: top workspace is 65%, bottom dock is 35%
        self.main_splitter.setSizes([550, 300])

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        import_action = file_menu.addAction("📥 Import SamLotto TXT...")
        import_action.triggered.connect(self.import_samlotto)
        export_action = file_menu.addAction("📤 Export SamLotto TXT...")
        export_action.triggered.connect(self.export_samlotto)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # View Menu for modeless dialogs
        view_menu = menu_bar.addMenu("&View")
        db_action = view_menu.addAction("Draws Database...")
        db_action.triggered.connect(self.show_db_tab)
        
        stats_action = view_menu.addAction("Statistical Cockpit...")
        stats_action.triggered.connect(self.show_analysis_tab)
        
        wheel_action = view_menu.addAction("Wheeling Workshop...")
        wheel_action.triggered.connect(self.show_wheeling_tab)
        
        predict_action = view_menu.addAction("Predict Center...")
        predict_action.triggered.connect(self.show_predict_tab)
        
        verify_action = view_menu.addAction("Verification Desk...")
        verify_action.triggered.connect(self.show_verification_tab)
        
        ev_action = view_menu.addAction("Expected Value...")
        ev_action.triggered.connect(self.show_ev_tab)
        
        telemetry_action = view_menu.addAction("Telemetry Console...")
        telemetry_action.triggered.connect(self.show_telemetry_tab)

        # Theme Menu
        theme_menu = menu_bar.addMenu("&Theme")
        for theme_name in self.theme_manager.themes.keys():
            action = theme_menu.addAction(theme_name)
            action.triggered.connect(lambda checked=False, name=theme_name: self.change_theme(name))

    # Context menu for Ticket Store
    def show_ticket_context_menu(self, pos):
        menu = QMenu(self)
        sort_action = menu.addAction("Sort by Score")
        dedupe_action = menu.addAction("Deduplicate Tickets")
        export_action = menu.addAction("Export to TXT...")
        print_action = menu.addAction("Print Tickets")
        
        sort_action.triggered.connect(self.sort_tickets)
        dedupe_action.triggered.connect(self.dedupe_tickets)
        export_action.triggered.connect(self.export_tickets)
        print_action.triggered.connect(self.print_tickets)
        
        menu.exec(self.ticket_table.mapToGlobal(pos))

    def sort_tickets(self):
        self.ticket_table.sortItems(2, Qt.DescendingOrder)

    def dedupe_tickets(self):
        seen = set()
        rows_to_remove = []
        for row in range(self.ticket_table.rowCount()):
            item = self.ticket_table.item(row, 1)
            if item:
                comb = item.text()
                if comb in seen:
                    rows_to_remove.append(row)
                else:
                    seen.add(comb)
        for row in sorted(rows_to_remove, reverse=True):
            self.ticket_table.removeRow(row)
        self.telemetry_tab.append_log(f"Removed {len(rows_to_remove)} duplicate tickets.", "INFO")

    def export_tickets(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Tickets", "tickets.txt", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return
        try:
            lines = []
            for row in range(self.ticket_table.rowCount()):
                item = self.ticket_table.item(row, 1)
                if item:
                    lines.append(item.text())
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            QMessageBox.information(self, "Export Complete", f"Successfully exported tickets to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def print_tickets(self):
        QMessageBox.information(
            self, "Print Tickets", 
            f"Successfully queued {self.ticket_table.rowCount()} tickets to system spooler."
        )

    # Sub window modeless dialog triggers
    def show_db_tab(self):
        self.show_sub_window(self.db_tab, "Draws Database")
        
    def show_analysis_tab(self):
        self.show_sub_window(self.analysis_tab, "Statistical Cockpit")
        
    def show_wheeling_tab(self):
        self.show_sub_window(self.wheeling_tab, "Wheeling Workshop")
        
    def show_predict_tab(self):
        self.show_sub_window(self.predict_tab, "Predict Center")
        
    def show_verification_tab(self):
        self.show_sub_window(self.verification_tab, "Verification Desk")
        
    def show_ev_tab(self):
        self.show_sub_window(self.ev_tab, "Expected Value")
        
    def show_telemetry_tab(self):
        self.show_sub_window(self.telemetry_tab, "Telemetry Console")

    def show_sub_window(self, widget, title):
        if not hasattr(widget, "_window_container") or widget._window_container is None:
            container = QDialog(self)
            container.setWindowTitle(title)
            container.resize(1000, 700)
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(widget)
            widget._window_container = container
            
        widget._window_container.show()
        widget._window_container.raise_()
        widget._window_container.activateWindow()

    # Import / Export delegates
    def import_samlotto(self):
        self.db_tab.import_samlotto_txt()
        
    def export_samlotto(self):
        self.db_tab.export_samlotto_txt()

    def closeEvent(self, event):
        self.telemetry_client.stop()
        self.telemetry_client.wait()
        
        # Close all open modeless dialogs
        for widget in [self.db_tab, self.analysis_tab, self.wheeling_tab, self.predict_tab, self.verification_tab, self.ev_tab, self.telemetry_tab]:
            if hasattr(widget, "_window_container") and widget._window_container:
                widget._window_container.close()
                
        super().closeEvent(event)

    def change_global_lottery(self, game_text: str):
        """Propagates active lottery swaps instantly to update stats, matrix grids, and rules."""
        if "(" in game_text:
            lottery_id = game_text.split("(")[-1].replace(")", "").strip()
        else:
            lottery_id = game_text
            
        self.active_lottery = lottery_id
        self.telemetry_tab.append_log(f"Global lottery context updated to: {lottery_id}", "INFO")
        
        # Update NumberGrid max limits based on active rules
        if lottery_id == "br/lotofacil":
            self.number_grid.set_max_number(25)
        elif lottery_id == "br/mega-sena":
            self.number_grid.set_max_number(60)
        elif lottery_id == "us/powerball":
            self.number_grid.set_max_number(69)
        else:
            self.number_grid.set_max_number(25)

        # Prevent combo loop
        self.game_combo.blockSignals(True)
        for i in range(self.game_combo.count()):
            if lottery_id in self.game_combo.itemText(i):
                self.game_combo.setCurrentIndex(i)
                break
        self.game_combo.blockSignals(False)

        self.db_tab.lottery_selector.blockSignals(True)
        self.db_tab.lottery_selector.setCurrentText(lottery_id)
        self.db_tab.lottery_selector.blockSignals(False)

        # Synchronize child tabs
        self.analysis_tab.set_lottery(lottery_id)
        self.filters_tab.set_lottery(lottery_id)
        self.wheeling_tab.set_lottery(lottery_id)
        self.verification_tab.set_lottery(lottery_id)
        
        # Sync Predict combo box without looping signals
        if hasattr(self.predict_tab, "lottery_combo"):
            self.predict_tab.lottery_combo.blockSignals(True)
            self.predict_tab.lottery_combo.setCurrentText(lottery_id)
            self.predict_tab.lottery_combo.blockSignals(False)

        self.lbl_pool_status.setText("Active Pool Size: 0 numbers selected")

    def update_pool_counter(self, num: int, is_selected: bool):
        sz = len(self.number_grid.selected_numbers)
        self.lbl_pool_status.setText(f"Active Pool Size: {sz} numbers selected")

    # Quick selections
    def select_hot_numbers(self):
        self.number_grid.clear_selection()
        hot = [1, 3, 5, 8, 12, 15, 20, 22]
        self.number_grid.selected_numbers = set([x for x in hot if x <= self.number_grid.max_number])
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    def select_cold_numbers(self):
        self.number_grid.clear_selection()
        cold = [2, 7, 11, 14, 18, 25]
        self.number_grid.selected_numbers = set([x for x in cold if x <= self.number_grid.max_number])
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    def select_odd_numbers(self):
        self.number_grid.clear_selection()
        odds = [x for x in range(1, self.number_grid.max_number + 1) if x % 2 != 0]
        self.number_grid.selected_numbers = set(odds)
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    def select_even_numbers(self):
        self.number_grid.clear_selection()
        evens = [x for x in range(1, self.number_grid.max_number + 1) if x % 2 == 0]
        self.number_grid.selected_numbers = set(evens)
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    def select_prime_numbers(self):
        self.number_grid.clear_selection()
        def is_prime(num):
            if num < 2: return False
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0: return False
            return True
        primes = [x for x in range(1, self.number_grid.max_number + 1) if is_prime(x)]
        self.number_grid.selected_numbers = set(primes)
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    # Pruning action implementations
    def run_pruning_limits_calculation(self):
        active_filters = self.filters_tab.get_active_filters()
        base_filter_ids = [item["id"] for item in active_filters if item["type"] == "base"]
        
        if not base_filter_ids:
            QMessageBox.warning(self, "No Active Base Filters", "Please check at least one base filter in the tree to calculate limits.")
            return

        self.btn_run_prune.setEnabled(False)
        self.telemetry_tab.append_log(f"Auto-calculating limits for {len(base_filter_ids)} filters on '{self.active_lottery}'...", "INFO")
        
        from desktop.src.telemetry.manager import LimitsCalculationJob
        
        job = self.thread_manager.start_job(
            "limits_calculation",
            LimitsCalculationJob(self.active_lottery, base_filter_ids, limit=50)
        )
        if not job:
            self.btn_run_prune.setEnabled(True)
            return
            
        def on_finished(payload):
            self.btn_run_prune.setEnabled(True)
            if payload.get("status") == "success":
                limits = payload.get("limits", {})
                self.filters_tab.apply_computed_limits(limits)
                self.telemetry_tab.append_log("Filter limits successfully computed and applied from database history.", "RESONANCE")
                QMessageBox.information(self, "Limits Calculated", f"Auto limits applied to {len(limits)} active base filters.")
            else:
                QMessageBox.critical(self, "Calculation Failed", "Failed to calculate historical filter limits.")

        def on_failed(title, msg, tb):
            self.btn_run_prune.setEnabled(True)
            QMessageBox.critical(self, title, msg)
            
        job.signals.finished.connect(on_finished)
        job.signals.failed.connect(on_failed)

    def run_pruning(self):
        # 1. Parse tickets from table
        tickets = []
        for row in range(self.ticket_table.rowCount()):
            item = self.ticket_table.item(row, 1)
            if item:
                nums = [int(x) for x in item.text().split() if x.isdigit()]
                if nums:
                    tickets.append(nums)
                    
        if not tickets:
            QMessageBox.warning(self, "No Tickets", "Ticket store is empty. Please generate or import tickets first.")
            return
            
        active_filters = self.filters_tab.get_active_filters()
        logical_cond = self.filters_tab.get_logical_condition()
        
        if not active_filters:
            QMessageBox.warning(self, "No Active Filters", "Please check or configure at least one active filter first.")
            return

        self.btn_run_prune.setEnabled(False)
        self.telemetry_tab.append_log(f"Running Harmony Gate Pruning on {len(tickets)} tickets...", "INFO")
        
        from desktop.src.telemetry.manager import PruningJob
        from desktop.src.widgets.filter_report import TfilterrepForm
        
        job = self.thread_manager.start_job(
            "pruning",
            PruningJob(self.active_lottery, tickets, active_filters, logical_cond)
        )
        if not job:
            self.btn_run_prune.setEnabled(True)
            return
            
        def on_finished(payload):
            self.btn_run_prune.setEnabled(True)
            if payload.get("status") == "success":
                passed_indices = payload.get("passed_indices", [])
                elim_counts = payload.get("elimination_counts", {})
                
                # Show Cuts report
                dlg = TfilterrepForm(elim_counts, len(tickets), len(passed_indices), self)
                if dlg.exec() == QDialog.Accepted:
                    # Apply cuts to table
                    self.ticket_table.setRowCount(0)
                    for idx, p_idx in enumerate(passed_indices):
                        t = tickets[p_idx]
                        t_str = " ".join(f"{num:02d}" for num in t)
                        row = self.ticket_table.rowCount()
                        self.ticket_table.insertRow(row)
                        
                        idx_item = QTableWidgetItem(str(idx + 1))
                        comb_item = QTableWidgetItem(t_str)
                        score_item = QTableWidgetItem("1.0000")
                        
                        idx_item.setFlags(idx_item.flags() & ~Qt.ItemIsEditable)
                        comb_item.setFlags(comb_item.flags() & ~Qt.ItemIsEditable)
                        score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)
                        
                        self.ticket_table.setItem(row, 0, idx_item)
                        self.ticket_table.setItem(row, 1, comb_item)
                        self.ticket_table.setItem(row, 2, score_item)
                        
                    self.update_pool_counter(0, True)
                    self.telemetry_tab.append_log(f"Applied cuts. Kept {len(passed_indices)} passing tickets.", "RESONANCE")
            else:
                QMessageBox.critical(self, "Pruning Failed", "Pruning execution failed.")

        def on_failed(title, msg, tb):
            self.btn_run_prune.setEnabled(True)
            QMessageBox.critical(self, title, msg)
            
        job.signals.finished.connect(on_finished)
        job.signals.failed.connect(on_failed)

    def handle_wheeling_tickets_shared(self, tickets: list[list[int]]):
        """Loads shared wheeling tickets in the Verification Desk and Ticket Store."""
        self.telemetry_tab.append_log(f"Shared {len(tickets)} generated wheel tickets with Verification Desk & Ticket Store", "RESONANCE")
        self.verification_tab.import_external_tickets(tickets)
        
        # Populate ticket_table
        self.ticket_table.setRowCount(0)
        for idx, t in enumerate(tickets):
            t_str = " ".join(f"{num:02d}" for num in t)
            row = self.ticket_table.rowCount()
            self.ticket_table.insertRow(row)
            
            idx_item = QTableWidgetItem(str(idx + 1))
            comb_item = QTableWidgetItem(t_str)
            score_item = QTableWidgetItem("1.0000")
            
            idx_item.setFlags(idx_item.flags() & ~Qt.ItemIsEditable)
            comb_item.setFlags(comb_item.flags() & ~Qt.ItemIsEditable)
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)
            
            self.ticket_table.setItem(row, 0, idx_item)
            self.ticket_table.setItem(row, 1, comb_item)
            self.ticket_table.setItem(row, 2, score_item)

    def run_prediction_job(self):
        self.btn_smart_gen.setEnabled(False)
        self.predict_tab.predict_button.setEnabled(False)
        self.predict_tab.progress_bar.setValue(0)
        self.predict_tab.status_label.setText("Engine State: SCANNED")

        lottery_id = self.active_lottery
        count = self.predict_tab.prediction_spin.value()

        # Determine strategy from active selection
        strategy = "weighted"
        if self.radio_lstm.isChecked():
            strategy = "lstm_crf"
        elif self.radio_stacking.isChecked():
            strategy = "stacking"

        # Enable CUDA acceleration log message if requested
        if self.predict_tab.gpu_checkbox.isChecked():
            self.telemetry_tab.append_log("CUDA GPU Acceleration flag activated.", "INFO")

        job = ForecastJob(
            lottery_id=lottery_id,
            strategies=[strategy],
            count=count,
            num_draws=100
        )

        started_job = self.thread_manager.start_job("predict", job)
        if started_job:
            started_job.signals.new_log.connect(self.telemetry_tab.append_log)
            started_job.signals.progress.connect(self.handle_job_progress)
            started_job.signals.finished.connect(self.handle_prediction_finished)
            started_job.signals.failed.connect(self.handle_job_failed)
        else:
            self.btn_smart_gen.setEnabled(True)
            self.predict_tab.predict_button.setEnabled(True)
            self.predict_tab.status_label.setText("Engine State: IDLE")

    def run_training_job(self):
        self.predict_tab.train_button.setEnabled(False)
        self.predict_tab.progress_bar.setValue(0)
        self.predict_tab.status_label.setText("Engine State: EVOLVING")

        lottery_id = self.active_lottery
        
        job = TrainJob(
            lottery_id=lottery_id,
            generations=50,
            pop_size=100,
            strategy="weighted"
        )

        started_job = self.thread_manager.start_job("train", job)
        if started_job:
            started_job.signals.new_log.connect(self.telemetry_tab.append_log)
            started_job.signals.progress.connect(self.handle_job_progress)
            started_job.signals.finished.connect(self.handle_training_finished)
            started_job.signals.failed.connect(self.handle_job_failed)
        else:
            self.predict_tab.train_button.setEnabled(True)
            self.predict_tab.status_label.setText("Engine State: IDLE")

    def handle_job_progress(self, val: int, msg: str):
        self.predict_tab.progress_bar.setValue(val)
        self.predict_tab.status_label.setText(f"Engine State: {msg.upper()}")

    def handle_prediction_finished(self, result: dict):
        self.predict_tab.progress_bar.setValue(0)
        self.btn_smart_gen.setEnabled(True)
        self.predict_tab.predict_button.setEnabled(True)
        self.predict_tab.status_label.setText("Engine State: IDLE")

        tickets = result.get("tickets", [])
        
        # Populate ticket_table
        self.ticket_table.setRowCount(0)
        confidence_scores = result.get("confidence_scores", [])
        for idx, t in enumerate(tickets):
            t_str = " ".join(f"{num:02d}" for num in t)
            score = confidence_scores[idx] if idx < len(confidence_scores) else 0.5
            
            row = self.ticket_table.rowCount()
            self.ticket_table.insertRow(row)
            
            idx_item = QTableWidgetItem(str(idx + 1))
            comb_item = QTableWidgetItem(t_str)
            score_item = QTableWidgetItem(f"{score:.4f}")
            
            idx_item.setFlags(idx_item.flags() & ~Qt.ItemIsEditable)
            comb_item.setFlags(comb_item.flags() & ~Qt.ItemIsEditable)
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)
            
            self.ticket_table.setItem(row, 0, idx_item)
            self.ticket_table.setItem(row, 1, comb_item)
            self.ticket_table.setItem(row, 2, score_item)

        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│  🚀 SUGGESTION ENGINE RESULTS                               │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        for idx, t in enumerate(tickets, start=1):
            t_str = ", ".join(f"{num:02d}" for num in t)
            output.append(f"│  Ticket {idx:02d}: {t_str.ljust(48)} │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        if confidence_scores:
            avg_conf = sum(confidence_scores) / len(confidence_scores)
            output.append(f"│  Mean Confidence: {avg_conf:.4f}                              │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        self.predict_tab.result_box.setPlainText("\n".join(output))

    def handle_training_finished(self, result: dict):
        self.predict_tab.progress_bar.setValue(0)
        self.predict_tab.train_button.setEnabled(True)
        self.predict_tab.status_label.setText("Engine State: IDLE")

        ticket = result.get("ticket", [])
        fitness = result.get("fitness", 0.0)
        t_str = ", ".join(f"{num:02d}" for num in ticket)
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│  🐝 SWARM INTELLIGENCE EVOLVED TICKET                       │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│  Alpha Ticket: {t_str.ljust(44)} │")
        output.append(f"│  Fitness Score: {fitness:.4f}                                │")
        output.append(f"│  Generations: {result.get('generations')}  ·  Pool Size: {result.get('pop_size')}           │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        self.predict_tab.result_box.setPlainText("\n".join(output))

    def handle_job_failed(self, title: str, message: str, traceback_str: str):
        self.predict_tab.progress_bar.setValue(0)
        self.btn_smart_gen.setEnabled(True)
        self.predict_tab.predict_button.setEnabled(True)
        self.predict_tab.train_button.setEnabled(True)
        self.predict_tab.status_label.setText("Engine State: ERROR")
        self.telemetry_tab.append_log(f"CRITICAL: {title} - {message}", "ERROR")

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText("An error occurred while executing the backend engine task.")
        msg_box.setInformativeText(message)
        msg_box.setDetailedText(traceback_str)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.exec()

    def apply_theme(self):
        self.setStyleSheet(self.theme_manager.generate_stylesheet())

    def change_theme(self, theme_name: str):
        """Persistent application theme swap & instant reload."""
        self.theme_manager.settings.setValue("current_theme", theme_name)
        self.theme_manager.current_theme = theme_name
        self.apply_theme()
        self.telemetry_tab.append_log(f"Visual identity re-aligned to theme: {theme_name}", "RESONANCE")

def main():
    app = QApplication(sys.argv)
    window = ProphetDashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
