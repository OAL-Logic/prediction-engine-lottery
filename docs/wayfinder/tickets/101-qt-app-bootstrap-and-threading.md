---
id: "101"
type: research
status: closed
assignee: antigravity
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-08-11
---

# Qt app bootstrap and threading

## Question

How should the PySide6 application bootstrap and coordinate background worker threads to run heavy core-engine computations (such as forecasts, calibrations, and backtests) without locking or freezing the desktop GUI?

## Context

- The entrypoint in [main.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/desktop/src/main.py) bootstraps a `ProphetDashboard` (QMainWindow) and uses a `ThreadManager` to spin up jobs.
- Heavy computations from `engine/` (e.g., stability/discrimination simulations in `forecast`, multi-draw loops in `calibrate`, and grid-searches in `tune`) can run from seconds to minutes. Running these in the main GUI thread will freeze the application window.
- The UI contains a `TelemetryTab` and uses a `TelemetryClient` connected to a WebSocket, but background tasks need a reliable, native Qt threading model (`QThread`, `QThreadPool`, or `QRunnable`) to communicate progress, logs, and finished states safely back to PySide6 widgets via custom signals.

## What to research

1. **Threading Model Choice**:
   - Evaluate `QThreadPool` + `QRunnable` vs. subclassing `QThread` vs. running an asyncio event loop alongside Qt.
   - Choose the best pattern for general core-engine execution and long-running tasks.
2. **Signal-Based Communication**:
   - Define the custom PySide6 signals (`progress`, `log`, `finished`, `error`) needed for workers.
   - Design how logs generated inside the engine (via standard `logging`) are captured and routed to the UI's `TelemetryTab`.
3. **Thread manager audit**:
   - Inspect the existing `ThreadManager` in `desktop/src/telemetry/manager.py` (if it exists) or design its replacement to handle job scheduling, cancellation, and progress updates cleanly.
4. **Error Handing**:
   - Establish how exceptions raised in background workers are captured and surfaced as error dialogs (QMessageBox) in the main thread.

## Acceptance criteria

- [x] A recommended background worker design pattern is documented in a markdown design record.
- [x] Code templates showing how to wrap a core engine command (e.g. `forecast`) in a Qt worker thread are provided.
- [x] A review of the current `ThreadManager` implementation is captured.
- [x] Output is a markdown decision spec linked from this ticket.

## Resolution

Resolved on 2026-08-11. See [MDR-101: Qt App Bootstrap and Threading Design](../decisions/101-qt-app-bootstrap-and-threading-decision.md) for full design and details.

### Key Decisions
- **Threading Framework**: subclassing `QThread` combined with helper `JobSignals` is chosen as the standard pattern for stateful long-running computations.
- **Signals Bridge**: Uses `progress(int, str)`, `new_log(str, str)`, `finished(dict)`, and `failed(str, str, str)` signals to cross thread boundaries safely.
- **Safety**: Threads catch all exceptions, capture tracebacks, emit the `failed` signal, and let the main GUI thread safely pop up `QMessageBox` details.
- **Manager Refactoring**: Thread manager is upgraded to coordinate thread lifecycle garbage collection via `.deleteLater()` and handle user cancellations.
