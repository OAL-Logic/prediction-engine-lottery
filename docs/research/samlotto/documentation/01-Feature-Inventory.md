# 01 — Complete Feature Inventory

Every user-visible feature, grouped by subsystem. Evidence keys: `[CHM]` = help
manual topic, `[EXE]` = binary strings (form/label), `[DATA]` = on-disk file.

---

## A. Lottery / Drawings management  `[CHM: Working with Lottery Drawing Files]`

| ID | Feature | Notes / evidence |
|---|---|---|
| A1 | Choose a lottery (open game) | `TLotteryForm`, `Lottery_Set.ini` |
| A2 | Create a new lottery (custom rules) | `TNewLotteryForm` — set pick, max number, bonus |
| A3 | Modify game rules | "Support for modifying lottery game rules" `[CHM Welcome]` |
| A4 | Add a drawing (manual entry) | `TAddInsertForm`, Drawings form → Add |
| A5 | Insert a drawing at a position | `TDrawingsForm` → Insert |
| A6 | Modify a drawing | Drawings form → Modify |
| A7 | Delete a drawing | Drawings form → Delete (confirm) |
| A8 | Import drawings (TXT) | Drawings form → Import |
| A9 | Export / backup drawings | Drawings form → Export |
| A10 | **Split drawings by weekday** | `TSplitForm` — keep e.g. only Thursday draws |
| A11 | **Online update** latest results | `TupdateForm`, "Free daily updates on 150+ lotteries" |
| A12 | 200+ built-in games worldwide | `Drawings/*.Txt` (see game list in doc 07) |
| A13 | Supports pick-2 … pick-9, numbers 1–90 | `[CHM Welcome]` |
| A14 | Bonus / supplementary numbers | `TbounsForm`, per-game `BounsCount`/`BounsName` |

## B. Statistical analysis  `[CHM: Interpreting the Statistical]` · `TstatisticForm`

"Over 10 methods" (actually 18 named). Full math in **doc 02**. Each method:
configurable draw range, position selection, click-a-column drill-down with
Actual/Average/Now Skips.

| ID | Method | Tab `[EXE]` |
|---|---|---|
| B1 | AC (Arithmetic Complexity) | `acTabSheet` |
| B2 | Actual Skip / Average Skip / Now Skip | (column drill-down, all tabs) |
| B3 | Base (30+ popular methods rollup) | — |
| B4 | Distance (first-last / max / avg / different) | `apartTabSheet` |
| B5 | Divided (mod 3–10 remainder groups) | `residueTabSheet` |
| B6 | Drawings Distributing (trend chart) | `distributingTabSheet`, `TdrdisForm` |
| B7 | Drawings (per-position number counts) | `drawingsTabSheet` |
| B8 | Hot-Cold / Warm (+ same-counts) | `hotcoldTabSheet` |
| B9 | Locked Number (co-occurrence) | — |
| B10 | Lotto Number Hits & Skips | `TnumstatForm` |
| B11 | Low-High (+ sums) | `bigsmallTabSheet` |
| B12 | Multiple (÷7,5,3,2,1) | `multipleTabSheet` |
| B13 | Odd-Even (+ sums + modality) | — |
| B14 | Prior / Previous Drawing repeats | `beforeTabSheet` |
| B15 | Range (auto-split groups) | — |
| B16 | Successive (adjacency runs) | — |
| B17 | Sum (many sum variants + root sum) | `sumtabSheet` |
| B18 | Units Number (digit-level, ~30 sub-metrics) | — |
| B19 | Multi-number combination analyze | `comanalyzeTabSheet` |

## C. Ticket generation  `[CHM: Creating and Edit Your Lottery Tickets]`

| ID | Feature | Evidence |
|---|---|---|
| C1 | **Random** numbers | Overview: "random" category |
| C2 | **Smart** (analysis-depth weighted random) | Analysis Depth dropdown (prev-N) |
| C3 | **Positional** — fixed number set per position | `Creating a Positon Number Tickets` |
| C4 | **Full generator** — all C(n,k) of chosen pool | `Creating Full Generate` |
| C5 | **Wheel generator** (choose formula) | `Creating Smart … Wheeling System` |
| C6 | Quick pick: hot / cold / last-N numbers | `How to Quick Picked Numbers`, `TgetmnuForm` |
| C7 | Random-select-K helper | `TrandomForm` |
| C8 | Save / load favorite numbers | `Save and Load Your Own Favorite Number` |
| C9 | Add bonus number to generated lines | `bounCheckBox`, `TbounsForm` |
| C10 | Free edition cap: pick ≤ 10 numbers | `[EXE]` gate |

