import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableView, QGroupBox, QFormLayout, QSpinBox, QDateEdit, 
    QLineEdit, QComboBox, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QThread, Signal, QDate
import pandas as pd
from datetime import datetime

from engine.modules.storage import storage
from engine.cli.utils import get_adapter

logger = logging.getLogger(__name__)

class DataFrameTableModel(QAbstractTableModel):
    """A high-performance read-only Table Model for displaying Pandas DataFrames in QTableView."""
    def __init__(self, df: pd.DataFrame = pd.DataFrame()):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None) -> int:
        return self._df.shape[0]

    def columnCount(self, parent=None) -> int:
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            val = self._df.iloc[index.row(), index.column()]
            if isinstance(val, list):
                return ", ".join(map(str, val))
            if isinstance(val, datetime):
                return val.strftime("%Y-%m-%d")
            return str(val)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section: int, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # Custom friendly column names
                col_name = self._df.columns[section]
                return col_name.replace("_", " ").title()
            else:
                return str(section + 1)
        return None

    def get_row_data(self, row_idx: int) -> dict | None:
        if 0 <= row_idx < self._df.shape[0]:
            return self._df.iloc[row_idx].to_dict()
        return None


class FetchWorker(QThread):
    """Background worker thread to fetch drawings without locking the GUI thread."""
    finished = Signal(bool, str)

    def __init__(self, lottery_id: str):
        super().__init__()
        self.lottery_id = lottery_id

    def run(self):
        try:
            adapter = get_adapter(self.lottery_id)
            df = adapter.fetch()
            if df.empty:
                self.finished.emit(False, "No drawings were returned by the update servers.")
            else:
                self.finished.emit(True, f"Successfully loaded {len(df)} drawings!")
        except Exception as e:
            logger.exception("Failed to fetch drawings online.")
            self.finished.emit(False, f"Error: {str(e)}")


