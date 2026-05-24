# LottoLogic — Statistical Analysis Dashboard Specification

**TL;DR:** LottoLogic is a professional data-driven companion framework for lottery analysis. It transforms raw historical data into actionable insights through visual heatmaps, structural filtering (Primes, Fibonacci, Frame/Center), anomaly detection, and combinatorial "Multi-Game" coverage strategies. It is designed to bridge the gap between "Nerd Mode" (pure stats) and "Chaos Mode" (esoteric seeding).

---

## 1. Product Philosophy: Beyond the Winner's Fallacy

Unlike traditional tools that simply track counts, LottoLogic focuses on **Anomaly Detection** and preventing the Gambler's Fallacy.
*   **Probability vs. Reality:** Instead of just showing that a pattern occurred 50 times, the engine calculates the **Standard Deviation (Z-Score)**. We highlight patterns that occur significantly more (or less) than mathematically expected.
*   **Reality Checks:** We provide "Historical Max Delay" context. Just because a number is "overdue" doesn't mean it's "due" to hit; we compare its current delay against its all-time record.

---

## 2. Data Visualization & Grid Management

The core of the visual interface is the **Dynamic Result Grid**, allowing users to visualize numbers in different spatial contexts.
*   **Grid Layouts:**
    *   **Standard (5x5):** The traditional view for 25-number games (e.g., Lotofácil).
    *   **Quadrant View:** Divides the board into sectors to analyze cluster density.
    *   **Row-of-10 View:** Reconfigures the grid to highlight linear streaks (e.g., for Mega-Sena).
*   **Heatmapping:** Toggle-able highlights for **Hot** (high frequency) vs. **Cold** (low frequency) vs. **Overdue** (high delay) numbers.

---

## 3. Advanced Statistical Engine

The engine calculates structural metrics for every draw to detect "Harmonious" combinations:
*   **Summation (Sum):** The total value of all numbers. We track the 70% probability band.
*   **Primes:** Count of prime numbers in a ticket (e.g., 2, 3, 5, 7, 11...).
*   **Fibonacci:** Count of numbers belonging to the Fibonacci sequence.
*   **Parity (Even/Odd):** The balance between Even and Odd numbers.
*   **Grid Positioning:**
    *   **Frame:** Numbers on the outer edges of the lottery board.
    *   **Center:** The internal block of numbers.
*   **Distribution Patterns:**
    *   **Row/Col Patterns:** String identifiers (e.g., `3-3-3-3-3`) representing the distribution of numbers across the board's lines and columns.
    *   **Rarity Meter:** Calculates the historical frequency of specific row/column distributions.

---

## 4. Advanced Analytics & Anomaly Detection

Moving beyond simple result tracking to provide multi-dimensional analysis:
*   **Delay (Lag) Tracker:** Tracks consecutive draws of absence for individual numbers, rows, and columns.
*   **Search Recency:** Ability to limit analysis to the last $X$ draws to spot short-term "regime changes" in the data.
*   **Cycle Analysis:** Tracks how many draws it takes for 100% of the game's numbers to appear at least once.

---

## 5. The Multi-Game Coverage Framework (Wheeling)

The framework prioritizes **Combinatorial Coverage** over expensive single bets.
*   **The Concept:** Instead of playing one large, high-cost ticket (e.g., 18 numbers), the user plays a set of standard tickets (e.g., 5 games of 15 numbers) to cover a larger pool of "Hot" candidates.
*   **Optimization:** Uses greedy solvers to ensure maximum coverage of potential winning subsets with minimal ticket overlap (Steiner Systems / Covering Designs).
*   **Prize Guarantees:** Explicitly optimizes for "n if m" guarantees (e.g., "Guarantee 14 hits if 15 of my pool are drawn"). Lower capital requirement with higher statistical efficiency for mid-tier prize guarantees.

---

## 6. Visual Board Map (`lottery map`)

A console-rendered grid providing immediate spatial insights:
*   **Frequency Heatmap:** Color-coded numbers (Hot = Bold Yellow, Cold = Blue).
*   **Delay (Lag) Tracker:** Displays the number of draws since each number last appeared in brackets `[ ]` directly on the board.
*   **Trend Highlights:** Real-time summary of the Top 5 Hottest and Top 5 Most Overdue numbers.

---

## 7. Technical Architecture & Mandates

*   **English First:** All code, variables, and documentation must use English standard terms (Frame, Center, Sum, Delay, Draw, Tier).
*   **Integrity Gate:** All "Predictive" outputs are gated by chi-squared significance tests.
*   **Source of Truth:** Rules are never hardcoded; they are derived from `DrawRules` in the game adapters, ensuring the logic adapts to any lottery (Mega-Sena, Lotofácil, Powerball).
