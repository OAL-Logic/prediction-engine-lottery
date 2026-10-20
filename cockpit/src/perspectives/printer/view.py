"""
Physical Betslip Studio & Caixa Calibrator Perspective View
===========================================================
Interactive studio for physical lottery slip calibration, PDF export,
and direct optical printing, prioritizing Brazilian Caixa Econômica Federal.
"""

from __future__ import annotations

import math
from typing import List, Optional, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QScrollArea,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from cockpit.src.core.models import GameSchema
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.services.file_io import TicketFileIO
from .models import BetslipTemplate, CAIXA_PRESETS
from .engine import BetslipPrintEngine
from .widgets import BetslipCanvasWidget


class PrinterPerspectiveView(QWidget):
    """
    Complete Caixa betslip calibrator, pagination studio, and printer interface.
    """
    tickets_loaded = Signal(int)

    def __init__(self, bridge: Optional[EngineBridge] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.bridge = bridge or EngineBridge()
        self._current_template: BetslipTemplate = CAIXA_PRESETS["Caixa Lotofácil"]
        self._tickets: List[List[int]] = []
        self._current_page: int = 0

        self._init_ui()
        self._load_sample_tickets()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 1. Header Bar
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        title_box = QVBoxLayout()
        title_lbl = QLabel("🖨️ Physical Betslip Studio & Caixa Calibrator")
        title_lbl.setStyleSheet("font-size: 17px; font-weight: bold;")
        sub_lbl = QLabel("Sub-millimeter thermal & inkjet printer alignment for Brazilian Caixa Econômica Federal slips")
        sub_lbl.setStyleSheet("font-size: 11px; opacity: 0.7;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        h_layout.addLayout(title_box)
        h_layout.addStretch()

        self.info_badge = QLabel("Template: Caixa Lotofácil | 0 Tickets Queued")
        self.info_badge.setStyleSheet(
            "background-color: rgba(30, 144, 255, 0.15); color: #1E90FF; "
            "padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 12px;"
        )
        h_layout.addWidget(self.info_badge)
        main_layout.addWidget(header)

        # 2. Main 3-column Splitter: [Calibration Controls] | [Interactive Slip Canvas] | [Ticket Queue]
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left Panel: Calibration Controls ---
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(320)
        left_scroll.setMaximumWidth(380)

        ctrl_container = QWidget()
        ctrl_layout = QVBoxLayout(ctrl_container)
        ctrl_layout.setSpacing(8)
        ctrl_layout.setContentsMargins(4, 4, 4, 4)

        # Preset Selector
        grp_preset = QGroupBox("Betslip Template Preset")
        p_lay = QVBoxLayout(grp_preset)
        self.combo_presets = QComboBox()
        for name in CAIXA_PRESETS.keys():
            self.combo_presets.addItem(name)
        self.combo_presets.addItem("Custom Template")
        self.combo_presets.currentTextChanged.connect(self._on_preset_changed)
        p_lay.addWidget(self.combo_presets)

        btn_reset_spec = QPushButton("🔄 Reset to Official Spec")
        btn_reset_spec.clicked.connect(self._reset_to_official_spec)
        p_lay.addWidget(btn_reset_spec)
        ctrl_layout.addWidget(grp_preset)

        # Slip Geometry
        grp_geom = QGroupBox("Slip Paper & Panels (mm)")
        g_lay = QVBoxLayout(grp_geom)

        h_dim = QHBoxLayout()
        self.spin_width = self._create_dspin(50.0, 300.0, 82.0, 0.5, "Width:")
        self.spin_height = self._create_dspin(50.0, 400.0, 155.0, 0.5, "Height:")
        h_dim.addLayout(self.spin_width[0])
        h_dim.addLayout(self.spin_height[0])
        g_lay.addLayout(h_dim)

        h_pan = QHBoxLayout()
        self.spin_panels = self._create_spin(1, 6, 3, 1, "Panels/Slip:")
        self.spin_panel_gap = self._create_dspin(0.0, 100.0, 34.5, 0.5, "Panel Step Y:")
        h_pan.addLayout(self.spin_panels[0])
        h_pan.addLayout(self.spin_panel_gap[0])
        g_lay.addLayout(h_pan)
        ctrl_layout.addWidget(grp_geom)

        # Grid Coordinates
        grp_grid = QGroupBox("Grid Calibration (mm)")
        grid_lay = QVBoxLayout(grp_grid)

        h_orig = QHBoxLayout()
        self.spin_origin_x = self._create_dspin(0.0, 100.0, 9.5, 0.1, "Origin X:")
        self.spin_origin_y = self._create_dspin(0.0, 100.0, 33.5, 0.1, "Origin Y:")
        h_orig.addLayout(self.spin_origin_x[0])
        h_orig.addLayout(self.spin_origin_y[0])
        grid_lay.addLayout(h_orig)

        h_pitch = QHBoxLayout()
        self.spin_pitch_x = self._create_dspin(1.0, 20.0, 4.8, 0.05, "Pitch X:")
        self.spin_pitch_y = self._create_dspin(1.0, 20.0, 4.2, 0.05, "Pitch Y:")
        h_pitch.addLayout(self.spin_pitch_x[0])
        h_pitch.addLayout(self.spin_pitch_y[0])
        grid_lay.addLayout(h_pitch)

        h_mark = QHBoxLayout()
        self.spin_mark_w = self._create_dspin(1.0, 10.0, 3.6, 0.1, "Mark W:")
        self.spin_mark_h = self._create_dspin(0.5, 10.0, 1.8, 0.1, "Mark H:")
        h_mark.addLayout(self.spin_mark_w[0])
        h_mark.addLayout(self.spin_mark_h[0])
        grid_lay.addLayout(h_mark)
        ctrl_layout.addWidget(grp_grid)

        # Printer Hardware Compensation
        grp_comp = QGroupBox("Printer Hardware Offset (mm)")
        comp_lay = QVBoxLayout(grp_comp)

        h_off = QHBoxLayout()
        self.spin_hw_x = self._create_dspin(-25.0, 25.0, 0.0, 0.1, "Offset X:")
        self.spin_hw_y = self._create_dspin(-25.0, 25.0, 0.0, 0.1, "Offset Y:")
        h_off.addLayout(self.spin_hw_x[0])
        h_off.addLayout(self.spin_hw_y[0])
        comp_lay.addLayout(h_off)

        h_scale = QHBoxLayout()
        self.spin_scale_x = self._create_dspin(0.800, 1.200, 1.000, 0.005, "Scale X:")
        self.spin_scale_y = self._create_dspin(0.800, 1.200, 1.000, 0.005, "Scale Y:")
        h_scale.addLayout(self.spin_scale_x[0])
        h_scale.addLayout(self.spin_scale_y[0])
        comp_lay.addLayout(h_scale)
        ctrl_layout.addWidget(grp_comp)

        ctrl_layout.addStretch()
        left_scroll.setWidget(ctrl_container)
        splitter.addWidget(left_scroll)

        # --- Center Panel: Interactive Slip Canvas & Controls ---
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(4, 4, 4, 4)
        center_layout.setSpacing(6)

        # Canvas Toolbar
        canvas_tb = QHBoxLayout()
        self.combo_mode = QComboBox()
        self.combo_mode.addItem("📋 Optical Slip Preview")
        self.combo_mode.addItem("📐 Millimeter Calibration Sheet")
        self.combo_mode.currentIndexChanged.connect(self._on_view_mode_changed)
        canvas_tb.addWidget(self.combo_mode)

        self.chk_guides = QCheckBox("Show Grid Guides")
        self.chk_guides.setChecked(True)
        self.chk_guides.toggled.connect(self._on_guides_toggled)
        canvas_tb.addWidget(self.chk_guides)

        canvas_tb.addStretch()

        btn_zoom_out = QPushButton("🔍 -")
        btn_zoom_out.setFixedWidth(36)
        btn_zoom_out.clicked.connect(lambda: self._adjust_zoom(-0.15))
        btn_zoom_in = QPushButton("🔍 +")
        btn_zoom_in.setFixedWidth(36)
        btn_zoom_in.clicked.connect(lambda: self._adjust_zoom(0.15))
        btn_zoom_fit = QPushButton("100%")
        btn_zoom_fit.setFixedWidth(48)
        btn_zoom_fit.clicked.connect(lambda: self.canvas.set_zoom(1.0))
        canvas_tb.addWidget(btn_zoom_out)
        canvas_tb.addWidget(btn_zoom_fit)
        canvas_tb.addWidget(btn_zoom_in)

        center_layout.addLayout(canvas_tb)

        # Center Canvas Widget
        self.canvas = BetslipCanvasWidget()
        self.canvas.coordinates_changed.connect(self._on_canvas_coord_changed)
        self.canvas.origin_dragged.connect(self._on_origin_dragged)
        center_layout.addWidget(self.canvas, stretch=1)

        # Pagination & Coordinates Footer
        footer_layout = QHBoxLayout()
        self.btn_prev_page = QPushButton("◀ Prev Slip")
        self.btn_prev_page.clicked.connect(self._prev_page)
        self.lbl_page_info = QLabel("Slip 1 of 1")
        self.lbl_page_info.setStyleSheet("font-weight: bold;")
        self.btn_next_page = QPushButton("Next Slip ▶")
        self.btn_next_page.clicked.connect(self._next_page)

        footer_layout.addWidget(self.btn_prev_page)
        footer_layout.addWidget(self.lbl_page_info)
        footer_layout.addWidget(self.btn_next_page)
        footer_layout.addStretch()

        self.lbl_coord_readout = QLabel("📍 Cursor: (0.0 mm, 0.0 mm)")
        self.lbl_coord_readout.setStyleSheet("font-family: monospace; font-size: 11px;")
        footer_layout.addWidget(self.lbl_coord_readout)

        center_layout.addLayout(footer_layout)
        splitter.addWidget(center_widget)

        # --- Right Panel: Ticket Queue & Actions ---
        right_panel = QWidget()
        right_panel.setMinimumWidth(320)
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(8)

        # Ticket Management Buttons
        grp_source = QGroupBox("Ticket Sources")
        src_lay = QVBoxLayout(grp_source)

        btn_pull_studio = QPushButton("🧪 Load Studio / Wheeling Survivors")
        btn_pull_studio.setStyleSheet("font-weight: bold; color: #1E90FF;")
        btn_pull_studio.clicked.connect(self._pull_from_studio)
        src_lay.addWidget(btn_pull_studio)

        h_files = QHBoxLayout()
        btn_import_file = QPushButton("📂 Import File...")
        btn_import_file.clicked.connect(self._import_tickets_file)
        btn_export_file = QPushButton("💾 Export File...")
        btn_export_file.clicked.connect(self._export_tickets_file)
        h_files.addWidget(btn_import_file)
        h_files.addWidget(btn_export_file)
        src_lay.addLayout(h_files)

        btn_sample = QPushButton("🎲 Generate Quick Sample (15 Tickets)")
        btn_sample.clicked.connect(self._load_sample_tickets)
        src_lay.addWidget(btn_sample)

        right_layout.addWidget(grp_source)

        # Ticket Queue Table
        right_layout.addWidget(QLabel("<b>Queued Tickets:</b>"))
        self.table_tickets = QTableWidget(0, 3)
        self.table_tickets.setHorizontalHeaderLabels(["Slip #", "Jogo #", "Numbers"])
        self.table_tickets.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_tickets.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_tickets.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_tickets.setAlternatingRowColors(True)
        right_layout.addWidget(self.table_tickets, stretch=1)

        # Primary Print Actions
        grp_print = QGroupBox("Print Execution")
        prn_lay = QVBoxLayout(grp_print)

        btn_print_calib = QPushButton("📐 Print Millimeter Calibration Sheet")
        btn_print_calib.clicked.connect(self._print_calibration_sheet)
        prn_lay.addWidget(btn_print_calib)

        btn_export_pdf = QPushButton("📄 Export Printable PDF Slips...")
        btn_export_pdf.setStyleSheet("font-weight: bold; background-color: #2E7D32; color: white;")
        btn_export_pdf.clicked.connect(self._export_pdf)
        prn_lay.addWidget(btn_export_pdf)

        btn_direct_print = QPushButton("🖨️ Direct Print to Slip Feed...")
        btn_direct_print.setStyleSheet("font-weight: bold; background-color: #1976D2; color: white;")
        btn_direct_print.clicked.connect(self._direct_print)
        prn_lay.addWidget(btn_direct_print)

        right_layout.addWidget(grp_print)
        splitter.addWidget(right_panel)

        # Set balanced splitter ratios
        splitter.setSizes([340, 580, 360])
        main_layout.addWidget(splitter, stretch=1)

        self._connect_spinbox_signals()
        self._sync_inputs_from_template()

    def _create_dspin(self, min_v: float, max_v: float, def_v: float, step: float, label: str):
        v = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px;")
        spin = QDoubleSpinBox()
        spin.setRange(min_v, max_v)
        spin.setValue(def_v)
        spin.setSingleStep(step)
        spin.setDecimals(3 if step < 0.01 else (2 if step < 0.1 else 1))
        v.addWidget(lbl)
        v.addWidget(spin)
        return (v, spin)

    def _create_spin(self, min_v: int, max_v: int, def_v: int, step: int, label: str):
        v = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px;")
        spin = QSpinBox()
        spin.setRange(min_v, max_v)
        spin.setValue(def_v)
        spin.setSingleStep(step)
        v.addWidget(lbl)
        v.addWidget(spin)
        return (v, spin)

    def _connect_spinbox_signals(self) -> None:
        self.spin_width[1].valueChanged.connect(self._on_param_changed)
        self.spin_height[1].valueChanged.connect(self._on_param_changed)
        self.spin_panels[1].valueChanged.connect(self._on_param_changed)
        self.spin_panel_gap[1].valueChanged.connect(self._on_param_changed)
        self.spin_origin_x[1].valueChanged.connect(self._on_param_changed)
        self.spin_origin_y[1].valueChanged.connect(self._on_param_changed)
        self.spin_pitch_x[1].valueChanged.connect(self._on_param_changed)
        self.spin_pitch_y[1].valueChanged.connect(self._on_param_changed)
        self.spin_mark_w[1].valueChanged.connect(self._on_param_changed)
        self.spin_mark_h[1].valueChanged.connect(self._on_param_changed)
        self.spin_hw_x[1].valueChanged.connect(self._on_param_changed)
        self.spin_hw_y[1].valueChanged.connect(self._on_param_changed)
        self.spin_scale_x[1].valueChanged.connect(self._on_param_changed)
        self.spin_scale_y[1].valueChanged.connect(self._on_param_changed)

    def _sync_inputs_from_template(self) -> None:
        t = self._current_template
        self.spin_width[1].blockSignals(True)
        self.spin_height[1].blockSignals(True)
        self.spin_panels[1].blockSignals(True)
        self.spin_panel_gap[1].blockSignals(True)
        self.spin_origin_x[1].blockSignals(True)
        self.spin_origin_y[1].blockSignals(True)
        self.spin_pitch_x[1].blockSignals(True)
        self.spin_pitch_y[1].blockSignals(True)
        self.spin_mark_w[1].blockSignals(True)
        self.spin_mark_h[1].blockSignals(True)
        self.spin_hw_x[1].blockSignals(True)
        self.spin_hw_y[1].blockSignals(True)
        self.spin_scale_x[1].blockSignals(True)
        self.spin_scale_y[1].blockSignals(True)

        self.spin_width[1].setValue(t.slip_width_mm)
        self.spin_height[1].setValue(t.slip_height_mm)
        self.spin_panels[1].setValue(t.panels_per_slip)
        self.spin_panel_gap[1].setValue(t.panel_gap_y_mm)
        self.spin_origin_x[1].setValue(t.origin_x_mm)
        self.spin_origin_y[1].setValue(t.origin_y_mm)
        self.spin_pitch_x[1].setValue(t.pitch_x_mm)
        self.spin_pitch_y[1].setValue(t.pitch_y_mm)
        self.spin_mark_w[1].setValue(t.mark_width_mm)
        self.spin_mark_h[1].setValue(t.mark_height_mm)
        self.spin_hw_x[1].setValue(t.hardware_offset_x_mm)
        self.spin_hw_y[1].setValue(t.hardware_offset_y_mm)
        self.spin_scale_x[1].setValue(t.scale_x)
        self.spin_scale_y[1].setValue(t.scale_y)

        self.spin_width[1].blockSignals(False)
        self.spin_height[1].blockSignals(False)
        self.spin_panels[1].blockSignals(False)
        self.spin_panel_gap[1].blockSignals(False)
        self.spin_origin_x[1].blockSignals(False)
        self.spin_origin_y[1].blockSignals(False)
        self.spin_pitch_x[1].blockSignals(False)
        self.spin_pitch_y[1].blockSignals(False)
        self.spin_mark_w[1].blockSignals(False)
        self.spin_mark_h[1].blockSignals(False)
        self.spin_hw_x[1].blockSignals(False)
        self.spin_hw_y[1].blockSignals(False)
        self.spin_scale_x[1].blockSignals(False)
        self.spin_scale_y[1].blockSignals(False)

        self.canvas.set_template(t)
        self._update_pagination_ui()

    def _on_param_changed(self) -> None:
        """Reads live inputs into active template and updates canvas."""
        t = self._current_template
        t.slip_width_mm = self.spin_width[1].value()
        t.slip_height_mm = self.spin_height[1].value()
        t.panels_per_slip = self.spin_panels[1].value()
        t.panel_gap_y_mm = self.spin_panel_gap[1].value()
        t.origin_x_mm = self.spin_origin_x[1].value()
        t.origin_y_mm = self.spin_origin_y[1].value()
        t.pitch_x_mm = self.spin_pitch_x[1].value()
        t.pitch_y_mm = self.spin_pitch_y[1].value()
        t.mark_width_mm = self.spin_mark_w[1].value()
        t.mark_height_mm = self.spin_mark_h[1].value()
        t.hardware_offset_x_mm = self.spin_hw_x[1].value()
        t.hardware_offset_y_mm = self.spin_hw_y[1].value()
        t.scale_x = self.spin_scale_x[1].value()
        t.scale_y = self.spin_scale_y[1].value()

        self.canvas.set_template(t)
        self._update_table_tickets()
        self._update_pagination_ui()

    def _on_preset_changed(self, name: str) -> None:
        if name in CAIXA_PRESETS:
            self._current_template = CAIXA_PRESETS[name]
            self._sync_inputs_from_template()
            self._update_badge()

    def _reset_to_official_spec(self) -> None:
        name = self.combo_presets.currentText()
        if name in CAIXA_PRESETS:
            self._current_template = CAIXA_PRESETS[name]
            self._sync_inputs_from_template()

    def _on_view_mode_changed(self, idx: int) -> None:
        self.canvas.set_show_calibration_sheet(idx == 1)

    def _on_guides_toggled(self, checked: bool) -> None:
        self.canvas.set_show_guides(checked)

    def _adjust_zoom(self, delta: float) -> None:
        self.canvas.set_zoom(self.canvas._zoom_factor + delta)

    def _on_canvas_coord_changed(self, x_mm: float, y_mm: float) -> None:
        self.lbl_coord_readout.setText(f"📍 Cursor: (X={x_mm:.1f} mm, Y={y_mm:.1f} mm)")

    def _on_origin_dragged(self, new_ox: float, new_oy: float) -> None:
        self.spin_origin_x[1].setValue(new_ox)
        self.spin_origin_y[1].setValue(new_oy)

    def set_tickets(self, tickets: List[List[int]]) -> None:
        """Sets the active batch of tickets to be paginated and printed."""
        self._tickets = tickets
        self._current_page = 0
        self.canvas.set_tickets(tickets)
        self._update_table_tickets()
        self._update_pagination_ui()
        self._update_badge()
        self.tickets_loaded.emit(len(tickets))

    def _load_sample_tickets(self) -> None:
        """Generates 15 realistic sample Lotofácil tickets."""
        import random
        sample: List[List[int]] = []
        for _ in range(15):
            t = sorted(random.sample(range(1, 26), 15))
            sample.append(t)
        self.set_tickets(sample)

    def _pull_from_studio(self) -> None:
        """Pulls generated survivor tickets from Studio perspective."""
        # Check if parent main window has studio perspective survivors
        main_win = self.window()
        if hasattr(main_win, "perspective_manager"):
            studio_view = main_win.perspective_manager._perspectives.get("Studio")
            if studio_view and hasattr(studio_view, "_survivors") and studio_view._survivors:
                self.set_tickets(studio_view._survivors)
                QMessageBox.information(
                    self,
                    "Tickets Loaded",
                    f"Successfully transferred {len(studio_view._survivors)} survivor tickets from Studio!",
                )
                return
        
        # Fallback: generate 10 tickets
        self._load_sample_tickets()
        QMessageBox.information(
            self,
            "Sample Loaded",
            "No active Studio run detected. Loaded 15 sample tickets.",
        )

    def _update_table_tickets(self) -> None:
        self.table_tickets.setRowCount(0)
        panels = self._current_template.panels_per_slip
        for i, t in enumerate(self._tickets):
            slip_num = (i // panels) + 1
            jogo_num = (i % panels) + 1
            r = self.table_tickets.rowCount()
            self.table_tickets.insertRow(r)
            self.table_tickets.setItem(r, 0, QTableWidgetItem(f"Slip {slip_num}"))
            self.table_tickets.setItem(r, 1, QTableWidgetItem(f"Jogo {jogo_num}"))
            self.table_tickets.setItem(r, 2, QTableWidgetItem(" ".join(f"{n:02d}" for n in t)))

    def _update_pagination_ui(self) -> None:
        panels = self._current_template.panels_per_slip
        total_tickets = len(self._tickets)
        total_pages = max(1, math.ceil(total_tickets / panels))
        
        if self._current_page >= total_pages:
            self._current_page = total_pages - 1
            
        self.lbl_page_info.setText(f"Slip {self._current_page + 1} of {total_pages}")
        self.btn_prev_page.setEnabled(self._current_page > 0)
        self.btn_next_page.setEnabled(self._current_page < total_pages - 1)
        self.canvas.set_page(self._current_page)

    def _prev_page(self) -> None:
        if self._current_page > 0:
            self._current_page -= 1
            self._update_pagination_ui()

    def _next_page(self) -> None:
        panels = self._current_template.panels_per_slip
        total_pages = max(1, math.ceil(len(self._tickets) / panels))
        if self._current_page < total_pages - 1:
            self._current_page += 1
            self._update_pagination_ui()

    def _update_badge(self) -> None:
        panels = self._current_template.panels_per_slip
        total_slips = math.ceil(len(self._tickets) / panels) if self._tickets else 0
        self.info_badge.setText(
            f"Template: {self._current_template.name} | {len(self._tickets)} Tickets ({total_slips} Slips)"
        )

    def _import_tickets_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Tickets",
            "",
            "Lottery Files (*.slk *.txt *.csv);;All Files (*)",
        )
        if path:
            parsed = TicketFileIO.parse_tickets(path)
            if parsed:
                self.set_tickets(parsed)
                QMessageBox.information(self, "Tickets Imported", f"Imported {len(parsed)} tickets from {path}")
            else:
                QMessageBox.warning(self, "Import Error", "No valid lottery tickets could be found in the file.")

    def _export_tickets_file(self) -> None:
        if not self._tickets:
            QMessageBox.warning(self, "No Tickets", "No tickets available to export.")
            return

        path, flt = QFileDialog.getSaveFileName(
            self,
            "Export Tickets",
            "tickets.slk",
            "SamLotto SYLK (*.slk);;Space-delimited Text (*.txt);;CSV Spreadsheet (*.csv)",
        )
        if path:
            if path.endswith(".slk"):
                TicketFileIO.export_tickets_slk(self._tickets, path)
            elif path.endswith(".csv"):
                TicketFileIO.export_tickets_csv(self._tickets, path, header=True)
            else:
                TicketFileIO.export_tickets_txt(self._tickets, path)
            QMessageBox.information(self, "Export Complete", f"Exported {len(self._tickets)} tickets to:\n{path}")

    def _export_pdf(self, show_dialog: bool = True) -> Optional[str]:
        if not self._tickets:
            if show_dialog:
                QMessageBox.warning(self, "No Tickets", "No tickets to export.")
            return None

        filepath = "betslips_export.pdf"
        if show_dialog:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Betslips to PDF",
                "betslips.pdf",
                "PDF Files (*.pdf)",
            )
            if not path:
                return None
            filepath = path

        BetslipPrintEngine.export_pdf(
            filepath=filepath,
            template=self._current_template,
            tickets=self._tickets,
            show_guides=self.chk_guides.isChecked(),
        )
        if show_dialog:
            QMessageBox.information(self, "PDF Export Complete", f"Saved printable PDF betslips to:\n{filepath}")
        return filepath

    def _print_calibration_sheet(self, show_dialog: bool = True) -> None:
        """Sends calibration test page to physical printer."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        if show_dialog:
            dlg = QPrintDialog(printer, self)
            if dlg.exec() != QPrintDialog.DialogCode.Accepted:
                return
        from PySide6.QtGui import QPainter
        painter = QPainter(printer)
        BetslipPrintEngine.render_calibration_sheet(painter, self._current_template, dpi=printer.resolution())
        painter.end()
        if show_dialog:
            QMessageBox.information(self, "Printing", "Calibration sheet dispatched to printer.")

    def _direct_print(self, show_dialog: bool = True) -> None:
        """Sends all queued tickets formatted for physical betslip feed."""
        if not self._tickets:
            if show_dialog:
                QMessageBox.warning(self, "No Tickets", "No tickets to print.")
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        if show_dialog:
            dlg = QPrintDialog(printer, self)
            if dlg.exec() != QPrintDialog.DialogCode.Accepted:
                return

        from PySide6.QtGui import QPainter
        painter = QPainter(printer)
        panels = self._current_template.panels_per_slip
        total_pages = math.ceil(len(self._tickets) / panels)

        for p in range(total_pages):
            if p > 0:
                printer.newPage()
            page_t = self._tickets[p * panels : (p + 1) * panels]
            BetslipPrintEngine.render_slip(
                painter=painter,
                template=self._current_template,
                tickets_for_slip=page_t,
                dpi=printer.resolution(),
                show_guides=False, # Print only optical marks onto real slips
                is_preview=False,
            )
        painter.end()
        if show_dialog:
            QMessageBox.information(self, "Print Complete", f"Successfully sent {total_pages} betslips to printer!")
