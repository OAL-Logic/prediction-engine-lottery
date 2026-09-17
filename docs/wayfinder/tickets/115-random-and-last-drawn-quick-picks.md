---
id: "115"
type: task
status: closed
blocked_by: []
map: samlotto-qt-interface-map.md
created: 2026-09-16
---

# Random Select Numbers + Last-X-Drawings quick pick

## Question

Two small, separately-named SamLotto capabilities, both missing from the existing HOT/COLD/CLEAR/ALL/Odd/Even/Prime quick-select toolbar:
- `extracted_manual/.../Random Select Numbers.htm` — a dedicated random-pick action.
- `extracted_manual/.../How to Quick Picked Numbers.htm` — "you can picked the Hot Numbers, Cold Numbers and **Last x Drawings Numbers** with one click." HOT/COLD already existed; Last-X-Drawings didn't.

## Resolution

- **`select_random_numbers()`** — new "🎲 RANDOM" button in the Quick Select toolbar. `random.sample()` over the active game's real number range for exactly `rules.pick_count` numbers (falls back to the grid's own range/a capped count if rules can't load, matching the existing HOT/COLD buttons' own defensive style).
- **`select_last_drawn_numbers()`** — new "Pick Last-X-Drawings Numbers..." entry in the Quick Selections dropdown. Prompts for N via `QInputDialog`, loads the last N draws (`storage.load_draws(..., limit=N)`), and selects the **union** of every number drawn across them — deliberately not clamped to `pick_count`, matching the manual's own framing of this as a recency-based pool (often larger than a single ticket) rather than a single ready-to-play selection like HOT/COLD/RANDOM.

Both reuse `NumberGrid.select_numbers()` for applying the result (consistent with every other quick-select added this session) rather than the older manual `selected_numbers = set(...)` + per-button restyle loop the original HOT/COLD/Odd/Even/Prime handlers use — no functional difference, just less code, since `select_numbers()` already does the same thing in one call.

**Verified:** `test_select_random_numbers_picks_valid_distinct_count` checks both the count and range hold across two different games (pick_count 15→6 when switching Lotofácil → Mega-Sena). `test_select_last_drawn_numbers` computes the expected union independently (via `storage.load_draws` directly) and asserts the button's result matches exactly; `test_select_last_drawn_numbers_cancelled` confirms a dismissed dialog leaves the pool untouched.

## Also fixed (unrelated, found via this session's regression pass)

`tests/test_desktop_logic.py::test_analysis_tab_stats_table_click` called `AnalysisTab.sync_theme_colors()`, a method that no longer exists — a concurrent session in this repo cleanly renamed it to the now-standard `apply_theme(colors)` used across every tab, and updated every real call site, but this one pre-existing test (calling it directly, externally, as incidental setup unrelated to what the test actually checks) was left stale. Removed the dead call; the test's real subject — click a stats row, confirm the skips drill-down dialog opens — was unaffected.
