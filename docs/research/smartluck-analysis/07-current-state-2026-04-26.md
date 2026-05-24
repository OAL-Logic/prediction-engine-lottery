---
title: Reconciliation v2 — Current Codebase State
project: Prediction Engine
date: 2026-04-26
supersedes: 06-reconciliation-with-current-state.md
status: snapshot
note: |
  After auditing the actual codebase on 2026-04-26 we found two
  out-of-plan CLI commands shipped in a Gemini-CLI session — `lottery
  backtest` and `lottery optimize`. Both are now formalized as
  Sprint 1.2 in the master plan. This file replaces 06.
---

# Reconciliation v2 — 2026-04-26

The authoritative roadmap is now `SPRINT_PLAN.md` at the workspace root.
This file documents the *delta* between the original plan and the
codebase as of 2026-04-26 — what shipped, what didn't, and what was
added without being on the plan.

## Summary

| Category | Count |
|---|---|
| Sprint 1 items shipped | All |
| Out-of-plan items shipped | 2 (`backtest`, `optimize`) — promoted to Sprint 1.2 |
| Plan items still pending | All of Sprint 1.1, 1.5, 2, 2.1, 3, 4, 5, 6 |

## What is fully working in `lottery-engine/`

- 3 adapters: `br/mega-sena`, `br/lotofacil`, `us/powerball` — smart
  incremental fetch (only pulls missing draws).
- 3 modules: `frequency.py`, `deviation.py`, `correlation.py`.
- 23 strategies across 4 tiers (statistical / ML / deep / fun) plus
  3 ensembles (`voting`, `prob_weighted`, `hybrid`).
- 8 CLI commands as `@app.command()`:
  `fetch`, `analyze`, `suggest`, `strategies`, `docs`, `validate`,
  `backtest`, `optimize`.

## Out-of-plan additions (NEW Sprint 1.2)

### `lottery backtest`
`engine/cli/main.py` lines 772–1008. Honest blind testing — strategy
only sees draws before the target. Supports single ID, comma list,
range (`2990-2999`), and relative-from-latest (`--prev 1-10`).
Strategy can be a single name, comma list, or `all`.

### `lottery optimize`
`engine/cli/main.py` lines 1009–1175. Grid search across
`(strategy × history_limit × temperature)` measured by top-N capture
rate over a validation window.

### Why this matters

- **Empirical floor for the chi² gate.** The Sprint 2 `is_predictive`
  flag was supposed to come only from a chi² p-value test. It can now
  also embed empirical capture rates — much harder to argue against.
- **Free ammo for blog post I.1.** "What a quant would do with lottery
  data" — paste optimizer output as proof none of the 23 strategies
  meaningfully beats uniform on a fair lottery.
- **App credibility surface.** Sprint 4 nerd mode gets a "best
  historical capture@N" badge per strategy.

## Already implemented (still relevant from 06)

### `engine/strategies/statistical/crowd_avoidance.py`
Covers most of **E (Anti-Popular Strategy)**. Already has
`birthday_penalty=0.5` and `round_penalty=0.4`. Remaining work in
Sprint 2.1: add sum-region preference (uses `sum_range` from 1.1),
lucky-number heuristics (7/11/13/17/21/23/33/77), repeating-digit and
betslip-diagonal patterns.

### `engine/strategies/statistical/steiner_wheel.py`
Covers a slice of **D (Wheels Module)** — Steiner-style covering
designs are exactly the abbreviated wheel family. Already
parameterized `pool_size=15, match_guarantee=3, max_tickets=100`.
Remaining work in Sprint 1.5: promote from a single-file strategy to
top-level `engine/wheels/`, add full + key wheels, evaluator, LJCR
JSON, standalone PyPI.

## Still entirely new

| Item | Sprint | Status |
|---|---|---|
| `engine/modules/sum_range.py` (A) | 1.1 | not started — highest priority |
| `engine/odds/comparator.py` (C) | 1.1 | not started |
| `engine/wheels/` promotion (D) | 1.5 | not started |
| FastAPI sidecar + endpoints (B/F/G/H) | 2 | not started |
| `lottery check <game> <numbers>` | 2 | not started |
| `lottery analyze` 14-chart expansion | 2 | not started |
| `--pool` / `--key` / `--filters` on suggest | 2 | not started |
| `copairs` strategy | 2 | not started |
| Crowd-avoidance extension | 2.1 | not started |
| Go gateway | 3 | not started |
| `data/games/registry.yaml` | 3 | not started |
| Expo app | 4 | not started |
| Blog posts I.1–I.4 | 5 | not started |

## Latent / staged but not exposed

- `_STRATEGY_EXPLAINERS` and `_STRATEGY_PRESETS` dicts in
  `engine/cli/main.py` (around line 1379+) are the data layer for a
  `lottery compare` command. The command itself is not registered as
  `@app.command()`.
- The CLI help text references `lottery wizard` (line 38) — no such
  command exists. Either build it (data is already there) or strip
  the reference.

## Recommended immediate next steps (in code order, leverage-ranked)

1. Create `engine/modules/sum_range.py` (Sprint 1.1 A).
2. Refactor `engine/strategies/statistical/pattern.py` to consume it.
3. Wire up `copairs` strategy on top of existing `correlation.py`
   (Sprint 2 G — small enough to ship inside Sprint 1.1).
4. Promote `steiner_wheel.py` → `engine/wheels/` (Sprint 1.5 D).
5. Begin Sprint 2 — FastAPI sidecar — with Combo Audit, sum-distribution,
   and chi² gating as first-class endpoints, AND embedding
   Sprint 1.2 backtest capture rates in `is_predictive`.

This reconciliation supersedes 06. The master plan is `SPRINT_PLAN.md`
at the workspace root.
