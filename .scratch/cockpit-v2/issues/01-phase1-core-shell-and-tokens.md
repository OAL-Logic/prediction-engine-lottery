---
title: Issue 01 — Phase 1: Architecture Core, Design Tokens & Shell
status: claimed
labels:
  - ready-for-agent
  - phase-1
  - core-shell
---

# Issue 01: Phase 1 — Architecture Core, Design Tokens & Shell

## Scope
1. Scaffold clean greenfield tree `cockpit/src/` with `core/`, `theme/`, `services/`, `shell/`, `widgets/`, `perspectives/`.
2. Define domain models in `cockpit/src/core/models.py`.
3. Implement `ThemeManager` in `cockpit/src/theme/` strictly adhering to `pyqt6-ui-designer` (4px grid, dual themes, interactive states).
4. Implement `EngineBridge` in `cockpit/src/services/engine_bridge.py` for headless game discovery and draws.
5. Implement `BallMatrixWidget` (QPainter vector) and `TicketReceiptWidget` in `cockpit/src/widgets/`.
6. Implement `PerspectiveManager`, `DockingManager`, and `CockpitMainWindow` in `cockpit/src/shell/`.
7. Build `ExpressPerspectiveView` and initial `StudioPerspectiveView`.
8. Create clean standalone launcher `cockpit/src/app.py`.
9. Create and execute test suite `cockpit/tests/test_phase1.py`.
