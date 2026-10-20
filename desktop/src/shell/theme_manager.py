"""
Modern Enterprise Design Tokens & Theme Manager (PyQt6 / PySide6)
================================================================
Implements the Modern Enterprise Design System defined in `pyqt6-ui-designer`:
1. 4px Grid Spacing Constants (SPACING_*)
2. Strict Border Radius Hierarchy (RADIUS_*)
3. Typography Scale & Font Families (FONT_HEADING, FONT_BODY, FONT_MONO)
4. Token-First Palette Presets (Modern Enterprise Light, Trading Terminal Dark, Forensic Neon, Cyber Synthwave)
5. Comprehensive QSS Engine with full state completeness (default, hover, pressed, focus, disabled)
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)

# =============================================================================
# 1. SPACING TOKENS (4px Base Grid — Never deviate from multiples of 4)
# =============================================================================
SPACING_UNIT: int = 4
SPACING_XS: int = 4      # Tight gaps, icon padding
SPACING_SM: int = 8      # Button padding (vertical), item gaps
SPACING_MD: int = 16     # Button padding (horizontal), card padding
SPACING_LG: int = 24     # Section gaps, container padding
SPACING_XL: int = 32     # Large section separators
SPACING_CONTAINER_MARGIN: int = 24  # Main content area padding
SPACING_GUTTER: int = 16 # Column gap in multi-column layouts

# =============================================================================
# 2. BORDER RADIUS TOKENS
# =============================================================================
RADIUS_SM: int = 2       # Inputs, chips, feedback toasts
RADIUS_DEFAULT: int = 4  # Buttons, small components
RADIUS_MD: int = 6       # Intermediate pills, tab items
RADIUS_LG: int = 8       # Cards, modals, groupbox containers
RADIUS_XL: int = 12      # Outer frames, hero banners
RADIUS_FULL: int = 9999  # Circular pills, lottery ball badges, avatars

# =============================================================================
# 3. TYPOGRAPHY SCALE (size_px, weight, line_height_px, letter_spacing_em)
# =============================================================================
FONT_HEADING: str = "Hanken Grotesk"
FONT_BODY: str = "Inter"
FONT_MONO: str = "JetBrains Mono"

TYPO_HEADLINE_LG = (24, 600, 32, -0.01)   # Page titles, hero banners
TYPO_HEADLINE_MD = (20, 600, 28, -0.01)   # Section headers, card titles
TYPO_HEADLINE_SM = (16, 600, 24,  0.00)   # Sub-section headers, dock titles
TYPO_BODY_LG     = (15, 400, 22,  0.00)   # Lead / emphasis body text
TYPO_BODY_MD     = (14, 400, 20,  0.00)   # Standard body / nav items
TYPO_BODY_SM     = (13, 400, 18,  0.00)   # Dense tables, secondary content
TYPO_LABEL_MD    = (12, 600, 16, +0.05)   # ALL-CAPS column headers, buttons
TYPO_LABEL_SM    = (11, 500, 14,  0.00)   # Micro labels, status chips, timestamps

# =============================================================================
# 4. PALETTE PRESETS (Light & Dark Variants)
# =============================================================================
THEME_PALETTES: Dict[str, Dict[str, str]] = {
    "Trading Terminal (Default)": {
        "is_dark": "true",
        "bg_root": "#0a0d14",          # Deep obsidian canvas
        "bg_surface": "#101522",       # Primary card panel surface
        "bg_card": "#151c2e",          # Elevated interactive card
        "bg_card_hover": "#1c263d",    # Hover card surface
        "bg_input": "#0c101a",         # Deep recessed inputs/tables
        "border": "#20293d",           # Refined card boundary
        "border_light": "#2d3a54",     # Highlight border
        "border_focus": "#00f0ff",     # Cyber Cyan focus ring
        "text_main": "#f1f5f9",        # Crisp high-contrast off-white
        "text_muted": "#8b9bb4",       # Accessible slate grey
        "text_dim": "#576782",         # Subdued label text
        "primary": "#00f0ff",          # Cyber Cyan brand primary
        "primary_hover": "#38f5ff",
        "primary_pressed": "#00cbd9",
        "matrix_green": "#10b981",     # Emerald green (GO, Pass, Live)
        "matrix_green_glow": "#00ff88",
        "warning_amber": "#f59e0b",    # Amber gold (Warning, Overdue)
        "signal_red": "#ef4444",       # Coral red (NO-GO, Eliminated)
        "accent_purple": "#a855f7",    # Esoteric purple
        "dock_title_bg": "#0e131f",
        "dock_title_active": "#161e30",
    },
    "Modern Enterprise Light": {
        "is_dark": "false",
        "bg_root": "#faf9ff",          # Soft light base canvas
        "bg_surface": "#f1f3ff",       # Surface low
        "bg_card": "#ffffff",          # Surface lowest (cards, white)
        "bg_card_hover": "#e9edff",    # Surface hover
        "bg_input": "#ffffff",         # Clean input background
        "border": "#c3c6d6",           # Subtle outline variant
        "border_light": "#e1e8ff",     # Light separator
        "border_focus": "#0052cc",     # Corporate Blue focus
        "text_main": "#051a3e",        # On-surface primary text
        "text_muted": "#434654",       # On-surface variant (muted)
        "text_dim": "#737685",         # Outline muted text
        "primary": "#0052cc",          # Corporate Blue brand
        "primary_hover": "#0c56d0",
        "primary_pressed": "#003d9b",
        "matrix_green": "#1e7d4a",     # Emerald green
        "matrix_green_glow": "#10b981",
        "warning_amber": "#b45309",    # Amber
        "signal_red": "#ba1a1a",       # Ruby red
        "accent_purple": "#7b2600",    # Warm terracotta
        "dock_title_bg": "#e1e8ff",
        "dock_title_active": "#d8e2ff",
    },
    "Forensic Neon": {
        "is_dark": "true",
        "bg_root": "#05070a",
        "bg_surface": "#0a0f14",
        "bg_card": "#101820",
        "bg_card_hover": "#162230",
        "bg_input": "#070b10",
        "border": "#1b2836",
        "border_light": "#25384c",
        "border_focus": "#00ff66",
        "text_main": "#e6ffed",
        "text_muted": "#7a9985",
        "text_dim": "#486653",
        "primary": "#00ff66",
        "primary_hover": "#33ff85",
        "primary_pressed": "#00cc52",
        "matrix_green": "#00ff66",
        "matrix_green_glow": "#33ff85",
        "warning_amber": "#ffea00",
        "signal_red": "#ff3344",
        "accent_purple": "#a855f7",
        "dock_title_bg": "#0c1218",
        "dock_title_active": "#141e28",
    },
    "Cyber Synthwave": {
        "is_dark": "true",
        "bg_root": "#0a0612",
        "bg_surface": "#120a22",
        "bg_card": "#1b0f33",
        "bg_card_hover": "#261547",
        "bg_input": "#0e071c",
        "border": "#2e1a54",
        "border_light": "#422578",
        "border_focus": "#ff007f",
        "text_main": "#fdf4ff",
        "text_muted": "#a88bbd",
        "text_dim": "#6c5380",
        "primary": "#ff007f",
        "primary_hover": "#ff3399",
        "primary_pressed": "#cc0066",
        "matrix_green": "#39ff14",
        "matrix_green_glow": "#66ff47",
        "warning_amber": "#ffff33",
        "signal_red": "#ff073a",
        "accent_purple": "#c084fc",
        "dock_title_bg": "#150c29",
        "dock_title_active": "#20123e",
    }
}

DEFAULT_THEME_NAME: str = "Trading Terminal (Default)"


class ThemeManager(QObject):
    """
    Orchestrates desktop styling and dynamic QSS generation.
    Follows pyqt6-ui-designer specifications:
    - 4px grid spacing
    - strict border radii
    - dual light/dark mode support
    - full interactive state completeness
    """

    theme_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("Operator", "LotteryEngineCockpit")
        saved_theme = self.settings.value("theme_name", DEFAULT_THEME_NAME)
        if saved_theme not in THEME_PALETTES:
            saved_theme = DEFAULT_THEME_NAME
        self._current_theme_name = saved_theme

    @property
    def current_theme_name(self) -> str:
        return self._current_theme_name

    @property
    def is_dark(self) -> bool:
        return self.get_tokens().get("is_dark", "true") == "true"

    def get_tokens(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Returns the token dictionary for a theme."""
        name = theme_name or self._current_theme_name
        return THEME_PALETTES.get(name, THEME_PALETTES[DEFAULT_THEME_NAME])

    def set_theme(self, theme_name: str) -> None:
        """Switches active theme, persists setting, and emits theme_changed."""
        if theme_name not in THEME_PALETTES:
            logger.warning("Attempted to set unknown theme: %s", theme_name)
            return
        self._current_theme_name = theme_name
        self.settings.setValue("theme_name", theme_name)
        tokens = self.get_tokens(theme_name)
        self.theme_changed.emit(tokens)

    def get_heading_font(self, size: int = 16, bold: bool = True) -> QFont:
        font = QFont(FONT_HEADING)
        font.setPointSize(size)
        font.setBold(bold)
        return font

    def get_body_font(self, size: int = 12, bold: bool = False) -> QFont:
        font = QFont(FONT_BODY)
        font.setPointSize(size)
        font.setBold(bold)
        return font

    def get_monospace_font(self, size: int = 11, bold: bool = False) -> QFont:
        font = QFont(FONT_MONO)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(size)
        font.setBold(bold)
        return font

    def generate_stylesheet(self, theme_name: Optional[str] = None) -> str:
        """
        Constructs an opaque, high-performance Qt stylesheet adhering strictly
        to the design tokens and component library patterns.
        """
        t = self.get_tokens(theme_name)

        return f"""
        /* -----------------------------------------------------------------
           1. Solid Application Root (Never Transparent)
        ----------------------------------------------------------------- */
        QMainWindow, QDialog {{
            background-color: {t['bg_root']};
            color: {t['text_main']};
            font-family: '{FONT_BODY}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: {TYPO_BODY_MD[0]}px;
        }}
        
        /* Central Stack & Top-Level Workspaces */
        QStackedWidget, QWidget#central_stack, QWidget#workspace_root {{
            background-color: {t['bg_root']};
            color: {t['text_main']};
        }}

        /* Clean ScrollArea Viewport */
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}

        /* -----------------------------------------------------------------
           2. Dock Widgets & Multi-Monitor Windows
        ----------------------------------------------------------------- */
        QDockWidget {{
            background-color: {t['bg_surface']};
            color: {t['text_main']};
            font-weight: 700;
            font-size: {TYPO_LABEL_SM[0]}px;
            border: 1px solid {t['border']};
        }}
        
        QDockWidget::title {{
            background-color: {t['dock_title_bg']};
            border: 1px solid {t['border']};
            border-bottom: 1px solid {t['border']};
            padding: {SPACING_SM}px {SPACING_MD}px;
            text-align: left;
            font-family: '{FONT_MONO}', monospace;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: {t['text_muted']};
        }}
        
        QDockWidget::title:hover {{
            background-color: {t['dock_title_active']};
            color: {t['primary']};
        }}

        /* -----------------------------------------------------------------
           3. Splitters & Separators
        ----------------------------------------------------------------- */
        QSplitter {{
            background-color: transparent;
        }}
        QSplitter::handle {{
            background-color: {t['border']};
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        QSplitter::handle:hover {{
            background-color: {t['primary']};
        }}

        /* -----------------------------------------------------------------
           4. Top Navigation Bar & Toolbars
        ----------------------------------------------------------------- */
        QToolBar {{
            background-color: {t['bg_surface']};
            border-bottom: 1px solid {t['border']};
            spacing: {SPACING_SM}px;
            padding: 6px {SPACING_MD}px;
        }}
        
        /* -----------------------------------------------------------------
           5. Push Buttons with Complete State Handling
        ----------------------------------------------------------------- */
        QPushButton {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_DEFAULT}px;
            color: {t['text_main']};
            padding: 7px {SPACING_MD}px;
            font-weight: 600;
            font-size: {TYPO_LABEL_MD[0]}px;
            outline: none;
        }}
        
        QPushButton:hover {{
            background-color: {t['bg_card_hover']};
            border-color: {t['border_light']};
            color: {t['text_main']};
        }}
        
        QPushButton:pressed {{
            background-color: {t['bg_input']};
            border-color: {t['primary']};
        }}

        QPushButton:focus {{
            border: 1px solid {t['border_focus']};
        }}
        
        QPushButton:disabled {{
            border-color: {t['border']};
            color: {t['text_dim']};
            background-color: {t['bg_surface']};
        }}

        /* -----------------------------------------------------------------
           6. Inputs, Combos, and Spinboxes (4px Grid)
        ----------------------------------------------------------------- */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {t['bg_input']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_SM}px;
            padding: 6px 10px;
            color: {t['text_main']};
            font-family: '{FONT_MONO}', monospace;
            font-size: {TYPO_BODY_SM[0]}px;
            selection-background-color: {t['primary']};
            selection-color: #000000;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 1px solid {t['border_focus']};
            background-color: {t['bg_input']};
        }}

        QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
            color: {t['text_dim']};
            border-color: {t['border']};
            background-color: {t['bg_surface']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {t['bg_surface']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_MD}px;
            color: {t['text_main']};
            selection-background-color: {t['bg_card_hover']};
            selection-color: {t['primary']};
            padding: 4px;
        }}

        /* -----------------------------------------------------------------
           7. Group Boxes & Cards
        ----------------------------------------------------------------- */
        QGroupBox {{
            background-color: {t['bg_surface']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_LG}px;
            margin-top: 14px;
            padding: 14px 12px 10px 12px;
            font-weight: 700;
            font-size: {TYPO_LABEL_SM[0]}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: 0px;
            padding: 2px 8px;
            color: {t['text_muted']};
            background-color: {t['bg_surface']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_DEFAULT}px;
            font-family: '{FONT_MONO}', monospace;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }}

        /* -----------------------------------------------------------------
           8. Tab Widgets & Segmented Tabs
        ----------------------------------------------------------------- */
        QTabWidget::pane {{
            background-color: {t['bg_surface']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_LG}px;
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {t['bg_input']};
            border: 1px solid {t['border']};
            padding: 6px 14px;
            margin-right: 4px;
            margin-bottom: 2px;
            border-radius: {RADIUS_MD}px;
            color: {t['text_muted']};
            font-weight: 700;
            font-size: {TYPO_LABEL_SM[0]}px;
            font-family: '{FONT_MONO}', monospace;
        }}
        
        QTabBar::tab:selected {{
            background-color: {t['bg_card_hover']};
            border: 1px solid {t['primary']};
            color: {t['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            color: {t['text_main']};
            background-color: {t['bg_card']};
            border-color: {t['border_light']};
        }}

        /* -----------------------------------------------------------------
           9. Tables & Tree Views (Tonal Rows, No Whiteout)
        ----------------------------------------------------------------- */
        QTableWidget, QTableView, QTreeWidget, QTreeView {{
            background-color: {t['bg_surface']};
            alternate-background-color: {t['bg_root']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_MD}px;
            gridline-color: {t['border']};
            color: {t['text_main']};
            font-family: '{FONT_MONO}', monospace;
            font-size: {TYPO_BODY_SM[0]}px;
            outline: none;
        }}
        
        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {t['bg_card_hover']};
            color: {t['primary']};
        }}
        
        QHeaderView::section {{
            background-color: {t['bg_surface']};
            color: {t['text_muted']};
            padding: 6px 10px;
            border: none;
            border-bottom: 1px solid {t['border']};
            border-right: 1px solid {t['border']};
            font-weight: 700;
            font-size: 10px;
            font-family: '{FONT_MONO}', monospace;
            letter-spacing: 0.5px;
        }}

        /* -----------------------------------------------------------------
           10. Progress Bars
        ----------------------------------------------------------------- */
        QProgressBar {{
            background-color: {t['bg_input']};
            border: 1px solid {t['border']};
            border-radius: 5px;
            height: 10px;
            text-align: center;
            font-size: 9px;
            font-weight: bold;
            color: {t['text_main']};
        }}
        QProgressBar::chunk {{
            background-color: {t['matrix_green']};
            border-radius: 4px;
        }}

        /* -----------------------------------------------------------------
           11. Modern Sleek Scrollbars (6px Hairline)
        ----------------------------------------------------------------- */
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {t['border']};
            min-height: 24px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['text_dim']};
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {t['border']};
            min-width: 24px;
            border-radius: 3px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            height: 0px;
            width: 0px;
        }}

        /* -----------------------------------------------------------------
           12. Menu Bar & Popups
        ----------------------------------------------------------------- */
        QMenuBar {{
            background-color: {t['bg_surface']};
            border-bottom: 1px solid {t['border']};
            color: {t['text_muted']};
            font-size: {TYPO_LABEL_SM[0]}px;
            font-weight: 500;
            padding: 2px {SPACING_SM}px;
        }}
        QMenuBar::item:selected {{
            background-color: {t['bg_card_hover']};
            color: {t['text_main']};
            border-radius: {RADIUS_DEFAULT}px;
        }}
        QMenu {{
            background-color: {t['bg_surface']};
            border: 1px solid {t['border']};
            border-radius: {RADIUS_MD}px;
            padding: 4px;
            color: {t['text_main']};
        }}
        QMenu::item {{
            padding: 6px 20px 6px 12px;
            border-radius: {RADIUS_DEFAULT}px;
            font-size: {TYPO_LABEL_SM[0]}px;
        }}
        QMenu::item:selected {{
            background-color: {t['bg_card_hover']};
            color: {t['primary']};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {t['border']};
            margin: 4px 6px;
        }}

        /* -----------------------------------------------------------------
           13. Status Bar
        ----------------------------------------------------------------- */
        QStatusBar {{
            background-color: {t['bg_surface']};
            border-top: 1px solid {t['border']};
            color: {t['text_muted']};
            font-family: '{FONT_MONO}', monospace;
            font-size: {TYPO_LABEL_SM[0]}px;
            padding: 2px 6px;
        }}
        """
