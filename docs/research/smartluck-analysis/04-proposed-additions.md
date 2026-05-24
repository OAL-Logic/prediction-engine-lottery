---
title: Proposed Sprint Additions — Smart Luck Pull
project: Prediction Engine
date: 2026-04-25
---

# Proposed Sprint Additions

Each item is sized by code effort (S/M/L) and ranked by expected
impact on the OSS positioning of the project. Pick any subset.

## Tier 1 — High impact, low effort, no controversy

### A. Sum-Range Module (S)
- New file: `engine/modules/sum_range.py`
- API:
  ```python
  most_probable_range(rules: DrawRules, coverage: float = 0.70) -> SumRange
  pmf(rules: DrawRules) -> dict[int, float]
  classify(combo: list[int], rules: DrawRules) -> Bucket  # low/mid-lo/mid-hi/high/out
  ```
- Implementation: analytical truncated normal (μ, σ from formulas in
  `02-sum-ranges-data.md`).
- Tests: assert that for every published Smart Luck `(pick, n)` the
  computed range is within ±1 of theirs.
- Impact: replaces sampling in `pattern.py`, powers Combo Audit and
  the bell-curve viz.

### B. Combo Audit API (S)
- Wraps `frequency`, `deviation`, `pattern`, `sum_range`, and the
  upcoming `popularity` strategy into a single endpoint.
- Output (per combo):
  - sum bucket + position on bell curve
  - odd/even ratio vs envelope
  - high/low ratio vs envelope
  - consecutive-pair count vs envelope
  - popularity score (after Tier-2 lands)
  - chi²-gated `is_predictive` flag
- Impact: viral feature, easy to demo, easy to monetize as "Audit Pro".

### C. Game-Selector / Odds Comparator (S)
- New module: `engine/odds/comparator.py`.
- API:
  ```python
  odds(rules: DrawRules) -> Odds        # jackpot, tier prizes, EV bands
  rank_games(adapters) -> list[GameRank]
  ```
- CLI: `lottery odds` and `lottery odds --compare`.
- Onboarding step in the Expo app.

## Tier 2 — High impact, medium effort, the OSS magnet

### D. Wheels Module (M-L)
- New top-level: `engine/wheels/`.
- Components:
  - `full_wheel.py` — `C(n, pick)` enumeration.
  - `key_wheel.py` — fix one number, wheel the rest.
  - `abbreviated.py` — load published covering designs from a static
    JSON shipped with the package (LJCR best-known values for k≤12,
    t≤5).
  - `evaluator.py` — given a wheel + a hypothetical winning combo,
    list which tickets win which prize tier.
- Tests: parity against published Gail Howard wheels + LJCR records.
- Distribution: also publish as standalone `lottery-wheels` PyPI
  package (zero deps) for max OSS reach.
- Blog post: "We open-sourced what Smart Luck charges $100+ for."

### E. Anti-Popular Strategy (M)
- New file: `engine/strategies/popularity.py`.
- Two scoring axes:
  1. **Crowd-pick proxy**: heuristic weights for calendar bias
     (1–31), repeating digits, "lucky" numbers, betslip patterns,
     consecutive-on-ticket choices.
  2. **Sum-region**: prefer upper half of the 70% range.
- API matches the existing `BaseStrategy` interface — auto-registered.
- Output: per-number popularity-resistance score, plus a
  `generate_combos(rules, n_combos, anti_popularity_strength)` helper.
- Sales line: "Don't try to win MORE — try to share LESS."

## Tier 3 — UX & Content

### F. Bell-Curve Visualization (S)
- FastAPI: `/games/{slug}/sum-distribution` returns `{bins, counts,
  pdf, range_70, midpoint}`.
- Expo Nerd-mode chart with the user's combo overlaid.

### G. Skip-and-Hit Visualization (S)
- FastAPI: `/games/{slug}/gap/{number}` returns the gap series and
  histogram.
- Expo Nerd-mode chart, low priority.

### H. Chi² Gate Surfacing (XS)
- API responses for any "predictive" recommendation include
  `is_predictive` and a one-liner caveat.
- UI: small badge ("Game appears statistically fair — predictions
  are heuristic only").

### I. Sprint-5 Content (no code)
- "What a quant would do with lottery data (and why mostly nothing)."
- "Lottery handicapping vs technical analysis: same illusions."
- "How wheel software works and why we open-sourced it."
- "Don't try to win more — try to share less. Anti-popular combos
  explained."

## Mapping to existing Sprint Plan

| Existing sprint | Add |
|---|---|
| Sprint 1 — Engine OSS anchor | A (sum_range), C (odds comparator) |
| Sprint 2 — FastAPI sidecar   | B (combo audit), F (sum-dist endpoint), G (gap endpoint), H (chi² gate) |
| Sprint 3 — Go gateway        | (no change) |
| Sprint 4 — Expo app          | bell-curve chart, gap chart, anti-popular toggle, game-selector onboarding |
| Sprint 5 — Content + deploy  | I (content drafts), launch wheels module + standalone PyPI package |
| **NEW Sprint 1.5 — Wheels**  | D (wheels module + LJCR data) — could ship before sidecar |
| **NEW Sprint 2.5 — Popularity** | E (anti-popular strategy) |

## Recommended pick if I had to choose 3

If the goal is maximum OSS pull with minimum code, ship in this order:

1. **A. Sum-Range Module** (one afternoon)
2. **D. Wheels Module** (one weekend)
3. **E. Anti-Popular Strategy** (one weekend)

Plus one blog post per item. That's the "Smart Luck Parity Pack" —
free OSS that does what they sell, with the chi² gate as the
integrity differentiator.
