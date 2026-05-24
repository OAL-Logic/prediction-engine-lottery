import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableView, QGroupBox, QFormLayout, QComboBox, QTextEdit, 
    QHeaderView, QMessageBox, QSplitter, QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt, QAbstractTableModel, Signal
from PySide6.QtGui import QBrush, QColor

from engine.modules.storage import storage
from engine.cli.utils import get_adapter

logger = logging.getLogger(__name__)

class TicketVerificationModel(QAbstractTableModel):
    """High-performance custom table model displaying tickets and color-highlighting hits."""
    
    def __init__(self, tickets: list[list[int]] = None, winning_set: set[int] = None, rules = None):
        super().__init__()
        self.tickets = tickets or []
        self.winning_set = winning_set or set()
        self.rules = rules

    def rowCount(self, parent=None) -> int:
        return len(self.tickets)

    def columnCount(self, parent=None) -> int:
        if not self.tickets:
            return 0
        # Columns: Ticket ID, B1..BK, Hits, Payout
        return 1 + len(self.tickets[0]) + 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        ticket = self.tickets[row]
        k = len(ticket)

        if role == Qt.DisplayRole:
            if col == 0:
                return f"#{row + 1:03d}"
            elif 1 <= col <= k:
                return f"{ticket[col - 1]:02d}"
            elif col == k + 1:
                # Hits count
                matches = len(set(ticket) & self.winning_set)
                return f"{matches} hits"
            elif col == k + 2:
                # Payout estimation
                matches = len(set(ticket) & self.winning_set)
                payout = self.calculate_payout(matches)
                if payout > 0:
                    curr = self.rules.currency if self.rules else "$"
                    if curr == "BRL": curr = "R$"
                    return f"{curr} {payout:,.2f}"
                return "-"
                
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
            
        elif role == Qt.BackgroundRole:
            # Highlight ball numbers if they match the winning set
            if 1 <= col <= k:
                val = ticket[col - 1]
                if val in self.winning_set:
                    return QBrush(QColor("#00ff41")) # Neon Green hit
            elif col == k + 1:
                # Hit count column
                matches = len(set(ticket) & self.winning_set)
                if self.rules and matches in self.rules.prize_tiers:
                    return QBrush(QColor("#008f11")) # Dim green for winning tier
                    
        elif role == Qt.ForegroundRole:
            if 1 <= col <= k:
                val = ticket[col - 1]
                if val in self.winning_set:
                    return QBrush(QColor("#000000")) # High contrast black text on green
            elif col == k + 1:
                matches = len(set(ticket) & self.winning_set)
                if self.rules and matches in self.rules.prize_tiers:
                    return QBrush(QColor("#ffffff"))

        return None

    def headerData(self, section: int, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if not self.tickets:
                return None
            k = len(self.tickets[0])
            if section == 0:
                return "Ticket ID"
            elif 1 <= section <= k:
                return f"B{section}"
            elif section == k + 1:
                return "Match Hits"
            elif section == k + 2:
                return "Est. Payout"
        return None

    def calculate_payout(self, matches: int) -> float:
        """Calculates estimated average payouts based on specific lottery prize tier lists."""
        if not self.rules:
            return 0.0
        
        name = self.rules.name.lower()
        if "lotofácil" in name or "lotofacil" in name:
            payouts = {
                11: 6.0,
                12: 12.0,
                13: 30.0,
                14: 2000.0,
                15: 1500000.0
            }
            return payouts.get(matches, 0.0)
        elif "mega-sena" in name or "mega sena" in name:
            payouts = {
                4: 1000.0,
                5: 40000.0,
                6: 30000000.0
            }
            return payouts.get(matches, 0.0)
        else:
            # Fallback estimation for general lotteries based on proximity to jackpot
            diff = self.rules.pick_count - matches
            if diff == 0:
                return 1000000.0
            elif diff == 1:
                return 10000.0
            elif diff == 2:
                return 100.0
            elif diff == 3:
                return 10.0
            return 0.0


class VerificationTab(QWidget):
    """
    Verification Desk Cockpit Tab.
    Checks user pasted or wheel-generated combinations against historical drawings or custom targets.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self.tickets = []
        self.winning_numbers = set()
        
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Main horizontal splitter (Left Input Desk vs Right Live Audit View)
        splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Panel: Ticket Importer & Drawing Controls
        # -------------------------------------------------------------
        left_group = QGroupBox("Import & Target Control Desk")
        left_layout = QVBoxLayout(left_group)
        left_layout.setSpacing(12)

        # 1. Ticket Input Monospace
        input_desc = QLabel("Enter/paste your combinations (one ticket per line):")
        left_layout.addWidget(input_desc)

        self.txt_tickets_input = QTextEdit()
        self.txt_tickets_input.setPlaceholderText(
            "e.g.\n"
            "01 02 03 04 05 06 07 08 09 10 11 12 13 14 15\n"
            "02 03 04 05 06 07 08 09 10 11 12 13 14 15 16"
        )
        self.txt_tickets_input.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px;")
        self.txt_tickets_input.textChanged.connect(self.parse_input_tickets)
        left_layout.addWidget(self.txt_tickets_input, stretch=2)

        # 2. Winning Target Settings (Historical vs Manual)
        target_group = QGroupBox("Winning Target Selection")
        target_layout = QFormLayout(target_group)
        target_layout.setSpacing(8)

        self.chk_manual = QCheckBox("Manual Target Input Mode")
        self.chk_manual.stateChanged.connect(self.toggle_manual_mode)
        target_layout.addRow(self.chk_manual)

        # Dropdown for historical drawings (DuckDB)
        self.combo_draws = QComboBox()
        self.combo_draws.currentIndexChanged.connect(self.on_historical_draw_changed)
        target_layout.addRow("Select Historical Draw:", self.combo_draws)

        # Custom Manual Input Box
        self.txt_manual_numbers = QLineEdit()
        self.txt_manual_numbers.setPlaceholderText("e.g. 1, 2, 3, 4, 5...")
        self.txt_manual_numbers.setEnabled(False)
        self.txt_manual_numbers.textChanged.connect(self.parse_manual_numbers)
        target_layout.addRow("Manual Draw Numbers:", self.txt_manual_numbers)

        left_layout.addWidget(target_group, stretch=1)
        splitter.addWidget(left_group)

        # -------------------------------------------------------------
        # Right Panel: Verification Results Grid & ROI Auditor
        # -------------------------------------------------------------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Grid view for results
        grid_group = QGroupBox("High-Density Hit Auditor Matrix")
        grid_layout = QVBoxLayout(grid_group)
        grid_layout.setContentsMargins(6, 6, 6, 6)

        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setStyleSheet("QTableView { font-family: 'JetBrains Mono'; font-size: 11px; }")
        grid_layout.addWidget(self.table_view)

        right_layout.addWidget(grid_group, stretch=3)

        # ROI & Financial Payout Card
        self.payout_box = QGroupBox("Payout & ROI Summary Audit")
        self.payout_card_layout = QVBoxLayout(self.payout_box)
        
        self.lbl_payout_stats = QLabel(
            "Total Imported Tickets  : 0\n"
            "Total Capital Invested  : $0.00\n"
            "Total Dividends Returned : $0.00\n"
            "Net Yield (ROI %)       : 0.00% (IDLE)"
        )
        self.lbl_payout_stats.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold; color: #008f11;")
        self.payout_card_layout.addWidget(self.lbl_payout_stats)

        right_layout.addWidget(self.payout_box, stretch=1)

        splitter.addWidget(right_panel)

        # Ratio: 1 part left, 2 parts right
        splitter.setSizes([350, 850])
        main_layout.addWidget(splitter)

        # Load initial drawings history
        self.load_historical_draws()

    def set_lottery(self, lottery_id: str):
        """Updates the active lottery, reloads historical dropdown, and clears current matches."""
        self.active_lottery = lottery_id
        self.winning_numbers.clear()
        self.txt_manual_numbers.clear()
        self.txt_tickets_input.clear()
        self.tickets.clear()
        
        self.load_historical_draws()
        self.update_results_grid()

    def load_historical_draws(self):
        """Loads historical draws from DuckDB into the selection dropdown."""
        self.combo_draws.blockSignals(True)
        self.combo_draws.clear()
        
        try:
            df = storage.load_draws(self.active_lottery, limit=100)
            if not df.empty:
                df = df.sort_values("draw_id", ascending=False)
                for _, row in df.iterrows():
                    draw_id = row["draw_id"]
                    date_str = str(row["draw_date"])
                    numbers = row["numbers"]
                    
                    display_text = f"Draw #{draw_id:04d} ({date_str}) ➔ " + " ".join(f"{n:02d}" for n in numbers)
                    # Store draw numbers list in the item data slot
                    self.combo_draws.addItem(display_text, numbers)
            else:
                self.combo_draws.addItem("No draws in database", [])
        except Exception as e:
            logger.exception("Failed to load historical drawings list.")
            self.combo_draws.addItem("Error loading database", [])
            
        self.combo_draws.blockSignals(False)
        self.on_historical_draw_changed(self.combo_draws.currentIndex())

    def toggle_manual_mode(self, state: int):
        """Toggles manual target input box versus historical dropdown."""
        is_manual = (state == Qt.Checked or state == 2)
        self.combo_draws.setEnabled(not is_manual)
        self.txt_manual_numbers.setEnabled(is_manual)
        
        if is_manual:
            self.parse_manual_numbers(self.txt_manual_numbers.text())
        else:
            self.on_historical_draw_changed(self.combo_draws.currentIndex())

    def on_historical_draw_changed(self, index: int):
        """Fires when selected historical dropdown index alters, setting the active winning target."""
        if self.chk_manual.isChecked():
            return

        numbers = self.combo_draws.itemData(index)
        if isinstance(numbers, list):
            self.winning_numbers = set(numbers)
        else:
            self.winning_numbers = set()
            
        self.update_results_grid()

    def parse_manual_numbers(self, text: str):
        """Parses custom comma/space separated numbers as winning target."""
        if not self.chk_manual.isChecked():
            return

        try:
            cleaned = text.replace(",", " ").replace(";", " ")
            nums = [int(x) for x in cleaned.split() if x.isdigit()]
            self.winning_numbers = set(nums)
        except Exception:
            self.winning_numbers = set()
            
        self.update_results_grid()

    def import_external_tickets(self, tickets: list[list[int]]):
        """Dynamically loads a structured list of tickets (e.g. from Wheeling Workshop)."""
        self.tickets = tickets
        
        # Format list into text box for user feedback
        text = ""
        for t in tickets:
            text += " ".join(f"{x:02d}" for x in t) + "\n"
        
        self.txt_tickets_input.blockSignals(True)
        self.txt_tickets_input.setText(text)
        self.txt_tickets_input.blockSignals(False)
        
        self.update_results_grid()

    def parse_input_tickets(self):
        """Fires when tickets textarea changes, parsing string lines into structured list."""
        text = self.txt_tickets_input.toPlainText().strip()
        parsed_tickets = []
        
        if text:
            lines = text.split("\n")
            for l in lines:
                cleaned = l.replace(",", " ").replace(";", " ")
                nums = [int(x) for x in cleaned.split() if x.isdigit()]
                if nums:
                    parsed_tickets.append(sorted(nums))
                    
        self.tickets = parsed_tickets
        self.update_results_grid()

    def update_results_grid(self):
        """Re-binds the QTableView model and triggers financial calculations."""
        try:
            rules = get_adapter(self.active_lottery).rules
        except Exception:
            rules = None

        self.model = TicketVerificationModel(self.tickets, self.winning_numbers, rules)
        self.table_view.setModel(self.model)
        
        self.calculate_roi_summary(rules)

    def calculate_roi_summary(self, rules):
        """Calculates total investment, returns, net yield, and updates color-coded statistics card."""
        if not self.tickets:
            self.lbl_payout_stats.setText(
                "Total Imported Tickets  : 0\n"
                "Total Capital Invested  : $0.00\n"
                "Total Dividends Returned : $0.00\n"
                "Net Yield (ROI %)       : 0.00% (IDLE)"
            )
            self.lbl_payout_stats.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold; color: #008f11;")
            return

        total_tickets = len(self.tickets)
        
        if rules:
            price = rules.ticket_price
            curr = rules.currency
            if curr == "BRL": curr = "R$"
        else:
            price = 3.0
            curr = "$"

        total_investment = total_tickets * price
        total_payout = 0.0

        # Sum payouts across all tickets
        for t in self.tickets:
            matches = len(set(t) & self.winning_numbers)
            total_payout += self.model.calculate_payout(matches)

        net_yield = total_payout - total_investment
        roi_pct = (net_yield / total_investment) * 100 if total_investment > 0 else 0.0

        # Build card text
        stats_text = (
            f"Total Imported Tickets  : {total_tickets:,}\n"
            f"Total Capital Invested  : {curr} {total_investment:,.2f}\n"
            f"Total Dividends Returned : {curr} {total_payout:,.2f}\n"
            f"Net Yield (ROI %)       : {roi_pct:+.2f}% ({curr} {net_yield:+,.2f})"
        )
        self.lbl_payout_stats.setText(stats_text)

        # Style colors depending on net return (green for profit, red for loss, yellow for break-even)
        if net_yield > 0:
            # High profit neon green
            self.lbl_payout_stats.setStyleSheet(
                "font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold; color: #00ff41;"
            )
        elif net_yield < 0:
            # Loss signal red
            self.lbl_payout_stats.setStyleSheet(
                "font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold; color: #ff3131;"
            )
        else:
            # Equal / break even dim green
            self.lbl_payout_stats.setStyleSheet(
                "font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold; color: #008f11;"
            )
