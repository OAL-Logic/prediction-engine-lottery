import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableView, QGroupBox, QFormLayout, QSpinBox, QDateEdit, 
    QLineEdit, QComboBox, QMessageBox, QHeaderView, QFileDialog
)
from PySide6.QtCore import Qt, QAbstractTableModel, QThread, Signal, QDate, QModelIndex
import pandas as pd
from datetime import datetime

from engine.modules.storage import storage
from engine.cli.utils import get_adapter
from engine.adapters.registry import registry

logger = logging.getLogger(__name__)

class DuckDBDrawsTableModel(QAbstractTableModel):
    """An editable Table Model for DuckDB draws supporting inline edits and CRUD operations."""
    data_mutated = Signal(str) # Emits active_lottery on mutation

    def __init__(self, lottery_id: str, df: pd.DataFrame = pd.DataFrame()):
        super().__init__()
        self.lottery_id = lottery_id
        self._df = df.copy()

    def rowCount(self, parent=None) -> int:
        return self._df.shape[0]

    def columnCount(self, parent=None) -> int:
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        val = self._df.iloc[row, col]
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            if isinstance(val, list):
                return ", ".join(map(str, val))
            if isinstance(val, datetime):
                return val.strftime("%Y-%m-%d")
            if pd.isna(val):
                return ""
            return str(val)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section: int, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                col_name = self._df.columns[section]
                return col_name.replace("_", " ").title()
            else:
                return str(section + 1)
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        # Draw ID (column 0) is read-only.
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        row = index.row()
        col = index.column()
        
        if col == 0:
            return False
            
        draw_id = int(self._df.iloc[row, 0])
        date_str = str(self._df.iloc[row, 1])
        
        numbers_val = self._df.iloc[row, 2]
        if isinstance(numbers_val, list):
            numbers = list(numbers_val)
        else:
            numbers = [int(x) for x in str(numbers_val).split(",") if x.strip()]
            
        bonus = []
        if self._df.shape[1] > 3:
            bonus_val = self._df.iloc[row, 3]
            if isinstance(bonus_val, list):
                bonus = list(bonus_val)
            elif pd.notna(bonus_val) and str(bonus_val).strip():
                bonus = [int(x) for x in str(bonus_val).split(",") if x.strip()]

        value_str = str(value).strip()
        
        # Load rules for range and format checks
        try:
            adapter = get_adapter(self.lottery_id)
            rules = adapter.rules
        except Exception:
            rules = None

        if col == 1:
            # Validate Date
            try:
                datetime.strptime(value_str, "%Y-%m-%d")
                date_str = value_str
            except ValueError:
                logger.warning(f"Invalid date format: {value_str}")
                return False
                
        elif col == 2:
            # Validate Main Numbers
            try:
                cleaned = value_str.replace(" ", "")
                if not cleaned:
                    return False
                new_numbers = [int(x) for x in cleaned.split(",") if x]
                
                # Apply rules validation
                if rules:
                    lo, hi = rules.number_range
                    if len(new_numbers) != rules.pick_count:
                        logger.warning(f"Winning numbers count must be exactly {rules.pick_count}")
                        return False
                    if any(n < lo or n > hi for n in new_numbers):
                        logger.warning(f"Numbers must be in range {lo}-{hi}")
                        return False
                numbers = new_numbers
            except ValueError:
                logger.warning(f"Invalid numbers format: {value_str}")
                return False
                
        elif col == 3:
            # Validate Bonus Numbers
            try:
                cleaned = value_str.replace(" ", "")
                if cleaned:
                    new_bonus = [int(x) for x in cleaned.split(",") if x]
                else:
                    new_bonus = []
                    
                # Apply rules validation
                if rules:
                    if rules.bonus_count > 0:
                        blo, bhi = rules.bonus_range
                        if len(new_bonus) != rules.bonus_count:
                            logger.warning(f"Bonus numbers count must be exactly {rules.bonus_count}")
                            return False
                        if any(n < blo or n > bhi for n in new_bonus):
                            logger.warning(f"Bonus numbers must be in range {blo}-{bhi}")
                            return False
                    elif rules.bonus_count == 0 and new_bonus:
                        logger.warning("Lottery does not support bonus numbers.")
                        return False
                bonus = new_bonus
            except ValueError:
                logger.warning(f"Invalid bonus numbers format: {value_str}")
                return False

        try:
            draw_payload = {
                "draw_id": draw_id,
                "draw_date": date_str,
                "numbers": numbers,
                "bonus": bonus
            }
            storage.save_draws(self.lottery_id, [draw_payload])
            
            # Update internal DataFrame
            if col == 1:
                self._df.iat[row, 1] = date_str
            elif col == 2:
                self._df.iat[row, 2] = numbers
            elif col == 3:
                self._df.iat[row, 3] = bonus
                
            self.dataChanged.emit(index, index, [role])
            self.data_mutated.emit(self.lottery_id)
            return True
        except Exception as e:
            logger.exception("Failed to save inline edit to database.")
            return False

    def load_data(self, df: pd.DataFrame):
        self.beginResetModel()
        self._df = df.copy()
        self.endResetModel()

    def insert_draw(self, draw_payload: dict) -> bool:
        try:
            storage.save_draws(self.lottery_id, [draw_payload])
            draw_id = draw_payload["draw_id"]
            
            existing_indices = self._df.index[self._df["draw_id"] == draw_id].tolist()
            row_dict = {
                "draw_id": draw_id,
                "draw_date": draw_payload["draw_date"],
                "numbers": draw_payload["numbers"]
            }
            if "bonus" in self._df.columns:
                row_dict["bonus"] = draw_payload.get("bonus", [])
                
            if existing_indices:
                row_idx = existing_indices[0]
                for col_name, val in row_dict.items():
                    self._df.at[row_idx, col_name] = val
                self.dataChanged.emit(self.index(row_idx, 0), self.index(row_idx, self.columnCount() - 1))
            else:
                self.beginResetModel()
                new_row_df = pd.DataFrame([row_dict])
                self._df = pd.concat([self._df, new_row_df], ignore_index=True)
                self._df = self._df.sort_values("draw_id", ascending=False).reset_index(drop=True)
                self.endResetModel()
                
            self.data_mutated.emit(self.lottery_id)
            return True
        except Exception as e:
            logger.exception("Failed to insert/update draw record.")
            return False

    def remove_draw(self, row_idx: int) -> bool:
        if not (0 <= row_idx < self._df.shape[0]):
            return False
            
        draw_id = int(self._df.iloc[row_idx, 0])
        try:
            if storage.use_duckdb:
                import duckdb
                with duckdb.connect(str(storage.db_path)) as con:
                    con.execute(
                        "DELETE FROM draws WHERE lottery_id = ? AND draw_id = ?",
                        [self.lottery_id, draw_id]
                    )
            self.beginRemoveRows(QModelIndex(), row_idx, row_idx)
            self._df = self._df.drop(self._df.index[row_idx]).reset_index(drop=True)
            self.endRemoveRows()
            self.data_mutated.emit(self.lottery_id)
            return True
        except Exception as e:
            logger.exception("Failed to remove draw record.")
            return False

    def get_row_data(self, row_idx: int) -> dict | None:
        if 0 <= row_idx < self._df.shape[0]:
            return self._df.iloc[row_idx].to_dict()
        return None


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
        self.model = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 1. Header Control Panel
        header_layout = QHBoxLayout()
        
        self.lottery_selector = QComboBox()
        available_games = registry.list_games(only_available=True)
        self.lottery_selector.addItems([g.id for g in available_games] or ["br/lotofacil"])
        self.lottery_selector.currentTextChanged.connect(self.set_lottery)
        
        self.sync_button = QPushButton("⚡ FETCH ONLINE DRAWINGS")
        self.sync_button.clicked.connect(self.sync_online_draws)

        self.import_button = QPushButton("📥 IMPORT Lottery Studio .TXT")
        self.import_button.clicked.connect(self.import_studio_txt)

        self.export_button = QPushButton("📤 EXPORT Lottery Studio .TXT")
        self.export_button.clicked.connect(self.export_studio_txt)

        header_layout.addWidget(QLabel("Select Active Lottery:"))
        header_layout.addWidget(self.lottery_selector)
        header_layout.addSpacing(15)
        header_layout.addWidget(self.sync_button)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.import_button)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.export_button)
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
        self.save_button.clicked.connect(self.save_draw_record)

        self.delete_button = QPushButton("❌ DELETE SELECTED DRAW")
        self.delete_button.clicked.connect(self.delete_draw_record)
        
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addStretch()
        
        bottom_layout.addWidget(actions_group, stretch=1)
        
        layout.addLayout(bottom_layout)

        # Load initial database rows
        self.load_database()

    def apply_theme(self, colors: dict):
        """Repaints the buttons this tab styles directly (outside the global QSS
        cascade) with the active theme's tokens, so they track theme swaps
        instead of staying frozen on Forensic-Neon-era hex values."""
        self.sync_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['text_dim']};
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
        """)
        self.import_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['tab_bg']};
                color: {colors['primary']};
                font-weight: bold;
                padding: 6px 12px;
                border: 1px solid {colors['primary']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: {colors['background']};
            }}
        """)
        self.export_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['tab_bg']};
                color: {colors['warning']};
                font-weight: bold;
                padding: 6px 12px;
                border: 1px solid {colors['warning']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {colors['warning']};
                color: {colors['background']};
            }}
        """)
        self.save_button.setStyleSheet(f"padding: 8px; font-weight: bold; color: {colors['success']};")
        self.delete_button.setStyleSheet(f"padding: 8px; font-weight: bold; color: {colors['error']};")

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
                df_view = df_view.sort_values("draw_id", ascending=False).reset_index(drop=True)
            else:
                df_view = pd.DataFrame(columns=["draw_id", "draw_date", "numbers", "bonus"])

            if not hasattr(self, "model") or self.model is None:
                self.model = DuckDBDrawsTableModel(self.active_lottery, df_view)
                self.model.data_mutated.connect(self.on_data_mutated)
                self.table_view.setModel(self.model)
            else:
                self.model.lottery_id = self.active_lottery
                self.model.load_data(df_view)
                
            self.update_form_defaults()
        except Exception as e:
            logger.exception("Failed to load draws from database.")
            QMessageBox.critical(self, "Database Error", f"Failed to query DuckDB:\n{str(e)}")

    def update_form_defaults(self):
        """Populates form field default values, constraints, and range checks according to active rules."""
        try:
            adapter = get_adapter(self.active_lottery)
            rules = adapter.rules
        except Exception:
            rules = None

        if rules:
            lo, hi = rules.number_range
            pick = rules.pick_count
            self.txt_numbers.setPlaceholderText(
                f"e.g. {','.join(map(str, range(lo, lo + min(pick, 5))))}... (exactly {pick} numbers in range {lo}-{hi})"
            )
            
            if rules.bonus_count > 0:
                blo, bhi = rules.bonus_range
                bcount = rules.bonus_count
                self.txt_bonus.setEnabled(True)
                self.txt_bonus.setPlaceholderText(
                    f"e.g. {blo} (exactly {bcount} numbers in range {blo}-{bhi})"
                )
            else:
                self.txt_bonus.setEnabled(False)
                self.txt_bonus.setPlaceholderText("No bonus numbers for this lottery")
                self.txt_bonus.clear()

        # Set default next draw ID
        if hasattr(self, "model") and self.model is not None and not self.model._df.empty:
            max_id = int(self.model._df["draw_id"].max())
            self.spin_draw_id.setValue(max_id + 1)
        else:
            self.spin_draw_id.setValue(1)

    def on_data_mutated(self, lottery_id: str):
        """Slot triggered when the table model mutates data."""
        self.database_changed.emit(lottery_id)

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
                numbers_val = row_data["numbers"]
                if isinstance(numbers_val, list):
                    self.txt_numbers.setText(", ".join(map(str, numbers_val)))
                else:
                    self.txt_numbers.setText(str(numbers_val))
                
                if "bonus" in row_data and pd.notna(row_data["bonus"]):
                    bonus_val = row_data["bonus"]
                    if isinstance(bonus_val, list):
                        self.txt_bonus.setText(", ".join(map(str, bonus_val)))
                    else:
                        self.txt_bonus.setText(str(bonus_val))
                else:
                    self.txt_bonus.clear()
        except Exception:
            pass

    def save_draw_record(self):
        """Saves or updates a drawing row manually in the model."""
        try:
            draw_id = self.spin_draw_id.value()
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
            
            # Fetch rules for validation
            try:
                adapter = get_adapter(self.active_lottery)
                rules = adapter.rules
            except Exception:
                rules = None

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

            if rules:
                lo, hi = rules.number_range
                if len(numbers) != rules.pick_count:
                    QMessageBox.warning(self, "Validation Error", f"Winning numbers count must be exactly {rules.pick_count}.")
                    return
                if any(n < lo or n > hi for n in numbers):
                    QMessageBox.warning(self, "Validation Error", f"Balls must be in range {lo} to {hi}.")
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
                
                if rules and rules.bonus_count > 0:
                    blo, bhi = rules.bonus_range
                    if len(bonus) != rules.bonus_count:
                        QMessageBox.warning(self, "Validation Error", f"Bonus numbers count must be exactly {rules.bonus_count}.")
                        return
                    if any(n < blo or n > bhi for n in bonus):
                        QMessageBox.warning(self, "Validation Error", f"Bonus balls must be in range {blo} to {bhi}.")
                        return
            elif rules and rules.bonus_count > 0:
                QMessageBox.warning(self, "Validation Error", f"This lottery requires {rules.bonus_count} bonus ball(s).")
                return

            # Package payload
            draw_payload = {
                "draw_id": draw_id,
                "draw_date": date_str,
                "numbers": numbers,
                "bonus": bonus
            }
            
            success = self.model.insert_draw(draw_payload)
            if success:
                self.update_form_defaults()
                QMessageBox.information(self, "Success", f"Draw #{draw_id} saved successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save Draw #{draw_id} to model.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save record: {str(e)}")

    def delete_draw_record(self):
        """Deletes a selected drawing record using the model's remove_draw method."""
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
            success = self.model.remove_draw(row_idx)
            if success:
                self.update_form_defaults()
                QMessageBox.information(self, "Deleted", f"Draw #{draw_id} removed from engine storage.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete Draw #{draw_id} from model.")

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

    def import_studio_txt(self):
        """Launches QFileDialog to import drawings from a Lottery Studio .txt flat file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Lottery Studio TXT", "", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            # Load rules to know pick and bonus count
            adapter = get_adapter(self.active_lottery)
            rules = adapter.rules
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            from desktop.src.utils.converter import parse_studio_txt
            draws = parse_studio_txt(content, rules.pick_count, rules.bonus_count)
            
            if not draws:
                QMessageBox.warning(self, "Import Failed", "No valid draws were parsed from the file.")
                return

            # Save draws to storage
            storage.save_draws(self.active_lottery, draws)
            
            # Reload the database and model
            self.load_database()
            self.database_changed.emit(self.active_lottery)
            
            QMessageBox.information(
                self, "Import Success", 
                f"Successfully parsed and loaded {len(draws)} draws for {self.active_lottery} into the database!"
            )
        except Exception as e:
            logger.exception("Failed to import Lottery Studio file.")
            QMessageBox.critical(self, "Import Error", f"An error occurred while importing:\n{str(e)}")

    def export_studio_txt(self):
        """Launches QFileDialog to export drawings to a Lottery Studio .txt flat file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Lottery Studio TXT", f"{self.active_lottery.replace('/', '_')}_studio.txt", 
            "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            from desktop.src.utils.converter import export_duckdb_to_studio
            content = export_duckdb_to_studio(self.active_lottery)
            
            if not content:
                QMessageBox.warning(self, "Export Failed", "No drawings found in the database to export.")
                return

            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
                
            QMessageBox.information(
                self, "Export Complete", 
                f"Successfully exported {self.active_lottery} drawings to:\n{file_path}"
            )
        except Exception as e:
            logger.exception("Failed to export Lottery Studio file.")
            QMessageBox.critical(self, "Export Error", f"An error occurred while exporting:\n{str(e)}")

