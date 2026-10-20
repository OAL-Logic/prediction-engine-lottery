"""
High-Performance Native QPainter Ball Matrix
============================================
Custom Qt widget rendering anti-aliased, high-DPI lottery ball matrices.
Supports dynamic pool adaptation (Lotofácil 25, Mega-Sena 60, Quina 80, Lotomania 100),
selection toggles, hot/cold heat coloring, and fast vector repainting.
"""

from __future__ import annotations

import math
from typing import List, Set, Optional, Dict
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QSize
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QRadialGradient,
    QMouseEvent, QPaintEvent
)

from desktop.src.core.models import GameSchema


class BallMatrixWidget(QWidget):
    """
    Native QPainter lottery ball selector grid with sub-pixel rendering.
    """

    selection_changed = Signal(list)  # Emits list of selected integers

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(240, 110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # State
        self.pool_min: int = 1
        self.pool_size: int = 25
        self.cols: int = 5
        self.selected_numbers: Set[int] = set()
        self.hovered_number: Optional[int] = None
        self.heat_scores: Dict[int, float] = {} # Number -> 0.0 to 1.0

        # Palette
        self.color_bg = QColor("#0c101a")
        self.color_ball_normal = QColor("#151c2e")
        self.color_ball_selected = QColor("#10b981")
        self.color_ball_text_normal = QColor("#f1f5f9")
        self.color_ball_text_selected = QColor("#ffffff")
        self.color_border = QColor("#1c2538")
        self.color_hover_ring = QColor("#00f0ff")

    def apply_theme_tokens(self, tokens: Dict[str, str]) -> None:
        """Dynamically calibrates QPainter palette to active design tokens."""
        is_dark = tokens.get("is_dark", "true") == "true"
        if is_dark:
            self.color_bg = QColor(tokens.get("bg_input", "#0c101a"))
            self.color_border = QColor(tokens.get("border", "#1c2538"))
            self.color_ball_normal = QColor(tokens.get("bg_card", "#151c2e"))
            self.color_ball_text_normal = QColor(tokens.get("text_main", "#f1f5f9"))
            self.color_ball_selected = QColor(tokens.get("matrix_green", "#10b981"))
            self.color_ball_text_selected = QColor("#ffffff")
            self.color_hover_ring = QColor(tokens.get("primary", "#00f0ff"))
        else:
            self.color_bg = QColor(tokens.get("bg_surface", "#f1f3ff"))
            self.color_border = QColor(tokens.get("border", "#c3c6d6"))
            self.color_ball_normal = QColor(tokens.get("bg_card", "#ffffff"))
            self.color_ball_text_normal = QColor(tokens.get("text_main", "#051a3e"))
            self.color_ball_selected = QColor(tokens.get("primary", "#0052cc"))
            self.color_ball_text_selected = QColor("#ffffff")
            self.color_hover_ring = QColor(tokens.get("primary_hover", "#0c56d0"))
        self.update()

    def configure_game(self, game: GameSchema) -> None:
        """Calibrates matrix layout and bounds to match active lottery game."""
        self.pool_min = game.number_range_min
        self.pool_size = game.pool_size
        self.cols = game.board_cols or 10
        self.selected_numbers.clear()
        self.heat_scores.clear()
        self.update()

    def set_selected_numbers(self, numbers: List[int]) -> None:
        """Sets active pool selection and updates display."""
        valid_range = range(self.pool_min, self.pool_min + self.pool_size)
        self.selected_numbers = {n for n in numbers if n in valid_range}
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def clear_selection(self) -> None:
        self.selected_numbers.clear()
        self.update()
        self.selection_changed.emit([])

    def select_all(self) -> None:
        self.selected_numbers = set(range(self.pool_min, self.pool_min + self.pool_size))
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def set_heat_scores(self, scores: Dict[int, float]) -> None:
        """Sets 0.0-1.0 thermal ratings for numbers (cold blue -> hot red)."""
        self.heat_scores = scores
        self.update()

    def sizeHint(self) -> QSize:
        rows = math.ceil(self.pool_size / self.cols) if self.cols else 5
        return QSize(320, max(110, rows * 38))

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        width = self.width()
        height = self.height()
        painter.setBrush(QBrush(self.color_bg))
        painter.setPen(QPen(self.color_border, 1.0))
        painter.drawRoundedRect(1, 1, width - 2, height - 2, 8, 8)

        rows = math.ceil(self.pool_size / self.cols)
        cell_w = (width - 4) / self.cols
        cell_h = (height - 4) / rows
        radius = min(cell_w, cell_h) * 0.40

        font = QFont("JetBrains Mono")
        font.setBold(True)
        font.setPixelSize(int(radius * 0.95))
        painter.setFont(font)

        for i in range(self.pool_size):
            num = self.pool_min + i
            r = i // self.cols
            c = i % self.cols

            cx = (c + 0.5) * cell_w
            cy = (r + 0.5) * cell_h

            is_selected = num in self.selected_numbers
            is_hovered = (num == self.hovered_number)

            # Determine Base Fill Brush
            if is_selected:
                gradient = QRadialGradient(cx - radius * 0.2, cy - radius * 0.2, radius)
                gradient.setColorAt(0.0, QColor("#33ff88"))
                gradient.setColorAt(1.0, self.color_ball_selected)
                painter.setBrush(gradient)
                painter.setPen(QPen(QColor("#00ff66"), 1.5))
            else:
                # Normal or heat-tinted ball
                heat = self.heat_scores.get(num, 0.5)
                if num in self.heat_scores:
                    # Tint towards amber/red if hot, or cyan if cold
                    tint = QColor(
                        int(255 * heat),
                        int(180 * (1.0 - abs(heat - 0.5) * 2)),
                        int(255 * (1.0 - heat))
                    )
                    painter.setBrush(QBrush(tint.darker(220)))
                    painter.setPen(QPen(tint.lighter(130), 1.0))
                else:
                    painter.setBrush(QBrush(self.color_ball_normal))
                    painter.setPen(QPen(self.color_border, 1.0))

            painter.drawEllipse(QPointF(cx, cy), radius, radius)

            # Draw Hover Accent Ring
            if is_hovered and not is_selected:
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(self.color_hover_ring, 1.8))
                painter.drawEllipse(QPointF(cx, cy), radius + 2, radius + 2)

            # Draw Number Text
            text_color = self.color_ball_text_selected if is_selected else self.color_ball_text_normal
            painter.setPen(text_color)
            num_str = f"{num:02d}"
            text_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            painter.drawText(text_rect, Qt.AlignCenter, num_str)

        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            num = self._hit_test(event.position().x(), event.position().y())
            if num is not None:
                if num in self.selected_numbers:
                    self.selected_numbers.remove(num)
                else:
                    self.selected_numbers.add(num)
                self.update()
                self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        num = self._hit_test(event.position().x(), event.position().y())
        if num != self.hovered_number:
            self.hovered_number = num
            self.update()

    def leaveEvent(self, event) -> None:
        if self.hovered_number is not None:
            self.hovered_number = None
            self.update()

    def _hit_test(self, x: float, y: float) -> Optional[int]:
        rows = math.ceil(self.pool_size / self.cols)
        cell_w = self.width() / self.cols
        cell_h = self.height() / rows

        c = int(x // cell_w)
        r = int(y // cell_h)

        if 0 <= c < self.cols and 0 <= r < rows:
            idx = r * self.cols + c
            if idx < self.pool_size:
                return self.pool_min + idx
        return None
