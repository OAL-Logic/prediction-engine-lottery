"""
Comprehensive Automated Test Suite: Lottery Engine Desktop Cockpit
=================================================================
Validates:
1. Dynamic game discovery & validation schemas
2. Domain models & bidirectional profile bundle serialization (JSON & CLI YAML)
3. Fault Tolerance Engine (Error Allowance pass/fail criteria)
4. Vectorized combinatorial streaming worker & cooperative cancellation
5. Mathematical wheeling solver (covering designs, Banker keys, Hamming pruning)
6. Application Shell (ThemeManager, DockingManager, PerspectiveManager)
"""

import os
import sys
import pytest
import numpy as np

# Set offscreen for headless Qt testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from desktop.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, ToleranceMode,
    WheelingConfig, WheelType, TicketReceipt, ProfileBundle
)
from desktop.src.services.engine_bridge import EngineBridge
from desktop.src.services.wheeling_solver import WheelingSolver
from desktop.src.services.streaming_worker import StreamingCombinatorialWorker
from desktop.src.shell.theme_manager import ThemeManager, THEME_PALETTES
from desktop.src.shell.docking_manager import DockingManager, DockDescriptor
from desktop.src.shell.perspective_manager import PerspectiveManager, PerspectiveType
from desktop.src.shell.main_window import CockpitMainWindow
from desktop.src.widgets.ball_matrix import BallMatrixWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# -------------------------------------------------------------
# 1. Dynamic Game Discovery & Schema Tests
# -------------------------------------------------------------
def test_game_discovery():
    bridge = EngineBridge()
    games = bridge.list_games(only_available=True)
    assert len(games) > 0

    lotofacil = bridge.get_game("br/lotofacil")
    assert lotofacil is not None
    assert lotofacil.pick_count == 15
    assert lotofacil.pool_size == 25
    assert lotofacil.number_range_min == 1
    assert lotofacil.number_range_max == 25

    # Line validation
    valid, msg = lotofacil.validate_line(list(range(1, 16)))
    assert valid is True
    assert msg is None

    # Too few numbers
    valid, msg = lotofacil.validate_line(list(range(1, 10)))
    assert valid is False
    assert "Expected 15" in msg

    # Out of range
    valid, msg = lotofacil.validate_line([1] * 14 + [99])
    assert valid is False


# -------------------------------------------------------------
# 2. Domain Models & Bidirectional Profile Bundles
# -------------------------------------------------------------
def test_profile_bundle_bidirectional_serialization():
    bundle = ProfileBundle(
        active_game_id="br/lotofacil",
        active_perspective="Advanced Studio",
        theme_name="Trading Terminal (Default)",
        filters=[
            FilterNode(id="structural_odd_count", name="Odd Count", category="Structural", min_val=7, max_val=9, enabled=True),
            FilterNode(id="structural_even_count", name="Even Count", category="Structural", min_val=6, max_val=8, enabled=True),
        ],
        tolerance=ToleranceRule(mode=ToleranceMode.RANGE, min_pass=1, max_pass=2),
        wheeling=WheelingConfig(wheel_type=WheelType.ABBREVIATED, guarantee=4, condition_match=5)
    )

    # 1. Desktop JSON Roundtrip
    json_data = bundle.to_json()
    assert "structural_odd_count" in json_data
    loaded = ProfileBundle.from_json(json_data)
    assert loaded.active_game_id == "br/lotofacil"
    assert len(loaded.filters) == 2
    assert loaded.tolerance.mode == ToleranceMode.RANGE

    # 2. CLI YAML Preset Export
    yaml_data = bundle.to_cli_yaml()
    assert "game: br/lotofacil" in yaml_data
    assert "min_pass: 1" in yaml_data


# -------------------------------------------------------------
# 3. Fault Tolerance (Error Allowance) Tests
# -------------------------------------------------------------
def test_fault_tolerance_criteria():
    bridge = EngineBridge()

    # Pass matrix for 4 combos across 3 filters
    # Combo 0: 3 True (100% match)
    # Combo 1: 2 True (66% match)
    # Combo 2: 1 True (33% match)
    # Combo 3: 0 True (0% match)
    pass_matrix = np.array([
        [True,  True,  True],
        [True,  True,  False],
        [True,  False, False],
        [False, False, False],
    ], dtype=bool)

    # AND mode (Strict: must match all 3)
    tol_and = ToleranceRule(mode=ToleranceMode.AND)
    mask_and = bridge.apply_tolerance_mask(pass_matrix, tol_and)
    np.testing.assert_array_equal(mask_and, [True, False, False, False])

    # OR mode (Any match: >= 1)
    tol_or = ToleranceRule(mode=ToleranceMode.OR)
    mask_or = bridge.apply_tolerance_mask(pass_matrix, tol_or)
    np.testing.assert_array_equal(mask_or, [True, True, True, False])

    # RANGE mode (Error Allowance: match 1 to 2)
    tol_range = ToleranceRule(mode=ToleranceMode.RANGE, min_pass=1, max_pass=2)
    mask_range = bridge.apply_tolerance_mask(pass_matrix, tol_range)
    np.testing.assert_array_equal(mask_range, [False, True, True, False])


