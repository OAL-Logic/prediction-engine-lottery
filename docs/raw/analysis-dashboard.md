# Analysis Dashboard — Raw Specification
**Document type:** Raw / Living Spec  
**Status:** Active — Phase 1 complete, Phase 2 in progress  
**Last updated:** 2026-04-28  
**Supersedes:** `docs/product/analysis-dashboard-spec.md`, `docs/research/dashboard-insights-and-critique.md`

> **Translation note:** All Portuguese field names have been replaced with their canonical English equivalents throughout this document and the codebase. The full mapping is recorded in [Appendix A: Translation Glossary](#appendix-a-translation-glossary).

---

## TL;DR

LottoLogic is a professional, data-driven companion framework for lottery analysis. It transforms raw historical draw data into actionable insights through visual heatmaps, structural filtering (Primes, Fibonacci, Frame/Center), anomaly detection, and combinatorial multi-game coverage strategies. It bridges the gap between **Nerd Mode** (pure statistical analysis) and **Chaos Mode** (esoteric seeding strategies).

---

## 1. Product Philosophy: Beyond the Winner's Fallacy

Unlike traditional tools that simply track occurrence counts, LottoLogic focuses on **Anomaly Detection** and actively guards users against the Gambler's Fallacy.

**Probability vs. Reality**  
Instead of just showing that a pattern occurred 50 times, the engine calculates the **Standard Deviation (Z-Score)**. We highlight patterns that occur significantly more or less than mathematically expected. The question is never "how often did this happen?" — it is "is this happening at a rate different from random chance?"

**Historical Maximum Delay Context**  
Just because a number is "overdue" does not mean it is statistically "due" to hit. We compare every number's current delay against its all-time historical maximum delay to give users a calibrated **Reality Check**. A number at delay-47 means very little if its all-time record delay is 85.

**The Insight Layer Principle**  
Every data surface in the product leads with a synthesized insight card rather than a raw table. Users should not have to scroll through 100 patterns to find the outlier — the dashboard surfaces the outlier automatically and explains why it matters.

---

## 2. Data Visualization & Grid Management

The core of the visual interface is the **Dynamic Draw Grid**, allowing users to visualize numbers in different spatial contexts to identify geometric and distributional patterns.

### 2.1 Grid Layouts

| Layout | Description | Best For |
|---|---|---|
| **Standard (5×5)** | Traditional 25-number view | Lotofácil analysis |
| **Quadrant View** | Board divided into four sectors | Cluster density analysis |
| **Row-of-10 View** | Reconfigured linear grid | Mega-Sena streak detection |
| **Sparse Grid (6×10)** | Full Mega-Sena board | Heatmap overlay, void analysis |

### 2.2 Heatmap Modes

Toggle-able color overlays applied directly to the grid:

- **Hot** — numbers in the top frequency percentile (bold yellow / deep orange)
- **Cold** — numbers in the bottom frequency percentile (blue / muted)
- **Overdue** — numbers with the highest current delay (glowing red)
- **Void** — rows or columns with no hit in the last *N* draws, Mega-Sena specific (dark gray)

All heatmaps update in real time when the **Search Window** (see §4.2) is changed.

---

## 3. Statistical Engine

The engine calculates structural metrics for every draw to detect and flag statistically anomalous combinations. All metrics are derived from `DrawRules` in the game adapter — no values are hardcoded per game.

### 3.1 Core Metrics

| Metric | Description |
|---|---|
| **Sum** | Total value of all drawn numbers. We track the 70% probability band and flag combinations outside it. |
| **Prime Count** | Count of prime numbers in the draw (2, 3, 5, 7, 11 …). |
| **Fibonacci Count** | Count of numbers belonging to the Fibonacci sequence. |
| **Parity** | Balance of Even vs. Odd numbers (e.g., `6 Even / 9 Odd`). |
| **Frame** | Numbers on the outer edges of the lottery board. |
| **Center** | Numbers in the internal block of the board. |
| **Row Pattern** | String identifier representing the distribution of numbers across rows (e.g., `3-3-3-3-3`). |
| **Column Pattern** | String identifier for column-level distribution. |
| **Rarity Score** | Historical frequency of a specific row/column distribution (e.g., "occurred 52 times out of 3,400 draws"). |

===========================================================================
[ DRAW: 3669 - Date YYYY-MM-DD ]
===========================================================================
G R I D                                      STATISTICS (VAL)
===========================================================================
 (Row)                                       [Odds]            ->   07
 [  4 ] > [ .. ][ 02 ][ 03 ][ 04 ][ 05 ]     [Evens]           ->   08
 [  3 ] > [ .. ][ .. ][ 08 ][ 09 ][ 10 ]     [Primes]          ->   06
 [  3 ] > [ 11 ][ 12 ][ .. ][ .. ][ 15 ]     [Fibonacci]       ->   04
 [  2 ] > [ 16 ][ 17 ][ .. ][ .. ][ .. ]     [Multiples of 3]  ->   05
 [  3 ] > [ .. ][ 22 ][ 23 ][ 24 ][ .. ]     [Frame]           ->   11
--------------------------------------       [Center]          ->   04
  (Col) : [  2 ][  4 ][  3 ][  3 ][  3 ]     [Repeated]        ->   10
                                             [Magic]           ->   02
                                             [SUM]             ->  181
===========================================================================

This carachteristcs (Row Count, Col Count, Odds, Evens, Primes, Fibonacci, Multiple of 3, Multiple of 2, Frame, Center, Repeated from Previous Draw, Magic, Sum ) must be saved on persistent storage, whether a database or json file.

### 3.2 Integrity Gate

Every "predictive" output is gated by a **chi-squared significance test** (p < 0.05). A metric is surfaced as a signal only when it departs from the uniform-random baseline at statistical significance. The gate status is always visible to the user — the p-value is never hidden.

---

## 4. Advanced Analytics & Anomaly Detection

Multi-dimensional analysis of how numbers, rows, and columns behave over time and space.

### 4.1 Delay (Lag) Tracker

Tracks consecutive draws of absence for individual elements. Three sub-trackers:

- **Number Delay** — ranked list of numbers by current delay (e.g., `#20: 5 draws absent`)
- **Row Delay** — measures the absence of entire rows
- **Column Delay** — same metric applied to columns

Each delay entry is always paired with its **Historical Maximum Delay** so users can contextualize the current value against the game's own record. This directly prevents the Gambler's Fallacy interpretation.

### 4.2 Search Window (Recency Filter)

A "Search Last *X* Draws" input that limits the analysis window. Preset options: 10, 50, 100, 500, All-time. All charts and tables respond instantly to window changes, allowing users to detect short-term "regime changes" (statistical hot streaks or cold spells) in the data.

### 4.3 Cycle Analysis

Tracks how many draws it takes for 100% of the game's valid numbers to appear at least once after a cycle reset.

- **Lotofácil cycle:** typically closes in 4–6 draws (15 numbers drawn from 25 — fast, predictable)
- **Mega-Sena cycle:** can take hundreds of draws to close (6 drawn from 60 — a number can sit absent for 80+ draws)

For Mega-Sena, the dashboard shows a **Cycle Progress Bar** — a percentage of the total number pool that has appeared since the current cycle started. A plain list of missing numbers is too overwhelming for the sparse-grid case; the bar gives instant orientation.

### 4.4 Void Analysis (Sparse-Grid Games)

In sparse-grid games (~10% of numbers drawn per draw), it is more informative to highlight "dead zones" than individual hot numbers. Void Analysis marks:

- **Row Voids** — rows with no hit in the last *N* draws
- **Column Voids** — columns with no hit in the last *N* draws
- **Sector Voids** — 3×3 or 2×2 quadrant sectors with no hit in the last *N* draws

---

## 5. Spatial & Structural Analysis

Breaks the lottery board into logical sub-groups to analyze weight distribution across the grid.

### 5.1 Frame vs. Center

For the standard 5×5 board (Lotofácil):

- **Frame** — the 16 numbers on the outer edge
- **Center** — the 9 numbers in the internal block

The dashboard tracks the Frame/Center split across every draw and surfaces the typical ratio (e.g., `11 Frame / 4 Center`) alongside the combination being evaluated.

### 5.2 Ticket Division (Halves)

Analyzes drawn numbers by their **Horizontal Half** (top vs. bottom) and **Vertical Half** (left vs. right) to detect whether winning numbers cluster in specific board regions. Displayed as a 2×2 tile with draw counts per region.

### 5.3 Quadrants

Splits the board into four zones. The dashboard tracks the distribution of drawn numbers across quadrants (e.g., `3 | 3 | 3 | 6`). Useful for spotting sectors that are systematically over- or under-represented.

### 5.4 Row-of-10 Pattern View

A specialized grid reconfiguration (2×10 + 1×5) used to detect linear streaks invisible in the standard 5×5 layout. Each cell displays both frequency and delay.

---

## 6. Multi-Game Coverage Framework (Wheeling)

The framework prioritizes **combinatorial coverage** over expensive single large bets.

### 6.1 Concept

Instead of playing one high-cost ticket (e.g., 18 numbers), the user plays a set of standard tickets (e.g., 5 games of 15 numbers) to cover a larger pool of "hot" candidates. Total spend is lower; coverage of potential winning subsets is higher.

### 6.2 Optimization Method

Uses greedy solvers to ensure maximum coverage with minimal ticket overlap, based on Steiner Systems / Covering Designs. The solver lives in `engine/wheels/` as a zero-dependency module, importable as a standalone PyPI package.

### 6.3 Prize Guarantees

Explicitly optimizes for **"n if m" guarantees** (e.g., "Guarantee 14 matches if 15 of my pool are drawn"). Lower capital requirement with higher statistical efficiency for mid-tier prize captures.

### 6.4 Parity-Enforced Generator

Beyond displaying the Even/Odd parity distribution, the product provides a **Generator** that enforces it: combinations are only emitted when they satisfy the historically high-probability parity split. The filter is opt-in and stackable with other constraints (`--parity`, `--sum-range`, `--prime-count`).

---

## 7. Neighbor Analysis (Cluster Tracker)

For sparse-grid games like Mega-Sena, numbers frequently appear in clusters (consecutive or near-consecutive values, e.g., 22 and 23 in the same draw).

The **Neighbor Analysis** table ranks:

- **Pair Frequency** — number pairs drawn together most often (all-time and last *N* draws)
- **Triplet Frequency** — three-number clusters
- **Adjacency Map** — grid overlay where cell color intensity reflects how often a number shares a draw with its neighbors

This is the primary cluster-detection surface for Mega-Sena, replacing the basic quadrant table.

---

## 8. Financial & Prize Dashboard

### 8.1 Prize Estimates

Real-time jackpot and special accumulation display (e.g., holiday special draws), updated at each official draw release.

### 8.2 Prize Tier Breakdown

Detailed table of winners across all prize tiers (Tier 11 through Tier 15 for Lotofácil; corresponding tiers for other games):

- Individual payout value per tier
- Total winner count per tier
- Total prize pool distributed

### 8.3 Location Data

City/State data for where winning tickets were sold, enabling regional trend analysis.

---

## 9. Visual Board Map (`lottery map` CLI)

Console-rendered grid for immediate spatial insight without the full UI:

- **Frequency Heatmap** — color-coded numbers (Hot = bold yellow, Cold = blue)
- **Delay Tracker** — draws since last appearance shown in brackets `[N]` on the board
- **Trend Summary** — real-time top 5 hottest and top 5 most overdue numbers

---

## 10. Strategy & Comparison Tools

| Feature | Description |
|---|---|
| **Saved Draw Comparison** | Compare user's saved/virtual bets against actual draw results |
| **Spreadsheet Export** | Export historical data to `.xlsx` for external analysis |
| **Draw Navigator** | Sequential browser to page through previous draws chronologically |
| **Cross-Platform Sync** | Saved patterns and custom filters sync instantly across mobile and web |
| **Alert Triggers** | User-defined push notifications (e.g., "Notify me when number 15 reaches a delay of 10 draws") |

---

## 11. Technical Architecture & Mandates

| Mandate | Detail |
|---|---|
| **English First** | All code, variables, and documentation use English standard terms (Frame, Center, Sum, Delay, Draw, Tier, Pattern, Cycle). No Portuguese in the codebase. |
| **Integrity Gate** | All "predictive" outputs are gated by chi-squared significance tests. P-value is always surfaced. |
| **Adapter as Source of Truth** | All game rules and number ranges are derived from `DrawRules` in game adapters. Nothing hardcoded. |
| **Dependency-Light Engine** | Engine core stays lean. `engine/wheels/` is zero-dependency to support standalone PyPI distribution. |
| **Chi² Gate Everywhere** | Every predictive surface gates on chi² p-value AND empirical capture rate from `lottery backtest`. |
| **Distinguish EV from P(win)** | Anti-popular and game-selector are EV claims (always real). Hot/cold are P(win) claims (real only when chi² rejects uniformity). |

---

## 12. Continuous Improvement Roadmap

This is the living improvement roadmap, organized by phase. Checked items are shipped.

### Phase 1 — Foundation ✅ Complete

- [x] Dynamic Draw Grid with three layout modes
- [x] Frequency heatmap (hot/cold)
- [x] Core metrics: Sum, Prime Count, Fibonacci Count, Parity, Frame/Center
- [x] Delay Tracker (number-level)
- [x] Row/Column Pattern display and Rarity Score
- [x] `lottery map` CLI board renderer
- [x] Prize Tier Breakdown display
- [x] Draw Navigator (sequential browse)

### Phase 2 — Anomaly Detection & Integrity 🔄 In Progress

- [ ] Z-Score overlay on all frequency metrics (standard deviation vs. expected)
- [ ] Historical Maximum Delay column on all Delay Tracker tables
- [ ] Chi-squared p-value badge visible on every statistical claim
- [ ] Search Window (Recency Filter) — 10 / 50 / 100 / 500 / All-time preset buttons
- [ ] Cycle Progress Bar for sparse-grid games (Mega-Sena)
- [ ] Void Analysis: row/column/sector dead zones
- [ ] Automated Insights Ribbon — top-of-tab summary card ("Pattern `3-3-3-3-3` is over-performing by 12% in the last 10 draws")

### Phase 3 — Advanced Spatial & Coverage ⏳ Planned

- [ ] Quadrant Heatmap overlay on the 6×10 Mega-Sena grid
- [ ] Ticket Division (horizontal/vertical halves) analysis
- [ ] Frame vs. Center split tracker
- [ ] Row-of-10 Pattern specialized view
- [ ] Neighbor Analysis (pair and triplet frequency cluster table)
- [ ] Adjacency Map grid overlay
- [ ] Parity-Enforced Generator (`--parity` constraint on `lottery suggest`)
- [ ] `lottery check <game> <numbers>` ticket evaluator command

### Phase 4 — Coverage & Multi-Game Tools ⏳ Planned

- [ ] Wheeling engine promotion: `engine/wheels/` as standalone zero-dep module
- [ ] Full Wheel, Key Wheel, and Abbreviated Wheel generators
- [ ] Wheel evaluator (prize guarantee calculator)
- [ ] LJCR JSON export for wheel configurations
- [ ] `--pool` / `--key` / `--filters` flags on `lottery suggest`
- [ ] Savings calculator: single large ticket vs. wheeled coverage set

### Phase 5 — UX & Sync ⏳ Planned

- [ ] Cross-platform saved-filter sync (mobile ↔ web)
- [ ] Alert triggers for delay thresholds (push notification system)
- [ ] Spreadsheet export (`.xlsx`) for historical data
- [ ] Draw Comparison view (virtual bets vs. actual draw)
- [ ] Dynamic Bell Curve overlay on Sum Range (Gaussian visualization for Mega-Sena)
- [ ] Summary Cards replacing text-heavy tables across all tabs

### Phase 6 — Test Coverage & Tech Debt ⏳ Planned

- [ ] Backfill unit tests for all 9 Sprint 1.3 strategies + `BaseStrategy` filter pipeline
- [ ] `engine/modules/sum_range.py` refactor (unblocks 5 downstream features)
- [ ] `pattern.py` refactor (move from empirical sampling to principled computation)
- [ ] Wire `correlation.py` as `copairs` strategy
- [ ] Git release tagging aligned with `docs/versions/` feature batches
- [ ] Resolve `--filters` always-on vs. opt-in semantics (open decision #5)

---

## Appendix A: Translation Glossary

Full mapping of Portuguese source terms to canonical English replacements used throughout the codebase and documentation.

| Portuguese (original) | English (canonical) | Notes |
|---|---|---|
| Concurso | Draw | Plural: "Draws" |
| Faixa | Prize Tier | e.g., "Faixa 11" → "Tier 11". "Band" acceptable for sum ranges. |
| Atraso | Delay | Preferred over "Lag" for UI labels; "Lag" acceptable in code identifiers. |
| Dezena | Number | A drawn ball number. |
| Linha | Row | Grid row. |
| Coluna | Column | Grid column. |
| Moldura | Frame | Outer-edge numbers of the board. |
| Quadro | Center | Inner-block numbers of the board. |
| Divisão Volante | Ticket Division | Horizontal/vertical half split of the board. |
| Quadrante | Quadrant | Board sector (2×2 or 3×3 zone). |
| Padrão | Pattern | Row/column distribution string (e.g., `3-3-3-3-3`). |
| Somas | Sum Range | Total value band; "Sum" for the raw metric. |
| Ciclo | Cycle | Full coverage cycle (all numbers appearing at least once). |
| Pesquisar nos últimos X concursos | Search Last X Draws | Recency filter input label. |
| Pares / Ímpares | Even / Odd | Parity labels. |
| Frequência | Frequency | Occurrence count of a number or pattern. |
| Quantidade | Count | Table column header. |

---

## Appendix B: Open Decisions

| # | Issue | Status |
|---|---|---|
| 1 | `BaseStrategy` filter pipeline is always-on; `--filters` was intended to be opt-in. Decide: invert to `--no-filters` or keep as opt-in. | Open |
| 2 | `docs/versions/v*.md` claim version bumps absent from `pyproject.toml`. Tag git releases or rename to `feature-batch-N`. | Partially resolved (files renamed) |
| 3 | `--full-name` / `--birth-date` defaults produce misleadingly "personalized" tickets. Require explicit flags or label output as "unseeded". | Open |
| 4 | Only one test file (`test_kabbalistic.py`) exists for 9+ strategies. Backfill tests before Sprint 2. | Open |
| 5 | `lottery wizard` referenced in help text but command not registered. Implement or remove the reference. | Open |
| 6 | Positioning conflict between Smart Luck Parity Pack and Absurdity Engine. Resolved via parallel Nerd/Chaos UI tracks in Sprint 4. | Resolved — deferred to Sprint 4 |
