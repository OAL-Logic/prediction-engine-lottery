# 08 — UI Screen Design & Navigation Map

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 07 — Architecture & Data Model (structure design)](07-Architecture-and-Data-Model.md) · [09 — Database Schema (authoritative, read from the .mdb files) ➡️](09-Database-Schema.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [1. Information architecture](#1-information-architecture)
- [2. Screen catalog (forms)](#2-screen-catalog-forms)
  - [Core workspace](#core-workspace)
  - [Drawings / games](#drawings-games)
  - [Analysis](#analysis)
  - [Prediction / optimize / search / check](#prediction-optimize-search-check)
  - [Output / utility](#output-utility)
- [3. Navigation map (who opens what)](#3-navigation-map-who-opens-what)
- [4. Interaction patterns worth preserving (they define the app's feel)](#4-interaction-patterns-worth-preserving-they-define-the-app-s-feel)
- [5. Recommended rebuild UI structure (technology-neutral)](#5-recommended-rebuild-ui-structure-technology-neutral)
- [6. Screenshots (from the official manual)](#6-screenshots-from-the-official-manual)
  - [Shell & analysis](#shell-analysis)
  - [Filtering](#filtering)
  - [Generation & tickets](#generation-tickets)
  - [Predict · optimize · search · check · drawings](#predict-optimize-search-check-drawings)

</details>
<!-- TOC_BLOCK_END -->

The app's UI **as it actually is**, derived from the real form/panel/tab names in
`studio_app.bin` `[EXE]` and the manual's screenshots/steps `[CHM]`. IDs `S###` are
assigned here for cross-reference.

---

## 1. Information architecture

The window is a **single-document workspace**: one game is "open" at a time, and a
persistent **numbers/ticket workspace** sits center while feature windows open as
dialogs over it. Navigation is **toolbar-driven**, not menu-tree-driven.

```
                    ┌────────────────── TOOLBAR ──────────────────┐
                    │ Lottery │ Drawings │ Statistics │ Prediction │
                    │ Search  │ Optimization │ Check Win │ Help     │
                    └──────────────────────────────────────────────┘
   ┌──────────────────────────── MAIN WORKSPACE ─────────────────────────────┐
   │  LEFT: Numbers grid (1..M, click=select/red)   │  RIGHT: Ticket store    │
   │  + generation radios (Full / Wheels / Position  │  (grid of lines, menu:  │
   │  / Random) + Pick buttons + Bonus toggles       │  sort/dedupe/export/    │
   │  --------------------------------------------    │  print/hits/optimize)   │
   │  SETUP PANEL (tabs): Base Filters | Advanced     │                         │
   │  Filters | logical condition | Start Filtering   │  [Generate Tickets >>]  │
   └──────────────────────────────────────────────────────────────────────────┘
```

Persisted layout: `Width/Height`, `GenActivePageIndex`, grid fonts/colors in
`Current_Set.ini`.

---

## 2. Screen catalog (forms)

### Core workspace
| ID | Form `[EXE]` | Purpose | Key controls |
|---|---|---|---|
| S01 | (main) `TnumPanelForm` | Numbers grid + generation | number buttons, Full/Wheels/Position/Random radios, Pick, Generate Tickets |
| S02 | Ticket store (right panel) | Hold/edit generated lines | grid, right-click menu (doc 01 F) |
| S03 | `TbasefiltersForm` | 50 base filters | filter checklist, condition `…`, Assistant, Generate Default Condition |
| S04 | `Tadv1Form` / `Tadv2Form` / `Tadv3Form` | Advanced filter editors (3 groups) | Add/Replace/Delete/Edit/Assistant/Save/Load |
| S05 | `TfilteringForm` | Run filtering + logical condition | AND/OR/N-of-M, Start Filtering |
| S06 | `TassistantfilterForm` + `TfrequencyForm` | Filter assistant charts | frequency + trend chart |
| S07 | `TftexteditForm` | Text edit of filter values | multiline condition editor |
| S08 | `TfilterrepForm` | Filtering report | per-filter removed counts |

### Drawings / games
| ID | Form | Purpose |
|---|---|---|
| S10 | `TLotteryForm` | Choose game (+ New button) |
| S11 | `TNewLotteryForm` | Create/define a new game (pick, max, bonus) |
| S12 | `TDrawingsForm` | Edit results (Add/Insert/Modify/Delete/Import/Export/Split/Update) |
| S13 | `TAddInsertForm` | Add / insert a single draw (date + numbers) |
| S14 | `TSplitForm` | Split draws by weekday |
| S15 | `TupdateForm` | Online update results |
| S16 | `TbounsForm` | Bonus-number picker |

### Analysis
| ID | Form / Tab | Purpose |
|---|---|---|
| S20 | `TstatisticForm` | Statistics workspace (tabbed) |
| S20a | `acTabSheet` | AC |
| S20b | `sumtabSheet` | Sum family |
| S20c | `hotcoldTabSheet` | Hot-Cold |
| S20d | `bigsmallTabSheet` | Low-High |
| S20e | `apartTabSheet` | Distance |
| S20f | `residueTabSheet` | Divided |
| S20g | `multipleTabSheet` | Multiple |
| S20h | `beforeTabSheet` | Prior drawing |
| S20i | `drawingsTabSheet` | Drawings (per-position) |
| S20j | `distributingTabSheet` + `TdrdisForm` | Drawings distributing / trend |
| S20k | `comanalyzeTabSheet` | Multi-number combination analyze |
| S21 | `TnumstatForm` | Lotto Number Hits & Skips |

### Prediction / optimize / search / check
| ID | Form | Purpose |
|---|---|---|
| S30 | `TPredictionForm` | Predictor + Verification (formula/algorithm/offset/depth) |
| S31 | `TopForm` | Optimization (2 strategies) |
| S32 | Search Past Drawings | 1/2/3-number combo search |
| S33 | `TcheckForm` | Check winning (=,>,<,≥,≤, bonus) |

### Output / utility
| ID | Form | Purpose |
|---|---|---|
| S40 | `TprintForm` | Print tickets (columns, title, date) |
| S41 | `TexportForm` / `TforexpForm` | Export / format export |
| S42 | `TrandomForm` | Random-select-K helper |
| S43 | `TgetmnuForm` | Quick-pick dropdown (hot/cold/last-N) |
| S44 | `TgotoForm` / `TshowForm` | Navigate / show helpers |
| S45 | `TprogresForm` | Progress dialog (long ops) |
| S46 | `TaboutForm` / `TtryForm` | About / trial-nag / register |
| S47 | `TMessageForm` | Message/confirm dialogs |

---

## 3. Navigation map (who opens what)

```
Toolbar
├─ Lottery ─────▶ S10 Select Game ──▶ (New) S11 Define Game
├─ Drawings ────▶ S12 Edit Drawings ─┬▶ S13 Add/Insert
│                                     ├▶ S14 Split
│                                     ├▶ S15 Online Update
│                                     └▶ Import/Export (S41)
├─ Statistics ──▶ S20 Statistics ────▶ tabs S20a..k, drill-down skips
│                                     └▶ S21 Number Hits/Skips
├─ Prediction ──▶ S30 Predictor / Verification ──▶ (push numbers to S01)
├─ Search ──────▶ S32 Search Past Drawings
├─ Optimization ▶ S31 Optimize (operates on S02 ticket store)
├─ Check Win ───▶ S33 Check Winning ──▶ export (S41)
└─ Help ────────▶ S46 About / CHM / video / purchase

Main workspace
├─ Numbers grid (S01) ─ Pick ▶ S43 quick pick · S16 bonus · S42 random
├─ Generate Tickets ▶ fills S02 ticket store
├─ Setup panel ▶ S03 Base / S04 Advanced ▶ S06 Assistant · S07 text edit
│                 └ Start Filtering (S05) ▶ S08 Report
└─ Ticket store (S02) ▶ menu: sort/dedupe/hits/convert-to-wheel/save/print(S40)
```

---

## 4. Interaction patterns worth preserving (they define the app's feel)
1. **Select-on-grid = red** — direct manipulation of the number pool.
2. **"Generate Default Condition"** — one click turns history into filter params; the single biggest usability win. Reproduce it.
3. **Assistant charts everywhere** — every filter and stat has a frequency + trend chart to set parameters by eye.
4. **Fault-tolerant N-of-M logic** — a first-class control, not an afterthought; prevents over-filtering the winning line.
5. **Column drill-down → skips** — clicking any statistic column reveals Actual/Average/Now skips inline.
6. **One workspace, dialogs over it** — the ticket store stays visible while you analyze/filter/predict.

---

## 5. Recommended rebuild UI structure (technology-neutral)
Mirror the as-built model, modernized:
- **Shell**: top toolbar (game context + the 8 verbs) + status bar (game, draw count, edition).
- **Center**: split view — **Pool builder** (left) ↔ **Ticket store** (right), always visible.
- **Setup dock** (bottom or left rail): Filters (Base / Advanced tabs) with inline assistant charts and the AND/OR/N-of-M selector.
- **Feature panels** as routed views or modals: Statistics (tabbed), Prediction, Search, Optimize, Check-Win, Drawings manager.
- **Reusable components**: NumberGrid, FrequencyChart, TrendChart, RangeSelector, PositionSelector, SkipsInspector, ExportMenu.

---

## 6. Screenshots (from the official manual)
Real UI captures from `studio_manual_ archive`, mapped to the screen IDs above. Images live in
`Documentation/assets/`.

### Shell & analysis
| Screen | Screenshot |
|---|---|
| **S20** Statistics workspace | ![Statistics workspace](assets/Lottery Studio-Lottery-Analyze-Software.jpg) |
| **S20/B2** Actual Skips drill-down | ![Actual skips](assets/Lottery Studio-Actual-Skips.jpg) |
| **S20a** AC · **S20c** Hot-Cold | ![AC](assets/ac.jpg) ![Hot-Cold](assets/hot-cold.jpg) |
| **S20d** Low-High · **S20e** Distance | ![Low-High](assets/low-high.jpg) ![Distance](assets/distance.jpg) |
| Range · Drawings-Distributing | ![Range](assets/Range-Analysis.jpg) ![Distributing](assets/Drawings-Distributing.jpg) |

### Filtering
| Screen | Screenshot |
|---|---|
| **S03** Base filters input | ![Base filters](assets/Lotto-Lottery Studio-BaseiltersInput.jpg) |
| **S04** Advanced filters | ![Advanced filters](assets/Lotto-Lottery Studio-AdvFilters.jpg) |
| Auto-generate params · **S06** assistant chart | ![Auto params](assets/Automatic-generation-filter.jpg) ![Assistant chart](assets/Lotto-Lottery Studio-Chart.jpg) |

### Generation & tickets
| Screen | Screenshot |
|---|---|
| **S01** Full generate · Positional | ![Full generate](assets/full-generate.jpg) ![Positional](assets/position.jpg) |
| **S43** Quick pick · line counter | ![Quick pick](assets/quick-picked-numbers.jpg) ![Line counter](assets/gen-line-counter.jpg) |
| **S02** Edit tickets · **S40** Print | ![Edit tickets](assets/eidt-lines.jpg) ![Print](assets/print-to-paper.jpg) |

### Predict · optimize · search · check · drawings
| Screen | Screenshot |
|---|---|
| **S30** Predictor · Drawings-Trend | ![Predictor](assets/predictor.jpg) ![Trend](assets/drawings_trend.jpg) |
| **S31** Optimize · **S32** Search | ![Optimize](assets/optimize.jpg) ![Search](assets/search-past-drawings.jpg) |
| **S33** Check winning | ![Check winning](assets/check-winn.jpg) |
| **S10** Open · **S11** New game | ![Open lottery](assets/open-lottery.jpg) ![New lottery](assets/create-new-lottery.jpg) |
| **S15** Update · **S14** Split | ![Update](assets/drawings-update.jpg) ![Split](assets/Split-Lottery-Drawings.jpg) |

---
> **Next Steps**: [⬅️ 07 — Architecture & Data Model (structure design)](07-Architecture-and-Data-Model.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [09 — Database Schema (authoritative, read from the .mdb files) ➡️](09-Database-Schema.md)
