---
id: "107"
type: task
status: closed
blocked_by: []
map: lottery-studio-qt-interface-map.md
created: 2026-09-16
---

# High-density statistics tabs

## Question

The map's "Not yet specified" section flagged deciding "how to present the 11+ statistics sheets (AC, Low-High, Sums, etc.) cleanly inside the tabbed stats workspace without overwhelming the screen" as fog. `AnalysisTab` (`desktop/src/tabs/analysis.py`) only had 4 views (Frequency Distribution, Actual Skips, Sum Range Bell Curve, Positional Matrix Heatmap) against `detailed_features.md`'s "Statistical Analysis Engine" catalog and the 5-tier filter taxonomy in `docs/research/Lottery Studio-feature-map.md`.

## Resolution

Kept the existing single-combo-box + chart + table + diagnostic-summary layout (already answers "without overwhelming the screen" — one view at a time, not 11 simultaneous panels) and added 7 more entries, reusing the historical-array-over-`get_*()` pattern already established in `engine/strategies/statistical/advanced.py` (`ac_hist`, `root_hist`, `unit_hist`, `succ_hist`) instead of introducing new metric math:

- Odd/Even & High/Low Balance — `get_odd_count`, `get_high_low_counts`
- Arithmetic Complexity (AC) Distribution — `get_ac_value`
- Root Sum Distribution — `get_root_sum`
- Decade Distribution — bucketed ball-frequency histogram + `get_decade_metrics` for the contiguous-groups summary stat
- Consecutive Groups Analysis — `get_successive_metrics`
- Prime & Composite Balance — `get_prime_count`, `get_composite_count`, `PRIMES`
- Unit Digit Analysis — `get_unit_metrics`

All 7 pull from `engine.modules.filters`, the same module `PruningJob`/`LimitsCalculationJob` (`desktop/src/telemetry/manager.py`) already use for ticket filtering — no metric logic was reimplemented. `AnalysisTab` now has 11 views, closing the "11+ statistics sheets" gap.

Also extended `on_row_selected`'s view-type guard (previously a single `== "Sum Range Bell Curve"` check) to a `NON_BALL_VIEWS` set covering all 7 new views, since their table's first column is Draw ID / bucket / digit rather than `"Ball NN"` — without the guard, the skips drill-down's `int(text)` fallback would have misparsed those as ball numbers.

Bug found and fixed via this work (unrelated to the new views, found while surveying `engine.modules.filters` for reusable metrics): the registered filters `successive_2`/`successive_3`/`successive_4` in `engine/modules/harmony.py` called `get_successive_metrics(ticket)["groups_of_2"/"groups_of_3"/"groups_of_4"]`, keys that function never returned (only `max_successive`/`groups`) — a guaranteed `KeyError` the moment any of those three filters were actually applied (no test caught it since none existed). Extended `get_successive_metrics()` to also return `groups_of_2`/`groups_of_3`/`groups_of_4` (backward compatible — existing keys/values unchanged), with regression tests in `tests/test_modules_filters.py`.

**Verified:** smoke-tested all 11 views against two lotteries with different pool sizes/pick counts/bonus structure (`br/lotofacil` 1-25 pick-15, `us/powerball` 1-69+bonus pick-5) with no exceptions; existing `test_analysis_tab_init` / `test_analysis_tab_stats_table_click` still pass; `tests/test_modules_filters.py` (19 tests, including the 3 new ones) passes.

## Not done here (separately tracked / still fog)

- **Drawings Trend manual predictor (E5)** — a manual visual-frequency-chart number checker feeding the pool. Different from these read-only diagnostic views (needs click-to-toggle + a "push to pool" signal like `PredictionTab`'s). Still fog, see map.
- **Optimization/wheeling port, Export & Print formatting** — untouched, still fog, see map.
