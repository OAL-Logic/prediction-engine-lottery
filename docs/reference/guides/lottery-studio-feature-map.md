# Lottery Studio-feature-map

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ How to Win Brazil Quina](how-to-win-brazil-quina.md) · [Lottery Studio-qt-interface-map ➡️](lottery-studio-qt-interface-map.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [🧠 1. Analytical Core: The Harmony Gate](#1-analytical-core-the-harmony-gate)
  - [Tier 1: Structural Invariants](#tier-1-structural-invariants)
  - [Tier 2: Positional & Distance](#tier-2-positional-distance)
  - [Tier 3: Algebraic & Modular](#tier-3-algebraic-modular)
  - [Tier 4: Historical & Temporal](#tier-4-historical-temporal)
  - [Tier 5: Custom Semantic](#tier-5-custom-semantic)
- [🎡 2. Combinatorial Layer: The WRG Engine](#2-combinatorial-layer-the-wrg-engine)
- [🎨 3. OpenTUI: The Next-Gen Cockpit](#3-opentui-the-next-gen-cockpit)
  - [The Command Palette](#the-command-palette)
  - [The Wheel Matrix Visualizer](#the-wheel-matrix-visualizer)
  - [The Oracle's Retina (Spatial Cartography)](#the-oracle-s-retina-spatial-cartography)
  - [Narrative Stream](#narrative-stream)
- [Clean-Room Python Boilerplate](#clean-room-python-boilerplate)

</details>
<!-- TOC_BLOCK_END -->

# Lottery Studio Feature Map & OpenTUI Blueprint 🗺️

This document synthesizes the features extracted from the 64MB disassembly and the Lottery Studio manual, mapped to the new OpenTUI architecture.

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

Matches the 2200+ formula parity of Lottery Studio with modern bit-packed optimization.

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

---

## Clean-Room Python Boilerplate

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class RangeFilter:
    tag: int
    name: str
    metric_fn: Callable[[list[int]], int]
    min_val: int
    max_val: int

    def evaluate(self, ticket: list[int]) -> bool:
        val = self.metric_fn(ticket)
        return self.min_val <= val <= self.max_val

def evaluate_filter_suite(
    ticket: list[int],
    filters: list[RangeFilter],
    mode: str = "AND",
    n_of_m: tuple[int, int] | None = None,
) -> bool:
    passed = sum(1 for f in filters if f.evaluate(ticket))
    if mode == "AND":
        return passed == len(filters)
    if mode == "OR":
        return passed >= 1
    if n_of_m is not None:
        lo, hi = n_of_m
        return lo <= passed <= hi
    return True
```

---
> **Next Steps**: [⬅️ How to Win Brazil Quina](how-to-win-brazil-quina.md) · [🏠 Reference Hub](../INDEX.md) · [📂 03. Mathematical & Strategy Guides](INDEX.md) · [Lottery Studio-qt-interface-map ➡️](lottery-studio-qt-interface-map.md)
