# Product Requirements Document: Lottery Engine v11.1

---
project_name: 'lottery-engine'
status: 'evolutionary-synthesis'
version: '11.1'
date: '2026-05-14'
input_documents: [
  'user_stories.md',
  'detailed_features.md',
  'docs/architecture/project-overview.md',
  'docs/research/intelligence-hierarchy.md',
  'docs/research/technical-quantum-astro-agentic-synthesis-for-v110-research-2026-05-14.md',
  'mnt/c/ws/prj-lotto.LottoProphet'
]
stepsCompleted: ['step-01-init', 'step-01b-continue', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation']
classification:
  projectType: 'Multi-Part AI Platform'
  domain: 'Computational Prediction & Financial Intelligence'
  complexity: 'High+'
  projectContext: 'brownfield-synthesis'
---

## 1. Executive Summary
The **Lottery Engine v11.1** marks the "Prophet Synthesis"—the integration of the high-density analytical capabilities of **LottoProphet** into the v11.0 Quantum-Astro-Agentic foundation. By synthesizing v11.0's 3D Riemannian manifolds with v11.1's **Game-Theoretic Expected Value** and **LSTM-CRF sequence modeling**, the platform evolves into a complete **Financial Intelligence Suite**. 

The core differentiator of v11.1 is the **Prophet Desktop Interface**: a cross-platform desktop alternative (PySide6) that exposes real-time model training, advanced statistical tabbed analysis, and "Expected Value" optimization alongside our high-fidelity 3D "Spatial Retina."

## 2. Project Classification
- **Project Type**: Multi-Part AI Platform (CLI, API, Expo App, and **Desktop Client**).
- **Domain**: Computational Prediction, Game Theory, & Financial Intelligence.
- **Complexity**: **High+** (Quantum-Astro-Agentic Synthesis + Advanced ML Ensemble + Multi-Platform Desktop GUI).

## 3. Success Criteria (v11.1 Additions)

### User Success
- **Analytical Mastery**: Users can leverage the "Expected Value" dashboard to identify combinations with the highest "Advantage Principle" score.
- **Interface Flexibility**: Users can switch between a high-speed TUI, a gestural mobile app, and a feature-rich desktop client without losing state.

### Technical Success
- **Model Parity**: Achieve 100% feature parity with LottoProphet’s `LSTM-CRF` and `XGBoost/LightGBM/CatBoost` ensemble.
- **Cross-Platform Fluidity**: The PySide6/PyQt6 interface must maintain < 200ms latency for tab switching and real-time log emitting.

## 4. Product Scope (v11.1 Expansion)

### MVP - Prophet Synthesis (v11.1 Launch)
- **Expected Value Engine**: Ported game-theory model for number combination valuation.
- **Sequence Modeling (LSTM-CRF)**: Advanced deep learning for inter-number dependency detection.
- **Desktop Prophet Client**: Multi-tab GUI alternative (PySide6/PyQt6) with real-time log emitting.
- **Advanced Feature Engineering**: Sliding window time-series features (frequency, gap, trend).

### Growth Features (v11.5)
- **Unified Swarm Dashboard**: Visualizing MARL agent trajectories within the Desktop Client.
- **Interactive Model Training**: GUI-based control for retraining the ML ensemble.

## 5. User Journeys (v11.1 Additions)

### Journey 4: The Prophet’s Audit (Desktop Path)
**Persona**: Elias, the Strategic Custodian.  
**Opening**: Elias wants to perform a deep-dive analysis of "Expected Value" before committing to a ticket.  
**Action**: Launches the **Desktop Client**, switches to the **"Expected Value"** tab, and reviews the probability distribution grounded in historical combination values.  
**Resolution**: He selects a combination that maximizes the "Advantage Principle," synchronized with the 3D manifold resonance.

## 6. Technical Grounding (LottoProphet Porting)

**Context Reference**: [Prophet Concepts: Game Theory & Sequence Modeling](docs/research/prophet-concepts.md)

### Feature: Expected Value Model (FR20)
**Code Anchor**: `LottoProphet/expected_value_model.py`
**Logic**: Calculates combination value based on `even_odd_ratio`, `high_low_ratio`, and `sum_range`.
```python
# Grounding Pattern:
value_dict = {
    'even_odd_ratio': {},  # Normalized parity frequency
    'high_low_ratio': {},  # Normalized magnitude frequency
    'sum_range': {},       # Arithmetic Goldilocks zone
    'span_range': {},      # Geodesic spread value
    'sequence_pattern': {} # Succession logic
}
```

### Feature: LSTM-CRF Sequence Modeling (FR21)
**Code Anchor**: `LottoProphet/model.py`
**Logic**: Uses Bi-LSTM paired with a Conditional Random Field (CRF) to label number sequences.
```python
# Grounding Pattern:
class LstmCRFModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, output_seq_length):
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim * output_seq_length)
        self.crf = CRF(output_dim, batch_first=True)
```

### Feature: ML Regressor Hub (FR22)
**Code Anchor**: `LottoProphet/ml_models.py`
**Logic**: Unified interface for high-performance regressors.
```python
# Grounding Pattern:
MODEL_TYPES = {
    'random_forest': 'Random Forest',
    'xgboost': 'XGBoost',
    'lightgbm': 'LightGBM',
    'catboost': 'CatBoost'
}
```

### Feature: Desktop Telemetry (FR23/FR25)
**Code Anchor**: `LottoProphet/thread_utils.py`
**Logic**: Non-blocking log emission using Qt Signals.
```python
# Grounding Pattern:
class LogEmitter(QObject):
    new_log = pyqtSignal(str) # Broadcast to Telemetry Hub
```

## 7. Technical Requirements (v11.1 Capability Contract)

### Functional Requirements
- **FR20 (Expected Value)**: Implement the game-theory based expected value model for combination scoring.
- **FR21 (LSTM-CRF)**: Implement sequence modeling for inter-number dependency detection.
- **FR22 (ML Ensemble)**: Integrate XGBoost, LightGBM, and CatBoost into a unified regressor tier.
- **FR23 (Desktop Client)**: Develop a multi-platform PySide6/PyQt6 interface with tabbed analysis and real-time logs.
- **FR24 (Feature Engineering)**: Implement sliding window time-series feature extraction.

### Non-Functional Requirements
- **NFR8 (Desktop Stability)**: Desktop client must handle 1GB+ historical datasets without memory leaks.
- **NFR9 (GUI Latency)**: Real-time telemetry updates must not block the main UI thread.
