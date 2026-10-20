# 02 — Statistical Analysis Reference (every method + exact math)

Notation: a **combination** / winning line is a sorted set of numbers
`c = {n1 < n2 < … < nk}` from a game with pool `1..M`, pick `k`. "History" =
the ordered list of past draws; most analyses take a configurable **range**
(previous 2/3/5/10/20/30/50/100/… or a custom date range).

Every statistics screen shares 3 behaviors:
1. **Range selector** — which past draws to analyze.
2. **Position selector** — which of the k columns participate.
3. **Column drill-down** — click a column value to get its Actual / Average / Now skips.

---

## Skips — the backbone concept (used everywhere)

For any pattern/value tracked over the draw history:
- **Actual Skips** — the sequence of gap lengths between successive hits
  (e.g. hit, then 6 misses, then hit → a skip of 6).
- **Average Skips** — mean of the Actual-Skips sequence: `Σ gaps / (#gaps)`.
- **Now Skips** — number of draws since the pattern last hit.

> **Reading rule** (from manual): if `Now Skips > Average Skips`, the pattern is
> "due" (hot to play); if `Now Skips` is near 0, it is "cold" — recently hit,
> not yet due. Worked example (4-odds filter): gaps `5,1,2` → avg `8/3 = 2.67`;
> now-skips `10` ⇒ overdue.

This engine feeds: analysis drill-down, filter auto-parameters, prediction
verification. Build it once as `skips(patternValueOverHistory) → {actual[], avg, now}`.

---

## 1. AC — Arithmetic Complexity  `acTabSheet`
> **✅ Validated (doc 10): exact, 100% (1666/1666).**
- **Measures**: how "non-arithmetic" (irregular) the spacing of a line is.
- **Formula**: take all pairwise positive differences of the k numbers; count the
  **distinct** difference values `d`; then `AC = d − (k − 1)`.
- **Example**: `01 05 09 13 18 26 34` (k=7): distinct diffs = 13 ⇒ `AC = 13 − 6 = 7`.
- **Range**: `AC ∈ [0, C(k,2) − (k−1)]`. Pure arithmetic progression ⇒ AC 0.
  Max for k=5 is 6, k=6 is 10, k=7 is 15. Higher AC = more random/complex.

## 2. Sum family  `sumtabSheet`
- **Sum** = Σ numbers. Ex `5+11+14+15+22+39 = 106`.
- **High Sum / Low Sum** = Σ of high / low numbers (see Low-High for split).
- **Odd Sum / Even Sum** = Σ of odd / even numbers.
- **Prime Sum** = Σ of prime numbers.
- **Root Sum** = digit-sum the total until… (one pass): sum=143 → `1+4+3 = 8`.
- **Unit Number Sum** = Σ of the **second digit** of each number.
  Ex `01 08 14 29 31 42` → `1+8+4+9+1+2 = 25`.
- **First+Second Unit Sum** = Σ first digits + Σ second digits.
  Ex first digits `0+0+1+2+3+4=10`, second `1+8+4+9+1+2=25` ⇒ `35`.

## 3. Odd-Even
- **Odd/Even Number** lists; **Odd/Even Count**; **Odd/Even Sum**.
- **Modality** = binary pattern, odd=1 even=0, in position order.
  Ex `02 18 19 36 41` = E E O E O ⇒ `00101`.

## 4. Low-High  `bigsmallTabSheet`
- Split pool in half: low = `1..M/2`, high = `M/2+1..M` (Mega Millions 1–70 → low 1–35, high 36–70).
- **Low/High Number** lists, **Low/High Count**, **Low/High Sum**.

## 5. Hot-Cold  `hotcoldTabSheet`
- Over a chosen range, count each number's hits.
- **Hot** = most-hit numbers; **Cold** = least-hit; **Warm** = the rest.
- **Hot/Cold/Warm Same Count** = how many hot/cold/warm numbers repeat from the previous 1 draw.

## 6. Distance  `apartTabSheet`
> **✅ Validated (doc 10), with a correction:** Max/Average/Different Distance are
> computed on the numbers **in draw order** (as drawn), using **absolute** adjacent
> differences — *not* the sorted line. The manual's examples were pre-sorted, which
> hid this. Validated 100% (1666/1666).

Let the drawn sequence be `a_1 … a_k` (draw order). Adjacent absolute diffs
`d_i = |a_{i+1} − a_i|`.
- **First-Last Distance** = `max − min` (sort-invariant). Ex `11..51` ⇒ 40. *(100%)*
- **Max Distance** = `max d_i` over the drawn order. *(100%)*
- **Average Distance** = `(Σ d_i) // (k−1)` — **integer floor division**. *(100%)*
- **Different Distance** = count of **distinct** `d_i`. *(100%)*

## 7. Successive (adjacency runs)
> **✅ Validated (doc 10), with a correction:** "adjacent" means **adjacent in draw
> order**, and a run counts only if its **length ≥ 2** (a lone number ⇒ 0). Sorted
> examples in the manual are a special case. Validated 99.8–100%.

