# Analysis Dashboard — Continuous Improvement Plan
**Document type:** Living Plan  
**Status:** Active  
**Last updated:** 2026-04-28  
**Owner:** Prediction Engine Project  
**Source spec:** `docs/raw/analysis-dashboard.md`

---

## Purpose

This document defines the phased improvement strategy for the LottoLogic Analysis Dashboard. It tracks what has been built, what is in progress, and what comes next — organized into discrete, shippable phases so that each session advances the product meaningfully without accumulating runaway scope.

The guiding principle across all phases: **every data surface must earn its screen real estate**. If a feature does not reduce the user's cognitive load or surface a non-obvious insight, it does not ship.

---

## Current State (as of 2026-04-28)

The engine core (Sprint 1 through Sprint 1.3) is fully operational via CLI:

- `lottery fetch <game>` — smart incremental draw fetch
- `lottery analyze <game>` — frequency, deviation, correlation modules
- `lottery suggest <game> --strategy <name>` — any single or ensemble strategy
- `lottery backtest <game>` — honest blind testing with empirical capture rates
- `lottery optimize <game>` — grid search across (strategy × history_limit × temperature)
- `lottery map` — console board heatmap with delay brackets

Frontend (Expo/React Native + Web) and API Gateway (Go) are not yet built. The improvement plan below applies to both the CLI and the eventual UI.

---

## Phase 1 — Foundation ✅ Complete

**Goal:** Ship a working analysis surface that replaces manual spreadsheet work.

| Feature | Status | Notes |
|---|---|---|
| Dynamic Draw Grid (3 layouts) | ✅ Done | Standard 5×5, Quadrant, Row-of-10 |
| Frequency Heatmap (hot/cold) | ✅ Done | Color-coded board map via CLI |
| Core Metrics (Sum, Primes, Fibonacci, Parity, Frame/Center) | ✅ Done | All derived from DrawRules |
| Delay Tracker (number-level) | ✅ Done | Displayed in brackets on board |
| Row/Column Pattern + Rarity Score | ✅ Done | String distributions + historical count |
| Prize Tier Breakdown | ✅ Done | Tiers 11–15 for Lotofácil |
| Draw Navigator | ✅ Done | Sequential draw browsing |

**Key decision locked in Phase 1:** All game rules derived from `DrawRules` adapter — no hardcoded values. This ensures the same code runs for Mega-Sena, Lotofácil, and Powerball without modification.

---

## Phase 2 — Anomaly Detection & Integrity 🔄 In Progress

**Goal:** Transform the dashboard from a "results viewer" into a genuine anomaly detector. Every displayed statistic must answer "is this unusual, and by how much?"

**Why this matters:** The current display of raw counts (e.g., "this pattern appeared 52 times") feeds the Gambler's Fallacy. Phase 2 adds the statistical layer that tells users whether 52 appearances is *expected*, *above average*, or *statistically significant*.

| Feature | Priority | Effort | Notes |
|---|---|---|---|
| Z-Score overlay on all frequency metrics | P0 | Medium | Requires baseline expected-count calculation per metric |
| Historical Maximum Delay column | P0 | Low | Append to existing Delay Tracker table |
| Chi-squared p-value badge | P0 | Low | Gate already exists in engine; surface in UI |
| Search Window (Recency Filter) | P1 | Low | 10 / 50 / 100 / 500 / All-time presets |
| Cycle Progress Bar (Mega-Sena) | P1 | Medium | Percentage of number pool seen since cycle reset |
| Void Analysis (row/column/sector) | P1 | Medium | Dead-zone detection for sparse-grid games |
| Automated Insights Ribbon | P2 | High | Summary card at top of each tab: top outlier + magnitude |

**Definition of done for Phase 2:** A user looking at any frequency, delay, or pattern table can immediately see whether the value is statistically significant — without needing to know what chi-squared means.

---

## Phase 3 — Advanced Spatial & Coverage ⏳ Planned

**Goal:** Give users a full spatial understanding of the board and provide constraint-based generators.

| Feature | Priority | Effort | Notes |
|---|---|---|---|
| Quadrant Heatmap (6×10 Mega-Sena grid) | P0 | Medium | Cell background intensity = frequency |
| Ticket Division (halves analysis) | P1 | Low | 2×2 tile with draw counts per half |
| Frame vs. Center split tracker | P1 | Low | Already computed; surface in UI |
| Row-of-10 Pattern view | P1 | Medium | Alternate grid layout for linear streak detection |
| Neighbor Analysis (pair/triplet frequency) | P1 | Medium | Adjacency map + ranked pair table |
| Parity-Enforced Generator | P0 | Medium | `--parity` flag on `lottery suggest` |
| `lottery check <game> <numbers>` | P0 | Low | Ticket evaluator using existing filter predicates |

**Definition of done for Phase 3:** A user can evaluate any 6-number Mega-Sena ticket against spatial, parity, and neighbor constraints before placing it.

---

