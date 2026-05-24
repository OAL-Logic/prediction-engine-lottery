from PySide6.QtCore import QThread, Signal, QObject

class TelemetrySignal(QObject):
    """Signals for background analytical jobs."""
    new_log = Signal(str, str) # message, level
    progress = Signal(int)
    finished = Signal(dict) # result data

class ProphetJob(QThread):
    """Base class for non-blocking analytical tasks."""
    def __init__(self, task_name: str, params: dict = None):
        super().__init__()
        self.task_name = task_name
        self.params = params or {}
        self.signals = TelemetrySignal()

    def run(self):
        self.signals.new_log.emit(f"Starting task: {self.task_name}...", "INFO")
        try:
            # Mock implementation for Story 5.4
            import time
            for i in range(1, 101, 10):
                time.sleep(0.1)
                self.signals.progress.emit(i)
                self.signals.new_log.emit(f"Processing node cluster {i//10}/10...", "INFO")
            
            self.signals.new_log.emit(f"Task {self.task_name} completed successfully.", "SUCCESS")
            self.signals.finished.emit({"status": "ok", "task": self.task_name})
        except Exception as e:
            self.signals.new_log.emit(f"Task {self.task_name} failed: {str(e)}", "ERROR")
            self.signals.finished.emit({"status": "error", "error": str(e)})

class ThreadManager:
    """Orchestrates background threads to prevent UI lockup."""
    def __init__(self):
        self.active_jobs = {}

    def start_job(self, task_id: str, task_name: str, params: dict = None):
        if task_id in self.active_jobs and self.active_jobs[task_id].isRunning():
            return None
            
        job = ProphetJob(task_name, params)
        self.active_jobs[task_id] = job
        job.start()
        return job
