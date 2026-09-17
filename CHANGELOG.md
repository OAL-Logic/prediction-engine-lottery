# Changelog

All notable changes to the Lottery Engine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [11.13.0] - 2026-09-16

### Added
- **Random Select Numbers + Last-X-Drawings quick pick (#115)** — the last two named quick-pick actions from the manual's Quick Select pages not yet covered by the existing HOT/COLD/CLEAR/ALL/Odd/Even/Prime toolbar. New "🎲 RANDOM" button (`select_random_numbers()`): `random.sample()` over the active game's real number range for exactly `rules.pick_count` numbers, with the same defensive range/count fallback the HOT/COLD buttons already use if rules can't load. New "Pick Last-X-Drawings Numbers..." Quick Selections entry (`select_last_drawn_numbers()`): prompts for N via `QInputDialog`, then selects the **union** of every number drawn across the last N draws — deliberately not clamped to `pick_count`, matching the manual's framing of this as a recency pool rather than a single ready-to-play pick. Both reuse `NumberGrid.select_numbers()` instead of the older manual per-button restyle loop.
  - Verified: `test_select_random_numbers_picks_valid_distinct_count` (count/range hold across two games with different `pick_count`), `test_select_last_drawn_numbers` (result matches an independently-computed union), `test_select_last_drawn_numbers_cancelled` (dismissed dialog leaves the pool untouched).

### Fixed
- `tests/test_desktop_logic.py::test_analysis_tab_stats_table_click` called `AnalysisTab.sync_theme_colors()`, a method a concurrent session in this repo had cleanly renamed to `apply_theme(colors)` everywhere in production code — this one pre-existing test call site (incidental setup, unrelated to what the test actually checks) was left stale. Removed the dead call.

---

## [11.12.0] - 2026-09-16

### Added
- **Position Number Tickets (#114)** — closes the last gap in SamLotto's 3-tab Build Tickets screen (Standard/Smart already covered by `WheelingTab`'s pool-based wheels; Position had no equivalent). New `desktop/src/widgets/position_tickets_dialog.py`: independent candidate-number list per ticket position, Cartesian product filtered to distinct-numbers-only combinations, sorted and deduplicated, behind a `MAX_POSITION_COMBINATIONS = 200,000` safety cap on the raw product size (same defensive pattern as #108's ticket-store reduction). Launched from a new `WheelingTab` button; re-emits through `WheelingTab`'s own existing `tickets_generated` signal, so it reaches the Ticket Store and Verification Desk via wiring `main.py` already had — no new cross-tab wiring needed.
  - Verified against a hand-computed expected result (a tiny 3-position case worked out by hand: 8 raw combinations → 4 survivors after dropping repeated-number entries and deduplicating), not just "produces some output."

---

## [11.11.0] - 2026-09-16

### Added
- **Save and Load Your Own Favorite Number (#113)** — closes the SamLotto manual's own named capability for this: "💾 SAVE FAVORITES" / "📂 LOAD FAVORITES" buttons in `ProphetDashboard`'s Pool Builder rail, round-tripping the active `NumberGrid` selection through a small JSON file. Distinct from #102's drawing-history `.txt` interop and #110's Ticket Store CSV/TXT export — neither covers a manually-picked pool. Load path validates file shape, warns (with override) on a game mismatch, and reuses `NumberGrid.select_numbers()`'s existing out-of-range clamping rather than re-implementing bounds checks.

---

## [11.10.0] - 2026-09-16

### Added
- **Filter Assistant Wizard (#112)** — GUI counterpart to `lottery filter-assistant`, closing `detailed_features.md`'s distinctly-named "Assistant Filter" SamLotto capability. `desktop/src/widgets/filter_assistant_wizard.py`: a `QWizard` with one page per filter tier (1-5, all populated — 19/22/20/18/20 filters respectively) built from `registry.list_by_tier()`, ending in an elimination-funnel report. The funnel itself (`FilterAssistantFunnelJob`) reuses `engine.cli.commands.filter_funnel`'s exact combination-generation-and-filter-chain logic (same `MAX_COMBINATIONS` cap) rather than reimplementing it — extracted into a QThread, not rewritten. Deliberately independent of `FiltersTab` (#105)/`PruningJob`: SamLotto exposes Assistant Filter and the base filter grid as two different workflows (sequential elimination with built-in filter defaults vs. parallel AND/OR/N-of-M with GUI-configured ranges), matching how the CLI already has two separate commands for this rather than one. Launched via a new button in `FiltersTab`'s header.
  - Verified by cross-checking, not just smoke-testing: `test_filter_assistant_wizard_matches_cli` runs identical filter/pool inputs through both the new job and the real `filter-funnel` CLI command and asserts they agree on the survivor count.

---

## [11.9.0] - 2026-09-16

### Added
- **4 more `AnalysisTab` statistics views (11 → 15), closing the gap to the wayfinder map's own "18-method tabbed statistics" target (#111)** — #107 shipped 11 views from secondary-source summaries without checking them against that specific number; reading the primary source (`extracted_manual/lotto_chm/Interpreting the Statistical/`, the decompiled SamLotto manual's own 18-page Statistics menu) directly found 4 genuinely distinct metrics no existing view covered:
  - **Distance Analysis** — First-Last Distance (span) and max/min adjacent gap, via `get_distance_metrics()`.
  - **Divisibility Analysis** — combines the manual's separate "Divided" (remainder-of-N groups, N=3-10) and "Multiple" (multiples-of-N membership) pages into one view, since Multiple's remainder-0 case is a subset of Divided's full breakdown. Via `get_multiples_count()`.
  - **Prior Drawing Repeat Analysis** — numbers repeated from the immediately preceding draw, via `get_repeated_count()` (`engine.modules.patterns`).
  - **Pair Co-occurrence Matrix** ("Locked Number" in the manual) — historical ball×ball co-occurrence heatmap + per-ball top-partner table; the one new view that's a genuine matrix rather than a per-draw table, so (unlike the other 3) it's deliberately kept ball-indexed, letting the existing skips drill-down work on it for free.
  
  All 4 follow #107's rule: zero new metric math, GUI wiring only, over helpers that already existed in `engine.modules.filters`/`engine.modules.patterns` with no prior caller.

### Fixed
- **`NumberGrid.build_grid()` silently mis-placed every ball for `br/lotomania`** (the one zero-indexed registered game, pool 0-99) — row/column math used `(n - 1) // cols` / `% cols`, correct only when the pool starts at 1. Ball `0` computed row `-1`; Qt's `QGridLayout` silently refuses to place a widget there (logged, not raised), so the "00" button simply never appeared, and every other ball landed one grid cell off from where `(n - self.min_number)` would put it. Found by smoke-testing 11.9.0's new views against all three pool shapes the app supports (`br/lotofacil` 1-25, `us/powerball` 1-69+bonus, `br/lotomania` 0-99) — not something a 1-indexed-only test run could have surfaced. Same shared `NumberGrid` widget backs both the main window's pool builder and #109's Drawings Trend checker, so both were affected; `WheelingTab`'s own independent grid-building code already used the correct `(n - min_n)` form. `test_number_grid_set_range_zero_indexed` previously only asserted ball `0` *existed* in `grid.buttons`, not that it was placed at a valid grid position — extended to check `layout.getItemPosition()` directly, which is what would have caught this originally.

### Changed
- **pyproject.toml** — version bumped to 11.9.0.

---

## [11.8.0] - 2026-09-16

### Added
- **Standalone multiplatform desktop builds** — the desktop app had no distribution story at all (users needed a Python environment, `pip install -e ".[desktop]"`, and to know to run `desktop/src/main.py`). Now packages as a native standalone app via PyInstaller:
  - `lottery-desktop` console-script entry point (`desktop/src/main.py:main`) — `pyproject.toml`'s `[project.scripts]` previously only registered the CLI (`lottery`).
  - `packaging/lottery-desktop.spec` — onedir build (not onefile: this app bundles duckdb/matplotlib/PySide6 and optionally torch/sklearn/lightgbm/xgboost/catboost, which onefile's extract-on-every-launch model handles badly). `hiddenimports` uses `collect_submodules("engine")`/`collect_submodules("desktop")` rather than a hand-maintained list, since both packages are full of dynamic imports (`get_strategy()`, `get_adapter()`, the CLI's own lazy `from engine.cli.commands.X import X as impl` wiring) that PyInstaller's static analysis can't see — a hand-maintained list would silently drift exactly the way the CLI wrapper signatures did (see 11.7.0).
  - `.github/workflows/build-desktop.yml` — Windows/macOS/Linux build matrix (there's no cross-compilation; each OS's artifact comes from actually running PyInstaller on that OS). `workflow_dispatch` for on-demand builds, `v*` tag push for release builds (also attaches all three .zips to the GitHub Release via `gh release upload`). Each non-Windows leg launches the built app headlessly (`QT_QPA_PLATFORM=offscreen`) as a real smoke test, not just "did PyInstaller exit 0."
  - `engine/_paths.py` (new) — `PROJECT_ROOT`, frozen-build aware. `engine/adapters/registry.py` (game registry → `data/registry.yaml`) and `engine/modules/storage.py` (draw database → `data/lottery.db`) both located their data by climbing `Path(__file__).parent` three times, which no longer lands anywhere real once PyInstaller extracts the source tree into its own bundle layout — the two now import `PROJECT_ROOT` instead of each re-deriving it. Uses `sys._MEIPASS` (PyInstaller's own runtime answer to "where are the bundled `datas=[...]` files"), not `sys.executable`'s directory — a first attempt at the latter built cleanly but silently pointed at an empty directory, because PyInstaller 6.x's onedir layout puts everything except the executable itself under `_internal/`. Caught by actually launching the packaged binary and confirming the registry/database load, not just checking that the build succeeded. The other ~28 files with the same `Path(__file__).parent...` pattern are untouched — deliberately: they're all CLI-only commands (calendar export, logs, alerts, profiles, watchlists) the desktop app never calls in-process, so fixing all of them wasn't necessary for this to work and would have meant re-verifying 28 independent relative-path computations for no behavioral gain.
  - README `## 🖥️ Desktop App` section — didn't exist before; the only prior desktop-launch instructions were "Desktop & API" as a `pip install -e ".[all]"` footnote with no follow-up.
  - `[project.optional-dependencies].packaging` (`pyinstaller>=6.0`) extras group.

### Fixed
- Local build note: PyInstaller's final copy-into-`dist/` step reliably failed with `OSError: [Errno 5] Input/output error` on multi-gigabyte files (`nvidia/nccl/lib/libnccl.so.2`, then `torch/lib/libtorch_cuda.so`) when `--distpath`/`--workpath` pointed under this WSL environment's `/mnt/c/...` mount — a 9p-protocol large-file reliability issue, not a spec defect. Resolved by pointing both at a native Linux path instead (documented in the README as a build note, not worked around in the spec itself, since GitHub Actions runners — the actual multiplatform build path — don't have this problem).
- Excluded torch's bundled `nvidia.*`/`cuda`/`cusparselt` CUDA redistributables from the build (`excludes` in the spec): `PredictionTab`'s "Enable CUDA Acceleration" checkbox doesn't currently route any strategy onto a CUDA device (`run_prediction_job_from_predict_center` only logs a message when it's checked), so bundling several GB of CUDA runtime libraries had no functional benefit — found while chasing the I/O error above, kept regardless since it also shrinks the build substantially.

### Changed
- **pyproject.toml** — version bumped to 11.8.0.

---

## [11.7.0] - 2026-09-16

### Fixed
Full-suite health pass (776 passed / 13 failed / 4 skipped baseline → 3 environmental-only remaining). Two systemic bug classes found via a full `pytest` run plus a purpose-built AST checker comparing every `engine/cli/main.py` wrapper's `impl(...)` call against the real command's signature (`engine.cli.commands.*`):

- **`lottery tune` silently ran the wrong feature on every normal invocation.** `tune()`'s real implementation (`engine/cli/commands/tune.py`) has a `stacking: bool` parameter (added for "STORY 7.3: Specialized Stacking Mode") between `no_grid` and `metric`; the `main.py` wrapper was never updated to match and called `impl(lottery, draws, limit, strategies, no_grid, metric, top, fmt, output, export_md, min_training)` — 11 positional args into a 12-parameter function. Every argument from `metric` onward silently shifted one slot: `stacking` received the `metric` string (always truthy), so `lottery tune <game>` always ran Stacking AI meta-learner training instead of the requested grid-search tuning, while `metric`/`top`/`fmt`/`output`/`export_md`/`min_training` each silently received the next parameter's value. Fixed by adding the missing `stacking` option to the wrapper and correcting the call.
- **The same wrapper/impl drift pattern, found by the AST checker, in 3 more commands** — each just missing a trailing parameter (not corrupting, since defaults absorbed the gap, but silently making a documented flag inaccessible from the actual CLI): `lottery scan` (`--offline` — could never skip network-dependent OSINT layers), `lottery daemon` (`--once` — could never run a single optimization cycle and exit; was stuck in the infinite loop), `lottery calibrate` (`--metric` — always used the `lift` default). The checker script (ad hoc, not committed) also confirmed `lottery record`'s equivalent gap (a `db_path` param) is `hidden=True` / testing-only, so left as-is, and flagged `lottery report-elite`/`lottery bio` as unrelated missing-optional-dependency errors (`fpdf`, `skbio` — never installed in this environment, not a code issue).
- **The CLI's 30-minute runaway-command watchdog (`SIGALRM`) was armed at module *import* time**, not per command invocation — harmless for a normal one-shot `lottery <cmd>` process, but any process that imports `engine.cli.main` and lives past 30 minutes (the test suite; potentially `engine/cli/commands/profile.py`'s saved-preset runner) gets `sys.exit(1)`'d wherever it happens to be 30 minutes after *import*, not after the command that's actually running. Reproduced as `tests/test_strategy_roster.py::test_select_strategies_registered_and_dry_run_completes` — a cheap `--dry-run` — timing out because the suite's total runtime crossed 30 minutes while that test happened to be executing. Moved the `signal.alarm(1800)` call into `main_callback` (fires once per actual command dispatch instead of once per import) and made `lottery daemon` (the one command meant to run indefinitely) explicitly cancel it via `signal.alarm(0)`. Also found and fixed a latent naming collision this surfaced: `main.py` defines a `signal` CLI command (`def signal(...)`) that shadows the stdlib `signal` module at module scope for every line after it — aliased the import to `os_signal`.
- **`harmony.py`'s `successive_2`/`successive_3`/`successive_4` filters** — see 11.6.0, same root cause class (stale/absent attribute), listed here too since it's part of the same health pass.
- `tests/test_architect_compliance.py` — both tests used `registry._filters`, an attribute that's never existed on `VectorRegistry` (it's `_instances`, populated lazily via `.get()`). Fixed to discover + resolve all filters via the registry's real public-ish surface (`_discover()` + `_module_map` + `.get(uid)`, the same pattern `desktop/src/tabs/filters.py` already uses). Both AC-numbered compliance checks (sub-1ms per filter over 10k tickets; filters don't mutate their input buffer) now actually run, and pass.
- `tests/test_cli_commands_smoke.py::test_hedge_smoke` — asserted the stale exact phrase `"Hedge Portfolio"`; the command's title has read "Combinatorial Hedging & Portfolio Balance" for a while. Checks `"Portfolio Allocations"` (the actual results table) instead.
- `tests/test_desktop_telemetry.py::test_desktop_client_receives_ws` — not fixed, marked `xfail` with the diagnosed root cause: `qtbot.waitSignal()`'s blocking nested Qt event loop starves the same-thread `pytest-asyncio` loop the test's mock websocket server needs to complete its handshake, so the client reliably times out regardless of system load. Needs a real Qt/asyncio bridge (e.g. `qasync`) to fix properly; not chased further since `TelemetryClient`'s only real counterpart — `gateway/`, the Go telemetry hub it talks to — has had zero commits since the project's initial commit and isn't part of the actively maintained system (confirmed via `git log -- gateway/`).

### Not fixed — confirmed environmental, not code bugs
- `test_cli_commands_smoke.py::test_daily_export_md` — `PermissionError` writing to a `tempfile.NamedTemporaryFile` path; a known WSL/`/mnt/c` file-locking quirk, not reproducible as a real defect.
- `test_cosmic_quantum.py` (both tests) — `pennylane`/`braket` (quantum computing SDKs for the `QuantumSidecar` entropy-distillation novelty feature) aren't installed in this environment and aren't in any `pyproject.toml` extras group.
- `test_lazy_filters.py::test_lazy_loading_registry` — passes in isolation (36/36 confirmed); fails only as part of the full suite because some earlier test legitimately triggers filter-registry resolution, which (correctly) leaves `tier1_structural` etc. cached in `sys.modules` for the rest of the process. Suite-order artifact, not a regression in the lazy-loading contract itself.

---

## [11.6.0] - 2026-09-16

### Added
- **Desktop cockpit — closes the `samlotto-qt-interface` wayfinder map (tickets #107-#110; map now has no open fog)**:
  - **High-density statistics tabs (#107)** — `AnalysisTab` grew from 4 to 11 views: Odd/Even & High/Low Balance, Arithmetic Complexity (AC) Distribution, Root Sum Distribution, Decade Distribution, Consecutive Groups Analysis, Prime & Composite Balance, and Unit Digit Analysis, alongside the existing Frequency Distribution/Actual Skips/Sum Range Bell Curve/Positional Matrix Heatmap. All 7 new views reuse `engine.modules.filters`' per-ticket metric helpers (`get_ac_value`, `get_root_sum`, `get_successive_metrics`, etc. — the same functions `PruningJob`/`LimitsCalculationJob` already use for ticket filtering) applied historically across `df_draws`, rather than reimplementing any metric math.
  - **Ticket Store WRG reduction (#108)** — `engine.modules.wheels_wrg.WheelingEngine.reduce_tickets()` existed with zero callers anywhere in the codebase; wired up as `TicketStoreReductionJob` (`desktop/src/telemetry/manager.py`), exposed via a new "🎯 REDUCE (WRG)" Ticket Store toolbar button and context-menu action. Prompts for the t-if-m guarantee (defaulting to the active game's pick-count/pick-count-1) and refuses upfront if the coverage universe `C(pool_size, m)` exceeds 50,000 target subsets, since the underlying greedy set-cover loop is plain Python with no interruption support and would otherwise hang the job indefinitely.
  - **Real ticket printing (#108)** — `ProphetDashboard.print_tickets()` was a pure stub (`QMessageBox` claiming success, no printer ever touched). Replaced with a real `QPrinter`/`QPrintDialog`/`QTextDocument` flow.
  - **Drawings Trend manual predictor (#109)** — `AnalysisTab` gained a "Drawings Trend — Manual Number Checker" panel reusing the existing `NumberGrid` widget as-is, with its own `numbers_recommended` signal wired to the same `handle_push_to_pool()` slot `PredictionTab` uses. Deliberately not tied to any view's computed data — the point (and the reason it's separate from #106's algorithmic Predict Center) is a manual, opinion-driven pick.
  - **CSV ticket export (#110)** — `export_tickets()` gained a CSV filter (stdlib `csv` module, `Index,Numbers,Score` with header) alongside the pre-existing `.txt` export.

### Fixed
- **`harmony.py`'s `successive_2`/`successive_3`/`successive_4` filters would `KeyError` the moment anyone actually applied them** — found while surveying `engine.modules.filters` for #107's reusable metrics. They called `get_successive_metrics(ticket)["groups_of_2"/"groups_of_3"/"groups_of_4"]`, keys that function never returned (only `max_successive`/`groups`); no test previously exercised these three registered filters. Extended `get_successive_metrics()` to also return `groups_of_2`/`groups_of_3`/`groups_of_4` (backward compatible), with regression coverage in `tests/test_modules_filters.py`.
- **Stale wayfinder docs** — the map's "Not yet specified" section still listed the GUI's online database updater (`DatabaseTab.sync_online_draws()`/`FetchWorker`) as unbuilt fog; it was already implemented. Corrected.

### Changed
- **pyproject.toml** — version bumped to 11.6.0.

---

## [11.5.0] - 2026-09-16

### Added
- **3 orphaned BR adapters reconnected to the registry** — `dupla_sena`, `dia_de_sorte`, and `lotomania` had complete, working `LotteryAdapter` classes and were already wired into `get_adapter()`'s adapter map, but were never added to `data/registry.yaml`, so the CLI reported them as unavailable. Added registry entries (`br/dupla-sena`, `br/dia-de-sorte`, `br/lotomania`) with verified draw schedules. Lotomania draws 00-99 (zero-indexed), which the registry schema couldn't express before — added `GameDefinition.number_range_min` (default 1, backward compatible) to `engine/adapters/registry.py`.
- **Mega Millions and EuroMillions adapters** (`engine/adapters/us/mega_millions.py`, new `engine/adapters/eu/` package + `euro_millions.py`) — both were placeholder `data_available: false` rows in the registry ("Placeholder for expansion"). Mega Millions uses the same NY Open Data Socrata source as `powerball` (resource `5xaw-6ayf`, verified live). EuroMillions has no single official open API (operators are national lotteries, not one body); uses a community-maintained, GitHub-Actions-updated CSV archive as its source, treated as best-effort the same way `CaixaBaseAdapter` treats its own community bulk mirror, with the local DB cache as the fallback of record.
- **`ADAPTER_MAP` promoted to module level** (`engine/cli/utils.py`, was a local dict inside `get_adapter()`) plus a new `tests/test_adapters_registry_consistency.py`: for every `data_available: true` registry row, its adapter must resolve and its rules must match; and for every `ADAPTER_MAP` entry, some registry row must reference it. The second direction is exactly the check that would have caught the orphaned-adapter gap above; both directions are now guarded so it can't recur, for these adapters or future ones.
- **`tabfm` strategy** (`engine/strategies/foundation/tabfm_forecast.py`) — the TabFM half of TODO.md's foundation-model integration plan that `timesfm`'s docstring flagged as "a natural follow-on ... not implemented [t]here." Google has no public standalone "TabFM"; implemented via Prior Labs' TabPFN (`pip install 'lottery-engine[foundation]'`, same optional-dependency group as `timesfm`), doing in-context tabular classification over engineered per-number features (gap, rolling frequency, historical mean gap, parity, pool position) rather than `timesfm`'s per-number univariate time series. Deliberately drops moon/solar/pair-synergy features from the original plan to stay offline-computable and fast to test.
- **SamLotto Qt interface — ticket #106 (Prediction & Verification GUI)**, closing the `samlotto-qt-interface` wayfinder map (`docs/wayfinder/samlotto-qt-interface-map.md`) alongside #105:
  - `PredictionTab` gained a live Formula (strategy family, from `STRATEGY_PRESETS`) → Algorithm (specific strategy) drill-down, replacing a hardcoded 5-item model list that `run_prediction_job` never actually read. Also added Offset/Depth controls (predict as of N draws ago, over an M-draw window) and a "Push to Pool" button/`numbers_recommended` signal wired to a new `NumberGrid.select_numbers()`.
  - `ForecastJob` gained an `offset` parameter (default 0, backward compatible) to back the Offset control.
  - `VerificationTab` gained a second "Formula Leaderboard" sub-tab (the existing single-ticket-set auditor is unchanged, now under a "Ticket Auditor" sub-tab) that walk-forward backtests checked formulas and ranks them by win rate. Backed by a new `FormulaVerificationJob` — a thin `QThread` wrapper around the already-existing `engine.services.backtest.run_backtest()`; no backtest logic was reimplemented.
  - The three lottery-picker combo boxes (`ProphetDashboard.game_combo`, `PredictionTab.lottery_combo`, `DatabaseTab.lottery_selector`) were each a hardcoded 3-game list (Lotofácil/Mega-Sena/Powerball) — the same "list doesn't match the registry" gap as the CLI's `ADAPTER_MAP` issue above, just in the GUI, and one this session's own registry additions would have made worse (all 10 available games are meant to be pickable). All three now populate from `registry.list_games(only_available=True)`. Doing so exposed a second, latent bug: `ProphetDashboard.change_global_lottery`'s NumberGrid sizing was a 3-game if/elif that defaulted every other game (now 7 of 10) to a wrong 25-number grid — replaced with a registry-driven lookup. `NumberGrid` gained `set_range(min, max)` (formerly `set_max_number` only, which assumed 1-indexed) so Lotomania's 00-99 pool renders correctly. Also fixed: the combos' item order no longer happens to start with Lotofácil, so the dashboard now does one explicit `change_global_lottery()` sync call at startup instead of relying on that coincidence.

### Fixed
- **Full test suite couldn't complete in one process — `Fatal Python error: Aborted`.** Six test files (`test_desktop_gateway.py`, `test_desktop_logic.py`, `test_desktop_telemetry.py`, `test_number_dossier_dialog.py`, `test_pattern_search_dialog.py`, `test_quick_calculator.py`) each had an `app` fixture creating a bare `QCoreApplication` instead of `QApplication`. Qt keeps one application singleton per process regardless of which subclass creates it, and `test_desktop_gateway.py` collects alphabetically before any real widget test — so its `QCoreApplication` became *the* singleton for the rest of the run, and the first real `QWidget()` built afterward (anywhere in the suite) hit a native abort, since a `QCoreApplication` never initializes the GUI subsystems a widget needs. Reproduced reliably with just two tests (`test_desktop_gateway.py` + `test_desktop_integrity.py::test_database_tab_init`); fixed by switching all six fixtures to `QApplication`. Full suite now runs end-to-end (733 passed, 19 failed — all pre-existing/environmental, see below — 14 skipped, in ~32 min) instead of aborting partway through.
- `TestStrategyRegistry::test_valid_tiers` hardcoded `{"statistical", "ml", "deep", "fun"}` and never got the `foundation` tier added — failing since 11.4.0's `timesfm`, and again on this release's `tabfm`. Added `"foundation"` to the valid set.
- **`lottery odds --compare` rendered an empty table for every registered game.** `_run_comparison()` built its rows from `GameDefinition.to_rules()`, which never sets `DrawRules.odds` — and `compare_lotteries()` silently skips any game with `jackpot_odds == 0`. A unit test already covered this (`TestOddsComparator::test_compare_lotteries`) but its assertion was `len(results) >= 0`, true regardless of the bug, so it never caught it. Fixed by building the comparison from each game's real adapter rules (`get_adapter(g.id).rules`) instead, which also model bonus-ball jackpot odds correctly (e.g. Powerball's 5-white + 1-red) where a generic `comb(pool, pick)` fallback couldn't. Backfilled the jackpot-tier `odds` that were missing from `quina`, `mais_milionaria`, `dupla_sena`, and `dia_de_sorte`'s adapters (pure combinatorics from each adapter's own already-defined pick/pool/bonus numbers) and from the new `euro_millions` adapter above. `lotomania` is deliberately left unmodeled: its 50-picks-of-100/20-drawn mechanic doesn't fit `DrawRules`' single-`pick_count` model, and a naive `comb()` would be wrong, not just approximate.
- `lottery odds --compare`'s efficiency score (`log10(odds) / ticket_price`) mixes currencies without conversion — already possible with Powerball vs. BR games, more visible now with EuroMillions added. Its existing footnote didn't mention this; extended it to say so explicitly whenever the compared set spans more than one currency. The jackpot-odds ranking itself is unaffected (pure probability, currency-independent).

### Changed
- **pyproject.toml** — version bumped to 11.5.0; `[foundation]` extras now also installs `tabpfn`.
- **README.md** — Foundation tier row now lists both strategies; corrected "Supported Lotteries: 150+ (registry)" (registry only ever had 7-9 entries) and "Strategy Tiers: 4" (Foundation already existed as of 11.4.0) to their actual counts.

---

## [11.4.0] - 2026-09-16

### Added
- **Strategy roster & meta-selection** — closes out the `strategy-pruning-meta-selection-map` wayfinder effort (tickets #001–#004; see `docs/wayfinder/decisions/003-policy-thresholds-decision.md` and `004-cli-ux-prototype-decision.md`):
  - `select-strategies <game>` — evaluates every candidate strategy's empirical lift (from `data/calibration_cache.json`, with a live `lottery prune`-style audit fallback for anything uncalibrated) against a documented policy (must beat random; `--min-lift` to tighten it), and persists the result to `data/strategy_roster.json`. Supports `--pin`/`--exclude` overrides, `--dry-run`, `--export-md`.
  - `forecast`/`rank-numbers --strategies roster` — consumes that saved roster, through a new shared `resolve_strategies()` seam in `engine/cli/utils.py` (falls back to the `default` preset with a warning if no roster exists yet or it resolves to zero active strategies).
- **`timesfm` strategy** — new `foundation` strategy tier (`engine/strategies/foundation/`): zero-shot forecast per number's binary hit-indicator series via Google's TimesFM 2.5, following the same lazy-optional-dependency pattern as `ml`/`deep`. Opt-in: `pip install 'lottery-engine[foundation]'` (not bundled in `[all]` — downloads ~800MB of model weights from Hugging Face on first use). Implements the TimesFM half of the integration plan in `TODO.md`; TabFM is a natural follow-on in the same tier, not yet implemented.

### Fixed
- `load_local_config()` (`engine/cli/utils.py`) was merging the *entire* contents of every `*.local.yaml` file in the project root, not just personal-numerology fields — so a same-named-convention file for an unrelated purpose (e.g. a `report`-pipeline template with its own top-level `name`/`steps` keys) would leak a `name` key into `get_strategy(name, **personal_data)`, raising `TypeError: get_strategy() got multiple values for argument 'name'` for **every** strategy. Silently swallowed by the broad `except Exception` around strategy execution in `forecast`/`suggest`/`tune`/`report`, it surfaced only as an unexplained "No strategies produced scores." Found while verifying `forecast --strategies roster` end-to-end on this repo's own `family_report_template.local.yaml`. Fixed by extracting only the two keys the function has always documented (`full_name`, `birth_date`) instead of merging each file wholesale.
- `lottery suggest --kelly` (`_print_single_result` in `engine/cli/commands/suggest.py`) raised `UnboundLocalError: cannot access local variable 'Panel'` and silently skipped every strategy. A stray `from rich.panel import Panel` further down in the same function (for the unrelated `placidus_wheel` panel) made Python treat `Panel` as function-local for the *whole* function, breaking the earlier, module-level-intended use in the Kelly panel. Was previously masked in `test_suggest_kelly_smoke` by the `load_local_config()` bug above throwing first; fixed by removing the redundant local import (module-level `Panel` already covers it).

### Changed
- **pyproject.toml** — version bumped to 11.4.0; new `[foundation]` optional-dependency group.

---

## [11.3.0] - 2026-09-15

### Added
**24 new capabilities**, closing gaps against the SamLotto feature catalog (`detailed_features.md`) and general engine QoL. Each shipped as its own commit:

- **Deterministic seeding** — `--weather-seed` on `genetic-wheel`/`suggest` derives a reproducible RNG seed from real weather/lunar/solar data instead of OS entropy; `seed-audit` previews it for any date without running a full generation.
- **Historical lookup** — `record` (manual draw entry/correction — the "DrawingsUpdate" equivalent), `pattern-search` (nsSearch-style historical overlap ranking), `twin-draws` (most-similar historical draw pairs), `draw-anniversary` (on-this-day-in-history lookup), `number-lifecycle` (per-number historical dossier), `ticket-backtest` (replay one fixed ticket across all history), `pair-trend` (rolling co-occurrence trend), `number-clique` (mutually co-occurring groups of k numbers, not just pairs).
- **Filter tooling** — `filter-funnel` (elimination-tracking report; the first real consumer of the previously-unused 100+ filter registry), `filter-assistant` (guided tier-by-tier filter picker — the "Assistant Filter" wizard equivalent), `--list-filters` catalog browser.
- **Tickets & data** — `combo-diff` (structural ticket comparison), `batch-grade` (bulk structural screening from a file), `random-baseline` (empirical structural control group from pure-random tickets).
- **Data integrity & ops** — `storage-consistency` (DuckDB vs JSON partition cross-check), `data-status` (cached-data freshness across every registered game), `config-check` (environment/setup health check), `pair-graph-export` (GraphML/DOT co-occurrence network export).
- **Workflow** — `profile` (save/list/show/delete/run named CLI presets), `calendar-export` (.ics upcoming-draw export).
- **Desktop (PySide6)** — Quick Calculator (combinatorics/bet-cost popup — the "PopupCalculator" equivalent), Pattern Search dialog, Number Dossier dialog.

### Fixed
- `--weather-seed` was not actually reproducible for same-day repeated calls: `fetch_weather`/`fetch_seismic_mag`/`fetch_solar_kp` each hit their live upstream API uncached on every call, so two runs made minutes apart on the same day could land on different readings and silently produce different seeds. Each is now cached for the rest of the calendar day.

### Changed
- **pyproject.toml** / **FastAPI sidecar** — version bumped to 11.3.0.

---

## [11.2.0] - 2026-05-29

### Added
- **6 new API endpoints** closing Sprint 2 planned gaps:
  - `GET /health` — Service health check with uptime, version, resource counts
  - `GET /games/{name}/sum-distribution` — Sum probability PMF with 70% range
  - `GET /games/{name}/gap/{number}` — Per-number gap/overdue analysis
  - `GET /games/compare` — Cross-game odds comparison
  - `POST /games/{name}/wheel` — Wheel generation (full/key/abbreviated)
  - `POST /games/{name}/ticket-grade` — Multi-dimension ticket grading (A+ → F)
- **8 new Pydantic models** for API endpoint request/response schemas
- **Comprehensive test suite** (`test_api_and_integration.py`) covering:
  - API model serialization, sum range integration, deviation analysis
  - Wheels module, odds comparator, strategy registry integrity
  - CLI command importability for 13 key commands
- **CHANGELOG.md** — this file (project-wide release notes)

### Changed
- **README.md** — Complete rewrite reflecting 100+ CLI commands, 80+ strategies, full architecture
- **pyproject.toml** — Version bumped to 11.2.0, removed duplicate dependencies (numexpr, bottleneck), updated description, added fastapi/uvicorn to `[all]` extras
- **API version** — Updated from 0.1.0 to 11.2.0

### Fixed
- Duplicate `numexpr>=2.10.2` and `bottleneck>=1.4.2` entries in pyproject.toml core dependencies
- `[all]` optional dependency group was missing `fastapi` and `uvicorn`

---

## [11.1.0] - 2026-05-28

### Added
- **Portfolio Dashboard** — Multi-lottery combo play simulation with HTML export
- **Expert Suggest API** — `POST /games/{name}/expert-suggest` endpoint
- **Sacred Manifold API** — `POST /games/{name}/sacred-manifold` and transit endpoints
- **Portfolio simulation tests** — `test_portfolio_dashboard.py`

---

## [11.0.0] - 2026-05-12

### Added
- **Quantum-Astro Intelligence Tier** — Arcsecond-accurate planetary calculations via AstroPy
- **Prophet ML Tier** — XGBoost/CatBoost/LightGBM regressor ensemble
- **LSTM-CRF Strategy** — Sequence labeling for inter-number dependency modeling
- **Stacking AI** — Meta-learner stacking ensemble
- **Desktop Client** — PySide6 analytical cockpit

---

## [10.0.0] - 2026-05-03

### Added
- **Diagnostic Terminal** (Sprint 2.36) — `signal`, `cluster`, `stress-test`, `--explain`
- **Esoteric Overlay** (Sprint 2.37) — `detect-patterns`, `leaderboard`, Obsidian DataviewJS
- **Daily Automation** (Sprint 2.38-2.40) — `log`, `forecast`, `daily`, `alert`, post-fetch hooks
- **Regime Detection** (Sprint 2.39) — `compare-draws`, `trend`, `next`, Jensen-Shannon divergence
- **Watchlist** (Sprint 2.41) — Batch game tracking sub-application
- **Calibration** (Sprint 2.45) — Empirical out-of-sample hit-rate calibration
- **Analytics Expansion** (Sprint 2.40-2.60) — 25 new CLI commands
- **Total CLI commands**: 100+
- **Total strategies**: 80+

---

## [9.0.0] - 2026-04-29

### Added
- **FastAPI Sidecar** (Sprint 2.1) — REST API with 12+ endpoints
- **Go Gateway** (Sprint 3) — Auth, rate limiting, caching proxy
- **Expo App** (Sprint 4) — React Native + Web dashboard
- **Analysis Dashboard Phase 2** — Spatial voids, Z-score scaling
- **Advanced Metrics Strategy** — AC Value, Root Sum, Unit Sum

---

## [8.0.0] - 2026-04-28

### Added
- **30+ new strategies** across statistical, ML, and fun tiers
- **100+ structural filters** — sum-range, parity, consecutive, decade breadth, etc.
- **Board command** — Rich terminal visualization with multiple views
- **Wheels module** — Full/key/abbreviated covering designs
- **150+ game registry** — Global lottery catalog in YAML
- **DuckDB integration** — High-performance analytical database
- **MCP server** — Model Context Protocol integration

---

## [7.0.0] - 2026-04-27

### Added
- **Absurdity Engine v4-v10** — 9 new strategies (primes, quantum, kabbalistic, ley_lines, etc.)
- **Sacred Manifold** — Dodecahedron geometry module
- **Intentional Seeding** — SHA256-based deterministic ticket generation
- **Chaos Temperature Governor** — Environmental chaos modulation

---

## [1.0.0] - 2026-04-26

### Added
- **Core Engine** — 23 strategies, 3 ensembles, 6 CLI commands
- **Adapters** — Mega-Sena, Lotofácil, Powerball
- **Analysis modules** — Frequency, deviation, correlation
- **Backtest** — Blind historical strategy testing
- **Optimize** — Grid search over strategy × history × temperature
- **Chi² gate** — Statistical significance testing on all predictions
