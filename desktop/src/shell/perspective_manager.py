"""
Global Perspective Manager
==========================
Coordinates layout perspectives:
1. Quick / Express Mode (Rapid generation, 6-layer diagnostic scan, receipt viewer)
2. Advanced Studio Mode (Combinatorial Lab, 105+ filter graph, fault tolerance, wheeling)
3. Analysis & Verification Lab (Draw database hub, skip/gap analytics, closed-loop backtesting)
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional, Callable

from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget

logger = logging.getLogger(__name__)


class PerspectiveType(str, Enum):
    EXPRESS = "Quick / Express"
    STUDIO = "Advanced Studio"
    LAB = "Analysis & Verification"


class PerspectiveManager(QObject):
    """
    Manages switching across perspectives, reconfiguring active docks,
    central stacked workspaces, and toolbar actions seamlessly.
    """

    perspective_changed = Signal(str)  # Emits new perspective name

    def __init__(self, main_window: QMainWindow, central_stack: QStackedWidget):
        super().__init__()
        self.main_window = main_window
        self.central_stack = central_stack
        self.settings = QSettings("Operator", "LotteryEngineCockpit")
        
        # Perspective index mapping in central stack
        self._perspective_indices: Dict[PerspectiveType, int] = {}
        # Perspective dock visibility configuration
        self._perspective_docks: Dict[PerspectiveType, List[str]] = {
            PerspectiveType.EXPRESS: ["ticket_store", "quick_diagnostics", "telemetry"],
            PerspectiveType.STUDIO: [
                "pool_builder", "filter_builder", "fault_tolerance",
                "wheeling_studio", "ticket_store", "telemetry"
            ],
            PerspectiveType.LAB: [
                "database_hub", "trend_analytics", "ticket_auditor", "telemetry"
            ],
        }

        saved_perspective = self.settings.value("active_perspective", PerspectiveType.EXPRESS.value)
        try:
            self._current_perspective = PerspectiveType(saved_perspective)
        except ValueError:
            self._current_perspective = PerspectiveType.EXPRESS

    @property
    def current_perspective(self) -> PerspectiveType:
        return self._current_perspective

    def register_workspace(self, perspective: PerspectiveType, widget: QWidget) -> int:
        """Registers a central perspective view in the central stacked widget."""
        idx = self.central_stack.addWidget(widget)
        self._perspective_indices[perspective] = idx
        return idx

    def set_perspective_docks(self, perspective: PerspectiveType, dock_ids: List[str]) -> None:
        """Overrides the visible dock IDs for a perspective."""
        self._perspective_docks[perspective] = dock_ids

    def switch_perspective(self, perspective: PerspectiveType) -> None:
        """Transitions application state to the requested perspective."""
        self._current_perspective = perspective
        self.settings.setValue("active_perspective", perspective.value)

        # 1. Switch central stack view
        if perspective in self._perspective_indices:
            self.central_stack.setCurrentIndex(self._perspective_indices[perspective])

        # 2. Reconfigure dock visibility via main window's dock manager
        dock_manager = getattr(self.main_window, "docking_manager", None)
        if dock_manager:
            visible_docks = self._perspective_docks.get(perspective, [])
            dock_manager.show_docks(visible_docks)

        logger.info("Switched to perspective: %s", perspective.value)
        self.perspective_changed.emit(perspective.value)
