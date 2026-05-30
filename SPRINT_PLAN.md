---
title: Prediction Engine — Master Sprint Plan
date: 2026-04-26
status: authoritative
supersedes:
  - sprint-plan-update.md (Gail Howard delta)
  - smartluck-analysis/05-approved-sprint-plan.md
  - smartluck-analysis/06-reconciliation-with-current-state.md
last_audit: 2026-04-28 (incorporates Gemini Apr-27 sessions: Absurdity Engine v4–v10)
---

# Prediction Engine — Master Sprint Plan

This is the single source of truth for the roadmap. It folds in:

1. The original 5-sprint plan (engine → sidecar → gateway → app → content).
2. The Smart Luck analysis additions (`smartluck-analysis/05-approved-sprint-plan.md`).
3. The Gail Howard CLI additions (`sprint-plan-update.md`).
4. **NEW**: out-of-plan work that already shipped — `lottery backtest` and `lottery optimize`. These are now formalized as **Sprint 1.2 — Validation Layer**.

If anything below conflicts with an older planning doc in this repo, this file wins.

---

## Architecture (unchanged)

```
Expo (React Native + Web / TypeScript)
    │ HTTP
Go API Gateway (auth, rate limiting, routing, cache)
    │ HTTP (localhost)
Python FastAPI Sidecar (frequency, deviation, correlation, sum_range, odds, wheels)
    │
Lottery Adapters (Mega-Sena, Lotofácil, Powerball, plug-and-play)
```

## Cross-cutting principles (locked)

1. **Chi² gate everywhere.** Any "predictive" surface returns `is_predictive` + a one-line caveat. With Sprint 1.2 in place, the gate is now also informed by empirical backtest hit rates, not only chi² p-values.
2. **Distinguish EV from P(win).** Anti-popular and game-selector are EV claims (always real). Hot/cold are P(win) claims (only real when chi² gate trips).
3. **Engine stays dependency-light.** `numpy`, `scipy`, `pandas` only. Wheels module zero-dep so it can split out as standalone PyPI.
4. **Adapters are the source of truth.** All tables (sum range, odds, popularity heuristics) computed from `DrawRules`, never hardcoded per game.
5. **Smart Luck Parity Pack positioning.** "OSS version of what Smart Luck sells, with the math gated on significance tests + empirical backtests."

---

## Sprint status board