## D. Filtering  `[CHM: How to Filtering]` · `TbasefiltersForm`, `Tadv1/2/3Form`

| ID | Feature | Evidence |
|---|---|---|
| D1 | 50 base filters | full list in **doc 03** |
| D2 | 18 advanced filters (multi-condition, ≤10,000 conds each) | doc 03 |
| D3 | **Auto-generate** filter params from history | ranges: prev 2/3/5/10/20/30/50/current |
| D4 | Manual params via "…" editor | `TftexteditForm` |
| D5 | **Filter assistant** — frequency + trend charts | `TassistantfilterForm`, `TfrequencyForm` |
| D6 | Logical condition: AND / OR / N-of-M fault tolerance | `RightCountValue` (AND/OR/"3-5") |
| D7 | "Filtering Contain Position" (position-scoped) | position checkboxes |
| D8 | Filter **report** (per-filter cut counts) | `TfilterrepForm` |
| D9 | Save / load / backup filter sets | Save / Load buttons |
| D10 | Delete-history-drawings filter (dedupe vs past draws) | Advanced #17 |

## E. Prediction  `[CHM: How to Predict]` · `TPredictionForm`

| ID | Feature | Evidence |
|---|---|---|
| E1 | Formula predictor (Formula-1 … Formula-6) | `formulaComboBox`, `[EXE]` |
| E2 | Algorithm selector + offset + depth | `algorithmRzComboBox`, `OffsetRzComboBox`, `deepRzComboBox` |
| E3 | "Predict Now" → next-draw numbers (+ bonus) | `Predict Now`, `Prediction Numbers:` |
| E4 | Push prediction into pick panel | "added to the picking number panel" |
| E5 | Manual **Drawings Trend** predictor | `How to Use Drawings Trend` |
| E6 | **Verification** — replay formula over history | `Verification`, `verifyComboBox` |
| E7 | Verification Bonus (bonus-number accuracy) | `Verification Bonus` |
| E8 | Prediction history recording per formula | `[CHM Verify]` |
| E9 | Verification uses Actual Skips | `[CHM]` |

## F. Tickets lifecycle, optimize, search, check  `TopForm`, `TcheckForm`

| ID | Feature | Evidence |
|---|---|---|
| F1 | Ticket store: add / delete / clear | `Editing Tickets` |
| F2 | Sort each line low→high | `Sort: Low to High` |
| F3 | Remove duplicate tickets | "Remove duplicates tickets" |
| F4 | Tag tickets + delete by tag ("X" / blank) | `Delete 'x' Tag Tickets` |
| F5 | Numbers-hit stats across ticket list | `Numbers Hits` |
| F6 | 2- & 3-number combo frequency across tickets | `[CHM Welcome]` |
| F7 | Convert tickets → wheel | "Convert tickets to wheel" |
| F8 | Save/load tickets (native + TXT), format export | `Save Tickets File`, `Formate Export` |
| F9 | Load past drawings into ticket store | `Load Drawings` (prev 10…all) |
| F10 | **Optimization** — 2 reduction strategies | `TopForm`, `Optimization1/2` (doc 05) |
| F11 | **Search past drawings** (1/2/3-number combos) | `Search-Past-Drawings`, `search_list.sl` |
| F12 | **Check winning** (=,>,<,≥,≤ match N, bonus) | `TcheckForm` |
| F13 | Save matches to HTML / TXT / XLS | `Check Winning` |
| F14 | Print tickets (columns, title, date) | `TprintForm` |

## G. Shell / app-level

| ID | Feature | Evidence |
|---|---|---|
| G1 | Toolbar: Lottery · Drawings · Check Win · Search · Prediction · Optimization | `[EXE]`, `[CHM Quick Start]` |
| G2 | Per-game + global settings persistence | `Current_Set.ini` (doc 07) |
| G3 | Window state, grid fonts/colors | `Current_Set.ini` DBGridEh-* |
| G4 | Edition gating (Free vs Pro) | `[EXE]` (doc 00) |
| G5 | Help (CHM), video tutorials, blog, purchase/register | `read2.ini`, `TaboutForm`, `TtryForm` |
| G6 | Progress dialog for long ops | `TprogresForm` |
