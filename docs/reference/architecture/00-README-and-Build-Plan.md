# Lottery Studio — Complete Feature Extraction & Rebuild Plan

> **What this is.** A full, evidence-based extraction of every feature, math
> algorithm, strategy, filter, and concept in **Standard Lottery Studio**
> (product lineage: *Lottery Analysis Studio*, "a true winning tool since 2003"),
> plus a structured plan and architecture design to rebuild an app with feature
> parity.
>
> **Sources used** (all local, non-circumventing):
> - `studio_manual_ archive` — the official help manual (63 HTML topics, decompiled to text).
> - `studio_app.bin` — surface string inspection (UI labels, form names, edition gates).
> - `Data/`, `Drawings/`, `Formula/`, `*.ini` — real data files (formats reverse-engineered from samples).
>
> **What Lottery Studio is.** A Windows desktop lottery-analysis toolkit for
> *number-draw* ("lotto-type") games. It maintains a historical results database
> for 200+ worldwide games, runs statistical analysis on that history, generates
> candidate tickets (random / positional / full / wheeled), filters those tickets
> down with 68 configurable filters, optimizes the surviving set, predicts the
> next draw with formula algorithms, and checks tickets against results.

---

## Document set

| File | Contents |
|---|---|
| `00-README-and-Build-Plan.md` | This file: overview + phased rebuild plan + edition matrix |
| `01-Feature-Inventory.md` | Every user-visible feature, grouped by subsystem, with evidence |
| `02-Statistical-Analysis-Reference.md` | Every analysis method + exact math/definitions |
| `03-Filters-Reference.md` | All 50 base + 18 advanced filters, with algorithms & examples |
| `04-Wheeling-Systems.md` | Wheeling math, full vs abbreviated, guarantees, file format |
| `05-Prediction-Generation-Optimization-Search.md` | Predictor, generation modes, optimization, search |
| `06-User-Flows-With-Examples.md` | End-to-end worked flows with concrete numbers |
| `07-Architecture-and-Data-Model.md` | Structure design: modules, data model, file formats |
| `08-UI-Screen-Design-and-Navigation.md` | The app's real screens (37 forms), navigation, interaction patterns |
| `09-Database-Schema.md` | **Authoritative** schema read from the `.mdb` files (supersedes inferences) |
| `10-Validation-Report.md` | Documented formulas **checked against the app's own computed values** (proven/corrected) |
| `11-Acceptance-Criteria.md` | Black-box Given/When/Then criteria per subsystem, on validated fixtures |
| `12-Diagrams.md` | Mermaid ER · sequence · state diagrams of the model and core flows |
| `glossary.md` | Ubiquitous-language glossary (one canonical term per concept) |
| `assets/` | Real UI screenshots from the manual (embedded in doc 08) |
| `games-catalog.csv` · `filters-catalog.csv` | Machine-readable game + filter catalogs (from the DB) |
| `_wayfinder/` | The documentation-improvement map (local-markdown tracker): destination, tickets, decisions |

---

## Product editions (feature gates)

Extracted verbatim from `studio_app.bin` ("Upgrade to Lottery Studio Full to unlock…"):

| # | Free Edition limit | Pro unlocks |
|---|---|---|
| 1 | Evaluation / trial nag ("Thank you for using Lottery Studio Trial") | Full license, free upgrades, latest results download |
| 2 | **Pick up to 10 numbers max** ("This is the FREE Edition, limit of picking up to 10 numbers") | Unlimited number pool |
| 3 | Wheels **locked** | 2200+ wheeling formulas |
| 4 | Subset of filters | 60+ filters (the full 50 base + 18 advanced) |
| 5 | Optimization **locked** | Ticket optimization function |
| 6 | Prediction **locked** | Next-draw prediction + verification |

> When rebuilding, model this as a single capability flag set (`entitlements`)
> rather than two binaries.

---

## The app at a glance (6 subsystems)

