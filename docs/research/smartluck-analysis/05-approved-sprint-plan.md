> ⚠️ **SUPERSEDED (2026-04-26)** — Folded into SPRINT_PLAN.md (Sprint 1.1, 1.5, 2, 2.1) at the workspace
> root. Preserved for historical reference.

---

---
title: Approved Sprint Plan v2 — Smart Luck Pull Locked In
project: Prediction Engine
date: 2026-04-25
status: approved (full slate)
supersedes: original sprint plan in MEMORY
---

# Approved Sprint Plan v2

User decision (2026-04-25): **adopt the full slate** of additions
derived from the Smart Luck article analysis. This document is now the
authoritative roadmap. The original 5-sprint plan keeps its anchors;
two new mid-sprints are inserted, and existing sprints absorb the
new endpoints / charts / content.

## Glossary of additions

| Code | Item | Tier |
|------|------|------|
| A    | Sum-Range Module                     | 1 |
| B    | Combo Audit API                      | 1 |
| C    | Game-Selector / Odds Comparator      | 1 |
| D    | Wheels Module (+ standalone PyPI)    | 2 |
| E    | Anti-Popular Strategy                | 2 |
| F    | Bell-Curve Viz                       | 3 |
| G    | Skip-and-Hit Viz                     | 3 |
| H    | Chi² Gate Surfacing                  | 3 |
| I.1  | Blog: Quant approach to lottery      | content |
| I.2  | Blog: Handicapping vs technical analysis | content |
| I.3  | Blog: How wheel software works (launch post for D) | content |
| I.4  | Blog: Anti-popular combos (launch post for E) | content |

---

## Sprint 1 — The Engine (OSS anchor)

Original goal: Python core + adapters + frequency + deviation + CLI.

**Add:**
- **A** — `engine/modules/sum_range.py` (analytical truncated-normal,
  exposes `most_probable_range(rules, coverage=0.70)`, `pmf(rules)`,
  `classify(combo, rules)`).
- **C** — `engine/odds/comparator.py` (cross-adapter ranking; CLI
  `lottery odds` and `lottery odds --compare`).
- 🔧 Refactor `strategies/statistical/pattern.py` to consume `sum_range`
  instead of empirical sampling. Drop `n_samples` parameter.

**Tests:**
- For every published Smart Luck `(pick, n)` row, computed range matches
  within ±1.
- Mega-Sena (6/60) midpoint = 183, range ≈ 140–226.
- Lotofácil (15/25) midpoint = 195, range ≈ 176–214.

**Definition of done:** CLI emits `lottery audit --combo 3,17,23,24,36,47`
returning sum bucket + envelope flags; `lottery odds --compare` ranks
all registered adapters.

---

## Sprint 1.5 — Wheels (NEW)

Insert before sidecar work. This is the OSS magnet, inserted early to
maximize GitHub-star runway.

**Build:**
- **D** — `engine/wheels/`:
  - `full_wheel.py` — `C(n, pick)` enumeration.
  - `key_wheel.py` — fix one number, wheel the rest.
  - `abbreviated.py` — load published covering designs from a static
    JSON (LJCR best-known sizes for k≤12, t≤5).
  - `evaluator.py` — given a wheel + hypothetical winning combo, list
    which tickets win which prize tier.
- Standalone PyPI package `lottery-wheels` (zero deps, MIT) re-exporting
  the same module — for users who want wheels without the rest of the
  engine.
- **I.3** — Launch blog: "We open-sourced what Smart Luck charges
  $100+ for." Linked from README.

**Tests:**
- Parity against published Gail Howard wheel sizes for `(7,6)`, `(8,6)`,
  `(10,6)` etc.
- Parity against LJCR best-known covering numbers for sampled
  `(v, k, t)` triples.

**Definition of done:** `lottery wheel --pick 6 --pool 1,5,12,17,23,29,36,42 --guarantee 4if6`
emits a deterministic, minimal-tickets table.

---

## Sprint 2 — The Sidecar

Original goal: wrap the engine in FastAPI; internal only.

**Add:**
- **B** — `POST /games/{slug}/combo/audit` returning the full audit
  (sum bucket + envelope + popularity score + chi²-gated
  `is_predictive` flag).
- **F** — `GET /games/{slug}/sum-distribution` (bins, counts, pdf,
  range_70, midpoint).
- **G** — `GET /games/{slug}/gap/{number}` (gap series + histogram).
- **H** — Every endpoint that produces a recommendation embeds
  `is_predictive` + caveat string derived from the chi² p-value.
