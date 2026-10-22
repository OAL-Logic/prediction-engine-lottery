# 12 — Diagrams (ER · sequence · state · pipeline)

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 11 — Acceptance Criteria (black-box, per subsystem)](11-Acceptance-Criteria.md) · [13 — Distilled Algorithmic Specifications & Clean-Room Python Boilerplate ➡️](13-Distilled-Algorithms-and-Boilerplate.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [1. Entity-relationship — the data model](#1-entity-relationship-the-data-model)
- [2. Sequence — the play pipeline (generate → … → check)](#2-sequence-the-play-pipeline-generate-check)
- [3. Sequence — predict & verify (pool-based)](#3-sequence-predict-verify-pool-based)
- [4. State — ticket lifecycle](#4-state-ticket-lifecycle)
- [5. System Container & Interface Topology](#5-system-container--interface-topology)
- [6. Five-Tier 69-Filter Funnel Architecture](#6-five-tier-69-filter-funnel-architecture)
- [7. Boundary-Swap Stochastic Balancing Pipeline](#7-boundary-swap-stochastic-balancing-pipeline)

</details>
<!-- TOC_BLOCK_END -->

Mermaid diagrams for the structure, pipelines, and the core flows, grounded in the verified
data model (doc 09), the flows (doc 06), and the frontier multi-modal synthesis (docs 15–29).
Renders on GitHub and any Mermaid-aware viewer.

---

## 1. Entity-relationship — the data model

The domain reduces to a handful of entities. Every analysis method persists a
per-draw **cache table** (doc 09 §2.2/2.5) — modelled here as one abstract
`AnalysisResult` with the concrete tables listed beneath, to keep the diagram
legible.

```mermaid
erDiagram
    accTitle: System Entity Relationship Data Model
    accDescr: High-level ER diagram linking games, historical draws, candidate tickets, 69-filter catalog, covering wheels, and cached analysis results.

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
    accTitle: Play Pipeline Sequence Diagram
    accDescr: Sequence of player actions through game selection, statistical analysis, generation, 69-filter evaluation, cost optimization, and win checking.
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
    accTitle: Pool Prediction and Historical Verification
    accDescr: Sequence diagram illustrating out-of-sample backtesting and pool verification across historical draw windows.
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
    accTitle: Ticket Lifecycle State Machine
    accDescr: State transitions of candidate tickets from initial combinatorial generation through filtering, wheeling, optimization, tagging, wagering, and settlement.
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

## 5. System Container & Interface Topology

High-level architecture decoupling the user presentation clients, the command dispatcher/gateway layer, the multi-tier prediction core, and the analytical storage backends.

```mermaid
flowchart TB
    accTitle: Container Architecture and Ecosystem Topology
    accDescr: High-level architectural container diagram illustrating frontend clients, routing gateways, engine core pipelines, and multi-database storage layers.

    subgraph clients["🖥️ Client Presentation Layer"]
        cli["CLI Launcher<br/><code>./p4lottery</code>"]
        desktop["Desktop Studio<br/><code>PySide6 / Qt6</code>"]
        cockpit["Web Cockpit<br/><code>TypeScript / React</code>"]
        tui["Terminal UI<br/><code>Textual / Ink</code>"]
        lab["Interactive Lab<br/><code>25 JS Simulators</code>"]
        portal["Dynamic Portal<br/><code>285 Indexed Docs</code>"]
    end

    subgraph gateway_layer["⚡ Control & Interface Gateway"]
        cli_router["CLI Command Dispatcher<br/>(100+ Commands)"]
        fastapi["FastAPI Core Engine Service<br/>(REST & WebSocket)"]
        pqc_gw["Go Gateway Hub<br/>(PQC & Telemetry)"]
    end

    subgraph engine_core["🧠 Prediction & Analytical Core"]
        direction TB
        diag_scan["6-Layer Diagnostic Scan<br/>(GO / NO-GO Filter)"]
        strat_ensemble["80+ Strategy Ensemble<br/>(Statistical, ML, DL, Physics, Esoteric)"]
        filter_funnel["69-Filter Funnel<br/>(5 Tiers, N-of-M Fault Tolerance)"]
        boundary_swap["Boundary-Swap Balancer<br/>(Stochastic Operator)"]
        wheel_engine["Combinatorial Wheeling Engine<br/>(2,360 Covering Designs)"]
        risk_kelly["Kelly Staking & Portfolio<br/>(Fractional Capital Allocator)"]
    end

    subgraph storage_layer["💾 High-Performance Storage Layer"]
        duckdb[("DuckDB OLAP Engine<br/>Vectorized Aggregates")]
        sqlite[("SQLite Relational DB<br/>Metadata & Draw History")]
        parquet[("Parquet Cache<br/>Precomputed Partitions")]
        blake_cache[("BLAKE2b Cache<br/>Sub-millisecond Hashes")]
    end

    subgraph external_sources["🌐 External Official Ingestion"]
        caixa["Caixa Econômica Federal (BR)<br/>Lotofácil, Mega-Sena, Quina"]
        intl_lotteries["US / EU Global Catalogs<br/>Powerball, Mega Millions, EuroMillions"]
    end

    cli --> cli_router
    desktop --> fastapi
    cockpit --> pqc_gw
    pqc_gw --> fastapi
    tui --> cli_router

    cli_router --> engine_core
    fastapi --> engine_core

    engine_core --> storage_layer
    caixa --> cli_router
    intl_lotteries --> cli_router

    classDef clientStyle fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    classDef gatewayStyle fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#0f172a;
    classDef engineStyle fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#0f172a;
    classDef storageStyle fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#0f172a;
    classDef externalStyle fill:#f1f5f9,stroke:#64748b,stroke-width:2px,color:#0f172a;

    class cli,desktop,cockpit,tui,lab,portal clientStyle;
    class cli_router,fastapi,pqc_gw gatewayStyle;
    class diag_scan,strat_ensemble,filter_funnel,boundary_swap,wheel_engine,risk_kelly engineStyle;
    class duckdb,sqlite,parquet,blake_cache storageStyle;
    class caixa,intl_lotteries externalStyle;
```

---

## 6. Five-Tier 69-Filter Funnel Architecture

The 69-filter evaluation engine processes candidate tickets through five hierarchical structural tiers with support for classical Boolean conjunction (`AND`), disjunction (`OR`), and soft $N$-of-$M$ fault-tolerant relaxation.

```mermaid
flowchart TD
    accTitle: Five-Tier 69-Filter Evaluation Funnel Dataflow
    accDescr: Structural hierarchy of the 69-filter evaluation engine showing progression through structural, positional, algebraic, historical, and advanced frontier tiers with fault-tolerant acceptance.

    raw_tickets["🎟️ Raw Candidate Combinations"]

    subgraph tier1["Tier 1: Structural Filters (1–15)"]
        t1["Sum Range, Odd/Even Ratio, High/Low Split,<br/>Consecutive Numbers, Decade & Unit Distribution"]
    end

    subgraph tier2["Tier 2: Positional Filters (16–30)"]
        t2["Positional Deltas, Number Gaps, First/Last Spread,<br/>Column/Row Grid Projections, Center-of-Mass"]
    end

    subgraph tier3["Tier 3: Algebraic & Modular Filters (31–45)"]
        t3["Arithmetic Complexity (AC), Modulo 3/5/9 Residues,<br/>Prime Counts, Fibonacci Density, Square Distances"]
    end

    subgraph tier4["Tier 4: Historical & Decay Filters (46–50)"]
        t4["Repeat Last Draw Counts, Overdue Frequency,<br/>Laplace Posterior Decay, Cluster Recurrence"]
    end

    subgraph tier5["Tier 5: Advanced & Topological Filters (51–69)"]
        t5["Chladni Nodal Density, Braid Invariants,<br/>Ising Energy Thresholds, Soliton Dispersion, Phase Angle"]
    end

    relaxer{"⚖️ N-of-M Fault-Tolerant Relaxer<br/>Acceptance Threshold (>= 90%)?"}
    accepted["🏆 Accepted Tickets Portfolio"]
    rejected["❌ Eliminated Candidate"]

    raw_tickets --> tier1
    tier1 --> tier2
    tier2 --> tier3
    tier3 --> tier4
    tier4 --> tier5
    tier5 --> relaxer
    relaxer -->|"Pass"| accepted
    relaxer -->|"Fail"| rejected

    classDef tierStyle fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef filterGate fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12;
    classDef finalPass fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#15803d;
    classDef finalFail fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#991b1b;

    class tier1,tier2,tier3,tier4,tier5 tierStyle;
    class relaxer filterGate;
    class accepted finalPass;
    class rejected finalFail;
```

---

## 7. Boundary-Swap Stochastic Balancing Pipeline

Balancing multi-objective target metrics (Sum range, Odd/Even ratio, AC complexity) via single-step minimal boundary perturbation without invalidating underlying strategy weights.

```mermaid
flowchart LR
    accTitle: Boundary-Swap Stochastic Balancing Pipeline
    accDescr: Pipeline flowchart showing candidate generation, objective metric discrepancy evaluation, boundary swap step, and ticket stabilization.

    init_ticket["🎯 Candidate Ticket<br/>(Weighted Output)"]
    eval_metrics{"📊 Metric Evaluation<br/>(Sum, Odd/Even, AC)"}
    in_range["✅ Within Gaussian Envelope"]
    out_range["⚠️ Boundary Violation"]
    swap_op["🔄 Boundary-Swap Operator<br/>(Delta +/- 1..k perturbation)"]
    stabilized["🏆 Stabilized Ticket"]

    init_ticket --> eval_metrics
    eval_metrics -->|"In Target Band"| in_range
    eval_metrics -->|"Out of Envelope"| out_range
    out_range --> swap_op
    swap_op --> eval_metrics
    in_range --> stabilized

    classDef nodeStyle fill:#f8fafc,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    classDef gateStyle fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef passStyle fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d;

    class init_ticket,swap_op nodeStyle;
    class eval_metrics,out_range gateStyle;
    class in_range,stabilized passStyle;
```

---

*Cross-referenced from doc 06 (flows), doc 07 (architecture), doc 09 (schema), and doc 15 (frontier mechanics).*

---
> **Next Steps**: [⬅️ 11 — Acceptance Criteria (black-box, per subsystem)](11-Acceptance-Criteria.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [13 — Distilled Algorithmic Specifications & Clean-Room Python Boilerplate ➡️](13-Distilled-Algorithms-and-Boilerplate.md)
