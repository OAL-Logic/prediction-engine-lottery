> ⚠️ **SUPERSEDED (2026-04-26)** — Folded into 07-current-state-2026-04-26.md and SPRINT_PLAN.md at the workspace
> root. Preserved for historical reference.

---

---
title: Reconciliation — Approved Plan vs Current Codebase
project: Prediction Engine
date: 2026-04-25
note: |
  Discovered after writing 04 and 05: Sprint 1 is already complete and
  the codebase has advanced far beyond what the original memory snapshot
  showed. Several "new" proposals are partially implemented.
---

# Reconciliation

After re-reading the project memory, the codebase already contains
strategies that overlap two of our approved additions. Updating
the action plan below.

## Already implemented

### `engine/strategies/statistical/crowd_avoidance.py`
- Covers most of **E (Anti-Popular Strategy)**.
- Already has `birthday_penalty=0.5` and `round_penalty=0.4`.
- **Remaining work for E**:
  - Add the *sum-region* preference (Smart Luck idea #8 — upper half
    of the 70% range). Wire to the new `sum_range` module from A.
  - Extend heuristics: "lucky numbers" (7, 11, 13, 17, 21, 23, 33, 77),
    repeating-digit patterns (11/22/33), betslip-diagonal patterns.
  - Expose a `generate_combos(rules, n_combos, anti_popularity_strength)`
    helper if not present.

### `engine/strategies/statistical/steiner_wheel.py`
- Covers a slice of **D (Wheels Module)** — Steiner-style covering
  designs are exactly the abbreviated wheel family.
- Already parameterized: `pool_size=15, match_guarantee=3, max_tickets=100`.
- **Remaining work for D**:
  - Promote from a single-file strategy to a top-level `engine/wheels/`
    module so it's not nested under `strategies/statistical/`. Strategies
    are scoring layers; wheels are ticket-generation layers — different
    abstraction.
  - Add `full_wheel.py` (`C(n, pick)` enumeration) and `key_wheel.py`
    (fix one number, wheel the rest).
  - Add `evaluator.py` to score wheels against hypothetical outcomes.
  - Ship LJCR best-known covering-number JSON for k≤12, t≤5.
  - Carve out a standalone `lottery-wheels` PyPI package re-exporting
    the module — zero-dep MIT for max reach.
  - Launch blog post **I.3** stays.

## Still entirely new

- **A. Sum-Range Module** — `engine/modules/sum_range.py` does not exist;
  `pattern.py` still does empirical sampling. Highest priority.
- **B. Combo Audit API** — needs the FastAPI sidecar (Sprint 2).
- **C. Game-Selector / Odds Comparator** — `engine/odds/` does not exist.
- **F / G / H** — sidecar endpoints + viz, all new.
- **I.1–I.4** — content drafts, all new.

## Adjusted sprint mapping

| Sprint | What changes |
|--------|--------------|
| Sprint 1 (✅ done) | Add **A** (sum_range module) + **C** (odds comparator) + **🔧 refactor** pattern.py to use A. Backfill into the "engine" sprint as a 1.1 patch. |
| Sprint 1.5 (Wheels promotion) | Promote `steiner_wheel.py` → `engine/wheels/`. Add full + key wheels, evaluator, LJCR JSON, standalone PyPI. Ship blog **I.3**. |
| Sprint 2 (Sidecar — next up) | All endpoints from approved plan. Special focus on **H** chi² gating and **B** combo audit. |
| Sprint 2.1 (Crowd-avoidance extension) | Extend `crowd_avoidance.py` with sum-region preference (uses A) + lucky-number / repeating-digit heuristics. Renames internally to keep API stable. |
| Sprint 3 (Go gateway) | Cache TTLs as in approved plan. |
| Sprint 4 (Expo app) | Bell-curve overlay, gap chart, chi² badge, anti-popular slider, game-selector onboarding. |
| Sprint 5 (Content + deploy) | Ship **I.1**, **I.2**, **I.4**. (**I.3** already shipped with Sprint 1.5.) |

## What I will not propose (because it already exists)

- A standalone "Anti-Popular" strategy — `crowd_avoidance` is it. Just
  extend.
- A first-cut covering-design wheel — `steiner_wheel` is it. Just
  refactor and broaden.

## Recommended immediate next steps (in code order)

1. Create `engine/modules/sum_range.py` (A).
2. Refactor `engine/strategies/statistical/pattern.py` to consume it.
3. Create `engine/odds/comparator.py` (C) + CLI subcommand.
4. Begin Sprint 2 — FastAPI sidecar — with Combo Audit, sum-distribution,
   and chi² gating as first-class endpoints.

This reconciliation supersedes the sprint mapping in
`05-approved-sprint-plan.md` where the two conflict.
