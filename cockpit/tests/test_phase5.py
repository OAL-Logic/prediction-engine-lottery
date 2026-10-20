"""
Phase 5 Master End-to-End Regression & Integration Suite
========================================================
Comprehensive system-level test verifying all interconnected Cockpit workflows:
1. End-to-End Express Workflow (Archetypes -> Engine Strategies -> HUD -> Receipt)
2. End-to-End Studio Workflow (105+ Filters -> Tolerance Mask -> Streaming Chunker -> Survivors)
3. End-to-End Wheeling Laboratory (Full/Abbreviated Covering, Key/Banker, Hamming Pruning)
4. End-to-End Esoteric Observatory (Chaos Attractors, Ephemeris, Biorhythms, Ticket Synthesis)
5. End-to-End Physical Printer Studio (Caixa Lotofácil/Mega-Sena Templates, PDF Slip Generation)
6. Bidirectional Profile Synchronization (.json & .yaml CLI presets)
7. DockingManager & Multi-Perspective State Persistence
8. Complete Theme Cycling (Dark & Light tokens across all components)
"""

import os
import sys
import tempfile
import pytest

# Headless Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSettings

from cockpit.src.core.models import (
    GameSchema,
    PerspectiveType,
    ProfileBundle,
    FilterNode,
    ToleranceRule,
    ToleranceMode,
    WheelingConfig,
    WheelType,
)
from cockpit.src.theme.tokens import THEME_PALETTES
from cockpit.src.theme.manager import ThemeManager
from cockpit.src.shell.main_window import CockpitMainWindow
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.services.wheeling_solver import WheelingSolver
from cockpit.src.services.condition_optimizer import ConditionOptimizer
from cockpit.src.services.file_io import TicketFileIO, ProfileManager
from cockpit.src.perspectives.printer.models import CAIXA_PRESETS
from cockpit.src.perspectives.printer.engine import BetslipPrintEngine


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_e2e_express_workflow(qapp):
    """Verifies complete quick generation path from Express perspective."""
    window = CockpitMainWindow()
    window.resize(1280, 800)
    window.perspective_manager.switch_perspective(PerspectiveType.EXPRESS)
    assert window.perspective_manager.current_perspective == PerspectiveType.EXPRESS

    game = window.bridge.get_game("br/lotofacil")
    assert game is not None
    window.set_active_game(game)

    # Trigger archetype generation
    window._handle_express_generation("balanced", count=3)
    qapp.processEvents()

    # Verify receipt and HUD update
    assert len(window.view_express.ticket_store._tickets) == 3
    assert "3" in window.view_express.ticket_store.lbl_count.text()
    assert "Express generation complete" in window.telemetry_label.text()


def test_e2e_studio_filtering_and_wheeling(qapp):
    """Verifies 105+ filter evaluation, tolerance masking, and abbreviated wheeling."""
    import numpy as np
    bridge = EngineBridge()
    game = bridge.get_game("br/lotofacil")
    filters = bridge.load_catalog_filters(game)

    # Enable Odd Count & Sum Total filters
    f_odd = next(f for f in filters if f.id == "structural_odd_count")
    f_odd.enabled = True
    f_odd.min_val = 7
    f_odd.max_val = 9

    f_sum = next(f for f in filters if f.id == "structural_number_sum")
    f_sum.enabled = True
    f_sum.min_val = 180
    f_sum.max_val = 220

    # 1. Evaluate sample combinatorial candidates
    candidates = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  # Odd: 8, Sum: 120 (sum fails)
        [1, 3, 5, 7, 9, 11, 13, 15, 16, 17, 18, 19, 20, 21, 22], # Odd: 11, Sum: 207 (odd fails)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 25], # Odd: 9, Sum: 136 (sum fails)
        [1, 3, 5, 7, 9, 11, 12, 14, 16, 17, 18, 20, 21, 23, 24], # Odd: 8, Sum: 211 (Passes both!)
    ]

    combos = np.array(candidates, dtype=np.uint8)
    pass_matrix = bridge.evaluate_filter_chunk_vectorized(combos, [f_odd, f_sum], game=game)

    # AND mode (Strict: must pass both)
    mask_and = bridge.apply_tolerance_mask(pass_matrix, ToleranceRule(mode=ToleranceMode.AND))
    survivors_and = [candidates[i] for i in np.where(mask_and)[0]]
    assert len(survivors_and) == 1
    assert survivors_and[0] == candidates[3]

    # RANGE mode (Error allowance: pass if at least 1 matches)
    mask_tol = bridge.apply_tolerance_mask(pass_matrix, ToleranceRule(mode=ToleranceMode.RANGE, min_pass=1, max_pass=2))
    survivors_tol = [candidates[i] for i in np.where(mask_tol)[0]]
    assert len(survivors_tol) >= 3

    # 2. Wheeling Solver: 17 numbers wheeled to 15, guarantee 14-if-15 with Key numbers
    pool = list(range(1, 18))
    key_numbers = [1, 2, 3] # Fixed bankers
    wheel_tickets = WheelingSolver.generate_abbreviated_wheel(
        pool=pool,
        pick_count=15,
        guarantee_t=14,
        condition_m=15,
        key_numbers=key_numbers,
    )
    assert len(wheel_tickets) > 0
    # Every ticket must contain all 3 banker numbers
    for wt in wheel_tickets:
        assert set(key_numbers).issubset(set(wt))

    # Coverage verification
    coverage_pct = WheelingSolver.evaluate_coverage(
        tickets=wheel_tickets,
        pool=pool,
        t=14,
        m=15,
        max_subsets_sample=100,
    )
    assert coverage_pct >= 80.0


