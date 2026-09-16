import logging
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)

class NumberGrid(QWidget):
    """
    Interactive dynamic grid of numeric balls that toggles numbers into the active pool.
    Styled with Forensic / Sleek Neon styling (cyan border unselected, solid neon red selected).
    """
    number_toggled = Signal(int, bool)  # number, is_selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.buttons = {}
        self.selected_numbers = set()
        self.min_number = 1
        self.max_number = 25
        self.build_grid()

    def set_max_number(self, max_num: int):
        """Shorthand for the common case: a 1-indexed pool. See set_range() for
        pools that don't start at 1 (e.g. Lotomania's 00-99)."""
        self.set_range(1, max_num)

    def set_range(self, min_num: int, max_num: int):
        self.min_number = min_num
        self.max_number = max_num
        self.selected_numbers.clear()
        self.build_grid()

    def build_grid(self):
        # Clear existing buttons from layout
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.buttons.clear()

        # Wrap at 5 columns for small pools (<= 30) or 10 columns for larger pools (> 30)
        pool_width = self.max_number - self.min_number + 1
        cols = 5 if pool_width <= 30 else 10
        for n in range(self.min_number, self.max_number + 1):
            btn = QPushButton(f"{n:02d}")
            btn.setCheckable(False)
            btn.setFixedSize(36, 36)
            btn.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            # Use lambda default argument to capture value of n correctly
            btn.clicked.connect(lambda checked=False, val=n: self.on_ball_clicked(val))
            
            btn.setStyleSheet(self.get_ball_style(n))

            row = (n - 1) // cols
            col = (n - 1) % cols
            self.layout.addWidget(btn, row, col)
            self.buttons[n] = btn

    def get_ball_style(self, num: int) -> str:
        if num in self.selected_numbers:
            # Active state: Neon Red background, white text
            return """
                QPushButton {
                    background-color: #FF3366;
                    color: #FFFFFF;
                    border: 2px solid #FF3366;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: #FF5588;
                    border-color: #FF5588;
                }
            """
        else:
            # Default state: unselected cyber cyan border, dark background
            return """
                QPushButton {
                    background-color: #1A1A1E;
                    color: #00F0FF;
                    border: 1px solid #222226;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: #222226;
                    border: 1px solid #00F0FF;
                }
            """

    def on_ball_clicked(self, num: int):
        if num in self.selected_numbers:
            self.selected_numbers.remove(num)
            is_selected = False
        else:
            self.selected_numbers.add(num)
            is_selected = True
        
        self.buttons[num].setStyleSheet(self.get_ball_style(num))
        self.number_toggled.emit(num, is_selected)

    def select_all(self):
        self.selected_numbers = set(range(self.min_number, self.max_number + 1))
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))
        self.number_toggled.emit(0, True)

    def select_numbers(self, numbers: list[int]):
        """Replace the active pool with exactly `numbers` (clamped to the current
        grid range) — used by callers pushing an externally-computed set (e.g. a
        predicted ticket) rather than a locally-computed one like hot/cold/prime."""
        self.selected_numbers = {n for n in numbers if self.min_number <= n <= self.max_number}
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))
        self.number_toggled.emit(0, True)

    def clear_selection(self):
        self.selected_numbers.clear()
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))
        self.number_toggled.emit(0, False)
