---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
inputDocuments: [
  '_bmad-output/planning-artifacts/prd.md',
  '_bmad-output/planning-artifacts/ux-design-specification.md',
  '_bmad-output/planning-artifacts/research/technical-quantum-astro-agentic-synthesis-for-v110-research-2026-05-14.md',
  '_bmad-output/project-context.md',
  'docs/architecture/project-overview.md',
  'mnt/c/ws/prj-lotto.LottoProphet'
]
workflowType: 'architecture'
project_name: 'lottery-engine'
user_name: 'oalsysd'
date: '2026-05-14'
version: '11.1'
---

# Architecture Decision Document v11.1: Prophet Synthesis

_This document defines the architectural expansion of the Lottery Engine to incorporate the high-density analytical and desktop interface capabilities of the LottoProphet project._

## 1. Project Context Analysis (v11.1)

### Requirements Overview

**Functional Requirements (Prophet Additions):**
The v11.1 evolution adds 5 core requirements (FR20-FR24) derived from the `LottoProphet` project. This includes the **Expected Value Model** for game-theoretic combination scoring, **LSTM-CRF** for deep sequence labeling, and a **PySide6 Desktop Interface** for multi-platform analytical depth.

**Non-Functional Requirements (v11.1):**
- **NFR8 (Interface Stability)**: The Desktop Client must maintain 99.9% crash-free sessions during intensive model training.
- **NFR9 (Concurrency)**: Real-time telemetry (log emitting) must operate on a dedicated background thread to prevent UI freezing.

---

## 2. Starter Template Evaluation (v11.1 Expansion)

### Selected v11.1 Pillars

#### 2.1 Desktop Client: PySide6 (Qt for Python)
- **Decision**: Implement a cross-platform desktop alternative using **PySide6**.
- **Rationale**: Based on the `lottery_predictor_app_new.py` pattern. PySide6 provides the high-density tabbed interface needed for complex ML analytics and real-time training visualization.

#### 2.2 ML Regressors: XGBoost / LightGBM / CatBoost
- **Decision**: Integrate high-performance gradient boosting frameworks into the `ml` tier.
- **Rationale**: Directly ported from the `ml_models.py` implementation in LottoProphet to provide superior predictive lift.

#### 2.3 Sequence Brain: LSTM-CRF
- **Decision**: Implement the `LstmCRFModel` in PyTorch with `torchcrf`.
- **Rationale**: Provides inter-number dependency detection, resolving the "Sequence Validity" problem in predicted tickets.

---

## 3. Core Architectural Decisions (v11.1)

### Data Architecture
- **Feature Store**: Implementation of a **Sliding Window Cache** in DuckDB to support the real-time feature engineering required by the Prophet ML models.
- **Model Registry**: Standardized serialization of trained XGBoost/Torch models into `data/model_cache/`.

### API & Communication Patterns
- **Unified Telemetry Stream**: The Go Gateway now supports a **Log-Emitter WebSocket** that broadcasts engine pulses, quantum distillation progress, and ML training logs to all clients (TUI, Expo, and Desktop).

### Desktop Client Architecture
- **Thread Management**: Utilizes a `ProphetThreadManager` to offload analytical calculations and model training from the Qt Main Thread.
- **Theme Bridge**: A unified **Theme Manager** to ensure "Forensic Neon" aesthetics are consistent across the desktop application.

---

## 4. Implementation Patterns (v11.1)

### Desktop GUI Pattern
- **Pattern**: Multi-tab "Intelligence Suite" (Predict | Expected Value | Statistics | Logs).
- **Grounding**: Follows the `create_main_tab` and `create_expected_value_tab` patterns from `LottoProphet/ui_components.py`.

### ML Integration Pattern
- **Pattern**: Strategy-level `train()` mandate. ML strategies must implement a standardized training interface that reports progress back to the `LogEmitter`.

---

## 5. Project Structure v11.1 (Final Synthesis)

```text
lottery-engine/
├── app/ (Expo Mobile)               # Gestural Interface
├── desktop/ (PySide6)               # NEW: High-Density Analytical Suite
│   ├── src/
│   │   ├── main.py                  # PyQt/PySide Entry Point
│   │   ├── tabs/                    # Tabbed Dashboard views
│   │   └── telemetry/               # Log-Emitter logic
├── engine/ (Python)                 # Analytical Core
│   ├── modules/
│   │   ├── expected_value.py        # FR20 (Game Theory Model)
│   │   └── feature_engineering.py   # FR24 (Sliding Window logic)
│   ├── strategies/
│   │   ├── deep/lstm_crf.py         # FR21 (Sequence Brain)
│   │   └── ml/regressor_hub.py      # FR22 (XGB/LGBM/CAT Hub)
├── gateway/ (Go)                    # PQC Gateway & Telemetry Hub
└── data/model_cache/                # Trained Prophet models
```

---

## 6. Architecture Readiness v11.1 ✅

**Overall Status: READY FOR PROPHET SYNTHESIS**

**Key Strength**:
The v11.1 architecture provides a **High-Density Desktop Bridge** for users who require deeper forensic controls than the TUI or Mobile App provide, while keeping the heavy ML/Deep models grounded in the high-performance Python engine.
