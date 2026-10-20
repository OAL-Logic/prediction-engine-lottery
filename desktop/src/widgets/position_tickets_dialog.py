"""
Position Number Tickets Dialog 🎯
==================================
Lottery Studio's "Creating a Position Number Tickets" (its Build Tickets screen's
"Position" tab, alongside "Standard" and "Smart"): independently specify a
candidate-number list for each ticket position, then generate every valid
ticket from the Cartesian product of those lists (distinct numbers only,
sorted into the final ticket — position order is an input-organization
device here, not a constraint on the stored ticket). A different generation
mode from WheelingTab's pool-based Full/Abbreviated/Key wheels, launched
from it but not built on its pool-selection UI, since the input shape
(K independent lists, not one pool) doesn't fit that model.
"""

from __future__ import annotations

import logging
from itertools import product

from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QScrollArea, QWidget,
)

logger = logging.getLogger(__name__)

MAX_POSITION_COMBINATIONS = 200_000


class PositionTicketsSignals(QObject):
    finished = Signal(list)   # list of sorted, deduplicated ticket lists
    failed = Signal(str)


class PositionTicketsJob(QThread):
    """
    Cartesian product of K independently-chosen candidate lists (one per
    ticket position). Keeps only combinations where all K numbers are
    distinct, sorts each into the final ticket, and deduplicates — different
    position-to-number assignments can land on the same final set.
    """

    def __init__(self, position_candidates: list[list[int]], parent: QObject | None = None):
        super().__init__(parent)
        self.position_candidates = position_candidates
        self.signals = PositionTicketsSignals()

    def run(self) -> None:
        try:
            theoretical = 1
            for candidates in self.position_candidates:
                theoretical *= max(1, len(candidates))
            if theoretical > MAX_POSITION_COMBINATIONS:
                raise ValueError(
                    f"These position lists yield up to {theoretical:,} raw combinations, above the "
                    f"{MAX_POSITION_COMBINATIONS:,} safety cap. Use fewer candidates per position."
                )

            seen = set()
            tickets = []
            for combo in product(*self.position_candidates):
                if len(set(combo)) != len(combo):
                    continue  # same number picked for more than one position
                ticket = tuple(sorted(combo))
                if ticket not in seen:
                    seen.add(ticket)
                    tickets.append(list(ticket))

            self.signals.finished.emit(tickets)
        except Exception as exc:
            logger.exception("Position Tickets job failed.")
            self.signals.failed.emit(str(exc) or type(exc).__name__)


class PositionTicketsDialog(QDialog):
    """One row per ticket position, each an editable candidate-number list."""

    tickets_generated = Signal(list)

    def __init__(self, rules, parent=None):
        super().__init__(parent)
        self.rules = rules
        self.generated_tickets: list[list[int]] = []
        self._job = None

        self.setWindowTitle(f"🎯 Position Number Tickets — {rules.name}")
        self.resize(600, 650)

        layout = QVBoxLayout(self)
        hint = QLabel(
            f"Give each of the {rules.pick_count} positions its own candidate numbers "
            f"(comma-separated, within {rules.number_range}). Every valid combination — one "
            f"number per position, all distinct — becomes a ticket."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        form = QFormLayout(inner)
        self.position_edits: list[QLineEdit] = []
        lo, _ = rules.number_range
        for i in range(rules.pick_count):
            edit = QLineEdit()
            edit.setPlaceholderText("e.g. " + ", ".join(str(n) for n in range(lo, lo + 3)))
            self.position_edits.append(edit)
            form.addRow(f"Position {i + 1}:", edit)
        scroll.setWidget(inner)
        layout.addWidget(scroll, stretch=1)

        self.btn_generate = QPushButton("⚡ Generate Tickets")
        self.btn_generate.clicked.connect(self._generate)
        layout.addWidget(self.btn_generate)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Generated tickets will appear here...")
        layout.addWidget(self.output, stretch=1)

        self.lbl_summary = QLabel("")
        layout.addWidget(self.lbl_summary)

        self.btn_send = QPushButton("🛡️ Send to Ticket Store")
        self.btn_send.setEnabled(False)
        self.btn_send.clicked.connect(self._send_to_store)
        layout.addWidget(self.btn_send)

    def _parse_position(self, text: str) -> list[int]:
        lo, hi = self.rules.number_range
        cleaned = text.replace(" ", "")
        if not cleaned:
            return []
        numbers = [int(x) for x in cleaned.split(",") if x]
        if any(not (lo <= n <= hi) for n in numbers):
            raise ValueError(f"All numbers must be within {self.rules.number_range}.")
        return numbers

    def _generate(self):
        try:
            position_candidates = [self._parse_position(e.text()) for e in self.position_edits]
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

        empty_positions = [i + 1 for i, c in enumerate(position_candidates) if not c]
        if empty_positions:
            QMessageBox.warning(
                self, "Missing Positions",
                f"Position(s) {', '.join(map(str, empty_positions))} have no candidate numbers."
            )
            return

        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("⚙ Generating...")

        self._job = PositionTicketsJob(position_candidates)
        self._job.signals.finished.connect(self._on_finished)
        self._job.signals.failed.connect(self._on_failed)
        self._job.start()

    def _on_finished(self, tickets: list):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("⚡ Generate Tickets")
        self.generated_tickets = tickets

        max_display = 1000
        lines = [f"Ticket #{i + 1:03d} ➔ " + " ".join(f"{n:02d}" for n in t) for i, t in enumerate(tickets[:max_display])]
        if len(tickets) > max_display:
            lines.append(f"\n[Output truncated to first {max_display} tickets. Total: {len(tickets)}]")
        self.output.setText("\n".join(lines))
        self.lbl_summary.setText(f"<b>{len(tickets)} unique ticket(s) generated.</b>")
        self.btn_send.setEnabled(bool(tickets))

    def _on_failed(self, message: str):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("⚡ Generate Tickets")
        QMessageBox.critical(self, "Generation Failed", message)

    def _send_to_store(self):
        if self.generated_tickets:
            self.tickets_generated.emit(self.generated_tickets)
            QMessageBox.information(self, "Sent", f"Sent {len(self.generated_tickets)} tickets to the Ticket Store.")