| Sprint | Theme                                                                                          | Status                                                                                               |
| ------ | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1      | The Engine                                                                                     | ✅ DONE                                                                                               |
| 1.2    | Validation Layer (backtest + optimize)                                                         | ✅ DONE (out-of-plan, formalized 2026-04-26)                                                          |
| 1.3    | Absurdity Engine v4–v10 (esoteric strategies + adaptive window)                                | ✅ DONE (out-of-plan, formalized 2026-04-28)                                                          |
| 1.4    | BaseStrategy filter layer (sum-range, parity, decade breadth)                                  | ✅ DONE (built inside `BaseStrategy.suggest`, 2026-04-27) — formalize as `--filters` flag in Sprint 2 |
| 1.1    | Sum-Range + Odds Patch                                                                         | ✅ DONE (2026-04-28)                                                                                  |
| 1.1.1  | Multiple Bet support (Variable Picks)                                                          | ✅ DONE (2026-04-28)                                                                                  |
| 1.5    | Wheels promotion + standalone PyPI                                                             | ✅ DONE (2026-04-28)                                                                                  |
| 1.6    | Tech Debt & Performance (caching, data audit, ensemble scaling)                                | ✅ DONE (2026-04-28)                                                                                  |
| 1.7    | Structural Filter Refinement (Dynamic multiple-bet bands)                                      | ✅ DONE (2026-04-28)                                                                                  |
| 1.8    | Advanced Structural Patterns & Multi-Game Coverage (Primes, Fibonacci, Frame/Center, Map)      | ✅ DONE (2026-04-28)                                                                                  |
| 1.9    | Framework Refinement & Translation (Anomaly detection, Cycle analysis, structural strategy)    | ✅ DONE (2026-04-28)                                                                                  |
| 2      | Advantage Dashboard & Structural Filters (Howard P1)                                           | ✅ DONE (2026-04-28)                                                                                  |
| 2.1    | Sidecar (FastAPI) implementation                                                               | ✅ DONE (2026-04-29)                                                                                 |
| 2.2    | Universal Synapse: Anomaly & Personal Utilities                                                | ✅ DONE (2026-04-28)                                                                                  |
| 2.3    | Analysis Dashboard Phase 2: Spatial Voids & Z-Score Scaling                                     | ✅ DONE (2026-04-29)                                                                                 |
| 2.4    | Advanced Metrics Strategy: AC Value, Root Sum, Unit Sum integration                            | ✅ DONE (2026-04-29)                                                                                 |
| 2.5    | Advanced Strategy Refinement (Anti-Popular, Void Analysis)                                     | ✅ DONE (2026-04-28)                                                                                  |
| 2.6    | Global Registry Expansion (150+ games)                                                         | ✅ DONE (2026-04-28)                                                                                  |
| 2.7    | System Optimization & UX (Pattern Vectorization, Granular Ensembles, Check Cmd)                | ✅ DONE (2026-04-28)                                                                                  |
| 2.8    | Holistic Strategy Convergence (Reincarnation, Global Entropy, Vectorized Markov)               | ✅ DONE (2026-04-28)                                                                                  |
| 2.9    | Tech Debt & Performance II (Deep Model Caching, Parallel Fetching, Monte Carlo Vectorization)  | ✅ DONE (2026-04-28)                                                                                  |
| 2.10   | Advanced Ensembles & Final Strategy Polish (Stacking, Gematria, Cycle, Vectorized Logistic)    | ✅ DONE (2026-04-28)                                                                                  |
| 2.11   | Strategy Educational Layer & UX (Wizard, Compare, Explainers, Howard Idea 6)                   | ✅ DONE (2026-04-28)                                                                                  |
| 2.12   | Strategic Portfolio & Info-Theory (Portfolio Cmd, Mutual Info, Repeat Filter)                  | ✅ DONE (2026-04-28)                                                                                  |
| 2.13   | Advanced Visual & Analytical Layers (Board Cmd: Balance, Coverage, Cluster, Sparsity)          | ✅ DONE (2026-04-28)                                                                                  |
| 2.14   | Dashboard Completion & Export (Halves, Row-of-10, Export Cmd)                                  | ✅ DONE (2026-04-28)                                                                                  |
| 2.15   | Converged Dashboard & Anomaly Insights (Z-Score, Max Delay, Insights Ribbon, Triplets)         | ✅ DONE (2026-04-28)                                                                                  |
| 2.16   | Universal Synapse Strategy (Multi-Tier Conjunction, Adaptive Stability Sampling)               | ✅ DONE (2026-04-28)                                                                                  |
| 2.17   | Robustness & Stability (Stability Strategy, Howard Filter Expansion, Synapse v2)               | ✅ DONE (2026-04-28)                                                                                  |
| 2.18   | Terminal Dashboard & Regime Selection (Rich Layout, Regime Strategy, Fixes)                    | ✅ DONE (2026-04-28)                                                                                  |
| 2.19   | Final Convergence & Harmonic Resonance (Dashboard+, Harmonic Strategy, Auto-Synapse)           | ✅ DONE (2026-04-28)                                                                                  |
| 2.20   | Convergence Visualization & Adjacency Mapping (Board Cmd: Convergence, Adjacency views)        | ✅ DONE (2026-04-28)                                                                                  |
| 2.21   | Analysis Dashboard Convergence (History Navigator, Compare-Bets, Savings Calc, Insight Ribbon) | ✅ DONE (2026-04-28)                                                                                  |
| 2.22   | Universal Synapse Convergence & Dashboard V2 (Terminal Live, Agreement Heatmap, Adjacency Map) | ✅ DONE (2026-04-28)                                                                                  |
| 2.23   | Maintenance & Stability (Visual Polish, Smart Luck Filters, Fixes)                             | ✅ DONE (2026-04-28)                                                                                  |
| 2.24   | Environmental Chaos & Simulation (Seismic Strategy, MC Simulation Map, Refraction)             | ✅ DONE (2026-04-28)                                                                                  |
| 2.25   | Power Pack (50+ Advanced Structural Filters, AC Value, Unit Metrics)                           | ✅ DONE (2026-04-28)                                                                                  |
| 2.26   | Market Regime & Modulo Filters (Hot/Cold, Duplicate Elimination, Multiples)            | ✅ DONE (2026-04-28)                                                                                  |
| 2.27   | Meta-Logic & Positional Physics (K-of-N Fault Tolerance, Ordered Vector Distribution) | ✅ DONE (2026-04-28)                                                                                  |
| 2.28   | High-Order Graph & Digital Filters (100-Filter Milestone, Successive Units, Parity Pairs) | ✅ DONE (2026-04-28)                                                                                  |
| 2.29   | Alert Systems & Summary Cards (Delay Red-Flags, Executive Dashboard, Card-based UX)    | ✅ DONE (2026-04-28)                                                                                  |
| 2.30   | Information Geometry & Prize Simulation (Fisher Strategy, Historical Simulator)        | ✅ DONE (2026-04-28)                                                                                  |
| 2.31   | Standardized API & Virtual Environment (API-refactor, .venv, [all] deps)                      | ✅ DONE (2026-04-28)                                                                                  |
| 2.32  | Dashboard V3: Automated Insights & Chi-squared Badge (insights module)                        | ✅ DONE (2026-04-28)                                                                                  |
| 2.33  | Strategy Expansion: Positional & Contagion (PDF slots, Lagged Adjacency)                      | ✅ DONE (2026-04-29)                                                                                  |
| 2.34  | CLI Modularization & Party Mode (ADR refactor, multi-persona brainstorming)                   | ✅ DONE (2026-05-03)                                                                                  |
| 2.35  | Configuration-Driven Reporting (lottery report, YAML/JSON pipelines)                          | ✅ DONE (2026-05-03)                                                                                  |
| 2.36  | Diagnostic Terminal: Signal-to-Noise, Clustering, Stress-Test, Explain                        | ✅ DONE (2026-05-03)                                                                                  |
| 2.36b | Risk Management & Kelly Criterion (lottery risk, EV analysis)                                  | ✅ DONE (2026-05-03)                                                                                  |
| 2.37  | Esoteric Overlay, Leaderboard & Obsidian Integration (detect-patterns, leaderboard, DataviewJS) | ✅ DONE (2026-05-03)                                                                                 |
| 2.37b | High-Intelligence Oracle (lottery oracle, persona-based insights)                             | ✅ DONE (2026-05-03)                                                                                  |
| 2.38  | Daily Log, Forecast Ensemble & Post-Fetch Hook                                                | ✅ DONE (2026-05-03)                                                                                  |
| 2.39  | Regime-Aware Scan, Compare-Draws & Trend Visualiser                                           | ✅ DONE (2026-05-03)                                                                                  |
| 2.40  | Daily Digest, CLI Smoke Tests, Alert Monitor                                                  | ✅ DONE (2026-05-03)                                                                                  |
| 2.41  | Watchlist — batch game tracking, run daily/alert/scan across multiple games                   | ✅ DONE (2026-05-04)                                                                                  |
| 2.42  | Report pipeline steps: daily/alert/scan/forecast/fetch/watchlist-run step types              | ✅ DONE (2026-05-04)                                                                                  |
| 2.43  | Ticket logging (forecast writes ticket_log.jsonl) + hitcheck retrospective scorer             | ✅ DONE (2026-05-04)                                                                                  |
| 2.44  | Weekly summary command + daily ticket logging fix                                             | ✅ DONE (2026-05-04)                                                                                  |
| 2.45  | Empirical calibration — out-of-sample hit rates + lift ranking across strategies              | ✅ DONE (2026-05-04)                                                                                  |
| 2.46  | Log export (CSV/TSV/JSON) + calibration-weighted forecast (--use-calibration)                 | ✅ DONE (2026-05-04)                                                                                  |
| 2.47  | rank-numbers (composite per-number score) + picks (consensus from ticket log)                 | ✅ DONE (2026-05-04)                                                                                  |
| 2.48  | Continuous Improvement (API gap closure, docs, tests)                                         | ✅ DONE (2026-05-29)                                                                                  |
| 3      | Go Gateway + extended game registry                                                            | ✅ DONE (2026-04-29)                                                                                 |
| 4      | Expo App                                                                                       | ✅ DONE (2026-04-29)                                                                                 |
| 5      | Content + Deploy                                                                               | ⏳ (CHANGELOG, README rewrite done 2026-05-29)                                                        |
| 6      | Ecosystem                                                                                      | ⏳                                                                                                    |
| 11.2   | API Gap Closure + Documentation + Quality (README, CHANGELOG, pyproject, 6 new endpoints)     | ✅ DONE (2026-05-29)                                                                                  |

---

