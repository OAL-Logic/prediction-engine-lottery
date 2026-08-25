---
label: wayfinder:map
destination: PySide6 modern desktop interface matching SamLotto Free Edition features
status: active
created: 2026-08-11
---

# SamLotto Qt Modern Interface Map

## Destination

A modern PySide6 desktop application ("the cockpit") that implements every feature of the SamLotto Free Edition (drawings management, 18-method tabbed statistics with skips drill-down, smart ticket generation, 50 base + 18 advanced filters with N-of-M logical logic, and Formula 1-6 predictions). The app runs in-process via direct Python imports from the core engine, stores drawings primarily in `data/lottery.db` (DuckDB), supports importing/exporting SamLotto flat `.txt` files, and is styled with a custom dark-mode aesthetic.

See the full [Product Requirement Document (PRD)](decisions/samlotto-qt-interface-spec.md) for detailed requirements and specifications.

## Notes

- **Domain**: PySide6 GUI development, UI/UX design, custom QSS styling, QThread/worker concurrent execution, DuckDB integration, and interactive data visualization.
- **Skills to consult**: `codebase-design` for window/module boundaries, `prototype` for layout/styling mocks, and `bmad-grilling` for usability trade-offs.
- **Standing preferences**:
  - **Framework**: PySide6 (Official Qt for Python, LGPL).
  - **Backend integration**: Direct in-process imports of `engine.*` modules and DuckDB connections.
  - **Storage**: DuckDB-first (`data/lottery.db`). Flat `.txt` file support is for import/export only.
  - **Aesthetic**: Sleek Dark Mode (custom QSS, clean visual hierarchy, colorful plotting).
  - **Concurrency**: Heavy operations (forecasts, backtests, audits) must run asynchronously via QThreads to keep UI responsive.

## Decisions so far

<!-- Index of closed tickets. One line per ticket: gist + link. -->

- [#101 Qt app bootstrap and threading](tickets/101-qt-app-bootstrap-and-threading.md) — Asynchronous QThread worker model with custom JobSignals and main-thread QMessageBox error logging established.
- [#102 Drawings and registry manager](tickets/102-drawings-and-registry-manager.md) — Implemented DuckDB CRUD QAbstractTableModel and bidirectional parser stubs for SamLotto .txt compatibility.
- [#103 Sleek dark theme and layout](tickets/103-sleek-dark-theme-and-layout.md) — Unified split-pane cockpit layout designed and implemented in a runnable PySide6 prototype with custom QSS styling and responsive grids.
- [#104 Interactive skips chart](tickets/104-interactive-skips-chart.md) — Matplotlib (`FigureCanvasQTAgg`) kept as the single plotting library (zero new dependency, only one with a native heatmap); drill-down flows through a new `SkipsJob(QThread)` into a table+chart `SkipsInspectorPanel`.
- [#105 Filter setup panel](tickets/105-filter-setup-panel.md) — Implemented tabbed Setup Dock (FiltersTab) with inline range sliders, advanced filters add/remove panels, logical N-of-M condition checks, auto-calculating limits, and background pruning execution.

## Tickets (frontier)

Open, unblocked tickets — pick one to claim:

- [#106 Prediction verification GUI](tickets/106-prediction-verification-gui.md) — Build the Formula-1..6 prediction form, verification run console, and pool-push interaction.

## Tickets (blocked)

<!-- No blocked tickets remaining -->

## Not yet specified

Fog that is in scope but not sharp enough to ticket yet:

- **Optimization and wheeling port**: Mapping the abbreviated wheels and ticket store reduction optimization algorithms (F10-F12) to the GUI ticket store menu actions.
- **Online database updater**: Interfacing the GUI drawings update window (A11) with the engine's scraping and fetch adapters.
- **High-density statistics tabs**: Deciding how to present the 11+ statistics sheets (AC, Low-High, Sums, etc.) cleanly inside the tabbed stats workspace without overwhelming the screen.
- **Export & Print formatting**: Designing print layouts for tickets (S40) and custom export formatting options.

## Out of scope

- Direct binary integration or linking with `samlotto.exe`.
- Running GUI code as a separate web client (Electron/browser).
- Pro-edition features that exceed the Free Edition capability checklist (unlocked wheels, unlimited numbers, custom script filters).
