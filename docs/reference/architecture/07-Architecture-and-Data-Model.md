# 07 — Architecture & Data Model (structure design)

This documents the app **as it actually is** (a Windows desktop app built with
Embarcadero C++Builder/Delphi VCL + LMD-Tools + DBGridEh, backed by MS Access
`.mdb` + flat files), then gives a clean, technology-neutral **reference
architecture** for a rebuild that "resonates with the app itself."

---

## 1. As-built technology (evidence)
- **UI framework**: VCL forms (`T…Form`), Raize/`Rz*` components (tabs, buttons), `DBGridEh` data grids. `[EXE]`
- **Persistence**: MS Access databases + INI files + flat TXT/binary files. `[DATA]`
  - `Data/LotteryResults_Data.db` (~34 MB) — master results DB for all games.
  - `Data/FilterCatalog_Data.db` (~1.2 MB) — filter presets/definitions.
  - `Drawings/*.Txt` — per-game results, plain text (also mirrored/seeded).
  - `Formula/*.Wheels` — packed wheel formula tables.
  - `*.ini` — settings & current lottery.
- **Network**: online results update (`TupdateForm`), affiliate links, help/blog URLs. `[DATA read2.ini / Current_Set.ini]`
- **Licensing**: edition gate strings in the binary (Free vs Pro). `[EXE]`

---

## 2. Layered reference architecture (for rebuild)

```
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION  (screens in doc 08)                            │
│  Shell/Toolbar · Numbers panel · Statistics tabs · Filters   │
│  panels · Prediction · Optimization · Search · Check-Win     │
├─────────────────────────────────────────────────────────────┤
│ APPLICATION  (use-cases / orchestration)                     │
│  GenerateTickets · RunFilters · BuildWheel · Optimize ·      │
│  Predict · Verify · SearchCombos · CheckWinnings · Manage-   │
│  Drawings · ManageGames                                      │
├─────────────────────────────────────────────────────────────┤
│ DOMAIN  (pure, testable core — no UI, no I/O)                │
│  • Game            • Combination        • SkipsEngine        │
│  • DrawHistory     • StatisticsEngine   • FilterEngine (68)  │
│  • WheelLibrary    • Predictor+Verifier • Optimizer          │
│  • TicketSet       • Searcher           • WinChecker         │
├─────────────────────────────────────────────────────────────┤
│ INFRASTRUCTURE  (I/O adapters)                               │
│  ResultsRepository · GameRepository · FilterPresetRepo ·     │
│  WheelRepo · SettingsStore · OnlineUpdateClient · Exporters  │
│  (TXT/HTML/XLS/print) · Entitlements                         │
└─────────────────────────────────────────────────────────────┘
```

**Design principle that matches the app**: the **domain is a batch pipeline over
combinations**. Everything downstream of "choose game" is:
`generate → predicate-filter → cover(wheel) → reduce(optimize) → evaluate(check)`.
Keep the domain pure so the same engine powers analysis, filters, prediction
verification, and search (they all reduce to *metric-over-history* + *skips*).

---

> ER · sequence · state diagrams of this model and the core flows are in
> [`12-Diagrams.md`](12-Diagrams.md).

## 3. Domain model

```
Game {
  id, name,
  pick k,               // 2..9
  maxNumber M,          // 1..90
  bonus { count, name, maxNumber } | none,
  drawSchedule?         // weekdays (enables Split)
  resultsRef            // -> DrawHistory
}

Draw { date, mains:number[k], bonus:number[bonusCount] }

DrawHistory { draws:Draw[] ordered by date; window(range) -> Draw[] }

Combination { numbers:number[k], bonus?:number[]; tag?:'X'|'' }

TicketSet { lines:Combination[]; dedupe(); sortEachLine(); numbersHistogram(); comboFrequency(size) }

Filter { id,name,kind, metric(combo,ctx)->num|num[], conditions[], test()->bool }

Wheel { k,n,guarantee,variant, letterCombos:number[][], generate(pool), report() }

Prediction { formulaId, algo, offset, depth } -> { numbers[], bonus[] }
Verification { formulaId, range } -> { perDraw[], accuracy, skips }
```

**Context object** passed to every metric/filter (single source of truth):
`ctx = { history, range, positions, M, k, lastDraw }`.

---

## 4. On-disk file formats (reverse-engineered)

### 4.1 Drawing results  `Drawings/<GameFile>.Txt`
```
M/D/YYYY  NN NN NN ... [BB]
3/11/1996 04 05 30 33 41 52
```
- Space-delimited; date is non-padded `M/D/YYYY`; numbers zero-padded 2-digit.
- For games with a bonus, the bonus number is an extra trailing column
  (e.g. Powerball line ends with the powerball value).

### 4.2 Current lottery pointer  `Lottery_Set.ini`
```
[PlayLottery]
LotteryName=Brazil Mega Sena
From=60          ; max number M
Match=6          ; pick k
Bouns=0          ; bonus present? (max)
LotteryFile=BrazilMegaSenaBR660.Txt
BounsCount=0
BounsName=
[SelectForm] Group / State / RecNo   ; last UI selection
```

