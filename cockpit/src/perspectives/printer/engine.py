"""
Betslip Printing & PDF Generation Engine
========================================
High-precision coordinate transform engine (Millimeters -> Device Pixels).
Supports:
- Vector rendering to QPainter (QPrinter, QPdfWriter, QImage)
- Optical registration dash marks for physical optical lottery scanners
- Millimeter calibration test sheets with alignment crosshairs and rulers
- Multi-page batch ticket pagination
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PySide6.QtCore import Qt, QRectF, QPointF, QMarginsF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QImage,
    QPdfWriter,
    QPageSize,
    QPageLayout,
)
from PySide6.QtPrintSupport import QPrinter

from .models import BetslipTemplate


def mm_to_px(mm: float, dpi: float) -> float:
    """Converts millimeters to device pixels given target DPI."""
    return mm * (dpi / 25.4)


def px_to_mm(px: float, dpi: float) -> float:
    """Converts device pixels to millimeters given target DPI."""
    return px * (25.4 / dpi)


class BetslipPrintEngine:
    """
    Core printing and rendering service for physical lottery slips.
    """

    @staticmethod
    def render_slip(
        painter: QPainter,
        template: BetslipTemplate,
        tickets_for_slip: List[List[int]],
        dpi: float = 300.0,
        show_guides: bool = True,
        is_preview: bool = False,
    ) -> None:
        """
        Renders a single betslip (paper boundary, panels, marks) to a QPainter.
        """
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        width_px = mm_to_px(template.slip_width_mm, dpi)
        height_px = mm_to_px(template.slip_height_mm, dpi)

        # 1. Background paper
        if is_preview:
            # Subtle cream paper color representing physical lottery ticket
            paper_rect = QRectF(0, 0, width_px, height_px)
            painter.fillRect(paper_rect, QColor("#FBF9F1"))
            painter.setPen(QPen(QColor("#D0CBC0"), 1.5))
            painter.drawRoundedRect(paper_rect, 8.0, 8.0)
        
        # 2. Draw template guides if enabled (for alignment on plain paper or preview)
        if show_guides:
            font_size = max(6, int(dpi * 0.024))
            guide_font = QFont("Helvetica", font_size)
            guide_font.setWeight(QFont.Weight.Normal)
            painter.setFont(guide_font)

            for panel_idx in range(template.panels_per_slip):
                panel_y_start = template.origin_y_mm + (panel_idx * template.panel_gap_y_mm)
                panel_h = (template.rows - 1) * template.pitch_y_mm + template.mark_height_mm + 4.0
                panel_w = (template.cols - 1) * template.pitch_x_mm + template.mark_width_mm + 6.0
                
                # Panel boundary outline
                bx = mm_to_px(template.origin_x_mm - 3.0, dpi)
                by = mm_to_px(panel_y_start - 3.0, dpi)
                bw = mm_to_px(panel_w, dpi)
                bh = mm_to_px(panel_h, dpi)
                painter.setPen(QPen(QColor("#E2DDD2"), 1, Qt.PenStyle.DashLine))
                painter.drawRect(QRectF(bx, by, bw, bh))

                # Panel header label
                painter.setPen(QPen(QColor("#8A8172")))
                lbl_font = QFont("Helvetica", max(7, int(dpi * 0.028)), QFont.Weight.Bold)
                painter.setFont(lbl_font)
                painter.drawText(
                    QRectF(bx, by - mm_to_px(4.0, dpi), bw, mm_to_px(4.0, dpi)),
                    int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                    f"Jogo {panel_idx + 1}"
                )
                painter.setFont(guide_font)

                # Draw faint cell guides with number labels
                total_cells = template.rows * template.cols
                for i in range(total_cells):
                    ball_num = i + template.number_offset
                    pos = template.calculate_mark_position_mm(panel_idx, ball_num)
                    if not pos:
                        continue
                    cx, cy = pos
                    cx_px = mm_to_px(cx, dpi)
                    cy_px = mm_to_px(cy, dpi)
                    cell_w_px = mm_to_px(template.pitch_x_mm * 0.85, dpi)
                    cell_h_px = mm_to_px(template.pitch_y_mm * 0.85, dpi)

                    # Soft oval / rect guide
                    painter.setPen(QPen(QColor("#E8E4DA"), 1))
                    cell_rect = QRectF(cx_px - cell_w_px / 2, cy_px - cell_h_px / 2, cell_w_px, cell_h_px)
                    painter.drawRoundedRect(cell_rect, 2.0, 2.0)

                    # Number label
                    painter.setPen(QPen(QColor("#A0988A")))
                    painter.drawText(cell_rect, int(Qt.AlignmentFlag.AlignCenter), f"{ball_num:02d}")

        # 3. Draw Optical Marks for each ticket assigned to this slip
        mark_w_px = mm_to_px(template.mark_width_mm, dpi)
        mark_h_px = mm_to_px(template.mark_height_mm, dpi)
        mark_brush = QBrush(QColor("#111111")) # Solid deep optical black
        painter.setBrush(mark_brush)
        painter.setPen(Qt.PenStyle.NoPen)

        for panel_idx, ticket in enumerate(tickets_for_slip):
            if panel_idx >= template.panels_per_slip:
                break
            for ball in ticket:
                pos = template.calculate_mark_position_mm(panel_idx, ball)
                if not pos:
                    continue
                cx_mm, cy_mm = pos
                cx_px = mm_to_px(cx_mm, dpi)
                cy_px = mm_to_px(cy_mm, dpi)

                mark_rect = QRectF(cx_px - mark_w_px / 2, cy_px - mark_h_px / 2, mark_w_px, mark_h_px)

                if template.mark_style == "rectangle":
                    painter.drawRect(mark_rect)
                elif template.mark_style == "oval":
                    painter.drawEllipse(mark_rect)
                elif template.mark_style == "cross":
                    painter.setPen(QPen(QColor("#111111"), 2.0))
                    painter.drawLine(mark_rect.topLeft(), mark_rect.bottomRight())
                    painter.drawLine(mark_rect.topRight(), mark_rect.bottomLeft())
                    painter.setPen(Qt.PenStyle.NoPen)
                else: # default dash
                    painter.drawRoundedRect(mark_rect, 1.0, 1.0)

        # 4. Header title / footer receipt if preview
        if is_preview:
            painter.setPen(QPen(QColor("#595244")))
            title_font = QFont("Helvetica", max(8, int(dpi * 0.032)), QFont.Weight.Bold)
            painter.setFont(title_font)
            painter.drawText(
                QRectF(mm_to_px(6, dpi), mm_to_px(6, dpi), width_px - mm_to_px(12, dpi), mm_to_px(14, dpi)),
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                f"{template.name.upper()}\n[Physical Betslip Calibrator]"
            )

        painter.restore()

    @staticmethod
    def render_calibration_sheet(
        painter: QPainter,
        template: BetslipTemplate,
        dpi: float = 300.0,
    ) -> None:
        """
        Renders a full millimeter calibration page.
        Draws precise metric rulers and crosshairs at key coordinates so
        users can measure feed alignment against their physical betslip.
        """
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        width_px = mm_to_px(template.slip_width_mm, dpi)
        height_px = mm_to_px(template.slip_height_mm, dpi)

        # Background
        painter.fillRect(QRectF(0, 0, width_px, height_px), QColor("#FFFFFF"))
        painter.setPen(QPen(QColor("#000000"), 1.0))

        # --- Top Millimeter Ruler ---
        ruler_font = QFont("Courier", max(5, int(dpi * 0.020)))
        painter.setFont(ruler_font)
        for mm in range(0, int(template.slip_width_mm) + 1):
            x = mm_to_px(mm, dpi)
            if mm % 10 == 0:
                painter.drawLine(QPointF(x, 0), QPointF(x, mm_to_px(5.0, dpi)))
                painter.drawText(QPointF(x + 2, mm_to_px(4.0, dpi)), f"{mm}")
            elif mm % 5 == 0:
                painter.drawLine(QPointF(x, 0), QPointF(x, mm_to_px(3.5, dpi)))
            else:
                painter.drawLine(QPointF(x, 0), QPointF(x, mm_to_px(2.0, dpi)))

        # --- Left Millimeter Ruler ---
        for mm in range(0, int(template.slip_height_mm) + 1):
            y = mm_to_px(mm, dpi)
            if mm % 10 == 0:
                painter.drawLine(QPointF(0, y), QPointF(mm_to_px(5.0, dpi), y))
                painter.drawText(QPointF(mm_to_px(2.0, dpi), y - 2), f"{mm}")
            elif mm % 5 == 0:
                painter.drawLine(QPointF(0, y), QPointF(mm_to_px(3.5, dpi), y))
            else:
                painter.drawLine(QPointF(0, y), QPointF(mm_to_px(2.0, dpi), y))

        # --- Alignment Crosshairs ---
        def draw_crosshair(x_mm: float, y_mm: float, label: str):
            cx = mm_to_px(x_mm, dpi)
            cy = mm_to_px(y_mm, dpi)
            r = mm_to_px(4.0, dpi)
            painter.setPen(QPen(QColor("#E63946"), 1.2)) # Crisp Red
            painter.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
            painter.drawLine(QPointF(cx, cy - r), QPointF(cx, cy + r))
            painter.drawEllipse(QPointF(cx, cy), mm_to_px(1.5, dpi), mm_to_px(1.5, dpi))
            painter.setPen(QPen(QColor("#333333"), 1.0))
            painter.drawText(QPointF(cx + r + 2, cy + 3), label)

        # Crosshair at Panel 1 Origin (First number)
        draw_crosshair(template.origin_x_mm, template.origin_y_mm, f"Origin 1 ({template.origin_x_mm:.1f}, {template.origin_y_mm:.1f})")

        # Crosshairs at Panel corners
        for p in range(template.panels_per_slip):
            # Top-left ball
            p1_pos = template.calculate_mark_position_mm(p, template.number_offset)
            if p1_pos:
                draw_crosshair(p1_pos[0], p1_pos[1], f"P{p+1} Start")
            
            # Bottom-right ball
            last_num = template.rows * template.cols - 1 + template.number_offset
            last_pos = template.calculate_mark_position_mm(p, last_num)
            if last_pos:
                draw_crosshair(last_pos[0], last_pos[1], f"P{p+1} End")

        # Instruction Box
        info_font = QFont("Helvetica", max(6, int(dpi * 0.024)))
        painter.setFont(info_font)
        painter.setPen(QPen(QColor("#2B2D42")))
        info_text = (
            f"TEMPLATE: {template.name}\n"
            f"Width: {template.slip_width_mm}mm | Height: {template.slip_height_mm}mm\n"
            f"Pitch: X={template.pitch_x_mm:.2f}mm, Y={template.pitch_y_mm:.2f}mm\n"
            f"Offset: X={template.hardware_offset_x_mm:+.2f}mm, Y={template.hardware_offset_y_mm:+.2f}mm\n"
            f"Scale: X={template.scale_x:.3f}, Y={template.scale_y:.3f}\n"
            "ALIGNMENT: Place this printout on top of your physical betslip.\n"
            "Check that crosshairs align with the number boxes."
        )
        info_rect = QRectF(
            mm_to_px(8.0, dpi),
            mm_to_px(template.slip_height_mm - 32.0, dpi),
            width_px - mm_to_px(16.0, dpi),
            mm_to_px(30.0, dpi),
        )
        painter.drawRect(info_rect)
        painter.drawText(info_rect.adjusted(6, 4, -6, -4), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop), info_text)

        painter.restore()

    @staticmethod
    def render_preview_image(
        template: BetslipTemplate,
        tickets_for_slip: List[List[int]],
        dpi: float = 150.0,
        show_guides: bool = True,
    ) -> QImage:
        """
        Creates a high-fidelity QImage preview of a betslip page.
        """
        width_px = int(mm_to_px(template.slip_width_mm, dpi))
        height_px = int(mm_to_px(template.slip_height_mm, dpi))
        
        image = QImage(width_px, height_px, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        BetslipPrintEngine.render_slip(
            painter=painter,
            template=template,
            tickets_for_slip=tickets_for_slip,
            dpi=dpi,
            show_guides=show_guides,
            is_preview=True,
        )
        painter.end()
        return image

    @staticmethod
    def export_pdf(
        filepath: str,
        template: BetslipTemplate,
        tickets: List[List[int]],
        show_guides: bool = False,
        dpi: float = 300.0,
    ) -> None:
        """
        Generates a multi-page PDF document containing all tickets formatted
        for direct feeding into printer slip trays.
        """
        writer = QPdfWriter(filepath)
        writer.setResolution(int(dpi))
        
        # Configure custom slip page size in millimeters
        page_size = QPageSize(
            QRectF(0, 0, template.slip_width_mm, template.slip_height_mm).size(),
            QPageSize.Unit.Millimeter,
            name="CaixaBetslip",
        )
        layout = QPageLayout(
            page_size,
            QPageLayout.Orientation.Portrait,
            QMarginsF(0.0, 0.0, 0.0, 0.0),
        )
        writer.setPageLayout(layout)

        painter = QPainter(writer)
        
        # Paginate tickets: chunk by panels_per_slip
        panels = template.panels_per_slip
        num_tickets = len(tickets)
        total_pages = math.ceil(num_tickets / panels) if num_tickets > 0 else 1

        for page_idx in range(total_pages):
            if page_idx > 0:
                writer.newPage()
            
            start_t = page_idx * panels
            end_t = min(start_t + panels, num_tickets)
            page_tickets = tickets[start_t:end_t]

            BetslipPrintEngine.render_slip(
                painter=painter,
                template=template,
                tickets_for_slip=page_tickets,
                dpi=dpi,
                show_guides=show_guides,
                is_preview=False,
            )

        painter.end()
