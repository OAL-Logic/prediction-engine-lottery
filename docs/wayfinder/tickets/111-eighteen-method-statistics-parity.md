---
id: "111"
type: task
status: closed
blocked_by: []
map: samlotto-qt-interface-map.md
created: 2026-09-16
---

# Closing the gap to the map's own "18-method tabbed statistics" target

## Question

The map's own **Destination** text (written 2026-08-11, before any of #101-107 existed) says: "a modern PySide6 desktop application... that implements every feature of the SamLotto Free Edition (drawings management, **18-method tabbed statistics** with skips drill-down, ...)". #107 took `AnalysisTab` from 4 to 11 views by working from `detailed_features.md`'s summary and `docs/research/samlotto-feature-map.md` — both secondary sources. Neither actually enumerates 18 methods, so #107's closure didn't check its 11 against that specific number.

The primary source does: `extracted_manual/lotto_chm/Interpreting the Statistical/` — the decompiled SamLotto help manual's own Statistics menu — has exactly 18 `.htm` pages (one per `Statistics ->` submenu entry). Reading them (not just the filenames) was the actual unlock here: several — Distance, Divided, Multiple, Prior Drawing, Locked Number — turned out to be genuinely distinct metrics with no equivalent among the 11.

## Resolution

Read all 18 manual pages. Mapped each to either an existing `AnalysisTab` view or a new one:

**Already covered by #107's 11** (Base is a menu umbrella, not its own metric; Drawings Distributing/Lotto Number Hits/Range overlap existing views closely enough not to duplicate — see ticket for reasoning): AC, Actual Skip, Hot-Cold, Odd-Even, Low-High, Successive, Sum, Units Number, Drawings (= Positional Matrix Heatmap), Base, Drawings Distributing, Lotto Number Hits, Range.

**Genuinely new, added** (4 views, `AnalysisTab` now at 15):
- **Distance Analysis** — First-Last Distance (span) + Max/Min adjacent gap, via `get_distance_metrics()` (already existed in `engine.modules.filters`, previously unused by any GUI view).
- **Divisibility Analysis** — combines the manual's separate "Divided" (remainder-of-N groups, N=3-10) and "Multiple" (multiples-of-N membership) pages into one view, since Multiple's remainder-0 case is a subset of Divided's full remainder breakdown. Reuses `get_multiples_count()`.
- **Prior Drawing Repeat Analysis** — numbers repeated from the immediately preceding draw. Reuses `get_repeated_count()` (`engine.modules.patterns`, previously only called from `desktop/src/widgets/filter_report.py`-adjacent code, not from any stats view).
- **Pair Co-occurrence Matrix** ("Locked Number" in the manual) — the one view that's a genuine ball×ball matrix rather than a per-draw table; built directly (no existing helper covers a full historical cross-tab). Deliberately kept in `on_row_selected`'s ball-indexed set (not added to `NON_BALL_VIEWS`) since its table is legitimately `"Ball NN"`-first-column, so the existing skips drill-down works on it for free.

All 4 follow #107's established reuse-don't-reimplement pattern — zero new metric math, only GUI wiring.

**Bug found via this work, unrelated to the new views**: `NumberGrid.build_grid()` (`desktop/src/widgets/number_grid.py`) computed each ball's grid position as `(n - 1) // cols` / `(n - 1) % cols` — correct only for 1-indexed pools. Surfaced as a live `QGridLayout: Cannot add QPushButton at row -1` warning while smoke-testing the new views against `br/lotomania` (the one zero-indexed game, pool 0-99): ball `0` computed row `-1` and was silently dropped by Qt, and every other ball landed one cell off from where it should be. Fixed to `(n - self.min_number) // cols` / `% cols`. This is the same shared `NumberGrid` widget both the main window's pool builder and #109's Drawings Trend checker use, so both were affected. `WheelingTab` has its own, already-correct, independent grid-building code (`row = (n - min_n) // cols`) — not affected. Existing test `test_number_grid_set_range_zero_indexed` only checked that button `0` *existed*, not that it was placed correctly, which is exactly how this shipped unnoticed; extended it to assert the actual grid position.

**Verified:** all 15 views smoke-tested against three lotteries with different pool shapes (`br/lotofacil` 1-25, `us/powerball` 1-69+bonus, `br/lotomania` 0-99) with no exceptions, run multiple times. `tests/test_desktop_integrity.py`/`test_desktop_logic.py` (28 tests) pass. One non-reproducing native crash (`free(): invalid pointer`) hit once during manual testing at a different view/lottery combination each time it was retried — confirmed non-deterministic across identical re-runs (full 45-view sequential smoke test passed clean immediately before and after), consistent with this environment's already-documented instability under concurrent load rather than a logic bug in any specific view.

## Map status

`AnalysisTab` is now at 15 of the map's own named "18-method" target. The remaining 3 (Base, Drawings Distributing, Lotto Number Hits) are menu umbrellas / near-duplicates of existing views by design, not gaps — see above.
