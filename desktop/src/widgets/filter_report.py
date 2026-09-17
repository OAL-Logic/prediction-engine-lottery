import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox
)
from PySide6.QtCore import Qt

from desktop.src.theme.manager import THEMES, DEFAULT_THEME

class TfilterrepForm(QDialog):
    def __init__(self, elimination_counts: dict[str, int], total_tickets: int, passed_count: int, parent=None, colors: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Harmony Gate Pruning Cuts Report")
        self.resize(550, 400)
        self.eliminated_count = total_tickets - passed_count
        self.total_tickets = total_tickets
        self.passed_count = passed_count
        self.elimination_counts = elimination_counts
        self.colors = dict(colors) if colors else dict(THEMES[DEFAULT_THEME])

        self.initUI()

    def initUI(self):
        lay = QVBoxLayout(self)

        # Summary card
        summary_lbl = QLabel(
            f"<b>Total Tickets Processed:</b> {self.total_tickets}<br>"
            f"<b>Passed:</b> <font color='{self.colors['success']}'>{self.passed_count}</font><br>"
            f"<b>Eliminated:</b> <font color='{self.colors['error']}'>{self.eliminated_count}</font> "
            f"({(self.eliminated_count / max(1, self.total_tickets) * 100):.2f}%)"
        )
        summary_lbl.setStyleSheet("font-size: 13px; line-height: 1.4;")
        lay.addWidget(summary_lbl)
        
        # Table of cuts
        lay.addWidget(QLabel("<b>Detailed Cuts by Filter:</b>"))
        
        self.table = QTableWidget(len(self.elimination_counts), 3)
        self.table.setHorizontalHeaderLabels(["Filter", "Tickets Eliminated", "Elimination Rate"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        for idx, (fid, count) in enumerate(sorted(self.elimination_counts.items(), key=lambda x: x[1], reverse=True)):
            from engine.modules.filters import registry
            f = registry.get(fid)
            disp_name = f.display_name if f else fid
            
            rate_pct = (count / max(1, self.total_tickets)) * 100
            
            id_item = QTableWidgetItem(disp_name)
            count_item = QTableWidgetItem(str(count))
            rate_item = QTableWidgetItem(f"{rate_pct:.2f}%")
            
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)
            rate_item.setFlags(rate_item.flags() & ~Qt.ItemIsEditable)
            
            if count > 0:
                count_item.setForeground(Qt.yellow)
                rate_item.setForeground(Qt.yellow)
                
            self.table.setItem(idx, 0, id_item)
            self.table.setItem(idx, 1, count_item)
            self.table.setItem(idx, 2, rate_item)
            
        lay.addWidget(self.table)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText("Apply Cuts to Ticket Store")
        self.buttons.button(QDialogButtonBox.Cancel).setText("Dismiss")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        lay.addWidget(self.buttons)
