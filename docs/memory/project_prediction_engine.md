---
name: Prediction Engine — Project Context
description: Full architecture, stack, structure, sprint plan, and current implementation state for the Prediction Engine (lottery analysis OSS tool). Authoritative roadmap is SPRINT_PLAN.md at the workspace root.
types: project
originSessionId: b4855d89-87ea-40d0-9443-583c1b460277
last_audit: 2026-04-28
---
# Prediction Engine

A lottery prediction/analysis engine built as an OSS credibility anchor with a monetizable app layer. Now also branded internally as "Absurdity Engine v10 / Universal Synapse" after the Apr-27 Gemini sessions added 9 esoteric strategies — see open decision #1 in SPRINT_PLAN.md about the positioning conflict.

**Authoritative roadmap:** `SPRINT_PLAN.md` at the workspace root. The smartluck-analysis files (05, 06) and `sprint-plan-update.md` carry "SUPERSEDED" banners pointing to the master plan.

## Architecture

```
Expo (React Native + Web / TypeScript)
    │ HTTP
Go API Gateway (auth, rate limiting, routing, cache)
    │ HTTP (localhost)
Python FastAPI Sidecar (frequency, deviation, correlation, sum_range, odds, wheels)
    │
Lottery Adapters (Mega-Sena, Lotofácil, Powerball, plug-and-play)
```

## Project Structure (current, as of 2026-04-28)

```
lottery-engine/
├── docs/                              # NEW (Apr 27)
│   ├── USER_GUIDE.md                  # end-user "Absurdity Engine" guide
│   ├── TECHNICAL_SPEC.md              # 12 sections of formulas
│   └── versions/
│       └── v4.0.md … v10.0.md         # 7 feature-batch docs
├── tests/                             # NEW (Apr 27)
│   └── test_kabbalistic.py            # only test in repo
├── engine/
│   ├── modules/
│   │   ├── frequency.py
│   │   ├── deviation.py
│   │   ├── correlation.py             # exists but not wired as a strategy yet (copairs pending)
│   │   └── geometry.py                # NEW Apr 27 — dodecahedron adjacency
│   ├── adapters/
│   │   ├── br/
│   │   │   ├── caixa_base.py          # smart fetch — only pulls missing draws
│   │   │   ├── mega_sena.py
│   │   │   └── lotofacil.py
│   │   └── us/
│   │       └── powerball.py
│   ├── cli/
│   │   └── main.py                    # 1461 lines (was 1413 on Apr 25)
│   └── strategies/
│       ├── __init__.py                # BaseStrategy now contains: chaos governor, intentional seed, muon flux, sum/parity/decade filter pipeline (v5–v9 builds)
│       ├── statistical/
│       │   ├── markov.py
│       │   ├── bayesian.py
│       │   ├── monte_carlo.py
│       │   ├── weighted.py
│       │   ├── pattern.py             # still empirical sampling — refactor pending in Sprint 1.1
│       │   ├── momentum.py
│       │   ├── spectral.py
│       │   ├── streak.py
│       │   ├── crowd_avoidance.py
│       │   ├── steiner_wheel.py       # to be promoted to engine/wheels/ in Sprint 1.5
│       │   ├── primes.py              # NEW Apr 27 — prime density × lunar phase
│       │   ├── quantum.py             # NEW Apr 27 — annealing/tunneling sim
│       │   └── survival.py            # NEW Apr 27 — alpha-pruning meta-ensemble
│       ├── ml/    {logistic, random_forest, gradient_boost, knn, ensemble}
│       ├── deep/  {lstm_gru, transformer, cnn_1d}
│       └── fun/
│           ├── numerology.py, moon_phase.py, weather.py, biorhythm.py, fibonacci.py, zodiac.py
│           ├── iching.py              # NEW Apr 27 — yarrow stalk hexagram
│           ├── kabbalistic.py         # NEW Apr 27 — 467 lines, sephoric numerology
│           ├── ley_lines.py           # NEW Apr 27 — Becker-Hagens grid
│           ├── noosphere.py           # NEW Apr 27 — global entropy jitter
│           ├── sefirot.py             # NEW Apr 27 — sephoroth + paths + qlippoth
│           └── solar.py               # NEW Apr 27 — NOAA K-index correlation
├── data/
│   ├── br_mega_sena.json
│   ├── br_lotofacil.json
│   └── solar_k_index.json             # NEW Apr 27
├── GEMINI_SESSION_REVIEW.md
├── 2026-04-26-gemini-session.md / 2026-04-26-gemini-session-2.md  (logs)
└── verify_hits.py
```

