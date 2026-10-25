# Features for Filters

This document outlines the filter capabilities and links to the comprehensive mathematical specification.

> For complete mathematical formulations, ASCII circuit diagrams, Mermaid decision flows, and dynamic ticket walkthroughs for all 5 tiers of filters, see:
> **[[docs/filters/LOTTERY_FILTERS_REFERENCE.md|Lottery Engine: Comprehensive Mathematical Filter Reference]]**

## Core Filter Categories

- **Tier 1 (Structural)**:
  - Odd Count & Even Count
  - Low/High Count & Ratios
  - Arithmetic Complexity (AC Value)
  - Prime & Composite Counts
  - Squares & Fibonacci Sequences
  - Total Digit Sum & Total Unit Sum
  - Decade Distributions (Decades 1 through 6)

- **Tier 2 (Positional & Dispersion)**:
  - Successive Groups & Consecutive Runs
  - Total Span (First-Last Distance)
  - Min & Max Distance Constraints
  - Positional Slot Bounds (Balls 1 through 6)
  - Adjacent Step Gaps (Gaps 1-2 through 5-6)
  - Statistical Dispersion (Variance, Standard Deviation, Mean Absolute Deviation)
  - Central Tendency (Ticket Median)

- **Tier 3 (Algebraic & Modular)**:
  - Dynamic Hypergeometric Number Sums
  - Modular Divisibility (Divided by N for N = 2..20)
  - Mod 3 & Mod 4 Congruence Partitions
  - Digital Root Summation
  - Geometric Mean & Harmonic Mean
  - Selective Sub-Sums (Prime Sum, Even Sum, Odd Sum)

- **Tier 4 (Historical & Temporal)**:
  - Dynamic Historical Sum Range ($\pm 2.8\sigma$)
  - Hot-Cold Frequency Partitioning
  - Previous Contest Repeats ($t-1$)
  - Overdue Skip-Cycle Recovery
  - Recent Winning Draws Deduplication

- **Tier 5 (Custom & Graph-Theoretic)**:
  - Locked Key Numbers (Banker Sets)
  - Blacklist Exclusions
  - Sub-Pool Cluster Coverings
  - Forbidden Anti-Correlated Pairs & Required Pairs
  - Inner Core & Perimeter Shell Spatial Bounds

## Interactive CLI Commands
- `lottery docs filters`: Browse the full 5-tier catalog.
- `lottery docs --filter <unique_id> --ticket <nums>`: View diagrams and dynamic gauge evaluation.
- `lottery filter-funnel <game> --info <unique_id>`: Check individual filter logic during elimination testing.
