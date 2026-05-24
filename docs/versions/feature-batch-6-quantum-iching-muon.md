> 📝 **Renamed 2026-04-28** — was `v9.0.md`. These are *feature batches*, not git releases.
> The `pyproject.toml` version is still `0.1.0`; the v4–v10 numbering reflects internal
> design rounds, not published versions. See `README.md` in this directory.

---

# Version 9.0: The Quantum Syntonization

## Overview
v9.0 is the culmination of our "Absurdity Engine," bridging classical probability with simulated quantum mechanics and ancient divination. We have introduced simulated cosmic variables and deterministic casting logic to push the engine beyond historical confines.

## Key Features

### 1. Quantum Annealing Approximation (`quantum_anneal`)
- **Theory:** Standard statistical models (like frequency analysis) often get trapped in "local minima" (overfitting to what has recently happened). True quantum annealers use quantum tunneling to probability-jump through energy barriers to find global minimums.
- **Technical:** The engine establishes a classical state based on historical frequency, then applies a "Cooling Schedule" where "cold" (low-scoring) numbers have a mathematical probability of tunneling through the barrier to become "hot" candidates.
- **User Impact:** Provides a mathematical escape hatch from historically entrenched patterns.

### 2. Atmospheric Muon Flux (Single-Event Upset Simulation)
- **Theory:** High-energy cosmic rays (muons) bombard the Earth, occasionally striking RAM chips and flipping bits (0 to 1). 
- **Technical:** Implemented directly into the sampling engine (`BaseStrategy.suggest`). Every generated ticket has a small probability of being struck by a simulated muon. If struck, one number in the ticket undergoes a bitwise XOR mutation, ensuring the final ticket contains a truly chaotic, non-deterministic variable.
- **User Impact:** If a ticket is struck, a **[RED] ⚡ ATMOSPHERIC MUON FLUX** alert appears in the CLI.

### 3. I Ching Resonance (`iching`)
- **Theory:** The *Book of Changes* (I Ching) maps 64 hexagrams to universal states. By casting a hexagram for the current draw, we align the mathematical pool with the prevailing "flow" of change.
- **Technical:** Simulates the Yarrow Stalk casting method. Uses the Intentional Seed (hashed date/name) to determine the 6 lines (Old Yin, Young Yang, etc.). Identifies the Primary Hexagram, the Transformed Hexagram, and boosts the numbers associated with the "Changing Lines."
- **User Impact:** Replaces rigid numerology with dynamic, transformative archetypes. The Correlation Evidence panel displays the specific Hexagram names (e.g., "33. Dun (Retreat)").

## Summary of Experts
- **The Statistician:** Quantum Annealing & Tunneling Simulation.
- **The Chaos Analyst:** Atmospheric Muon Flux Bit-Flips.
- **The Esoteric Architect:** I Ching Yarrow Stalk Casting.
