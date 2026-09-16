import pytest
import sys
from PySide6.QtWidgets import QApplication

from desktop.src.tabs.database import DatabaseTab
from desktop.src.tabs.analysis import AnalysisTab
from desktop.src.tabs.filters import FiltersTab
from desktop.src.tabs.wheeling import WheelingTab
from desktop.src.tabs.verification import VerificationTab
from desktop.src.main import ProphetDashboard

@pytest.fixture(scope="session")
def qapp():
    """Initialises a session-wide QApplication to support headless GUI widget testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_database_tab_init(qapp):
    tab = DatabaseTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert tab.table_view is not None

def test_analysis_tab_init(qapp):
    tab = AnalysisTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert tab.combo_analysis_type is not None

def test_filters_tab_init(qapp):
    tab = FiltersTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab._active_filters) == 0

def test_wheeling_tab_init(qapp):
    tab = WheelingTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab.pool_numbers) == 0
    assert len(tab.key_numbers) == 0

def test_verification_tab_init(qapp):
    tab = VerificationTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab.tickets) == 0
    # Formula Leaderboard (ticket #106) — added as a second sub-tab alongside
    # the pre-existing Ticket Auditor, not a replacement for it.
    assert tab.desk_tabs.count() == 2
    assert "weighted" in tab.selected_formulas()  # `default` preset members start checked

def test_prediction_tab_formula_algorithm_drilldown(qapp):
    from desktop.src.tabs.predict import PredictionTab
    from engine.strategies import STRATEGY_PRESETS

    tab = PredictionTab()
    assert tab.formula_combo.count() == len(STRATEGY_PRESETS)
    assert tab.algorithm_combo.count() > 0
    assert tab.selected_strategy() == tab.algorithm_combo.currentText()

    # Switching formula repopulates the algorithm list to that family's members
    tab.formula_combo.setCurrentText("fast")
    assert set(
        tab.algorithm_combo.itemText(i) for i in range(tab.algorithm_combo.count())
    ) == set(STRATEGY_PRESETS["fast"])

    # Push to Pool stays disabled until a prediction actually lands
    assert not tab.push_pool_button.isEnabled()
    received = []
    tab.numbers_recommended.connect(lambda nums: received.append(nums))
    tab.set_last_ticket([1, 2, 3])
    assert tab.push_pool_button.isEnabled()
    tab.push_pool_button.click()
    assert received == [[1, 2, 3]]

def test_number_grid_select_numbers(qapp):
    from desktop.src.widgets.number_grid import NumberGrid

    grid = NumberGrid()
    grid.set_max_number(25)
    grid.select_numbers([3, 7, 99, 12])  # 99 is out of range and must be dropped
    assert grid.selected_numbers == {3, 7, 12}

def test_number_grid_set_range_zero_indexed(qapp):
    """Lotomania draws 00-99 — the one registered game whose pool doesn't
    start at 1. set_range() (unlike the 1-indexed-only set_max_number())
    must render/accept 0 as a real button, not silently drop it."""
    from desktop.src.widgets.number_grid import NumberGrid

    grid = NumberGrid()
    grid.set_range(0, 99)
    assert 0 in grid.buttons
    assert 100 not in grid.buttons
    assert len(grid.buttons) == 100

    grid.select_all()
    assert 0 in grid.selected_numbers

    grid.select_numbers([0, 50, 99, 100])  # 100 is out of range for a 0-99 pool
    assert grid.selected_numbers == {0, 50, 99}

def test_prophet_dashboard_games_combo_and_default_sync(qapp):
    """Regression guard for two bugs introduced-then-fixed in the same change:
    the game pickers must list every available registry game (not a stale
    hardcoded 3-game list), and their default selection must actually match
    dashboard.active_lottery instead of whatever the registry happens to list
    first."""
    from engine.adapters.registry import registry as game_registry

    dashboard = ProphetDashboard()
    available = game_registry.list_games(only_available=True)

    assert dashboard.game_combo.count() == len(available)
    assert dashboard.predict_tab.lottery_combo.count() == len(available)
    assert dashboard.db_tab.lottery_selector.count() == len(available)

    assert dashboard.active_lottery == "br/lotofacil"
    assert "br/lotofacil" in dashboard.game_combo.currentText()
    assert dashboard.db_tab.lottery_selector.currentText() == "br/lotofacil"
    assert dashboard.predict_tab.lottery_combo.currentText() == "br/lotofacil"

    # And a non-1-indexed game switches the NumberGrid to its real range, not a
    # silent 25-number fallback.
    dashboard.change_global_lottery("br/lotomania")
    assert dashboard.number_grid.min_number == 0
    assert dashboard.number_grid.max_number == 99

def test_prophet_dashboard_init(qapp):
    dashboard = ProphetDashboard()
    assert dashboard is not None
    assert dashboard.active_lottery == "br/lotofacil"
    
    # Verify new QSplitter layout hierarchy is registered
    assert dashboard.main_splitter is not None
    assert dashboard.upper_splitter is not None
    assert dashboard.setup_tabs.count() == 3
    assert dashboard.number_grid is not None
    assert dashboard.ticket_table is not None
    
    # Verify lottery context propagation
    dashboard.change_global_lottery("br/mega-sena")
    assert dashboard.active_lottery == "br/mega-sena"
    assert dashboard.analysis_tab.active_lottery == "br/mega-sena"
    assert dashboard.filters_tab.active_lottery == "br/mega-sena"
    assert dashboard.wheeling_tab.active_lottery == "br/mega-sena"
    assert dashboard.verification_tab.active_lottery == "br/mega-sena"

def test_prophet_dashboard_push_to_pool_wiring(qapp):
    """End-to-end check of ticket #106's Predict Center -> NumberGrid signal
    chain: emitting PredictionTab.numbers_recommended must land in the main
    window's NumberGrid selection, not just call a handler in isolation."""
    dashboard = ProphetDashboard()
    dashboard.number_grid.set_max_number(60)
    dashboard.predict_tab.numbers_recommended.emit([4, 8, 15, 16, 23, 42])
    assert dashboard.number_grid.selected_numbers == {4, 8, 15, 16, 23, 42}

