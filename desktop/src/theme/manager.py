from PySide6.QtCore import QSettings, QObject, Signal
import logging

logger = logging.getLogger(__name__)

# Every entry in `self.themes` must define exactly these tokens; `generate_stylesheet`
# interpolates them unconditionally, so a theme missing one crashes the whole app
# at startup rather than just looking wrong.
REQUIRED_TOKENS = frozenset({
    "background", "primary", "primary_hover", "primary_pressed", "text",
    "text_dim", "border", "panel", "tab_bg", "accent", "success", "warning", "error",
})

# The one theme name every fallback path trusts. Settings files can outlive the
# theme they point at (a theme gets renamed or retired between versions), so any
# lookup that misses must land here instead of on an arbitrary hardcoded name.
DEFAULT_THEME = "Sleek Dark Mode"

# Module-level so widgets that need a color dict before a ThemeManager instance
# exists (a pre-`apply_theme` fallback, a modal dialog built with no `theme_manager`
# in reach) can import THEMES/DEFAULT_THEME directly instead of re-typing hex
# literals that silently drift from the registered palette.
THEMES = {
    "Forensic Neon": {
        "background": "#000000",      # Obsidian Black
        "primary": "#00ff41",         # Matrix Green
        "primary_hover": "#00e63a",
        "primary_pressed": "#00cc33",
        "text": "#00ff41",            # Neon Green
        "text_dim": "#009c11",  # bumped from #008f11: 4.09:1 on tab_bg #1a1a1a failed WCAG AA; now 4.78:1
        "border": "#333333",          # Lead Grey
        "panel": "#0a0a0a",
        "tab_bg": "#1a1a1a",
        "accent": "#8a2be2",          # Astro Violet
        "success": "#00ff41",
        "warning": "#ffea00",
        "error": "#ff3131"            # Signal Red
    },
    "Cyber Synthwave": {
        "background": "#0d0115",      # Deep Void Indigo
        "primary": "#ff007f",         # Neon Hot Pink
        "primary_hover": "#e60072",
        "primary_pressed": "#cc0065",
        "text": "#00f0ff",            # Cyber Cyan
        "text_dim": "#009bb3",
        "border": "#2c163f",          # Dark Cyber Violet
        "panel": "#140520",           # Cyber Panel Purple
        "tab_bg": "#1d0c2c",
        "accent": "#ff8c00",          # Neon Amber
        "success": "#39ff14",         # Radioactive Green
        "warning": "#ffff33",
        "error": "#ff073a"            # Neon Red
    },
    "Astro Emerald": {
        "background": "#020f12",      # Astral Deep Teal
        "primary": "#00ffd0",         # Aurora Turquoise
        "primary_hover": "#00e6bc",
        "primary_pressed": "#00cca7",
        "text": "#adff2f",            # Cosmic Lime
        "text_dim": "#7cb321",
        "border": "#0e292d",          # Solar Dark Teal
        "panel": "#05181b",
        "tab_bg": "#092429",
        "accent": "#ff0055",          # Solar Flare Magenta
        "success": "#00ffd0",
        "warning": "#ffd700",         # Supernova Gold
        "error": "#ff4500"
    },
    "Classic Dark": {
        "background": "#121212",
        "primary": "#1976D2",
        "primary_hover": "#1E88E5",
        "primary_pressed": "#0D47A1",
        "text": "#E0E0E0",
        "text_dim": "#9E9E9E",
        "border": "#404040",
        "panel": "#1E1E1E",
        "tab_bg": "#252525",
        "accent": "#00B0FF",
        "success": "#66BB6A",
        "warning": "#FFA726",
        "error": "#EF5350"
    },
    "Sleek Dark Mode": {
        "background": "#121214",
        "primary": "#00F0FF",
        "primary_hover": "#00D7E6",
        "primary_pressed": "#00C3CF",
        "text": "#E0E0E5",
        "text_dim": "#8A8A95",
        "border": "#222226",
        "panel": "#1A1A1E",
        "tab_bg": "#141418",
        "accent": "#FF3366",
        "success": "#39FF14",
        "warning": "#FFEA00",
        "error": "#FF3366"
    }
}

for _name, _tokens in THEMES.items():
    _missing = REQUIRED_TOKENS - _tokens.keys()
    if _missing:
        raise ValueError(f"Theme '{_name}' is missing required token(s): {sorted(_missing)}")


