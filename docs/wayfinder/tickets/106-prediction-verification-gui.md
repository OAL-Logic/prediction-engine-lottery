---
id: "106"
type: grilling
status: closed
blocked_by: []
map: samlotto-qt-interface-map.md
created: 2026-08-11
---

# Prediction verification GUI

## Question

How should we design the PySide6 Predict Center and Verification Desk tabs to run Formula-1..6 algorithms, display prediction history/accuracy leaderboards, and seamlessly push recommended numbers into the active Pool Builder?

## Context

- The SamLotto prediction engine uses six formulas (`Formula-1` ... `Formula-6`), adjustable offsets, and evaluation depths to recommend a pool of numbers (~17-27 numbers) for the next draw.
- The `Verification` desk replays a formula over a selected historical draw range (e.g., last 20 draws) and tracks the hit-rate of recommended numbers versus actual results.
- When a prediction is made, the recommended numbers must be sent back to the main window's `NumberGrid` to serve as the active pool.
- This ticket is blocked by:
  - [#101](101-qt-app-bootstrap-and-threading.md) (running prediction calculations and history verifications asynchronously).
  - [#102](102-drawings-and-registry-manager.md) (querying draw history from DuckDB).

## What to decide

1. **Prediction Inputs Layout**:
   - Design the Predict tab layout: formula dropdown, algorithm select, offset spinbox, depth selector, and the prominent "Predict Now" button.
2. **Verification Leaderboard Grid**:
   - Design the leaderboard layout inside the Verification tab. It should show a table comparing formulas, their parameters, average hit-rates, and precision. Include controls to select the validation range (e.g., "Verification depth: 50 draws").
3. **Inter-Tab "Push to Pool" Flow**:
   - Specify the mechanism for pushing recommended numbers to the `NumberGrid` (left rail). Detail the Qt signals used, how they toggle numbers to active/selected (red), and how the UI transitions focus back to the Pool Builder workspace.
4. **Drawings Trend Predictor**:
   - Replicate the "Drawings Trend" manual predictor (E5), detailing how trend visualizers inside the stats tabs let users manually check or uncheck numbers based on visual frequency charts.

## Acceptance criteria

- [ ] A design layout for the Prediction and Verification views is documented.
- [ ] The signal-slot signature and handler code stubs for sharing recommended numbers with the `NumberGrid` are provided.
- [ ] A plan for displaying verification accuracy tables is outlined.
- [ ] Output is a markdown design spec linked from this ticket.