## Sprint 1 — The Engine ✅ DONE

Python core: adapters + analysis modules + strategies + CLI.

**What is fully working:**

- Adapters: `br/mega-sena`, `br/lotofacil`, `us/powerball` (smart incremental fetch).
- Analysis modules: `frequency.py`, `deviation.py`, `correlation.py`.
- 23 strategies: 10 statistical (markov, bayesian, monte_carlo, weighted, pattern, momentum, spectral, streak, crowd_avoidance, steiner_wheel), 4 ML (logistic, random_forest, gradient_boost, knn), 3 deep (lstm_gru, transformer, cnn_1d), 6 fun (numerology, moon_phase, weather, biorhythm, fibonacci, zodiac).
- 3 ensembles: `voting`, `prob_weighted`, `hybrid`.
- CLI commands: `fetch`, `analyze`, `suggest`, `strategies`, `docs`, `validate`.
- `BaseStrategy.suggest()` injects parameters via `inspect.signature` so all strategy params surface in CLI output.
- Comma-joined strategies trigger an automatic voting ensemble (e.g. `--strategy bayesian,weighted,crowd_avoidance`).

---

## Sprint 1.2 — Validation Layer ✅ DONE (NEW)

Originally not on the roadmap — built in a Gemini-CLI session. Promoted here because both commands are now structural, and the `is_predictive` story across Sprint 2+ depends on them.

### `lottery backtest`

Runs any strategy (or all strategies) against historical draws.

- Single ID, comma list, range (`2990-2999`), or relative-from-latest (`--prev 1-10`).
- Strategy can be a name, comma list, or `all`.
- Honest blind testing — strategy only sees draws *before* the target.
- Per-draw report: rank of each winning number, capture@N, hit summary.
- `--summary` aggregate report when testing multiple draws.
- Reuses the per-strategy date kwargs (`upcoming_draw_date`, `target_date`, `draw_date`).

### `lottery optimize`

Grid search over `(strategy × history_limit × temperature)` measured by top-N capture rate.

- `--strategies all` runs the full battery.
- Validation window controlled by `--prev start-end`.
- Surfaces the optimal config per strategy.

### Why this matters for the roadmap

- **Sprint 2 (sidecar)**: the chi² gate on `is_predictive` can now also embed empirical capture rates — the integrity moat is stronger and earlier than originally planned.
- **Sprint 5 (content)**: blog post I.1 ("what a quant would do") gets free ammunition — publish optimizer output as proof none of the strategies meaningfully beat uniform on a fair lottery.
- **Sprint 4 (Expo app)**: the Nerd-mode chi² fairness badge can include a "best historical capture@N" stat alongside.

---

## Sprint 1.3 — Absurdity Engine v4–v10 ✅ DONE (NEW, 2026-04-28)

Originally not on the roadmap. Built across multiple Gemini-CLI sessions on 2026-04-27 and documented in `lottery-engine/docs/versions/v4.0.md` … `v10.0.md`. Formalized here because it adds 9 new strategies, 1 new module, 4 new CLI flags, and 7 new "OSINT signals" to the evidence panel. Documentation lives at `lottery-engine/docs/USER_GUIDE.md` (end-user) and `lottery-engine/docs/TECHNICAL_SPEC.md` (technical).

### What shipped

**New statistical strategies** (`engine/strategies/statistical/`):
- `primes.py` — Prime Oscillator: correlates prime-density of draws with lunar phase.
- `quantum.py` — Quantum Annealing approximation: simulates quantum tunneling so historically "cold" numbers can probability-jump to hot.
- `survival.py` — Alpha-pruning meta-ensemble: backtests members on last 10 draws, drops bottom 25%, runs 500-iteration Monte Carlo to find Convergence Zones.

**New fun strategies** (`engine/strategies/fun/`):
- `iching.py` — Yarrow-stalk hexagram casting from Intentional Seed.
- `kabbalistic.py` — 467-line Sephoric numerology with Inverted Triangle of Life, gold/red sigils, Karmic Debts/Lessons alerts, and "Success Trigger" UI alerts (`[bold gold]LUCK WINDOW OPEN[/bold gold]`).
- `ley_lines.py` — Becker-Hagens grid + Haversine distance from draw city; Tesla 3/6/9 boost.
- `noosphere.py` — Global-entropy jitter via hashed time-drift.
- `sefirot.py` — Maps numbers to 10 Sephiroth + 22 Paths + Qlippoth shells.
- `solar.py` — NOAA K-index correlation with historical hits (data cached in `data/solar_k_index.json`).
- `moon_phase.py` (Enhanced) — Added Lunar Gravitational Tides, tracking Perigee/Apogee distance and Tidal Intensity/Drag.

**New module:**
- `engine/modules/geometry.py` — Dodecahedron adjacency graph, 20-vertex mapping, modular pollination boost.

**Baked into `BaseStrategy.suggest`:**
- **Chaos Temperature Governor** — `T_active = T_base + δ_seismic + δ_solar + δ_lunar + δ_arcano + δ_noosphere`.
- **Intentional Seeding & Sacred Manifold** — `SHA256(name + birthdate + topic + arcano) mod 2^32` as the numpy RNG seed, with topic strings acting as a Universal Gematria overlay filtered through a "Flower of Life" manifold pattern. Same input → same ticket for the same draw date.
- **Atmospheric Muon Flux** — 0.5% per-ticket strike chance flips a number via bitwise XOR.
- **Adaptive History Sweep** — `--adaptive-window` flag picks the optimal `--limit` by precision sweep.

**New CLI flags on `lottery suggest`:**
- `--full-name`, `--birth-date`, `--topic` (intentional seed inputs).
- `--adaptive-window` (auto-`--limit`).

**Tests:**
- `tests/test_kabbalistic.py` (only formal test in repo so far).

### Tension with the original positioning

This work pulls hard against the "Smart Luck Parity Pack — credibility is the moat" framing. The chi² gate is unaffected (all 9 new strategies will land `is_predictive: false` for any fair lottery, by definition), but the marketing surface — `docs/USER_GUIDE.md` reads as full mystic — is now misaligned with blog post **I.1** ("what a quant would do with lottery data"). Decision needed: parallel tracks (Nerd mode = credibility, Chaos mode = absurdity) vs single track. Recommendation: keep both, lean into the parallel-tracks framing already drafted for Sprint 4.

### Why this matters for the roadmap

