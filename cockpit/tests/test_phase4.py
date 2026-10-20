"""
Phase 4 Automated Test Suite
============================
Verifies:
1. TicketFileIO (Lottery Studio .slk, .txt, .csv parsers and exporters)
2. ProfileManager (bidirectional JSON & CLI YAML roundtrips)
3. BetslipTemplate & Brazilian Caixa Presets (Lotofácil, Mega-Sena, Quina, Lotomania)
4. BetslipPrintEngine (PDF rendering, calibration sheets, metric transforms)
5. PrinterPerspectiveView (UI state, pagination, preset switching)
6. CockpitMainWindow Printer Perspective integration
7. CLI parser integration
"""

import os
import sys
from pathlib import Path
import tempfile
import pytest

# Headless Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

from cockpit.src.core.models import (
    GameSchema,
    PerspectiveType,
    ProfileBundle,
    FilterNode,
    ToleranceRule,
    ToleranceMode,
    WheelingConfig,
)
from cockpit.src.services.file_io import TicketFileIO, ProfileManager
from cockpit.src.perspectives.printer.models import BetslipTemplate, CAIXA_PRESETS
from cockpit.src.perspectives.printer.engine import BetslipPrintEngine, mm_to_px, px_to_mm
from cockpit.src.perspectives.printer.view import PrinterPerspectiveView
from cockpit.src.shell.main_window import CockpitMainWindow
from cockpit.src.app import build_arg_parser


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_ticket_file_io_roundtrips(tmp_path):
    """Verifies .slk, .txt, and .csv ticket import and export fidelity."""
    sample_tickets = [
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25],
        [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    ]

    # 1. Space-delimited .txt
    txt_path = str(tmp_path / "test_tickets.txt")
    TicketFileIO.export_tickets_txt(sample_tickets, txt_path)
    assert os.path.exists(txt_path)
    loaded_txt = TicketFileIO.parse_tickets(txt_path)
    assert len(loaded_txt) == 3
    assert loaded_txt[0] == sample_tickets[0]

    # 2. Comma-delimited .csv
    csv_path = str(tmp_path / "test_tickets.csv")
    TicketFileIO.export_tickets_csv(sample_tickets, csv_path, header=True)
    assert os.path.exists(csv_path)
    loaded_csv = TicketFileIO.parse_tickets(csv_path)
    assert len(loaded_csv) == 3
    assert loaded_csv[1] == sample_tickets[1]

    # 3. Lottery Studio SYLK .slk
    slk_path = str(tmp_path / "test_tickets.slk")
    TicketFileIO.export_tickets_slk(sample_tickets, slk_path)
    assert os.path.exists(slk_path)
    loaded_slk = TicketFileIO.parse_tickets(slk_path)
    assert len(loaded_slk) == 3
    assert loaded_slk[2] == sample_tickets[2]


def test_profile_manager_roundtrips(tmp_path):
    """Verifies JSON and YAML profile bundle serialization."""
    profile = ProfileBundle(
        active_game_id="br/mega-sena",
        active_perspective="Studio",
        theme_name="Trading Terminal (Default)",
        filters=[
            FilterNode(id="sum_total", name="Sum Total", category="Sums", enabled=True, min_val=130, max_val=210),
            FilterNode(id="odd_count", name="Odd Count", category="Counts", enabled=True, min_val=2, max_val=4),
        ],
        tolerance=ToleranceRule(mode=ToleranceMode.RANGE, min_pass=1, max_pass=2),
        wheeling=WheelingConfig(guarantee=4, condition_match=6, pruning_enabled=True),
        strategy_weights={"bayesian": 0.4, "markov": 0.6},
    )

    # 1. JSON
    json_path = str(tmp_path / "profile.json")
    ProfileManager.save_profile_json(profile, json_path)
    loaded_json = ProfileManager.load_profile_json(json_path)
    assert loaded_json.active_game_id == "br/mega-sena"
    assert len(loaded_json.filters) == 2
    assert loaded_json.tolerance.mode == ToleranceMode.RANGE

    # 2. CLI YAML
    yaml_path = str(tmp_path / "profile.yaml")
    ProfileManager.save_profile_yaml(profile, yaml_path)
    loaded_yaml = ProfileManager.load_profile_yaml(yaml_path)
    assert loaded_yaml.active_game_id == "br/mega-sena"
    assert len(loaded_yaml.filters) == 2
    assert loaded_yaml.tolerance.mode == ToleranceMode.RANGE


