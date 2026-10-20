# 03 — Filters Reference (68 filters: 50 base + 18 advanced)

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 02 — Statistical Analysis Reference (every method + exact math)](02-Statistical-Analysis-Reference.md) · [04 — Wheeling Systems (covering designs) ➡️](04-Wheeling-Systems.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [How filters work (shared mechanics)](#how-filters-work-shared-mechanics)
- [Base filters (50)](#base-filters-50)
  - [Count filters](#count-filters)
  - [Sum / average](#sum-average)
  - [Successive](#successive)
  - [Extremes / distance](#extremes-distance)
  - [Complexity / repeats](#complexity-repeats)
  - [Decade / group structure](#decade-group-structure)
  - [Unit / digit filters (map to doc 02 §18)](#unit-digit-filters-map-to-doc-02-18)
- [Advanced filters (18)](#advanced-filters-18)
- [Implementation contract (for rebuild)](#implementation-contract-for-rebuild)

</details>
<!-- TOC_BLOCK_END -->

A **filter** is a predicate over a candidate combination. If a line fails a
selected filter, it is removed from the ticket pool. Filters are the app's core
value: "play more numbers, save money."

## How filters work (shared mechanics)
- **Parameter** = an allowed range (min–max) or a target value/set.
- **Auto-generate default condition**: the app statistics the last N draws
  (2/3/5/10/20/30/50 or current) and fills the range from observed values.
  *Smaller range ⇒ tighter filter ⇒ more lines cut ⇒ lower win chance.*
  Recommended: previous 20 or 30.
- **Assistant**: per-filter frequency chart + trend chart to set ranges by eye.
- **Logical condition** across selected filters:
  - `AND` — all must pass.
  - `OR` — any one passes.
  - **`N-of-M`** (e.g. "3-5") — fault-tolerant: pass if between N and M of the
    selected filters match. *Guards against over-filtering out the jackpot line.*
- **Filtering Contain Position**: restrict which positions are evaluated.
- **Filter Report**: per-filter count of lines removed.

Base filters = **one** condition each, auto-fillable. Advanced filters = **many**
conditions each (up to ~10,000), grouped.

> **DB-confirmed taxonomy** (see doc 09). Internally each filter has a stable
> `Condition_Tag` (1–69) and an engine `Condition_Type` (1–4):
> **type 1 = base** (50 filters, tags 1–21 & 41–69), **type 2 = advanced bundle**
> (tags 22–24), **type 3 = advanced set** (tags 25–39), **type 4 = advanced
> special** (tag 40). The database also contains a **19th advanced filter,
> "Difference Filter" (tag 40)**, that the manual omits — so the real advanced
> count is **19**, not 18. Default parameter ranges as shipped are in
> `filters-catalog.csv`.

---

## Base filters (50)

Each: *what it measures → the settable value*. Math for shared concepts is in
doc 02; here we note the filter-specific rule.

> **✅ Validated against the app's own computations (doc 10).** The count/sum
> metrics (Odd, Even, High, Low, Prime, Number Sum, **Average Value = floor
> division**, Unit Number Sum, Unit Number Different, Min, Max, First-Last
> Distance, **AC**) match 100%. The adjacency metrics (Successive ×2, Odd/Even
> Successive, Max/Average/Different Distance) match ≥99.8% **once computed in
> draw order with the "run ≥2 else 0" rule** — see doc 10 for the corrected
> definitions, which also apply to the corresponding statistics in doc 02.

### Count filters
1. **Odd Count** — # odd numbers in line.
2. **Even Count** — # even numbers.
3. **High Count** — # numbers in the high half (e.g. Powerball 35–69).
4. **Low Count** — # numbers in the low half.
5. **Prime Count** — # primes (2,3,5,7,11,…).

### Sum / average
6. **Number Sum** — Σ numbers (ex 106).
7. **Average Value** — Σ/k (integer, ex 106/6=17).
8. **Unit Number Sum** — Σ of second digits.
9. **Unit Number Different Number Count** — distinct second-digit values.

### Successive
10. **Successive** — longest consecutive run length.
11. **Successive Groups** — # of runs (len ≥2).
12. **Odd Successive** — longest run among odds.
13. **Even Successive** — longest run among evens.

### Extremes / distance
14. **Minimum Number** — smallest number allowed.
15. **Maximum Number** — largest number allowed.
16. **First-Last Distance** — `n_k − n_1`.
17. **Max Distance** — largest adjacent gap.
18. **Average Distance** — mean adjacent gap.
19. **Different Distance** — # distinct adjacent gaps.

### Complexity / repeats
20. **AC** — arithmetic complexity value (doc 02 §1).
21. **Same Last Drawn** — # numbers repeating the previous (or a chosen) draw.
22. **Sum Value Even/Odd** — parity of the sum; value is 0 (even) or 1 (odd).

### Decade / group structure
23. **Unit Number Group Count** — # adjacency groups of the line's unit digits.
24. **Decade Group Count** — # adjacency groups of decades (0–9,10–19,…) that are neighbors.
25. **Different Decade Count** — # distinct decades represented.
26. **Same End Units with Last Drawn** — # second-digits repeating the last draw's second-digits.

### Unit / digit filters (map to doc 02 §18)
27. **High Units Count** — second digits ∈ {6,7,8,9} (with repeats).
28. **Odd Units Count** — distinct odd units {1,3,5,7,9}.
29. **Lowest 4 Units Count** — units {1,2,3,4}, no 0, no repeats.
30. **Successive Paired Units Count** — adjacent second-digit successive pairs.
31. **Pairs Count Odd and Even Units** — numbers with one odd + one even digit.
32. **InterChangeable Units Count** — digit-swap stays ≤ M, exclude palindromes.
33. **Count for 1 2 3 Units** — occurrences of units {1,2,3} (with repeats).
34. **Even Units Count** — even units {2,4,6,8}, exclude 0.
35. **Pairs Count Even Units Only** — both digits even (0 allowed).
36. **Pairs Count for 1 2 3 Units** — numbers of only digits {1,2,3}.
37. **Successive End Units** — longest successive run among second digits.
38. **Pairs Count Odd Units Only** — both digits odd.
39–48. **Units (0)…(9) Number Count** — count of each digit 0..9 across both digits.
49. **Root Sum** — digital root of the sum (doc 02 §2).
50. **First and Second Unit Sum** — Σ first digits + Σ second digits.

> Auto-parameter demo: Odd filter, last-20 stats show value 1×5, 2×5, 3×4, 4×2,
> 5×2 draws ⇒ default range `1–5`.

---

## Advanced filters (18)

Advanced filters hold **collections** of conditions and support Add / Replace /
Delete / Delete-All / Edit / Assistant / Save / Load per condition.

1. **Adv Number Count** — bundle of Odd/Even/Prime/High/Low count conditions in one filter.
2. **Adv Number Sum** — bundle of Number Sum + Unit Number Sum conditions.
3. **Successive Number Filter** — set allowed group-counts for:
   - **Successive 2/3/4/5** — # of runs of exactly that length. Ex `02 03 … 30 31` ⇒ Successive-2 groups = 2; `10 11 12` ⇒ Successive-3 groups = 1.
4. **Range Filter** — define arbitrary ranges (01-10, 11-20, …) and how many numbers may fall in each (ex range 01-10 allow 0–1).
5. **Number Groups Filter** — like Range but any custom number set (ex "01 13 21 25 30 …" allow 1–2). More flexible than Range.
6. **Must Contain the Numbers** — listed numbers **must** all appear (ex 11 & 25).
7. **Locked Numbers** — like Number Groups but with a **lock** number: line only participates if it contains the locked number; otherwise it's ignored (passes).
8–15. **Divided by 3 / 4 / 5 / 6 / 7 / 8 / 9 / 10** — for chosen remainder groups, allow a count range (ex ÷3 remainder-0 numbers allow 0–2).
16. **Multiple Filter** — multiples of 7/5/3/2/1 allowed-count ranges (priority assignment as in doc 02 §9).
17. **Delete History Drawings** — remove any candidate that duplicates a historical draw (range adjustable). Deduplication against reality.
18. **Hot-Cold Filter** — customizable hot/cold lists (range-based, editable); set allowed counts (ex hot 1–2, cold 1).
19. **Difference Filter** *(DB tag 40, engine type 4; not in the manual)* — constrains the differences between numbers in a line (a set/pattern constraint over adjacent or pairwise differences). Present in the shipped filter catalog; exact parameter form is UI-driven.

---

## Implementation contract (for rebuild)

```
Filter = {
  id, name, kind: 'base' | 'advanced',
  metric(combo, ctx) -> number | number[]     // ctx = {history, range, positions, M, k, lastDraw}
  conditions: [{min, max} | {set, min, max} | {value}]
  logic within advanced: each condition ORs into a pass-set; filter passes if metric satisfies any
}
Engine.run(pool, selectedFilters, mode) where mode ∈ {AND, OR, {n,m}}:
  for each combo: passes = selectedFilters.map(f => f.test(combo, ctx))
    AND -> all true; OR -> any true; {n,m} -> n <= count(true) <= m
  report[f] += removedCount
```

Auto-params: `defaults(filter, range) = observedMinMax(filter.metric over lastN draws)`.

---
> **Next Steps**: [⬅️ 02 — Statistical Analysis Reference (every method + exact math)](02-Statistical-Analysis-Reference.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [04 — Wheeling Systems (covering designs) ➡️](04-Wheeling-Systems.md)
