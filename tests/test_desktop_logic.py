import pytest
from PySide6.QtWidgets import QApplication
from desktop.src.telemetry.manager import ThreadManager

@pytest.fixture
def app(qtbot):
    # Must be QApplication, not QCoreApplication — see the comment in
    # test_desktop_gateway.py's identical fixture for why: this file builds
    # real widgets (test_analysis_tab_stats_table_click), so it needs the
    # real thing regardless, but the bug was cross-file (whichever ran first
    # won the process-wide singleton), so every one of these fixtures had to
    # be consistent.
    return QApplication.instance() or QApplication([])

def test_thread_manager_starts_job(app, qtbot):
    manager = ThreadManager()
    
    # Track signal emission
    logs = []
    def on_log(msg, level):
        logs.append(msg)
        
    job = manager.start_job("test_task", "Unit Test Task")
    assert job is not None
    assert job.isRunning()
    assert "test_task" in manager.active_jobs
    
    job.signals.new_log.connect(on_log)
    
    # Wait for job to finish (mock job is fast but we need to give it time)
    with qtbot.waitSignal(job.signals.finished, timeout=5000):
        pass
        
    # Wait a brief moment for the QThread's native finished signal to trigger cleanup
    qtbot.wait(100)
        
    assert len(logs) > 0
    assert "Task Unit Test Task completed successfully." in logs
    assert "test_task" not in manager.active_jobs

def test_forecast_job_runs(app, qtbot):
    import pytestqt
    from desktop.src.telemetry.manager import ForecastJob
    # Initialize ForecastJob with 35 draws history and a fast strategy
    job = ForecastJob(lottery_id="br/lotofacil", strategies=["weighted"], count=2, num_draws=35)
    
    logs = []
    job.signals.new_log.connect(lambda msg, lvl: logs.append(msg))
    
    failures = []
    job.signals.failed.connect(lambda title, msg, tb: failures.append((title, msg, tb)))
    
    results = {}
    job.signals.finished.connect(results.update)
    
    job.start()
    
    # Wait for finished signal
    with qtbot.waitSignal(job.signals.finished, timeout=15000):
        pass
        
    if failures:
        title, msg, tb = failures[0]
        pytest.fail(f"ForecastJob failed: {title} - {msg}\nTraceback:\n{tb}")
        
    assert results.get("status") == "success"
    assert "tickets" in results
    assert len(results["tickets"]) == 2
    assert len(results["tickets"][0]) == 15  # Lotofácil pick count
    assert "confidence_scores" in results
    assert len(logs) > 0


def test_train_job_runs(app, qtbot):
    from desktop.src.telemetry.manager import TrainJob
    # Initialize TrainJob with low iterations/population for rapid execution
    job = TrainJob(lottery_id="br/lotofacil", generations=3, pop_size=10, strategy="weighted")
    
    results = {}
    job.signals.finished.connect(results.update)
    
    job.start()
    
    with qtbot.waitSignal(job.signals.finished, timeout=15000):
        pass
        
    assert results.get("status") == "success"
    assert "ticket" in results
    assert len(results["ticket"]) == 15
    assert "fitness" in results


