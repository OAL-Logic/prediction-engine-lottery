# 11 — Acceptance Criteria (black-box, per subsystem)

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 10 — Validation Report (documented formulas vs the app's own computations)](10-Validation-Report.md) · [12 — Diagrams (ER · sequence · state) ➡️](12-Diagrams.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [S1 — Drawings / game management](#s1-drawings-game-management)
- [S2 — Statistics engine  (assert against validated formulas, doc 10)](#s2-statistics-engine-assert-against-validated-formulas-doc-10)
- [S3 — Generation](#s3-generation)
- [S4 — Filtering](#s4-filtering)
- [S5 — Wheeling](#s5-wheeling)
- [S6 — Prediction & verification](#s6-prediction-verification)
- [S7 — Tickets, optimize, search, check](#s7-tickets-optimize-search-check)
- [Cross-cutting](#cross-cutting)

</details>
<!-- TOC_BLOCK_END -->

Testable criteria for a rebuild, in Given/When/Then form. Terms follow
`glossary.md`; formulas are the **validated** ones (doc 10). Where a concrete
number is given it is a fixture you can assert on directly. Each subsystem's suite
is independently runnable.

Fixtures reused below:
- **G6/60** — a pick-6, pool-max-60 game (Brazil Mega-Sena); low = 1–30, high = 31–60.
- **Draw D** = `04 05 30 33 41 52` (drawn order).
- **Draw E** = `03 05 11 14 16` (a pick-5 example).

---

## S1 — Drawings / game management
- **AC-D1** *Open game.* Given the game list, When I open **G6/60**, Then the app loads its `Drawings/*.Txt`, sets pick=6 / pool-max=60, and shows the draw count.
- **AC-D2** *Add draw.* Given an open game, When I add `07/09/2026 = 04 05 30 33 41 52`, Then it appears in the history and the count increments by 1.
- **AC-D3** *Insert/modify/delete.* Given a selected draw, When I insert/modify/delete it and confirm, Then the history reflects exactly that change and persists across reopen.
- **AC-D4** *Split by weekday.* Given a game drawn on multiple weekdays, When I split keeping only Thursday, Then only Thursday draws remain.
- **AC-D5** *Import/export.* Given a `.Txt` in `M/D/YYYY NN NN …` format, When I import it, Then all rows load; When I export, Then the file round-trips byte-equivalently (modulo ordering).
- **AC-D6** *New game.* Given New-Lottery with pick=5, max=50, bonus=1/max=12, Then a new empty game is created with those rules.

## S2 — Statistics engine  (assert against validated formulas, doc 10)
For **Draw D** `04 05 30 33 41 52`:
- **AC-S1** Sum = 165; Average Value = 27 (floor); Odd Count = 3; Even Count = 3.
- **AC-S2** Low = {04,05,30} → Low Count 3; High = {33,41,52} → High Count 3. *(low = `1..⌊M/2⌋` = 1..30, so 30 is low)*
- **AC-S3** AC = `#{distinct pairwise diffs} − 5`.
- **AC-S4** First-Last Distance = 52 − 4 = 48; Max/Average/Different Distance computed on **draw order**, absolute diffs.
- **AC-S5** Root Sum = single digit-sum pass of 165 = 1+6+5 = 12 (**not** 3).
- **AC-S6** Successive / Odd-Successive / Even-Successive count **draw-order-adjacent** runs, value 0 if longest run <2.
- **AC-S7** *Skips.* Given a range and a tracked value, Then Actual/Average/Now Skips match `{gaps[], mean, sinceLast}`; `Now > Average` flags "due".
- **AC-S8** *Range & positions.* Changing the analysis range or unchecking a position changes only the in-scope computation.
- **AC-S9** *Units module.* Every unit metric matches doc 02 §18 (validated 100%): High-Units & Count-for-1-2-3 count **with** repeats; Odd/Even/Lowest-4 count **distinct** digits; Successive End Units = longest distinct-second-digit run (≥2 else 0).

## S3 — Generation
- **AC-G1** *Full.* Given a pool of 12 numbers on G6/60 and Full mode, Then exactly `C(12,6)=924` unique combinations are produced.
- **AC-G2** *Positional.* Given per-position sets, Then output = the cross-product, each line respecting its slot sets.
- **AC-G3** *Wheel.* Given 8 numbers and "pick-6, if-4" wheel, Then exactly 7 lines (see S5).
- **AC-G4** *Quick pick.* Hot/Cold/Last-N picks return numbers consistent with the current Hot-Cold analysis.
- **AC-G5** *Random* produces the requested count of valid `k`-number lines.
- **AC-G6** *Free-edition cap.* Selecting >10 pool numbers is blocked with the "up to 10" message.

## S4 — Filtering
- **AC-F1** *Predicate correctness.* Given the pool and filter **Number Sum = 120–210**, Then every surviving line has sum in `[120,210]` and every removed line does not.
- **AC-F2** *Auto-params.* Given "generate default condition, prev 20", Then each base filter's range equals the observed min–max over the last 20 draws.
- **AC-F3** *AND.* With logic=AND, a line survives iff it passes **all** selected filters.
- **AC-F4** *OR.* With logic=OR, a line survives iff it passes **≥1**.
- **AC-F5** *N-of-M.* With logic="3-5" over 5 filters, a line survives iff 3–5 of them pass.
- **AC-F6** *Report.* The filtering report's per-filter removed counts sum-consistently with the pool reduction.
- **AC-F7** *Position scope.* With "filtering contain position" set, only those positions are evaluated.
- **AC-F8** *Advanced multi-condition.* An advanced filter with several conditions passes a line iff it satisfies the filter's combined condition set.
- **AC-F9** *Delete-history.* The Delete-History filter removes any line equal to a historical draw in range.

## S5 — Wheeling
- **AC-W1** *Full count.* 8 numbers, pick-6, full wheel → 28 lines; 10 → 210; 12 → 924.
- **AC-W2** *Abbreviated guarantee.* 8 numbers, "if any 4 of 6 are among them" → exactly 7 lines, and **for every** 4-subset of the 8 there exists ≥1 line containing all 4.
- **AC-W3** *Instantiation.* Substituting the chosen numbers into the letter map yields the reported lines in order.
- **AC-W4** *Guarantee report.* The stated "if X in pool → Y lines match Z" holds when checked by brute force over all X-subsets.

## S6 — Prediction & verification
- **AC-P1** *Pool output.* Predict returns a **recommended pool** (+ eliminated, + bonus if any), not a single line.
- **AC-P2** *Push to panel.* "Add to picking panel" places the recommended pool into the number grid.
- **AC-P3** *Verification.* Given Formula-n over a range, Then per draw: `correctCount = |recommendedPool ∩ actualWinners|`, and the rollup hit-rate = `Σ correctCount / Σ winners`.
- **AC-P4** *Bonus verify.* For a bonus game, bonus-number accuracy is reported separately.
- **AC-P5** *Determinism.* Same formula + algorithm + offset + depth + history ⇒ identical pool.

## S7 — Tickets, optimize, search, check
- **AC-T1** *Sort/dedupe.* Sort-low→high orders each line ascending; remove-duplicates leaves a set with no repeated line.
- **AC-T2** *Numbers hits.* The per-number histogram sums to `k × (#tickets)`.
- **AC-T3** *Optimize — reserve.* "Each of 10 reserve 3" reduces every block of 10 lines to 3.
- **AC-T4** *Optimize — same-number.* Lines sharing X identical numbers collapse to one representative.
- **AC-T5** *Search.* For a 2-number combo over range R, Appear Count = its occurrences in R and Now Skips = draws since last occurrence; hit-draw list matches.
- **AC-T6** *Check winning.* Given draw D and "≥ 4", Then exactly the lines sharing ≥4 numbers with D are returned; with bonus checked, also matching the bonus.
- **AC-T7** *Export.* Matching tickets export to TXT/HTML/XLS with identical content.

## Cross-cutting
- **AC-X1** *Persistence.* Settings (range, filters, selections, window) survive reopen (per-game + global).
- **AC-X2** *Entitlements.* Free edition blocks: >10 pool, wheels, optimization, prediction — each with its message.
- **AC-X3** *Data fidelity.* Every statistic equals the app's cached value on the validation fixtures (doc 10).

---
> **Next Steps**: [⬅️ 10 — Validation Report (documented formulas vs the app's own computations)](10-Validation-Report.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [12 — Diagrams (ER · sequence · state) ➡️](12-Diagrams.md)