A "successive" run = a maximal block of draw-order-adjacent numbers that are
consecutive integers (differ by 1).
- **Successive** = size of the longest such run, `0` if none has length ≥2. *(99.8%)*
- **Successive Groups** = number of runs of length ≥ 2. *(99.8%)*
- **Odd Successive** = longest run of draw-order-adjacent **odd** numbers (≥2 else 0). *(100%)*
- **Even Successive** = longest run of draw-order-adjacent **even** numbers (≥2 else 0). *(100%)*
- (Filter variant also exposes Successive-2/3/4/5 group counts — see doc 03.)

## 8. Divided (residue groups)  `residueTabSheet`
- Pick divisor `D ∈ [3,10]`. Partition pool by `n mod D` into remainder groups `0..D−1`.
- **Remainder-r Count** = how many of the line fall in group r.
- **Modality** = the concatenated counts. Ex D=3 counts (3,1,1) ⇒ modality `311`.

## 9. Multiple (÷7,5,3,2,1)  `multipleTabSheet`
- Assign each number to the **first** of 7→5→3→2→1 it is a multiple of (priority order; once assigned, not re-added — e.g. 35 is mult-of-7 not mult-of-5).
- **7/5/3/2/1 Multiple** counts; **Modality** = concatenated counts (e.g. `21200`).

## 10. Range (auto-split groups)
- Program auto-splits pool into ~5 contiguous groups (Powerball 1–69 → 01-13,14-26,27-39,40-52,53-69).
- Count hits per group. (The **Range filter**, doc 03, lets you define custom ranges.)

## 11. Prior / Previous Drawing repeats  `beforeTabSheet`
Count how many of the line repeat numbers from earlier draws:
- **Previous 1/2/3/4 Draw** = repeats vs exactly that single prior draw.
- **Previous 2/3/4/5 Draws** = repeats vs the union of the last N draws.

## 12. Locked Number (co-occurrence)
For a given number, count how many other numbers have co-occurred with it
exactly 0, 1, 2, 3, or ≥4 times across winning lines. (Basis for the Locked filter.)

## 13. Lotto Number Hits & Skips  `TnumstatForm`
- **Hits** — every number's total hit count, sorted hot→cold.
- **Skips** — every number's now-skip, sorted.

## 14. Drawings (per-position counts)  `drawingsTabSheet`
Treat each of the k positions as a column; count which numbers appeared in each position.

## 15. Drawings Distributing (trend)  `distributingTabSheet` · `TdrdisForm`
Grid/chart of all winning numbers over time to eyeball number-movement trends
(feeds the manual "Drawings Trend" prediction).

## 16. Base (rollup)
"Over 30 popular analysis methods" surfaced together — the count/sum/distance
metrics above computed for the current line at a glance.

## 17. Multi-number combination analyze  `comanalyzeTabSheet`
Frequency of 1-, 2-, or 3-number combinations (radio `nsRadioButton1/2/3`,
`onlyCheckBox`). Same engine as **Search Past Drawings** (doc 05).

---

## 18. Units Number (digit-level) — the deepest module
Split every number into **first digit** and **second (end/unit) digit**. Then:

**Digit tallies (whole line, both digits):**
- **Units (0)…(9) Count** — count of each digit 0–9 across all first+second digits.
- **S0…S9** — count of each digit restricted to the **second** digit only.

**Derived unit metrics:**
- **High Units Count** — second digits in {6,7,8,9} (counts repeats).
- **Odd Units Count** — distinct odd units {1,3,5,7,9} across both digits (no repeats).
- **Even Units Count** — even units {2,4,6,8}, excluding 0, both digits.
- **Lowest 4 Units Count** — units {1,2,3,4} (exclude 0), no repeats.
- **Count for 1 2 3 Units** — occurrences of units {1,2,3} (with repeats).
- **Successive Paired Units Count** — of the second-digit sequence, count adjacent pairs that form a successive pair {01,12,23,34,45,56,67,78,89}.
- **Successive End Units** — length of the **longest run of consecutive distinct second digits** on the 0–9 line, `0` if the longest run is <2. *(✅ validated 100%)*
- **Pairs Count Odd Units Only** — count numbers whose both digits are odd (11,13,15,…).
- **Pairs Count Even Units Only** — both digits even (02,04,…; 0 counts as even).
- **Pairs Count Odd and Even Units** — numbers with one odd + one even digit.
- **Pairs Count for 1 2 3 Units** — numbers made only of digits {1,2,3} (11,12,13,22,23,31,32,33).
- **InterChangeable Units Count** — numbers whose digit-swap yields a still-valid (≤ M) number, excluding palindromes (11,22,…). Ex for 6/45: 20 such numbers.
- **Unit Number Sum** — Σ second digits (also in Sum family).
- **Unit Number Different Number Count** — distinct second-digit values.
- **Unit Number Group Count** — count of adjacency groups formed by the line's unit digits on the 0–9 line.
- **Same End Units with Last Drawn** — size of the **distinct** second-digit set shared with the previous draw (intersection, no repeats). *(✅ validated 100%)*

> These map 1:1 onto base filters #23–#50 (doc 03) — implement the metrics once,
> reuse as both analysis columns and filter predicates.
>
> **✅ Entire Units module validated 100%** against the app's `UnitsNumbers` table
> (doc 10): all metrics above **plus** the 20 digit-count columns (0–9, S0–S9).
> Counting rules confirmed: High-Units and Count-for-1-2-3 count **with** repeats;
> Odd/Even/Lowest-4 Units count **distinct** digits.