def test_duckdb_draws_table_model_crud(tmp_path):
    import pandas as pd
    from PySide6.QtCore import Qt
    from engine.modules.storage import storage
    from desktop.src.tabs.database import DuckDBDrawsTableModel
    
    # Save original database path and policy
    orig_db_path = storage.db_path
    orig_policy = storage.policy
    
    # Point storage to isolated temp DB and set policy to primary to avoid writing JSON partition files
    storage.db_path = tmp_path / "test_lottery.db"
    storage.policy = "primary"
    storage._init_db()
    
    try:
        # Create test dataframe
        df = pd.DataFrame([
            {"draw_id": 2, "draw_date": "2026-08-20", "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "bonus": []},
            {"draw_id": 1, "draw_date": "2026-08-19", "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "bonus": []}
        ])
        
        model = DuckDBDrawsTableModel(lottery_id="br/lotofacil", df=df)
        
        # Test row/column counts
        assert model.rowCount() == 2
        assert model.columnCount() == 4
        
        # Test data retrieval
        assert model.data(model.index(0, 0)) == "2"
        assert model.data(model.index(0, 1)) == "2026-08-20"
        assert model.data(model.index(0, 2)) == "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15"
        
        # Test flags (draw_id is read-only, others editable)
        assert not (model.flags(model.index(0, 0)) & Qt.ItemIsEditable)
        assert model.flags(model.index(0, 1)) & Qt.ItemIsEditable
        assert model.flags(model.index(0, 2)) & Qt.ItemIsEditable
        
        # Test inline editing validations
        # 1. Invalid date string
        assert not model.setData(model.index(0, 1), "invalid-date-string")
        # 2. Valid date string
        assert model.setData(model.index(0, 1), "2026-08-21")
        assert model.data(model.index(0, 1)) == "2026-08-21"
        
        # 3. Invalid numbers (under pick_count=15 rules for lotofacil)
        assert not model.setData(model.index(0, 2), "1, 2, 3, 4, 5")
        # 4. Valid numbers
        valid_numbers_str = "2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16"
        assert model.setData(model.index(0, 2), valid_numbers_str)
        assert model.data(model.index(0, 2)) == valid_numbers_str
        
        # Test insert_draw
        new_draw = {
            "draw_id": 3,
            "draw_date": "2026-08-22",
            "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "bonus": []
        }
        assert model.insert_draw(new_draw)
        assert model.rowCount() == 3
        # Sorted descending by draw_id, so draw_id 3 is row 0
        assert model.data(model.index(0, 0)) == "3"
        
        # Test remove_draw
        assert model.remove_draw(0)
        assert model.rowCount() == 2
        assert model.data(model.index(0, 0)) == "2"
        
    finally:
        # Restore original configurations
        storage.db_path = orig_db_path
        storage.policy = orig_policy


def test_samlotto_bidirectional_converter(tmp_path):
    from desktop.src.utils.converter import parse_samlotto_txt, export_duckdb_to_samlotto
    from engine.modules.storage import storage
    
    # Test file parsing
    # Content format: M/D/YYYY followed by space-separated zero-padded numbers
    file_content = (
        "10/12/2023 01 02 03 04 05 06\r\n"
        "5/7/2024 07 08 09 10 11 12\r\n"
    )
    
    # Pick count = 5, Bonus count = 1
    draws = parse_samlotto_txt(file_content, pick_count=5, bonus_count=1)
    
    assert len(draws) == 2
    assert draws[0]["draw_id"] == 1
    assert draws[0]["draw_date"] == "2023-10-12"
    assert draws[0]["numbers"] == [1, 2, 3, 4, 5]
    assert draws[0]["bonus"] == [6]
    
    assert draws[1]["draw_id"] == 2
    assert draws[1]["draw_date"] == "2024-05-07"
    assert draws[1]["numbers"] == [7, 8, 9, 10, 11]
    assert draws[1]["bonus"] == [12]

    # Test database exporting
    orig_db_path = storage.db_path
    orig_policy = storage.policy
    
    storage.db_path = tmp_path / "test_lottery_conv.db"
    storage.policy = "primary"
    storage._init_db()
    
    try:
        # Save to DB
        storage.save_draws("us/powerball", draws)
        
        # Export from DB
        exported_content = export_duckdb_to_samlotto("us/powerball")
        
        # Compare
        # Export formats to M/D/YYYY, zero-pads to 2 digits, CRLF endings
        expected_exported = (
            "10/12/2023 01 02 03 04 05 06\r\n"
            "5/7/2024 07 08 09 10 11 12\r\n"
        )
        assert exported_content == expected_exported
    finally:
        storage.db_path = orig_db_path
        storage.policy = orig_policy


def test_skips_job_runs(app, qtbot):
    from desktop.src.telemetry.manager import SkipsJob
    job = SkipsJob(lottery_id="br/lotofacil", number=7, num_draws=35)
    
    logs = []
    job.signals.new_log.connect(lambda msg, lvl: logs.append(msg))
    
    failures = []
    job.signals.failed.connect(lambda title, msg, tb: failures.append((title, msg, tb)))
    
    results = {}
    job.signals.finished.connect(results.update)
    
    job.start()
    
    with qtbot.waitSignal(job.signals.finished, timeout=15000):
        pass
        
    if failures:
        title, msg, tb = failures[0]
        pytest.fail(f"SkipsJob failed: {title} - {msg}\nTraceback:\n{tb}")
        
    assert results.get("status") == "success"
    assert "number" in results
    assert results["number"] == 7
    assert "actual_skips" in results
    assert "average_skip" in results
    assert "now_skip" in results
    assert "draw_ids" in results
    assert len(logs) > 0


def test_analysis_tab_stats_table_click(app, qtbot):
    from desktop.src.tabs.analysis import AnalysisTab
    from desktop.src.widgets.skips_inspector import SkipsInspectorDialog
    from desktop.src.telemetry.manager import ThreadManager

    class DummyMainWindow:
        def __init__(self):
            self.thread_manager = ThreadManager()
    
    tab = AnalysisTab()
    win = DummyMainWindow()
    tab.window = lambda: win
    
    tab.sync_theme_colors()
    tab.load_data()
    
    # Ensure stats table is populated
    assert tab.stats_table.rowCount() > 0
    
    # Click the first row (Ball 01)
    tab.stats_table.cellClicked.emit(0, 0)
    
    # Wait for dialog to instantiate and load data
    # The skips job runs asynchronously in a thread
    def check_dialog():
        assert tab.skips_dialog is not None
        assert tab.skips_dialog.isVisible()
        assert tab.skips_dialog.ledger_table.rowCount() > 0

    qtbot.waitUntil(check_dialog, timeout=10000)
    
    # Cleanup
    tab.skips_dialog.close()
    for job in list(win.thread_manager.active_jobs.values()):
        job.wait()


def test_limits_calculation_job(app, qtbot):
    from desktop.src.telemetry.manager import LimitsCalculationJob
    
    # Run limit calculation for odd/even count
    job = LimitsCalculationJob(
        lottery_id="br/lotofacil",
        active_filter_ids=["structural_odd_count", "structural_prime_count"],
        limit=10
    )
    
    results = {}
    job.signals.finished.connect(results.update)
    
    job.start()
    
    with qtbot.waitSignal(job.signals.finished, timeout=5000):
        pass
        
    assert results.get("status") == "success"
    assert "limits" in results
    limits = results["limits"]
    assert "structural_odd_count" in limits
    assert "structural_prime_count" in limits
    lo, hi = limits["structural_odd_count"]
    assert lo >= 0 and hi <= 15


def test_forecast_job_offset_uses_earlier_history(app, qtbot):
    """offset=N holds back the last N draws before slicing — ticket #106's
    Predict Center 'Offset' control. Zero-offset default stays covered by
    test_forecast_job_runs; this only exercises the new parameter."""
    from desktop.src.telemetry.manager import ForecastJob

    job = ForecastJob(lottery_id="br/lotofacil", strategies=["weighted"], count=1, num_draws=35, offset=5)

    results = {}
    job.signals.finished.connect(results.update)

    failures = []
    job.signals.failed.connect(lambda title, msg, tb: failures.append((title, msg, tb)))

    job.start()
    with qtbot.waitSignal(job.signals.finished, timeout=15000):
        pass

    if failures:
        title, msg, tb = failures[0]
        pytest.fail(f"ForecastJob(offset=5) failed: {title} - {msg}\nTraceback:\n{tb}")

    assert results.get("status") == "success"
    assert results.get("num_draws_analyzed", 0) <= 35


def test_formula_verification_job_runs(app, qtbot):
    """Verification Desk 'Formula Leaderboard' — thin QThread wrapper around
    engine.services.backtest.run_backtest(). Kept to a single fast strategy
    and a short depth so the walk-forward backtest stays quick in CI."""
    from desktop.src.telemetry.manager import FormulaVerificationJob

    job = FormulaVerificationJob(lottery_id="br/lotofacil", strategy_names=["weighted"], depth=6)

    logs = []
    job.signals.new_log.connect(lambda msg, lvl: logs.append(msg))

    failures = []
    job.signals.failed.connect(lambda title, msg, tb: failures.append((title, msg, tb)))

    results = {}
    job.signals.finished.connect(results.update)

    job.start()
    with qtbot.waitSignal(job.signals.finished, timeout=20000):
        pass

    if failures:
        title, msg, tb = failures[0]
        pytest.fail(f"FormulaVerificationJob failed: {title} - {msg}\nTraceback:\n{tb}")

    assert results.get("status") == "success"
    leaderboard = results.get("leaderboard", [])
    assert len(leaderboard) == 1
    row = leaderboard[0]
    assert row["formula"] == "weighted"
    assert row["draws_tested"] <= 6
    assert 0.0 <= row["win_rate_pct"] <= 100.0
    assert len(logs) > 0


def test_pruning_job(app, qtbot):
    from desktop.src.telemetry.manager import PruningJob
    
    tickets = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], # 8 odd
        [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 23, 21], # 3 odd
    ]
    active_filters = [
        {"id": "structural_odd_count", "type": "base", "lo": 5, "hi": 10}
    ]
    logical_condition = {"mode": "AND"}
    
    job = PruningJob(
        lottery_id="br/lotofacil",
        tickets=tickets,
        active_filters=active_filters,
        logical_condition=logical_condition
    )
    
    results = {}
    job.signals.finished.connect(results.update)
    
    job.start()
    
    with qtbot.waitSignal(job.signals.finished, timeout=5000):
        pass
        
    assert results.get("status") == "success"
    passed_indices = results.get("passed_indices", [])
    elimination_counts = results.get("elimination_counts", {})
    
    assert 0 in passed_indices # 1st ticket has 8 odds, falls in [5, 10]
    assert 1 not in passed_indices # 2nd ticket has 3 odds, outside [5, 10]
    assert elimination_counts.get("structural_odd_count") == 1


