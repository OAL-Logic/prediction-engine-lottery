> 📝 **Renamed 2026-04-28** — was `v6.0.md`. These are *feature batches*, not git releases.
> The `pyproject.toml` version is still `0.1.0`; the v4–v10 numbering reflects internal
> design rounds, not published versions. See `README.md` in this directory.

---

# Version 6.0: The Synchronicity Matrix

## Overview
v6.0 introduced the concept of "Personal Determinism" and real-time physical resonance.

## Key Features
### 1. Intentional Seeding
- **Theory:** The random seed of the sampling engine should be a unique "Vibrational Fingerprint."
- **Technical:** Hashes (SHA-256) the user's name, birthdate, and topic to create a deterministic 32-bit seed.
- **User Impact:** Predictions are no longer "randomly generated"; they are "born" from the user's specific input. The same input always produces the same ticket for the same draw date.

### 2. Seismic Resonance (USGS)
- **Theory:** Even micro-tremors (Mag 1.0+) create mechanical jitter in pneumatic lottery blowers, affecting the "random" bouncing of balls.
- **Technical:** Integrates real-time USGS Earthquake API data within a 1000km radius of the draw location.
- **User Impact:** Tremors add a "Jitter Boost" to the Chaos Governor's temperature.

### 3. Recursive Ensemble Pruning
- **Theory:** In an ensemble, weak signals create noise. Only the "Alpha" strategies should lead.
- **Technical:** The `survival` strategy now discards the bottom 25% of strategies based on their 10-draw precision window.

## CLI Commands
```bash
lottery suggest mega-sena --strategy kabbalistic --full-name "YOUR NAME" --topic "PROSPERITY"
```
Check for "🫨 Seismic Resonance" in the evidence panel.
