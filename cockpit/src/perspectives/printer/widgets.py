"""
Betslip Preview & Interactive Calibration Canvas Widget
======================================================
Interactive QWidget displaying high-resolution betslip preview with:
- Metric grid overlay and alignment crosshairs
- Real-time mouse position readout in exact millimeters
- Interactive slip zoom controls
- Toggle between Optical Ticket Marks and Millimeter Calibration Sheet
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QImage, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget, QSizePolicy

from .models import BetslipTemplate
from .engine import BetslipPrintEngine, px_to_mm, mm_to_px


class BetslipCanvasWidget(QWidget):
    """
    Renders the calibrated betslip on screen with smooth QPainter scaling.
    """
    coordinates_changed = Signal(float, float)  # Emits (x_mm, y_mm) on mouse move
    origin_dragged = Signal(float, float)       # Emits (new_origin_x, new_origin_y) on drag

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

        self._template: BetslipTemplate = BetslipTemplate()
        self._tickets: List[List[int]] = []
        self._current_page: int = 0
        self._show_guides: bool = True
        self._show_calibration_sheet: bool = False
        self._zoom_factor: float = 1.0
        self._cached_pixmap: Optional[QPixmap] = None
        
        self._dragging_origin: bool = False
        self._drag_start_origin: Tuple[float, float] = (0.0, 0.0)
        self._drag_start_pos: QPointF = QPointF()

    def set_template(self, template: BetslipTemplate) -> None:
        self._template = template
        self._cached_pixmap = None
        self.update()

    def set_tickets(self, tickets: List[List[int]]) -> None:
        self._tickets = tickets
        self._current_page = 0
        self._cached_pixmap = None
        self.update()

    def set_page(self, page_index: int) -> None:
        self._current_page = max(0, page_index)
        self._cached_pixmap = None
        self.update()

    def set_show_guides(self, show: bool) -> None:
        self._show_guides = show
        self._cached_pixmap = None
        self.update()

    def set_show_calibration_sheet(self, show: bool) -> None:
        self._show_calibration_sheet = show
        self._cached_pixmap = None
        self.update()

    def set_zoom(self, zoom: float) -> None:
        self._zoom_factor = max(0.5, min(3.0, zoom))
        self.update()

    def _get_page_tickets(self) -> List[List[int]]:
        """Returns the tickets that belong on the active slip page."""
        panels = self._template.panels_per_slip
        start_idx = self._current_page * panels
        end_idx = min(start_idx + panels, len(self._tickets))
        return self._tickets[start_idx:end_idx]

    def _calculate_render_rect(self) -> Tuple[QRectF, float]:
        """
        Calculates destination rect on screen keeping aspect ratio centered.
        Returns (target_rect, effective_scale).
        """
        slip_w = self._template.slip_width_mm
        slip_h = self._template.slip_height_mm

        w = self.width() - 40
        h = self.height() - 40
        if w <= 10 or h <= 10:
            return (QRectF(), 1.0)

        scale_fit = min(w / slip_w, h / slip_h)
        scale = scale_fit * self._zoom_factor

        target_w = slip_w * scale
        target_h = slip_h * scale
        target_x = (self.width() - target_w) / 2
        target_y = (self.height() - target_h) / 2

        return (QRectF(target_x, target_y, target_w, target_h), scale)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        target_rect, scale = self._calculate_render_rect()
        if target_rect.isEmpty():
            painter.end()
            return

        # Render backing shadow
        shadow_rect = target_rect.translated(4, 6)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 40))

        # Render preview offscreen at high DPI then paint onto target_rect
        preview_dpi = 160.0
        if self._show_calibration_sheet:
            img_w = int(mm_to_px(self._template.slip_width_mm, preview_dpi))
            img_h = int(mm_to_px(self._template.slip_height_mm, preview_dpi))
            img = QImage(img_w, img_h, QImage.Format.Format_ARGB32_Premultiplied)
            img.fill(Qt.GlobalColor.white)
            img_p = QPainter(img)
            BetslipPrintEngine.render_calibration_sheet(img_p, self._template, dpi=preview_dpi)
            img_p.end()
        else:
            page_tickets = self._get_page_tickets()
            img = BetslipPrintEngine.render_preview_image(
                self._template,
                page_tickets,
                dpi=preview_dpi,
                show_guides=self._show_guides,
            )

        painter.drawImage(target_rect, img)

        # Draw red crosshair on Origin if in interactive calibrator mode
        ox_mm = self._template.origin_x_mm
        oy_mm = self._template.origin_y_mm
        ox_px = target_rect.x() + (ox_mm * scale)
        oy_px = target_rect.y() + (oy_mm * scale)

        painter.setPen(QPen(QColor("#E63946"), 1.5))
        painter.drawLine(QPointF(ox_px - 8, oy_px), QPointF(ox_px + 8, oy_px))
        painter.drawLine(QPointF(ox_px, oy_px - 8), QPointF(ox_px, oy_px + 8))
        painter.drawEllipse(QPointF(ox_px, oy_px), 4, 4)

        painter.end()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        target_rect, scale = self._calculate_render_rect()
        if not target_rect.isEmpty() and scale > 0:
            rel_x = event.position().x() - target_rect.x()
            rel_y = event.position().y() - target_rect.y()
            mm_x = rel_x / scale
            mm_y = rel_y / scale
            if 0 <= mm_x <= self._template.slip_width_mm and 0 <= mm_y <= self._template.slip_height_mm:
                self.coordinates_changed.emit(mm_x, mm_y)

        if self._dragging_origin:
            delta_px = event.position() - self._drag_start_pos
            delta_mm_x = delta_px.x() / scale
            delta_mm_y = delta_px.y() / scale
            new_ox = max(0.0, min(self._template.slip_width_mm, self._drag_start_origin[0] + delta_mm_x))
            new_oy = max(0.0, min(self._template.slip_height_mm, self._drag_start_origin[1] + delta_mm_y))
            self.origin_dragged.emit(new_ox, new_oy)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            target_rect, scale = self._calculate_render_rect()
            if not target_rect.isEmpty() and scale > 0:
                ox_px = target_rect.x() + (self._template.origin_x_mm * scale)
                oy_px = target_rect.y() + (self._template.origin_y_mm * scale)
                dist = ((event.position().x() - ox_px)**2 + (event.position().y() - oy_px)**2)**0.5
                if dist < 20: # Dragging origin
                    self._dragging_origin = True
                    self._drag_start_origin = (self._template.origin_x_mm, self._template.origin_y_mm)
                    self._drag_start_pos = event.position()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_origin = False
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.set_zoom(self._zoom_factor + 0.1)
            else:
                self.set_zoom(self._zoom_factor - 0.1)
            event.accept()
        else:
            super().wheelEvent(event)
