import pytest
from PySide6.QtCore import QCoreApplication
from desktop.src.telemetry.manager import ThreadManager

@pytest.fixture
def app(qtbot):
    # This fixture ensures a QApplication is running for the tests
    return QCoreApplication.instance() or QCoreApplication([])

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



