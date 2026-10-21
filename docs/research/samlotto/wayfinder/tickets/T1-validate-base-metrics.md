<!-- parent: MAP · label: wayfinder:research -->
# T1 — Validate base metrics vs the app's ComprehensiveAnalyze cache

Type: research (AFK) · Assignee: fable-session · Status: CLOSED
Blocked-by: —  ·  Blocks: T2, T6

## Question

Do the formulas documented in `02-Statistical-Analysis-Reference.md` and
`03-Filters-Reference.md` actually match what the app computes? Recompute each
base metric from the raw `Drawings` values and compare against the app's own
`ComprehensiveAnalyze` cache (28 columns × 1,742 rows) in
`LottoWinner_Data.mdb`. Produce a validation report; flag any mismatch.

## Resolution (CLOSED)

Full report: `Documentation/10-Validation-Report.md`. Reconstructed 1,666/1,742
(95.6%) combinations from the cache (working around an `access_parser` memo-column
bug) and verified each reconstruction against the app's own Sum/Min/Max/count.

- **11 game-independent metrics proven exact at 100%** (Odd, Even, Prime, Number
  Sum, Average Value = *floor division*, Unit Number Sum, Unit Number Different,
  Min, Max, First-Last Distance, **AC**).
- **7 adjacency metrics reach 99.8–100% after a definition correction**: the app
  computes adjacency **in draw order, not sorted**, and successive runs count only
  when length ≥2. This corrected docs 02 (§6 Distance, §7 Successive) and doc 03.
- **6 game-relative metrics deferred to T2** (Low/High, Decade ×2, Unit Number
  Group Count, Same-Last-Drawn, Same-End-Units) — unverifiable on this *mixed-game
  rolling cache* (4/5/6-number combos coexist); need single-game data.

Docs patched: 02, 03. New doc: 10. New finding worth its own attention → surfaced
the drawn-order rule, folded into T2's scope.
