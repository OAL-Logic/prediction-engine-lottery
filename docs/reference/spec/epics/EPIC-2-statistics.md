# EPIC 2 — Statistical Analysis Engine

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ EPIC 1 — Games & Drawings (data foundation)](EPIC-1-games-drawings.md) · [EPIC 3 — Ticket Generation ➡️](EPIC-3-generation.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [F2.1 — SkipsEngine (Actual / Average / Now)](#f2-1-skipsengine-actual-average-now)
- [F2.2 — Count metrics (Odd / Even / High / Low / Prime)](#f2-2-count-metrics-odd-even-high-low-prime)
- [F2.3 — Sum family](#f2-3-sum-family)
- [F2.4 — AC (Arithmetic Complexity)](#f2-4-ac-arithmetic-complexity)
- [F2.5 — Distance family (DRAW ORDER)](#f2-5-distance-family-draw-order)
- [F2.6 — Successive family (DRAW ORDER, ≥2 else 0)](#f2-6-successive-family-draw-order-2-else-0)
- [F2.7 — Divided (÷3–10) & Multiple (÷7·5·3·2·1)](#f2-7-divided-3-10-multiple-7-5-3-2-1)
- [F2.8 — Odd-Even / Low-High / Decade](#f2-8-odd-even-low-high-decade)
- [F2.9 — Units module (~30 metrics + 20 digit counts)](#f2-9-units-module-30-metrics-20-digit-counts)
- [F2.10 — Hot-Cold / Prior-Draw / Locked / Number-Hits](#f2-10-hot-cold-prior-draw-locked-number-hits)
- [F2.11 — Drawings (per-position) & Distributing (trend)](#f2-11-drawings-per-position-distributing-trend)
- [F2.12 — Statistics UI (tabbed workspace)](#f2-12-statistics-ui-tabbed-workspace)
  - [Epic 2 exit criteria](#epic-2-exit-criteria)

</details>
<!-- TOC_BLOCK_END -->

**Goal:** every one of the 18 methods computes exactly what the original app
computes — proven at ≥98.7% (most 100%) in `../../Documentation/10-Validation-Report.md`.
**Verified source:** Doc 02 (math), Doc 09 §2.2/2.5 (cache schemas), Doc 10 (proof).
**Depends on:** EPIC 1 (`Draw`, `DrawHistory`, `Ctx`). **Phase:** 2.

> **Non-negotiable validated rules — bake into every prompt and test:**
> 1. **Adjacency (Successive, Distance) is computed in DRAW ORDER, not sorted.**
> 2. **Successive-family runs count only if length ≥ 2, else 0.**
> 3. **Average Value & Average Distance use integer FLOOR division.**
> 4. **Root Sum = a SINGLE digit-sum pass** of the total (257→14), not iterated.
> 5. **Low/High split at ⌊M/2⌋** (low = `1..⌊M/2⌋`).
> 6. **Decade = fixed tens** `⌊n/10⌋`.
> Fixtures are ground truth (from the app's own cache tables) — never invent expected values.

**Features:** F2.1 SkipsEngine · F2.2 Counts · F2.3 Sum family · F2.4 AC ·
F2.5 Distance · F2.6 Successive · F2.7 Divided & Multiple · F2.8 Odd-Even/Low-High/Decade ·
F2.9 Units module · F2.10 Hot-Cold/Prior/Locked/Hits · F2.11 Drawings/Distributing ·
F2.12 Statistics UI.

Common fixtures: `fixtures/drawings/*` + the validation tables. A shared golden
fixture `fixtures/stats-golden.json` (export the app's `ComprehensiveAnalyze` +
`UnitsNumbers` + `SumA`, or use the numbers in Doc 10) drives F2.2–F2.9.

---

## F2.1 — SkipsEngine (Actual / Average / Now)
The backbone (Doc 02 "Skips"); every method's drill-down and the filters/predictor reuse it.

**User stories** — *As an analyst,* for any tracked value I see its Actual Skips
(gap sequence), Average Skips (mean), and Now Skips (since last hit), and a "due"
flag when Now > Average.

**Acceptance:** AC-S7. **Module:** `core/stats/skips`.

**Chain**
- **S1:** `skips(present: boolean[]): { actual: number[]; average: number; now: number }` where `present[i]` = value hit at draw i (chronological). Pure.
- **S2:** fixture from Doc 02 worked example (4-odds: gaps `5,1,2` → avg `8/3`… i.e. `2.67`; now-skips 10 → due). Assert actual gaps, average (float), now, and `due = now > average`.
- **S3:** walk the boolean series; gap = run of falses between trues.
- **S4:** exposed via `analyze()` drill-down (F2.12).
- **S5:** compute skips for "4 odds" over a fixture; match Doc 02.
- **Gate:** `{{FIXTURES}}`=Doc 02 skips example; `{{ACCEPTANCE}}`=AC-S7.

---

## F2.2 — Count metrics (Odd / Even / High / Low / Prime)
**User stories** — *As an analyst,* I see per-draw counts of odd, even, high, low, prime numbers.
**Acceptance:** AC-S1, AC-S2 (validated 100%). **Module:** `core/stats/counts`.

**Chain**
- **S1:** `counts(c: number[], M: number): {odd,even,low,high,prime}`.
- **S2:** For Draw D `04 05 30 33 41 52`, M=60: odd 3, even 3, **low 3** (`1..30`, 30 is low), high 3, prime = count in {primes}. Pull more rows from `stats-golden.json`.
- **S3:** floor split `x<=M//2` = low; primes via sieve/set to 90.
- **S4:** columns in the Base tab.
- **S5:** run over the golden set; assert 100% match.
- **Gate:** `{{FIXTURES}}`=stats-golden; `{{ACCEPTANCE}}`=AC-S1/S2.

---

## F2.3 — Sum family
Sum, High/Low/Odd/Even/Prime Sum, Unit Number Sum, **Root Sum (single pass)**, First+Second Unit Sum, Average Value (floor).
**Acceptance:** AC-S1, AC-S5 (Root Sum). Validated 100% (Doc 10). **Module:** `core/stats/sum`.

**Chain**
- **S1:** `sums(c, M): {sum, highSum, lowSum, oddSum, evenSum, primeSum, unitSum, rootSum, firstSecondUnitSum, average}`.
- **S2:** From `SumA` golden rows (Doc 10): e.g. `02 37 38 46 52 55` → sum 230, highSum 228, lowSum 2, primeSum 39, unitSum 30, rootSum(230)=5, firstSecond 50. Add Root-Sum edge: sum 257 → **14** (single pass), sum 165 → **12** (1+6+5), NOT 3.
- **S3:** `rootSum = digits(sum).reduce(+)` ONCE; `average = Math.floor(sum/k)`; `unitSum = Σ (n%10)`; `firstSecond = Σ(⌊n/10⌋) + Σ(n%10)`.
- **S4:** Sum tab columns.
- **S5:** run over `SumA` golden; assert 100%.
- **Gate:** `{{FIXTURES}}`=SumA golden; `{{ACCEPTANCE}}`=AC-S1/S5. Explicitly test Root Sum ≥10 cases.

---

## F2.4 — AC (Arithmetic Complexity)
**Acceptance:** AC-S3. Validated 100%. **Module:** `core/stats/ac`.
**Chain** — S1 `ac(c): number`; S2 fixture `01 05 09 13 18 26 34`→7, plus golden rows; S3 `#{distinct pairwise positive diffs} − (k−1)`; S4 AC tab; S5 golden match. Gate: AC-S3.

---

## F2.5 — Distance family (DRAW ORDER)
First-Last, Max, Average(floor), Different — **all on the numbers as drawn** (absolute adjacent diffs), except First-Last = max−min.
**Acceptance:** AC-S4. Validated 100% (after the draw-order correction). **Module:** `core/stats/distance`.

**Chain**
- **S1:** `distances(drawn: number[]): {firstLast, max, average, different}` — note the input is the **drawn-order** array, not sorted.
- **S2:** golden `Apart` rows; include a case where sorted ≠ drawn order to prove order-sensitivity (Doc 10 example `[5,12,14,32,38,42]` drawn → Max 30, not 18).
- **S3:** `d_i=|a_{i+1}-a_i|` over drawn order; `average=⌊Σd/(k−1)⌋`; `different=|set(d)|`; `firstLast=max−min`.
- **S4:** Distance tab.
- **S5:** golden match 100%.
- **Gate:** `{{ACCEPTANCE}}`=AC-S4. Test MUST include a non-sorted drawn order.

---

## F2.6 — Successive family (DRAW ORDER, ≥2 else 0)
Successive, Successive Groups, Odd Successive, Even Successive.
**Acceptance:** AC-S6. Validated 99.8–100%. **Module:** `core/stats/successive`.

**Chain**
- **S1:** `successive(drawn: number[]): {longest, groups, oddLongest, evenLongest}`.
- **S2:** golden `BeJoined`/`ComprehensiveAnalyze` rows; assert lone number ⇒ 0; runs use draw-order adjacency (`|a_{i+1}-a_i|==1` for integer-consecutive; parity runs = draw-order-adjacent same-parity).
- **S3:** implement per Doc 02 §7 corrected rules; `0` if longest run <2.
- **S4:** Successive columns.
- **S5:** golden match.
- **Gate:** `{{ACCEPTANCE}}`=AC-S6. Test the ≥2 rule and draw-order explicitly.

---

## F2.7 — Divided (÷3–10) & Multiple (÷7·5·3·2·1)
**Acceptance:** AC-X3. Validated 100% (`Residue`, `Multiple`). **Module:** `core/stats/divided`, `core/stats/multiple`.
**Chain** — S1 `divided(c, D): remainderCounts[0..D-1]` and `multiple(c): {m7,m5,m3,m2,m1}` with **priority assignment** (7→5→3→2→1; once assigned, not re-added, e.g. 35→m7); S2 golden `Residue` (÷3) + `Multiple` rows, incl. Modality; S3 per Doc 02 §8/§9; S4 Divided/Multiple tabs; S5 golden match. Gate: AC-X3.

---

## F2.8 — Odd-Even / Low-High / Decade
Counts+sums+Modality; Decade Group Count & Different Decade Count (**fixed tens**).
**Acceptance:** AC-S2. Validated (Decade via shift-corrected 99–100%). **Module:** `core/stats/groups`.
**Chain** — S1 `oddEven(c)`, `lowHigh(c,M)`, `decades(c): {groupCount, differentCount}`; S2 golden `OddEven`/`BigSmall` + Doc 10 decade cases (`[3,5,14,16]`→differentDecade 2, decadeGroups 1 by fixed tens); S3 modality strings + `⌊n/10⌋` decades; S4 tabs; S5 golden match. Gate: AC-S2.

---

## F2.9 — Units module (~30 metrics + 20 digit counts)
The deepest module — **validated 100%** against `UnitsNumbers` (Doc 10).
**Acceptance:** AC-S9. **Module:** `core/stats/units`.

**Chain**
- **S1:** `units(drawn, M): { digitCount[0..9], secondDigitCount[0..9], highUnits, oddUnits, evenUnits, lowest4Units, count123, successivePairedUnits, pairsOddEven, pairsOddOnly, pairsEvenOnly, pairs123, interchangeable, successiveEndUnits, unitSum, unitDifferent, unitGroupCount, sameEndUnitsWithLast }`.
- **S2:** golden `UnitsNumbers` rows (Doc 10 confirmed 100%). Encode the pinned rules as tests: High-Units & Count-1-2-3 **with repeats**; Odd/Even/Lowest-4 **distinct**; **Successive End Units = longest run of consecutive distinct second-digits, ≥2 else 0**; **Same End Units = distinct intersection with prior draw**; **InterChangeable = swap ≤ M, non-palindrome**; unitGroupCount = adjacency groups of distinct second digits.
- **S3:** implement each per Doc 02 §18 corrected definitions.
- **S4:** Units tab (dense grid).
- **S5:** run over the full `UnitsNumbers` golden (100 rows) → 100% match required.
- **Gate:** `{{ACCEPTANCE}}`=AC-S9; **gate fails if any of the 38 columns < 100% on the golden set.**

---

## F2.10 — Hot-Cold / Prior-Draw / Locked / Number-Hits
**Acceptance:** AC-S7, AC-X3. **Module:** `core/stats/frequency`.
**Chain** — S1 `hotCold(history,range)`, `priorDraw(c,history)`, `locked(number,history)`, `numberHits(history)`; S2 goldens `hotcold`,`BeforeDrawings`,`AppearCount`,`NumbersHits` (record the **window** the app used so ranges are exact); S3 per Doc 02 §5/§11/§12/§13; S4 respective tabs; S5 golden match (note prev-draw metrics need same-game ordering). Gate: AC-S7/X3.

---

## F2.11 — Drawings (per-position) & Distributing (trend)
**Acceptance:** AC-X3. **Module:** `core/stats/position`, `core/stats/distributing`.
**Chain** — S1 `perPosition(history)` (counts per column) and `distributing(history): matrix[number 1..M][draw]`; S2 goldens `DrawingsNumber` (Position 1..k) + `DrawingsDistributing` (90 number-columns); S3 per Doc 02 §14/§15; S4 Drawings tab + trend chart; S5 golden match. Gate: AC-X3.

---

## F2.12 — Statistics UI (tabbed workspace)
Screen **S20** (+ S21). Range selector, position selector, click-a-column → skips drill-down.
**User stories** — *As an analyst,* I pick a range and positions, switch method tabs, and click any column to see its Actual/Average/Now skips inline.
**Acceptance:** AC-S8. **Module:** `apps/desktop` route + `ui` charts.

**Chain**
- **S1:** component contract: `<Statistics game history />` renders tabs (AC, Sum, Odd-Even, Low-High, Distance, Divided, Multiple, Prior, Drawings, Distributing, Units, Combo-analyze) each calling the matching core method through an `analyze` use-case.
- **S2 (E2E):** Playwright — change range prev-30, uncheck a position, switch to Sum tab, click Sum column → skips panel shows.
- **S3:** implement tabs + RangeSelector + PositionSelector + SkipsInspector (F8.4).
- **S4:** wire to `app/usecases/analyze`.
- **S5:** launch app, drive the Flow-2 walkthrough (Doc 06).
- **Gate:** `{{ACCEPTANCE}}`=AC-S8; all core methods reachable; changing range/position rescopes only in-scope computation.

### Epic 2 exit criteria
Every method matches its golden fixtures (Units 100%); the Statistics screen drives
all methods with range/position/skips; `10-Validation-Report.md` fixtures are green
in CI.

---
> **Next Steps**: [⬅️ EPIC 1 — Games & Drawings (data foundation)](EPIC-1-games-drawings.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [EPIC 3 — Ticket Generation ➡️](EPIC-3-generation.md)
