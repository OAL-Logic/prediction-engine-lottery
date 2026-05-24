# Analytical Engine: Strategy Documentation

The Lottery Engine utilizes a diverse set of strategies to score the number pool and generate suggestions. Strategies are categorized into tiers based on their methodology and complexity.

## 🛠️ The BaseStrategy Class
All strategies inherit from `BaseStrategy` (found in `engine/strategies/__init__.py`), which provides:
- **`score(df, rules)`**: (Mandatory) Assigns a 0–1 score to each number.
- **`suggest()`**: (Provided) Handles temperature-based sampling, mandatory keys, pool constraints, and the Harmony Gate.
- **`is_harmonious()`**: (Provided) Evaluates 30+ structural filters (Sum Range, Parity, Breadth, etc.).

---

## 📊 Statistical Tier
Focuses on historical frequency and mathematical distributions.

| Strategy | Logic Genesis | Key Pattern |
| :--- | :--- | :--- |
| **`weighted`** | Multi-signal blend | Weighted average of freq, recency, and momentum. |
| **`bayesian`** | Bayesian inference | Updated prior distribution based on draw evidence. |
| **`markov`** | State transitions | Probability of N appearing given N-1 in history. |
| **`spectral`** | Periodicity | FFT (Fast Fourier Transform) to detect "rhythm." |
| **`steiner`** | Combinatorial design | Uses Steiner Triple Systems for optimal coverage. |

---

## 🔮 Fun / Chaos Tier
Esoteric and environment-driven strategies for experimental exploration.

| Strategy | Input Vector | Logic |
| :--- | :--- | :--- |
| **`kabbalistic`** | Gematria / Arcanos | Mapping draw dates and topics to Hebrew Arcanos. |
| **`moon_phase`** | Lunar Synodic Cycle | Correlation of numbers with the 29.5-day cycle. |
| **`solar`** | Geomagnetic Flux | Modulating scores based on the K-Index (Solar Flares). |
| **`seismic`** | Tectonic Resonance | Mapping seismic magnitude to number frequency. |
| **`biorhythm`** | Biological Cycles | Personal Physical/Emotional/Intellectual alignment. |

---

## 🤖 ML & Deep Tiers
Advanced predictive models requiring external dependencies.

- **`synapse` (Ensemble)**: A neural consensus model that votes across multiple statistical signals.
- **`transformer` (Deep)**: Uses attention mechanisms to find long-range dependencies in draw sequences.
- **`regime` (Adaptive)**: Detects shifts in statistical stability and switches between "Hot" and "Cold" models.

---

## 🎲 Advanced Sampling Concepts

### Temperature ($T$)
Controls the "sharpness" of the prediction:
- **Low $T$ (< 0.7)**: Exploitation mode. Focuses only on high-scoring numbers.
- **High $T$ (> 1.2)**: Exploration mode. Flattens the distribution to allow long-shots.

### Atmospheric Muon Flux
A 0.5% "Chaos Event" per ticket generation. Simulates a bit-flip in the sampling memory, causing a single number to mutate. This represents the "Ghost in the Machine" and prevents 100% deterministic traps.

### Geometric Singularity
Boosts the scores of "Dodecahedron Neighbors" for top-scoring numbers, assuming a 3D structural relationship between numbers in the universe.
