# Lottery Studio-qt-interface-spec

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ Lottery Studio-qt-interface-map](lottery-studio-qt-interface-map.md) · [Pick 3 Tic-Tac-Toe Generator  Free Lottery Software ➡️](pick-3-tic-tac-toe-generator-free-lottery-software.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [User Stories](#user-stories)
  - [A. Drawings & Game Management](#a-drawings-game-management)
  - [B. Statistical Analysis](#b-statistical-analysis)
  - [C. Ticket Generation](#c-ticket-generation)
  - [D. Filtering](#d-filtering)
  - [E. Prediction & Verification](#e-prediction-verification)
  - [F. Ticket Store Workspace](#f-ticket-store-workspace)
- [Implementation Decisions](#implementation-decisions)
  - [1. Architectural Integration](#1-architectural-integration)
  - [2. Concurrency & Concurrency Model (MDR-101)](#2-concurrency-concurrency-model-mdr-101)
  - [3. Database CRUD & Converter bindings (MDR-102)](#3-database-crud-converter-bindings-mdr-102)
  - [4. Layout & UI Controls](#4-layout-ui-controls)
- [Testing Decisions](#testing-decisions)
  - [1. Headless GUI & Integration Testing](#1-headless-gui-integration-testing)
  - [2. Module Test Coverage](#2-module-test-coverage)
- [Out of Scope](#out-of-scope)
- [Further Notes](#further-notes)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

# Product Requirement Document (PRD): Lottery Studio PySide6 Modern Cockpit

* **Status**: Proposed / Ready for Triage (`ready-for-agent`)
* **Date**: 2026-08-11
* **Authors**: Antigravity (AI Assistant) & USER
* **Tracker Label**: `ready-for-agent`

---

## Problem Statement

The Lottery Prediction Engine currently has over 80 advanced strategies and extensive filtering layers, but they are accessed primarily through a CLI or a basic terminal TUI. Quantitative users and lottery analysts lack a high-density, modern desktop graphical cockpit to interactively select active number pools, inspect mathematical statistics (like skips) visually, manage historical draws, execute predictions/verifications, and configure multi-layered filters. The legacy **Standard Lottery Studio** provides a robust feature footprint, but its Windows XP-era styling, flat-file architecture, and lack of integration with our advanced predictive engine prevent it from serving as a modern analytical workspace.

---

## Solution

Build a modern PySide6 desktop cockpit that wraps our core Python lottery engine in-process. The cockpit will implement the complete feature set of Standard Lottery Studio, running directly on our DuckDB database (`data/lottery.db`), but styled with a premium dark-themed aesthetic. It features a split-pane central workspace: a **Pool Builder** (interactive number grid to toggle active pools) on the left, a **Ticket Store** (editable table of generated lines with sort/dedupe/export tools) on the right, and a tabbed **Setup Dock** at the bottom (base/advanced filters, logical N-of-M conditions, and automatic parameter generator). Long-running calculations (ensemble forecasts, verifications) are delegated to background worker threads using `QThread` and custom signal channels to keep the GUI fluid and responsive.

---

## User Stories

### A. Drawings & Game Management
1. As a lottery analyst, I want to select a game context from a dropdown, so that the active rules, pool size, and ticket store update instantly.
2. As a lottery analyst, I want to create a new custom game context by specifying its pick size, pool max, and optional bonus pool parameters, so that I can analyze non-standard games.
3. As a lottery analyst, I want to view historical drawings in a clean tabular grid, so that I can easily verify drawing dates and winning numbers.
4. As a lottery analyst, I want to add new draws manually via a dedicated dialog, so that I can keep the database up-to-date.
5. As a lottery analyst, I want to insert a draw at a specific historical position, so that I can correct missed entries in past drawings.
6. As a lottery analyst, I want to modify any cell in the drawings grid inline, so that I can correct data-entry mistakes quickly.
7. As a lottery analyst, I want to delete a draw from the history, so that I can remove corrupted or test draws.
8. As a lottery analyst, I want to import drawings from a flat space-delimited `.txt` file, so that I can reuse my existing Lottery Studio draw files.
9. As a lottery analyst, I want to export drawings from the DuckDB database back to a flat Lottery Studio-compatible `.txt` file, so that I can share data with legacy systems.
10. As a lottery analyst, I want to split drawings by specific weekdays, so that I can run analyses restricted to particular draw cycles (e.g. only Saturday draws).
11. As a lottery analyst, I want to update drawings online with a single click, so that I don't have to input latest results manually.

### B. Statistical Analysis
12. As a quant, I want to open a tabbed statistics workspace, so that I can review historical metrics across all 18 standard mathematical categories.
13. As a quant, I want to configure the draw range (e.g. last 50, 100 draws) for any statistical chart, so that I can analyze short-term recency bias vs. long-term frequency.
14. As a quant, I want to click any column header in a statistics table, so that the grid drills down and displays the Actual, Average, and Now skips for that number.
15. As a quant, I want to view a drawings distribution trend chart, so that I can visually identify number clusters and skips.
16. As a quant, I want to run co-occurrence analysis on pairs and triples of numbers, so that I can find numbers that frequently hit together.

### C. Ticket Generation
17. As a player, I want to generate tickets randomly, so that I can quickly buy quick-pick lines.
18. As a player, I want to generate "smart" tickets, so that the generator uses analysis-depth weights (such as hot/cold frequency) to bias the random selection.
19. As a player, I want to use positional generation, so that I can fix specific number sets for position 1, position 2, etc.
20. As a player, I want to generate a full combinatorial wheel of my chosen pool, so that I can play all possible tickets from my selected numbers.
21. As a player, I want to select a wheeling formula (Guarantee wheel), so that I can generate abbreviated lines that mathematically guarantee a prize if my pool contains the winners.
22. As a player, I want to quick-pick numbers (hot, cold, or last-N) into my active pool, so that I don't have to click them individually.
23. As a player, I want to save and load my favorite numbers, so that I can quickly reload my personal combinations.

### D. Filtering
24. As a player, I want to select from 50 base filters, so that I can prune bad tickets (e.g. sum-range, odd-even ratio).
25. As a player, I want to configure up to 18 advanced filters, so that I can apply complex multi-condition logic to my tickets.
26. As a player, I want to click "Generate Default Condition", so that the system automatically calculates the minimum/maximum bounds for all active filters based on recent history.
27. As a player, I want to open a filter assistant window, so that I can view frequency and trend charts to set filter thresholds visually.
28. As a player, I want to set a logical condition (AND, OR, or N-of-M fault-tolerant logic), so that my generated tickets don't get overly restricted by single volatile filters.
29. As a player, I want to view a filtering report after running a filter pass, so that I can see exactly how many lines were eliminated by each filter.
30. As a player, I want to save and load my filter configuration sets, so that I can reuse my custom filter criteria across games.

### E. Prediction & Verification
31. As a quant, I want to select a prediction formula (Formula 1-6) and set its algorithm, offset, and depth parameters, so that I can forecast the next draw.
32. As a quant, I want to click "Predict Now", so that the engine generates recommended numbers and automatically updates the active Pool Builder.
33. As a quant, I want to run verification on a prediction formula, so that I can replay it over history and view its out-of-sample hit-rate.
34. As a quant, I want to view a leaderboard of prediction formulas, so that I can select the most accurate formula for the active game.

### F. Ticket Store Workspace
35. As a player, I want to view all generated tickets in a main grid, so that I can inspect my lines.
36. As a player, I want to sort my ticket lines low-to-high, so that they are easy to read.
37. As a player, I want to remove duplicate lines with a single click, so that I don't waste money buying the same ticket twice.
38. As a player, I want to tag specific ticket lines and delete them by tag, so that I can clean up my ticket store.
39. As a player, I want to search past drawings for my ticket combinations, so that I can see how often they would have won in the past.
40. As a player, I want to run optimization reductions on my tickets, so that I can reduce the total ticket cost while maintaining coverage.
41. As a player, I want to run "Check Winning" against a specific draw, so that I can see how many matches my tickets achieved (bonus-ball aware).
42. As a player, I want to print my ticket lines to paper or export them to TXT/XLS/HTML formats, so that I can take them to a physical lottery terminal.

---

## Implementation Decisions

### 1. Architectural Integration
- **Direct In-Process Imports**: The PySide6 GUI imports modules directly from `engine.*` in-process. It does not run a decoupled sidecar or invoke CLI wrappers, preventing IPC latency and reducing code redundancy.
- **Database Engine**: DuckDB is the single source of truth for drawings persistence (`data/lottery.db`). Flat `.txt` file parsing and exporting are handled inside helper utilities, keeping database read/writes relational and fast.

### 2. Concurrency & Concurrency Model (MDR-101)
- **QThread Workers**: Heavy computations (forecast suggestions, backtests, filter audits, formula verifications) are subclassed as `QThread` workers (e.g., `ForecastJob`).
- **Thread Manager**: A central `ThreadManager` class schedules background threads, prevents duplicate executions, handles user-initiated cancellation requests cooperatives via `isInterruptionRequested()`, and automatically releases memory via `.deleteLater()` when threads finish.
- **Thread-Safe Signals**: Communications across threads use a typed `JobSignals(QObject)` object carrying:
  - `progress(int, str)`: percentage and step status.
  - `new_log(str, str)`: logs routed to the UI console.
  - `finished(dict)`: final result payload.
  - `failed(str, str, str)`: error window triggers.
- **GUI Thread Affinity Safeties**: Worker threads are strictly forbidden from spawning widgets or QMessageBox objects directly. Exceptions are captured, converted to traceback strings, emitted via the `failed` signal, and displayed by the Main GUI thread.

### 3. Database CRUD & Converter bindings (MDR-102)
- **Editable Table Model**: Grid views for drawings bind to `DuckDBDrawsTableModel` (derived from `QAbstractTableModel`). Inline modifications are written back to DuckDB via `storage.save_draws()` and emit `data_mutated` signals.
- **Lottery Studio Converter**: Bidirectional conversion scripts are in place:
  - `parse_Lottery Studio_txt` reads files, matching implicit draw IDs with line numbers, and parsing date formats (`M/D/YYYY` or `MM/DD/YYYY`).
  - `export_duckdb_to_Lottery Studio` queries DuckDB, sorts ascending by draw ID, formats dates back, and writes file with CRLF line endings.

### 4. Layout & UI Controls
- **Split-Panel Layout**: Uses `QSplitter` to partition the **Pool Builder** (Left Rail) and the **Ticket Store** (Right Rail) dynamically.
- **Interactive Number Grid**: Generates button layouts dynamically matching the pool size ($1..M$). Clicking toggles numbers to selected (red). Active ranges and column sizes adapt to selected game rules.
- **Setup Dock**: A bottom layout containing tabbed widgets for:
  - **Base Filters**: A checklist of filters with inline range parameters and `…` edit slots.
  - **Advanced Filters**: A list view supporting item additions/replacements/deletions.
  - **Logical Conditions**: Radio buttons for AND/OR and spinboxes for N-of-M ranges.
- **QSS Style Sheets**: A centralized `ThemeManager` loads and applies custom QSS stylesheets for a sleek dark mode theme featuring high-contrast text and neon green/cyan/red highlight elements.

---

## Testing Decisions

### 1. Headless GUI & Integration Testing
- We will test the external behavior of widgets and models rather than implementation details.
- We will utilize `pytest` combined with the `qapp` session-wide fixture and `qtbot` (from `pytest-qt`) to test GUI interactions headlessly.
- Prior art: `tests/test_desktop_integrity.py` and `tests/test_desktop_logic.py`.

### 2. Module Test Coverage
- **`DuckDBDrawsTableModel`**: Test inline updates via `setData()`, verify CRUD modifications write successfully to a temporary DuckDB instance, and assert that the `data_mutated` signal is emitted.
- **Import/Export Converters**: Test importing and exporting Lottery Studio `.txt` files, asserting that draw counts, date formats, and number values are preserved exactly.
- **Concurrency Workers**: Spin up `ForecastJob`, mock worker executions, monitor signal emissions, check that progress values scale properly, and assert that trapped exceptions trigger `failed` signals containing correct error messages.
- **Global Context Propagation**: Verify that changing the global lottery ID in `DatabaseTab` triggers slot handlers that successfully update rules, number pools, and active lists across all tabs.

---

## Out of Scope

- Direct execution, decompilation, or linking of the `studio_app.bin` assembly binaries.
- Running the GUI as a web application or exposing it over a remote gateway (remains local-only).
- Features locked behind Lottery Studio Full Edition that are not present in the Free Edition (unlimited abbreviated wheels, custom filter scripting engines, multi-game concurrent windows).

---

## Further Notes

- **Usability Preference**: The "Generate Default Condition" range calculator is a massive convenience feature for users and should be prioritized for development once the basic filter layouts are styled.
- **Registry Alignment**: All custom game profiles created in the UI drawings manager should sync back to `data/registry.yaml`.

---

## Clean-Room Python Boilerplate

```python
def compute_ac_value(ticket: list[int]) -> int:
    """
    Arithmetic Complexity (AC):
    AC = #{distinct positive pairwise differences} - (k - 1)
    """
    k = len(ticket)
    diffs = {abs(a - b) for i, a in enumerate(ticket) for b in ticket[i + 1 :]}
    return len(diffs) - (k - 1)
```

---
> **Next Steps**: [⬅️ Lottery Studio-qt-interface-map](lottery-studio-qt-interface-map.md) · [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [Pick 3 Tic-Tac-Toe Generator  Free Lottery Software ➡️](pick-3-tic-tac-toe-generator-free-lottery-software.md)
