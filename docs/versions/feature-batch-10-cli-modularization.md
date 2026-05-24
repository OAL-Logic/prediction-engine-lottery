# Feature Batch 10 — CLI Modularization & Strategy Hardening
**Date:** 2026-05-01  
**Status:** Shipped  

## Overview
This batch introduces a major architectural shift in the CLI layer and hardens the strategy engine against "time-travel" data anomalies discovered during backtesting.

## 1. CLI Modularization (ADR)
The monolithic 4,800+ line `engine/cli/main.py` has been refactored into a modular package structure. This improves maintainability, IDE performance, and team collaboration.

**Structure:**
- `engine/cli/main.py`: Lean entry point and command registration.
- `engine/cli/utils.py`: Shared UI components (tables, bar charts, formatting).
- `engine/cli/commands/`:
    - `fetch.py`: Data ingestion logic.
    - `analyze.py` & `dashboard.py`: Statistical visualization.
    - `suggest.py` & `portfolio.py`: Ticket generation and ensembles.
    - `backtest.py` & `wizard.py`: Evaluation and interactive flows.
    - `manage.py` & `management.py`: Administrative utilities.
    - `personal.py`: Personalized Kabbalistic/Biorhythm tools.
    - `check.py`: Structural auditing.

## 2. Strategy Hardening
Fixed several regressions that caused crashes when strategies were run against historical draws with missing metadata or `NaT` (Not a Time) values.

- **`moon_phase` / `weather` / `biorhythm`**: Added date resilience. If the engine performs a "blind" backtest on a draw with an unknown date, the strategies now fallback gracefully instead of crashing on date arithmetic.
- **`mutual_info`**: Fixed a critical `AttributeError` where the strategy attempted to call `.tolist()` on a native Python list.
- **`ensemble`**: Standardized parameter passing to ensure that custom seeds and personal context (name, birth date) flow correctly through multi-tier models.

## 3. Data Integration
Updated all adapters and the `fetch` command to support the new **DuckDB + Partitioned JSON** storage architecture. The CLI now provides clear visibility into where analytical data vs. human-readable inspections are stored.

## Verification Results
- **Modular CLI:** Verified all 15+ commands (`games`, `suggest`, `backtest`, `dashboard`, `wizard`, etc.) work seamlessly.
- **Backtest Stability:** Successfully ran a full-battery backtest (`all` strategies) against Mega-Sena Draw 3002 with 100% success rate.
- **Environment:** All changes verified within the `.venv` with `[all]` dependencies.
