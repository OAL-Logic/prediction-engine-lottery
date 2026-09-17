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

def test_filter_assistant_wizard_matches_cli(qapp):
    """GUI counterpart to `lottery filter-assistant`. Cross-checks the wizard's
    background funnel job against the real filter-funnel CLI command for the
    same inputs — not just "does it run," but "does it agree.\""""
    from engine.cli.utils import get_adapter
    from desktop.src.widgets.filter_assistant_wizard import FilterAssistantWizard, FilterAssistantFunnelJob

    rules = get_adapter("br/lotofacil").rules
    wizard = FilterAssistantWizard(rules)
    assert len(wizard.tier_pages) == 5  # every tier 1-5 has at least one filter

    tier1 = wizard.tier_pages[0]
    tier1.list_widget.item(0).setSelected(True)
    filter_ids = tier1.selected_ids()
    assert len(filter_ids) == 1

    pool = list(range(1, 21))
    job = FilterAssistantFunnelJob(rules, pool, filter_ids)
    results = {}
    job.signals.finished.connect(lambda rows, total: results.update({"rows": rows, "total": total}))
    failures = []
    job.signals.failed.connect(lambda msg: failures.append(msg))
    job.run()

    assert not failures, failures
    assert results["rows"][0]["after"] == results["total"]
    final = results["rows"][-1]["after"]

    from typer.testing import CliRunner
    from engine.cli.main import app as cli_app
    cli_result = CliRunner().invoke(cli_app, [
        "filter-funnel", "br/lotofacil",
        "--pool", ",".join(map(str, pool)),
        "--filters", ",".join(filter_ids),
    ])
    assert cli_result.exit_code == 0
    assert f"{final:,}" in cli_result.output, "wizard job's survivor count doesn't match the CLI's own report"

def test_filter_assistant_launch_button_wired(qapp, monkeypatch):
    """Clicking the button must actually construct and show the wizard —
    not just that a button with the right label exists somewhere."""
    from desktop.src.tabs.filters import FiltersTab
    from desktop.src.widgets.filter_assistant_wizard import FilterAssistantWizard

    shown = []
    monkeypatch.setattr(FilterAssistantWizard, "exec", lambda self: shown.append(self) or 0)

    tab = FiltersTab()
    assert hasattr(tab, "btn_filter_assistant")
    tab.btn_filter_assistant.click()
    assert len(shown) == 1
    assert isinstance(shown[0], FilterAssistantWizard)

def test_wheeling_tab_init(qapp):
    tab = WheelingTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab.pool_numbers) == 0
    assert len(tab.key_numbers) == 0

def test_position_tickets_job_combinatorics(qapp):
    """SamLotto's 'Creating a Position Number Tickets'. Hand-verified: with
    positions {1,2} x {2,3} x {3,4}, the 8-entry raw product has 4 entries
    with a repeated number (dropped), leaving exactly {1,2,3} {1,2,4} {1,3,4}
    {2,3,4} once sorted and deduplicated."""
    from desktop.src.widgets.position_tickets_dialog import PositionTicketsJob

    job = PositionTicketsJob([[1, 2], [2, 3], [3, 4]])
    results = {}
    job.signals.finished.connect(lambda tickets: results.update({"tickets": tickets}))
    failures = []
    job.signals.failed.connect(lambda msg: failures.append(msg))
    job.run()

    assert not failures, failures
    assert sorted(results["tickets"]) == sorted([[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]])

def test_position_tickets_job_safety_cap(qapp):
    from desktop.src.widgets.position_tickets_dialog import PositionTicketsJob

    job = PositionTicketsJob([list(range(1, 60)) for _ in range(15)])
    failures = []
    job.signals.failed.connect(lambda msg: failures.append(msg))
    job.run()
    assert len(failures) == 1
    assert "safety cap" in failures[0]

def test_position_tickets_dialog_matches_pick_count(qapp):
    from engine.cli.utils import get_adapter
    from desktop.src.widgets.position_tickets_dialog import PositionTicketsDialog

    rules = get_adapter("br/lotofacil").rules
    dialog = PositionTicketsDialog(rules)
    assert len(dialog.position_edits) == rules.pick_count

def test_wheeling_tab_position_tickets_reemits_own_signal(qapp):
    """launch_position_tickets_dialog() must re-emit through WheelingTab's own
    tickets_generated signal — that's what main.py already wires to the
    Ticket Store/Verification Desk, so this reaches both for free."""
    from desktop.src.tabs.wheeling import WheelingTab
    from desktop.src.widgets.position_tickets_dialog import PositionTicketsDialog

    tab = WheelingTab()
    captured = []
    tab.tickets_generated.connect(lambda t: captured.append(t))

    # Stub exec() so this doesn't block on a real modal loop; simulate the
    # dialog emitting results the way a user clicking "Send to Ticket Store"
    # would, then confirm the launcher wired it through to tab's own signal.
    def fake_exec(self):
        self.tickets_generated.emit([[1, 2, 3]])
        return 0

    original_exec = PositionTicketsDialog.exec
    PositionTicketsDialog.exec = fake_exec
    try:
        tab.launch_position_tickets_dialog()
    finally:
        PositionTicketsDialog.exec = original_exec

    assert captured == [[[1, 2, 3]]]

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

    # Regression: build_grid() used to compute row/col from (n - 1), which is
    # only correct for 1-indexed pools. For this 0-indexed one, ball 0 landed
    # at row -1 (Qt silently refuses to place it — "QGridLayout: Cannot add
    # QPushButton at row -1"), and every other ball was off by one position.
    idx = grid.layout.indexOf(grid.buttons[0])
    assert idx != -1, "ball 0 was never actually placed in the grid layout"
    row, col, _, _ = grid.layout.getItemPosition(idx)
    assert (row, col) == (0, 0), f"ball 0 should be the grid's first cell, got (row={row}, col={col})"

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

