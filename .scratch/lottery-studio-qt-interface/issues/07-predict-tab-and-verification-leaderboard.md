# 07 — Predict Tab & Verification Leaderboard

**What to build:** A Prediction and Verification dashboard containing parameters for Formula-1..6 forecasting, an asynchronous verifier that runs backtests and ranks formulas inside a sorted leaderboard table, and a "Push to Pool" button that updates the main NumberGrid pool selection.

**Blocked by:** 01 — QThread Concurrency Integration (ProphetJob), 02 — DuckDB Editable Model & CRUD Drawings UI, 04 — Sleek Dark Mode QSS & Main Layout Restructuring

**Status:** ready-for-agent

- [ ] The `PredictionTab` is designed with controls for formula, algorithm, offset, depth, and a "Predict Now" execution button.
- [ ] Running a prediction spawns a background thread that calculates recommended numbers for the next draw and outputs them to the results panel.
- [ ] A "Push to Pool" button is implemented. Clicking it fires a Qt signal, which updates the main `NumberGrid` pool state (coloring the recommended numbers red) and activates the first tab.
- [ ] The `VerificationTab` is implemented with a database verifier worker thread that runs backtests on selected formulas.
- [ ] The verifier returns average hit-rates and net profit/ROI statistics, populating a sorted leaderboard grid to highlight the most accurate formula configurations.