## Tech Stack
- **Python**: FastAPI (planned), Typer, pandas, numpy, scipy, rich — engine core
- **Go**: API gateway — auth, rate limiting, caching, proxy (not yet built)
- **TypeScript + Expo**: React Native + Web frontend (not yet built)
- **Lottery targets**: Mega-Sena (Brazil), Lotofacil (Brazil), Powerball (US)

## What is fully working

### Sprint 1 ✅ DONE
- `lottery fetch <lottery>` — smart incremental fetch (only missing draws)
- `lottery analyze <lottery>` — frequency, deviation, correlation modules
- `lottery suggest <lottery> --strategy <name>` — any single or comma-joined strategy (auto voting ensemble)
- `lottery strategies` — list registered strategies
- `lottery docs` — full educational reference
- `lottery validate <lottery> <numbers>` — check user ticket against history
- `BaseStrategy.suggest()` injects parameters via `inspect.signature`
- Comma-joined strategies trigger an automatic voting ensemble

### Sprint 1.2 ✅ DONE (out-of-plan, formalized 2026-04-26)
- `lottery backtest <lottery> [draw_id]` — honest blind testing. Single ID, comma list, range, `--prev 1-10`. Strategy name, comma list, or `all`.
- `lottery optimize <lottery>` — grid search across (strategy × history_limit × temperature) measured by top-N capture rate.

### Sprint 1.3 ✅ DONE (out-of-plan, formalized 2026-04-28) — Absurdity Engine v4–v10
- 9 new strategies (3 statistical, 6 fun) listed in the structure tree above.
- `engine/modules/geometry.py` — dodecahedron adjacency.
- New `BaseStrategy.suggest` features: Chaos Temperature Governor, Intentional Seeding (SHA-256), Atmospheric Muon Flux (XOR bit-flip), Adaptive History Sweep.
- New CLI flags on `lottery suggest`: `--full-name`, `--birth-date`, `--topic`, `--adaptive-window`.
- Documentation: `docs/USER_GUIDE.md` (mystic-flavored), `docs/TECHNICAL_SPEC.md` (12 formula sections), `docs/versions/v4.0.md…v10.0.md`.

### Sprint 1.4 ✅ PARTIALLY DONE (built into BaseStrategy, 2026-04-27)
- Sum-Range Check, Parity Balance, Decade Breadth — auto-enforced inside `BaseStrategy.suggest` via the v5.0 "Balanced Wheel Filter" resampling loop.
- Still pending for Sprint 2 closure: surface as `--filters` flag with opt-in/out semantics, add `no_arithmetic`/`no_consecutive_run`/`no_same_last_digit`/`no_calendar_cluster`, build `lottery check` reporting command.

### Latent / staged but not exposed
- `_STRATEGY_EXPLAINERS` / `_STRATEGY_PRESETS` dicts in `engine/cli/main.py` — data layer for a future `lottery compare` / `lottery wizard`. Help text references `lottery wizard` but no such command is registered.

## Sprint Plan (v4 — updated 2026-04-28)

Authoritative file: `SPRINT_PLAN.md` at workspace root. Snapshot:

