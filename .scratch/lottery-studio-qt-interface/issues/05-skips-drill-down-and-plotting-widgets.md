# 05 — Skips Drill-down & Plotting Widgets

**What to build:** A custom skips inspector widget displaying Actual, Average, and Now skips, integrated with the Statistics tab. Clicking any number row inside a stats table automatically recalculates skips and updates a real-time bar chart of historical skips sequences using Matplotlib.

**Blocked by:** 04 — Sleek Dark Mode QSS & Main Layout Restructuring

**Status:** ready-for-human

- [x] A custom `SkipsInspector` widget is implemented to show skips values and actual sequence intervals.
- [x] Matplotlib is integrated into the workspace and styled to match the dark theme (transparent grids, neon labels) per MDR-104.
- [x] A row selection slot is added to statistics tables in `AnalysisTab`. Clicking a row emits the target number.
- [x] The skips calculator queries DuckDB draws, computes the actual skip spacing sequence, average skip length, and current now-skip.
- [x] The skips grid values update with calculated metrics.
- [x] The skips chart canvas is cleared and redrawn with a bar chart of actual skips sequences, with hover tooltips displaying the draw ID of each hit.

*Note: Per accepted architecture decision [MDR-104](../docs/wayfinder/decisions/104-interactive-skips-chart-decision.md), Matplotlib was used as the single plotting library for all cockpit charts to avoid unnecessary package dependencies and support all necessary chart formats, bypassing the initial pyqtgraph suggestion.*
