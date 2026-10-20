---
id: "104"
type: research
status: closed
assignee: claude
blocked_by: ["103"]
map: lottery-studio-qt-interface-map.md
created: 2026-08-11
---

# Interactive skips chart

## Question

Which plotting library (pyqtgraph, QChart, or Matplotlib) should be used to display statistical graphs, and how do we design the interactive skips drill-down (Actual, Average, and Now skips) widget to update in real-time?

## Context

- In the original Lottery Studio, clicking a column in the statistics grids triggers a drill-down skips analysis (Actual Skips sequence, Average Skip, Now Skip).
- The app also displays Drawings Distributing (trend chart) and filter assistants with frequency charts.
- The charts must load instantly, fit the dark mode QSS theme (colors, gridlines, fonts), and handle dynamic updates when the user switches game context or changes the draw history window.
- This ticket is blocked by:
  - [#101](101-qt-app-bootstrap-and-threading.md) for how the data-fetching worker threads pass calculation arrays back to the main thread.
  - [#103](103-sleek-dark-theme-and-layout.md) for the QSS stylesheet and color palette.

## What to research

1. **Plotting Library Evaluation**:
   - Compare `pyqtgraph` (very fast, natively styled, slightly steeper API) vs `QChart` (part of PySide6, clean, sometimes slower) vs `Matplotlib` (highly feature-rich, slower rendering, requires canvas wrapping).
   - Recommend the best fit for our dark-mode aesthetic and real-time responsiveness.
2. **Skips Drill-down Interactive Flow**:
   - Design the user interaction: when the user clicks a number in a stats grid, how is the skips data calculated by the engine and displayed?
   - Define the layout of the skips inspector (e.g. left side holds a table of skips values, right side shows a bar chart of actual skip sequences).
3. **Chart Styling Specifications**:
   - Define custom QSS and plotting properties (grid opacity, line widths, point hover tooltips, neon colors) for the selected library.

## Acceptance criteria

- [x] A comparison of PySide6-compatible plotting libraries is documented.
- [x] An interface layout showing the stats table and skips chart relationship is designed.
- [x] Rationale for the chosen plotting library and its QSS integration is stated.
- [x] Output is a markdown design spec linked from this ticket.

## Resolution

Resolved on 2026-08-22. See [MDR-104: Interactive Skips Chart — Plotting Library & Drill-down Design](../decisions/104-interactive-skips-chart-decision.md) for full comparison and details.

### Key Decisions
- **Plotting library: Matplotlib (`FigureCanvasQTAgg`/`QtAgg`)**, kept as the single library for all cockpit charts. Zero new dependency (already required), covers all four existing `analysis.py` chart types including the heatmap (which `QtCharts` cannot do natively), and its discrete-update cadence (once per game-context/history-window change) makes pyqtgraph's streaming-performance advantage irrelevant. `pyqtgraph` was rejected mainly for lacking a native per-bar click signal on `BarGraphItem`; `QtCharts` was rejected mainly for no heatmap chart type and more verbose pixel-exact token styling.
- **Skips drill-down flow**: `QHeaderView.sectionClicked` on a stats table → `ThreadManager.start_job` → a new `SkipsJob(QThread)` calling a proposed vectorized `engine/modules/skips.py::compute_skip_profile()` → `JobSignals.finished(dict)` → a main-thread `SkipsInspectorPanel` (left: `QTableWidget` skip ledger; right: Matplotlib bar/line chart of the actual skip sequence), styled with `rcParams`/`Figure(facecolor=...)`/`Axes.set_facecolor()` against the MDR-103 Sleek Dark Mode tokens.
