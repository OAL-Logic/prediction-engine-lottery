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
    
    job.signals.new_log.connect(on_log)
    
    # Wait for job to finish (mock job is fast but we need to give it time)
    with qtbot.waitSignal(job.signals.finished, timeout=5000):
        pass
        
    assert len(logs) > 0
    assert "Task Unit Test Task completed successfully." in logs
    assert "test_task" in manager.active_jobs