def test_ticket_store_reduction_job(app, qtbot):
    """Ticket Store 'Reduce (WRG)' — thin QThread wrapper around
    engine.modules.wheels_wrg.WheelingEngine.reduce_tickets(). Full wheel over
    a 5-number pool (all C(5,3)=10 tickets) reduced under a '2 if 3' guarantee
    must shrink, and the guarantee must still hold for every possible 3-draw."""
    from itertools import combinations
    from desktop.src.telemetry.manager import TicketStoreReductionJob

    pool = [1, 2, 3, 4, 5]
    all_tickets = [list(c) for c in combinations(pool, 3)]

    job = TicketStoreReductionJob(all_tickets, t=2, m=3)

    failures = []
    job.signals.failed.connect(lambda title, msg, tb: failures.append((title, msg, tb)))

    results = {}
    job.signals.finished.connect(results.update)

    job.start()
    with qtbot.waitSignal(job.signals.finished, timeout=5000):
        pass

    if failures:
        title, msg, tb = failures[0]
        pytest.fail(f"TicketStoreReductionJob failed: {title} - {msg}\nTraceback:\n{tb}")

    assert results.get("status") == "success"
    assert results.get("original_count") == 10
    kept = results.get("kept_tickets", [])
    assert 0 < len(kept) < 10

    for subset in combinations(pool, 3):
        subset = set(subset)
        assert any(len(subset & set(ticket)) >= 2 for ticket in kept), (
            f"coverage guarantee violated for draw {subset}: no kept ticket has >=2 matches"
        )


def test_ticket_store_reduction_job_rejects_oversized_universe(app, qtbot):
    """Guards against the pure-Python O(subsets) reduce_tickets() loop hanging
    the UI: a pool this size makes C(30, 15) > 150M target subsets, which must
    fail fast with a clear message instead of freezing."""
    from desktop.src.telemetry.manager import TicketStoreReductionJob

    tickets = [list(range(1, 16)), list(range(16, 31))]
    job = TicketStoreReductionJob(tickets, t=10, m=15)

    failures = []
    job.signals.failed.connect(lambda title, msg, tb: failures.append((title, msg, tb)))

    job.start()
    with qtbot.waitSignal(job.signals.failed, timeout=5000):
        pass

    assert len(failures) == 1
    title, msg, tb = failures[0]
    assert "too large" in msg