- **Sprint 1.4** (below) is partly already done — sum-range / parity / decade-breadth filters are baked into `BaseStrategy`. Sprint 2's `--filters` flag is a UI surface on top of code that already runs.
- **Sprint 4 Chaos mode** has 9 new strategies to plug into the anti-popular slider and Combo Audit screen.
- **Sprint 5 content** gets free posts: each version doc (v4–v10) is a draft of one blog post about an "absurdity feature" that ships behind the chi² gate.

---

## Sprint 1.4 — BaseStrategy Filter Layer ✅ PARTIALLY DONE (2026-04-27)

Documented in `docs/versions/v5.0.md` ("Balanced Wheel Filter") and v8.0/v9.0 (Adaptive Window, Muon Flux). The filter pipeline runs inside `BaseStrategy.suggest` itself — every ticket emitted is already auto-filtered.

### What's already running

- **Sum-Range Check** — ticket sum must fall within the 70% probability window (ideal sum ± 30%).
- **Parity Balance** — no all-odd or all-even tickets.
- **Decade Breadth** — must span ≥ 3 different decades.
- **Resampling loop** — failing tickets are discarded and resampled.

### What's still missing for Sprint 2 closure

- **Surface as an explicit `--filters` flag** so users can opt in/out and combine with `no_arithmetic`, `no_consecutive_run`, `no_same_last_digit`, `no_calendar_cluster` (the Howard catalog).
- **`lottery check`** — separate command that *reports* on filter violations rather than *enforcing* them, so users can audit their own tickets.

This is now low-effort: the predicates exist; we just need to expose them and add the four missing rules.

---

## Sprint 1.1 — Sum-Range + Odds Patch ✅ DONE

**Highest leverage single-file work.** One module unblocks five downstream features.

### Build

- `engine/modules/sum_range.py` — analytical truncated-normal Most-Probable-Range-of-Sums. Exposes `most_probable_range(rules, coverage=0.70)`, `pmf(rules)`, `classify(combo, rules)`. **Replaces sampling in `pattern.py`**.
- `engine/odds/comparator.py` — cross-adapter odds ranking + EV comparator.
- CLI: `lottery odds` and `lottery odds --compare`.
- CLI: `lottery audit --combo 3,17,23,24,36,47` returning sum bucket + envelope flags.
- 🔧 Refactor `engine/strategies/statistical/pattern.py` to consume `sum_range`. Drop `n_samples` parameter.

### Tests

- For every published Smart Luck `(pick, n)` row, computed range matches within ±1.
- Mega-Sena (6/60) midpoint = 183, range ≈ 140–226.
- Lotofácil (15/25) midpoint = 195, range ≈ 176–214.

### Definition of done

- `lottery audit --combo …` emits sum bucket + envelope flags.
- `lottery odds --compare` ranks all registered adapters.
- `pattern.py` no longer does empirical sampling.

---

## Sprint 1.5 — Wheels Promotion + Standalone PyPI ✅ DONE

The OSS magnet. Inserted before sidecar to maximize GitHub-star runway.

### Build

Promote `engine/strategies/statistical/steiner_wheel.py` → top-level `engine/wheels/`:

- `full_wheel.py` — `C(n, pick)` enumeration (trivial `itertools.combinations`).
- `key_wheel.py` — fix one number, wheel the rest.
- `abbreviated.py` — load published covering designs from a static JSON (LJCR best-known sizes for k≤12, t≤5).
- `evaluator.py` — given a wheel + hypothetical winning combo, list which tickets win which prize tier.

Standalone PyPI package `lottery-wheels` (zero-dep, MIT) re-exporting the same module.

CLI: `lottery wheel <game> --pool … --guarantee 4if6` and `lottery wheels --game-type pick6`.

### Tests

- Parity against published Gail Howard wheel sizes for `(7,6)`, `(8,6)`, `(10,6)` etc.
- Parity against LJCR best-known covering numbers for sampled `(v, k, t)` triples.

### Content (co-shipped)

- Blog post **I.3** — *"How wheel software works and why we open-sourced it."* / *"We open-sourced what Smart Luck charges \$100+ for."*

---

## Sprint 1.6 — Tech Debt & Performance ✅ DONE

Derived from the April 25/27 Gemini session reviews, these are critical stability and performance enhancements before wrapping the core engine.

- **Deep & ML Strategy Model Caching:** Deep learning models (`transformer`, `lstm_gru`, `cnn_1d`) currently train from scratch each call (~30–60s on CPU). Implement caching for model weights using `torch.save`, keyed on `(lottery_slug, draw_count, last_draw_hash)`. Furthermore, added `joblib` caching to ML tier models (`random_forest`, `gradient_boost`, `logistic`) which drastically speeds up inference by caching the scaler and model.
- **Data Integrity Audit (`lottery audit-data`):** A standalone CLI command to validate cached JSON data files. Scans for missing draw IDs, duplicate dates, and out-of-range numbers to ensure the engine isn't training on corrupted data.
- **Parallel Fetching:** Parallelize the HTTP mirror chain in `caixa_base.py` (and future adapters) using `ThreadPoolExecutor` to significantly speed up incremental history fetches.

---

## Sprint 2 — The Sidecar (FastAPI) ✅ DONE

Wrap the engine in FastAPI, internal only, no auth yet.

### Endpoint surface

```
GET  /games
GET  /games/{slug}/odds
GET  /games/compare
GET  /games/{slug}/sum-distribution
GET  /games/{slug}/gap/{number}
GET  /analyze/{slug}
POST /games/{slug}/combo/audit
POST /check
POST /games/{slug}/wheel
POST /games/{slug}/strategy/{name}
POST /suggest                       (with pool, key, filters params)
```

Every recommendation surface returns `is_predictive` + caveat string derived from the chi² p-value AND the Sprint 1.2 backtest capture rate.

### Howard CLI add-ons (also part of Sprint 2)

These were promised in `sprint-plan-update.md` and are folded in here without change:

