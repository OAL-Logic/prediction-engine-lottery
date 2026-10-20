"""
Ball Matrix Widget
==================
High-performance native QPainter interactive lottery ball selector grid.
Features:
- Anti-aliased high-DPI circular balls
- Hover animations and interactive toggling
- Dynamic geometry adaptation based on active GameSchema
- Batch selection presets (All, Clear, Odd, Even, Primes, High, Low)
- Full dual theme token reactivity
"""

from __future__ import annotations

import math
from typing import Set, List, Optional, Dict
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QMouseEvent, QPaintEvent
from PySide6.QtWidgets import QWidget, QSizePolicy

from cockpit.src.core.models import GameSchema
from cockpit.src.theme.tokens import FONT_MONO, RADIUS_FULL

PRIMES_SET = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}


class BallMatrixWidget(QWidget):
    """
    Native QPainter grid for intuitive number pool selection.
    """

    selection_changed = Signal(list)  # Emits sorted List[int]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.game: Optional[GameSchema] = None
        self.selected_numbers: Set[int] = set()
        self.hovered_number: Optional[int] = None
        self._is_dragging: bool = False
        self._drag_state: bool = True  # True = selecting, False = unselecting

        # Theme visual tokens (Defaults to dark trading terminal)
        self._c_bg = QColor("#0c101a")
        self._c_ball_unselected = QColor("#151c2e")
        self._c_ball_border = QColor("#20293d")
        self._c_ball_hover = QColor("#1c263d")
        self._c_ball_selected = QColor("#00f0ff")
        self._c_text_unselected = QColor("#8b9bb4")
        self._c_text_selected = QColor("#000000")

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(280, 200)

    def apply_theme_tokens(self, tokens: Dict[str, str]) -> None:
        """Applies active design system palette tokens dynamically."""
        is_dark = tokens.get("is_dark", "true") == "true"
        self._c_bg = QColor(tokens.get("bg_input", "#0c101a"))
        self._c_ball_unselected = QColor(tokens.get("bg_card", "#151c2e"))
        self._c_ball_border = QColor(tokens.get("border", "#20293d"))
        self._c_ball_hover = QColor(tokens.get("bg_card_hover", "#1c263d"))
        self._c_ball_selected = QColor(tokens.get("primary", "#00f0ff"))
        self._c_text_unselected = QColor(tokens.get("text_muted", "#8b9bb4"))
        self._c_text_selected = QColor("#000000" if is_dark else "#ffffff")
        self.update()

    def configure_game(self, game: GameSchema) -> None:
        """Calibrates matrix dimensions, cell counts, and pool bounds."""
        self.game = game
        # Ensure selected numbers are clamped to the new game pool
        valid_pool = set(range(game.number_range_min, game.number_range_max + 1))
        self.selected_numbers = self.selected_numbers.intersection(valid_pool)
        self.hovered_number = None
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def set_selected_numbers(self, numbers: List[int]) -> None:
        self.selected_numbers = set(numbers)
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def clear_selection(self) -> None:
        self.selected_numbers.clear()
        self.update()
        self.selection_changed.emit([])

    def select_all(self) -> None:
        if not self.game:
            return
        self.selected_numbers = set(range(self.game.number_range_min, self.game.number_range_max + 1))
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def select_odd(self) -> None:
        if not self.game:
            return
        self.selected_numbers = {n for n in range(self.game.number_range_min, self.game.number_range_max + 1) if n % 2 != 0}
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def select_even(self) -> None:
        if not self.game:
            return
        self.selected_numbers = {n for n in range(self.game.number_range_min, self.game.number_range_max + 1) if n % 2 == 0}
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def select_primes(self) -> None:
        if not self.game:
            return
        self.selected_numbers = {n for n in range(self.game.number_range_min, self.game.number_range_max + 1) if n in PRIMES_SET}
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def select_high(self) -> None:
        if not self.game:
            return
        mid = self.game.number_range_min + (self.game.pool_size // 2)
        self.selected_numbers = {n for n in range(mid, self.game.number_range_max + 1)}
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def select_low(self) -> None:
        if not self.game:
            return
        mid = self.game.number_range_min + (self.game.pool_size // 2) - 1
        self.selected_numbers = {n for n in range(self.game.number_range_min, mid + 1)}
        self.update()
        self.selection_changed.emit(sorted(list(self.selected_numbers)))

    def _get_grid_metrics(self) -> Tuple[int, int, float, float, float]:
        """Calculates rows, cols, cell_width, cell_height, and ball_radius."""
        if not self.game:
            return 1, 1, 30.0, 30.0, 12.0

        total_balls = self.game.pool_size
        cols = self.game.board_cols
        rows = math.ceil(total_balls / cols)

        w = self.width()
        h = self.height()

        cell_w = max(16.0, w / cols)
        cell_h = max(16.0, h / rows)
        radius = min(cell_w, cell_h) * 0.40

        return rows, cols, cell_w, cell_h, radius

    def _number_at_pos(self, pt: QPointF) -> Optional[int]:
        if not self.game:
            return None

        rows, cols, cell_w, cell_h, radius = self._get_grid_metrics()
        c = int(pt.x() // cell_w)
        r = int(pt.y() // cell_h)

        if 0 <= c < cols and 0 <= r < rows:
            idx = r * cols + c
            num = self.game.number_range_min + idx
            if num <= self.game.number_range_max:
                cx = c * cell_w + cell_w / 2.0
                cy = r * cell_h + cell_h / 2.0
                dist = math.hypot(pt.x() - cx, pt.y() - cy)
                if dist <= radius * 1.2:
                    return num
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            num = self._number_at_pos(event.position())
            if num is not None:
                self._is_dragging = True
                self._drag_state = (num not in self.selected_numbers)
                if self._drag_state:
                    self.selected_numbers.add(num)
                else:
                    self.selected_numbers.discard(num)
                self.update()
                self.selection_changed.emit(sorted(list(self.selected_numbers)))
        elif event.button() == Qt.RightButton:
            self.clear_selection()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        num = self._number_at_pos(event.position())
        if self._is_dragging and num is not None:
            if self._drag_state:
                self.selected_numbers.add(num)
            else:
                self.selected_numbers.discard(num)
            self.update()
            self.selection_changed.emit(sorted(list(self.selected_numbers)))
        elif not self._is_dragging:
            if num != self.hovered_number:
                self.hovered_number = num
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._is_dragging = False

    def leaveEvent(self, event) -> None:
        self.hovered_number = None
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Background Fill
        painter.fillRect(self.rect(), self._c_bg)

        if not self.game:
            painter.setPen(self._c_text_unselected)
            painter.drawText(self.rect(), Qt.AlignCenter, "No active lottery game context.")
            return

        rows, cols, cell_w, cell_h, radius = self._get_grid_metrics()
        font_size = max(8, int(radius * 0.85))
        font = QFont(FONT_MONO, font_size, QFont.Bold)
        painter.setFont(font)

        # 2. Render each lottery ball in grid
        for idx in range(self.game.pool_size):
            num = self.game.number_range_min + idx
            r = idx // cols
            c = idx % cols

            cx = c * cell_w + cell_w / 2.0
            cy = r * cell_h + cell_h / 2.0
            center = QPointF(cx, cy)

            is_selected = (num in self.selected_numbers)
            is_hovered = (num == self.hovered_number)

            if is_selected:
                brush = QBrush(self._c_ball_selected)
                pen = QPen(self._c_ball_selected, 1.5)
                text_color = self._c_text_selected
            elif is_hovered:
                brush = QBrush(self._c_ball_hover)
                pen = QPen(self._c_ball_selected, 1.0)
                text_color = self._c_ball_selected
            else:
                brush = QBrush(self._c_ball_unselected)
                pen = QPen(self._c_ball_border, 1.0)
                text_color = self._c_text_unselected

            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawEllipse(center, radius, radius)

            # Draw text label (zero-padded)
            painter.setPen(text_color)
            label = self.game.format_number(num)
            text_rect = QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0)
            painter.drawText(text_rect, Qt.AlignCenter, label)
