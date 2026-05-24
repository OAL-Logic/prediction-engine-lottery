---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments: [
  '_bmad-output/planning-artifacts/prd.md',
  '_bmad-output/planning-artifacts/ux-design-specification.md',
  '_bmad-output/planning-artifacts/architecture.md',
  'mnt/c/ws/prj-lotto.LottoProphet'
]
version: '11.1'
---

# lottery-engine - Epic Breakdown v11.1

## Overview
This document provides the complete epic and story breakdown for the v11.1 Prophet Synthesis. We are integrating the analytical depth and desktop GUI capabilities of the LottoProphet project as a new alternative interface and intelligence tier.

## Requirements Inventory (v11.1 Additions)

### Functional Requirements
- **FR20 (Expected Value)**: Implement the game-theory based expected value model for combination scoring.
- **FR21 (LSTM-CRF)**: Implement sequence modeling for inter-number dependency detection.
- **FR22 (ML Ensemble)**: Integrate XGBoost, LightGBM, and CatBoost into a unified regressor tier.
- **FR23 (Desktop Client)**: Develop a multi-platform PySide6 interface with tabbed analysis.
- **FR24 (Feature Engineering)**: Implement sliding window time-series feature extraction.

### FR Coverage Map (v11.1 Additions)
- FR20: Epic 5 Story 5.1 - Game-Theoretic Expected Value Model
- FR21: Epic 5 Story 5.2 - Sequence Logic Brain (LSTM-CRF)
- FR22: Epic 5 Story 5.3 - Extended ML Hub (XGB/LGBM/CAT)
- FR23: Epic 5 Story 5.4 - Desktop Client Interface (PySide6)
- FR24: Epic 5 Story 5.3 - Extended ML Hub (Feature Engineering)

## Epic List

... (Epics 1-4 preserved) ...

### Epic 5: Prophet Synthesis (Interface & Intelligence)
**Goal**: Integrate the full analytical depth and GUI capabilities of LottoProphet as a cross-platform desktop alternative.
**FRs covered**: FR20, FR21, FR22, FR23, FR24.

---

## Epic 5: Prophet Synthesis (Interface & Intelligence)

**Context Reference**: [Prophet Concepts: Game Theory & Sequence Modeling](docs/research/prophet-concepts.md)

### Story 5.1: Game-Theoretic Expected Value Model
**Technical Grounding**: Ported from `expected_value_model.py`.
```python
# LottoProphet Pattern: Feature Valuation
value_dict = {
    'even_odd_ratio': {},  # Parity logic
    'high_low_ratio': {},  # Magnitude logic
    'sum_range': {},       # Arithmetic logic
    'span_range': {},      # Spread logic
    'sequence_pattern': {} # Succession logic
}
```
**User Value**: Identify combinations that maximize the "Advantage Principle" based on historical structural ratios.

**Acceptance Criteria:**
- **Given** a historical dataset
- **When** the Expected Value strategy is invoked
- **Then** the system must calculate value scores for `even_odd_ratio`, `high_low_ratio`, and `sum_range`
- **And** output a normalized combination value score [0.0, 1.0].

### Story 5.2: Sequence Logic Brain (LSTM-CRF)
**Technical Grounding**: Ported from `model.py`.
```python
# LottoProphet Pattern: Deep Sequence Labeling
class LstmCRFModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, output_seq_length):
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim * output_seq_length)
        self.crf = CRF(output_dim, batch_first=True)
```
**User Value**: Deep sequence modeling to ensure predicted tickets follow realistic dependency patterns.

**Acceptance Criteria:**
- **Given** a PyTorch environment
- **When** the LSTM-CRF model is initialized
- **Then** it must utilize a Bi-LSTM layer followed by a Conditional Random Field (CRF)
- **And** achieve a sequence-labeling accuracy ≥ v10.0 baselines.

### Story 5.3: Extended ML Hub (XGBoost/LightGBM/CatBoost)
**Technical Grounding**: Ported from `ml_models.py`.
```python
# LottoProphet Pattern: Multi-Regressor Ensemble
MODEL_TYPES = {
    'random_forest': 'random forest',
    'xgboost': 'XGBoost',
    'gbdt': 'gradient boosted tree',
    'ensemble': 'integrated model'
}
# Supports optional: lightgbm, catboost
```
**User Value**: Superior predictive lift via high-performance gradient boosting ensembles.

**Acceptance Criteria:**
- **Given** sliding-window features (frequency, gap, trend)
- **When** the ML Regressor hub is trained
- **Then** it must optimize parameters for XGBoost, LightGBM, and CatBoost
- **And** store the serialized models in `data/model_cache/`.

### Story 5.4: Desktop Client Interface (PySide6)
**Technical Grounding**: Ported from `lottery_predictor_app_new.py`.
```python
# LottoProphet Pattern: Multi-Tab Dashboard
self.tab_widget = QTabWidget()
self.tab_widget.addTab(self.main_tab, "predict")
self.tab_widget.addTab(self.expectedvalue_tab, "Expected value model")
self.tab_widget.addTab(self.analysis_tab, "data analysis")
```
**User Value**: A feature-rich desktop alternative for professional deep-dives.

**Acceptance Criteria:**
- **Given** a PySide6 environment
- **When** the Desktop Client launches
- **Then** it must present a multi-tabbed dashboard (Predict | Expected Value | Analysis | Logs)
- **And** adhere to the "Forensic Neon" color palette.

### Story 5.5: Real-time Telemetry WebSocket
**Technical Grounding**: Ported from `thread_utils.py`.
```python
# LottoProphet Pattern: Non-blocking Log Emitting
class LogEmitter(QObject):
    new_log = pyqtSignal(str)
    def emit_log(self, message):
        self.new_log.emit(message)
```
**User Value**: Real-time feedback for long-running distillation and training jobs.

**Acceptance Criteria:**
- **Given** an active analytical job
- **When** the Go Gateway emits a signal
- **Then** the Desktop Client must render a live-scrolling monospaced log stream
- **And** provide semantic highlighting for critical events.
