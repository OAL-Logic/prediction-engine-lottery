"""
Theme Manager & QSS Engine
==========================
Generates pixel-perfect PySide6 Qt Style Sheets (QSS) adhering to
the pyqt6-ui-designer specification:
- 4px grid spacing derived styles
- Complete interactive states (:hover, :pressed, :disabled, :focus, :selected)
- Dual theme switching with signal broadcast
- Session persistence via QSettings
"""

from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtWidgets import QApplication

from cockpit.src.theme.tokens import (
    THEME_PALETTES, DEFAULT_THEME_NAME,
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
    RADIUS_NONE, RADIUS_SM, RADIUS_DEFAULT, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
    FONT_HEADING, FONT_BODY, FONT_MONO
)


class ThemeManager(QObject):
    """
    Central theme and style manager for the Cockpit desktop suite.
    Emits theme_changed(dict) whenever active tokens are updated.
    """

    theme_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("Operator", "LotteryEngineCockpitV2")
        saved_theme = self.settings.value("theme_name", DEFAULT_THEME_NAME)
        if saved_theme not in THEME_PALETTES:
            saved_theme = DEFAULT_THEME_NAME
        self._current_theme_name: str = saved_theme
        self._tokens: Dict[str, str] = THEME_PALETTES[self._current_theme_name]

    @property
    def current_theme_name(self) -> str:
        return self._current_theme_name

    @property
    def is_dark(self) -> bool:
        return self._tokens.get("is_dark", "true") == "true"

    def get_tokens(self) -> Dict[str, str]:
        return dict(self._tokens)

    def set_theme(self, theme_name: str) -> None:
        """Swaps active palette, generates stylesheet, and notifies subscribers."""
        if theme_name in THEME_PALETTES:
            self._current_theme_name = theme_name
            self._tokens = THEME_PALETTES[theme_name]
            self.settings.setValue("theme_name", theme_name)
            self.theme_changed.emit(self.get_tokens())

    def generate_stylesheet(self) -> str:
        """
        Generates the comprehensive enterprise Qt Style Sheet (QSS) for the application.
        Strictly enforces 4px grid tokens and interactive completeness.
        """
        t = self._tokens
        is_dark = self.is_dark
        scroll_handle_bg = "#222c42" if is_dark else "#d0d5e5"
        scroll_hover_bg = "#2f3d5c" if is_dark else "#b8bfd6"

        return f"""
        /* -------------------------------------------------------------
           Base Window & Canvas
           ------------------------------------------------------------- */
        QMainWindow, QDialog, QWidget#root_container {{
            background-color: {t['bg_root']};
            color: {t['text_main']};
            font-family: '{FONT_BODY}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
        }}

        QWidget {{
            color: {t['text_main']};
        }}

        /* -------------------------------------------------------------
           Containers, Frames & Dock Widgets
           ------------------------------------------------------------- */
        QGroupBox {{
            background-color: {t['bg_surface']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_MD}px;
            margin-top: {SPACING_LG}px;
            padding: {SPACING_MD}px;
            font-family: '{FONT_HEADING}';
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
            color: {t['primary']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: {SPACING_MD}px;
            top: 4px;
            padding: 0 {SPACING_SM}px;
            background-color: {t['bg_surface']};
        }}

        QDockWidget {{
            color: {t['text_main']};
            font-family: '{FONT_HEADING}';
            font-weight: 700;
            font-size: 12px;
        }}

        QDockWidget::title {{
            background-color: {t['dock_title_bg']};
            border-bottom: 1px solid {t['border']};
            padding: {SPACING_SM}px {SPACING_MD}px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}

        QDockWidget::close-button, QDockWidget::float-button {{
            border: none;
            background: transparent;
            padding: 2px;
            icon-size: 14px;
        }}

        QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
            background-color: {t['bg_card_hover']};
            border-radius: {RADIUS_SM}px;
        }}

        /* -------------------------------------------------------------
           Buttons & Interactive Controls
           ------------------------------------------------------------- */
        QPushButton {{
            background-color: {t['bg_card']};
            color: {t['text_main']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_DEFAULT}px;
            padding: {SPACING_SM}px {SPACING_MD}px;
            font-family: '{FONT_BODY}';
            font-weight: 600;
            font-size: 12px;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {t['bg_card_hover']};
            border-color: {t['border_light']};
            color: {t['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {t['bg_surface']};
            border-color: {t['primary']};
        }}

        QPushButton:disabled {{
            background-color: {t['bg_surface']};
            border-color: {t['border']};
            color: {t['text_dim']};
        }}

        QPushButton#btn_primary {{
            background-color: {t['primary']};
            color: #000000;
            border: 1px solid {t['primary']};
            font-weight: 800;
        }}

        QPushButton#btn_primary:hover {{
            background-color: {t['primary_hover']};
            border-color: {t['primary_hover']};
        }}

        QPushButton#btn_primary:pressed {{
            background-color: {t['primary_pressed']};
            border-color: {t['primary_pressed']};
        }}

        /* -------------------------------------------------------------
           Inputs, LineEdits & SpinBoxes
           ------------------------------------------------------------- */
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {t['bg_input']};
            color: {t['text_main']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_DEFAULT}px;
            padding: {SPACING_SM}px {SPACING_SM}px;
            font-family: '{FONT_MONO}';
            font-size: 12px;
            selection-background-color: {t['primary']};
            selection-color: #000000;
            min-height: 22px;
        }}

        QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
            border-color: {t['border_light']};
        }}

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
            border: 1px solid {t['border_focus']};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid {t['border']};
        }}

        QComboBox QAbstractItemView {{
            background-color: {t['bg_card']};
            color: {t['text_main']};
            border: 1px solid {t['border']};
            selection-background-color: {t['primary']};
            selection-color: #000000;
            padding: {SPACING_XS}px;
            outline: none;
        }}

        /* -------------------------------------------------------------
           Tables, Trees & Grids
           ------------------------------------------------------------- */
        QTableWidget, QTableView {{
            background-color: {t['bg_input']};
            alternate-background-color: {t['bg_card']};
            color: {t['text_main']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_MD}px;
            gridline-color: {t['border']};
            selection-background-color: {t['bg_card_hover']};
            selection-color: {t['primary']};
            font-family: '{FONT_MONO}';
            font-size: 12px;
            outline: none;
        }}

        QTableWidget QDoubleSpinBox, QTableWidget QSpinBox, QTableWidget QLineEdit {{
            background-color: transparent;
            color: {t['text_main']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_SM}px;
            padding: 2px 4px;
        }}

        QScrollArea, QScrollArea > QWidget > QWidget {{
            background-color: transparent;
            border: none;
        }}

        QTableWidget::item {{
            padding: {SPACING_XS}px {SPACING_SM}px;
            border: none;
        }}

        QTableWidget::item:selected {{
            background-color: {t['bg_card_hover']};
            color: {t['primary']};
        }}

        QHeaderView::section {{
            background-color: {t['bg_surface']};
            color: {t['text_muted']};
            padding: {SPACING_SM}px {SPACING_MD}px;
            border: none;
            border-right: 1px solid {t['border']};
            border-bottom: 1px solid {t['border']};
            font-family: '{FONT_HEADING}';
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}

        /* -------------------------------------------------------------
           Scrollbars & Sliders
           ------------------------------------------------------------- */
        QScrollBar:vertical {{
            background: {t['bg_root']};
            width: 10px;
            margin: 0;
            border: none;
        }}

        QScrollBar::handle:vertical {{
            background: {scroll_handle_bg};
            border-radius: {RADIUS_SM}px;
            min-height: 24px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {scroll_hover_bg};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background: {t['bg_root']};
            height: 10px;
            margin: 0;
            border: none;
        }}

        QScrollBar::handle:horizontal {{
            background: {scroll_handle_bg};
            border-radius: {RADIUS_SM}px;
            min-width: 24px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {scroll_hover_bg};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* -------------------------------------------------------------
           Status Bar, ToolBar & Tabs
           ------------------------------------------------------------- */
        QStatusBar {{
            background-color: {t['bg_surface']};
            border-top: 1px solid {t['border']};
            color: {t['text_muted']};
            font-family: '{FONT_MONO}';
            font-size: 11px;
            padding: {SPACING_XS}px {SPACING_MD}px;
        }}

        QToolBar {{
            background-color: {t['bg_surface']};
            border-bottom: 1px solid {t['border']};
            padding: {SPACING_SM}px {SPACING_MD}px;
            spacing: {SPACING_MD}px;
        }}

        QTabWidget::pane {{
            border: 1px solid {t['border']};
            border-radius: {RADIUS_MD}px;
            background-color: {t['bg_surface']};
        }}

        QTabBar::tab {{
            background-color: {t['bg_card']};
            color: {t['text_muted']};
            border: 1px solid {t['border']};
            border-bottom: none;
            border-top-left-radius: {RADIUS_DEFAULT}px;
            border-top-right-radius: {RADIUS_DEFAULT}px;
            padding: {SPACING_SM}px {SPACING_MD}px;
            font-family: '{FONT_BODY}';
            font-weight: 600;
            font-size: 12px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {t['bg_surface']};
            color: {t['primary']};
            border-color: {t['border']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {t['bg_card_hover']};
            color: {t['text_main']};
        }}

        /* Checkbox styling */
        QCheckBox {{
            spacing: {SPACING_SM}px;
            color: {t['text_main']};
            font-size: 12px;
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {t['border']};
            border-radius: {RADIUS_SM}px;
            background-color: {t['bg_input']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {t['primary']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {t['primary']};
            border-color: {t['primary']};
        }}
        """
