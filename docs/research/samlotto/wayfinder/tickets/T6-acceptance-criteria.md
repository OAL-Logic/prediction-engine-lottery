<!-- parent: MAP · label: wayfinder:task -->
# T6 — Per-feature acceptance criteria

Type: task (AFK) · Assignee: fable-session  · Status: CLOSED
Blocked-by: T1, T4 (both closed)  ·  Blocks: —

## Resolution (CLOSED)

Produced `Documentation/11-Acceptance-Criteria.md` — Given/When/Then criteria for
all 7 subsystems (Drawings, Statistics, Generation, Filtering, Wheeling, Prediction,
Tickets/Optimize/Search/Check) plus cross-cutting (persistence, entitlements, data
fidelity). Grounded in the validated formulas (doc 10) and glossary (T4), with
concrete black-box fixtures (e.g. full-generate 12→924; 8-number pick-6 "if-4"→7
lines; Root Sum 165→12; check-winning ≥4).

## Question

Expand doc 00's per-phase "DoD" lines into testable **acceptance criteria** per
subsystem (Given/When/Then), grounded in the *validated* formulas (T1/T2) and the
agreed glossary (T4). One suite per subsystem: Drawings, Statistics, Generation,
Filtering, Wheeling, Prediction, Tickets/Optimize/Search/Check. Each criterion
must be black-box verifiable against real draw data (reuse the validation
fixtures). Output: `Documentation/11-Acceptance-Criteria.md`.
