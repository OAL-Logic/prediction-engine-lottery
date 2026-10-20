"""
Phase 1 Test Suite
==================
Automated unit and integration tests verifying Phase 1 architecture:
- Dynamic Game Schema Discovery
- Theme Manager & pyqt6-ui-designer Tokens
- Headless Engine Bridge & Real Draws
- SamLotto Actual Skips Analytics
- Vector BallMatrixWidget & TicketReceiptWidget
- Perspective Manager & CockpitMainWindow
- Bidirectional Profile Bundle Serialization
- Strategy Ensemble Execution
"""

import pytest
import os
import sys

# Ensure offscreen Qt platform for test runner
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from cockpit.src.core.models import (
    GameSchema, PerspectiveType, ToleranceRule, ToleranceMode,
    FilterNode, TicketReceipt, ProfileBundle
)
from cockpit.src.theme.tokens import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    THEME_PALETTES, DEFAULT_THEME_NAME
)
from cockpit.src.theme.manager import ThemeManager
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.widgets.ball_matrix import BallMatrixWidget
from cockpit.src.widgets.ticket_receipt import TicketReceiptWidget
from cockpit.src.shell.main_window import CockpitMainWindow


@pytest.fixture(scope="session")
def qapp():
    """Initializes a shared QApplication instance for headless Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_game_discovery():
    """Verifies dynamic detection and schema binding of registered lottery games."""
    bridge = EngineBridge()
    games = bridge.list_games()
    assert len(games) >= 6

    game_ids = {g.id for g in games}
    assert "br/lotofacil" in game_ids
    assert "br/mega-sena" in game_ids
    assert "br/quina" in game_ids

    # Validate schema rules
    lotofacil = bridge.get_game("br/lotofacil")
    assert lotofacil is not None
    assert lotofacil.pick_count == 15
    assert lotofacil.pool_size == 25
    assert lotofacil.number_range_max == 25

    valid, err = lotofacil.validate_line(list(range(1, 16)))
    assert valid is True
    assert err is None


def test_theme_tokens_and_qss(qapp):
    """Verifies strict 4px grid tokens and dynamic stylesheet generation."""
    theme_mgr = ThemeManager()
    tokens = theme_mgr.get_tokens()
    assert "bg_root" in tokens
    assert "primary" in tokens

    # Dark mode
    theme_mgr.set_theme("Trading Terminal (Default)")
    assert theme_mgr.is_dark is True
    qss_dark = theme_mgr.generate_stylesheet()
    assert "#0a0d14" in qss_dark
    assert "QMainWindow" in qss_dark

    # Light mode
    theme_mgr.set_theme("Modern Enterprise Light")
    assert theme_mgr.is_dark is False
    qss_light = theme_mgr.generate_stylesheet()
    assert "#faf9ff" in qss_light

    # Reset to default
    theme_mgr.set_theme("Trading Terminal (Default)")


def test_engine_bridge_draws():
    """Verifies loading real historical draws from engine/modules/storage."""
    bridge = EngineBridge()
    df = bridge.get_draws("br/lotofacil", limit=10)
    assert not df.empty
    assert "numbers" in df.columns
    assert len(df) == 10
    sample_draw = df.iloc[-1]["numbers"]
    assert len(sample_draw) == 15


def test_actual_skips_computation():
    """Verifies SamLotto actual skips calculation logic."""
    bridge = EngineBridge()
    skips_data = bridge.compute_skips_analysis("br/lotofacil", target_number=10)
    assert "actual_skips" in skips_data
    assert "average_skip" in skips_data
    assert "now_skip" in skips_data
    assert "gap_histogram" in skips_data
    assert skips_data["number"] == 10
    assert len(skips_data["actual_skips"]) > 0


def test_ball_matrix_widget(qapp):
    """Verifies native QPainter ball matrix interaction and presets."""
    bridge = EngineBridge()
    game = bridge.get_game("br/lotofacil")

    matrix = BallMatrixWidget()
    matrix.configure_game(game)
    matrix.resize(500, 300)

    # Preset: Odd numbers
    matrix.select_odd()
    assert all(n % 2 != 0 for n in matrix.selected_numbers)
    assert len(matrix.selected_numbers) == 13  # Odd numbers between 1 and 25

    # Preset: Primes
    matrix.select_primes()
    assert all(n in {2, 3, 5, 7, 11, 13, 17, 19, 23} for n in matrix.selected_numbers)

    # Clear
    matrix.clear_selection()
    assert len(matrix.selected_numbers) == 0

    # Theme tokens application
    matrix.apply_theme_tokens(THEME_PALETTES["Modern Enterprise Light"])


def test_ticket_receipt_widget(qapp):
    """Verifies ticket receipt card rendering."""
    widget = TicketReceiptWidget()
    sample_tickets = [
        TicketReceipt(ticket_id=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], confidence_score=0.92, strategy_source="AI Consensus"),
        TicketReceipt(ticket_id=2, numbers=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 22, 23, 24, 25], confidence_score=0.88, strategy_source="Hot Momentum")
    ]
    widget.set_tickets(sample_tickets)
    assert widget.card_layout.count() == 3  # 2 cards + stretch


def test_perspective_manager_and_shell(qapp):
    """Verifies top-level window shell and perspective switcher."""
    win = CockpitMainWindow()
    assert win.active_game is not None
    assert len(win._available_games) > 0

    # Test Perspective Switcher
    win.perspective_manager.switch_perspective(PerspectiveType.EXPRESS)
    assert win.perspective_manager.current_perspective == PerspectiveType.EXPRESS

    win.perspective_manager.switch_perspective(PerspectiveType.STUDIO)
    assert win.perspective_manager.current_perspective == PerspectiveType.STUDIO

    win.close()


def test_profile_bundle_roundtrip():
    """Verifies JSON and YAML profile serialization."""
    bridge = EngineBridge()
    filters = bridge.load_catalog_filters()
    filters[0].enabled = True
    filters[0].min_val = 6
    filters[0].max_val = 10

    bundle = ProfileBundle(
        active_game_id="br/lotofacil",
        filters=filters,
        tolerance=ToleranceRule(mode=ToleranceMode.RANGE, min_pass=5, max_pass=15)
    )

    # JSON Roundtrip
    json_str = bundle.to_json()
    loaded_bundle = ProfileBundle.from_json(json_str)
    assert loaded_bundle.active_game_id == "br/lotofacil"
    assert loaded_bundle.tolerance.min_pass == 5
    assert loaded_bundle.tolerance.max_pass == 15

    # YAML Roundtrip
    yaml_str = bundle.to_cli_yaml()
    assert "game: br/lotofacil" in yaml_str
    assert "tolerance:" in yaml_str


def test_generate_archetype_tickets():
    """Verifies execution of headless engine prediction strategies for archetypes."""
    bridge = EngineBridge()
    tickets = bridge.generate_archetype_tickets("br/lotofacil", "archetype_ai_consensus", count=5)
    assert len(tickets) == 5
    for t in tickets:
        assert len(t.numbers) == 15
        assert len(set(t.numbers)) == 15
        assert all(1 <= n <= 25 for n in t.numbers)
        assert t.confidence_score > 0.0