- New endpoint surface (full):
  ```
  GET  /games
  GET  /games/{slug}/odds
  GET  /games/compare
  GET  /games/{slug}/sum-distribution
  GET  /games/{slug}/gap/{number}
  POST /games/{slug}/combo/audit
  POST /games/{slug}/wheel
  POST /games/{slug}/strategy/{name}
  ```

---

## Sprint 2.5 — Anti-Popular (NEW)

Inserted after the sidecar so the strategy can plug into the
existing `BaseStrategy` registry and be served via
`POST /games/{slug}/strategy/popularity`.

**Build:**
- **E** — `engine/strategies/popularity.py`:
  - Heuristic crowd-pick proxy: calendar bias (1–31), repeating digits,
    "lucky" numbers (7, 11, 13, 17, 21, 23, 33, 77, …), betslip-diagonal
    patterns, multiples of 5/10.
  - Sum-region preference: upper half of the 70% range (Smart Luck
    idea #8 absorbed here).
  - Output: per-number popularity-resistance score + helper
    `generate_combos(rules, n_combos, anti_popularity_strength)`.
- Auto-registered via `@register` decorator (mirrors `pattern.py`).

**Definition of done:** `lottery strategy popularity` returns top-N
combos ranked by inverse popularity, and audit endpoint includes the
score per combo.

---

## Sprint 3 — Go Gateway

Original goal: HTTP proxy + rate limiting + auth skeleton.

**Add:** No new functional surface — gateway just proxies all the
endpoints added in Sprint 2/2.5. Add cache TTLs:
- `/sum-distribution` — 24h (rarely changes per draw)
- `/odds`, `/games/compare` — static, infinite TTL
- `/combo/audit` — no cache (user-specific)
- `/strategy/*` — short TTL (5min) to absorb burst load

---

## Sprint 4 — Expo App

Original goal: Nerd mode first, Chaos mode second.

**Nerd mode (must-have visuals):**
- Bell-curve chart with the user's combo overlaid (consumes F).
- Per-number gap histogram (consumes G).
- Chi² gate badge: "Game appears statistically fair — predictions are
  heuristic only" when `is_predictive: false`.

**Chaos mode (Anti-Popular UX):**
- "Don't try to win MORE — try to share LESS." Headline.
- Anti-popular slider (strength 0–1) → calls strategy E, displays
  generated combos, each with a "shareability" badge.
- Combo Audit screen — paste numbers, get full audit + share.

**Onboarding:**
- Game-Selector step using C (`/games/compare`). Asks user goal:
  "Big jackpot" vs "More frequent wins" vs "Lowest cost per ticket"
  → ranks adapters accordingly.

---

## Sprint 5 — Content + Deploy

Original goal: write-up, hosted demo, monetization hooks.

**Content (all four blog posts):**
- **I.1** — *What a quant would do with lottery data (and why mostly
  nothing).* Top-of-funnel SEO. Anchors the integrity moat.
- **I.2** — *Lottery handicapping vs technical analysis: same illusions,
  different prices.* Repurposes the "horse-racing / Wall Street" framing
  Smart Luck uses but reframes it honestly.
- **I.3** — *How wheel software works and why we open-sourced it.*
  (Co-launched with Sprint 1.5.)
- **I.4** — *Don't try to win more — try to share less. Anti-popular
  combos explained.* (Co-launched with Sprint 2.5.)

Each post links: GitHub repo, hosted demo, the corresponding endpoint
or CLI command.

---

## Cross-cutting principles (locked)

1. **Chi² gate everywhere.** Any "predictive" surface returns
   `is_predictive` and a one-line caveat. Disabled if the game looks
   statistically fair.
2. **Distinguish EV from P(win).** Anti-popular and game-selector are
   EV claims (real). Hot/cold are P(win) claims (real only when chi²
   gate trips).
3. **Engine stays dependency-light.** `numpy`, `scipy`, `pandas` only
   in the engine. Wheels module zero-dep so it can be split out.
4. **Adapters are the source of truth.** All lookup tables (sum range,
   odds, popularity heuristics) are computed from `DrawRules`, not
   hardcoded per game.
5. **Smart Luck Parity Pack** — repo README explicitly positions us as
   "the OSS version of what Smart Luck sells, with the math gated on
   significance tests."

---

## Quick reference — what to build first

If you sit down today and have one weekend, build **A** (Sum-Range
Module). It unblocks B, F, and the pattern.py refactor — that's the
single highest-leverage change.

If you have a second weekend, build **D** (Wheels Module) and ship
**I.3** (the wheel-software blog post). That's the OSS launch beat
with the most viral surface area.

If you have a third weekend, build **E** (Anti-Popular Strategy) and
ship **I.4**. Now you have the differentiated narrative.

Everything else is glue and UI on top of those three.
