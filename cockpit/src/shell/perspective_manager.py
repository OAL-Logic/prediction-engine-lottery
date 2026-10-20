"""
Perspective Manager
===================
Orchestrates seamless switching across Cockpit perspectives:
- Express (1-Click archetypes & diagnostic HUD)
- Studio (105+ combinatorial filters & wheeling lab)
- Esoteric (2D/3D Chaos & Ephemeris Observatory)
- Lab (Draw database, skips analytics & backtesting)
- Printer (Caixa physical betslip calibrator)
"""

from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

from cockpit.src.core.models import PerspectiveType


class PerspectiveManager(QObject):
    """
    Coordinates active view states and broadcasts perspective transitions.
    """

    perspective_changed = Signal(str)  # Emits perspective name

    def __init__(self, stack: QStackedWidget):
        super().__init__()
        self.stack = stack
        self._perspectives: Dict[PerspectiveType, QWidget] = {}
        self._current_perspective: PerspectiveType = PerspectiveType.EXPRESS

    def register_perspective(self, p_type: PerspectiveType, widget: QWidget) -> None:
        """Registers a view widget to a perspective type."""
        self._perspectives[p_type] = widget
        self.stack.addWidget(widget)

    @property
    def current_perspective(self) -> PerspectiveType:
        return self._current_perspective

    def switch_perspective(self, p_type: PerspectiveType | str) -> None:
        """Switches the active perspective in the central stack."""
        if isinstance(p_type, str):
            p_type = PerspectiveType(p_type)
        if p_type in self._perspectives:
            self._current_perspective = p_type
            target_widget = self._perspectives[p_type]
            self.stack.setCurrentWidget(target_widget)
            self.perspective_changed.emit(p_type.value)
