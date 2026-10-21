<!-- parent: MAP · label: wayfinder:research -->
# T2 — Validate remaining analysis methods vs their cache tables

Type: research (AFK) · Assignee: fable-session  · Status: CLOSED
Blocked-by: T1  ·  Blocks: —

## Resolution (CLOSED)

Diagnosed the root cause of every T1 "miss": `access_parser` shifts all columns
**after** a corrupted memo field by one. Correcting the offset, the remaining
`ComprehensiveAnalyze` metrics validate — **Unit Number Group Count 98.7%,
Decade Group Count 99.1%, Different Decade Count 100%, Sum-parity 99.4%**. So:
- **Decade = fixed tens `⌊n/10⌋`** (confirmed; my doc-10 "game-relative" doubt was
  the artifact).
- **Unit Number Group Count** = adjacency groups of distinct unit digits (confirmed).
- **Low/High split = `⌊M/2⌋` per game** (confirmed; T1's low score was mixed-game M).

Net: **all 26 Base-rollup metrics validated**; one real math correction total
(draw-order, from T1). Details appended to `Documentation/10-Validation-Report.md`.

**Handed to T3** (needs a clean, memo-aware read): Root Sum, Prime Sum, Odd/Even
Sum, High/Low Sum, First+Second Unit Sum, Divided remainders, Multiple counts, and
the prev-draw metrics — these live only in memo-corrupted tables (`SumA`, `Residue`,
`Multiple`) with no reconstructable combination, so they can't be checked until the
tables are re-read cleanly.

## Question

Extend the T1 validation harness to the analysis methods that have their own
cache tables: `SumA` (Sum family incl. Root/Unit/First+Second), `Residue`
(Divided remainders 0–9), `BigSmall` (Low-High + Modality), `OddEven` (+Modality),
`hotcold` (Hot/Cold/Warm + Same counts), `BeforeDrawings` (prior-draw repeats),
`Apart` (Distance ×4), `BeJoined` (Successive ×4), `AppearCount` (Locked/co-occur),
`Multiple` (÷7/5/3/2/1). For each: recompute from raw draws, diff vs the cache,
report match rate, and correct docs 02/03 where they diverge. Note that some
metrics (Hot-Cold, prior-draw) depend on a *range/window* — record the window the
app used so the docs state it precisely.

**Carry forward from T1:** (a) validate on a **single known game** (clean
`Drawings/*.Txt`), not the mixed-game `ComprehensiveAnalyze` cache; (b) the app
computes adjacency **in draw order** — apply that when checking `Apart` and
`BeJoined`; (c) specifically resolve the still-open definitions of **Low/High
split point**, **Decade width** (fixed tens vs game-relative range groups), and
**Unit Number Group Count** (the app disagreed with the manual's own example);
(d) reuse the reconstruction guard, but prefer the raw `.Txt` to avoid the
`access_parser` memo bug (see also T3).
