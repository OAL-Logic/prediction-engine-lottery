"""
High-Performance Ticket Asset Display
====================================
Renders candidate lottery tickets as elegant UI cards with:
- Circular lottery ball badges with subtle glow and contrast
- Bonus ball badges in gold/cyan
- Ticket metadata (line index, confidence score, strategy source)
- 1-click clipboard copy per line
- Empty state placeholder with call-to-action
"""

from __future__ import annotations

from typing import List, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QApplication, QMessageBox, QSizePolicy,
    QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from desktop.src.core.models import TicketReceipt, GameSchema
from desktop.src.shell.theme_manager import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_DEFAULT, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
    FONT_MONO, FONT_BODY
)


class TicketCardWidget(QFrame):
    """Visual card displaying a single candidate lottery line with ball pills."""

    def __init__(self, ticket: TicketReceipt, currency: str = "USD", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ticket = ticket
        self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(76)
        self.setStyleSheet(f"""
            TicketCardWidget {{
                background-color: #111624;
                border: 1px solid #1e283d;
                border-radius: {RADIUS_LG}px;
            }}
            TicketCardWidget:hover {{
                border-color: #00f0ff;
                background-color: #141c2e;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_SM, SPACING_MD, SPACING_SM)
        layout.setSpacing(SPACING_SM)

        # Header: Ticket #ID, Strategy Tag, Confidence Pill, Copy Button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_SM)

        lbl_id = QLabel(f"TICKET #{ticket.ticket_id:04d}")
        lbl_id.setStyleSheet(f"font-family: '{FONT_MONO}'; font-weight: 800; font-size: 11px; color: #00f0ff;")
        header_layout.addWidget(lbl_id)

        lbl_source = QLabel(f"•  {ticket.strategy_source}")
        lbl_source.setStyleSheet("font-size: 11px; color: #8b9bb4; font-weight: 500;")
        header_layout.addWidget(lbl_source)

        header_layout.addStretch()

        if ticket.confidence_score > 0:
            lbl_conf = QLabel(f"CONFIDENCE {ticket.confidence_score*100:.1f}%")
            lbl_conf.setStyleSheet("""
                background-color: #0d261e;
                border: 1px solid #10b981;
                color: #10b981;
                font-family: 'JetBrains Mono';
                font-size: 9px;
                font-weight: 800;
                padding: 2px 6px;
                border-radius: 4px;
            """)
            header_layout.addWidget(lbl_conf)

        self.btn_copy_line = QPushButton("📋")
        self.btn_copy_line.setToolTip("Copy this line to clipboard")
        self.btn_copy_line.setFixedSize(24, 24)
        self.btn_copy_line.setStyleSheet("""
            QPushButton {
                background-color: #182030;
                border: 1px solid #20293d;
                border-radius: 4px;
                padding: 0px;
                font-size: 11px;
            }
            QPushButton:hover {
                border-color: #00f0ff;
                background-color: #222d42;
            }
        """)
        self.btn_copy_line.clicked.connect(self._copy_line)
        header_layout.addWidget(self.btn_copy_line)

        layout.addLayout(header_layout)

        # Balls Row: Circular Pill Badges
        balls_layout = QHBoxLayout()
        balls_layout.setContentsMargins(0, 0, 0, 0)
        balls_layout.setSpacing(5)

        ball_size = 28 if len(ticket.numbers) > 12 else 30
        radius = ball_size // 2

        for num in sorted(ticket.numbers):
            lbl_ball = QLabel(f"{num:02d}")
            lbl_ball.setFixedSize(ball_size, ball_size)
            lbl_ball.setAlignment(Qt.AlignCenter)
            lbl_ball.setStyleSheet(f"""
                QLabel {{
                    background-color: #0c111a;
                    border: 1.5px solid #10b981;
                    border-radius: {RADIUS_FULL}px;
                    color: #f1f5f9;
                    font-family: '{FONT_MONO}';
                    font-weight: 800;
                    font-size: 11px;
                    padding: 0px;
                }}
            """)
            balls_layout.addWidget(lbl_ball)

        # Bonus Balls (if present)
        if ticket.bonus_numbers:
            sep = QLabel("+")
            sep.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 13px; padding: 0 2px;")
            balls_layout.addWidget(sep)
            for b in sorted(ticket.bonus_numbers):
                lbl_bonus = QLabel(f"{b:02d}")
                lbl_bonus.setFixedSize(ball_size, ball_size)
                lbl_bonus.setAlignment(Qt.AlignCenter)
                lbl_bonus.setStyleSheet(f"""
                    QLabel {{
                        background-color: #1f1608;
                        border: 1.5px solid #f59e0b;
                        border-radius: {RADIUS_FULL}px;
                        color: #fbbf24;
                        font-family: '{FONT_MONO}';
                        font-weight: 800;
                        font-size: 11px;
                        padding: 0px;
                    }}
                """)
                balls_layout.addWidget(lbl_bonus)

        balls_layout.addStretch()
        layout.addLayout(balls_layout)

    def _copy_line(self) -> None:
        text = self.ticket.formatted_main
        if self.ticket.bonus_numbers:
            text += " " + self.ticket.formatted_bonus
        QApplication.clipboard().setText(text)
        self.btn_copy_line.setText("✓")


class EmptyStateWidget(QFrame):
    """Empty placeholder encouraging the user to generate tickets."""

    quick_generate_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet("""
            EmptyStateWidget {
                background-color: #0e121c;
                border: 1.5px dashed #1e2638;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel("🎯")
        icon_lbl.setStyleSheet("font-size: 38px;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        title_lbl = QLabel("No Tickets Generated Yet")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #f1f5f9;")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("Select a strategy archetype on the left to instantly generate\ncalibrated candidate lines, or open Studio mode for custom wheeling.")
        desc_lbl.setStyleSheet("font-size: 12px; color: #8b9bb4; line-height: 1.4;")
        desc_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_lbl)

        btn_quick = QPushButton("⚡ Generate AI Consensus (10 Lines)")
        btn_quick.setStyleSheet("""
            QPushButton {
                background-color: #00f0ff;
                color: #000000;
                font-weight: 800;
                font-size: 12px;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #38f5ff;
            }
        """)
        btn_quick.clicked.connect(self.quick_generate_requested.emit)
        layout.addWidget(btn_quick, alignment=Qt.AlignCenter)


class TicketStoreWidget(QWidget):
    """Complete Ticket Store container hosting ticket cards or empty placeholder."""

    quick_generate_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._tickets: List[TicketReceipt] = []
        self._currency = "USD"
        self._ticket_price = 0.0

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Header Bar
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #101522;
                border: 1px solid #1c2436;
                border-radius: 8px;
                padding: 8px 12px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(4, 2, 4, 2)

        self.lbl_title = QLabel("TICKET ASSET REPOSITORY")
        self.lbl_title.setStyleSheet("font-family: 'JetBrains Mono'; font-weight: 800; font-size: 12px; color: #f1f5f9;")
        header_layout.addWidget(self.lbl_title)

        self.lbl_badge = QLabel("0 LINES")
        self.lbl_badge.setStyleSheet("""
            background-color: #182030;
            border: 1px solid #20293d;
            color: #8b9bb4;
            font-family: 'JetBrains Mono';
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 4px;
        """)
        header_layout.addWidget(self.lbl_badge)

        header_layout.addStretch()

        self.lbl_cost = QLabel("Est. Cost: $0.00")
        self.lbl_cost.setStyleSheet("font-family: 'JetBrains Mono'; color: #00ff66; font-weight: 700; font-size: 11px;")
        header_layout.addWidget(self.lbl_cost)

        main_layout.addWidget(header_frame)

        # Central Stack: 0 = Empty State, 1 = Scroll Area with Tickets
        self.stack = QStackedWidget()

        # 0. Empty State View
        self.empty_state = EmptyStateWidget()
        self.empty_state.quick_generate_requested.connect(self.quick_generate_requested.emit)
        self.stack.addWidget(self.empty_state)

        # 1. Scrollable Card View
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)

        self.scroll_area.setWidget(self.cards_container)
        self.stack.addWidget(self.scroll_area)

        main_layout.addWidget(self.stack, stretch=1)
        self.stack.setCurrentIndex(0)

    def set_game_info(self, currency: str, ticket_price: float) -> None:
        self._currency = currency
        self._ticket_price = ticket_price
        self._update_cost_label()

    def set_tickets(self, tickets: List[TicketReceipt]) -> None:
        self._tickets = tickets
        self._rebuild_cards()

    def clear(self) -> None:
        self._tickets = []
        self._rebuild_cards()

    def get_tickets(self) -> List[TicketReceipt]:
        return self._tickets

    def _rebuild_cards(self) -> None:
        # Clear existing layout
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        if not self._tickets:
            self.lbl_badge.setText("0 LINES")
            self.lbl_badge.setStyleSheet("""
                background-color: #182030; border: 1px solid #20293d; color: #8b9bb4;
                font-family: 'JetBrains Mono'; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 4px;
            """)
            self.stack.setCurrentIndex(0)
        else:
            count = len(self._tickets)
            self.lbl_badge.setText(f"{count} LINES READY")
            self.lbl_badge.setStyleSheet("""
                background-color: #0b261a; border: 1px solid #10b981; color: #10b981;
                font-family: 'JetBrains Mono'; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 4px;
            """)
            for t in self._tickets:
                card = TicketCardWidget(t, currency=self._currency)
                self.cards_layout.addWidget(card)
            self.cards_layout.addStretch()
            self.stack.setCurrentIndex(1)

        self._update_cost_label()

    def _update_cost_label(self) -> None:
        total = len(self._tickets) * self._ticket_price
        self.lbl_cost.setText(f"Est. Cost: {self._currency} {total:,.2f}")