# -------------------------------------------------------------
# 4. Mathematical Wheeling Solver Tests
# -------------------------------------------------------------
def test_wheeling_solver_math():
    game = GameSchema(id="test/game", name="Test", pick_count=6, pool_size=12)

    # Full Wheel on 8 numbers -> C(8, 6) = 28 lines
    pool = list(range(1, 9))
    cfg_full = WheelingConfig(
        wheel_type=WheelType.FULL,
        pool_numbers=pool
    )
    lines_full = WheelingSolver.generate_tickets(cfg_full, game)
    assert len(lines_full) == 28
    for line in lines_full:
        assert len(line) == 6

    # Abbreviated Covering (Guaranteed 4 if 5)
    cfg_abbrev = WheelingConfig(
        wheel_type=WheelType.ABBREVIATED,
        pool_numbers=pool,
        guarantee=4,
        condition_match=5
    )
    lines_abbrev = WheelingSolver.generate_tickets(cfg_abbrev, game)
    assert len(lines_abbrev) < 28  # Abbreviated produces a significant reduction!
    assert len(lines_abbrev) >= 4

    # Banker key numbers (Fix numbers 1 and 2)
    cfg_banker = WheelingConfig(
        wheel_type=WheelType.FULL,
        pool_numbers=pool,
        key_numbers=[1, 2]
    )
    lines_banker = WheelingSolver.generate_tickets(cfg_banker, game)
    # Remaining 6 numbers choosing (6 - 2) = 4 -> C(6, 4) = 15 lines
    assert len(lines_banker) == 15
    for line in lines_banker:
        assert 1 in line and 2 in line

    # Hamming redundancy pruning
    pruned = WheelingSolver.prune_redundant_overlaps(lines_full, min_distinct=2)
    assert len(pruned) <= len(lines_full)


# -------------------------------------------------------------
# 5. Application Shell & UI Perspectives Tests
# -------------------------------------------------------------
def test_application_shell(qapp):
    win = CockpitMainWindow()
    assert win.active_game is not None
    assert len(win._available_games) > 0

    # Test Perspective Switcher
    win.perspective_manager.switch_perspective(PerspectiveType.EXPRESS)
    assert win.perspective_manager.current_perspective == PerspectiveType.EXPRESS

    win.perspective_manager.switch_perspective(PerspectiveType.STUDIO)
    assert win.perspective_manager.current_perspective == PerspectiveType.STUDIO

    win.perspective_manager.switch_perspective(PerspectiveType.LAB)
    assert win.perspective_manager.current_perspective == PerspectiveType.LAB

    # Test BallMatrixWidget hit testing & selection
    matrix = BallMatrixWidget()
    matrix.configure_game(win.active_game)
    matrix.resize(500, 300)
    matrix.set_selected_numbers([1, 3, 5, 7])
    assert sorted(list(matrix.selected_numbers)) == [1, 3, 5, 7]
    matrix.clear_selection()
    assert len(matrix.selected_numbers) == 0

    win.close()


def test_streaming_combinatorial_worker(qapp):
    """Verifies chunked background combination streaming and filter evaluation."""
    active_filters = [
        FilterNode(id="structural_odd_count", name="Odd Count", category="Structural", min_val=2, max_val=4, enabled=True),
        FilterNode(id="structural_even_count", name="Even Count", category="Structural", min_val=2, max_val=4, enabled=True),
    ]
    tolerance = ToleranceRule(mode=ToleranceMode.AND)
    worker = StreamingCombinatorialWorker(
        pool=list(range(1, 13)),  # 12 numbers
        pick_count=6,             # C(12, 6) = 924 combos
        active_filters=active_filters,
        tolerance=tolerance,
        chunk_size=200,
        max_survivors_cap=2000
    )

    results = []
    worker.signals.finished.connect(lambda survivors, summary: results.append((survivors, summary)))

    worker.run()

    assert len(results) == 1
    survivors, summary = results[0]
    assert summary["total_scanned"] == 924
    assert len(survivors) > 0
    assert summary["total_survived"] == len(survivors)
    assert summary["reduction_rate_pct"] > 0.0