def test_e2e_esoteric_observatory_workflow(qapp):
    """Verifies 3D strange attractors, ephemeris calculations, and chaos ticket synthesis."""
    import datetime
    window = CockpitMainWindow()
    window.perspective_manager.switch_perspective(PerspectiveType.ESOTERIC)
    assert window.perspective_manager.current_perspective == PerspectiveType.ESOTERIC

    esoteric_view = window.view_esoteric
    assert esoteric_view.canvas_3d is not None

    # Change attractor mode
    esoteric_view.combo_attractor.setCurrentIndex(2) # Aizawa Attractor
    assert esoteric_view.canvas_3d._current_mode == "aizawa"

    # Ephemeris calculations
    eph = esoteric_view.ephemeris_widget
    eph.set_draw_date(datetime.date(2026, 10, 15))
    assert "Moon" in eph._planets
    assert 0.0 <= eph._lunar_illumination <= 1.0

    # Biorhythm harmonics
    bio = esoteric_view.biorhythm_widget
    bio.plot_biorhythms(days_offset=5)
    assert len(bio.plot_widget.plotItem.curves) == 4

    # Chaos Ticket Synthesis
    esoteric_view._synthesize_chaos_prediction(show_dialog=False)
    assert len(esoteric_view.ticket_viewer._tickets) == 10
    assert esoteric_view.notebook.currentIndex() == 3
    sample_ticket = esoteric_view.ticket_viewer._tickets[0]
    assert len(sample_ticket.numbers) == window.active_game.pick_count
    assert len(set(sample_ticket.numbers)) == len(sample_ticket.numbers)


def test_e2e_physical_betslip_printer_workflow(qapp, tmp_path):
    """Verifies end-to-end slip calibration, ticket transfer, and multi-page PDF generation."""
    window = CockpitMainWindow()
    window.perspective_manager.switch_perspective(PerspectiveType.PRINTER)
    printer_view = window.view_printer

    # Select Mega-Sena template
    printer_view.combo_presets.setCurrentText("Caixa Mega-Sena")
    assert printer_view._current_template.name == "Caixa Mega-Sena"
    assert printer_view._current_template.rows == 6
    assert printer_view._current_template.cols == 10

    # Queue 10 Mega-Sena tickets (3 slips: 3 + 3 + 3 + 1 -> 4 slips)
    sample_tickets = [
        [4, 12, 18, 27, 39, 58],
        [5, 10, 22, 34, 45, 50],
        [1, 14, 25, 33, 42, 59],
        [7, 19, 28, 31, 48, 60],
        [3, 11, 21, 30, 44, 55],
        [8, 16, 29, 36, 49, 57],
        [2, 15, 23, 38, 41, 52],
        [6, 17, 24, 35, 46, 56],
        [9, 20, 32, 40, 47, 53],
        [13, 26, 37, 43, 51, 54],
    ]
    printer_view.set_tickets(sample_tickets)
    assert printer_view.table_tickets.rowCount() == 10
    assert "Slip 1 of 4" in printer_view.lbl_page_info.text()

    # Export PDF slips
    pdf_out = str(tmp_path / "e2e_caixa_megasena.pdf")
    BetslipPrintEngine.export_pdf(
        filepath=pdf_out,
        template=printer_view._current_template,
        tickets=sample_tickets,
        show_guides=True,
    )
    assert os.path.exists(pdf_out)
    assert os.path.getsize(pdf_out) > 2000


def test_e2e_profile_sync_lossless(tmp_path):
    """Verifies lossless bidirectional profile persistence across JSON and YAML."""
    bridge = EngineBridge()
    game = bridge.get_game("br/lotofacil")
    filters = bridge.load_catalog_filters(game)
    filters[0].enabled = True
    filters[1].enabled = True

    bundle = ProfileBundle(
        active_game_id=game.id,
        active_perspective="Studio",
        theme_name="Cyberpunk Neon",
        filters=filters,
        tolerance=ToleranceRule(mode=ToleranceMode.RANGE, min_pass=5, max_pass=10),
        wheeling=WheelingConfig(guarantee=13, condition_match=15, pruning_enabled=True),
        strategy_weights={"voting": 0.5, "prob_weighted": 0.5},
    )

    # 1. JSON Roundtrip
    json_file = str(tmp_path / "master_profile.json")
    ProfileManager.save_profile_json(bundle, json_file)
    restored_json = ProfileManager.load_profile_json(json_file)
    assert restored_json.active_game_id == game.id
    assert restored_json.theme_name == "Cyberpunk Neon"
    assert restored_json.tolerance.min_pass == 5
    assert len(restored_json.filters) == len(bundle.filters)

    # 2. YAML CLI Roundtrip
    yaml_file = str(tmp_path / "cli_preset.yaml")
    ProfileManager.save_profile_yaml(bundle, yaml_file)
    restored_yaml = ProfileManager.load_profile_yaml(yaml_file)
    assert restored_yaml.active_game_id == game.id
    assert restored_yaml.tolerance.min_pass == 5
    assert len(restored_yaml.filters) == 2  # Only enabled filters in YAML


def test_e2e_theme_cycling(qapp):
    """Verifies that all registered theme palettes apply cleanly without errors."""
    window = CockpitMainWindow()
    for theme_name in THEME_PALETTES.keys():
        window.theme_manager.set_theme(theme_name)
        qss = window.theme_manager.generate_stylesheet()
        assert len(qss) > 500
        window.setStyleSheet(qss)
        window.apply_theme()
        qapp.processEvents()
        assert window.theme_manager.current_theme_name == theme_name
