import sys
import logging
from pathlib import Path

# Add project root to sys.path to enable importing from the 'desktop' package when run directly
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PySide6.QtCore import Qt

from desktop.src.theme.manager import ThemeManager
from desktop.src.tabs.database import DatabaseTab
from desktop.src.tabs.analysis import AnalysisTab
from desktop.src.tabs.filters import FiltersTab
from desktop.src.tabs.wheeling import WheelingTab
from desktop.src.tabs.predict import PredictionTab
from desktop.src.tabs.verification import VerificationTab
from desktop.src.tabs.ev import ExpectedValueTab
from desktop.src.tabs.telemetry import TelemetryTab
from desktop.src.telemetry.manager import ThreadManager
from desktop.src.telemetry.client import TelemetryClient

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
        self.resize(1250, 850)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Setup Menu Bar with Theme Options
        menu_bar = self.menuBar()
        theme_menu = menu_bar.addMenu("&Theme")
        for theme_name in self.theme_manager.themes.keys():
            action = theme_menu.addAction(theme_name)
            action.triggered.connect(lambda checked=False, name=theme_name: self.change_theme(name))

        # Initialize High-Density Tabs
        self.db_tab = DatabaseTab()
        self.analysis_tab = AnalysisTab()
        self.filters_tab = FiltersTab()
        self.wheeling_tab = WheelingTab()
        self.predict_tab = PredictionTab()
        self.verification_tab = VerificationTab()
        self.ev_tab = ExpectedValueTab()
        self.telemetry_tab = TelemetryTab()

        # Add Tabs to Widget in Logical analytical workflow sequence
        self.tabs.addTab(self.db_tab, "Draws Database")
        self.tabs.addTab(self.analysis_tab, "Statistical Cockpit")
        self.tabs.addTab(self.filters_tab, "Harmony Gate Filters")
        self.tabs.addTab(self.wheeling_tab, "Wheeling Workshop")
        self.tabs.addTab(self.predict_tab, "Predict Center")
        self.tabs.addTab(self.verification_tab, "Verification Desk")
        self.tabs.addTab(self.ev_tab, "Expected Value")
        self.tabs.addTab(self.telemetry_tab, "Telemetry Console")

        # -------------------------------------------------------------
        # Connect Global Signals & Synchronization
        # -------------------------------------------------------------
        # 1. Global Lottery Context Sync (propagates from Draws Database dropdown)
        self.db_tab.lottery_selector.currentTextChanged.connect(self.change_global_lottery)
        
        # 2. Database Modification Signals (forces auto-refresh of statistical charts & lists)
        self.db_tab.database_changed.connect(self.analysis_tab.load_data)
        self.db_tab.database_changed.connect(self.verification_tab.load_historical_draws)

        # 3. Inter-Tab Wheeling Ticket Flow (Wheeling Workshop ➔ Verification Desk)
        self.wheeling_tab.tickets_generated.connect(self.handle_wheeling_tickets_shared)

        # 4. Telemetry Signals
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

    def closeEvent(self, event):
        self.telemetry_client.stop()
        self.telemetry_client.wait()
        super().closeEvent(event)

    def change_global_lottery(self, lottery_id: str):
        """Propagates active lottery swaps instantly to update stats, matrix grids, and rules."""
        self.active_lottery = lottery_id
        
        self.telemetry_tab.append_log(f"Global lottery context updated to: {lottery_id}", "INFO")
        
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

    def handle_wheeling_tickets_shared(self, tickets: list[list[int]]):
        """Loads shared wheeling tickets in the Verification Desk and navigates there immediately."""
        self.telemetry_tab.append_log(f"Shared {len(tickets)} generated wheel tickets with Verification Desk", "RESONANCE")
        self.verification_tab.import_external_tickets(tickets)
        
        # Smooth navigation swap to Verification Desk tab (Index 5)
        self.tabs.setCurrentWidget(self.verification_tab)

    def run_prediction_job(self):
        job = self.thread_manager.start_job("predict", "Ticket Generation Scan")
        if job:
            job.signals.new_log.connect(self.telemetry_tab.append_log)
            job.signals.progress.connect(self.predict_tab.progress_bar.setValue)
            job.signals.finished.connect(lambda: self.predict_tab.progress_bar.setValue(0))

    def run_training_job(self):
        job = self.thread_manager.start_job("train", "MARL Swarm Retraining")
        if job:
            job.signals.new_log.connect(self.telemetry_tab.append_log)
            job.signals.progress.connect(self.predict_tab.progress_bar.setValue)
            job.signals.finished.connect(lambda: self.predict_tab.progress_bar.setValue(0))

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