1. **Sprint 1 — The Engine** ✅ DONE
2. **Sprint 1.2 — Validation Layer** ✅ DONE (`backtest`, `optimize`)
3. **Sprint 1.3 — Absurdity Engine v4–v10** ✅ DONE (9 strategies + geometry + adaptive window + intentional seed + muon flux)
4. **Sprint 1.4 — BaseStrategy Filter Layer** ✅ PARTIAL (sum/parity/decade enforced; surface as `--filters` in Sprint 2)
5. **Sprint 1.1 — Sum-Range + Odds Patch** ⏳ NEXT
6. **Sprint 1.5 — Wheels Promotion**
7. **Sprint 2 — The Sidecar (FastAPI)** + Howard CLI add-ons
8. **Sprint 2.1 — Crowd-Avoidance Extension**
9. **Sprint 3 — Go Gateway + Game Registry**
10. **Sprint 4 — Expo App** (Nerd + Chaos modes; 9 new strategies plug into Chaos slider)
11. **Sprint 5 — Content + Deploy** (4 blog posts; v4–v10 docs are draft material for absurdity-track posts)
12. **Sprint 6 — Ecosystem**

## Cross-cutting principles (locked 2026-04-25, reinforced 2026-04-28)
- **Chi² gate everywhere** — every "predictive" surface gates on chi² p-value AND Sprint 1.2 empirical capture rate. All Sprint 1.3 esoteric strategies will land `is_predictive: false` for any fair lottery, by design.
- **Distinguish EV from P(win)** — anti-popular and game-selector are EV claims (always real); hot/cold are P(win) claims (real only when chi² rejects uniformity).
- **Engine stays dependency-light**; wheels module zero-dep so it can split out as standalone PyPI.
- **Adapters are the source of truth** — all tables computed from `DrawRules`, never hardcoded per game.
- **Parallel positioning** — Nerd-mode (credibility, Smart Luck Parity Pack) + Chaos-mode (Absurdity Engine, mystic). Both ship; Sprint 4 UI split makes the choice explicit.

## Open decisions (2026-04-28)
1. Positioning conflict between Smart Luck Parity Pack and Absurdity Engine — resolve via parallel Nerd/Chaos tracks.
2. Only one test file (`test_kabbalistic.py`) exists despite 9 new strategies — backfill tests as Sprint 1.5 prerequisite.
3. Default values for `--full-name` / `--birth-date` may produce misleadingly "personalized" tickets — either require flags or label as unseeded.
4. `docs/versions/v4.0.md…v10.0.md` claim version bumps that don't exist in `pyproject.toml` — tag git releases or rename to "feature-batch-N".
5. `BaseStrategy` filter pipeline is currently always-on; Sprint 2 `--filters` was meant to be opt-in. Decide: invert (always-on with `--no-filters`) or move to opt-in.

## What we can ship right now (single-session targets, leverage-ranked)

1. Backfill tests for the 9 Sprint 1.3 strategies + the `BaseStrategy` filter pipeline.
2. `engine/modules/sum_range.py` + `pattern.py` refactor — unblocks 5 downstream features (Sprint 1.1).
3. Decide and implement open-decision #5 on filter opt-in/out semantics.
4. Rename `docs/versions/v*.md` to `feature-batch-N.md` OR tag git releases.
5. `copairs` strategy — wire up existing `correlation.py`.
6. `engine/wheels/` promotion — split `steiner_wheel.py`, add full + key + evaluator + LJCR JSON.
7. `lottery check <game> <numbers>` — ticket evaluator using existing filter predicates.
8. `--pool` / `--key` / `--filters` flags on `lottery suggest`.

## Why: monetizable OSS side project generating multiple income streams (OSS credibility → app → content)
## How to apply: check `SPRINT_PLAN.md` first; respect the parallel Nerd/Chaos positioning; the Absurdity Engine work shipped fast but adds test debt and a positioning question that needs to be resolved before Sprint 5 content
