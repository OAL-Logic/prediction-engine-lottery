# 07 — Predict Tab & Verification Leaderboard

**What to build:** A Prediction and Verification dashboard containing parameters for Formula-1..6 forecasting, an asynchronous verifier that runs backtests and ranks formulas inside a sorted leaderboard table, and a "Push to Pool" button that updates the main NumberGrid pool selection.

**Blocked by:** 01 — QThread Concurrency Integration (ProphetJob), 02 — DuckDB Editable Model & CRUD Drawings UI, 04 — Sleek Dark Mode QSS & Main Layout Restructuring

**Status:** resolved

- [x] The `PredictionTab` is designed with controls for formula, algorithm, offset, depth, and a "Predict Now" execution button.
- [x] Running a prediction spawns a background thread that calculates recommended numbers for the next draw and outputs them to the results panel.
- [x] A "Push to Pool" button is implemented. Clicking it fires a Qt signal, which updates the main `NumberGrid` pool state (coloring the recommended numbers red) and activates the first tab.
- [x] The `VerificationTab` is implemented with a database verifier worker thread that runs backtests on selected formulas.
- [x] The verifier returns average hit-rates and net profit/ROI statistics, populating a sorted leaderboard grid to highlight the most accurate formula configurations.

## Comments

### Resolution Summary
1. **Prediction Center Controls**: Verified `PredictionTab` in [`desktop/src/tabs/predict.py`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/PRJ%20Prediction%20Engine/lottery/desktop/src/tabs/predict.py) with dynamic strategy presets dropdowns (Formula family -> Algorithm drill-down matching SamLotto Formula-1..6 logic), history depth (`depth_spin`), draw offset (`offset_spin`), and execution button.
2. **Background Concurrency (ForecastJob)**: Implemented in [`desktop/src/telemetry/manager.py`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/PRJ%20Prediction%20Engine/lottery/desktop/src/telemetry/manager.py) via `ForecastJob(QThread)`. Runs asynchronous multi-strategy predictions off the UI thread and streams live logs and progress percentages to the cockpit.
3. **Push to Pool Signal**: Implemented `numbers_recommended = Signal(list)` on `PredictionTab`. Wired up in `ProphetDashboard.handle_push_to_pool` to load numbers into `NumberGrid.select_numbers()`, highlight them in active neon red, and switch views to the workspace.
4. **Formula Verification Desk & Leaderboard**: Implemented `FormulaVerificationJob` wrapping `run_backtest()` for walk-forward historical simulation. Renders results on `VerificationTab` with columns `["Formula", "Draws Tested", "Win Rate %", "Capture %", "Best Hit", "Avg Rank"]`.
5. **Validation Testing**: Verified integrity through unit tests `test_prediction_tab_formula_algorithm_drilldown`, `test_prophet_dashboard_push_to_pool_wiring`, and `test_formula_verification_job_runs`.
