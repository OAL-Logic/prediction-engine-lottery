---
id: "109"
type: task
status: closed
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-09-16
---

# Drawings Trend manual predictor (E5)

## Question

From #106's closure note and the map's "Not yet specified" section: replicate Lottery Studio's "Drawings Trend" manual predictor (E5) — "a manual visual-frequency-chart number checker inside the stats tabs" that lets users manually check/uncheck numbers based on what they see in the chart, distinct from Predict Center's *algorithmic* Formula/Algorithm push-to-pool (#106).

## Resolution

Added a "Drawings Trend — Manual Number Checker" panel to the bottom of `AnalysisTab` (`desktop/src/tabs/analysis.py`), below the existing chart/table/summary split (which already serves as "the visual frequency chart" across all 11 views from #107 — Frequency Distribution, Actual Skips, etc.). Reused the existing `NumberGrid` widget (`desktop/src/widgets/number_grid.py`) wholesale rather than building a new toggle-grid — it already has everything needed (`set_range`, `selected_numbers`, `clear_selection`). The workflow: eyeball whichever view is on screen, manually click numbers in the grid underneath, then "→ PUSH CHECKED NUMBERS TO POOL".

`AnalysisTab` gained a `numbers_recommended = Signal(list)`, named and shaped identically to `PredictionTab`'s signal of the same name, so `ProphetDashboard` (`desktop/src/main.py`) wires it to the exact same `handle_push_to_pool()` slot — no new handler needed, no logic duplicated. The grid's number range resyncs on `set_lottery()` the same way `PredictionTab`/`WheelingTab`/`DatabaseTab` already do.

This is deliberately *not* wired to any specific view's chart data (e.g. auto-highlighting hot balls) — the point of E5 in Lottery Studio, and the reason it's a separate feature from #106's algorithmic predictor, is that the selection is manual and opinion-driven, not computed.

**Verified:** `test_analysis_tab_drawings_trend_manual_checker` (`tests/test_desktop_logic.py`) checks the emit-on-push, warn-instead-of-emit-when-empty, and range-resync-on-game-switch paths. Full `test_desktop_integrity.py` (builds `ProphetDashboard` itself) still passes (11/11).

## Not done here (still fog)

- **Custom export formats** — the only remaining item on the map's fog list.
