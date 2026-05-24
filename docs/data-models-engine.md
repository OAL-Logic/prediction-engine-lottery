# Data Models: core-engine

The core engine uses Pydantic for data validation and NumPy/Pandas for high-performance mathematical modeling.

## 📐 Core Schemas

### Game & Rules
- `GameRulesSchema`: Defines the number pool, pick count, and prize tiers.
- `GameSummary`: A lean metadata snapshot for game indexing.

### Strategy & Prediction
- `SuggestionRequest`: Parameters for ticket generation (Strategy, Count, Temperature, Mode).
- `SuggestionResponse`: The resulting tickets, including scores, confidence, and OSINT metadata.
- `BacktestRequest`: Configuration for historical performance audits.

### Intelligence & Analysis
- `AnalysisResultSchema`: Detailed statistical breakdown (Frequency, Gaps, Z-Scores).
- `PruningResponse`: Performance audit results identifying underperforming models.

## 🗄️ Storage Models
- **Partitioned JSON**: Historical draws are stored in yearly chunks (`data/history/YYYY.json`).
- **DuckDB/SQLite**: High-frequency indices for sub-second retrieval of specific structural patterns.

---
_Generated: 2026-05-14_
