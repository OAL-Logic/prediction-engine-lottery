# 06 — Logic Conditions & Category-Filtered Base/Advanced Filters

**What to build:** A bottom Setup Dock containing tabs for Base Filters (checklist layout), Advanced Filters (list view), and Logical Conditions (AND/OR/N-of-M radios), combined with a "Generate Default Condition" range calculator that updates filter bounds from database history in a background thread.

**Blocked by:** 02 — DuckDB Editable Model & CRUD Drawings UI, 04 — Sleek Dark Mode QSS & Main Layout Restructuring

**Status:** ready-for-human

- [x] A tabbed `FilterSetupDock` is created, replacing the placeholder filters tab.
- [x] Base filters are classified into categories (e.g. Sum, Position, Digit) and displayed in a compact tree checklist with inline range sliders.
- [x] The Logical Conditions tab is implemented with radio buttons for AND/OR, and a numeric spinbox picker for N-of-M range logic.
- [x] A "Generate Default Condition" button is added. Clicking it launches a background worker thread that queries historical draws, calculates boundary limits for active filters, and updates the QSS-styled sliders.
- [x] The "Start Filtering" execution button runs selected filters against the ticket store in a background thread and triggers `TfilterrepForm` (the filter cuts report dialog) to display elimination counts.
