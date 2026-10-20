"""
Multi-Monitor Docking Subsystem
===============================
Manages PySide6 QDockWidget panels with support for detaching, floating,
tabbed tiling, and persistence across multiple monitors and application sessions.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QMainWindow, QDockWidget, QWidget, QMenu
from PySide6.QtCore import Qt, QSettings, QByteArray

logger = logging.getLogger(__name__)


@dataclass
class DockDescriptor:
    """Metadata specification for a dockable panel."""
    id: str
    title: str
    widget: QWidget
    default_area: Qt.DockWidgetArea
    allowed_areas: Qt.DockWidgetAreas = Qt.AllDockWidgetAreas
    features: QDockWidget.DockWidgetFeatures = (
        QDockWidget.DockWidgetMovable |
        QDockWidget.DockWidgetFloatable |
        QDockWidget.DockWidgetClosable
    )


class DockingManager:
    """
    Orchestrates dock widgets on a QMainWindow, handling persistence,
    multi-monitor floating, and perspective-based panel visibility.
    """

    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.docks: Dict[str, QDockWidget] = {}
        self.descriptors: Dict[str, DockDescriptor] = {}
        self.settings = QSettings("Operator", "LotteryEngineCockpit")

        # Configure Main Window Docking behavior
        self.main_window.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks |
            QMainWindow.GroupedDragging
        )
        from PySide6.QtWidgets import QTabWidget
        self.main_window.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)

    def register_panel(self, descriptor: DockDescriptor) -> QDockWidget:
        """Instantiates and mounts a dock widget into the main window."""
        dock = QDockWidget(descriptor.title, self.main_window)
        dock.setObjectName(f"Dock_{descriptor.id}")
        dock.setWidget(descriptor.widget)
        dock.setAllowedAreas(descriptor.allowed_areas)
        dock.setFeatures(descriptor.features)

        self.main_window.addDockWidget(descriptor.default_area, dock)
        self.docks[descriptor.id] = dock
        self.descriptors[descriptor.id] = descriptor
        return dock

    def get_dock(self, panel_id: str) -> Optional[QDockWidget]:
        """Retrieves a registered dock widget by panel ID."""
        return self.docks.get(panel_id)

    def set_dock_visible(self, panel_id: str, visible: bool) -> None:
        """Toggles visibility of a specific dock."""
        dock = self.docks.get(panel_id)
        if dock:
            dock.setVisible(visible)

    def show_docks(self, panel_ids: List[str]) -> None:
        """Displays specified docks, hiding all others."""
        target_set = set(panel_ids)
        for pid, dock in self.docks.items():
            dock.setVisible(pid in target_set)

    def populate_view_menu(self, menu: QMenu) -> None:
        """Generates dynamic View -> Panels checkable menu actions."""
        menu.clear()
        for pid, dock in self.docks.items():
            desc = self.descriptors.get(pid)
            title = desc.title if desc else pid
            action = dock.toggleViewAction()
            action.setText(title)
            menu.addAction(action)

    def save_state(self, key: str = "default_layout") -> None:
        """Persists dock layout and geometry to QSettings."""
        state = self.main_window.saveState()
        self.settings.setValue(f"dock_state_{key}", state)
        logger.debug("Dock state saved under key '%s'", key)

    def restore_state(self, key: str = "default_layout") -> bool:
        """Restores dock layout and geometry from QSettings."""
        state: Optional[QByteArray] = self.settings.value(f"dock_state_{key}")
        if state is not None and isinstance(state, (QByteArray, bytes)):
            success = self.main_window.restoreState(state)
            logger.debug("Dock state restored for key '%s': %s", key, success)
            return success
        return False
