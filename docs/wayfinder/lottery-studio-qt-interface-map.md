---
label: wayfinder:map
destination: PySide6 modern desktop interface matching SamLotto Free Edition features
status: active
created: 2026-08-11
---

# SamLotto Qt Modern Interface Map

## Destination

A modern PySide6 desktop application ("the cockpit") that implements every feature of the SamLotto Free Edition (drawings management, 18-method tabbed statistics with skips drill-down, smart ticket generation, 50 base + 18 advanced filters with N-of-M logical logic, and Formula 1-6 predictions). The app runs in-process via direct Python imports from the core engine, stores drawings primarily in `data/lottery.db` (DuckDB), supports importing/exporting SamLotto flat `.txt` files, and is styled with a custom dark-mode aesthetic.

See the full [Product Requirement Document (PRD)](decisions/samlotto-qt-interface-spec.md) for detailed requirements and specifications.

## Notes

- **Domain**: PySide6 GUI development, UI/UX design, custom QSS styling, QThread/worker concurrent execution, DuckDB integration, and interactive data visualization.
- **Skills to consult**: `codebase-design` for window/module boundaries, `prototype` for layout/styling mocks, and `bmad-grilling` for usability trade-offs.
- **Standing preferences**:
  - **Framework**: PySide6 (Official Qt for Python, LGPL).
  - **Backend integration**: Direct in-process imports of `engine.*` modules and DuckDB connections.
  - **Storage**: DuckDB-first (`data/lottery.db`). Flat `.txt` file support is for import/export only.
  - **Aesthetic**: Sleek Dark Mode (custom QSS, clean visual hierarchy, colorful plotting).
  - **Concurrency**: Heavy operations (forecasts, backtests, audits) must run asynchronously via QThreads to keep UI responsive.

## Decisions so far

<!-- Index of closed tickets. One line per ticket: gist + link. -->

