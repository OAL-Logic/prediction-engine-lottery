---
project_name: 'lottery-engine'
user_name: 'oalsysd'
date: '2026-05-14'
sections_completed:
  [
    'technology_stack',
    'language_rules',
    'framework_rules',
    'testing_rules',
    'quality_rules',
    'workflow_rules',
    'don_t_miss_rules',
    'desktop_interface_rules'
  ]
status: 'evolutionary-hardened'
version: '11.1'
rule_count: 72
optimized_for_llm: true
---

# Project Context: Lottery Engine v11.1

_This file contains critical rules and patterns for the v11.1 Prophet Synthesis. Follow these rules to ensure the multi-platform Desktop Client and Advanced ML models integrate seamlessly._

---

## Technology Stack v11.1

### Core Technologies
- **Python 3.11+**: Base analytical engine and strategy logic.
- **Go 1.23.0**: High-performance API gateway and Telemetry Hub.
- **React Native / Expo ~54.0**: Gestural Mobile Interface.
- **Bun 1.2.x**: Terminal Cockpit.
- **PySide6 / PyQt6**: NEW: Prophet Desktop Client Interface.

### Key Dependencies (Prophet)
- **Machine Learning**: `xgboost`, `lightgbm`, `catboost`.
- **Deep Learning**: `torch`, `torchcrf` (LSTM-CRF).
- **Desktop UI**: `PySide6`, `matplotlib` (Charts), `seaborn`.

---

## Critical Implementation Rules

### Desktop Interface Rules (PySide6)

- **Qt: Thread Isolation Mandate**: NEVER run model training or heavy data processing on the main GUI thread. Always implement a `QThread` or `QRunnable` with a `LogEmitter` (pyqtSignal) to maintain UI responsiveness.
- **Qt: Signal-Slot Integrity**: Use type-safe signals for all telemetry data. Avoid passing complex objects; pass JSON strings or primitive identifiers.
- **Visuals: Forensic Theming**: Desktop tabs must utilize the "Forensic Neon" palette (Matrix Green: `#00ff41`, Obsidian Black: `#000000`).
- **Telemetry: Live Scrolling**: The log emitter viewport must support autoscroll-to-bottom by default to mimic the TUI experience.

### Model Integration Rules

- **Feature Grounding**: All ML models in `engine/strategies/ml/` MUST utilize the sliding-window feature engineering pattern from `data_processing.py`.
- **Model Checkpointing**: Models trained via the Desktop GUI must be serialized to `data/model_cache/` using `joblib` (ML) or `torch.save` (Deep) with a `{model_type}_{timestamp}.pt` naming convention.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing the **Prophet Desktop Client**.
- **Threading Safety**: Agents implementing GUI tabs MUST demonstrate proper `QThread` usage.
- **Parity Check**: Ensure that features exposed in the Desktop Client are also reachable via the API sidecar for TUI/Mobile parity.

Last Updated: 2026-05-14
