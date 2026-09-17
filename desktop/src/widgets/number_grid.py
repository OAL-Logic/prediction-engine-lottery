import logging
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QColor

from desktop.src.theme.manager import THEMES, DEFAULT_THEME

logger = logging.getLogger(__name__)


def _readable_text_color(background_hex: str) -> str:
    """Return '#000000' or '#ffffff', whichever gives higher WCAG contrast
    against `background_hex`. The selected ball's fill is a per-theme accent
    hue, and some themes' accent is dark enough (Forensic Neon's Astro Violet,
    contrast 3.52:1 against black) that a fixed light/dark text assumption
    fails the 4.5:1 AA floor other tokens in this system are held to — so the
    readable color is computed per fill rather than assumed.
    """
    def _linear(channel: int) -> float:
        v = channel / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b, _ = QColor(background_hex).getRgb()
    luminance = 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)
    contrast_with_black = (luminance + 0.05) / 0.05
    contrast_with_white = 1.05 / (luminance + 0.05)
    return "#000000" if contrast_with_black >= contrast_with_white else "#ffffff"


class NumberGrid(QWidget):
    """
    Interactive dynamic grid of numeric balls that toggles numbers into the active pool.
    Unselected balls read in the active theme's primary color on a panel surface;
    selected balls fill with the active theme's accent color — see apply_theme().

    Column count is width-aware: it reflows to however many 36px balls fit the
    widget's current width (see _columns_for_width()) instead of a fixed count,
    so the grid stays legible whether it's docked in a narrow rail or stretched
    across a wide splitter pane.
    """
    number_toggled = Signal(int, bool)  # number, is_selected

    BALL_SIZE = 36

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.buttons = {}
        self.selected_numbers = set()
        self.min_number = 1
        self.max_number = 25
        self.cols = 5
        # Default-theme fallback; apply_theme() overwrites this once the parent
        # tab/window wires up the real ThemeManager tokens.
        self.colors = THEMES[DEFAULT_THEME]
        self.build_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cols = self._columns_for_width(event.size().width())
        if cols != self.cols:
            self.cols = cols
            self.build_grid()

    def _columns_for_width(self, width: int) -> int:
        """How many BALL_SIZE balls (plus inter-ball spacing) fit `width`,
        clamped to at least 1 and to the pool's own size so a wide window
        never spreads a small pool thinner than it has numbers."""
        margins = self.layout.contentsMargins()
        spacing = self.layout.spacing()
        usable = width - margins.left() - margins.right()
        stride = self.BALL_SIZE + spacing
        cols = (usable + spacing) // stride if stride > 0 else 1
        pool_width = max(1, self.max_number - self.min_number + 1)
        return max(1, min(int(cols), pool_width))

    def apply_theme(self, colors: dict):
        self.colors = colors
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))

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

        # Recompute against the widget's actual current width — covers calls
        # that don't come through resizeEvent (e.g. set_range() swapping games).
        self.cols = self._columns_for_width(self.width())
        for n in range(self.min_number, self.max_number + 1):
            btn = QPushButton(f"{n:02d}")
            btn.setCheckable(False)
            btn.setFixedSize(self.BALL_SIZE, self.BALL_SIZE)
            btn.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            # Use lambda default argument to capture value of n correctly
            btn.clicked.connect(lambda checked=False, val=n: self.on_ball_clicked(val))

            btn.setStyleSheet(self.get_ball_style(n))

            row = (n - self.min_number) // self.cols
            col = (n - self.min_number) % self.cols
            self.layout.addWidget(btn, row, col)
            self.buttons[n] = btn

    def get_ball_style(self, num: int) -> str:
        c = self.colors
        if num in self.selected_numbers:
            # Active state: accent fill, background-tone text for contrast
            # against every theme's (bright) accent hue.
            accent_hover = QColor(c["accent"]).lighter(125).name()
            return f"""
                QPushButton {{
                    background-color: {c['accent']};
                    color: {c['background']};
                    border: 2px solid {c['accent']};
                    border-radius: 18px;
                }}
                QPushButton:hover {{
                    background-color: {accent_hover};
                    border-color: {accent_hover};
                }}
            """
        else:
            # Default state: primary-colored border/text on a panel surface
            return f"""
                QPushButton {{
                    background-color: {c['panel']};
                    color: {c['primary']};
                    border: 1px solid {c['border']};
                    border-radius: 18px;
                }}
                QPushButton:hover {{
                    background-color: {c['tab_bg']};
                    border: 1px solid {c['primary']};
                }}
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
