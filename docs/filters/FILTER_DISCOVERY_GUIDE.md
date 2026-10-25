# Filter Discovery & CLI Inspection Quick Guide 🛡️

The Lottery Engine provides the `lottery docs --filter <unique_id>` command to inspect any of the **109 mathematical filters** across Tiers 1–5 in real time with:
1. **Formal Mathematical Specification**
2. **ASCII Box-Flow & Visual Gauge**
3. **Mermaid Flowchart**
4. **Dynamic Combination Evaluation**

---

## ⚡ Quick Discovery Cheat Sheet

| Purpose | Command |
| :--- | :--- |
| **Browse all filters** | `lottery docs filters` |
| **Browse by Tier** | `lottery docs filters --tier 1` *(1=Structural, 2=Positional, 3=Algebraic, 4=Historical, 5=Custom)* |
| **Inspect single filter** | `lottery docs --filter <unique_id>` |
| **Evaluate specific ticket** | `lottery docs --filter <unique_id> --ticket 4,11,23,35,48,59` |
| **Evaluate for specific game** | `lottery docs --filter <unique_id> --game br/lotofacil --ticket 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15` |
| **Interactive Wizard** | `lottery filter-assistant br/mega-sena` |
| **Run Elimination Funnel** | `lottery filter-funnel br/mega-sena --pool 1,2,3,4,5,6,7,8,9,10,11,12 --filters parity,spread,historical_ac_range` |

---

## 🔬 Representative Filter Examples by Tier

### 1. Tier 1: Structural & Number Theory
- **Arithmetic Complexity (AC)**:
  ```bash
  lottery docs --filter structural_ac_value --ticket 4,11,23,35,48,59
  ```
- **Prime Number Density**:
  ```bash
  lottery docs --filter structural_prime_count --ticket 4,11,23,35,48,59
  ```
- **Parity / Odd-Even Count**:
  ```bash
  lottery docs --filter structural_odd_count --ticket 4,11,23,35,48,59
  ```
- **Birthday Bias Clustering**:
  ```bash
  lottery docs --filter structural_birthday_bias --ticket 4,11,23,35,48,59
  ```

### 2. Tier 2: Positional & Gaps
- **Quadrant Balance (Cartesian Lattice)**:
  ```bash
  lottery docs --filter positional_quadrant_balance --ticket 4,11,23,35,48,59
  ```
- **Sequential Pair Gaps ($x_{i+1} - x_i$)**:
  ```bash
  lottery docs --filter positional_gap_1_2 --ticket 3,18,22,35,41,50
  lottery docs --filter positional_gap_2_3 --ticket 3,18,22,35,41,50
  ```
- **Total Span ($x_k - x_1$)**:
  ```bash
  lottery docs --filter positional_first_last_distance --ticket 4,11,23,35,48,59
  ```
- **Median Absolute Deviation (MAD)**:
  ```bash
  lottery docs --filter positional_mad --ticket 4,11,23,35,48,59
  ```

### 3. Tier 3: Algebraic & Modular
- **Magic Square Harmonics (Lo Shu Order-3 M=15)**:
  ```bash
  lottery docs --filter algebraic_magic_square --ticket 4,11,23,35,48,59
  ```
- **Restricted Digit Space (1-2-3)**:
  ```bash
  lottery docs --filter algebraic_digit_space_123 --ticket 4,11,23,35,48,59
  ```
- **Mixed Parity Digits**:
  ```bash
  lottery docs --filter algebraic_mixed_parity_digits --ticket 4,11,23,35,48,59
  ```
- **Digital Root (Modulo 9 Vedic Sum)**:
  ```bash
  lottery docs --filter algebraic_root_sum --ticket 5,12,23,34,45,56
  ```
- **Modulo Multiples Factory (`algebraic_div_by_{n}`)**:
  ```bash
  lottery docs --filter algebraic_div_by_3 --ticket 4,11,23,35,48,59
  lottery docs --filter algebraic_div_by_5 --ticket 4,11,23,35,48,59
  ```

### 4. Tier 4: Historical & Co-occurrences (Dual-Mode Game-Adaptive)
- **Maximum Draw Skip Interval**:
  ```bash
  lottery docs --filter historical_max_skips --ticket 4,11,23,35,48,59
  ```
- **Arithmetic Complexity Range (Game-Adaptive)**:
  ```bash
  lottery docs --filter historical_ac_range --ticket 4,11,23,35,48,59
  ```
- **Co-occurrence Graph Pairs & Triplets**:
  ```bash
  lottery docs --filter historical_common_pair --ticket 10,23,34,42,51,58
  lottery docs --filter historical_common_triplet --ticket 10,23,34,42,51,58
  ```
- **Median Range Across Lotteries**:
  ```bash
  # Mega-Sena (k=6, N=60)
  lottery docs --filter historical_median_range --ticket 4,11,23,35,48,59

  # Lotofácil (k=15, N=25)
  lottery docs --filter historical_median_range --game br/lotofacil --ticket 1,2,5,8,10,12,13,14,15,17,19,20,21,23,25
  ```

### 5. Tier 5: Custom, Banker Locks & Geometry
- **Trevo da Sorte Resonance (Harmonic Core & Anchors)**:
  ```bash
  lottery docs --filter custom_trevo_resonance --ticket 4,11,23,35,48,59
  ```
- **Banker Locks & Blacklists**:
  ```bash
  lottery docs --filter custom_locked_numbers --ticket 7,14,21,28,35,42
  lottery docs --filter custom_exclude_set --ticket 4,11,23,35,48,59
  ```
- **Inner Core & Outer Shell Geometry**:
  ```bash
  lottery docs --filter custom_inner_core --ticket 12,22,28,34,45,55
  lottery docs --filter custom_outer_shell --ticket 3,12,28,34,45,58
  ```

---

## 📖 Complete Encyclopedia

For the comprehensive 1,800+ line reference containing mathematical proofs, ASCII flowcharts, and Mermaid diagrams for every individual filter, consult:
👉 **[`LOTTERY_FILTERS_REFERENCE.md`](LOTTERY_FILTERS_REFERENCE.md)**

