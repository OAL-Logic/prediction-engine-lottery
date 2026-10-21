<!-- label: wayfinder:map -->
# MAP — Verified, build-ready SamLotto documentation

## Destination

Turn the existing SamLotto extraction (docs `00`–`09` + CSVs + artifact) into a
**verified, build-ready** documentation set: every documented statistic, filter,
and algorithm **cross-checked against the app's own cached computations** in the
`.mdb` (inferred → proven), and completed to implementation-readiness — per-feature
acceptance criteria, a glossary / ubiquitous-language doc, ER + sequence diagrams,
and real screenshots where they clarify. Done when an engineer could rebuild the
app from the docs alone and every quantitative claim is backed by app data.

## Notes

- **Domain**: SamLotto lottery-analysis desktop app. Existing docs live in
  `Documentation/00..09` + `games-catalog.csv`, `filters-catalog.csv`,
  `design-overview.html`. Master data: `Data/LottoWinner_Data.mdb` (read via
  pure-Python `access_parser`), `Data/Filters_Data.mdb`, `Drawings/*.Txt`.
- **Execution override**: PLAN **and** DO — tickets resolve by *producing docs*
  (validation reports, spec sections, diagrams), not only by deciding.
- **Skills to consult**: `domain-modeling` (glossary), `grilling` (HITL tickets),
  `research`. Validation is AFK and doable now with the DB already accessible.
- **Standing prefs**: non-circumventing (no DRM/endpoint/binary-format cracking);
  ground every number in real draw data; keep docs cross-linked by number.
- **Tracker**: local-markdown (this folder). No native blocking UI, so blocking is
  a body convention (`Blocked-by:` / `Blocks:`). Claim = set `Assignee:`.

## Decisions so far

<!-- one line per closed ticket -->

- [T1 — Validate base metrics vs the app's ComprehensiveAnalyze cache](tickets/T1-validate-base-metrics.md) — on 1,666 reconstructed rows, **11 game-independent metrics proven exact (100%)** incl. AC & floor-division Average; **7 adjacency metrics reach ≥99.8% after correcting the definition** (app uses **draw order, not sorted**, + "run ≥2 else 0"). Docs 02/03 patched; report: [`Documentation/10-Validation-Report.md`](../10-Validation-Report.md).
- [T2 — Validate remaining analysis methods vs their caches](tickets/T2-validate-remaining-caches.md) — diagnosed the T1 misses as an `access_parser` **column-shift artifact** (memo field offsets later columns by one); corrected, **all 26 Base-rollup metrics validate ≥98.7%**. Confirmed **Decade = fixed tens**, **Unit Number Group Count** formula, **Low/High = ⌊M/2⌋**. Only-in-other-table metrics handed to T3.
- [T3 — Recover the memo-corrupted tables + finish validation](tickets/T3-recover-unparsed-tables.md) — re-read the DB with **Jackcess** (bypasses the `access_parser` memo bug); recovered schemas for `Tickets`/`UnitsNumbers`/`DrawingsNumber` (→ doc 09 §2.5) and **validated the last metrics at 100%** (Sum extras, Divided, Multiple, and the **entire Units module + 20 digit-count columns**). Pinned Root Sum (single digit-sum pass) + 3 unit defs. **Net: entire statistical vocabulary verified**; only 2 real math corrections in the whole effort.
- [T5 — Diagrams (ER · sequence · state)](tickets/T5-diagrams.md) — added [`Documentation/12-Diagrams.md`](../12-Diagrams.md): Mermaid ER of the verified data model, two sequence diagrams (play pipeline; pool-based predict/verify), and the ticket-lifecycle state diagram. Cross-linked from docs 00/06/07.
- [T4 — Glossary / ubiquitous language](tickets/T4-glossary-ubiquitous-language.md) — added [`Documentation/glossary.md`](../glossary.md): one canonical term per concept + spelling normalizations; 4 naming choices flagged for user confirmation. (Resolved AFK on user instruction.)
- [T6 — Acceptance criteria](tickets/T6-acceptance-criteria.md) — added [`Documentation/11-Acceptance-Criteria.md`](../11-Acceptance-Criteria.md): Given/When/Then for all 7 subsystems on validated fixtures.
- [T7 — Screenshots](tickets/T7-screenshots.md) — 27 curated UI captures → `Documentation/assets/`, embedded in doc 08 §6 keyed to screen IDs.

> **Map essentially complete.** All charted tickets (T1–T7) closed; the way to the
> destination (verified, build-ready docs) is clear. Remaining items are optional
> polish (see Not yet specified) — graduate them only if desired.

## Not yet specified

<!-- in-scope fog; graduates as the frontier advances -->

- **[GRADUATED 2026-07-12] Build-ready implementation spec** — the `/goal` directive
  graduated the destination into a full rebuild spec under `../../spec/`: master
  index, project structure (deep-module map), conventions (prompt + quality-gate
  templates), **8 epics** (F1–F8; ~45 features each with user stories, module design,
  a 5-stage workflow chain of exact prompts, and a quality gate), build order, and a
  weekly maintenance protocol. Plus root `CONTEXT.md` glossary.
- **Final doc-set restructure / navigable index** — optional: fold `Documentation/`
  + `spec/` into one navigable index or refresh `design-overview.html`.
- **Refresh the visual artifact** with verified numbers + screenshot thumbnails —
  depends on T7 (screenshots) and validation results.

## Out of scope

<!-- ruled beyond the destination; never graduates -->

- **Recovering proprietary internals** — Formula-1..6 prediction math, `.Wheels`
  binary decode, online-update endpoints. (User did not pick "Recover unknowns";
  also brushes the non-circumventing line.) Would be a separate effort.
- **Building the rebuilt app** — the docs are the destination; implementation is
  downstream.