def test_caixa_presets_and_coordinates():
    """Verifies Caixa betslip geometry and mathematical coordinate projections."""
    # Test all Caixa presets exist
    assert "Caixa Lotofácil" in CAIXA_PRESETS
    assert "Caixa Mega-Sena" in CAIXA_PRESETS
    assert "Caixa Quina" in CAIXA_PRESETS
    assert "Caixa Lotomania" in CAIXA_PRESETS

    loto = CAIXA_PRESETS["Caixa Lotofácil"]
    assert loto.slip_width_mm == 82.0
    assert loto.slip_height_mm == 155.0
    assert loto.panels_per_slip == 3

    # Panel 0, Ball 1 (origin)
    pos_1 = loto.calculate_mark_position_mm(0, 1)
    assert pos_1 is not None
    assert pytest.approx(pos_1[0], 0.01) == 9.5
    assert pytest.approx(pos_1[1], 0.01) == 33.5

    # Panel 0, Ball 25 (last cell)
    pos_25 = loto.calculate_mark_position_mm(0, 25)
    assert pos_25 is not None
    expected_x = 9.5 + (4 * 4.8)
    expected_y = 33.5 + (4 * 4.2)
    assert pytest.approx(pos_25[0], 0.01) == expected_x
    assert pytest.approx(pos_25[1], 0.01) == expected_y

    # Panel 1, Ball 1 (shifted by panel_gap_y_mm)
    pos_p1_1 = loto.calculate_mark_position_mm(1, 1)
    assert pos_p1_1 is not None
    assert pytest.approx(pos_p1_1[0], 0.01) == 9.5
    assert pytest.approx(pos_p1_1[1], 0.01) == 33.5 + 34.5

    # Out of bounds checks
    assert loto.calculate_mark_position_mm(3, 1) is None # only 3 panels (0, 1, 2)
    assert loto.calculate_mark_position_mm(0, 0) is None # Lotofacil starts at 1
    assert loto.calculate_mark_position_mm(0, 26) is None

    # Hardware compensation
    loto_custom = BetslipTemplate(**CAIXA_PRESETS["Caixa Lotofácil"].__dict__)
    loto_custom.hardware_offset_x_mm = 2.0
    loto_custom.scale_y = 1.05
    pos_comp = loto_custom.calculate_mark_position_mm(0, 1)
    assert pytest.approx(pos_comp[0], 0.01) == 9.5 + 2.0
    assert pytest.approx(pos_comp[1], 0.01) == 33.5 * 1.05


def test_betslip_print_engine(qapp, tmp_path):
    """Verifies metric conversions, preview image rendering, and PDF generation."""
    # Metric conversion check: 25.4mm = 1 inch = DPI pixels
    assert pytest.approx(mm_to_px(25.4, 300.0), 0.01) == 300.0
    assert pytest.approx(px_to_mm(300.0, 300.0), 0.01) == 25.4

    template = CAIXA_PRESETS["Caixa Lotofácil"]
    tickets = [
        list(range(1, 16)),
        list(range(2, 17)),
        list(range(3, 18)),
        list(range(4, 19)),
    ]

    # 1. Preview Image
    img = BetslipPrintEngine.render_preview_image(template, tickets[:3], dpi=150.0)
    assert isinstance(img, QImage)
    assert not img.isNull()
    assert img.width() > 400
    assert img.height() > 800

    # 2. PDF Export
    pdf_path = str(tmp_path / "slips_test.pdf")
    BetslipPrintEngine.export_pdf(pdf_path, template, tickets, show_guides=True, dpi=300.0)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Non-trivial PDF output


def test_printer_perspective_view(qapp, tmp_path):
    """Verifies the complete interactive PrinterPerspectiveView widget."""
    view = PrinterPerspectiveView()
    assert view.combo_presets.count() >= 5
    assert view.canvas is not None

    # Test preset change
    view.combo_presets.setCurrentText("Caixa Mega-Sena")
    assert view._current_template.name == "Caixa Mega-Sena"
    assert view.spin_width[1].value() == 82.0

    # Test ticket loading & pagination
    test_tickets = [list(range(1, 16)) for _ in range(7)]  # 7 tickets = 3 slips (3 + 3 + 1)
    view.set_tickets(test_tickets)
    assert view.table_tickets.rowCount() == 7
    assert view._current_page == 0
    assert "Slip 1 of 3" in view.lbl_page_info.text()

    # Next page
    view._next_page()
    assert view._current_page == 1
    assert "Slip 2 of 3" in view.lbl_page_info.text()

    # Prev page
    view._prev_page()
    assert view._current_page == 0

    # Export PDF headless check
    pdf_out = str(tmp_path / "test_out.pdf")
    BetslipPrintEngine.export_pdf(pdf_out, view._current_template, test_tickets)
    assert os.path.exists(pdf_out)


def test_main_window_printer_integration(qapp):
    """Verifies Printer perspective integration and switching inside CockpitMainWindow."""
    window = CockpitMainWindow()
    assert PerspectiveType.PRINTER in window.perspective_manager._perspectives
    assert window.view_printer is not None

    # Switch to Printer
    window.perspective_manager.switch_perspective(PerspectiveType.PRINTER)
    assert window.perspective_manager.current_perspective == PerspectiveType.PRINTER
    assert window.central_stack.currentWidget() == window.view_printer

    # Switch game and verify preset sync
    mega_game = window.bridge.get_game("br/mega-sena")
    if mega_game:
        window.set_active_game(mega_game)
        assert window.view_printer.combo_presets.currentText() == "Caixa Mega-Sena"

    loto_game = window.bridge.get_game("br/lotofacil")
    if loto_game:
        window.set_active_game(loto_game)
        assert window.view_printer.combo_presets.currentText() == "Caixa Lotofácil"


def test_cli_parser():
    """Verifies CLI argument parser in cockpit/src/app.py."""
    parser = build_arg_parser()
    args = parser.parse_args(["--game", "br/quina", "--perspective", "printer", "--theme", "light"])
    assert args.game == "br/quina"
    assert args.perspective == "printer"
    assert args.theme == "light"
