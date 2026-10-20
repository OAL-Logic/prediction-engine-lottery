# 04. Clean-Room Engineering Epics

> **Navigation**: [🏠 Master Reference Hub](../INDEX.md) · [🌐 Interactive Dynamic Portal](../dynamic-portal.html)

13 modular engineering specifications and build-order roadmaps (EPIC-1 through EPIC-8).

## Contents

| # | Module / Subgroup | Document | Key Sections |
| :--- | :--- | :--- | :--- |
| `01` | `Core` | [Lottery Studio Rebuild — Build-Ready Specification](./00-INDEX.md) | How to use this spec, The product in one paragraph, Stack decision (concrete, so prompts are concrete) |
| `02` | `Core` | [01 — Project Structure & Function Context](./01-project-structure.md) | Monorepo layout, Dependency rule (enforced), Context for every major function (deep-module map) |
| `03` | `Core` | [02 — Conventions: the Prompt Template, Quality Gate & Definition of Done](./02-conventions.md) | The five-stage workflow chain (every feature), PROMPT TEMPLATE — paste these, filling the `{{…}}` slots, Stage 1 — Design (interface + types) |
| `04` | `Core` | [90 — Build Order (start-to-finish sequence)](./90-build-order.md) | Dependency graph (epics), Ordered checklist, Global exit criteria (the destination) |
| `05` | `Core` | [99 — Weekly Maintenance Protocol](./99-maintenance-protocol.md) | Weekly cycle (fixed cadence), Monday — Data freshness, Tuesday — Dependency & security |
| `06` | `epics` | [EPIC 1 — Games & Drawings (data foundation)](./epics/EPIC-1-games-drawings.md) | F1.8 — Results file format (parse/serialize `.Txt`), F1.1 — Game model & catalog, F1.2 — Open / choose game |
| `07` | `epics` | [EPIC 2 — Statistical Analysis Engine](./epics/EPIC-2-statistics.md) | F2.1 — SkipsEngine (Actual / Average / Now), F2.2 — Count metrics (Odd / Even / High / Low / Prime), F2.3 — Sum family |
| `08` | `epics` | [EPIC 3 — Ticket Generation](./epics/EPIC-3-generation.md) | F3.1 — Full generator, F3.2 — Positional generator, F3.3 — Random & Smart |
| `09` | `epics` | [EPIC 4 — Filtering Engine (the core value)](./epics/EPIC-4-filtering.md) | F4.1 — Filter framework, F4.2 — Base filters (50), F4.3 — Advanced filters (19) |
| `10` | `epics` | [EPIC 5 — Wheeling Systems](./epics/EPIC-5-wheeling.md) | F5.1 — Full wheel, F5.2 — Abbreviated wheel + guarantee report, F5.3 — Wheel library storage + naming |
| `11` | `epics` | [EPIC 6 — Prediction & Verification](./epics/EPIC-6-prediction.md) | F6.1 — Predictor (pool output), F6.2 — Formula strategies (Formula-1 … Formula-6), F6.3 — Verifier (replay → hit-rate) |
| `12` | `epics` | [EPIC 7 — Tickets Lifecycle · Optimize · Search · Check-Win](./epics/EPIC-7-tickets-lifecycle.md) | F7.1 — TicketSet operations, F7.2 — Optimizer (2 strategies), F7.3 — Searcher (1/2/3-number combos) |
| `13` | `epics` | [EPIC 8 — Shell · Settings · Entitlements · Reusable Components](./epics/EPIC-8-shell-settings-entitlements.md) | F8.1 — App shell + toolbar + navigation, F8.2 — Settings store (per-game + global), F8.3 — Entitlements (Free / Pro gate) |
