# 01 — QThread Concurrency Integration (ProphetJob)

**What to build:** Multi-core asynchronous job execution in the PySide6 application using a refactored `ThreadManager` and `JobSignals` bridge to prevent GUI lockup. Updates the main window to run calculations in background threads and log progress, while intercepting thread exceptions to display detailed `QMessageBox` critical alerts.

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] A thread-safe `JobSignals(QObject)` is implemented carrying `progress(int, str)`, `new_log(str, str)`, `finished(dict)`, and `failed(str, str, str)` signals.
- [ ] The `ThreadManager` class is refactored to handle starting, stopping, and cleaning up finished jobs dynamically using `.deleteLater()`.
- [ ] A concrete QThread worker subclass is implemented that runs core engine forecasting tasks in-process, releasing the GIL during NumPy/Pandas operations.
- [ ] The worker catches all exceptions during execution, captures tracebacks, and emits the `failed` signal.
- [ ] The main thread GUI slots are wired to handle signals, updating progress bars and appending logs.
- [ ] A thread-safe error slot on the Main Thread displays a `QMessageBox.critical()` dialog showing informative messages and detailed stack traces on thread failure.