### 4.3 Per-game + global state  `Current_Set.ini` (root and per-game folder)
Key groups:
- `[LotteryParam]` — DrawingsIndex (row count), window size, formula/algorithm
  indices (`formulaComboBox`, `algorithmRzComboBox`, `OffsetRzComboBox`,
  `deepRzComboBox`), grid fonts/colors (`DBGridEh-*`), `RightCountValue`
  (AND/OR/N-M), prediction labels.
- `[Position] Position 1..8` — positional generator sets.
- `[bounCheckBox]`, `[randomComboBox]`, `[bounsComboBox]` — generation toggles.
- `[Multi-Number Combination of Stat]` — combo-analyze radios.
- `[Search] SearchIndex/From/To`, `[depthComboBox]` — search & depth.
- `[Ramdom]`, `[Select]`, `[AddSelect]` — number selections.

### 4.4 Tickets  `Data/Tickets.Txt` and per-game `Tickets.Txt`
```
04k06k09k24k35k tw 04k06k19k21k23k tw ...
```
- Numbers joined by `k`; each line terminated, lines separated by `tw`
  (line tag rides just before the `tw` separator; `X`/blank tag → doc 01 F4).

### 4.5 Wheels  `Formula/PICK-WHEELSIZE-GUARANTEE-VARIANT.Wheels`
Packed binary letter-combination table (doc 04). **Regenerate, don't copy.**

### 4.6 Search list  `search_list.sl` — persisted combo search set.
### 4.7 Prediction scratch  `Num_Dis_Next.nxt` — "next drawings" trend buffer.
### 4.8 Master DBs  `*.mdb` — Access tables for results/filters (no OLEDB driver
present on this machine; treat as canonical store, mirror to TXT for portability).

---

> **DB-confirmed (doc 09).** The `.mdb` files were read with the pure-Python
> `access_parser`. The master DB (`LotteryResults_Data.db`, 39 tables) holds the
> `Lottery` catalog (**376 rows / 222 distinct games**, schema
> `From=M, Match=k, Bouns, PB_Max`), a **cache table per analysis method**
> (`ACA, Apart, BigSmall, OddEven, SumA, Residue, hotcold, BeforeDrawings,
> BeJoined, UnitsNumbers, DrawingsDistributing[90 number cols],
> ComprehensiveAnalyze[28 base cols], AppearCount…`), and operational tables
> (`Filters, FilterReport, Tickets, CheckWinning, nsSearch, nsStat, Validation,
> perdiction`). Analysis is **materialized** per game, not recomputed per view —
> which is why tab-switching is instant. Full schema + the corrected prediction
> model are in doc 09; catalogs exported to `games-catalog.csv` /
> `filters-catalog.csv`.

## 5. Supported games catalog  `Drawings/*.Txt` (222 distinct games)
Coverage is worldwide; games are identified by a file code embedding pick/max
(e.g. `…BR660` = Brazil 6/60, `…MM570` = Mega Millions 5/70, `PB553` = Powerball
5/53, `…AU745` = Oz Lotto 7/45). Regions represented:
- **North America**: US state lotteries (CA, FL, NY, TX, PA, OH, …), Powerball, Mega Millions, Lotto America, Cash4Life, Lucky-for-Life; Canada (6/49, Lotto Max, provincial).
- **Europe**: EuroMillions, EuroJackpot, UK National/Thunderball/Set-for-Life, Germany, Spain, Poland, Romania, Sweden, Netherlands, Switzerland, Austria, Croatia, Hungary, Greece, Viking.
- **Latin America**: Brazil (Mega-Sena, Quina), Mexico (Melate, Chispazo), Chile, Colombia, Peru, Uruguay, Argentina, Costa Rica, Puerto Rico.
- **Asia-Pacific**: Australia (Powerball, Oz, Tatts, Saturday/Monday/Wed), NZ, Japan (Loto 6/7/Mini), Korea, Taiwan, Hong Kong Mark Six, Singapore/Malaysia Toto & 4D, Philippines, India, China Union Lotto.
- **Africa/ME**: South Africa (Lotto/Powerball/Daily), Ghana, Mauritius, Jamaica, Trinidad, Israel, Lebanon, Turkey, Russia.

Game types span pick-4 dailies, 5/xx, 6/xx, 7/xx, and 4D digit games.

---

## 6. Cross-cutting concerns
- **Entitlements**: capability flags (pick-cap, wheels, filter-count, optimize, predict) — doc 00 matrix.
- **Settings**: layered (global root `Current_Set.ini` + per-game folder override).
- **Charts**: one reusable frequency-bar + trend-line component (used by every stat tab and every filter assistant).
- **Long-running ops**: progress dialog (`TprogresForm`) for generate/filter/verify.
- **Export**: shared exporter interface → TXT / HTML / XLS / printer.
