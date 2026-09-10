# 01 — QThread Concurrency Integration (ProphetJob)

**What to build:** Multi-core asynchronous job execution in the PySide6 application using a refactored `ThreadManager` and `JobSignals` bridge to prevent GUI lockup. Updates the main window to run calculations in background threads and log progress, while intercepting thread exceptions to display detailed `QMessageBox` critical alerts.

**Blocked by:** None — can start immediately

**Status:** resolved

- [x] A thread-safe `JobSignals(QObject)` is implemented carrying `progress(int, str)`, `new_log(str, str)`, `finished(dict)`, and `failed(str, str, str)` signals.
- [x] The `ThreadManager` class is refactored to handle starting, stopping, and cleaning up finished jobs dynamically using `.deleteLater()`.
- [x] A concrete QThread worker subclass is implemented that runs core engine forecasting tasks in-process, releasing the GIL during NumPy/Pandas operations.
- [x] The worker catches all exceptions during execution, captures tracebacks, and emits the `failed` signal.
- [x] The main thread GUI slots are wired to handle signals, updating progress bars and appending logs.
- [x] A thread-safe error slot on the Main Thread displays a `QMessageBox.critical()` dialog showing informative messages and detailed stack traces on thread failure.

## Comments

### Resolution Summary
1. **Verified Threading & Signaling Logic**: Verified that the thread safety bridge (`JobSignals`) and dynamic `ThreadManager` function correctly and run without GUI blocking.
2. **Environment & Sandbox Mocks**: Introduced a session-wide pytest fixture in [conftest.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/tests/conftest.py) to write mock fetch cooldowns and mock the solar/seismic environment jitter caches (`env_jitter.json`). This completely eliminates live HTTP network fetches during test runs in standard sandboxed environment.
3. **Shiboken QThread Deadlock Resolution**: Discovered and resolved a classic PySide6/Shiboken GIL import deadlock. When `engine.modules.environment` was first imported inside the background `QThread`, shibokensupport intercepted the import via `inspect.getsource()` while holding Python's global import lock, deadlocking with the main thread. Resolved by pre-importing heavy engine backend packages on the main thread during application startup in [main.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/main.py) and within [conftest.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/tests/conftest.py) for test execution.
4. **Successful Validation**: All 9 desktop tests (`tests/test_desktop_logic.py` and `tests/test_desktop_integrity.py`) now pass successfully under sandboxed constraints.

