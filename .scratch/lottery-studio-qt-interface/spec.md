---
title: Spec — Lottery Studio Qt Desktop Interface (Prophet Dashboard)
status: ready-for-agent
labels:
  - ready-for-agent
---

# Specification: Lottery Studio Qt Desktop Interface (Prophet Dashboard)

## Problem Statement

The user currently interacts with the lottery prediction engine via the Command Line Interface (OpenTUI) and a gestural Mobile App (Expo). However, for advanced, multi-tab forensic analysis, real-time model training monitoring, and spreadsheet-like database operations, a terminal or a small mobile screen is insufficient. 

Users need a persistent, high-density, cross-platform desktop application cockpit to perform complex mathematical audits, manage historical drawing databases, configure advanced composable filtering conditions, and inspect number trends (like skips and intervals) without GUI lag or locking.

## Solution

Implement the **Prophet Desktop Client** (PySide6/Qt for Python). The client acts as a professional-grade alternative cockpit styled under a dark neon design aesthetic ("Forensic Neon"). It integrates:
- **Draws Database Tab:** Spreadsheet-like editable grid of all drawings with DuckDB backend CRUD operations, and flat-file import/export of Lottery Studio `.txt` formats.
- **Statistical Cockpit Tab:** Multi-dimensional charts showing frequencies, gaps, and number intervals.
- **Harmony Gate Filters Tab:** Interactive number pool selection and range filters running in background worker threads.
- **Wheeling Workshop Tab:** Cover designs generation with direct ticket transfer to verification.
- **Predict Center & Verification Desk Tabs:** Optimization parameters (Stacking AI, LSTM-CRF, etc.), genetic swarm training, and an ROI-based backtesting leaderboard.
- **Telemetry Console Tab:** Real-time monospaced logging console receiving server-side engine signals.

## User Stories

1. As an Analyst, I want to launch a PySide6-based desktop application, so that I can perform heavy computational analysis on lottery draws in a dedicated cockpit.
2. As a Hobbyist, I want to view a unified tabbed interface, so that I can easily navigate between database views, analysis charts, and ticket predictors.
3. As a User, I want to select a global lottery context (e.g., Lotofácil, Mega-Sena), so that all charts, grids, and predictions instantly update to reflect that game.
4. As an Analyst, I want to view a spreadsheet-like grid of all historical drawings, so that I can browse drawing history efficiently.
5. As an Administrator, I want to edit drawings directly in the grid, so that I can quickly fix typos or incorrect records in the database.
6. As an Administrator, I want to insert or delete drawings, so that I can keep the database up-to-date with new results.
7. As a User, I want to import drawings from a Lottery Studio space-delimited flat text file, so that I do not have to enter thousands of draws manually.
8. As a User, I want to export drawings to a Lottery Studio format text file, so that I can share or reuse my database with other legacy lottery tools.
9. As an Analyst, I want to visualize number frequencies and gaps in interactive charts, so that I can recognize underlying trends.
10. As an Analyst, I want to inspect a number's skips (Actual, Average, and Now skips) and view its historical skip interval spacing on a bar chart, so that I can determine if a number is overdue.
11. As a User, I want to toggle numbers in/out of a pool using an interactive clickable grid, so that I can define a custom subset of numbers to generate tickets from.
12. As a Hobbyist, I want to set and adjust base filters (like Sum, Parity, Decade) using range sliders, so that I can exclude statistically unlikely number combinations.
13. As an Analyst, I want to apply logical conditions (AND/OR/N-of-M) to combined filters, so that I can design highly custom pruning strategies.
14. As an Analyst, I want to run a background computation to automatically set filter bounds based on historical averages, so that I don't have to calculate them myself.
15. As a User, I want to see the count of tickets eliminated by each active filter, so that I can see the exact impact of my filtering decisions.
16. As a User, I want to choose a wheeling cover design, apply it to a selected pool of numbers, and generate tickets, so that I can mathematically guarantee a prize if a certain number of hits occur.
17. As a User, I want to click a button to send my wheeled tickets directly to the Verification tab, so that I can audit their historical performance immediately.
18. As a Hobbyist, I want to select a forecasting model (like Stacking AI or LSTM-CRF) and generate suggested tickets, so that I can buy optimized bets.
19. As an Analyst, I want to trigger a Swarm Intelligence genetic algorithm to retrain forecasting models on the latest draw history, so that my models are constantly calibrated.
20. As a User, I want model training and prediction generation to run in background threads, so that the application GUI does not freeze during intensive tasks.
21. As an Analyst, I want a Telemetry Console that shows a live scrolling stream of backend logs, so that I can monitor the execution of long-running operations.
22. As a User, I want visual alerts with detailed crash tracebacks to pop up if a background thread encounters a critical error, so that I can understand and debug the failure.
23. As a User, I want to select different visual themes (like Matrix Green or Neon Pink) from a menu, so that I can customize the cockpit's look to my preference.

