# Lottery Studio Rebuild — Build-Ready Specification

**Role framing:** written as your Chief System Architect. This is not a framework
or a skeleton — it is the complete set of epics, features, user stories, module
designs, **exact build prompts**, quality gates, and a maintenance protocol needed
to rebuild Lottery Studio to feature parity, starting today.

It stands on a **verified** foundation: every statistic and filter in this spec was
validated against the original app's own computed values (see `../Documentation/10-Validation-Report.md`).
Where this spec states a formula, it is the proven one.

---

## How to use this spec

1. Read `01-project-structure.md` — the module map and the context for every major
   function.
2. Read `02-conventions.md` — the **prompt template**, **quality-gate template**,
   Definition of Done, and test strategy. Every feature chain below reuses these.
3. Build in the order of `90-build-order.md`. For each feature, open its epic file
   and run its **workflow chain**: each stage has a ready-to-paste prompt; the chain
   ends with a quality gate you must pass before moving on.
4. Keep the system current with `99-maintenance-protocol.md` (weekly).

Each **feature** in an epic file is fully self-contained:
> Epic → Feature → *User stories* → *Module design (interface/seam)* →
> *Workflow chain (staged prompts)* → *Quality gate*.

---

## The product in one paragraph

A cross-platform desktop app for analysing number-draw ("lotto-type") lotteries.
It maintains a historical results database for 200+ games, runs 18 statistical
methods over that history, generates candidate tickets (random / positional /
full / wheeled), filters them with 69 configurable filters, reduces the survivors
with wheels and optimization, predicts a next-draw recommended pool with
verifiable formulas, and checks tickets against results. Verified reference:
`../Documentation/`.

---

## Stack decision (concrete, so prompts are concrete)

> "Don't give me a framework" = don't hand-wave. So we commit to a concrete stack.
> The **domain core is framework-agnostic**, so the shell is swappable later.

| Layer | Choice | Why |
|---|---|---|
| Language | **TypeScript** (strict) | The validated math ports 1:1; one language across core, app, UI; huge test tooling. |
| Domain core | **`packages/core`** — pure TS, zero I/O, zero UI | The crown jewel (all math); 100% unit-tested through its interfaces. |
| Application layer | **`packages/app`** — use-cases orchestrating core + data | Framework-agnostic; the UI calls this, never core internals. |
| Data adapters | **`packages/data`** — repositories, exporters, update client | Implements interfaces *defined by* core/app (dependency inversion). |
| Desktop shell | **Tauri** (Rust) + **React** + TS (`apps/desktop`) | Small binary, native file access; Electron is a drop-in alt. |
| Tests | **Vitest** (unit/integration), **Playwright** (e2e UI) | Fast, TS-native. |
| Charts | **Reusable chart components** (see `01`) | Frequency + trend charts appear everywhere. |
| Monorepo | **pnpm workspaces** + **Turborepo** | Clean package graph, cached builds. |

If you prefer Electron, or a Python/Qt core, the epics still apply verbatim — only
the Stage-1 scaffold prompt changes. Everything downstream is behavior, not stack.

---

## Epic index

| # | Epic | Rebuild phase | File |
|---|---|---|---|
| 1 | Games & Drawings (data foundation) | 1 | `epics/EPIC-1-games-drawings.md` |
| 2 | Statistical Analysis Engine | 2 | `epics/EPIC-2-statistics.md` |
| 3 | Ticket Generation | 3 | `epics/EPIC-3-generation.md` |
| 4 | Filtering Engine | 4 | `epics/EPIC-4-filtering.md` |
| 5 | Wheeling Systems | 5 | `epics/EPIC-5-wheeling.md` |
| 6 | Prediction & Verification | 6 | `epics/EPIC-6-prediction.md` |
| 7 | Tickets Lifecycle · Optimize · Search · Check-Win | 7 | `epics/EPIC-7-tickets-lifecycle.md` |
| 8 | Shell · Settings · Entitlements (cross-cutting) | 1→7 | `epics/EPIC-8-shell-settings-entitlements.md` |

Supporting docs: `90-build-order.md` (end-to-end sequence), `99-maintenance-protocol.md`
(weekly), `../CONTEXT.md` (glossary / ubiquitous language).

---

## Traceability

Every feature links back to the verified reference so you never guess:
- Feature behavior → `../Documentation/01-Feature-Inventory.md`
- Statistics math → `../Documentation/02-Statistical-Analysis-Reference.md`
- Filters → `../Documentation/03-Filters-Reference.md`
- Wheeling → `../Documentation/04-Wheeling-Systems.md`
- Prediction/gen/optimize/search → `../Documentation/05-...md`
- Flows → `../Documentation/06-User-Flows-With-Examples.md`
- Architecture/data model → `../Documentation/07`, `09`
- UI/screens → `../Documentation/08-UI-Screen-Design-and-Navigation.md`
- Acceptance criteria → `../Documentation/11-Acceptance-Criteria.md`
- Diagrams → `../Documentation/12-Diagrams.md`
- Validation proof → `../Documentation/10-Validation-Report.md`
