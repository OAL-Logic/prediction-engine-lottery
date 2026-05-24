# 🎲 Prediction Engine — Strategy Guide

> *A field guide to choosing, reading, and combining prediction strategies.*
> *56 strategies across 4 tiers — Sprint 1 + Sprint 2 + High-Fidelity restoration.*

---

## The Big Picture

The Prediction Engine doesn't just "guess" numbers. It runs dozens of independent algorithms—each with its own mathematical or environmental logic—and aggregates them into a **Consensus Signal**.

### Tier 1: Statistical (Quantitative)
Pure math. These strategies look at the "physics" of the draw distribution.
- **Top Picks:** `markov`, `bayesian`, `spectral`, `weighted`.
- **New Additions:** `structural` (Howard-style balance), `survival` (meta-adaptive), `mutual_info`.

### Tier 2: Machine Learning (Tabular)
Detects non-linear patterns that humans miss.
- **Top Picks:** `gradient_boost`, `random_forest`, `synapse`.
- **Ensembles:** `voting`, `hybrid`, `stacking` (combine multiple models for better accuracy).

### Tier 3: Deep Learning (Sequential)
Neural networks that treat lottery draws like a language or a time-series.
- **Models:** `transformer`, `lstm_gru`, `cnn_1d`.

### Tier 4: Fun & Chaos (Esoteric / Environmental)
Experimental strategies that correlate draws with the world around them.
- **Atmospheric:** `weather`, `refraction`, `seismic`, `solar`.
- **Consciousness:** `noosphere`, `sentiment`, `entropy_global`.
- **Classical:** `numerology`, `kabbalistic`, `iching`, `zodiac`.
- **Market:** `vix_jitter` (Financial volatility resonance).

---

## The Golden Path (How to Choose)

### 1. The Sober Quantitative Approach (Nerd Mode)
If you believe the lottery is a closed mathematical system:
```bash
lottery suggest lotofacil --strategy statistical --temp 0
```
*Uses only pure statistical models with deterministic sampling.*

### 2. The High-Fidelity Convergence (The Synapse)
If you want the peak of the engine's capability:
```bash
lottery suggest lotofacil --strategy synapse --explain
```
*Runs Statistical, Deep, and Chaos cylinders simultaneously to find "Universal Conjunctions".*

### 3. The Chaos Session (Experimental)
If you want to play with the environmental "jitter" of the day:
```bash
lottery suggest lotofacil --strategy chaos --temp 1.2
```
*Uses esoteric and environmental signals with high exploratory temperature.*

---

## Command Reference

| Goal | Command |
|------|---------|
| **Predict** | `lottery suggest <game>` |
| **Verify** | `lottery analyze <game> --view complete` |
| **Optimize** | `lottery tune <game> --strategies statistical` |
| **Calibrate** | `lottery calibrate <game>` |
| **Audit** | `lottery audit-data <game>` |
| **Compare** | `lottery compare-strategies <game>` |

---

## Full Strategy List

Run the following to see the detailed description of every strategy:
```bash
lottery strategies
```

*Prediction Engine — High-Fidelity restoration. 56 strategies across 4 tiers.*
