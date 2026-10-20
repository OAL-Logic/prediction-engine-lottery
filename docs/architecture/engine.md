# Architecture: core-engine (Python)

The core engine is the mathematical heartbeat of the system.

## 🏛️ Technical Stack
- **Language**: Python 3.12+
- **API**: FastAPI (Sidecar pattern)
- **Data Engine**: Pandas/NumPy (Vectorized)
- **Database**: DuckDB + SQLite
- **Intelligence**: PyTorch (Transformers/LSTM), Scikit-Learn (Ridge/ML)

## 📐 Core Modules
- `engine/modules/filters/`: The **Universal Harmony Gate**. 100+ high-performance structural filters.
- `engine/modules/narrative.py`: The **Synapse Architect**. Generative briefings and decision auditing.
- `engine/modules/risk.py`: Financial tier implementing the **Kelly Criterion**.
- `engine/modules/pruning.py`: Performance/redundancy audits (`lottery prune`) — the on-demand evaluation `strategy_roster.py` falls back to for uncalibrated strategies.
- `engine/modules/strategy_roster.py`: Turns calibration lift into a persisted per-game active roster (`lottery select-strategies`, consumed via `--strategies roster`). Policy: `docs/wayfinder/decisions/003-policy-thresholds-decision.md`.
- `engine/strategies/`: Prediction algorithms categorized into Statistical, ML, Deep, Foundation, and Fun tiers.

---
_Generated: 2026-05-14_
_Updated: 2026-09-16 (strategy roster, foundation tier: timesfm + tabfm, 3 orphaned BR adapters + Mega Millions/EuroMillions wired into the registry, Lottery Studio Qt interface #106)_