# -------------------------------------------------------------
# 6. SamLotto 68-Filter Catalog & Empirical Analytics Tests
# -------------------------------------------------------------
def test_samlotto_68_filter_catalog():
    bridge = EngineBridge()
    lotofacil = bridge.get_game("br/lotofacil")
    filters = bridge.load_catalog_filters(lotofacil)
    assert len(filters) >= 68

    categories = {f.category for f in filters}
    assert "Structural / Count" in categories
    assert "Sums & Averages" in categories
    assert "Positional & Distance" in categories
    assert "Complexity & Repeats" in categories
    assert "Algebraic Residue" in categories
    assert "Decades & Units" in categories
    assert "Advanced & Sets" in categories

    # Verify SamLotto signature tags
    tag_1 = next(f for f in filters if "tag:1" in f.tags)
    assert tag_1.name == "Odd Count"
    assert tag_1.min_val >= 1

    tag_20 = next(f for f in filters if "tag:20" in f.tags)
    assert "Arithmetic Complexity" in tag_20.name


def test_actual_skips_and_gap_analytics():
    bridge = EngineBridge()
    skips_data = bridge.compute_skips_analysis("br/lotofacil", target_number=10)
    assert "actual_skips" in skips_data
    assert "average_skip" in skips_data
    assert "now_skip" in skips_data
    assert "gap_histogram" in skips_data
    assert skips_data["number"] == 10
    assert len(skips_data["actual_skips"]) > 0


def test_auto_fit_historical_bounds():
    bridge = EngineBridge()
    filters = bridge.load_catalog_filters()
    fitted = bridge.compute_auto_fit_ranges("br/lotofacil", filters, last_n_draws=30)
    assert len(fitted) > 0
    assert "structural_odd_count" in fitted
    min_odd, max_odd = fitted["structural_odd_count"]
    assert 0 <= min_odd <= max_odd <= 15


def test_theme_manager_light_dark_switching(qapp):
    theme_mgr = ThemeManager()
    
    # Dark mode
    theme_mgr.set_theme("Trading Terminal (Default)")
    assert theme_mgr.is_dark is True
    qss_dark = theme_mgr.generate_stylesheet()
    assert "#0a0d14" in qss_dark

    # Light mode
    theme_mgr.set_theme("Modern Enterprise Light")
    assert theme_mgr.is_dark is False
    qss_light = theme_mgr.generate_stylesheet()
    assert "#faf9ff" in qss_light


def test_generate_archetype_tickets():
    """Verifies that engine archetypes generate valid tickets matching game schema."""
    bridge = EngineBridge()
    tickets = bridge.generate_archetype_tickets("br/lotofacil", "archetype_ai_consensus", count=5)
    assert len(tickets) == 5
    for t in tickets:
        assert len(t.numbers) == 15
        assert len(set(t.numbers)) == 15
        assert all(1 <= n <= 25 for n in t.numbers)
        assert t.confidence_score > 0.0


def test_advanced_filters_dialog(qapp):
    """Verifies modal dialog for SamLotto advanced sets."""
    from desktop.src.widgets.advanced_filters_dialog import AdvancedFiltersDialog
    bridge = EngineBridge()
    game = bridge.get_game("br/lotofacil")
    filters = bridge.load_catalog_filters(game)
    dlg = AdvancedFiltersDialog(game, filters)
    assert dlg.tabs.count() == 4
    
    received_config = []
    dlg.filters_configured.connect(lambda cfg: received_config.append(cfg))
    dlg._apply_and_close()
    
    assert len(received_config) == 1
    cfg = received_config[0]
    assert "advanced_successive_filter" in cfg
    assert "historical_delete_drawings" in cfg
    assert len(cfg["range_partitions"]) == 5
    dlg.close()


def test_cli_preset_round_trip():
    """Verifies bidirectional CLI preset serialization."""
    bridge = EngineBridge()
    filters = bridge.load_catalog_filters()
    filters[0].enabled = True
    filters[0].min_val = 5
    filters[0].max_val = 9
    
    bundle = ProfileBundle(
        active_game_id="br/lotofacil",
        filters=filters,
        tolerance=ToleranceRule(mode=ToleranceMode.RANGE, min_pass=4, max_pass=8)
    )
    yaml_str = bundle.to_cli_yaml()
    assert "game: br/lotofacil" in yaml_str
    assert "tolerance:" in yaml_str
    
    import yaml
    data = yaml.safe_load(yaml_str)
    assert data["game"] == "br/lotofacil"
    assert data["tolerance"]["min_pass"] == 4
    assert data["tolerance"]["max_pass"] == 8