## Phase 4 — Coverage & Multi-Game Tools ⏳ Planned

**Goal:** Ship the wheeling system as a first-class, standalone module with prize-guarantee math.

| Feature | Priority | Effort | Notes |
|---|---|---|---|
| `engine/wheels/` promotion to standalone module | P0 | Medium | Zero-dep, PyPI-publishable |
| Full Wheel generator | P0 | Low | All combinations of a pool — educational only |
| Key Wheel generator | P0 | Medium | Guarantees one key number in every ticket |
| Abbreviated Wheel generator | P0 | High | Covering design with stated prize guarantee |
| Wheel evaluator (prize guarantee calculator) | P1 | Medium | "n if m" guarantee display |
| LJCR JSON export | P1 | Low | Machine-readable wheel config |
| `--pool` / `--key` / `--filters` flags | P0 | Low | Surface existing filter pipeline as explicit flags |
| Savings calculator | P2 | Low | Cost comparison: single large ticket vs. wheel |

**Definition of done for Phase 4:** A user can generate a 5-ticket abbreviated wheel guaranteeing a Tier 14 win if 14 of their 20-number pool are drawn — and the system shows the math.

---

## Phase 5 — UX & Sync ⏳ Planned

**Goal:** Make the dashboard something users return to daily, not just before each draw.

| Feature | Priority | Effort | Notes |
|---|---|---|---|
| Cross-platform saved-filter sync | P0 | High | Requires Go gateway + user accounts |
| Alert triggers for delay thresholds | P1 | High | Push notification when delay > user-set threshold |
| Spreadsheet export (`.xlsx`) | P1 | Low | Historical data export for power users |
| Draw Comparison view | P1 | Medium | Virtual bets vs. actual draw side-by-side |
| Dynamic Bell Curve overlay on Sum Range | P1 | Medium | Gaussian curve over sum-band table for Mega-Sena |
| Summary Cards across all tabs | P0 | High | Replace text-heavy tables with insight-first cards |

**Definition of done for Phase 5:** A user on mobile receives a push notification that number 15 has reached delay-10 in Lotofácil, opens the app, and sees a summary card explaining the historical context.

---

## Phase 6 — Test Coverage & Tech Debt ⏳ Planned

**Goal:** Ensure the engine is stable enough to support a public API and multiple contributors.

| Item | Priority | Effort | Notes |
|---|---|---|---|
| Backfill tests for 9 Sprint 1.3 strategies | P0 | Medium | Prerequisite for Sprint 2 |
| Backfill tests for `BaseStrategy` filter pipeline | P0 | Medium | Sum-range, parity, decade breadth filters |
| `sum_range.py` refactor | P0 | Medium | Unblocks 5 downstream features |
| `pattern.py` refactor | P1 | High | Move from empirical sampling to principled computation |
| Wire `correlation.py` as `copairs` strategy | P1 | Low | Module exists; just needs registration |
| Git release tagging | P1 | Low | Align with `docs/versions/feature-batch-N.md` |
| Resolve `--filters` opt-in vs. always-on | P0 | Low | Open decision #1 — decide before Sprint 2 ships |
| Remove or implement `lottery wizard` | P2 | Low | Help text references a non-existent command |

**Definition of done for Phase 6:** `pytest` runs clean on the full strategy suite. `lottery suggest` `--filters` behavior is documented and intentional.

---

## Cross-Cutting Principles (locked)

These constraints apply to every phase and every feature decision:

1. **Chi-squared gate everywhere** — No predictive claim ships without a significance test. P-value is always visible.
2. **Distinguish EV from P(win)** — Anti-popular and game-selector are Expected Value claims (structurally real). Hot/cold are P(win) claims (real only when chi² rejects uniformity).
3. **Adapters are source of truth** — All game parameters come from `DrawRules`. Never hardcode a number range, prize tier, or draw size.
4. **English First** — No Portuguese in code or documentation. Translation Glossary in `docs/raw/analysis-dashboard.md` is authoritative.
5. **Insight before data** — Every screen leads with a synthesized takeaway, not a raw table.
6. **Nerd Mode / Chaos Mode are parallel, not competing** — Statistical rigor and esoteric seeding both ship; the Sprint 4 UI split makes the choice explicit to users.

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-04-25 | Chi-squared gate locked as non-negotiable | Prevents false predictive claims; credibility anchor for OSS audience |
| 2026-04-25 | Adapters as source of truth locked | Enables Powerball, future games without code changes |
| 2026-04-26 | `backtest` and `optimize` added out-of-plan | Provides empirical ground truth for strategy claims |
| 2026-04-27 | Absurdity Engine (9 esoteric strategies) shipped | Fast content generation for Chaos Mode; all labeled `is_predictive: false` |
| 2026-04-28 | Nerd/Chaos parallel positioning confirmed | Resolves branding conflict; Sprint 4 UI split implements the split explicitly |
| 2026-04-28 | All Portuguese terms replaced with English equivalents | Codebase consistency; international contributors; "English First" mandate |
