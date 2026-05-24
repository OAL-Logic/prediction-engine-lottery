> 📝 **Renamed 2026-04-28** — was `v4.0.md`. These are *feature batches*, not git releases.
> The `pyproject.toml` version is still `0.1.0`; the v4–v10 numbering reflects internal
> design rounds, not published versions. See `README.md` in this directory.

---

# Version 4.0: Celestial Gravitation & Universal Gematria

## Overview
v4.0 introduced the transition from static historical analysis to real-time celestial and linguistic correlation.

## Key Features
### 1. Lunar Gravitational Tides
- **Theory:** The Moon's distance (Anomalistic month) and phase (Synodic month) create varying levels of gravitational drag in the draw room.
- **Technical:** Calculates Lunar Distance (Perigee/Apogee) and Tidal Intensity (0.0-1.0).
- **User Impact:** Displays "High Tide" alerts, indicating potential physical instability in the ball blower.

### 2. Universal Gematria Overlay
- **Theory:** Words are vibrations. Overlaying a specific intent (topic) onto a personal signature creates a focused "Intentional Intersection."
- **User Impact:** New `--topic` flag allowed users to input words like "WEALTH" or "VICTORY" to modify the prediction grid.

### 3. The Prime Oscillator
- **Theory:** Prime numbers follow cyclical harmonic patterns entrained to the synodic month.
- **Technical:** Correlates "Prime Density" (percentage of primes in a draw) with lunar phases.
- **User Impact:** Identifies prime-heavy regimes based on the current moon phase.

## CLI Commands
```bash
lottery suggest mega-sena --strategy primes
lottery suggest mega-sena --strategy kabbalistic --topic "SUCCESS"
```
