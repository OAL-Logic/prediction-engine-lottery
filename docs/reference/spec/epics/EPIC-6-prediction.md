# EPIC 6 — Prediction & Verification

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ EPIC 5 — Wheeling Systems](EPIC-5-wheeling.md) · [EPIC 7 — Tickets Lifecycle · Optimize · Search · Check-Win ➡️](EPIC-7-tickets-lifecycle.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [F6.1 — Predictor (pool output)](#f6-1-predictor-pool-output)
- [F6.2 — Formula strategies (Formula-1 … Formula-6)](#f6-2-formula-strategies-formula-1-formula-6)
- [F6.3 — Verifier (replay → hit-rate)](#f6-3-verifier-replay-hit-rate)
- [F6.4 — Drawings Trend (manual prediction)](#f6-4-drawings-trend-manual-prediction)
- [F6.5 — Prediction UI](#f6-5-prediction-ui)
  - [Epic 6 exit criteria](#epic-6-exit-criteria)

</details>
<!-- TOC_BLOCK_END -->

**Goal:** a predictor that outputs a **recommended number pool** (not a single line)
plus an eliminated set, and an honest **verifier** that replays a formula over
history and measures pool hit-rate. **Verified source:** Doc 05 §B, Doc 09 §2.4
(the pool finding). **Depends on:** EPIC 2 (SkipsEngine, Hot-Cold, trend). **Phase:** 6.

**Features:** F6.1 Predictor · F6.2 Formula strategies (1–6) · F6.3 Verifier ·
F6.4 Drawings Trend · F6.5 Prediction UI.

> **Corrected model (Doc 09 §2.4):** `predict → {recommended[], eliminated[], bonus[]}`
> where `recommended` is ~17–27 numbers; `verify` measures `|recommended ∩ actual|`,
> NOT whether one line won. The internal math of the original Formula-1..6 is
> proprietary and *undocumented* — implement them as pluggable strategies over the
> validated engine and prove value via the verifier. Do not attempt to recover the
> original formulas (out of scope, `_wayfinder/MAP.md`).

---

## F6.1 — Predictor (pool output)
**User stories** — *As a player,* I run a formula and get a recommended pool + an
eliminated set (+ bonus if the game has one), which I can push into the number panel.
**Acceptance:** AC-P1, AC-P2, AC-P5. **Module:** `core/predict/predictor`.

**Chain**
- **S1:** `predict(formula: Formula, ctx: {history, offset, depth}): { recommended:number[]; eliminated:number[]; bonus?:number[] }`. Deterministic (no clock/rng).
- **S2:** same inputs → identical pool (AC-P5); pool ∪ eliminated = full pool 1..M; pool size within a sane band.
- **S3:** a Formula is a strategy: score each number over the window (skips/hot-cold/trend), keep the top band as recommended, rest eliminated.
- **S4:** `app/usecases/predict`; "add to picking panel" pushes `recommended` into the grid (EPIC 3).
- **S5:** run Formula-1 on a fixture; print pool + eliminated.
- **Gate:** `{{ACCEPTANCE}}`=AC-P1/P2/P5; pool is a strict subset, deterministic.

---

## F6.2 — Formula strategies (Formula-1 … Formula-6)
**User stories** — *As a player,* I choose among 6 formulas (+ algorithm, offset,
depth) that weight the history differently.
**Acceptance:** AC-P1. **Module:** `core/predict/formulas` (strategy registry).

**Chain**
- **S1:** `Formula { id:1..6; algorithm:number; score(number, ctx): number }`; registry of 6 distinct scorers (e.g. skip-due, hot-window, trend-slope, gap-regression, co-occurrence, blended).
- **S2:** each formula produces a valid pool; different formulas produce different pools on the same input (diversity check).
- **S3:** implement 6 scorers over the validated engine; `offset` shifts the window, `depth` sizes it.
- **S4:** formula/algorithm/offset/depth selectors on screen S30.
- **S5:** run all 6; show pools differ.
- **Gate:** `{{ACCEPTANCE}}`=AC-P1; each formula tested; **none claim to reproduce the original's internal math** (documented as our own strategies).

---

## F6.3 — Verifier (replay → hit-rate)
**User stories** — *As a player,* I verify a formula over a range and see per-draw
hits and a rollup hit-rate, so I can compare formulas honestly.
**Acceptance:** AC-P3, AC-P4. **Module:** `core/predict/verifier`.

**Chain**
- **S1:** `verify(formula, range): { perDraw: {date, actual, pool, correct: number[], correctCount, poolSize}[]; hitRate: number; bonusHitRate?: number }` where `hitRate = Σ correctCount / Σ winners`.
- **S2:** reproduce the shape of the app's `Validation` table (Doc 09 §2.4): e.g. pool of 20, actual `12 15 30 50 65`, correct `12 30 50`, correctCount 3.
- **S3:** for each draw in range, predict as-of that draw (offset), intersect with actual; roll up.
- **S4:** Verification tab on S30 (+ Verification Bonus for bonus games).
- **S5:** verify a formula over the last 100 fixture draws; print per-draw + hit-rate.
- **Gate:** `{{ACCEPTANCE}}`=AC-P3/P4; correctCount = |pool ∩ actual| exactly; bonus reported separately when present.

---

## F6.4 — Drawings Trend (manual prediction)
**User stories** — *As an analyst,* I read a number-movement chart with a "Next
Drawings" row and pick the trend-predicted numbers into the panel.
**Acceptance:** AC-P2. **Module:** `ui/TrendChart` + F2.11 distributing.

**Chain** — S1 `<DrawingsTrend history/>` with a next-row picker; S2 (E2E) toggle show/hide, pick all → numbers land in panel; S3 build on distributing (F2.11) + TrendChart (F8.4); S4 screen S20j/manual; S5 drive in app. Gate: AC-P2.

---

## F6.5 — Prediction UI
**User stories** — *As a player,* screen S30 lets me predict, push to panel, and
verify (with bonus), changing the past-draw range.
**Acceptance:** AC-P1..P5. **Module:** `apps/desktop` screen S30.

**Chain** — S1 `<PredictionPanel/>` (Predictor + Verification tabs, formula/algorithm/offset/depth, range); S2 (E2E) Flow-6 (Doc 06); S3 assemble; S4 wire to predict/verify use-cases; S5 drive Flow-6. Gate: all AC-P*.

### Epic 6 exit criteria
Predictor outputs a deterministic pool; 6 formulas distinct; verifier reproduces the
`Validation`-table hit-rate semantics; nothing claims to be the original's secret math.

---
> **Next Steps**: [⬅️ EPIC 5 — Wheeling Systems](EPIC-5-wheeling.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [EPIC 7 — Tickets Lifecycle · Optimize · Search · Check-Win ➡️](EPIC-7-tickets-lifecycle.md)
