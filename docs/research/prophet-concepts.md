# Prophet Concepts: Game Theory & Sequence Modeling 🔮

_This document provides foundational context for the v11.1 Prophet Synthesis, explaining the core concepts derived from the LottoProphet project._

---

## 1. Expected Value Model (Game Theory)

### The Concept
Traditional lottery analysis focuses on the **Frequency** of individual numbers. The **Expected Value (EV) Model** shifts the focus to the **Value of Combinations** based on the "Advantage Principle."

In game theory, we treat the lottery draw as a non-cooperative game between the "Player" and the "Machine." By analyzing historical structural ratios, we can identify which "Move" (combination pattern) has the highest mathematical advantage in the current cycle.

### Scoring Metrics
The EV model calculates the "Advantage Score" using the following grounding logic from `expected_value_model.py`:
- **Parity Value (`even_odd_ratio`)**: Measures the historical success of specific odd/even distributions.
- **Magnitude Value (`high_low_ratio`)**: Evaluates the balance between low-half and high-half numbers.
- **Arithmetic Value (`sum_range`)**: Identifies the "Goldilocks Zone" of ticket sums.
- **Spread Value (`span_range`)**: Calculates the optimal distance between the lowest and highest numbers.

**Grounding Logic:**
```python
# The model creates a 'Value Dict' for every pattern
value_dict['even_odd_ratio'][even_odd_key] = value_dict['even_odd_ratio'].get(even_odd_key, 0) + 1
# This is then normalized against total drawings to provide a probability-weighted score
```

---

## 2. LSTM-CRF Sequence Modeling

### The Concept
Predicting lottery numbers is inherently a **Sequence Labeling** problem. Traditional LSTMs are good at capturing long-term dependencies (e.g., "Number 7 often follows Number 3"), but they lack structural constraints for the entire sequence.

**Conditional Random Fields (CRF)** solve this by modeling the dependencies between the labels (the numbers in a ticket) globally. In v11.1, the **LSTM-CRF** architecture ensures that the predicted sequence not only has high individual probability but also follows a mathematically valid "Transition Matrix."

### Architecture
Grounded in the `model.py` pattern:
- **Bi-LSTM Layer**: Processes historical sequences in both directions to identify "Symmetry Gaps."
- **CRF Layer**: Decodes the logits to find the most probable *sequence* of numbers, enforcing that no two numbers in the same ticket are identical (Label Consistency).

**Grounding Logic:**
```python
class LstmCRFModel(nn.Module):
    def __init__(self, ...):
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim * output_seq_length)
        self.crf = CRF(output_dim, batch_first=True)
```

---

## 3. Real-time Telemetry (Log Emitting)

### The Concept
To maintain an "Instant Intelligence" feel in a multi-platform environment, we port the PyQt5 `LogEmitter` pattern to a **Unified Telemetry Hub**. 

Every analytical job (Distillation, Retraining, Resonance Scans) emits real-time binary/text pulses. This ensures the user is never left with a "frozen" interface during high-latency operations.

---
_This document is a live research artifact for the v11.1 Singularity._