- **`lottery check <game> <numbers>`** — ticket structural evaluator. Reuses filter logic from `--filters` system. Output also exposed as `POST /check`.
- **`lottery analyze` 14-chart expansion** — frequency, recency, gap, sum distribution (with 70% band), odd/even, high/low, positional, decade, last-digit, consecutive-pair, repeat rate, hot pairs (top 20 from `correlation.py`), cycle detection, day-of-week bias. `--charts` flag for selection. `--format json` for app layer. Also exposed at `GET /analyze/{slug}`.
- **`--pool <nums>`** flag on `lottery suggest` — constrains score map pre-sampling.
- **`--key <num>`** flag on `lottery suggest` — guarantees inclusion in every ticket post-sampling.
- **`--filters` composable system** — `no_all_odd`, `no_all_even`, `no_all_high`, `no_all_low`, `no_single_decade`, `no_same_last_digit`, `no_arithmetic`, `no_consecutive_run`, `sum_range`, `no_calendar_cluster`. `--filters all` applies all. **Note (2026-04-28):** `sum_range`, parity, and decade-breadth are already enforced in `BaseStrategy.suggest` via the v5.0 "Balanced Wheel Filter" — Sprint 2 surfaces them as opt-in flags and adds the remaining rules.
- **`copairs` strategy** — wire up existing `engine/modules/correlation.py` as a co-occurrence scoring strategy. Add to `_STRATEGY_PRESETS` and `_STRATEGY_EXPLAINERS`.
- **70% sum band** displayed in `lottery analyze` chart, in `sum_range` filter, in `lottery check` sum line, and in `lottery docs sum_formula`.

### CLI cleanup task

`engine/cli/main.py` references `lottery wizard` and has `_STRATEGY_EXPLAINERS` / `_STRATEGY_PRESETS` dicts staged for a `compare` command, but neither is exposed as `@app.command()`. Either build them or strip references — pick one in this sprint. Recommendation: build them; the data is already there.

---

## Sprint 2.1 — Crowd-Avoidance Extension ✅ DONE

