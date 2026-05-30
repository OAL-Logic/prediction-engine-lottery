# Lottery Engine: Project Index (v11.2)

Welcome to the **Lottery Engine** — a professional intelligence platform for lottery statistical analysis, prediction, and portfolio management with 100+ CLI commands, 80+ prediction strategies, and a full-stack architecture.

## 🗺️ Project Map

### 🏗️ Architecture & Core
- [Project Overview](architecture/project-overview.md) — Strategic vision and quad architecture summary.
- [ADR-001](architecture/ADR-001-architecture-evaluation.md) — Architecture evaluation and decisions.
- [Technical Spec](architecture/technical-spec.md) — Detailed technical specification.
- [System Overview](architecture/system-overview.md) — High-level system design.
- [Engine Architecture](architecture/engine.md) — Mathematical heartbeat (Python).
- [Gateway Architecture](architecture/gateway.md) — Security and routing hub (Go).
- [App Architecture](architecture/app.md) — Cross-platform visualization (Expo).
- [TUI Architecture](architecture/tui.md) — Terminal command center (OpenTUI).
- [Integration Architecture](integration-architecture.md) — How the quad communicates.

### 🧠 Intelligence & Research
- [Intelligence Hierarchy](research/intelligence-hierarchy.md) — Map of the 80+ strategies and 30+ filters.
- [Data Models](data-models-engine.md) — Core schemas and persistence layers.
- [API Contracts (Engine)](api-contracts-engine.md) — Python sidecar endpoints (17+).
- [API Contracts (Gateway)](api-contracts-gateway.md) — Go edge security.

### 🚀 Implementation & Lifecycle
- [Sprint Plan](../SPRINT_PLAN.md) — Master roadmap (authoritative).
- [Changelog](../CHANGELOG.md) — Version history and release notes.
- [Source Tree](source-tree.md) — Detailed repository structure.
- [Development Guide](development-guide.md) — Environment setup and testing.
- [User Stories](../user_stories.md) — Functional requirements and ACs.

### 📖 Manuals
- [User Guide](user_guides/user-guide.md) — Operational instructions.
- [TUI Design](user_guides/TUI.md) — Visual cockpit reference.
- [Desktop Guide](user_guides/PROPHET_DESKTOP.md) — PySide6 desktop client.

---

## 🛠️ Technology Stack
- **Backend**: Python 3.11+ (FastAPI), Go 1.23 (Chi)
- **Frontend**: Expo/React Native, TypeScript
- **Desktop**: PySide6
- **Visualization**: Three.js, OpenTUI, Rich, Chart.js
- **Intelligence**: PyTorch, Scikit-Learn, XGBoost, CatBoost, LightGBM
- **Data**: NumPy, Pandas, DuckDB, AstroPy
- **Integration**: MCP (Model Context Protocol), FastMCP

---

## 📊 Project Statistics (v11.2)

| Metric | Count |
|--------|-------|
| CLI Commands | 100+ |
| Prediction Strategies | 80+ |
| Structural Filters | 30+ |
| API Endpoints | 17+ |
| Supported Lotteries | 150+ (registry) |
| Test Files | 42 |

---
_Last Updated: 2026-05-29_