```
                       ┌──────────────────────────────────────────┐
                       │            Lottery Studio main window           │
                       └──────────────────────────────────────────┘
   ┌───────────────┬───────────────┬───────────────┬───────────────┬──────────────┐
   │ 1. DRAWINGS   │ 2. ANALYSIS   │ 3. GENERATION │ 4. FILTERING  │ 5. PREDICT   │
   │ (results DB)  │ (statistics)  │ (make tickets)│ (cut tickets) │ (next draw)  │
   ├───────────────┼───────────────┼───────────────┼───────────────┼──────────────┤
   │ open/new game │ 18+ methods   │ random/smart  │ 50 base       │ 6 formulas   │
   │ add/edit/ins  │ AC, Sum, Odd- │ positional    │ 18 advanced   │ drawings     │
   │ del/modify    │ Even, Hot-Cold│ full generate │ AND/OR/N-of-M │  trend       │
   │ import/export │ Distance, Sum │ wheels        │ assistant     │ verification │
   │ split by day  │ Skips, Range  │ quick pick    │ auto-params   │ (records     │
   │ online update │ Units, Divided│ favorites     │ report        │  accuracy)   │
   └───────────────┴───────────────┴───────────────┴───────────────┴──────────────┘
                       ┌──────────────────────────────────────────┐
                       │ 6. TICKETS: edit · optimize · search ·    │
                       │    check-winning · print · export         │
                       └──────────────────────────────────────────┘
```

---

## Phased rebuild plan

A clone reaching feature parity can be built in 7 phases. Each phase is
independently shippable and testable against the real app's behavior.

### Phase 1 — Data foundation (game model + results store)
- **Game definition model**: `{name, pick (2–9), maxNumber (1–90), bonusCount, bonusName, bonusMax, drawingFile}` (from `Lottery_Set.ini`).
- **Results store**: date + N main numbers (+ optional bonus). Support 200+ seed games (see `Drawings/*.Txt`).
- CRUD on draws: add, insert-at-position, modify, delete, import (txt), export/backup, **split by weekday**.
- Online update hook (fetch latest results per game).
- *DoD:* load `BrazilMegaSenaBR660.Txt`, round-trip edit, split Thu-only.

### Phase 2 — Statistical analysis engine
- Implement every method in `02-Statistical-Analysis-Reference.md` as pure functions over a draw-history window.
- **Actual Skips / Average Skips / Now Skips** engine (used everywhere: analysis, filter auto-params, prediction).
- Configurable analysis range and position selection.
- *DoD:* numbers match the manual's worked examples exactly.

### Phase 3 — Ticket generation
- 4 modes: Random, Positional (per-position number sets), Full-combination generator, Wheel generator.
- Quick-pick helpers (hot / cold / last-N-draw numbers).
- Favorites save/load.
- *DoD:* full generator on chosen pool = C(n,k) lines; positional respects per-slot sets.

### Phase 4 — Filtering engine (the core value)
- 50 base + 18 advanced filters (`03-Filters-Reference.md`), each as a predicate `(combo, history) → bool`.
- **Auto-parameter generation** from history (ranges: prev 2/3/5/10/20/30/50/current).
- **Logical combination**: AND, OR, or fault-tolerant "N-of-M" (e.g. pass if 3–5 of 5 filters match).
- Filter **assistant** (frequency + trend charts per filter), position-scoped filtering, filter **report**.
- Save/load filter sets.
- *DoD:* on a known pool, filter counts + report match manual demo.

### Phase 5 — Wheeling systems
- Covering-design library: pick(2–7) × wheel-size(≤36) × guarantee × variant (`04-Wheeling-Systems.md`).
- Full wheels (all C(n,k)) + abbreviated wheels (minimal guaranteed-cover sets).
- Guarantee reporting ("if X of pick are in your Y numbers → Z tickets match W").
- *DoD:* 8-number pick-6 "if 4 match" = 7 lines; full 8→28 lines.

### Phase 6 — Prediction & verification
- Formula predictor (Formula-1…6 + algorithm selector + offset/depth).
- Manual "Drawings Trend" predictor UI.
- **Verification**: replay each formula over history, record hit accuracy per formula/algorithm, incl. bonus and Actual-Skips.
- *DoD:* verification produces per-formula accuracy over a chosen range.

### Phase 7 — Tickets lifecycle & output
- Ticket store: add/delete/sort(low→high)/dedupe/tag/clear, numbers-hit stats, 2- & 3-number combo frequency.
- **Optimization** (2 strategies, see doc 05).
- **Check-winning** (= / > / < / ≥ / ≤ match N, bonus-aware).
- Search past drawings (1/2/3-number combos, skips, ranges).
- Print, and export to TXT / HTML / XLS.
- *DoD:* check-winning finds all lines matching ≥4 of a chosen past draw.

### Cross-cutting
- **Settings/state**: per-game `Current_Set.ini` + global set (see doc 07).
- **Entitlements** gate (edition matrix above).
- **Charts**: frequency bars + trend lines are used pervasively — build one reusable chart component early.

---

## How to read the algorithm docs

Every filter/stat entry uses this shape so it's directly implementable:

> **Name** — *what it measures* · **Formula/rule** · **Worked example** · **Used by** (analysis / filter / prediction).

See `02` and `03` for the full catalog.