class DatabaseTab(QWidget):
    """Graphical cockpit tab to view, edit, and sync the historical drawings database."""
    
    # Broadcast when database gets modified so other tabs can refresh
    database_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 1. Header Control Panel
        header_layout = QHBoxLayout()
        
        self.lottery_selector = QComboBox()
        self.lottery_selector.addItems(["br/lotofacil", "br/mega-sena", "us/powerball"])
        self.lottery_selector.currentTextChanged.connect(self.set_lottery)
        
        self.sync_button = QPushButton("⚡ FETCH ONLINE DRAWINGS")
        self.sync_button.setStyleSheet("""
            QPushButton {
                background-color: #008f11;
                color: #ffffff;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #000000;
            }
        """)
        self.sync_button.clicked.connect(self.sync_online_draws)
        
        header_layout.addWidget(QLabel("Select Active Lottery:"))
        header_layout.addWidget(self.lottery_selector)
        header_layout.addSpacing(15)
        header_layout.addWidget(self.sync_button)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        # 2. Main High-Density Analytical Grid
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.selectionModel()
        self.table_view.clicked.connect(self.row_selected)
        
        layout.addWidget(self.table_view, stretch=3)

        # 3. Manual Drawing Manager Panel
        bottom_layout = QHBoxLayout()
        
        # 3.1 Insert / Edit Form
        form_group = QGroupBox("Manual Draw Entry Manager")
        form_layout = QFormLayout(form_group)
        
        self.spin_draw_id = QSpinBox()
        self.spin_draw_id.setRange(1, 999999)
        self.spin_draw_id.setValue(1)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        self.txt_numbers = QLineEdit()
        self.txt_numbers.setPlaceholderText("e.g. 1, 2, 3, 4, 5... (separated by commas)")
        
        self.txt_bonus = QLineEdit()
        self.txt_bonus.setPlaceholderText("Optional (e.g. 7)")
        
        form_layout.addRow("Draw Number ID:", self.spin_draw_id)
        form_layout.addRow("Draw Date:", self.date_edit)
        form_layout.addRow("Winning Balls:", self.txt_numbers)
        form_layout.addRow("Bonus Balls:", self.txt_bonus)
        
        bottom_layout.addWidget(form_group, stretch=2)

        # 3.2 Action Commands
        actions_group = QGroupBox("Command Execution")
        actions_layout = QVBoxLayout(actions_group)
        
        self.save_button = QPushButton("💾 SAVE / UPDATE DRAW")
        self.save_button.setStyleSheet("padding: 8px; font-weight: bold; color: #00ff41;")
        self.save_button.clicked.connect(self.save_draw_record)
        
        self.delete_button = QPushButton("❌ DELETE SELECTED DRAW")
        self.delete_button.setStyleSheet("padding: 8px; font-weight: bold; color: #ff3b30;")
        self.delete_button.clicked.connect(self.delete_draw_record)
        
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addStretch()
        
        bottom_layout.addWidget(actions_group, stretch=1)
        
        layout.addLayout(bottom_layout)

        # Load initial database rows
        self.load_database()

    def set_lottery(self, lottery_id: str):
        self.active_lottery = lottery_id
        self.load_database()

    def load_database(self):
        """Loads drawings from DuckDB and displays them in the table view."""
        try:
            df = storage.load_draws(self.active_lottery)
            if not df.empty:
                # Select clean columns for visualization
                view_cols = ["draw_id", "draw_date", "numbers"]
                if "bonus" in df.columns:
                    view_cols.append("bonus")
                df_view = df[view_cols].copy()
                df_view = df_view.sort_values("draw_id", ascending=False)
            else:
                df_view = pd.DataFrame(columns=["draw_id", "draw_date", "numbers", "bonus"])

            self.model = DataFrameTableModel(df_view)
            self.table_view.setModel(self.model)
        except Exception as e:
            logger.exception("Failed to load draws from database.")
            QMessageBox.critical(self, "Database Error", f"Failed to query DuckDB:\n{str(e)}")

    def row_selected(self, index):
        """Pre-populates the input form when a table row is clicked."""
        try:
            row_data = self.model.get_row_data(index.row())
            if row_data:
                self.spin_draw_id.setValue(int(row_data["draw_id"]))
                
                # Parse date
                date_str = str(row_data["draw_date"])
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                self.date_edit.setDate(QDate(dt.year, dt.month, dt.day))
                
                # Parse numbers
                self.txt_numbers.setText(str(row_data["numbers"]))
                
                if "bonus" in row_data and pd.notna(row_data["bonus"]):
                    self.txt_bonus.setText(str(row_data["bonus"]))
                else:
                    self.txt_bonus.clear()
        except Exception:
            pass

    def save_draw_record(self):
        """Saves or updates a drawing row manually in the storage engine."""
        try:
            draw_id = self.spin_draw_id.value()
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
            
            # Parse main numbers
            num_raw = self.txt_numbers.text().replace(" ", "")
            if not num_raw:
                QMessageBox.warning(self, "Validation Error", "Winning balls list cannot be empty.")
                return
            
            try:
                numbers = [int(x) for x in num_raw.split(",") if x]
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Balls must be integers separated by commas.")
                return

            # Parse bonus numbers
            bonus = []
            bonus_raw = self.txt_bonus.text().replace(" ", "")
            if bonus_raw:
                try:
                    bonus = [int(x) for x in bonus_raw.split(",") if x]
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", "Bonus balls must be integers separated by commas.")
                    return

            # Package and save
            draw_payload = {
                "draw_id": draw_id,
                "draw_date": date_str,
                "numbers": numbers,
                "bonus": bonus
            }
            
            storage.save_draws(self.active_lottery, [draw_payload])
            self.load_database()
            self.database_changed.emit(self.active_lottery)
            
            QMessageBox.information(self, "Success", f"Draw #{draw_id} saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save record: {str(e)}")

    def delete_draw_record(self):
        """Deletes a selected drawing record from the DuckDB table."""
        # Retrieve selected row
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Selection Required", "Please click a row in the table first.")
            return

        row_idx = selected[0].row()
        row_data = self.model.get_row_data(row_idx)
        if not row_data:
            return

        draw_id = int(row_data["draw_id"])
        
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to permanently delete Draw #{draw_id} from {self.active_lottery} history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Remove from database
                if storage.use_duckdb:
                    import duckdb
                    with duckdb.connect(str(storage.db_path)) as con:
                        con.execute(
                            "DELETE FROM draws WHERE lottery_id = ? AND draw_id = ?",
                            [self.active_lottery, draw_id]
                        )
                # Note: For partition files or JSON cache, a full storage.export_to_json or clean cache rewrite can occur.
                # To maintain consistency, we reload the database:
                self.load_database()
                self.database_changed.emit(self.active_lottery)
                QMessageBox.information(self, "Deleted", f"Draw #{draw_id} removed from engine storage.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {str(e)}")

    def sync_online_draws(self):
        """Starts background worker thread to sync newest drawings online."""
        self.sync_button.setEnabled(False)
        self.sync_button.setText("⚡ SYNCHRONISING...")
        
        self.worker = FetchWorker(self.active_lottery)
        self.worker.finished.connect(self.on_sync_finished)
        self.worker.start()

    def on_sync_finished(self, success: bool, message: str):
        self.sync_button.setEnabled(True)
        self.sync_button.setText("⚡ FETCH ONLINE DRAWINGS")
        
        if success:
            QMessageBox.information(self, "Synchronization Complete", message)
            self.load_database()
            self.database_changed.emit(self.active_lottery)
        else:
            QMessageBox.warning(self, "Synchronization Failed", f"Could not sync with Caixa/Powerball:\n{message}")
