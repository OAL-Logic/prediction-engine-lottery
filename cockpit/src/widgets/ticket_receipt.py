"""
Ticket Receipt Widget
=====================
Presents generated lottery tickets in clean, receipt-style monospace cards.
Supports instant clipboard copying, CSV export, and confidence score displays.
"""

from __future__ import annotations

from typing import List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtGui import QClipboard

from cockpit.src.core.models import TicketReceipt, GameSchema
from cockpit.src.theme.tokens import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_SM, RADIUS_DEFAULT, RADIUS_MD, FONT_MONO, FONT_HEADING
)


class TicketReceiptWidget(QWidget):
    """
    Receipt-style ticket display repository.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._tickets: List[TicketReceipt] = []
        self._game: Optional[GameSchema] = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        # Header bar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(SPACING_SM, SPACING_XS, SPACING_SM, SPACING_XS)

        self.lbl_count = QLabel("Generated Lines (0)")
        self.lbl_count.setStyleSheet(f"font-family: '{FONT_HEADING}'; font-weight: 700; font-size: 12px; color: #00f0ff;")
        header_layout.addWidget(self.lbl_count)
        header_layout.addStretch()

        self.btn_copy = QPushButton("Copy All")
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)
        header_layout.addWidget(self.btn_copy)

        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)
        self.btn_export_csv.clicked.connect(self._export_csv)
        header_layout.addWidget(self.btn_export_csv)

        layout.addLayout(header_layout)

        # Scroll Area holding cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background-color: #0c101a; border-radius: 8px;")

        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.card_layout = QVBoxLayout(self.container)
        self.card_layout.setContentsMargins(SPACING_XS, SPACING_XS, SPACING_XS, SPACING_XS)
        self.card_layout.setSpacing(SPACING_SM)
        self.card_layout.addStretch()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def set_game(self, game: GameSchema) -> None:
        self._game = game

    def set_tickets(self, tickets: List[TicketReceipt]) -> None:
        """Populates scroll area with styled receipt cards."""
        self._tickets = tickets
        self.lbl_count.setText(f"Generated Lines ({len(tickets)})")

        # Clear existing cards
        while self.card_layout.count() > 1:
            child = self.card_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for t in tickets:
            card = self._create_ticket_card(t)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)

    display_tickets = set_tickets

    def _create_ticket_card(self, t: TicketReceipt) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #101522;
                border: 1px solid #20293d;
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px;
            }}
            QFrame:hover {{
                border-color: #00f0ff;
                background-color: #151c2e;
            }}
        """)
        c_layout = QHBoxLayout(card)
        c_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        c_layout.setSpacing(SPACING_MD)

        # Ticket ID badge
        lbl_id = QLabel(f"#{t.ticket_id:02d}")
        lbl_id.setStyleSheet(f"font-family: '{FONT_MONO}'; font-weight: 800; font-size: 11px; color: #8b9bb4;")
        c_layout.addWidget(lbl_id)

        # Monospace numbers
        main_balls = "  ".join(f"{n:02d}" for n in sorted(t.numbers))
        lbl_nums = QLabel(main_balls)
        lbl_nums.setStyleSheet(f"font-family: '{FONT_MONO}'; font-weight: 900; font-size: 13px; color: #f1f5f9; letter-spacing: 1px;")
        c_layout.addWidget(lbl_nums, stretch=2)

        # Bonus balls if any
        if t.bonus_numbers:
            bonus_str = " + " + " ".join(f"{b:02d}" for b in sorted(t.bonus_numbers))
            lbl_bonus = QLabel(bonus_str)
            lbl_bonus.setStyleSheet(f"font-family: '{FONT_MONO}'; font-weight: 800; font-size: 12px; color: #f59e0b;")
            c_layout.addWidget(lbl_bonus)

        # Source / Archetype tag
        lbl_src = QLabel(t.strategy_source)
        lbl_src.setStyleSheet(f"""
            background-color: #0c101a; border: 1px solid #20293d; border-radius: {RADIUS_SM}px;
            color: #8b9bb4; font-family: '{FONT_MONO}'; font-size: 10px; font-weight: 600; padding: 2px 6px;
        """)
        c_layout.addWidget(lbl_src)

        # Confidence chip
        pct = int(t.confidence_score * 100)
        lbl_conf = QLabel(f"{pct}%")
        color = "#10b981" if pct >= 80 else ("#f59e0b" if pct >= 60 else "#ef4444")
        lbl_conf.setStyleSheet(f"""
            background-color: #0d261e; border: 1px solid {color}; border-radius: {RADIUS_SM}px;
            color: {color}; font-family: '{FONT_MONO}'; font-weight: 800; font-size: 11px; padding: 2px 6px;
        """)
        c_layout.addWidget(lbl_conf)

        return card

    def _copy_to_clipboard(self) -> None:
        if not self._tickets:
            return
        lines = []
        for t in self._tickets:
            nums = " ".join(f"{n:02d}" for n in sorted(t.numbers))
            if t.bonus_numbers:
                nums += f" + [{' '.join(f'{b:02d}' for b in sorted(t.bonus_numbers))}]"
            lines.append(nums)
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Clipboard", f"Copied {len(lines)} ticket lines to clipboard.")

    def _export_csv(self) -> None:
        if not self._tickets:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Tickets CSV", "tickets.csv", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("ticket_id,numbers,bonus_numbers,confidence,strategy\n")
            for t in self._tickets:
                main_nums = " ".join(str(n) for n in sorted(t.numbers))
                bonus = " ".join(str(b) for b in sorted(t.bonus_numbers))
                f.write(f"{t.ticket_id},\"{main_nums}\",\"{bonus}\",{t.confidence_score},\"{t.strategy_source}\"\n")
        QMessageBox.information(self, "Exported", f"Successfully exported {len(self._tickets)} lines to:\n{path}")
