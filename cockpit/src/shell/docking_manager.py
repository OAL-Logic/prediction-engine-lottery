"""
Docking Manager
===============
Provides multi-monitor workspace layout management using PySide6 QDockWidget.
Supports floating, tiling, tabbing, multi-monitor detaching, and QSettings
state persistence across application sessions.
"""

from typing import Dict, Optional, List
from PySide6.QtCore import Qt, QSettings, QByteArray
from PySide6.QtWidgets import QMainWindow, QDockWidget, QMenu, QWidget


class DockingManager:
    """
    Coordinates modular QDockWidgets across multiple monitors.
    """

    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.settings = QSettings("Operator", "LotteryEngineCockpitV2")
        self._docks: Dict[str, QDockWidget] = {}

    def register_dock(
        self,
        dock_id: str,
        title: str,
        widget: QWidget,
        area: Qt.DockWidgetArea = Qt.RightDockWidgetArea,
        allowed_areas: Qt.DockWidgetAreas = Qt.AllDockWidgetAreas
    ) -> QDockWidget:
        """Creates and registers a dock panel."""
        dock = QDockWidget(title, self.main_window)
        dock.setObjectName(dock_id)
        dock.setWidget(widget)
        dock.setAllowedAreas(allowed_areas)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )
        self.main_window.addDockWidget(area, dock)
        self._docks[dock_id] = dock
        return dock

    def get_dock(self, dock_id: str) -> Optional[QDockWidget]:
        return self._docks.get(dock_id)

    def populate_view_menu(self, menu: QMenu) -> None:
        """Populates View menu with toggleable actions for all registered docks."""
        for dock in self._docks.values():
            action = dock.toggleViewAction()
            menu.addAction(action)

    def save_state(self, key_suffix: str = "default") -> None:
        """Saves dock arrangement and window state to QSettings."""
        state = self.main_window.saveState()
        self.settings.setValue(f"dock_state_{key_suffix}", state)

    def restore_state(self, key_suffix: str = "default") -> bool:
        """Restores saved dock arrangement from QSettings."""
        state = self.settings.value(f"dock_state_{key_suffix}")
        if state and isinstance(state, (QByteArray, bytes)):
            return self.main_window.restoreState(state)
        return False
