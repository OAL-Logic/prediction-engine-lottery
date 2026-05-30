# Changelog

All notable changes to the Lottery Engine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [11.2.0] - 2026-05-29

### Added
- **6 new API endpoints** closing Sprint 2 planned gaps:
  - `GET /health` — Service health check with uptime, version, resource counts
  - `GET /games/{name}/sum-distribution` — Sum probability PMF with 70% range
  - `GET /games/{name}/gap/{number}` — Per-number gap/overdue analysis
  - `GET /games/compare` — Cross-game odds comparison
  - `POST /games/{name}/wheel` — Wheel generation (full/key/abbreviated)
  - `POST /games/{name}/ticket-grade` — Multi-dimension ticket grading (A+ → F)
- **8 new Pydantic models** for API endpoint request/response schemas
- **Comprehensive test suite** (`test_api_and_integration.py`) covering:
  - API model serialization, sum range integration, deviation analysis
  - Wheels module, odds comparator, strategy registry integrity
  - CLI command importability for 13 key commands
- **CHANGELOG.md** — this file (project-wide release notes)

### Changed
- **README.md** — Complete rewrite reflecting 100+ CLI commands, 80+ strategies, full architecture
- **pyproject.toml** — Version bumped to 11.2.0, removed duplicate dependencies (numexpr, bottleneck), updated description, added fastapi/uvicorn to `[all]` extras
- **API version** — Updated from 0.1.0 to 11.2.0

### Fixed
- Duplicate `numexpr>=2.10.2` and `bottleneck>=1.4.2` entries in pyproject.toml core dependencies
- `[all]` optional dependency group was missing `fastapi` and `uvicorn`

---

## [11.1.0] - 2026-05-28

### Added
- **Portfolio Dashboard** — Multi-lottery combo play simulation with HTML export
- **Expert Suggest API** — `POST /games/{name}/expert-suggest` endpoint
- **Sacred Manifold API** — `POST /games/{name}/sacred-manifold` and transit endpoints
- **Portfolio simulation tests** — `test_portfolio_dashboard.py`

---

## [11.0.0] - 2026-05-12

### Added
- **Quantum-Astro Intelligence Tier** — Arcsecond-accurate planetary calculations via AstroPy
- **Prophet ML Tier** — XGBoost/CatBoost/LightGBM regressor ensemble
- **LSTM-CRF Strategy** — Sequence labeling for inter-number dependency modeling
- **Stacking AI** — Meta-learner stacking ensemble
- **Desktop Client** — PySide6 analytical cockpit

---

## [10.0.0] - 2026-05-03

### Added
- **Diagnostic Terminal** (Sprint 2.36) — `signal`, `cluster`, `stress-test`, `--explain`
- **Esoteric Overlay** (Sprint 2.37) — `detect-patterns`, `leaderboard`, Obsidian DataviewJS
- **Daily Automation** (Sprint 2.38-2.40) — `log`, `forecast`, `daily`, `alert`, post-fetch hooks
- **Regime Detection** (Sprint 2.39) — `compare-draws`, `trend`, `next`, Jensen-Shannon divergence
- **Watchlist** (Sprint 2.41) — Batch game tracking sub-application
- **Calibration** (Sprint 2.45) — Empirical out-of-sample hit-rate calibration
- **Analytics Expansion** (Sprint 2.40-2.60) — 25 new CLI commands
- **Total CLI commands**: 100+
- **Total strategies**: 80+

---

## [9.0.0] - 2026-04-29

### Added
- **FastAPI Sidecar** (Sprint 2.1) — REST API with 12+ endpoints
- **Go Gateway** (Sprint 3) — Auth, rate limiting, caching proxy
- **Expo App** (Sprint 4) — React Native + Web dashboard
- **Analysis Dashboard Phase 2** — Spatial voids, Z-score scaling
- **Advanced Metrics Strategy** — AC Value, Root Sum, Unit Sum

---

## [8.0.0] - 2026-04-28

### Added
- **30+ new strategies** across statistical, ML, and fun tiers
- **100+ structural filters** — sum-range, parity, consecutive, decade breadth, etc.
- **Board command** — Rich terminal visualization with multiple views
- **Wheels module** — Full/key/abbreviated covering designs
- **150+ game registry** — Global lottery catalog in YAML
- **DuckDB integration** — High-performance analytical database
- **MCP server** — Model Context Protocol integration

---

## [7.0.0] - 2026-04-27

### Added
- **Absurdity Engine v4-v10** — 9 new strategies (primes, quantum, kabbalistic, ley_lines, etc.)
- **Sacred Manifold** — Dodecahedron geometry module
- **Intentional Seeding** — SHA256-based deterministic ticket generation
- **Chaos Temperature Governor** — Environmental chaos modulation

---

## [1.0.0] - 2026-04-26

### Added
- **Core Engine** — 23 strategies, 3 ensembles, 6 CLI commands
- **Adapters** — Mega-Sena, Lotofácil, Powerball
- **Analysis modules** — Frequency, deviation, correlation
- **Backtest** — Blind historical strategy testing
- **Optimize** — Grid search over strategy × history × temperature
- **Chi² gate** — Statistical significance testing on all predictions
