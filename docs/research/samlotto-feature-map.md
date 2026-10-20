# SamLotto Feature Map & OpenTUI Blueprint 🗺️

This document synthesizes the features extracted from the 64MB disassembly and the SamLotto manual, mapped to the new OpenTUI architecture.

## 🧠 1. Analytical Core: The Harmony Gate

The system employs a 5-tier filtering architecture, implemented via the **Vectorized Protocol** (NumPy) for extreme performance.

### Tier 1: Structural Invariants
- **Odd/Even Count**: Ratio of odd to even numbers (Ideal: 40-60%).
- **Prime Count**: Number of prime balls in the combination.
- **Arithmetic Complexity (AC)**: Measures the non-randomness of differences.
- **High/Low Count**: Balance between the upper and lower halves of the pool.

### Tier 2: Positional & Distance
- **Successive Groups**: Counts contiguous number runs (e.g., 03-04).
- **First-Last Distance (Span)**: Breadth of the combination (Max - Min).
- **Max Adjacency Distance**: Largest gap between sorted numbers.
- **Successive End Units**: Consecutive unit digits (e.g., 1, 2, 3 in 11, 22, 43).

### Tier 3: Algebraic & Modular
- **Number Sum**: Total arithmetic sum compared to probabilistic normal.
- **Root Sum**: Digital root ($1 + (sum - 1) \pmod 9$).
- **Unit Number Sum**: Sum of the last digits.
- **Divided By N**: Modular residue groups (Div-by-3 to Div-by-10).

### Tier 4: Historical & Temporal
- **Last Draw Repeat**: Intersection with the most recent winning line.
- **Historical Duplicate Deletion**: Hard-stop for previously drawn tickets.
- **Hot-Cold Distribution**: Membership counts in frequency-based tiers.
- **Actual Skips**: Predictive timing based on "Average Skip" vs "Now Skip".

### Tier 5: Custom Semantic
- **Must-Contain**: Enforcement of user-defined strategic sets.
- **Locked Numbers**: Mandatory inclusion of specific balls.
- **Include Position**: Restricting specific numbers to specific ball indices.

---

## 🎡 2. Combinatorial Layer: The WRG Engine

Matches the 2200+ formula parity of SamLotto with modern bit-packed optimization.

- **Full Wheeling**: Exhaustive generation of all $C(n, k)$ combinations.
- **Abbreviated Wheeling**: Guaranteed $t$-match if $m$ numbers hit in pool ($t$-if-$m$).
- **Wheel Reduction Guarantee (WRG)**: Proprietary-grade reduction logic that minimizes ticket count while preserving prize guarantees.
- **Key Number Wheels**: Wheels anchored around 1 or more fixed numbers.

---

## 🎨 3. OpenTUI: The Next-Gen Cockpit

Building a high-fidelity terminal experience that surpasses the Windows legacy.

### The Command Palette
- **Fuzzy Search**: Instantly find and toggle any of the 100+ filters.
- **Keyboard-First**: Rapid configuration via hotkeys (e.g., `Ctrl+F` for filter search).

### The Wheel Matrix Visualizer
- **Coverage Heatmap**: Using ASCII block characters (`█`, `▒`, `░`) to show combinatorial density and gaps.
- **Interactive Grid**: Select pairs of numbers to see their mutual coverage across the wheel.

### The Oracle's Retina (Spatial Cartography)
- **3D Correlation Map**: ANSI-based spatial rendering of number relationships in a dodecahedron space.
- **Confidence Saliency**: Visualizing "Statistical Fog" using color gradients and braille patterns.

### Narrative Stream
- **Living Log**: A persistent ticker of the engine's "thoughts" during analysis (e.g., `[SCAN] T3 residues detected... [HINT] 4-if-6 coverage at 92%`).

---
_Formalized 2026-05-13 — Optimized for v10.0 Implementation_
