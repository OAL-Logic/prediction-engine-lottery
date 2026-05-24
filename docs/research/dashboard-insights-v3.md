# Engine Improvements & Analysis Dashboard Documentation

## 1. Analysis Dashboard (`lottery dashboard`) - V3
The dashboard has been upgraded to a high-fidelity analytical workbench:
- **Structural Harmony:** Real-time tracking of Arithmetic Complexity (AC), Digital Root Sum, and Unit Sum (remainders mod 10).
- **Clusters & Gaps:** Dedicated panel for Successive Groups (adjacent pairs/triplets) and Maximum Gap (largest distance between numbers). Includes a **30-day Gap History Sparkline**.
- **Market Overview:** Consolidated panel showing the latest draw, analytical sum band, and **Row Pattern Rarity** (empirical frequency of the current grid distribution).
- **Spatial Voids:** Identifies "Cold Sectors" on the board that are statistically overdue for a mean-reversion event.

## 2. Advanced Board Analytics (`lottery board`)
Two new powerful views have been added to the board command:
- **Positional Heatmap (`--view heatmap`):** Tracks the exact slot frequencies (e.g. "Where does the 1st number usually land?"). This exposes positional sorting biases in the draw machine.
- **Enhanced Clusters (`--view cluster`):** In addition to Lift pairs and Adjacency, the Cluster view now tracks **Frequent Triplets** over the analysis window, surfacing complex 3-way correlations.

## 3. Advanced Metrics Strategy (`advanced`)
The `advanced` strategy has been refactored to use **Harmonic Harmony Scoring**:
- Instead of a binary pass/fail mask, each candidate combination is assigned a score based on its **Z-Score distance** from historical norms for AC, Root Sum, Unit Sum, Spread, and Clusters.
- **Exponential Decay Mapping:** Scores are mapped using `exp(-Z/2)`, ensuring that only combinations that land in the "Sweet Spot" receive a high predictive weight.
- **Participation Weighting:** Individual numbers are scored by the aggregate harmony of all combinations they participate in.

## 3. Core Mandate: Data-First
We follow a **Data-First** mandate: every visual metric must be paired with a statistical significance test (Z-Score or Chi-squared). This prevents the user from following "phantom patterns" that are merely the result of random variance.
