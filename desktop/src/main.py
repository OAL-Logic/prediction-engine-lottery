import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Add project root to sys.path to enable importing from the 'desktop' package when run directly
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists() and str(user_site) not in sys.path:
    sys.path.insert(0, str(user_site))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QGroupBox, QLabel, QComboBox, QScrollArea, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup, QCheckBox, QSpinBox,
    QTabWidget, QMenu, QFileDialog, QDialog, QInputDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from engine.cli.utils import get_adapter
from engine.adapters.registry import registry

try:
    from desktop.src.theme.manager import ThemeManager
    from desktop.src.tabs.database import DatabaseTab
    from desktop.src.tabs.analysis import AnalysisTab
    from desktop.src.tabs.filters import FiltersTab
    from desktop.src.tabs.wheeling import WheelingTab
    from desktop.src.tabs.predict import PredictionTab
    from desktop.src.tabs.verification import VerificationTab
    from desktop.src.tabs.ev import ExpectedValueTab
    from desktop.src.tabs.telemetry import TelemetryTab
    from desktop.src.telemetry.manager import ThreadManager, ForecastJob, TrainJob, FormulaVerificationJob
    from desktop.src.telemetry.client import TelemetryClient
    from desktop.src.widgets.number_grid import NumberGrid
except ImportError as e:
    logging.debug("Legacy desktop tab import deferred: %s", e)

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
        # Floor beneath which the two-rail workspace (Pool Builder + Ticket Store)
        # and the Harmony Gate dock start clipping their controls.
        self.setMinimumSize(1000, 650)

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
        
        self.predict_tab.predict_button.clicked.connect(self.run_prediction_job_from_predict_center)
        self.predict_tab.train_button.clicked.connect(self.run_training_job)
        self.predict_tab.numbers_recommended.connect(self.handle_push_to_pool)
        self.analysis_tab.numbers_recommended.connect(self.handle_push_to_pool)
        self.verification_tab.run_leaderboard_button.clicked.connect(self.run_verification_job)
        self.telemetry_client.new_log.connect(self.telemetry_tab.append_log)

        # game_combo/db_tab.lottery_selector list every available game in registry
        # order, which won't generally put self.active_lottery's default first —
        # run one explicit sync so every child tab's starting state (NumberGrid
        # range included) actually matches self.active_lottery from the first
        # frame, the same way selecting a game from either combo would.
        self.change_global_lottery(self.active_lottery)

        # Start Websocket client background listener
        self.telemetry_client.start()

        # Apply Theme manager styles
        self.apply_theme()

        # Tabs that paint outside the global QSS cascade (per-widget setStyleSheet
        # calls, matplotlib canvases) own an apply_theme(colors) hook — wire them to
        # live theme swaps and prime them with whatever theme is active right now,
        # since the global QSS alone would otherwise leave them stuck on their
        # Forensic-Neon-era hardcoded defaults regardless of the selected theme.
        themed_tabs = [
            self.db_tab, self.analysis_tab, self.wheeling_tab, self.filters_tab,
            self.ev_tab, self.telemetry_tab, self.predict_tab, self.verification_tab,
        ]
        for tab in themed_tabs:
            self.theme_manager.theme_changed.connect(tab.apply_theme)
            tab.apply_theme(self.theme_manager.get_colors())

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
        self.game_combo.addItems([f"{g.name} ({g.id})" for g in registry.list_games(only_available=True)])
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
        btn_random = QPushButton("🎲 RANDOM")
        btn_clear = QPushButton("CLEAR")
        btn_all = QPushButton("ALL")

        btn_hot.clicked.connect(self.select_hot_numbers)
        btn_cold.clicked.connect(self.select_cold_numbers)
        btn_random.clicked.connect(self.select_random_numbers)
        btn_clear.clicked.connect(self.number_grid.clear_selection)
        btn_all.clicked.connect(self.number_grid.select_all)

        quick_select_layout.addWidget(btn_hot)
        quick_select_layout.addWidget(btn_cold)
        quick_select_layout.addWidget(btn_random)
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
        pick_last_drawn_action = qp_menu.addAction("Pick Last-X-Drawings Numbers...")
        pick_last_drawn_action.triggered.connect(self.select_last_drawn_numbers)
        self.btn_quick_pick.setMenu(qp_menu)
        pool_layout.addWidget(self.btn_quick_pick)

        # Save/Load Favorite Numbers ("Save and Load Your Own Favorite Number"
        # in the Lottery Studio manual) — a named pool selection, independent of the
        # Ticket Store's Lottery Studio .txt drawings import/export (DatabaseTab).
        favorites_layout = QHBoxLayout()
        btn_save_favorites = QPushButton("💾 SAVE FAVORITES")
        btn_load_favorites = QPushButton("📂 LOAD FAVORITES")
        btn_save_favorites.clicked.connect(self.save_favorite_numbers)
        btn_load_favorites.clicked.connect(self.load_favorite_numbers)
        favorites_layout.addWidget(btn_save_favorites)
        favorites_layout.addWidget(btn_load_favorites)
        pool_layout.addLayout(favorites_layout)

        # Counter Status Label
        self.lbl_pool_status = QLabel("Active Pool Size: 0 numbers selected")
        self.lbl_pool_status.setStyleSheet("font-weight: bold; font-size: 11px;")
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
        btn_optimize = QPushButton("⚡ OPTIMIZE (OVERLAP)")
        btn_optimize.setToolTip("Lottery Studio TopForm: eliminate redundant tickets with excessive number overlap.")
        btn_reduce = QPushButton("🎯 REDUCE (WRG)")
        btn_reduce.setToolTip("Greedy WRG set-cover reduction: drop tickets whose t-if-m coverage is already subsumed by others.")
        btn_check_draw = QPushButton("🔍 CHECK LAST DRAW")
        btn_check_draw.setToolTip("1-click quick verification of stored tickets against the most recent official draw.")
        btn_export = QPushButton("EXPORT TXT")
        btn_print = QPushButton("PRINT")

        btn_dedupe.clicked.connect(self.dedupe_tickets)
        btn_optimize.clicked.connect(self.optimize_ticket_store_overlap)
        btn_reduce.clicked.connect(self.reduce_ticket_store)
        btn_check_draw.clicked.connect(self.quick_check_last_draw)
        btn_export.clicked.connect(self.export_tickets)
        btn_print.clicked.connect(self.print_tickets)

        table_actions.addWidget(btn_dedupe)
        table_actions.addWidget(btn_optimize)
        table_actions.addWidget(btn_reduce)
        table_actions.addWidget(btn_check_draw)
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
        import_action = file_menu.addAction("📥 Import Lottery Studio TXT...")
        import_action.triggered.connect(self.import_drawings)
        export_action = file_menu.addAction("📤 Export Lottery Studio TXT...")
        export_action.triggered.connect(self.export_drawings)
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
        reduce_action = menu.addAction("🎯 Reduce (WRG Guarantee)...")
        export_action = menu.addAction("Export to TXT...")
        print_action = menu.addAction("Print Tickets")

        sort_action.triggered.connect(self.sort_tickets)
        dedupe_action.triggered.connect(self.dedupe_tickets)
        reduce_action.triggered.connect(self.reduce_ticket_store)
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
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Tickets", "tickets.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return
        try:
            if file_path.lower().endswith(".csv") or "CSV" in selected_filter:
                import csv
                with open(file_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Index", "Numbers", "Score"])
                    for row in range(self.ticket_table.rowCount()):
                        idx_item = self.ticket_table.item(row, 0)
                        comb_item = self.ticket_table.item(row, 1)
                        score_item = self.ticket_table.item(row, 2)
                        writer.writerow([
                            idx_item.text() if idx_item else "",
                            comb_item.text() if comb_item else "",
                            score_item.text() if score_item else "",
                        ])
            else:
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
        row_count = self.ticket_table.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "No Tickets", "Ticket store is empty. Nothing to print.")
            return

        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        print_dialog.setWindowTitle("Print Ticket Store")
        if print_dialog.exec() != QDialog.Accepted:
            return

        html = [
            f"<h2>Lottery Engine — Ticket Store ({self.active_lottery})</h2>",
            f"<p>Printed {datetime.now().strftime('%Y-%m-%d %H:%M')} — {row_count} ticket(s)</p>",
            "<table border='1' cellspacing='0' cellpadding='4' width='100%'>",
            "<tr><th>#</th><th>Combination</th><th>Score</th></tr>",
        ]
        for row in range(row_count):
            idx_item = self.ticket_table.item(row, 0)
            comb_item = self.ticket_table.item(row, 1)
            score_item = self.ticket_table.item(row, 2)
            html.append(
                f"<tr><td>{idx_item.text() if idx_item else ''}</td>"
                f"<td>{comb_item.text() if comb_item else ''}</td>"
                f"<td>{score_item.text() if score_item else ''}</td></tr>"
            )
        html.append("</table>")

        document = QTextDocument()
        document.setHtml("".join(html))
        document.print_(printer)

        self.telemetry_tab.append_log(f"Printed {row_count} tickets via system print dialog.", "INFO")

    def reduce_ticket_store(self):
        """Runs WheelingEngine's greedy WRG set-cover reduction (F10-F12 wheel-reduction
        parity) against the tickets currently sitting in the Ticket Store, dropping
        tickets whose t-if-m coverage is already subsumed by others kept."""
        tickets = []
        for row in range(self.ticket_table.rowCount()):
            item = self.ticket_table.item(row, 1)
            if item:
                nums = [int(x) for x in item.text().split() if x.isdigit()]
                if nums:
                    tickets.append(nums)

        if len(tickets) < 2:
            QMessageBox.warning(self, "Nothing to Reduce", "Ticket store needs at least 2 tickets to reduce.")
            return

        try:
            default_pick = get_adapter(self.active_lottery).rules.pick_count
        except Exception:
            default_pick = len(tickets[0])

        pool_size = len({n for t in tickets for n in t})
        m, ok = QInputDialog.getInt(
            self, "Reduce Ticket Store — Step 1/2",
            f"If-drawn count (m): how many numbers out of the store's {pool_size}-number pool\n"
            f"must be drawn to trigger the guarantee?",
            default_pick, 2, max(2, pool_size)
        )
        if not ok:
            return
        t, ok = QInputDialog.getInt(
            self, "Reduce Ticket Store — Step 2/2",
            f"Guarantee match (t): minimum matches guaranteed in at least one\nkept ticket, if {m} pool numbers are drawn.",
            max(2, min(default_pick - 1, m)), 2, m
        )
        if not ok:
            return

        self.telemetry_tab.append_log(
            f"Running WRG ticket store reduction on {len(tickets)} tickets ({t}-if-{m})...", "INFO"
        )

        from desktop.src.telemetry.manager import TicketStoreReductionJob
        job = self.thread_manager.start_job(
            "ticket_store_reduction",
            TicketStoreReductionJob(tickets, t, m)
        )
        if not job:
            return

        def on_finished(payload):
            if payload.get("status") != "success":
                QMessageBox.critical(self, "Reduction Failed", "Ticket store reduction failed.")
                return

            kept = payload.get("kept_tickets", [])
            original = payload.get("original_count", len(tickets))

            self.ticket_table.setRowCount(0)
            for idx, tk in enumerate(kept):
                t_str = " ".join(f"{num:02d}" for num in tk)
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

            self.telemetry_tab.append_log(
                f"Ticket store reduced: {original} -> {len(kept)} tickets (guarantee {t}-if-{m} preserved).",
                "RESONANCE",
            )
            QMessageBox.information(
                self, "Reduction Complete",
                f"Reduced {original} tickets down to {len(kept)}, preserving the {t}-if-{m} coverage guarantee."
            )

        def on_failed(title, msg, tb):
            QMessageBox.critical(self, title, msg)

        job.signals.finished.connect(on_finished)
        job.signals.failed.connect(on_failed)

    def optimize_ticket_store_overlap(self):
        """Lottery Studio TopForm parity: eliminates ticket redundancy by enforcing
        that no two tickets share more than M numbers."""
        from engine.modules.ticket_optimizer import same_number_reduction
        tickets = []
        for row in range(self.ticket_table.rowCount()):
            item = self.ticket_table.item(row, 1)
            if item:
                nums = [int(x) for x in item.text().split() if x.isdigit()]
                if nums:
                    tickets.append(nums)

        if len(tickets) < 2:
            QMessageBox.warning(self, "Nothing to Optimize", "Ticket store needs at least 2 tickets to optimize.")
            return

        k = len(tickets[0])
        max_overlap, ok = QInputDialog.getInt(
            self, "Ticket Optimizer (Lottery Studio TopForm)",
            f"Maximum allowed numbers shared between any two tickets (1 to {k - 1}):",
            min(3, k - 1), 1, k - 1
        )
        if not ok:
            return

        optimized = same_number_reduction(tickets, max_overlap=max_overlap)
        original_count = len(tickets)
        kept_count = len(optimized)
        pruned_count = original_count - kept_count

        self.ticket_table.setRowCount(0)
        for idx, t in enumerate(optimized):
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

        self.telemetry_tab.append_log(
            f"Ticket Optimizer: Kept {kept_count}/{original_count} tickets (pruned {pruned_count}, max overlap: {max_overlap}).", "SUCCESS"
        )
        QMessageBox.information(
            self, "Optimization Complete",
            f"Kept: {kept_count} tickets\nPruned: {pruned_count} redundant tickets\nOverlap constraint: ≤ {max_overlap} numbers."
        )

    def quick_check_last_draw(self):
        """1-click verification of all tickets in store against the latest official draw."""
        from engine.modules.storage import storage
        tickets = []
        for row in range(self.ticket_table.rowCount()):
            item = self.ticket_table.item(row, 1)
            if item:
                nums = [int(x) for x in item.text().split() if x.isdigit()]
                if nums:
                    tickets.append(nums)

        if not tickets:
            QMessageBox.warning(self, "No Tickets", "Generate or add tickets before running quick check.")
            return

        try:
            df = storage.load_draws(self.active_lottery, limit=1)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load latest draw: {e}")
            return

        if df.empty:
            QMessageBox.warning(self, "No Draws", f"No historical draws found for {self.active_lottery}.")
            return

        last_draw = df.iloc[0]
        draw_num = last_draw.get("draw_number", "Latest")
        winning_nums = set(last_draw["numbers"])

        hit_counts = {}
        for t in tickets:
            hits = len(set(t) & winning_nums)
            hit_counts[hits] = hit_counts.get(hits, 0) + 1

        summary_lines = [f"Official Draw #{draw_num} Winning Numbers: {sorted(list(winning_nums))}\n"]
        summary_lines.append("Audit Results:")
        for hits in sorted(hit_counts.keys(), reverse=True):
            summary_lines.append(f"  • {hits} Hits: {hit_counts[hits]} ticket(s)")

        summary_msg = "\n".join(summary_lines)
        self.telemetry_tab.append_log(f"Quick Check: {summary_msg}", "INFO")
        QMessageBox.information(self, f"Quick Check — Draw #{draw_num}", summary_msg)

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
    def import_drawings(self):
        self.db_tab.import_studio_txt()
        
    def export_drawings(self):
        self.db_tab.export_studio_txt()

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
        
        # Update NumberGrid bounds from the registry (covers every registered game,
        # including zero-indexed pools like Lotomania's 00-99 via number_range_min —
        # this used to be a 3-game if/elif that silently defaulted everything else
        # to a 25-number grid).
        game_def = registry.get_game(lottery_id)
        if game_def:
            self.number_grid.set_range(game_def.number_range_min, game_def.number_range_min + game_def.pool_size - 1)
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

    def select_random_numbers(self):
        """Lottery Studio manual: 'Random Select Numbers' — picks pick_count distinct
        random numbers from the active game's range."""
        import random
        try:
            rules = get_adapter(self.active_lottery).rules
            lo, hi = rules.number_range
            count = rules.pick_count
        except Exception:
            lo, hi = self.number_grid.min_number, self.number_grid.max_number
            count = min(6, hi - lo + 1)
        pool = list(range(lo, hi + 1))
        count = min(count, len(pool))
        picks = set(random.sample(pool, count))
        self.number_grid.select_numbers(picks)
        self.update_pool_counter(0, True)

    def select_last_drawn_numbers(self):
        """Lottery Studio manual: 'How to Quick to Pick Numbers' — 'Last x Drawings
        Numbers with one click'. Selects the union of every number drawn in
        the most recent N draws (N asked via a prompt), not a fixed count —
        matching the manual's own framing (a recency-based pool, not a
        precise pick_count-sized selection like HOT/COLD/RANDOM)."""
        from engine.modules.storage import storage

        n, ok = QInputDialog.getInt(
            self, "Last-X-Drawings Numbers",
            "Include numbers drawn in the last how many draws?",
            5, 1, 100
        )
        if not ok:
            return

        try:
            df = storage.load_draws(self.active_lottery, limit=n)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load recent draws:\n{str(e)}")
            return
        if df.empty:
            QMessageBox.warning(self, "No Draws", f"No historical draws found for {self.active_lottery}.")
            return

        recent_numbers = set()
        for nums in df["numbers"]:
            recent_numbers.update(nums)

        self.number_grid.select_numbers(recent_numbers)
        self.update_pool_counter(0, True)
        self.telemetry_tab.append_log(
            f"Selected {len(recent_numbers)} numbers drawn across the last {len(df)} draws.", "INFO"
        )

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

    # Save/Load Favorite Numbers
    def save_favorite_numbers(self):
        """Lottery Studio manual: 'Save and Load Your Own Favorite Number' — writes
        the active pool selection to a JSON file for later recall."""
        numbers = sorted(self.number_grid.selected_numbers)
        if not numbers:
            QMessageBox.warning(self, "Nothing to Save", "Select some numbers in the pool builder first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Favorite Numbers", f"{self.active_lottery.replace('/', '_')}_favorites.json",
            "Favorite Numbers (*.json);;All Files (*)"
        )
        if not file_path:
            return
        try:
            import json
            payload = {"lottery": self.active_lottery, "numbers": numbers}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self.telemetry_tab.append_log(f"Saved {len(numbers)} favorite numbers to {file_path}", "INFO")
            QMessageBox.information(self, "Favorites Saved", f"Saved {len(numbers)} numbers to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save favorites: {str(e)}")

    def load_favorite_numbers(self):
        """Lottery Studio manual: 'Save and Load Your Own Favorite Number' — restores
        a previously-saved pool selection into the active NumberGrid."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Favorite Numbers", "", "Favorite Numbers (*.json);;All Files (*)"
        )
        if not file_path:
            return
        try:
            import json
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            numbers = payload.get("numbers", [])
            if not isinstance(numbers, list) or not all(isinstance(n, int) for n in numbers):
                raise ValueError("File does not contain a valid list of favorite numbers.")

            saved_lottery = payload.get("lottery")
            if saved_lottery and saved_lottery != self.active_lottery:
                proceed = QMessageBox.question(
                    self, "Different Game",
                    f"These favorites were saved for {saved_lottery}, but the active game is "
                    f"{self.active_lottery}. Load anyway (out-of-range numbers will be dropped)?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if proceed != QMessageBox.Yes:
                    return

            self.number_grid.select_numbers(numbers)
            self.update_pool_counter(0, True)
            loaded_count = len(self.number_grid.selected_numbers)
            self.telemetry_tab.append_log(f"Loaded {loaded_count} favorite numbers from {file_path}", "INFO")
            QMessageBox.information(self, "Favorites Loaded", f"Loaded {loaded_count} numbers from:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load favorites: {str(e)}")

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

    def run_prediction_job_from_predict_center(self):
        """Predict Center's own trigger — unlike the Pool Builder's quick 'SMART
        SUGGEST' (run_prediction_job, which reads the left-rail radio buttons),
        this reads the Predict Center's Formula/Algorithm/Offset/Depth controls."""
        self.predict_tab.predict_button.setEnabled(False)
        self.predict_tab.progress_bar.setValue(0)
        self.predict_tab.status_label.setText("Engine State: SCANNED")

        lottery_id = self.active_lottery
        count = self.predict_tab.prediction_spin.value()
        strategy = self.predict_tab.selected_strategy()
        offset = self.predict_tab.offset_spin.value()
        depth = self.predict_tab.depth_spin.value()

        if self.predict_tab.gpu_checkbox.isChecked():
            self.telemetry_tab.append_log("CUDA GPU Acceleration flag activated.", "INFO")

        job = ForecastJob(
            lottery_id=lottery_id,
            strategies=[strategy],
            count=count,
            num_draws=depth,
            offset=offset,
        )

        started_job = self.thread_manager.start_job("predict", job)
        if started_job:
            started_job.signals.new_log.connect(self.telemetry_tab.append_log)
            started_job.signals.progress.connect(self.handle_job_progress)
            started_job.signals.finished.connect(self.handle_prediction_finished)
            started_job.signals.failed.connect(self.handle_job_failed)
        else:
            self.predict_tab.predict_button.setEnabled(True)
            self.predict_tab.status_label.setText("Engine State: IDLE")

    def handle_push_to_pool(self, numbers: list):
        """Predict Center's 'Push to Pool' — loads a recommended ticket into the
        main NumberGrid (colored as selected) and brings the cockpit to front."""
        self.number_grid.select_numbers(numbers)
        self.update_pool_counter(0, True)
        self.telemetry_tab.append_log(f"Pushed predicted ticket to Pool Builder: {numbers}", "RESONANCE")
        self.raise_()
        self.activateWindow()

    def run_verification_job(self):
        """Verification Desk's 'Formula Leaderboard' — walk-forward backtests
        the checked formulas and ranks them by win rate."""
        formulas = self.verification_tab.selected_formulas()
        if not formulas:
            QMessageBox.warning(self, "No Formulas Selected", "Check at least one formula to verify.")
            return

        depth = self.verification_tab.leaderboard_depth_spin.value()
        self.verification_tab.run_leaderboard_button.setEnabled(False)
        self.verification_tab.leaderboard_progress.setValue(0)
        self.verification_tab.leaderboard_status.setText(f"Verifying {len(formulas)} formula(s)...")

        job = FormulaVerificationJob(
            lottery_id=self.active_lottery,
            strategy_names=formulas,
            depth=depth,
        )

        started_job = self.thread_manager.start_job("verify_formulas", job)
        if not started_job:
            self.verification_tab.run_leaderboard_button.setEnabled(True)
            return

        started_job.signals.new_log.connect(self.telemetry_tab.append_log)
        started_job.signals.progress.connect(self.handle_leaderboard_progress)
        started_job.signals.finished.connect(self.handle_leaderboard_finished)
        started_job.signals.failed.connect(self.handle_leaderboard_failed)

    def handle_leaderboard_progress(self, val: int, msg: str):
        self.verification_tab.leaderboard_progress.setValue(val)
        self.verification_tab.leaderboard_status.setText(msg)

    def handle_leaderboard_finished(self, payload: dict):
        self.verification_tab.run_leaderboard_button.setEnabled(True)
        self.verification_tab.leaderboard_progress.setValue(0)
        self.verification_tab.leaderboard_status.setText(
            f"Ranked {len(payload.get('leaderboard', []))} formula(s) over the last "
            f"{self.verification_tab.leaderboard_depth_spin.value()} draws."
        )
        self.verification_tab.populate_leaderboard(payload)

    def handle_leaderboard_failed(self, title: str, message: str, traceback_str: str):
        self.verification_tab.run_leaderboard_button.setEnabled(True)
        self.verification_tab.leaderboard_progress.setValue(0)
        self.verification_tab.leaderboard_status.setText("Verification failed — see error dialog.")
        self.handle_job_failed(title, message, traceback_str)

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
        if hasattr(self.predict_tab, "pipeline_widget"):
            stage = min(5, max(1, (val // 20) + 1))
            self.predict_tab.pipeline_widget.set_pipeline_stage(stage, "running", msg)

    def handle_prediction_finished(self, result: dict):
        self.predict_tab.progress_bar.setValue(0)
        self.btn_smart_gen.setEnabled(True)
        self.predict_tab.predict_button.setEnabled(True)
        self.predict_tab.status_label.setText("Engine State: IDLE")
        if hasattr(self.predict_tab, "pipeline_widget"):
            self.predict_tab.pipeline_widget.set_pipeline_stage(6, "done", "Assets Verified")

        tickets = result.get("tickets", [])
        self.predict_tab.set_last_ticket(tickets[0] if tickets else [])

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
        # Applied on QApplication, not self: a QSS stylesheet set on a widget only
        # cascades to its non-window descendants. Every QDialog is a top-level
        # window regardless of its `parent=`, so a main-window-level stylesheet
        # never reached them — every dialog had to re-derive and re-apply its own
        # copy of the theme (background/text at minimum) to avoid rendering with
        # the raw OS widget style. QApplication-level styling reaches all
        # top-level windows, so new dialogs are themed for free.
        QApplication.instance().setStyleSheet(self.theme_manager.generate_stylesheet())
        colors = self.theme_manager.get_colors()
        self.number_grid.apply_theme(colors)
        self.lbl_pool_status.setStyleSheet(f"color: {colors['primary']}; font-weight: bold; font-size: 11px;")
        accent_hover = QColor(colors["accent"]).lighter(125).name()
        self.btn_run_prune.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent']};
                color: {colors['background']};
                font-weight: bold;
                font-size: 13px;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid {colors['accent']};
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
                border-color: {accent_hover};
            }}
        """)

    def change_theme(self, theme_name: str):
        """Persistent application theme swap & instant reload."""
        self.theme_manager.set_theme(theme_name)
        self.apply_theme()
        self.telemetry_tab.append_log(f"Visual identity re-aligned to theme: {theme_name}", "RESONANCE")

def main():
    app = QApplication(sys.argv)
    if "--legacy" in sys.argv:
        window = ProphetDashboard()
    else:
        from desktop.src.shell.main_window import CockpitMainWindow
        window = CockpitMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
