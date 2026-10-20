# 12 — Diagrams (ER · sequence · state)

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 11 — Acceptance Criteria (black-box, per subsystem)](11-Acceptance-Criteria.md) · [13 — Distilled Algorithmic Specifications & Clean-Room Python Boilerplate ➡️](13-Distilled-Algorithms-and-Boilerplate.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [1. Entity-relationship — the data model](#1-entity-relationship-the-data-model)
- [2. Sequence — the play pipeline (generate → … → check)](#2-sequence-the-play-pipeline-generate-check)
- [3. Sequence — predict & verify (pool-based)](#3-sequence-predict-verify-pool-based)
- [4. State — ticket lifecycle](#4-state-ticket-lifecycle)

</details>
<!-- TOC_BLOCK_END -->

Mermaid diagrams for the structure and the core flows, grounded in the verified
data model (doc 09) and the flows (doc 06). Renders on GitHub and any Mermaid-aware
viewer.

---

## 1. Entity-relationship — the data model

The domain reduces to a handful of entities. Every analysis method persists a
per-draw **cache table** (doc 09 §2.2/2.5) — modelled here as one abstract
`AnalysisResult` with the concrete tables listed beneath, to keep the diagram
legible.

```mermaid
erDiagram
    GAME ||--o{ DRAW : "has history"
    GAME ||--o{ TICKET : "tickets built for"
    GAME ||--o{ ANALYSIS_RESULT : "cached per draw"
    GAME ||--o{ PREDICTION : "formula runs"
    PREDICTION ||--o{ VALIDATION : "verified against draws"
    FILTER_CATALOG }o--o{ TICKET : "eliminates"
    WHEEL ||--o{ TICKET : "generates"
    DRAW ||--o{ ANALYSIS_RESULT : "computed from"

    GAME {
        string Lottery_Name PK
        int    From "max number M"
        int    Match "pick k (2..9)"
        bool   Bouns "has bonus"
        int    PB_Max "bonus pool max"
        string Groups "region"
        string Country_State
        string Lottery_File "Drawings/*.Txt"
    }
    DRAW {
        date   Date
        int_array numbers "k main numbers"
        int_array bonus "0..PB_Max"
    }
    TICKET {
        string Tickets "combination"
        string Tag "'' or X"
        int    Sum
        int    AC
        int    Root_Sum
        int    Prime
        int    Low
        int    High
    }
    FILTER_CATALOG {
        int    Condition_Tag PK "1..69"
        int    Condition_Type "1=base 2..4=advanced"
        string Condition_Caption
        string Condition "default range e.g 1-5"
        string IncludePos
    }
    WHEEL {
        int  k "pick"
        int  n "wheel size <=36"
        int  guarantee "match tier"
        int  variant
    }
    ANALYSIS_RESULT {
        date   Date
        string Drawings
        string metrics "method-specific columns"
    }
    PREDICTION {
        string Formula "Formula-1..6"
        int    algorithm
        int    offset
        int    depth
        string Recommended "number pool"
        string Eliminated
    }
    VALIDATION {
        date   Verification_Drawings
        string Drawings "actual"
        string Perdiction_Numbers "pool"
        int    Correct_Count
    }
```

**Concrete `ANALYSIS_RESULT` tables** (one per statistics screen, doc 09):
`ACA, Apart, BigSmall, OddEven, SumA, Residue, Multiple, hotcold, BeforeDrawings,
BeJoined, UnitsNumbers, DrawingsNumber, DrawingsDistributing, NumbersHits,
AppearCount, ComprehensiveAnalyze`.

---

## 2. Sequence — the play pipeline (generate → … → check)

Maps the domain modules of doc 07 onto the flow of doc 06. Filtering and wheeling
both **reduce** the candidate set before it becomes tickets to play.

```mermaid
sequenceDiagram
    actor U as Player
    participant SH as Shell/Toolbar
    participant GN as GenerationEngine
    participant ST as StatisticsEngine
    participant FE as FilterEngine
    participant WL as WheelLibrary
    participant OP as Optimizer
    participant TS as TicketStore
    participant WC as WinChecker

    U->>SH: open game (Lottery)
    SH->>ST: analyze(range, positions)
    ST-->>U: skips / hot-cold / sum ranges
    U->>GN: select pool + mode (full / wheel / positional)
    alt Wheel mode
        GN->>WL: build(k, n, guarantee)
        WL-->>GN: covering lines (guarantee report)
    end
    GN-->>TS: candidate combinations
    U->>FE: choose filters + logic (AND / OR / N-of-M)
    FE->>ST: auto-params from history (prev 20/30…)
    FE->>TS: remove failing lines
    FE-->>U: filter report (per-filter cut counts)
    U->>OP: optimize (reduce cost)
    OP->>TS: keep representative subset
    U->>SH: play / print / export
    Note over TS: after the draw
    U->>WC: check(draw, op, matchN, bonus?)
    WC->>TS: scan lines
    WC-->>U: winning tickets → save HTML/TXT/XLS
```

---

## 3. Sequence — predict & verify (pool-based)

Prediction produces a **recommended number pool** (not a single line); verification
replays a formula and measures how many actual winners fell inside the pool
(doc 05, doc 09 §2.4).

```mermaid
sequenceDiagram
    actor U as Player
    participant PR as Predictor
    participant SK as SkipsEngine
    participant H as DrawHistory
    participant VF as Verifier
    participant GN as GenerationEngine

    U->>PR: Formula-n, algorithm, offset, depth
    PR->>H: window(depth, offset)
    PR->>SK: skips / trend per number
    PR-->>U: recommended pool (~17-27) + eliminated + bonus
    U->>GN: push pool into number panel → wheel/pick
    U->>VF: verify(Formula-n, range)
    loop each past draw in range
        VF->>PR: predict pool as-of that draw
        VF->>H: actual result
        VF->>VF: correctCount = |pool ∩ actual|
    end
    VF-->>U: per-draw hits + rollup hit-rate + Actual Skips
```

---

## 4. State — ticket lifecycle

A combination moves through generation, reduction, play, and settlement. Tags
(`X` / blank) mark lines for bulk keep/delete before play.

```mermaid
stateDiagram-v2
    [*] --> Generated : full / wheel / positional / random
    Generated --> Filtered : run selected filters (AND/OR/N-of-M)
    Filtered --> Generated : adjust params / re-generate
    Filtered --> Wheeled : convert-to-wheel (optional)
    Filtered --> Optimized : reduce cost
    Wheeled --> Optimized
    Optimized --> Tagged : sort · dedupe · tag X/blank
    Tagged --> Optimized : delete tagged / edit
    Tagged --> Played : print / export / save
    Played --> Checked : after the draw — check winning
    Checked --> Won : matchN satisfied (+bonus?)
    Checked --> Lost : no qualifying match
    Won --> [*] : save HTML/TXT/XLS
    Lost --> [*]
```

---

*Cross-referenced from doc 06 (flows), doc 07 (architecture), doc 09 (schema).*

---
> **Next Steps**: [⬅️ 11 — Acceptance Criteria (black-box, per subsystem)](11-Acceptance-Criteria.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [13 — Distilled Algorithmic Specifications & Clean-Room Python Boilerplate ➡️](13-Distilled-Algorithms-and-Boilerplate.md)
