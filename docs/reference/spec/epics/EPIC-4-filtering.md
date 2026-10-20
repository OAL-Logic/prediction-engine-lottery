# EPIC 4 — Filtering Engine (the core value)

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ EPIC 3 — Ticket Generation](EPIC-3-generation.md) · [EPIC 5 — Wheeling Systems ➡️](EPIC-5-wheeling.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [F4.1 — Filter framework](#f4-1-filter-framework)
- [F4.2 — Base filters (50)](#f4-2-base-filters-50)
- [F4.3 — Advanced filters (19)](#f4-3-advanced-filters-19)
- [F4.4 — Logic combinator (AND / OR / N-of-M)](#f4-4-logic-combinator-and-or-n-of-m)
- [F4.5 — Auto-parameter generation](#f4-5-auto-parameter-generation)
- [F4.6 — Filter assistant + report](#f4-6-filter-assistant-report)
- [F4.7 — Filtering UI](#f4-7-filtering-ui)
  - [Epic 4 exit criteria](#epic-4-exit-criteria)

</details>
<!-- TOC_BLOCK_END -->

**Goal:** 69 filters (50 base + 19 advanced), each a predicate over a combination,
combinable by AND / OR / N-of-M, with auto-parameters from history, an assistant,
and a report. **Verified source:** Doc 03, `../../Documentation/filters-catalog.csv`
(tags + default ranges), Doc 09 §DB-1. **Depends on:** EPIC 2 (metrics — filters
reuse them), EPIC 3 (a pool to filter). **Phase:** 4.

**Features:** F4.1 Filter framework · F4.2 Base filters (50) · F4.3 Advanced filters
(19) · F4.4 Logic combinator · F4.5 Auto-parameters · F4.6 Assistant + report ·
F4.7 Filtering UI.

> **Reuse rule:** a filter's metric is the SAME function EPIC 2 already validated —
> never reimplement. A base filter = `metric(combo,ctx) ∈ [min,max]`. Canonical key
> = `Condition_Tag` (1–69); engine type 1=base, 2/3/4=advanced.

---

## F4.1 — Filter framework
**User stories** — *As the system,* I represent any filter as a predicate with a
stable tag, default range, and position scope, and run a pool through a selected set.
**Acceptance:** AC-F1. **Module:** `core/filters/engine`.

**Chain**
- **S1:** types
  ```ts
  interface Filter { tag:number; type:1|2|3|4; name:string;
    metric(c:Combination, ctx:Ctx): number | number[];
    test(c:Combination, ctx:Ctx): boolean; defaultRange:string; positions:number[] }
  interface RunResult { survivors:Combination[]; report:{tag:number; removed:number}[] }
  run(pool:Combination[], filters:Filter[], logic:Logic, ctx:Ctx): RunResult
  type Logic = {kind:'AND'}|{kind:'OR'}|{kind:'NofM'; n:number; m:number}
  ```
- **S2:** given a pool and one filter Number-Sum `120–210`, survivors all have sum ∈ range; removed ones don't; report count matches.
- **S3:** predicate loop + per-filter removed tally.
- **S4:** `app/usecases/runFilters`.
- **S5:** filter a real generated pool; print survivor + removed counts.
- **Gate:** `{{ACCEPTANCE}}`=AC-F1; report counts reconcile with pool reduction.

---

## F4.2 — Base filters (50)
**User stories** — *As a player,* I enable any of the 50 base filters and set a
min–max range (or auto-fill it).
**Acceptance:** AC-F1, AC-F2. **Module:** `core/filters/base` (registry of 50).

**Chain**
- **S1:** a registry mapping each `Condition_Tag` (1–21, 41–69) to `{name, metric}`,
  where `metric` = the EPIC-2 function. Seed names + default ranges from
  `filters-catalog.csv`.
- **S2:** for each tag, a line passing/failing its range is filtered correctly; spot-check tags 1 (Odd 1-5), 6 (Number Sum), 20 (AC 2-6), 68 (Root Sum 4-17), 69 (First+Second 24-60).
- **S3:** wire each tag to its metric (counts F2.2, sums F2.3, ac F2.4, distance F2.5, successive F2.6, units F2.9, etc.).
- **S4:** appears in the Base Filters panel (F4.7).
- **S5:** enable 6 base filters, run, check report.
- **Gate:** `{{ACCEPTANCE}}`=AC-F1/F2; all 50 tags registered and covered by a test.

---

## F4.3 — Advanced filters (19)
Types 2 (bundle: Adv Number Count, Adv Number Sum, Successive-Number), 3 (set: Range,
Number Groups, Must-Contain, Locked, Divided-by-3..10, Multiple, Delete-History,
Hot-Cold), 4 (special: **Difference Filter**, tag 40).
**Acceptance:** AC-F8, AC-F9. **Module:** `core/filters/advanced`.

**Chain**
- **S1:** `AdvancedFilter { tag; conditions: Condition[]; test(c,ctx) }` — a line
  passes iff it satisfies the filter's combined condition set (each type has its own
  combine rule: bundle = all sub-conditions; set = membership-count in range;
  Must-Contain = superset; Locked = ignore lines lacking the locked number;
  Delete-History = not equal to any historical draw; Difference = adjacent/pairwise
  difference constraint).
- **S2:** Range `01-10 allow 0-1`; Number-Groups `{…} 1-2`; Must-Contain `11 25`;
  Locked `02 + {…} 1-2`; Delete-History drops a line equal to a real draw;
  Difference filter constrains diffs (Doc 03 #19; tag 40).
- **S3:** implement each per Doc 03 §Advanced; Difference Filter documented as
  constraining the set of adjacent/pairwise differences (UI-driven param).
- **S4:** Advanced Filters panel (screens S04, Tadv1/2/3).
- **S5:** run 3 advanced filters on a pool; verify.
- **Gate:** `{{ACCEPTANCE}}`=AC-F8/F9; all 19 tags covered; note Difference Filter is
  the 19th (not in the manual — Doc 03/09).

---

## F4.4 — Logic combinator (AND / OR / N-of-M)
**User stories** — *As a player,* I choose how selected filters combine, including a
fault-tolerant "N-of-M" that guards against over-filtering the winning line.
**Acceptance:** AC-F3, AC-F4, AC-F5. **Module:** `core/filters/logic`.

**Chain**
- **S1:** `combine(results: boolean[], logic): boolean`.
- **S2:** AND = all; OR = any; `NofM{n,m}` = `n ≤ count(true) ≤ m`. Property: `AND ⇒ OR` (survivor set AND ⊆ OR).
- **S3:** implement; validate n≤m and both within [0, #filters].
- **S4:** logic selector in the filtering panel; persists in settings.
- **S5:** run same filters under AND vs "3-5"; compare survivor counts.
- **Gate:** `{{ACCEPTANCE}}`=AC-F3/F4/F5.

---

## F4.5 — Auto-parameter generation
**User stories** — *As a player,* one click fills every base filter's range from the
last N draws (2/3/5/10/20/30/50/current).
**Acceptance:** AC-F2. **Module:** `core/filters/defaults`.

**Chain**
- **S1:** `defaults(filter, history, range): {min,max}` = observed min–max of the filter's metric over the window.
- **S2:** for Odd over a window, range = [minObserved, maxObserved]; matches Doc 03 demo (last-20 Odd → 1-5).
- **S3:** compute metric per draw in window; min/max.
- **S4:** "Generate Default Condition" button (range dropdown).
- **S5:** auto-fill on a fixture; spot-check a few ranges.
- **Gate:** `{{ACCEPTANCE}}`=AC-F2; smaller window ⇒ tighter (or equal) range.

---

## F4.6 — Filter assistant + report
**User stories** — *As a player,* each filter shows a frequency + trend chart to set
its range by eye; after filtering I see per-filter removed counts.
**Acceptance:** AC-F6. **Module:** `ui/FrequencyChart`,`ui/TrendChart` + `RunResult.report`.

**Chain** — S1 `<FilterAssistant filter history/>` (freq + trend) and `<FilterReport report/>`; S2 (E2E) open assistant → chart renders; run → report totals reconcile; S3 charts from F8.4 + report from F4.1; S4 screens S06/S08; S5 drive in app. Gate: AC-F6.

---

## F4.7 — Filtering UI
**User stories** — *As a player,* I pick Base/Advanced filters, set logic and position
scope, click Start Filtering, and the pool is cut with a report.
**Acceptance:** AC-F1..F9. **Module:** `apps/desktop` screens S03/S04/S05/S07/S08.

**Chain** — S1 `<FilteringPanel/>` (tabs Base/Advanced, per-filter condition editor + Assistant, logic selector, position checkboxes, Start Filtering); S2 (E2E) Flow-4 (Doc 06): 924→~60 with report; S3 assemble; S4 wire to `runFilters`; S5 drive Flow-4. Gate: all AC-F*.

### Epic 4 exit criteria
All 69 filters registered + tested; AND/OR/N-of-M correct; auto-params match Doc 03;
Flow-4 verified end-to-end with a reconciling report.

---
> **Next Steps**: [⬅️ EPIC 3 — Ticket Generation](EPIC-3-generation.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [EPIC 5 — Wheeling Systems ➡️](EPIC-5-wheeling.md)
