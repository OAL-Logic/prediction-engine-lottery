# Feature Batch 8 — Continuous Improvement & Dashboard V3
**Date:** 2026-04-28  
**Status:** Shipped  

## Overview
This batch focused on system-wide robustness, API standardization, and enhancing the visual intelligence of the terminal dashboard. It bridges the gap between the core statistical engine and high-fidelity user insights.

## New Features & Enhancements

### 1. Automated Insights Ribbon (Dashboard V3)
Developed a new `engine/modules/insights.py` module that synthesizes raw data into actionable intelligence. The `lottery dashboard` command now features a top-level "Insight Ribbon" that automatically flags:
*   **Regime Changes:** Statistical fairness alerts based on Chi-squared p-values.
*   **Hotspots:** Significant over-performers (Z-Score > 2.0).
*   **Anomaly Detection:** Records broken (All-Time High delays).
*   **Cyclical Trends:** Cycle progress and missing number warnings.
*   **Environmental Jitter:** Real-time Noosphere entropy levels.

### 2. Standardized Strategy API
Performed a massive refactor of the `suggest()` method across **28+ strategy files**. 
*   Adopted the `*args, **kwargs` pattern for all strategy overrides.
*   Ensured consistent parameter passing (seed, pick, pool, key, filters) through ensembles and master cylinders.
*   Fixed multiple `TypeError` and `NameError` bugs in the `portfolio` and `compare` commands.

### 3. Surgical Strategy Instantiation
Enhanced `get_strategy` in `engine/strategies/__init__.py` with `inspect`-based parameter filtering.
*   Automatically detects which arguments a strategy's `__init__` accepts.
*   Prevents crashes when passing personal data (name, birth date) to statistical strategies that don't need them.
*   Gracefully handles classes using the default `object.__init__`.

### 4. Global Registry Enrichment
Updated `DrawRules` and `GameDefinition` to support visual board configuration.
*   Added `board_cols` parameter to the registry.
*   Configured Lotofácil as 5-column (5x5) and Mega-Sena/Powerball as 10-column layouts.
*   Centralized visual metadata used by mapping and dashboard commands.

### 5. Environment & Dependency Hardening
*   Created a managed virtual environment (`.venv`) for isolated development.
*   Added missing `PyYAML` dependency to `pyproject.toml`.
*   Verified the `[all]` dependency group installation (Statistical + ML + Deep Learning).

## Bug Fixes
*   Fixed `AttributeError` when calling `.tolist()` on native Python lists in the strategy engine.
*   Fixed `NameError` in `lottery portfolio` due to missing strategy registrations.
*   Fixed `AttributeError` in `insights` module caused by a function name mismatch (`get_pattern_string`).
*   Resolved multiple test failures in `test_kabbalistic.py` and `test_docs_up_to_date.py`.

## Verification Results
Every registered CLI command was smoke-tested across multiple variations (Mega-Sena, Lotofácil, Powerball) within the new `.venv`. The engine is now robust and ready for the Sidecar (FastAPI) implementation.
