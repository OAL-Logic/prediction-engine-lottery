# 01. Architecture & Data Structures

> **Navigation**: [🏠 Master Reference Hub](../INDEX.md) · [🌐 Interactive Dynamic Portal](../dynamic-portal.html)

Architectural specifications, reverse-engineered mathematical formulas, 69-filter engine schemas, and data structures.

## Contents

| # | Module / Subgroup | Document | Key Sections |
| :--- | :--- | :--- | :--- |
| `01` | `Core` | [Lottery Studio — Complete Feature Extraction & Rebuild Plan](./00-README-and-Build-Plan.md) | Document set, Product editions (feature gates), The app at a glance (6 subsystems) |
| `02` | `Core` | [01 — Complete Feature Inventory](./01-Feature-Inventory.md) | A. Lottery / Drawings management  `[CHM: Working with Lottery Drawing Files]`, B. Statistical analysis  `[CHM: Interpreting the Statistical]` · `TstatisticForm`, C. Ticket generation  `[CHM: Creating and Edit Your Lottery Tickets]` |
| `03` | `Core` | [02 — Statistical Analysis Reference (every method + exact math)](./02-Statistical-Analysis-Reference.md) | Skips — the backbone concept (used everywhere), 1. AC — Arithmetic Complexity  `acTabSheet`, 2. Sum family  `sumtabSheet` |
| `04` | `Core` | [03 — Filters Reference (68 filters: 50 base + 18 advanced)](./03-Filters-Reference.md) | How filters work (shared mechanics), Base filters (50), Count filters |
| `05` | `Core` | [04 — Wheeling Systems (covering designs)](./04-Wheeling-Systems.md) | The two wheel types, Full wheel, Abbreviated wheel |
| `06` | `Core` | [05 — Prediction, Generation, Optimization & Search](./05-Prediction-Generation-Optimization-Search.md) | A. Ticket generation modes  `[CHM: Creating tickets]`, A1. Random, A2. Smart (analysis-depth weighted) |
| `07` | `Core` | [06 — User Flows (end-to-end, with concrete examples)](./06-User-Flows-With-Examples.md) | Flow 0 — The canonical "play a lottery" pipeline, Flow 1 — Open a game & update results, Flow 2 — Statistical analysis to inform filters |
| `08` | `Core` | [07 — Architecture & Data Model (structure design)](./07-Architecture-and-Data-Model.md) | 1. As-built technology (evidence), 2. Layered reference architecture (for rebuild), 3. Domain model |
| `09` | `Core` | [08 — UI Screen Design & Navigation Map](./08-UI-Screen-Design-and-Navigation.md) | 1. Information architecture, 2. Screen catalog (forms), Core workspace |
| `10` | `Core` | [09 — Database Schema (authoritative, read from the .mdb files)](./09-Database-Schema.md) | Database 1 — `Data/FilterCatalog_Data.db` (filter catalog / presets), The 4 filter engine types (definitive taxonomy), Base-filter default ranges (as shipped) |
| `11` | `Core` | [10 — Validation Report (documented formulas vs the app's own computations)](./10-Validation-Report.md) | Method, Results, ✅ Proven exactly — 100% (1666/1666), game-independent |
| `12` | `Core` | [11 — Acceptance Criteria (black-box, per subsystem)](./11-Acceptance-Criteria.md) | S1 — Drawings / game management, S2 — Statistics engine  (assert against validated formulas, doc 10), S3 — Generation |
| `13` | `Core` | [12 — Diagrams (ER · sequence · state)](./12-Diagrams.md) | 1. Entity-relationship — the data model, 2. Sequence — the play pipeline (generate → … → check), 3. Sequence — predict & verify (pool-based) |
| `14` | `Core` | [13 — Distilled Algorithmic Specifications & Clean-Room Python Boilerplate](./13-Distilled-Algorithms-and-Boilerplate.md) | 1. Unified 69-Filter Evaluation Engine (50 Base + 19 Advanced), Boilerplate Implementation, 2. Advanced Filter Token Serializer & Evaluator |
| `15` | `Core` | [14 — Comprehensive Data Structures & Storage Reference](./14-Data-Structures-and-Storage-Reference.md) | 1. High-Level Data Architecture & Entity-Relationship Map, 2. File System & Directory Layout, 3. On-Disk File Formats & Wire Protocols |
| `16` | `Core` | [Glossary — Ubiquitous Language](./glossary.md) | Core objects, Skips & frequency, Combination metrics (all ✅ validated, doc 10) |
