> 📝 **Renamed 2026-04-28** — was `v5.0.md`. These are *feature batches*, not git releases.
> The `pyproject.toml` version is still `0.1.0`; the v4–v10 numbering reflects internal
> design rounds, not published versions. See `README.md` in this directory.

---

# Version 5.0: The Neural-Quantum Orchestrator

## Overview
v5.0 focused on structural harmony and visual transparency, ensuring that "absurd" predictions still followed rigorous mathematical constraints.

## Key Features
### 1. The Balanced Wheel Filter
- **Theory:** Based on Gail Howard's "Balanced Wheel" theory. Tickets must represent "Structural Harmony" to be valid.
- **Technical:** Implemented a resampling loop in `BaseStrategy`. Tickets are discarded if they fail:
  - **Sum Range:** Must fall within the 70% probability window (ideal sum ± 30%).
  - **Parity:** No all-odd or all-even tickets allowed.
  - **Breadth:** Must span at least 3 different decades.

### 2. Chaos Temperature Governor
- **Theory:** Sampling randomness should not be fixed; it should breathe with the environment.
- **Technical:** Adjusts the `active_temp` based on entropy signals.
- **User Impact:** Automatic +0.5 temperature boost during **Arcano 78 (Sudden Windfall)** windows.

### 3. High-Definition Color Sigils
- **Theory:** Visual entrainment with the prediction grid.
- **User Impact:** 
  - **Red:** Highlights negative sequences (repeated digits) representing stagnation.
  - **Gold:** Highlights Arcanos of Success.
  - **Personal Profile:** Displays Motivation, Impression, Expression, Destiny, and Mission.

## CLI Rendering
The `kabbalistic` strategy now outputs a colorized "Inverted Triangle of Life" (Signature Sigil).
