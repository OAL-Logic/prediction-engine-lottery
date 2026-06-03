from PySide6.QtCore import QSettings
import json

class ThemeManager:
    """Handles the high-contrast Forensic Neon theme for the Desktop Client."""
    
    def __init__(self):
        self.settings = QSettings("Operator", "LotteryEngine")
        self.themes = {
            "Forensic Neon": {
                "background": "#000000",      # Obsidian Black
                "primary": "#00ff41",         # Matrix Green
                "primary_hover": "#00e63a",
                "primary_pressed": "#00cc33",
                "text": "#00ff41",            # Neon Green
                "text_dim": "#008f11",
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
                "border": "#404040",
                "panel": "#1E1E1E",
                "tab_bg": "#252525",
                "accent": "#00B0FF",
                "success": "#66BB6A",
                "warning": "#FFA726",
                "error": "#EF5350"
            }
        }
        self.current_theme = self.settings.value("current_theme", "Cyber Synthwave")

    def generate_stylesheet(self, theme_name=None):
        theme = self.themes.get(theme_name or self.current_theme, self.themes["Cyber Synthwave"])
        
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
        """

