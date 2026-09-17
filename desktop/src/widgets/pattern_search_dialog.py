"""
Pattern Search Dialog 🔎
========================
Desktop front-end for the `pattern-search` engine command: type a few
numbers, see every historical draw ranked by overlap, without leaving the
desktop app. SamLotto's "nsSearch" equivalent in dialog form.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QFormLayout
)
from PySide6.QtCore import Qt

from engine.cli.utils import get_adapter


def rank_by_overlap(df, query: set[int], min_overlap: int = 2) -> list[tuple]:
    """Pure ranking logic, shared with the CLI's pattern-search command."""
    matches = []
    for _, row in df.iterrows():
        drawn = set(row["numbers"])
        overlap = query & drawn
        if len(overlap) >= min_overlap:
            matches.append((row["draw_id"], row["date"], row["numbers"], len(overlap)))
    matches.sort(key=lambda m: (m[3], m[0]), reverse=True)
    return matches


class PatternSearchDialog(QDialog):
    def __init__(self, parent=None, lottery_id: str = "br/mega-sena"):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.setWindowTitle("Pattern Search")
        self.resize(560, 420)
        self.numbers_input = QLineEdit()
        self.numbers_input.setPlaceholderText("e.g. 3,7,12,24")

        self.min_overlap_spin = QSpinBox()
        self.min_overlap_spin.setRange(1, 20)
        self.min_overlap_spin.setValue(2)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.run_search)

        form = QFormLayout()
        form.addRow("Numbers:", self.numbers_input)
        form.addRow("Min overlap:", self.min_overlap_spin)

        self.status_label = QLabel("")
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Draw", "Date", "Numbers", "Overlap"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(search_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.table)

    def run_search(self) -> None:
        try:
            query = {int(x.strip()) for x in self.numbers_input.text().split(",") if x.strip()}
        except ValueError:
            self.status_label.setText("Enter comma-separated integers.")
            return
        if not query:
            self.status_label.setText("Enter at least one number.")
            return

        adapter = get_adapter(self.lottery_id)
        df = adapter.fetch()
        matches = rank_by_overlap(df, query, self.min_overlap_spin.value())

        self.table.setRowCount(len(matches))
        for i, (draw_id, date, numbers, overlap) in enumerate(matches):
            self.table.setItem(i, 0, QTableWidgetItem(str(draw_id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(date)[:10]))
            self.table.setItem(i, 2, QTableWidgetItem(str(list(numbers))))
            self.table.setItem(i, 3, QTableWidgetItem(str(overlap)))
        self.status_label.setText(f"{len(matches)} draw(s) matched at least {self.min_overlap_spin.value()} numbers.")
