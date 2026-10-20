# 05 — Prediction, Generation, Optimization & Search

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 04 — Wheeling Systems (covering designs)](04-Wheeling-Systems.md) · [06 — User Flows (end-to-end, with concrete examples) ➡️](06-User-Flows-With-Examples.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [A. Ticket generation modes  `[CHM: Creating tickets]`](#a-ticket-generation-modes-chm-creating-tickets)
  - [A1. Random](#a1-random)
  - [A2. Smart (analysis-depth weighted)](#a2-smart-analysis-depth-weighted)
  - [A3. Positional](#a3-positional)
  - [A4. Full generator](#a4-full-generator)
  - [A5. Wheel generator](#a5-wheel-generator)
  - [Quick pick & favorites](#quick-pick-favorites)
- [B. Prediction  `[CHM: How to Predict]` · `TPredictionForm`](#b-prediction-chm-how-to-predict-tpredictionform)
  - [B1. Formula predictor (automatic)](#b1-formula-predictor-automatic)
  - [B2. Drawings Trend (manual)  `[CHM: How to Use Drawings Trend]`](#b2-drawings-trend-manual-chm-how-to-use-drawings-trend)
  - [B3. Verification  `[CHM: How to Verify]`](#b3-verification-chm-how-to-verify)
- [C. Optimization  `[CHM: Optimize Bet Tickets]` · `TopForm`](#c-optimization-chm-optimize-bet-tickets-topform)
- [D. Search past drawings  `[CHM: Search Past Results]` · `search_list.sl`](#d-search-past-drawings-chm-search-past-results-search-list-sl)
- [E. Check winning  `[CHM: Checking Your Tickets]` · `TcheckForm`](#e-check-winning-chm-checking-your-tickets-tcheckform)

</details>
<!-- TOC_BLOCK_END -->

---

## A. Ticket generation modes  `[CHM: Creating tickets]`

The generation panel (`TnumPanelForm`) offers four categories. The manual's
recommended order for beginners: **wheels > favorites > random**.

### A1. Random
Pure random k-number lines. Manual explicitly says random is for *comparison
only* ("we don't recommend playing random tickets").
- `TrandomForm`: enter how many numbers to random-select.

### A2. Smart (analysis-depth weighted)
Same UI as random, but you pick an **Analysis Depth** (previous-N draws) instead
of "Random Numbers". Lines are biased by historical statistics of that window.
- `depthComboBox` / `deepRzComboBox`, `Analysis Depth` dropdown.

### A3. Positional
Specify the exact candidate set **per position** (`Pick` button per slot →
`[Position] Position 1..8` in the ini). Generates the cross-product of positional
sets. Optionally append a bonus number.

### A4. Full generator
Select a pool on the numbers grid (selected = red). "Full Generator" radio →
generate **all** `C(pool, k)` combinations.

### A5. Wheel generator
Select pool → "Wheels Generator" radio → choose a formula → generate the wheel's
lines (see doc 04).

### Quick pick & favorites
- **Quick pick** (`TgetmnuForm`): one-click Hot numbers / Cold numbers / Last-N-draw numbers.
- **Favorites**: Save Selected / Load Selected number sets.
- Bonus toggles: `bounposCheckBox`, `ranbouCheckBox`, `bounmaxComboBox`.

---

## B. Prediction  `[CHM: How to Predict]` · `TPredictionForm`

Two prediction philosophies:

### B1. Formula predictor (automatic)
- **Formula** selector: `Formula-1 … Formula-6` (`formulaComboBox`).
- **Algorithm** selector: `algorithmRzComboBox` (algorithm family per formula).
- **Offset**: `OffsetRzComboBox` — shift the analysis window.
- **Depth**: `deepRzComboBox` — how much history feeds the formula.
- **Predict Now** → produces a **recommended number pool** (+ **Prediction Bonus
  Numbers** if the game has a bonus). Result can be pushed into the pick panel
  ("The prediction numbers has been add to the picking number panel").

> **The predictor outputs a POOL, not a single line** (confirmed from the
> `Validation` / `perdiction` DB tables, doc 09). A formula produces a
> **recommended** set (typically ~17–27 numbers) and an **eliminated** set — it
> *narrows the pool* by requiring candidates to pass per-metric conditions
> (Same-Last-Draws, Sum, Odd Count, …). You then wheel/pick your lines from the
> recommended pool. Example (`Validation`): actual `12 15 30 50 65`; recommended
> pool of 20 numbers contained `12 30 50` ⇒ correct-count 3.

> The exact internal math of Formula-1..6 is not documented in the manual (it is
> the app's proprietary "lottery prediction algorithm"). For a rebuild, treat
> each formula as a pluggable strategy over the skips/hot-cold/trend engine, and
> **prove value via the verification harness below** rather than copying.

### B2. Drawings Trend (manual)  `[CHM: How to Use Drawings Trend]`
A number-movement chart with a "Next Drawings" row at the bottom; click the `==`
area to show/hide numbers, then pick all the trend-predicted numbers at once.
Human-in-the-loop prediction driven by the Drawings Distributing chart (doc 02 §15).

### B3. Verification  `[CHM: How to Verify]`
The differentiator: the app **replays** a formula across past draws and records
how accurately it would have predicted them.
- Select a formula → **Verification** → accuracy over the chosen range.
- **Verification Bonus** → accuracy of bonus-number prediction (if applicable).
- Change the past-draw range and re-run.
- Uses **Actual Skips** so you can see each formula's hit/skip pattern.
- The predictor **records its own prediction history** per formula/algorithm.

**Rebuild contract:**
```
predict(formula, algo, {history, offset, depth}) -> {recommended[], eliminated[], bonus[]}
verify(formula, range) -> per-draw {recommendedPool, actual, correctNumbers, correctCount,
                                    poolSize, bonusHits} + rollup hit-rate, skips
// hit-rate = Σ correctCount / Σ (winning numbers) across the verification range
```

---

## C. Optimization  `[CHM: Optimize Bet Tickets]` · `TopForm`

Used **after** wheeling + filtering when too many tickets remain (cost control).
"Reduce the number of bets while playing more numbers." Two strategies:

1. **Same-number reduction** — "the amount of the same X numbers for each
   combination": when multiple tickets share X identical numbers, keep only one
   representative. You can choose which position(s) the shared-count applies to.
2. **Reserve-per-block** — "each of 10 combinations reserved for X tickets":
   from every group of 10 lines, keep X (X ∈ 1–9).

Config keys: `reservedOPCheckGroup`, `fromOPCheckGroup`, `toOPCheckGroup`,
`eachOPCheckGroup`, `searchOPCheckGroup`.

---

## D. Search past drawings  `[CHM: Search Past Results]` · `search_list.sl`

More powerful than single-number hot/cold: search **combinations** of 1, 2, or 3
numbers across history.

- **Range**: Past 50 / 100 / 120 / 260 drawings, all history, or custom date range (`[Search] SearchIndex/From/To`).
- **Search list**: auto-generate all 1-, 2-, or 3-number combinations, manual entry, or load from TXT.
- **Position scoping**: choose which positions to search (bonus excluded by default).
- **Output per combination**: Appear Count, Now Skips, Average Skips, Actual Skips, and the exact list of draws where it occurred.
- **Sort** by Appear Count or Now Skips → identify hot/cold combinations.

**Rebuild contract:**
```
search(combos, {range, positions}) -> [{combo, appearCount, nowSkips, avgSkips, actualSkips[], hitDraws[]}]
```

---

## E. Check winning  `[CHM: Checking Your Tickets]` · `TcheckForm`

- Choose a draw to check against (ensure results are up to date first).
- Match operator: `=`, `>`, `<`, `>=`, `<=`  against a **match count**.
- Bonus-aware: if the game has a bonus, a Bonus checkbox restricts to lines also matching the bonus.
- Matching lines shown in a panel; **save to HTML / TXT / XLS**, or clear.

---
> **Next Steps**: [⬅️ 04 — Wheeling Systems (covering designs)](04-Wheeling-Systems.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [06 — User Flows (end-to-end, with concrete examples) ➡️](06-User-Flows-With-Examples.md)