- [#101 Qt app bootstrap and threading](tickets/101-qt-app-bootstrap-and-threading.md) — Asynchronous QThread worker model with custom JobSignals and main-thread QMessageBox error logging established.
- [#102 Drawings and registry manager](tickets/102-drawings-and-registry-manager.md) — Implemented DuckDB CRUD QAbstractTableModel and bidirectional parser stubs for SamLotto .txt compatibility.
- [#103 Sleek dark theme and layout](tickets/103-sleek-dark-theme-and-layout.md) — Unified split-pane cockpit layout designed and implemented in a runnable PySide6 prototype with custom QSS styling and responsive grids.
- [#104 Interactive skips chart](tickets/104-interactive-skips-chart.md) — Matplotlib (`FigureCanvasQTAgg`) kept as the single plotting library (zero new dependency, only one with a native heatmap); drill-down flows through a new `SkipsJob(QThread)` into a table+chart `SkipsInspectorPanel`.
- [#105 Filter setup panel](tickets/105-filter-setup-panel.md) — Implemented tabbed Setup Dock (FiltersTab) with inline range sliders, advanced filters add/remove panels, logical N-of-M condition checks, auto-calculating limits, and background pruning execution.
- [#106 Prediction verification GUI](tickets/106-prediction-verification-gui.md) — Implemented. SamLotto's fixed Formula-1..6 picker adapted to this engine's registry as a live Formula (STRATEGY_PRESETS family) -> Algorithm (specific strategy) drill-down in `PredictionTab`, plus Offset/Depth controls (`ForecastJob.offset`). "Push to Pool" is a real `numbers_recommended` Qt signal wired to `NumberGrid.select_numbers()`. `VerificationTab` gained a second "Formula Leaderboard" sub-tab (existing single-ticket auditor kept as-is) backed by a new `FormulaVerificationJob` — a thin QThread wrapper around the already-existing `engine.services.backtest.run_backtest()`, so no backtest logic was reimplemented. Drawings Trend manual predictor (E5) was not built — still fog, see below.
- [#107 High-density statistics tabs](tickets/107-high-density-statistics-tabs.md) — Implemented. `AnalysisTab` grew from 4 to 11 views (Odd/Even & High/Low Balance, AC Distribution, Root Sum, Decade Distribution, Consecutive Groups, Prime & Composite Balance, Unit Digit Analysis added), all reusing `engine.modules.filters` helpers rather than reimplementing metric math. Found and fixed a pre-existing `KeyError` bug in `harmony.py`'s `successive_2`/`_3`/`_4` filters along the way.
- **Online database updater (A11)** — already implemented prior to this map being last edited (`DatabaseTab.sync_online_draws()` / `FetchWorker` in `desktop/src/tabs/database.py`, wired to each adapter's `.fetch()`). Documenting here since the "Not yet specified" section below still listed it as fog; removing that entry.
- [#108 Ticket Store WRG reduction and real printing](tickets/108-ticket-store-wrg-reduction-and-print.md) — Implemented. `WheelingEngine.reduce_tickets()` (existed, zero callers) wired up as `TicketStoreReductionJob`, exposed via a Ticket Store toolbar button and context-menu action with a combinatorial-universe safety guard. `print_tickets()`'s fake "queued to spooler" stub replaced with a real `QPrinter`/`QPrintDialog`/`QTextDocument` flow.
- [#109 Drawings Trend manual predictor (E5)](tickets/109-drawings-trend-manual-checker.md) — Implemented. `AnalysisTab` gained a manual number-checker panel (reusing the existing `NumberGrid` widget as-is) below its chart/table, with its own `numbers_recommended` signal wired to the same `handle_push_to_pool()` slot `PredictionTab` uses — deliberately not tied to any view's computed data, since the point is a manual, opinion-driven pick distinct from #106's algorithmic predictor.
- [#110 Custom export formats](tickets/110-ticket-store-csv-export.md) — Implemented. `export_tickets()` gained a CSV filter (stdlib `csv` module, `Index,Numbers,Score` with header) alongside the existing `.txt` export.
- [#111 Closing the gap to "18-method tabbed statistics"](tickets/111-eighteen-method-statistics-parity.md) — Implemented. This map's own Destination text named "18-method" statistics; #107 shipped 11 without checking against the primary-source manual's actual 18-page Statistics menu. Reading it (not the secondary summaries #107 used) found 4 genuinely distinct missing metrics — Distance Analysis, Divisibility Analysis, Prior Drawing Repeat Analysis, Pair Co-occurrence Matrix — `AnalysisTab` now at 15/18 (the other 3 are menu umbrellas/near-duplicates by design). Also fixed a real bug found via testing: `NumberGrid.build_grid()`'s `(n - 1)`-based row/col math silently mis-placed ball `0` (and shifted every other ball) for `br/lotomania`, the one zero-indexed game.

- [#112 Filter Assistant Wizard](tickets/112-filter-assistant-wizard.md) — Implemented. GUI counterpart to `lottery filter-assistant` (detailed_features.md's "Assistant Filter"): a `QWizard` walking tiers 1-5's filter registry, ending in an elimination-funnel report via a new `FilterAssistantFunnelJob` that reuses `engine.cli.commands.filter_funnel`'s exact logic. Deliberately separate from FiltersTab (#105) — different SamLotto workflow, confirmed by the CLI already having two distinct commands for it. Cross-checked against the real CLI command's own output for identical inputs, not just "does it run."

- [#113 Save and Load Your Own Favorite Number](tickets/113-save-load-favorite-numbers.md) — Implemented. Two Pool Builder buttons in `ProphetDashboard` save/restore the active number selection to a small JSON file — distinct from #102's drawing-history .txt round-trip and #110's Ticket Store CSV/TXT export, neither of which covers the raw manually-picked pool.

- [#114 Position Number Tickets](tickets/114-position-number-tickets.md) — Implemented. New `PositionTicketsDialog`/`PositionTicketsJob`: independent candidate numbers per ticket position, Cartesian product filtered to distinct-numbers-only and deduplicated, with a combinatorial safety cap. Launched from `WheelingTab` but re-emits through its own existing `tickets_generated` signal rather than adding a second `main.py` wiring path.

- [#115 Random Select Numbers + Last-X-Drawings quick pick](tickets/115-random-and-last-drawn-quick-picks.md) — Implemented. New "🎲 RANDOM" quick-select button and "Pick Last-X-Drawings Numbers..." menu entry, filling the last two named quick-pick actions from the manual's Quick Select pages that weren't yet covered by the existing HOT/COLD/CLEAR/ALL/Odd/Even/Prime set. Also fixed a stale test (`sync_theme_colors` → `apply_theme`) left over from a concurrent session's clean rename.

## Tickets (frontier)

None open — #105-#115 are closed.

## Tickets (blocked)

<!-- No blocked tickets remaining -->

## Not yet specified

No open fog — #101-#115 closed every item this map had queued. New gaps get a fresh ticket when they surface.

## Out of scope

- Direct binary integration or linking with `samlotto.exe`.
- Running GUI code as a separate web client (Electron/browser).
- Pro-edition features that exceed the Free Edition capability checklist (unlocked wheels, unlimited numbers, custom script filters).
