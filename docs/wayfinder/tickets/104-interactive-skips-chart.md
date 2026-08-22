---
id: "104"
type: research
status: open
blocked_by: ["103"]
map: samlotto-qt-interface-map.md
created: 2026-08-11
---

# Interactive skips chart

## Question

Which plotting library (pyqtgraph, QChart, or Matplotlib) should be used to display statistical graphs, and how do we design the interactive skips drill-down (Actual, Average, and Now skips) widget to update in real-time?

## Context

- In the original SamLotto, clicking a column in the statistics grids triggers a drill-down skips analysis (Actual Skips sequence, Average Skip, Now Skip).
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

- [ ] A comparison of PySide6-compatible plotting libraries is documented.
- [ ] An interface layout showing the stats table and skips chart relationship is designed.
- [ ] Rationale for the chosen plotting library and its QSS integration is stated.
- [ ] Output is a markdown design spec linked from this ticket.