## Implementation Decisions

- **GUI Engine (desktop package):** Built with PySide6 (`desktop/src/main.py`), utilizing custom widgets for the `DatabaseTab`, `AnalysisTab`, `FiltersTab`, `WheelingTab`, `PredictionTab`, `VerificationTab`, `ExpectedValueTab`, and `TelemetryTab`.
- **Global Event Synchronization:** Managed using Qt Signals and Slots. Specifically:
  - `DatabaseTab.lottery_selector.currentTextChanged` propagates context changes globally.
  - `DatabaseTab.database_changed` triggers UI reloads on analysis and verification tabs.
  - `WheelingTab.tickets_generated` shares combinations with the Verification Desk.
- **Asynchronous Processing (`ThreadManager` & `JobSignals`):** All computational jobs (forecasting, training, filter audits, db loading) must subclass `QThread` (e.g., `ForecastJob`, `TrainJob`) or use `QRunnable`. Communication between worker threads and the main thread is strictly mediated via `JobSignals` (type-safe `pyqtSignal` objects for progress, logs, finish payloads, and errors). The GUI thread must never execute blocking calculations directly.
- **Database Model (`DuckDBDrawsTableModel`):** An editable model derived from `QAbstractTableModel` wraps DuckDB queries, managing CRUD edits safely by upserting dates and number sequences, and emitting `dataChanged` to trigger view refreshes.
- **File Conversion Utilities:** Bidirectional parser/converter logic for legacy Lottery Studio `.txt` files (space-delimited, `M/D/YYYY` date format, CRLF line endings) to enable instant database synchronization.
- **Charts and Visualizations (`pyqtgraph` & `matplotlib`):** Integrating fast-rendering charts styled with neon aesthetics. Specifically, skips analysis plots use `pyqtgraph` for interactive bar charts, and general analysis plots use a styled `matplotlib` backend.
- **Theming System (`ThemeManager`):** Manages stylesheet injection using custom QSS files or dynamically generated styling tokens (`dark` background, neon colors for selected/active states).

## Testing Decisions

### Seams
We test the desktop cockpit functionality across three distinct seams to guarantee UI responsiveness and execution validity:
1. **Core Strategy Seam (Highest level - Logic Only):** Standard unit testing of forecasting models and statistical modules directly via Python inputs (NumPy arrays, Pandas DataFrames) and assertions, completely independent of Qt UI layouts.
2. **QThread Worker Seam (Asynchronous Execution):** Testing background jobs (`ForecastJob`, `TrainJob`, `ProphetJob`) using `pytest-qt`'s `qtbot.waitSignal`. We verify that tasks spin off, report progress accurately, catch internal errors, and emit type-safe signals with finished payloads, decoupling threading logic from UI view implementations.
3. **Widget Component Seam (GUI & Event Wiring):** Instantiating individual tabs and the main `ProphetDashboard` in headless test environments via pytest fixtures to assert layout integrity, active lottery swaps propagation, and slot handling logic (e.g., verifying a dropdown change triggers statistical updates in child tabs).

### Prior Art
- Existing unit tests in [test_desktop_logic.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/tests/test_desktop_logic.py) verify the `ThreadManager` start/stop routines, `ForecastJob` outputs, and `TrainJob` genetic updates.
- GUI initialization and global signal context checks are modeled after [test_desktop_integrity.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/tests/test_desktop_integrity.py).

## Out of Scope

- Direct hardware integration with physical lottery ticket printing machines.
- Adding a real-time web crawler inside the PySide6 app to fetch draw results (all fetches must go through the existing engine/API adapters).
- In-app payment gateways or premium licensing servers (licensing checks remain local-only).

## Further Notes
- Adheres to the **v11.1 "Prophet Synthesis"** architecture rules. Thread isolation must be preserved at all times during heavy calculations to ensure 99.9% crash-free sessions.