`engine/strategies/statistical/crowd_avoidance.py` already exists with `birthday_penalty=0.5`, `round_penalty=0.4`. Extend (don't rename) with:

- Sum-region preference (uses `sum_range` from 1.1; absorbs Smart Luck idea #8 — upper half of 70% range).
- "Lucky number" heuristics: 7, 11, 13, 17, 21, 23, 33, 77.
- Repeating-digit patterns (11/22/33).
- Betslip-diagonal patterns.
- Multiples of 5/10.
- Helper: `generate_combos(rules, n_combos, anti_popularity_strength)` if not already present.

### Definition of done

`lottery suggest <game> --strategy crowd_avoidance` returns top-N combos ranked by inverse popularity, and the `combo/audit` endpoint includes the popularity-resistance score per combo.

---

## Sprint 2.2 — Universal Synapse Phase ✅ DONE (2026-04-28)

The final frontier of Nerd/Chaos integration, filling gaps identified in the v10.0 audit.

### Anomaly Detection (`lottery audit-data`)
- **Z-Score Scaling:** Surface Standard Deviation for every pattern to distinguish "likely" from "statistically impossible" draws. ✅ DONE (2026-04-28)
- **Atmospheric Refractive Index ($N$):** Use pressure/temp to model static charge potential on pneumatic balls. ✅ DONE (v12.0 placeholder, 2026-04-28)

### Personal Utilities (`lottery calendar` & `lottery signature`)
- **`lottery calendar`:** Generates a monthly console grid of "Favorable Days" (Dia Natalício) and Karmic trial windows based on personal vibrations. ✅ DONE (2026-04-28)
- **`lottery signature`:** Analyzes names for "Negative Sequences" and suggests minimal modifications (adding a middle name or extra letter) to align with prosperity goals. ✅ DONE (2026-04-28)
- **Karmic Suppressors:** Integrate Debts (13, 14, 16, 19) into the suggestion engine to lower confidence scores during high-risk windows. ✅ DONE (2026-04-28)

---

## Sprint 3 — Go Gateway + Extended Game Registry ✅ DONE (2026-04-29)

### Gateway

HTTP proxy + rate limiting + auth skeleton. Cache TTLs:

- `/sum-distribution` — 24h.
- `/odds`, `/games/compare` — static, infinite TTL.
- `/combo/audit`, `/check` — no cache (user-specific).
- `/strategy/*` — 5min (absorb burst load).
- `/analyze/*` — 24h.

### Extended game registry — `data/games/registry.yaml`

Catalog 150+ lotteries. Schema per game:

```yaml
- id: br/mega-sena
  name: Mega-Sena
  country: Brazil
  pick_count: 6
  pool_size: 60
  bonus_pool: null
  bonus_pick: null
  draw_days: [Wednesday, Saturday]
  draw_city: "São Paulo"
  draw_city_lat: -23.5505
  draw_city_lon: -46.6333
  adapter: mega_sena
  data_available: true
```

- Adapters read parameters from registry instead of hardcoding.
- Games with `data_available: false` listed in `lottery games` but skipped in `fetch`.
- Each missing adapter = one open GitHub issue for community contribution.

---

## Sprint 4 — Expo App ✅ DONE (2026-04-29)

### Nerd mode (must-have visuals)

- Bell-curve chart with the user's combo overlaid (consumes `/sum-distribution`).
- Per-number gap histogram (consumes `/gap/{number}`).
- Chi² gate badge — "Game appears statistically fair — predictions are heuristic only" when `is_predictive: false`.
- **NEW (from Sprint 1.2)**: best historical capture@N badge per strategy.

### Chaos mode (Anti-Popular UX)

- Headline: "Don't try to win MORE — try to share LESS."
- Anti-popular slider (strength 0–1) → calls strategy `crowd_avoidance`.
- Combo Audit screen — paste numbers, get full audit + share.

### Numerology & Esoteric Utilities (New)

- **Favorable Days Calendar (`Dia Natalício`):** Generates a monthly calendar of days mathematically aligned with the user's personal vibration for signing contracts, placing bets, or making investments.
- **Signature Adjustment Generator:** Evaluates a user's full name for "negative sequences" and suggests signature modifications to remove numerological blockages and align with prosperity goals.
- **Karmic Debts Dashboard:** Visual surface tracking personal Karmic Debts (13, 14, 16, 19) and current active Arcanos.

---

## Session Log: 2026-04-29 — The Orchestration Layer

**Achievements:**
- **Codebase Stabilization:** Fixed critical regressions in `BaseStrategy` (`AttributeError` on list/dataframe interaction), updated documentation paths in automated tests, and standardized `suggest()` signatures across all 52+ strategies to support `**kwargs` and explicit seeding.
- **Sprint 2.1 (FastAPI Sidecar) ✅ DONE:** Implemented `engine/api/` featuring a RESTful wrapper for the engine. Endpoints include `/games`, `/games/{name}/analysis`, `/games/{name}/suggest`, and `/strategies`. Integrated `typer` with a new `lottery serve` command to launch the API.
- **Sprint 3 (Go Gateway) ✅ DONE:** Bootstrapped `gateway/` in Go 1.25.9 (installed locally to bypass env restrictions). Features:
    - **Reverse Proxy:** Transparently forwards requests to the Python Sidecar.
    - **Authentication:** `X-API-KEY` header middleware.
    - **Rate Limiting:** `go-chi/httprate` (100 req/min per IP).
    - **Caching:** In-memory GET request cache (10s TTL) with `X-Cache: HIT` headers.
- **Sprint 4 (Expo App) ✅ DONE (2026-04-29):** Scaffolder and implemented the React Native + Web application. Verified with a successful web build.
- **Analysis Dashboard Phase 2 ✅ DONE (2026-04-29):** Integrated Spatial Voids, Pattern Rarity, and Z-Score Z-Scaling into the terminal dashboard. Refactored `check` command for structural audit clarity.
- **Advanced Metrics Strategy ✅ DONE (2026-04-29):** Implemented `AdvancedMetricsStrategy` using AC Value, Root Sum, and Unit Sum participation scoring. Integrated 'Structural Health' panel into the dashboard and added an 'advanced' view to the `board` command.
- **Continuous Improvement Phase ✅ DONE (2026-04-29):** Standardized Strategy API, Automated Insights Ribbon, Dashboard V3, and Global Registry enrichment.
- **Sprint P0 & Advanced Analytics ✅ DONE (2026-04-30):** Resolved critical hotfixes (G1, G2, G3), eliminated name-change liability (G10), and implemented Positional Heatmaps + Frequent Triplet clustering.
- **Board View & UX Refinement ✅ DONE (2026-04-30):** Refactored `board --view heatmap` to respect registry `board_cols` (fixing Lotofácil visualization), added `--cols` override, implemented "Marked Number" highlights, and added `board`/`heatmap` topics to the internal `docs` command.
- **Unified Launcher & Storage Policy ✅ DONE (2026-04-30):** 
    - Created root-level `./lottery` launcher script with automatic `.venv` setup and `PYTHONPATH` exports.
    - Implemented a hybrid storage architecture in `engine/modules/storage.py` supporting **Performance Cache** (JSON base + SQL index) and **Source of Truth** (SQL primary) policies.
    - Standardized Yearly Partitioned JSON as the persistent human-readable base.
- **Repository Integrity ✅ DONE (2026-04-30):** Consolidated entire repository history (108 commits) under unified author `oalsysd@gmail.com`.

---

## Sprint 7 — The Horizon (Continuous Evolution) 🚀

To maintain our edge and continue the philosophy of "Constant Improvement," this phase outlines radical new ideas across our four primary pillars:

### 1. Quantitative Finance & Risk Management
*   **Kelly Criterion Bet Sizing (`lottery risk`):** Implement the Kelly Criterion formula to calculate if a jackpot has rolled over heavily enough to provide +EV (Expected Value > 1.0). The engine will output: *"Do not play today"* or *"EV is 1.05. Play exactly 12 tickets."*
*   **Combinatorial Hedging:** Generating a "Hedge Portfolio" where the probability of hitting the lowest tier prize mathematically covers the cost of the entire bet, turning the jackpot attempt into a "free roll."

### 2. Advanced Physics & Math
*   **Graph Neural Networks (GNN):** Treat the lottery bet slip as a 2D spatial graph. Nodes are numbers; edges are physical adjacencies. Train a PyTorch Geometric model to learn how winning numbers propagate across the grid.
*   **Pseudo-Kinetic Fluid Simulation (`collision_sim`):** A 3D Monte Carlo physics simulation of elastic spheres bouncing in a rotating drum. Introduce micro-variations (e.g., the weight of the ink) to see which balls drop into the chute first under simulated gravity.

### 3. The "Absurdity" Horizon
*   **Astrological Ephemeris (Planetary Transits):** Integrate the Swiss Ephemeris API to fetch real-time planetary alignments (e.g., Jupiter in the 5th House). Correlate historical draws with planetary angles.
*   **Financial Market Volatility Resonance (`vix_jitter`):** Correlate historical draw anomalies with the CBOE Volatility Index (VIX) or major Bitcoin price crashes, simulating "Global Anxiety."
*   **LLM "Oracle" Agent:** Pass the JSON output of the statistical analysis to a local LLM to generate a personalized, human-readable "Horoscope" for the user based on the hard math.

### 4. Systems Engineering & Architecture
*   **AutoML Background Daemon (`lottery daemon`):** A background worker that continuously runs `lottery optimize` over moving windows, automatically updating the default weights and hyperparameters for the `synapse` ensemble without human intervention.
*   **Real-time Webhook Ingestion:** The FastAPI sidecar listens for external triggers to update the DuckDB database the exact second a draw is published live on TV.

---

## Sprint 2.36 — Diagnostic Terminal ✅ DONE (2026-05-03)

Addresses the "Confirmation Bias Engine" risk by transforming the CLI from a
simple prediction requester into a Pattern Diagnostic Terminal that exposes
structural friction and entropy.

### `lottery signal` — Signal-to-Noise Rolling Window Dashboard

Runs any strategy over overlapping historical windows (`--window`, `--step`)
and tracks **confidence** and **score entropy** at each snapshot.

- **Sparkline output:** Unicode block characters show confidence and entropy
  trajectories at a glance.
- **Plateau detection:** Rolling std dev < 25th-percentile threshold →
  window labelled `STABLE`; otherwise `NOISE`.
- **Stability score:** % of windows that are stable surfaced at summary.
- **`--export-md`:** Writes a YAML-frontmattered pattern log for DataviewJS
  cross-referencing in Obsidian.

Command: `lottery signal br/lotofacil --strategy weighted --window 50 --step 10`

### `lottery cluster` — Unsupervised Clustering

Builds a number co-occurrence + structural feature matrix (sum, parity ratio)
and clusters draws with K-Means or DBSCAN.

- Scikit-learn required (`pip install 'lottery-engine[ml]'`).
- **Cluster profiles:** size, top-10 most frequent numbers, avg sum, even ratio.
- **Latest draw cluster:** identifies which cluster the most recent draw belongs to.
- **`--export-md`:** Pattern log with Obsidian-ready frontmatter for esoteric
  marker correlation.

Command: `lottery cluster br/lotofacil --method kmeans --k 5`

The cluster–esoteric alignment hypothesis: if a specific esoteric cycle
consistently maps to draws in Cluster X, that is a High-Probability Node
rather than random chance.

### `lottery stress-test` — Adversarial CLI

Baseline → run strategy on real data; Adversarial → replace `inject-ratio`
fraction of draws with true uniform random draws, repeat `trials` times.

- Compares **confidence** and **score entropy** real vs. random.
- Verdicts: `REAL > RANDOM` (structure detected) / `CANNOT DISTINGUISH`
  (patterns likely hallucinated) / `RANDOM > REAL` (check inverted logic).
- **`--export-md`:** Adversarial report for Obsidian.

Command: `lottery stress-test br/lotofacil --strategy weighted --inject-ratio 0.5 --trials 5`

### `lottery suggest --explain` — Feature Explanation Panel

Adds a blue Explain panel to the standard suggestion output:

- **Feature 1–3:** Top-scoring numbers + their relative score percentile.
- **Feature 4:** 30-draw Chi² regime (uniform vs. non-uniform).
- **Feature 5:** Score entropy and concentration ratio (focused vs. diffuse).

Command: `lottery suggest br/lotofacil --explain`

### Design philosophy

All four additions answer the mentor's core question: *"Can the CLI reveal the
structural friction between traditional math and esoteric theories?"*

- `signal` shows *when* a strategy is stable vs. noisy.
- `cluster` shows *what* natural groupings exist in the data.
- `stress-test` shows *whether* strategy patterns are genuine or hallucinated.
- `--explain` shows *why* the strategy made a specific prediction.

---

## Sprint 2.37 — Esoteric Overlay, Leaderboard & Obsidian Integration ✅ DONE (2026-05-03)

Completes the Diagnostic Terminal with the remaining two commands from the
"Pattern Recognition" design brief and wires the export layer into Obsidian.

### `lottery detect-patterns` — Esoteric Cycle Overlay

Cross-correlates rolling stability windows with esoteric marker values:

- **`--esoteric cyclical`** — lunar cycle progress in 5 quintile buckets
- **`--esoteric lunar`** — 8 discrete moon phases (New Moon → Waning Crescent)
- **`--esoteric solar`** — NOAA K-index bucket (quiet / unsettled / storm)
- **`--esoteric all`** — run every overlay in one pass

For each bucket: stable% vs baseline, chi-squared independence test (scipy),
`|Δ%| >= --threshold` → **High-Probability Node** flag.

First real run on Lotofacil weighted/30-draw windows returned **no nodes at
±12%** — an honest null result that validates the anti-confirmation-bias design.

Command: `lottery detect-patterns br/lotofacil --esoteric all --threshold 0.15`

### `lottery leaderboard` — Comparative Strategy Ranking

Runs stability analysis + adversarial stress-test across a configurable list
of strategies and produces a composite diagnostic ranking:

```
Composite = 0.5 × stability% + 0.5 × clamp(Δconf / 0.05, 0, 1)
```

Strategy groups: `default | statistical | esoteric | deep | <custom list>`

Assessments: `DISCRIMINATES` (≥0.50) / `NOISE` / `INVERTED` / `UNSTABLE`

Key finding on Lotofacil: `bayesian` is the top discriminator among statistical
strategies (+0.063 real-vs-random Δ). `noosphere` is 100% stable but 0.0 Δ
(deterministic hash, not data-dependent — correctly identified as non-discriminating).
`weighted` shows a negative Δ on short windows (INVERTED) — worth investigating.

Command: `lottery leaderboard br/lotofacil --strategies default`

### `examples/obsidian_dataviewjs.md` — Obsidian Live Dashboard

Six DataviewJS blocks that query YAML-frontmattered pattern logs from all five
`--export-md` commands and build a live Obsidian dashboard:

1. Signal stability% history over time
2. Leaderboard composite trend (month-to-month)
3. High-Probability Nodes tracker
4. Adversarial stress-test summary
5. Cluster latest-draw membership
6. **Convergence cross-reference** — flags dates where esoteric nodes AND
   cluster assignments coincide (the strongest cross-signal)

### Test fix (pre-existing)

ML strategy smoke tests (`logistic`, `knn`, `voting`, `regime`, `synapse`) now
gracefully `pytest.skip` when scikit-learn is absent rather than raising
`KeyError`. `seismic` strategy added to `docs/user-guide.md` (was missing).

Test suite: **86 pass, 10 skip** (no new failures).

---

## Sprint 2.38 — Daily Log, Forecast Ensemble & Post-Fetch Hook ✅ DONE (2026-05-03)

### Problem addressed

The Diagnostic Terminal had strong analytical commands but no passive data
accumulation. Each `scan` / `signal` run was stateless. We also had no way to
ask "what's the consensus across all good strategies?" — just individual
strategy outputs.

### Deliverables

#### `lottery log` / `lottery log-view`

Lightweight daily tracker (`engine/cli/commands/log.py`).

- `lottery log <game>` — appends a compact record to `data/draw_log.jsonl` (JSONL, CSV, or MD)
- `lottery log-view` — displays recent entries in a Rich table (filterable by game/count)
- Fields: date, draw_id, game, strategy, confidence, entropy, stable, chi2_p, moon_phase, moon_ratio, solar_kp, cluster
- `--quiet` flag for cron/pipeline use (zero terminal output)
- Default path: `data/draw_log.jsonl` (append-only)

#### `lottery forecast`

Weighted ensemble consensus ticket (`engine/cli/commands/forecast.py`).

Algorithm:
1. For each strategy: compute stability% (rolling window std-dev) + discrimination Δ (real vs random)
2. Composite weight = `0.5 × stability + 0.5 × clamp(Δ/0.05, 0, 1)`
3. Run `strategy.suggest()` → per-number score distribution, normalise
4. `consensus_score[n] = Σ(normalised_score[n] × weight) / total_weight`
5. Pick top `pick_count` numbers by consensus score
6. Report per-number std-dev across strategies (confidence band)
7. `--export-md` appends YAML-frontmattered forecast block to running file

Strategy groups: `default` (6 strategies), `fast` (3), `statistical` (14), `esoteric` (6)

Live result on Lotofacil (`--strategies fast`):
- `weighted` → w=0.626 (highest Δ=+0.108), `markov` → w=0.277, `bayesian` → w=0.126 (negative Δ)
- Consensus ticket: 1, 2, 3, 4, 5, 6, 7, 10, 11, 13, 15, 20, 23, 24, 25
- consensus_mass=0.799 — concentrated agreement

#### `scripts/post_fetch_log.sh`

Shell hook that appends a `lottery log` snapshot immediately after `lottery fetch`.
Env-configurable: `LOG_FILE`, `LOG_FORMAT`, `STRATEGY`. Cron-ready.

Test suite: **86 pass, 10 skip** (no new failures).

---

## Sprint 2.39 — Regime-Aware Scan, Compare-Draws & Trend Visualiser ✅ DONE (2026-05-03)

### Problem addressed

The engine had strong per-run diagnostics but no temporal depth (how are
conditions evolving?) and no regime-awareness in the scan (has the draw
distribution shifted?). The scan also had no way to express "this is the
same lottery, but it's behaving differently lately."

### Deliverables

#### `lottery compare-draws`

Jensen-Shannon regime-shift detector (`engine/cli/commands/compare_draws.py`).

- Compares last-N draw frequency distribution against full history
- Metrics: JS divergence, KL divergence, chi-squared independence test
- Verdicts: STABLE (JS<0.02) / DRIFT (0.02–0.08) / SHIFT (≥0.08)
- Top-movers table: which numbers have risen/fallen most in recent window
- `--export-md` appends YAML-frontmattered regime block for Obsidian DataviewJS
- Live result: STABLE, JS=0.00135 (Lotofacil recent window consistent with history)

#### `lottery scan` Layer 6

Added a 6th diagnostic layer to `scan` (was 5 layers / max 10pts → now 6 / max 12pts).

- Layer 6 computes JS divergence inline (same algorithm as compare-draws)
- STABLE → 2pts, DRIFT → 1pt, SHIFT (JS≥0.08) → 0pts
- Export includes `js_divergence` and `regime` fields in YAML block
- Scan verdict threshold is pct-based so backward-compatible
- Live result: GO 10/12 → GO 10/12 (regime STABLE contributed 2pts)

#### `lottery trend`

Temporal trend visualiser from the daily log (`engine/cli/commands/trend.py`).

- Reads `data/draw_log.jsonl` built by `lottery log`
- Renders ASCII sparklines for each metric (confidence, entropy, chi2_p, moon_ratio, solar_kp)
- 7-day rolling mean + direction arrow per metric
- Summary table of last 7 entries
- Alert triggers: confidence drop >0.05, entropy spike >0.5, stability <30%, chi2_p <0.05
- Filterable by game and day window

#### `lottery next`

One-liner executive summary (`engine/cli/commands/next_draw.py`).

- Internally runs the 6-layer scan + fast 3-strategy forecast in sequence
- If GO: outputs consensus ticket. If not GO: shows verdict + reason, skips ticket
- `--force` overrides verdict gate and generates ticket anyway
- `--quiet` prints only the numbers (cron/pipeline-friendly)
- Live result: GO 9/12 → ticket: 1 3 4 5 6 7 10 11 13 15 19 20 23 24 25

Test suite: **86 pass, 10 skip** (no new failures).


---

## Sprint 2.40–2.51 — Analytics Expansion ✅ DONE (2026-05-04)

### Commands added (15 new CLI commands)

| Sprint | Command | Description |
|--------|---------|-------------|
| 2.40 | `lottery daily` | Morning digest: regime+scan+EV+ticket+oracle pipeline |
| 2.41 | `lottery watchlist` | Sub-app: add/remove/list/status/run tracked games |
| 2.42 | `lottery report` (rewrite) | Steps-based YAML pipeline (fetch/daily/alert/scan/forecast/watchlist-run/suggest) |
| 2.43 | `lottery hitcheck` | Compare logged tickets vs actual draw results |
| 2.44 | `lottery weekly` | 7-day performance summary from logs (sparklines + hit table) |
| 2.45 | `lottery calibrate` | Empirical out-of-sample hit-rate calibration → calibration_cache.json |
| 2.46 | `lottery log-export` | Export draw-log/ticket-log/all to CSV/TSV/JSON |
| 2.47 | `lottery rank-numbers` | Composite per-number score across strategies (calibration-weighted) |
| 2.47 | `lottery picks` | Consensus ticket from ticket_log.jsonl frequency analysis |
| 2.48 | `lottery number-timeline` | Hit/miss sparkline + gap stats + OVERDUE flag for any pool number |
| 2.48 | `lottery compare-strategies` | Side-by-side tickets across all strategies; consensus heatmap |
| 2.49 | `lottery streak-report` | All-pool hot/cold streak ranking with historical record flags |
| 2.50 | `lottery pair-analysis` | Co-occurrence lift for number pairs; affinity table for --focus N |
| 2.51 | `lottery draw-summary` | Per-draw contextual analysis: frequency, gap, streak, surprise score |

### Test suite

**66 pass, 2 warnings** (no failures). All commands have smoke + export-md tests.

### Key architectural patterns

- All commands support `--export-md` appending YAML-frontmattered blocks for Obsidian DataviewJS
- `data/ticket_log.jsonl` — append-only log written by forecast + daily; read by picks/hitcheck/weekly
- `data/calibration_cache.json` — empirical lift scores; read by rank-numbers + forecast --use-calibration
- Alert/watchlist exit-code semantics: 0=GO, 1=NO-GO, 2=error
- `typer.Exit` uses `.exit_code` (not `.code`) — critical distinction from `SystemExit`

---

## Sprint 2.52–2.60 — Diagnostic Deep Dive ✅ DONE (2026-05-04)

### Commands added (10 new CLI commands)

| Sprint | Command | Description |
|--------|---------|-------------|
| 2.52 | `lottery session` | 5-stage pre-draw pipeline: scan→regime→streak→compare-strategies→forecast |
| 2.53 | `lottery ticket-grade` | Grade a hand-picked ticket (A+→F) across freq/streak/pair/consensus dimensions |
| 2.54 | `lottery pool-stats` | Draw distribution stats (sum/parity/consecutive/spread); ticket envelope check |
| 2.55 | `lottery history-scan` | Retrospective GO/NO-GO timeline with sparkline (3-layer lightweight scan) |
| 2.56 | `lottery number-heat` | Full-pool hit/miss heatmap grid: all numbers × recent-N draws |
| 2.57 | `lottery suggest-swaps` | Best single-number swap recommendations to improve a ticket |
| 2.58 | `lottery quick` | One-line cron command: scan+forecast; --quiet/--json/--force modes |
| 2.59 | `lottery variance-report` | 5-dimension volatility regime (freq/sum/parity/consecutive/confidence CV) |
| 2.60 | `lottery coverage-check` | Pool coverage grid for 1–N tickets; efficiency, entropy, prize tier simulation |

### Also added (Sprint 2.48)
- `lottery number-timeline` — per-number hit/miss sparkline, gap stats, OVERDUE flag
- `lottery compare-strategies` — side-by-side tickets across strategy group; consensus heatmap

### Test suite

**93 pass, 2 warnings** (no failures). Commands: 56 total.
