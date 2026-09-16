"""
Quick Calculator Widget 🧮
==========================
SamLotto's "PopupCalculator" equivalent: a small standalone dialog for
combinatorics (C(n,k)) and multi-bet cost math, so you don't have to leave
the desktop app to sanity-check "how many combinations is this pool, and
what would a multi-bet on it cost?"
"""

from __future__ import annotations

from math import comb

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QSpinBox, QDoubleSpinBox, QGroupBox
)
from PySide6.QtCore import Qt


def combination_cost(pool_size: int, pick_count: int, ticket_price: float = 0.0) -> dict:
    """Pure calculation, independent of Qt — easy to unit test."""
    if pool_size < 0 or pick_count < 0 or pick_count > pool_size:
        return {"combinations": 0, "cost": 0.0, "valid": False}
    combinations = comb(pool_size, pick_count)
    return {"combinations": combinations, "cost": combinations * ticket_price, "valid": True}


class QuickCalculatorDialog(QDialog):
    """Standalone popup: pick pool size / pick count / unit price, see C(n,k) and total cost live."""

    def __init__(self, parent=None, pool_size: int = 60, pick_count: int = 6, ticket_price: float = 0.0):
        super().__init__(parent)
        self.setWindowTitle("Quick Calculator")
        self.resize(360, 220)
        self.setStyleSheet("background-color: #121214; color: #E0E0E5;")

        self.pool_spin = QSpinBox()
        self.pool_spin.setRange(1, 999)
        self.pool_spin.setValue(pool_size)

        self.pick_spin = QSpinBox()
        self.pick_spin.setRange(1, 999)
        self.pick_spin.setValue(pick_count)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.0, 1_000_000.0)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(ticket_price)

        self.result_label = QLabel()
        self.result_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 14px; color: #00F0FF;")
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        form = QFormLayout()
        form.addRow("Pool size (n):", self.pool_spin)
        form.addRow("Pick count (k):", self.pick_spin)
        form.addRow("Ticket price:", self.price_spin)

        box = QGroupBox("C(n, k) combinatorics")
        box.setLayout(form)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(self.result_label)

        for w in (self.pool_spin, self.pick_spin, self.price_spin):
            w.valueChanged.connect(self.recalculate)
        self.recalculate()

    def recalculate(self) -> None:
        result = combination_cost(self.pool_spin.value(), self.pick_spin.value(), self.price_spin.value())
        if not result["valid"]:
            self.result_label.setText("Pick count cannot exceed pool size.")
            return
        self.result_label.setText(
            f"C({self.pool_spin.value()}, {self.pick_spin.value()}) = {result['combinations']:,} combinations\n"
            f"Total cost @ {self.price_spin.value():,.2f}/ticket = {result['cost']:,.2f}"
        )
