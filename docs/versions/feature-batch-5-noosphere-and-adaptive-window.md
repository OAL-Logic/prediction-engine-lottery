> 📝 **Renamed 2026-04-28** — was `v8.0.md`. These are *feature batches*, not git releases.
> The `pyproject.toml` version is still `0.1.0`; the v4–v10 numbering reflects internal
> design rounds, not published versions. See `README.md` in this directory.

---

# Version 8.0: The Noospheric Singularity

## Overview
v8.0 represents a breakthrough in moving the Absurdity Engine beyond individual vibrational paths and into the broader realm of global consciousness and adaptive temporal analysis. The focus has expanded from personal geometries to macroscopic fluctuations.

## Key Features
### 1. The Sephoric Tree of Life
- **Theory:** Kabbalistic tradition suggests reality emanates through 10 Sephiroth and 22 connecting Paths. By mapping numbers to these emanations, we detect the "structural flow" of energy in the draws.
- **Technical:** Implements the `sefirot` strategy, grouping the number pool into Sephiroth (1-10), Paths (11-32), and Harmonics (33+). The "Active Sephirah" of the draw day receives a probability boost.
- **User Impact:** Provides a macro-esoteric view of draw outcomes through the lens of ancient emanation trees.

### 2. The Noosphere Jitter Layer
- **Theory:** Inspired by the Global Consciousness Project (GCP), this assumes that synchronized mass attention influences random number generators. We model this as "vibrational jitter" in the human Noosphere.
- **Technical:** The `noosphere` strategy simulates this by analyzing high-frequency time-drifts (hashed epochs) to measure current "global entropy." Volatile states increase the Chaos Temperature Governor.
- **User Impact:** Injects a "Noosphere Intensity" reading into the correlation panel, driving more exploratory ticket suggestions when global focus is highly coherent or volatile.

### 3. The Adaptive History Window
- **Theory:** The statistical "signal-to-noise" ratio of historical draws varies. Sometimes the most recent 20 draws are the most predictive; sometimes it's the last 50.
- **Technical:** The engine introduces the `--adaptive-window` flag. `BaseStrategy.suggest()` sweeps multiple history boundaries to select the optimal temporal window dynamically.
- **User Impact:** Removes the need to manually guess the `--limit`. The Statistician expert automatically finds the sweet spot.

## Summary of Experts
- **The Statistician:** Adaptive History Window Sweep.
- **The Chaos Analyst:** Noosphere Jitter Detection.
- **The Esoteric Architect:** Sephoric Tree of Life Emanations.