def test_prophet_dashboard_drawings_trend_push_to_pool_wiring(qapp):
    """Same end-to-end signal chain as above, but for ticket #109's Drawings
    Trend manual checker (AnalysisTab.numbers_recommended) — both tabs share
    the same handle_push_to_pool() slot."""
    dashboard = ProphetDashboard()
    dashboard.number_grid.set_max_number(60)
    dashboard.analysis_tab.numbers_recommended.emit([1, 2, 3])
    assert dashboard.number_grid.selected_numbers == {1, 2, 3}

def test_save_and_load_favorite_numbers_round_trip(qapp, tmp_path, monkeypatch):
    """SamLotto manual: 'Save and Load Your Own Favorite Number'."""
    dashboard = ProphetDashboard()
    dashboard.change_global_lottery("br/lotofacil")
    dashboard.number_grid.select_numbers([1, 7, 12, 23])

    save_path = tmp_path / "my_favorites.json"
    monkeypatch.setattr(
        "desktop.src.main.QFileDialog.getSaveFileName",
        lambda *a, **kw: (str(save_path), "Favorite Numbers (*.json)"),
    )
    monkeypatch.setattr("desktop.src.main.QMessageBox.information", lambda *a, **kw: None)
    dashboard.save_favorite_numbers()

    assert save_path.exists()
    import json
    saved = json.loads(save_path.read_text(encoding="utf-8"))
    assert saved == {"lottery": "br/lotofacil", "numbers": [1, 7, 12, 23]}

    # Clear, then load back — must restore exactly what was saved.
    dashboard.number_grid.clear_selection()
    assert dashboard.number_grid.selected_numbers == set()

    monkeypatch.setattr(
        "desktop.src.main.QFileDialog.getOpenFileName",
        lambda *a, **kw: (str(save_path), "Favorite Numbers (*.json)"),
    )
    dashboard.load_favorite_numbers()
    assert dashboard.number_grid.selected_numbers == {1, 7, 12, 23}

def test_load_favorite_numbers_rejects_malformed_file(qapp, tmp_path, monkeypatch):
    dashboard = ProphetDashboard()
    bad_path = tmp_path / "bad.json"
    bad_path.write_text('{"lottery": "br/lotofacil", "numbers": "not-a-list"}', encoding="utf-8")

    monkeypatch.setattr(
        "desktop.src.main.QFileDialog.getOpenFileName",
        lambda *a, **kw: (str(bad_path), ""),
    )
    errors = []
    monkeypatch.setattr("desktop.src.main.QMessageBox.critical", lambda *a, **kw: errors.append(a))
    dashboard.load_favorite_numbers()
    assert len(errors) == 1

def test_select_random_numbers_picks_valid_distinct_count(qapp):
    """SamLotto manual: 'Random Select Numbers'."""
    dashboard = ProphetDashboard()
    dashboard.change_global_lottery("br/lotofacil")  # pick_count=15, range 1-25
    dashboard.select_random_numbers()
    picked = dashboard.number_grid.selected_numbers
    assert len(picked) == 15
    assert all(1 <= n <= 25 for n in picked)

    # Re-running must be capable of landing on a different set (not hardcoded) —
    # not asserted directly (random could coincidentally repeat), but rules-driven
    # count must track the active game after switching.
    dashboard.change_global_lottery("br/mega-sena")  # pick_count=6, range 1-60
    dashboard.select_random_numbers()
    picked2 = dashboard.number_grid.selected_numbers
    assert len(picked2) == 6
    assert all(1 <= n <= 60 for n in picked2)

def test_select_last_drawn_numbers(qapp, monkeypatch):
    """SamLotto manual: quick-pick 'Last x Drawings Numbers'."""
    dashboard = ProphetDashboard()
    dashboard.change_global_lottery("br/lotofacil")

    monkeypatch.setattr("desktop.src.main.QInputDialog.getInt", lambda *a, **kw: (3, True))

    dashboard.select_last_drawn_numbers()
    from engine.modules.storage import storage
    df = storage.load_draws("br/lotofacil", limit=3)
    expected = set()
    for nums in df["numbers"]:
        expected.update(nums)

    assert dashboard.number_grid.selected_numbers == expected
    assert len(expected) > 0

def test_select_last_drawn_numbers_cancelled(qapp, monkeypatch):
    """Dialog cancel (ok=False) must leave the pool untouched."""
    dashboard = ProphetDashboard()
    dashboard.number_grid.select_numbers([1, 2, 3])
    monkeypatch.setattr("desktop.src.main.QInputDialog.getInt", lambda *a, **kw: (5, False))
    dashboard.select_last_drawn_numbers()
    assert dashboard.number_grid.selected_numbers == {1, 2, 3}

