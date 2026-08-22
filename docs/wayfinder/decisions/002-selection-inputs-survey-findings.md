# Selection Inputs Survey Findings

* **Date**: 2026-08-11
* **Author**: Antigravity (AI Assistant)
* **Status**: Complete
* **Subsystem Surveyed**: Calibration, Pruning, Tuning, Forecast Diagnostics, and Strategy Registry.

---

## 1. Candidate Input Signals Comparison

The following table evaluates the available signals in the prediction engine that can potentially feed the strategy selection decision layer:

| Signal Source | Primary Metrics | Game-Specific? | Storage Format & Location | Computational Cost | Historical Depth |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`lottery calibrate`** | Out-of-sample lift, net profit, ROI, precision | **Yes** | JSON (`data/calibration_cache.json`) | **High** (Runs backtest predictions across $N$ past draws) | Snapshot only (overwrites previous runs for that game) |
| **`lottery prune`** | Lift over random, average ranks, best match | **Yes** | None (stdout console only; logs to Markdown on demand) | **Medium-High** (Runs single-ticket backtests over $N$ draws) | No history (not persisted programmatically) |
| **`lottery tune`** | Optimal parameter configurations, stacking weights | **Yes** | YAML (`tuned/<game_id_flat>.yaml`) | **Very High** (Runs grid search over parameter/filter spaces) | Snapshot of best parameters, no history |
| **`lottery forecast`** | Stability% (rolling window variance), Discrimination $\Delta$ (lift vs. random data) | **Yes** | JSONL (`data/ticket_log.jsonl` logs final tickets, metrics are runtime-only) | **Medium** (Runs stability and shuffle stress tests at runtime) | Snapshot (diagnostics evaluated on current frame only) |
| **Runtime Tier** | Expected CPU/GPU/Network cost per strategy | **No** (Implicit to strategy definition) | Implicit (Derived from tier field in `STRATEGY_REGISTRY`) | **None** (Read from metadata) | Constant |

---

## 2. MVP Input Signal Recommendation

For the initial strategy selector design (`lottery select-strategies`), we recommend using a **dual-signal input model**:

1. **Primary Signal: Out-of-Sample Calibration Lift**
   - **Rationale**: Calibration lift (actual wins / baseline random wins) is the most direct, empirically validated metric of a strategy's success. Unlike forecast-time diagnostics (which measure statistical shape), calibration tests how often the strategy's predictions actually matched historical draws. It is already programmatically saved in `data/calibration_cache.json`, making it trivially accessible.
2. **Secondary Signal: Strategy Registry Tier (Static Metadata)**
   - **Rationale**: Restricting strategies by tier (statistical, ML, deep, fun) protects against extreme latency spikes (e.g. running multiple deep models on a machine without PyTorch/GPU) and excludes high-noise categories (esoteric/fun models) by default while keeping them selectable.

---

## 3. Gaps to Close Before Policy Design

To build a robust pruning policy in `#003 Policy thresholds`, we must address the following gaps:

1. **No Pruning Metrics Cache**: `lottery prune` does not write its audit metrics or hibernation status to a structured file.
   - *Fix needed*: Modify `prune.py` or `pruning.py` to write results to `data/prune_cache.json` so the selector can read it, or import `run_pruning_audit()` directly into the selector.
2. **Calibration Cache Volatility**: `calibration_cache.json` only tracks the most recent run's lift. It doesn't capture whether a strategy's performance is decaying or improving over time (no historical trajectory).
   - *Fix needed*: Extend the calibration cache schema to keep a rolling list of the last $K$ calibrations, or rely on a larger backtest window during calibration.
3. **No Latency Metadata**: The `STRATEGY_REGISTRY` lists descriptions and modules but does not capture expected runtime cost or dependency rules (e.g., `requires_gpu=True`, `avg_latency=2.5s`).
   - *Fix needed*: Add optional latency indicators (`fast`, `medium`, `slow`) or hardware requirements to `STRATEGY_REGISTRY` to prevent running heavy deep learning models on low-end systems.
4. **Redundancy Matrix Persistence**: The Jaccard similarity matrix from `prune --redundancy` is printed to stdout but is not saved anywhere. It cannot be used to automatically demote redundant strategies.
   - *Fix needed*: If we want redundancy-aware pruning, the redundancy matrix must be stored in JSON format or calculated dynamically at selection time.
