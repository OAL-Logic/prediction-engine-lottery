# 09 — Database Schema (authoritative, read from the .mdb files)

Read directly from the Access databases with the pure-Python `access_parser`
(no ODBC/OLEDB driver needed). This is the **canonical data model** — it
supersedes inferences in docs 01–08 wherever they differ.

Companion exports in this folder:
- `games-catalog.csv` — 222 distinct games (name + rules + file).
- `filters-catalog.csv` — 69 filters (tag, engine type, caption, default range).

---

## Database 1 — `Data/FilterCatalog_Data.db` (filter catalog / presets)

One user table: **`Filters`** (176 rows = filter defaults, some duplicated with
`Checked` on/off). Columns:

| Column | Meaning |
|---|---|
| `ID` | row id |
| `Condition_Caption` | display name (e.g. "Odd Count") |
| `Condition_Name` | internal name |
| `Condition_Type` | **engine type** 1–4 (see below) |
| `Condition_Tag` | **stable filter id** 1–69 (use this as the canonical key) |
| `Condition` | default parameter, e.g. `1-5`, `96-271` |
| `Condition_Memo` | free text (usually null) |
| `Checked` | selected by default? |
| `delete_Count` | last run's removed count |
| `IncludePos` | positions in scope, e.g. `1 2 3 4 5` |
| `HoldRemove` | keep/remove behavior flag |

### The 4 filter engine types (definitive taxonomy)
| Type | Class | Tags | Members |
|---|---|---|---|
| **1** | **Base** (single scalar range) | 1–21, 41–69 | the 50 base filters |
| **2** | **Advanced bundle** (many scalar conditions) | 22–24 | Adv Number Count · Adv Number Sum · Successive Number Filter |
| **3** | **Advanced set** (number-set membership) | 25–39 | Range · Number Groups · Must Contain · Locked · Divided by 3–10 · Multiple · Delete History · Hot-Cold |
| **4** | **Advanced special** | 40 | **Difference Filter** |

> **New finding**: tag **40 "Difference Filter"** exists in the engine but is
> **not** in the manual's "18 advanced filters" list — so the real advanced count
> is **19** (types 2+3+4 = 3+15+1). Base = **50** (types-1 tags). Total **69**.

### Base-filter default ranges (as shipped)
These are the auto-fill defaults (tuned for a ~5/69 game). Full list in
`filters-catalog.csv`; highlights:

| Tag | Filter | Default |
|---|---|---|
| 1/2 | Odd / Even Count | 1-5 / 0-4 |
| 3/4 | High / Low Count | 0-5 |
| 5 | Prime Count | 0-3 |
| 6 | Number Sum | 96-271 |
| 7 | Average Value | 19-54 |
| 20 | AC | 2-6 |
| 21 | Same Last Drawn | 0-2 |
| 24 | Decade Group Count | 1-4 |
| 51 | InterChangeable Units | 2-5 |
| 68 | Root Sum | 4-17 |
| 69 | First+Second Unit Sum | 24-60 |

---

## Database 2 — `Data/LotteryResults_Data.db` (master data + result caches)

**39 tables.** Three groups: game catalog, per-method analysis caches (one table
per statistics screen — this literally mirrors doc 02), and operational tables.

### 2.1 Game catalog — `Lottery` (376 rows; 222 distinct by name)
| Column | Meaning |
|---|---|
| `From` | **max number M** (pool = 1..From) |
| `Match` | **pick k** |
| `Bouns` | has a bonus? (0/1) |
| `PB_Max` | **bonus pool max** (e.g. Powerball 26) |
| `Groups` | region bucket |
| `Country_State` | jurisdiction |
| `Lottery_Name` | display name |
| `Lottery_File` | results file in `Drawings/` |
| `Des` | note (e.g. "Bonus") |
| `Drawn_Site` / `Play_Online_Url` | source / play links |

Distribution: **227 US · 148 other · 1 Russia**; **261 of 376 have a bonus**.
Most common formats: 5/69+bonus (47), 5/70+bonus (45), 5/48+bonus (24),
5/50+bonus (19), 6/49 (13). This is the exact `Game` domain object (doc 07 §3).

### 2.2 Per-method analysis cache tables (mirror of doc 02)
Each statistics screen persists its computed columns — proving the exact output
schema of every method:

| Table | Method (doc 02) | Key columns |
|---|---|---|
| `ACA` | AC | Date, Drawings, AC |
| `Apart` | Distance | First-Last, Max, Average, Different Distance |
| `BigSmall` | Low-High | Low/High Number, Count, Sum, Modality |
| `OddEven` | Odd-Even | Odd/Even Number, Count, Sum, Modality |
| `SumA` | Sum family | Sum, High/Low/Odd/Even/Prime/Unit/Root/First+Second Sum |
| `Residue` | Divided | Modality + Remainder 0–9 Count |
| `Multiple` | Multiple | (÷7/5/3/2/1 counts) |
| `hotcold` | Hot-Cold | Hot/Cold/Warm Number + Same Counts |
| `BeforeDrawings` | Prior Drawing | Previous 1–4 Draw, Previous 2–5 Draws |
| `BeJoined` | Successive | Successive, Groups, Odd/Even Successive |
| `UnitsNumbers` | Units Number | 38 cols (see 2.5) |
| `DrawingsNumber` | Drawings (per-position) | per-position number columns (see 2.5) |
| `DrawingsDistributing` | Distributing/Trend | **90 columns** (one per number 01–90) × date |
| `NumbersHits` | Number Hits | Numbers, Hits |
| `AppearCount` | Locked Number | Same-Time-Appear = 0,1,2,3,≥4,5,6,≥7 |
| `IntervalA` | (skips/interval) | — |
| `ComprehensiveAnalyze` | **Base** rollup | 28 columns: Odd…Same-End-Units (all base metrics in one row) |

