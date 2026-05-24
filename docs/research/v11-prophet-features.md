# v11.1 Prophet Synthesis: Feature Catalog 🧩

_This document provides a detailed technical catalog of the features synthesized from the LottoProphet project into the Lottery Engine v11.1._

---

## 1. Intelligence Tiers (ML & Deep)

### 1.1 Game-Theoretic Expected Value Model (FR20)
**Objective**: Shift from individual number frequency to combination-based valuation.
- **Advantage Principle**: Each number in the pool is weighted by how much it contributes to high-value historical combinations (Parity, High-Low, Span).
- **Mixed Strategy**: Injects a temperature parameter into the EV calculation to prevent 100% deterministic traps.
- **Grounding**: Ported from `expected_value_model.py`.

### 1.2 Sequence Brain (LSTM-CRF) (FR21)
**Objective**: Model the inter-number dependencies within sorted ticket vectors.
- **Global Normalization**: The CRF layer models the entire sequence transition, ensuring that `Ticket[i]` is mathematically aware of `Ticket[i-1]`.
- **Validation**: Enforces structural validity of the sequence at the neural level.
- **Grounding**: Ported from `model.py`.

### 1.3 High-Performance Regressors (FR22)
**Objective**: Maximum predictive lift via gradient boosting ensembles.
- **XGBoost**: Captures non-linear feature interactions in historical time-series.
- **LightGBM / CatBoost**: Handles categorical features (e.g., Draw Day, Lunar Phase) with extreme efficiency.
- **Grounding**: Ported from `ml_models.py`.

---

## 2. The Prophet Dashboard (Desktop)

### 2.1 Multi-Tab Cockpit (FR23)
**Objective**: A professional-grade desktop analytical interface.
- **Predict Tab**: Unified suggestion interface for all strategies (Nerd, Chaos, Prophet).
- **Expected Value Tab**: Interactive heatmap and probability distribution viewer.
- **Data Analysis Tab**: High-fidelity charts for trend and gap analysis.
- **Grounding**: Ported from `lottery_predictor_app_new.py`.

### 2.2 Real-time Telemetry Hub (FR25)
**Objective**: Visualize non-blocking analytical progress.
- **Log Emitter**: A dedicated background thread that pipes analytical pulses (Astro-Scans, QPU status) to a scrolling mono viewport.
- **Semantic Highlighting**: Uses the "Forensic Neon" theme to color-code engine status updates.
- **Grounding**: Ported from `thread_utils.py`.

---

## 3. Data Engineering (FR24)

### 3.1 Sliding-Window Feature Store
**Objective**: Real-time extraction of time-series features for the ML ensemble.
- **Feature Set**:
    - `frequency_window`: Rolling frequency per number.
    - `gap_window`: Rolling interval since last appearance.
    - `trend_score`: Momentum based on recent successes.
- **Grounding**: Ported from `data_processing.py`.

---
_This document is the authoritative technical reference for the v11.1 Prophet Synthesis._
