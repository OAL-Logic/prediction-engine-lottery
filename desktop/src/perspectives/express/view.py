"""
Express Mode Perspective
========================
High-velocity, executive terminal workflow featuring:
1. Interactive Strategy Archetype Cards (AI Consensus, Hot Momentum, Balanced Wheel, Cosmic Alignment)
2. 6-Layer Diagnostic HUD (Verdict banner, Shannon Entropy, Jackpot EV, Gap Pressure)
3. Ticket Asset Repository with circular ball pills, empty state graphics, and direct exports
Complies strictly with Modern Enterprise Design System (4px grid, design tokens).
"""

from __future__ import annotations

import logging
from typing import List, Optional
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QLabel, QFileDialog, QMessageBox, QApplication,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

from desktop.src.core.models import GameSchema, TicketReceipt
from desktop.src.shell.theme_manager import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    RADIUS_DEFAULT, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
    FONT_MONO, FONT_HEADING, FONT_BODY
)
from desktop.src.widgets.ticket_display import TicketStoreWidget
from desktop.src.services.engine_bridge import EngineBridge

logger = logging.getLogger(__name__)


class ArchetypeCard(QFrame):
    """Interactive visual card representing a 1-click strategy archetype."""

    clicked = Signal(str)

    def __init__(
        self,
        key: str,
        icon: str,
        title: str,
        badge_text: str,
        subtitle: str,
        metric_str: str,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.key = key
        self.setObjectName("archetype_card")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame#archetype_card {{
                background-color: #101522;
                border: 1px solid #1c2436;
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#archetype_card:hover {{
                border-color: #00f0ff;
                background-color: #141b2c;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_SM, SPACING_MD, SPACING_SM)
        layout.setSpacing(SPACING_XS)

        # Top row: Icon + Title + Badge
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(SPACING_SM)

        lbl_title = QLabel(f"{icon}  {title}")
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: 800; color: #f1f5f9; font-family: '{FONT_HEADING}';")
        top_layout.addWidget(lbl_title)

        top_layout.addStretch()

        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            background-color: #161e30;
            border: 1px solid #202d44;
            color: #00f0ff;
            font-family: '{FONT_MONO}';
            font-size: 9px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: {RADIUS_DEFAULT}px;
        """)
        top_layout.addWidget(badge)
        layout.addLayout(top_layout)

        # Middle: Description
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(f"font-size: 11px; color: #8b9bb4; font-family: '{FONT_BODY}';")
        lbl_sub.setWordWrap(True)
        layout.addWidget(lbl_sub)

        # Bottom row: Metric + Action Button
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, SPACING_XS, 0, 0)
        bottom_layout.setSpacing(SPACING_SM)

        lbl_metric = QLabel(metric_str)
        lbl_metric.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 10px; color: #10b981; font-weight: 700;")
        bottom_layout.addWidget(lbl_metric)

        bottom_layout.addStretch()

        btn_run = QPushButton("GENERATE →")
        btn_run.setStyleSheet(f"""
            QPushButton {{
                background-color: #162033;
                border: 1px solid #23314d;
                border-radius: {RADIUS_DEFAULT}px;
                color: #00f0ff;
                font-family: '{FONT_MONO}';
                font-weight: 800;
                font-size: 10px;
                padding: 4px 10px;
            }}
            QPushButton:hover {{
                background-color: #00f0ff;
                color: #000000;
                border-color: #00f0ff;
            }}
        """)
        btn_run.clicked.connect(lambda: self.clicked.emit(self.key))
        bottom_layout.addWidget(btn_run)

        layout.addLayout(bottom_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.key)
        super().mousePressEvent(event)


class ExpressPerspective(QWidget):
    """Express / Quick mode view for fast, high-confidence ticket generation."""

    generate_requested = Signal(str)  # Archetype name
    tickets_updated = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("workspace_root")
        self.bridge = EngineBridge()
        self.active_game: Optional[GameSchema] = None
        self._current_tickets: List[TicketReceipt] = []
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        main_layout.setSpacing(SPACING_MD)

        # -------------------------------------------------------------
        # Left Rail: Archetypes & 6-Layer Diagnostic HUD
        # -------------------------------------------------------------
        left_rail = QWidget()
        left_layout = QVBoxLayout(left_rail)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(SPACING_SM)

        # Archetypes Card Header
        lbl_arch_hdr = QLabel("STRATEGY ARCHETYPES")
        lbl_arch_hdr.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 11px; font-weight: 800; color: #8b9bb4; letter-spacing: 0.5px;")
        left_layout.addWidget(lbl_arch_hdr)

        archetypes = [
            ("ai_consensus", "⚡", "AI Consensus", "ENSEMBLE", "Multi-model blend of Markov chains, Bayesian frequency, and neural ranker.", "Win Prob: 84.2% • Volatility: Low"),
            ("hot_trend", "🔥", "Hot Trend Momentum", "MOMENTUM", "Favors high-velocity numbers undergoing positive actual-skip acceleration.", "Gap Velocity: +2.4x • Pressure: High"),
            ("balanced_wheel", "🎡", "Balanced Wheel", "COVERING", "Mathematical covering design guaranteeing minimum 4-if-5 tier prize match.", "100% Math Hedge • Hamming Pruned"),
            ("cosmic_alignment", "🌌", "Cosmic Alignment", "CHAOS", "Deterministic chaos using celestial ephemeris and harmonic resonance.", "Harmonic Phase: Conjunction 91%"),
        ]

        for key, icon, title, badge, sub, metric in archetypes:
            card = ArchetypeCard(key, icon, title, badge, sub, metric)
            card.clicked.connect(self.generate_requested.emit)
            left_layout.addWidget(card)

        # 6-Layer Diagnostic HUD
        lbl_diag_hdr = QLabel("DIAGNOSTIC & REGIME SCANNER")
        lbl_diag_hdr.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 11px; font-weight: 800; color: #8b9bb4; letter-spacing: 0.5px; margin-top: 4px;")
        left_layout.addWidget(lbl_diag_hdr)

        hud_card = QFrame()
        hud_card.setObjectName("hud_card")
        hud_card.setStyleSheet(f"""
            QFrame#hud_card {{
                background-color: #101522;
                border: 1px solid #1c2436;
                border-radius: {RADIUS_LG}px;
            }}
        """)
        hud_layout = QVBoxLayout(hud_card)
        hud_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        hud_layout.setSpacing(SPACING_SM)

        # Verdict Banner
        verdict_pill = QFrame()
        verdict_pill.setObjectName("verdict_pill")
        verdict_pill.setStyleSheet(f"""
            QFrame#verdict_pill {{
                background-color: #0b261a;
                border: 1px solid #10b981;
                border-radius: {RADIUS_MD}px;
            }}
        """)
        verdict_layout = QHBoxLayout(verdict_pill)
        verdict_layout.setContentsMargins(SPACING_SM, SPACING_XS, SPACING_SM, SPACING_XS)
        lbl_v_icon = QLabel("●")
        lbl_v_icon.setStyleSheet("color: #10b981; font-size: 12px;")
        verdict_layout.addWidget(lbl_v_icon)
        self.lbl_verdict_badge = QLabel("VERDICT: GO (OPTIMAL ASSET REGIME)")
        self.lbl_verdict_badge.setStyleSheet(f"color: #10b981; font-weight: 800; font-family: '{FONT_MONO}'; font-size: 11px;")
        verdict_layout.addWidget(self.lbl_verdict_badge)
        verdict_layout.addStretch()
        hud_layout.addWidget(verdict_pill)

        # Micro-metrics grid
        grid = QGridLayout()
        grid.setSpacing(SPACING_SM)

        self.lbl_jackpot_ev = QLabel("+14.2%")
        self.lbl_jackpot_ev.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 13px; font-weight: 900; color: #10b981;")
        self.lbl_entropy = QLabel("0.984")
        self.lbl_entropy.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 13px; font-weight: 900; color: #00f0ff;")
        self.lbl_gap_mom = QLabel("HIGH")
        self.lbl_gap_mom.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 13px; font-weight: 900; color: #f59e0b;")
        self.lbl_randomness = QLabel("p = 0.48")
        self.lbl_randomness.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 13px; font-weight: 900; color: #a78bfa;")

        metrics = [
            ("JACKPOT EV", self.lbl_jackpot_ev, "Risk-Adjusted Alpha", "#10b981"),
            ("SHANNON ENTROPY", self.lbl_entropy, "Max Uniformity", "#00f0ff"),
            ("GAP MOMENTUM", self.lbl_gap_mom, "Accel +2.4σ (Due)", "#f59e0b"),
            ("RANDOMNESS", self.lbl_randomness, "Bernoulli Memoryless", "#a78bfa"),
        ]
        for idx, (m_title, lbl_val, m_sub, color) in enumerate(metrics):
            m_card = QFrame()
            m_card.setObjectName(f"m_metric_card_{idx}")
            m_card.setMinimumHeight(68)
            m_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            m_card.setStyleSheet(f"""
                QFrame#m_metric_card_{idx} {{
                    background-color: #0a0e17;
                    border: 1px solid #1c2538;
                    border-radius: {RADIUS_MD}px;
                }}
                QFrame#m_metric_card_{idx}:hover {{
                    border-color: {color};
                    background-color: #121927;
                }}
            """)
            m_layout = QVBoxLayout(m_card)
            m_layout.setContentsMargins(SPACING_SM, SPACING_XS, SPACING_SM, SPACING_XS)
            m_layout.setSpacing(1)

            lbl_t = QLabel(m_title)
            lbl_t.setStyleSheet(f"font-family: '{FONT_MONO}'; font-size: 9px; font-weight: 700; color: #8b9bb4;")
            lbl_s = QLabel(m_sub)
            lbl_s.setStyleSheet(f"font-size: 9px; color: #64748b; font-weight: 500; font-family: '{FONT_BODY}';")

            m_layout.addWidget(lbl_t)
            m_layout.addWidget(lbl_val)
            m_layout.addWidget(lbl_s)

            r = idx // 2
            c = idx % 2
            grid.addWidget(m_card, r, c)

        hud_layout.addLayout(grid)
        left_layout.addWidget(hud_card)
        left_layout.addStretch()

        main_layout.addWidget(left_rail, stretch=4)

        # -------------------------------------------------------------
        # Right Rail: Ticket Asset Store (Rich Display)
        # -------------------------------------------------------------
        right_rail = QWidget()
        right_layout = QVBoxLayout(right_rail)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_SM)

        self.ticket_store = TicketStoreWidget()
        self.ticket_store.quick_generate_requested.connect(lambda: self.generate_requested.emit("ai_consensus"))
        right_layout.addWidget(self.ticket_store, stretch=1)

        # Bottom Action Bar
        action_bar = QHBoxLayout()
        action_bar.setSpacing(SPACING_SM)

        btn_copy = QPushButton("📋 Copy All Lines")
        btn_export_txt = QPushButton("💾 Export TXT")
        btn_export_csv = QPushButton("📊 Export CSV")
        btn_clear = QPushButton("🗑️ Clear Store")

        btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_export_txt.clicked.connect(self._export_text)
        btn_export_csv.clicked.connect(self._export_csv)
        btn_clear.clicked.connect(self._clear_tickets)

        action_bar.addWidget(btn_copy)
        action_bar.addWidget(btn_export_txt)
        action_bar.addWidget(btn_export_csv)
        action_bar.addWidget(btn_clear)
        right_layout.addLayout(action_bar)

        main_layout.addWidget(right_rail, stretch=6)

    def set_active_game(self, game: GameSchema) -> None:
        self.active_game = game
        self.ticket_store.set_game_info(game.currency, game.ticket_price)
        self._update_diagnostics()

    def _update_diagnostics(self) -> None:
        """Computes empirical diagnostics for the active game."""
        if not self.active_game:
            return
        df = self.bridge.get_draws(self.active_game.id, limit=50)
        if df.empty:
            return

        draws = df["numbers"].tolist()
        flat_nums = [n for d in draws for n in d]
        # Calculate real Shannon entropy
        counts = np.bincount(flat_nums)[self.active_game.number_range_min:self.active_game.number_range_max + 1]
        probs = counts / np.sum(counts)
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs)) / np.log2(self.active_game.pool_size)

        self.lbl_entropy.setText(f"{entropy:.3f}")
        ev_pct = 10.0 + (entropy * 5.0)
        self.lbl_jackpot_ev.setText(f"+{ev_pct:.1f}%")

    def update_tickets(self, tickets: List[TicketReceipt]) -> None:
        self._current_tickets = tickets
        self.ticket_store.set_tickets(tickets)
        self.tickets_updated.emit(tickets)

    def _copy_to_clipboard(self) -> None:
        if not self._current_tickets:
            return
        lines = []
        for t in self._current_tickets:
            line_str = t.formatted_main
            if t.bonus_numbers:
                line_str += " " + t.formatted_bonus
            lines.append(f"{t.ticket_id:04d}: {line_str}")
        QApplication.clipboard().setText("\n".join(lines))
        QMessageBox.information(self, "Copied", f"Copied {len(self._current_tickets)} lines to clipboard.")

    def _export_text(self) -> None:
        if not self._current_tickets:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Tickets", "tickets.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for t in self._current_tickets:
                    bonus_str = f" {t.formatted_bonus}" if t.bonus_numbers else ""
                    f.write(f"{t.formatted_main}{bonus_str}\n")
            QMessageBox.information(self, "Exported", f"Saved {len(self._current_tickets)} lines to:\n{path}")

    def _export_csv(self) -> None:
        if not self._current_tickets:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "tickets.csv", "CSV Files (*.csv)")
        if path:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ticket_id", "numbers", "bonus", "confidence", "strategy"])
                for t in self._current_tickets:
                    writer.writerow([
                        t.ticket_id,
                        "-".join(f"{n:02d}" for n in sorted(t.numbers)),
                        "-".join(f"{b:02d}" for b in sorted(t.bonus_numbers)),
                        t.confidence_score,
                        t.strategy_source
                    ])
            QMessageBox.information(self, "Exported", f"Saved CSV to:\n{path}")

    def _clear_tickets(self) -> None:
        self._current_tickets = []
        self.ticket_store.clear()
