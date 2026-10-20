---
id: "105"
type: prototype
status: closed
assignee: claude
blocked_by: ["103"]
map: lottery-studio-qt-interface-map.md
created: 2026-08-11
---

# Filter setup panel

## Question

How should we lay out the 50 base and 18 advanced filters within a compact, high-density PySide6 Setup Dock, and how do we design the N-of-M logical condition controls and the "Generate Default Condition" automation?

## Context

- In Lottery Studio, filters are configured in the bottom Setup panel.
- Base filters are listed in `S03` with checkboxes, range columns, and a `…` button for editing lists.
- Advanced filters are configured in `S04` where filters can be added, replaced, or deleted.
- The "Logical Condition" tab (`S05`) lets users combine active filters using AND, OR, or fault-tolerant N-of-M logic (e.g. "let the ticket pass if between 3 and 5 of the selected filters are satisfied").
- The "Generate Default Condition" button is highly load-bearing: it scans recent historical drawings (e.g. last 30, 50, 100 draws) to calculate the minimum/maximum bounds for each filter and auto-fills them.
- This ticket is blocked by:
  - [#101](101-qt-app-bootstrap-and-threading.md) (running audit/filter loops asynchronously).
  - [#102](102-drawings-and-registry-manager.md) (fetching historical draws to calculate auto-conditions).
  - [#103](103-sleek-dark-theme-and-layout.md) (styling inputs, grids, and checkboxes).

## What to decide

1. **High-Density Filter Grid Layout**:
   - Design a layout that fits 50 base filters without requiring excessive scrolling. Evaluate a multi-column list, a category tree view (e.g., Sum Filters, Digit Filters, Adjacency Filters), or a search-filtered panel.
2. **Value Parameter Editor**:
   - Design the editor for setting filter ranges and values. Recommend when to use range sliders (e.g., Sum between 100 and 150) vs. multiline text editors (for sets of numbers, like Odd-Even positions).
3. **N-of-M Logical Selector UI**:
   - Design a clean widget for logical conditions: radio buttons for AND/OR, and a numeric spinbox/combobox range selector for "N-of-M" (e.g., "Pass if [ 3 ] to [ 5 ] filters match").
4. **"Generate Default Condition" Flow**:
   - Specify how the UI triggers range auto-generation. Define the parameters (range selection, like "Last 30 Draws"), the SQL/Python logic that computes bounds, and how the resulting values populate the filter rows in the GUI.

## Acceptance criteria

- [ ] A layout structure for the base and advanced filter dock is designed.
- [ ] UI specifications for range sliders, list editors, and the N-of-M widget are documented.
- [ ] A clear sequence showing how "Generate Default Condition" queries the DB and populates parameters is documented.
- [ ] Output is a markdown design spec linked from this ticket.
