# Engine Improvements & Analysis Dashboard Documentation

## 1. Analysis Dashboard (`lottery dashboard`)
The dashboard has been upgraded to a 3-panel layout providing a holistic view of the market regime:
- **Top Performers (Z-Score):** Real-time tracking of numbers that are statistically over-performing relative to their expected frequency.
- **Overdue vs Max Delay:** Identifies "cold" numbers and compares their current lag against their historical record (all-time maximum delay).
- **Spatial Voids (NEW):** Analyzes the board for empty rows and columns. Highlighting "Cold Rows" that haven't seen a hit in 3+ draws.
- **Distribution Patterns (NEW):** Displays the current row pattern (e.g., `1-2-1-1-1`) and its empirical rarity over the last 100 draws.
- **Cycle Progress:** Visual progress bar showing how much of the number pool has been "cleared" in the current hit cycle.

## 2. Structural Auditor (`lottery check`)
The `check` command now provides a unified Z-Score for the ticket sum and identifies prime/Fibonacci counts without redundancy. It serves as the primary "Ticket Integrity Gate" for manual play.

## 3. Pattern Module (`engine/modules/patterns.py`)
New spatial utility functions:
- `analyze_voids()`: Generic row/column delay tracker.
- `get_pattern_string()`: Vectorized row-distribution signature generator.

## 4. Constant Improvement Strategy
We follow a **Data-First** mandate: every visual metric must be paired with a statistical significance test (Z-Score or Chi-squared). This prevents the user from following "phantom patterns" that are merely the result of random variance.
