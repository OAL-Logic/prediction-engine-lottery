# API Contracts: core-engine (Python)

The core engine provides a FastAPI-based REST interface for lottery analysis and prediction.

## Endpoints

### 🎮 Game Management
- `GET /games`: List available lottery games and their latest draw IDs.
- `GET /games/{name}`: Get detailed rules and configuration for a specific lottery.
- `POST /games/{name}/fetch`: Trigger a historical draw fetch (via adapters).

### 📊 Statistical Analysis
- `GET /games/{name}/analysis`: Get a comprehensive statistical snapshot (Frequency, Deviation, Correlation).
- `GET /games/{name}/odds`: Calculate combinatorial odds for specific prize tiers.

### 🚀 Prediction & Simulation
- `POST /games/{name}/suggest`: Generate optimized ticket suggestions using specified strategies.
- `POST /games/{name}/backtest`: Run historical simulations to evaluate strategy performance.
- `POST /games/{name}/check`: Verify a specific ticket against historical draws.

### 🧠 Intelligence & AutoML
- `GET /strategies`: List all registered prediction strategies and their tiers.
- `POST /games/{name}/prune`: Automatically identify and disable underperforming strategies.
- `POST /games/{name}/calibrate`: Fine-tune strategy parameters based on recent drift.
- `POST /games/{name}/tune`: Run exhaustive grid search for optimal configuration.

## Schemas
- `GameSummary`: {name, total_draws, last_draw_id, last_draw_date}
- `SuggestionResponse`: {tickets, scores, confidence, metadata}
- `AnalysisResult`: {frequency_stats, gap_stats, pattern_anomalies}

---
_Generated: 2026-05-14_
