"""Application shell components."""
from desktop.src.shell.theme_manager import ThemeManager, DEFAULT_THEME_NAME, THEME_PALETTES
from desktop.src.shell.docking_manager import DockingManager, DockDescriptor
from desktop.src.shell.perspective_manager import PerspectiveManager, PerspectiveType
from desktop.src.shell.main_window import CockpitMainWindow

__all__ = [
    "ThemeManager",
    "DEFAULT_THEME_NAME",
    "THEME_PALETTES",
    "DockingManager",
    "DockDescriptor",
    "PerspectiveManager",
    "PerspectiveType",
    "CockpitMainWindow",
]