class ThemeManager(QObject):
    """Handles the high-contrast Forensic Neon theme for the Desktop Client."""

    # Emitted with the new theme's color dict whenever the active theme changes,
    # so tabs that paint outside the global QSS cascade (custom setStyleSheet
    # calls, matplotlib canvases) can repaint themselves in step.
    theme_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("Operator", "LotteryEngine")
        self.themes = THEMES

        stored_theme = self.settings.value("current_theme", DEFAULT_THEME)
        if stored_theme not in self.themes:
            logger.warning(
                "Persisted theme '%s' is not registered; falling back to '%s'.",
                stored_theme, DEFAULT_THEME,
            )
            stored_theme = DEFAULT_THEME
        self.current_theme = stored_theme

    def get_colors(self, theme_name=None) -> dict:
        """Returns the color token dict for `theme_name` (or the active theme)."""
        name = theme_name if theme_name is not None else self.current_theme
        colors = self.themes.get(name)
        if colors is None:
            logger.warning("Unknown theme '%s' requested; falling back to '%s'.", name, DEFAULT_THEME)
            colors = self.themes[DEFAULT_THEME]
        return colors

    def set_theme(self, theme_name: str):
        """Persists the theme choice and notifies subscribers via `theme_changed`."""
        if theme_name not in self.themes:
            logger.warning("Refusing to switch to unknown theme '%s'; keeping '%s'.", theme_name, self.current_theme)
            return
        self.settings.setValue("current_theme", theme_name)
        self.current_theme = theme_name
        self.theme_changed.emit(self.get_colors(theme_name))

    def generate_stylesheet(self, theme_name=None):
        theme = self.get_colors(theme_name)

        return f"""
            QMainWindow {{
                background-color: {theme['background']};
            }}
            QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
                font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                background-color: {theme['panel']};
            }}
            QTabBar::tab {{
                background-color: {theme['tab_bg']};
                border: 1px solid {theme['border']};
                padding: 8px 12px;
                color: {theme['text_dim']};
            }}
            QTabBar::tab:selected {{
                background-color: {theme['panel']};
                color: {theme['text']};
                border-bottom: 2px solid {theme['primary']};
            }}
            QPushButton {{
                background-color: {theme['panel']};
                color: {theme['primary']};
                border: 1px solid {theme['primary']};
                border-radius: 4px;
                padding: 8px 16px;
                text-transform: uppercase;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['primary']};
                color: {theme['background']};
            }}
            QPushButton:pressed {{
                background-color: {theme['primary_pressed']};
            }}
            QTextEdit, QLineEdit {{
                background-color: {theme['panel']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 2px;
            }}
            QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {theme['panel']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 2px;
                padding: 4px;
            }}
            QGroupBox {{
                border: 1px solid {theme['border']};
                border-radius: 4px;
                margin-top: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
                color: {theme['accent']};
            }}
            QHeaderView::section {{
                background-color: {theme['tab_bg']};
                color: {theme['text']};
                padding: 4px;
                border: 1px solid {theme['border']};
            }}
            QTableView {{
                gridline-color: {theme['border']};
                border: 1px solid {theme['border']};
            }}
            QTreeWidget, QListWidget {{
                background-color: {theme['panel']};
                border: 1px solid {theme['border']};
            }}
            QProgressBar {{
                border: 1px solid {theme['border']};
                border-radius: 2px;
                text-align: center;
                background-color: {theme['tab_bg']};
            }}
            QProgressBar::chunk {{
                background-color: {theme['primary']};
                width: 10px;
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QMenuBar {{
                background-color: {theme['tab_bg']};
                color: {theme['text']};
                border-bottom: 1px solid {theme['border']};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 10px;
                color: {theme['text_dim']};
            }}
            QMenuBar::item:selected {{
                background-color: {theme['primary']};
                color: {theme['background']};
            }}
            QMenu {{
                background-color: {theme['panel']};
                border: 1px solid {theme['border']};
                color: {theme['text']};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {theme['primary']};
                color: {theme['background']};
            }}
            QCheckBox {{
                color: {theme['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme['border']};
                background-color: {theme['panel']};
                border-radius: 2px;
            }}
            QCheckBox::indicator:hover {{
                border-color: {theme['primary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['primary']};
                border: 2px solid {theme['panel']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {theme['tab_bg']};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme['border']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {theme['tab_bg']};
                height: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {theme['border']};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme['primary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
            QTableWidget {{
                gridline-color: {theme['border']};
                border: 1px solid {theme['border']};
                background-color: {theme['panel']};
                alternate-background-color: {theme['tab_bg']};
            }}
        """


