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
    from desktop.src.telemetry.manager import ForecastJob
    # Initialize ForecastJob with 35 draws history and a fast strategy
    job = ForecastJob(lottery_id="br/lotofacil", strategies=["weighted"], count=2, num_draws=35)
    
    logs = []
    job.signals.new_log.connect(lambda msg, lvl: logs.append(msg))
    
    results = {}
    job.signals.finished.connect(results.update)
    
    job.start()
    
    with qtbot.waitSignal(job.signals.finished, timeout=15000):
        pass
        
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
