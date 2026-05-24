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
        self.current_theme = self.settings.value("current_theme", "Forensic Neon")

    def generate_stylesheet(self, theme_name=None):
        theme = self.themes.get(theme_name or self.current_theme, self.themes["Forensic Neon"])
        
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
                border-radius: 2px;
                padding: 6px 12px;
                text-transform: uppercase;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['primary']};
                color: {theme['background']};
            }}
            QTextEdit {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                gridline-color: {theme['border']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
        """