> Design implication: analysis is **materialized** per game (cache tables), not
> recomputed each view. A rebuild can compute on the fly, but this explains the
> app's instant tab switching.

### 2.3 Operational tables
| Table | Purpose | Notable columns |
|---|---|---|
| `Filters` | active filter set for current game | same shape as DB-1 Filters |
| `FilterReport` | per-filter removed counts (1364 rows) | Filters Name, Amount |
| `Tickets` | ticket store | (packed like `Tickets.Txt`) |
| `CheckWinning` | check-win results (401 rows) | Tickets ID, Winning Number Count `"m + b"` |
| `nsSearch` | search-combos results (6887 rows) | AppearCount, NowSkips, Actual/Average Skips, Search |
| `nsStat` | combo frequency (15423 rows) | AppearCount, Number Combination, Frequency |
| `nsSearchDetails` | per-combo hit draws | — |
| `perdiction` | prediction scratch | Date, Drawings, Recommended, Eliminated, per-metric passed counts |
| `Validation` | **prediction verification log** (171 rows) | see below |
| `HitRate` / `winrecord` | accuracy & P/L logs | — |

### 2.4 Prediction is a POOL, not a single line  ⚠ corrects doc 05
`Validation` rows show what "prediction" actually produces:

| Column | Example |
|---|---|
| Verification Drawings | `9/17/2019` |
| Drawings (actual result) | `12 15 30 50 65` |
| **Perdiction Numbers** (recommended pool) | `01 04 06 08 10 12 14 24 27 28 30 32 44 45 46 47 48 49 50 52` |
| Perdiction Numbers Count | `20` |
| Correct Numbers | `12 30 50` |
| Correct Count | `3` |

So a formula outputs a **recommended number pool** (typically ~17–27 numbers)
plus an **eliminated** set; verification measures **how many of the actual
winning numbers fell inside the recommended pool** (a hit-rate over the pool),
not whether a single predicted line won. `perdiction` also records, per metric
(Same-Last-Draws, Sum, Odd Count…), how many combinations passed — i.e. the
predictor is filter-driven: it *reduces the pool*, then you wheel/pick from it.

### 2.5 Tables recovered with Jackcess (were unreadable in `access_parser`)
`access_parser` mishandles memo/overflow columns — it empties the memo field and
**shifts every subsequent column by one**, and throws outright on three tables.
Re-reading with **Jackcess 4.0.5** (Java) returns them cleanly, with intact
`Drawings`/`Tickets` text columns and no shift. The recovered schemas:

- **`Tickets`** — the ticket store's per-line metric cache: `Tag, ID, Tickets`
  (the combination, space-delimited), `Even, Odd, Sum, Root Sum, AC, Average,
  Prime, Low, High, Max Distance, Average Distance`. Confirms the ticket store
  caches base metrics per line.
- **`UnitsNumbers`** — 38 columns: `Date, Drawings`, digit counts `0..9` (both
  digits) and `S0..S9` (second digit only), plus every unit metric
  (`High/Odd/Even/Lowest 4 Units Count, Successive Paired Units, Pairs Count Odd
  and Even / Odd only / Even only / 1 2 3, InterChangeable Units, Count for 1 2 3,
  Successive End Units, The Unit Number Sum, Unit Number Different / Group Count,
  Same End Units with Last Drawn`). ← the ground truth that validated the whole
  Units module 100% (doc 10).
- **`DrawingsNumber`** — per-position layout: `Date, Draings` (sic) + `Position
  1..15` (one drawn number per position; unused positions `null`). This is the
  per-position "Drawings" analysis source (games use as many Position-N columns as
  their pick size).

> **Rebuild note:** for a clean re-implementation, read Access files with Jackcess
> / UCanAccess (JVM) or `mdbtools` — not `access_parser`, whose memo handling
> corrupts text columns. Or better: don't depend on `.mdb` at all; the flat
> `Drawings/*.Txt` are the portable source of truth.

---

## Rebuild takeaways from the real schema
1. **Game** = `{From:M, Match:k, Bouns, PB_Max, region, name, file}` — use exactly these fields.
2. **Filter** canonical key = `Condition_Tag` (1–69) + `Condition_Type` (1–4 engine). Ship the default ranges from `filters-catalog.csv`.
3. **Prediction** = pool-reduction + hit-rate verification, not single-line guessing. Model `predict → {recommended[], eliminated[]}` and `verify → correctCount / poolSize per draw`.
4. **Analysis** output schemas are fixed and known — implement each method to emit exactly the cache-table columns above.
