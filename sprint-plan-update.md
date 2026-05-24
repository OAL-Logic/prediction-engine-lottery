> ⚠️ **SUPERSEDED (2026-04-26)** — The authoritative roadmap is now
> `SPRINT_PLAN.md` at the workspace root. This file is preserved for
> historical reference. All additions documented here are folded into
> Sprint 2 in the master plan. Two new items have shipped since this
> file was written (`lottery backtest`, `lottery optimize`) — see
> Sprint 1.2 in `SPRINT_PLAN.md`.

---

# Prediction Engine — Sprint Plan Update
## Source: Gail Howard / SmartLuck Analysis (2026-04-25)

This document records all confirmed additions to the sprint plan derived from the
Gail Howard material analysis. Every item was explicitly approved.
Full analysis lives in `gail-howard-analysis.md`.

---

## Decisions Summary

| Idea | Feature | Approved Sprint |
|---|---|---|
| Idea 11 | `lottery check` ticket evaluator | Sprint 2 |
| Idea 4  | `lottery analyze` charts command | Sprint 2 |
| Idea 2  | `--pool` flag on `lottery suggest` | Sprint 2 |
| Idea 3  | `--key` flag on `lottery suggest` | Sprint 2 |
| Idea 6  | Last digit filter + analysis | Sprint 2 |
| Idea 8  | Expose 70% sum band in output | Sprint 2 |
| Idea 7  | `--filters` composable filter system | Sprint 2 |
| Idea 12 | `copairs` strategy (wire up `correlation.py`) | Sprint 2 |
| Idea 1  | Lottery Wheeling Module (`lottery wheel`) | Sprint 3 |
| Idea 10 | Extended game registry (100+ games YAML) | Sprint 3 |

---

## Sprint 2 — The Sidecar (EXPANDED)

**Original scope:** Wrap engine in FastAPI. Internal only, no auth yet.

**Added scope from Gail Howard analysis:**

### A. `lottery check <game> <numbers>` — Ticket Evaluator

New top-level CLI command. Evaluates a user-provided ticket against all structural rules and returns a scored report.

```bash
lottery check br/mega-sena 3,12,24,31,45,47
```

**Output format:**
```
Ticket: 3 12 24 31 45 47

✅ Sum: 162 — within 70% band (135–195)
✅ Odd/Even: 3/3 — balanced
✅ High/Low: 3/3 — balanced
✅ Decades: 1-10(1) 11-20(1) 21-30(1) 31-40(1) 41-50(2) — well spread
✅ Last digits: 3 2 4 1 5 7 — all unique
⚠️  Calendar cluster: 4 of 6 numbers ≤ 31 — competing with birthday pickers
✅ No consecutive run of 4+
✅ No arithmetic sequence detected

Structural score: 85/100 — Strong ticket
```

**Implementation notes:**
- Reuses all filter logic from the `--filters` system (item D below)
- The 70% sum band is computed from historical data on first run, cached
- Output is also exposed via FastAPI endpoint: `POST /check`

---

### B. `lottery analyze <game>` — Advantage Charts Command

New top-level CLI command. A comprehensive multi-chart analysis report, the OSS equivalent of Howard's "Lottery Advantage Charts" product.

```bash
lottery analyze br/mega-sena
lottery analyze us/powerball --charts frequency,sum,pairs
```

**Charts included:**
1. **Frequency Table** — all-time frequency + hot/cold rank per number
2. **Recency Table** — frequency in last 10 / 30 / 60 draws
3. **Gap (Skip) Table** — draws since each number last appeared
4. **Sum Distribution** — histogram with 70% band (P15–P85) highlighted
5. **Odd/Even Distribution** — % breakdown across all draws
6. **High/Low Distribution** — % breakdown across all draws
7. **Positional Frequency** — which numbers prefer which sorted position
8. **Decade/Group Frequency** — numbers per decade per draw distribution
9. **Last Digit Frequency** — frequency by terminal digit 0–9
10. **Consecutive Pair Rate** — % of draws containing at least one consecutive pair
11. **Repeat Rate** — how many numbers from the previous draw reappear
12. **Hot Pairs Table** — top 20 number pairs by co-occurrence (from `correlation.py`)
13. **Cycle Detection Summary** — top 5 numbers with spectral periodicity signal
14. **Day-of-Week Bias** — per-number frequency by draw day (if draw days vary)

**Implementation notes:**
- No new math — all data computed from existing modules; this is presentation only
- Rich terminal output using `rich` library (already in project dependencies)
- Also exposed via FastAPI: `GET /analyze/{game_id}`
- `--charts` flag allows selective output; `--format json` outputs raw data for app layer

---

### C. `--pool` and `--key` flags on `lottery suggest`

Two new flags that complete the "Howard workflow": select numbers you believe in, then generate tickets from them.

```bash
# Constrain suggestions to pool only
lottery suggest br/mega-sena --strategy weighted,bayesian --pool 3,7,12,24,31,45

# Guarantee one number appears in every ticket
lottery suggest br/mega-sena --strategy weighted --key 7

# Full Howard workflow: pool + key + filters
lottery suggest br/mega-sena \
  --strategy weighted,bayesian \
  --pool 3,7,12,24,31,45,9,18,22,36 \
  --key 24 \
  --filters sum_range,no_all_even
```

**Implementation notes:**
- `--pool`: filter the engine's score map to only pool members before sampling
- `--key`: post-processing step — enforce key number inclusion in every sampled ticket
- Both work transparently with every existing strategy and ensemble
- Both exposed as FastAPI params: `POST /suggest?pool=3,7,12&key=24`

---

### D. `--filters` Composable Structural Filter System

A `--filters` flag on `lottery suggest` (and used internally by `lottery check`). Applies binary rejection rules post-sampling. Tickets that fail a filter are resampled.

```bash
lottery suggest br/mega-sena --strategy weighted --filters sum_range,no_all_even
lottery suggest br/mega-sena --filters all   # apply all standard filters
```

**Filter catalog:**
| Filter name | Rule |
|---|---|
| `no_all_odd` | Reject tickets with all odd numbers |
| `no_all_even` | Reject tickets with all even numbers |
| `no_all_high` | Reject if all numbers > pool midpoint |
| `no_all_low` | Reject if all numbers ≤ pool midpoint |
| `no_single_decade` | Reject if all numbers from the same decade |
| `no_same_last_digit` | Reject if 3+ numbers share terminal digit |
| `no_arithmetic` | Reject arithmetic sequences (e.g. 5,10,15,20,25,30) |
| `no_consecutive_run` | Reject if 4+ consecutive numbers appear |
| `sum_range` | Reject if sum falls outside historical P15–P85 band |
| `no_calendar_cluster` | Warn/reject if 4+ numbers ≤ 31 (birthday picker bias) |
| `all` | Apply all filters above |

**Implementation notes:**
- Each filter is an O(k) function where k = ticket size
- Filters compose cleanly — any combination works
- If a valid ticket cannot be found after N attempts, relax the strictest filter and warn the user
- The filter pipeline is also the core of `lottery check`

---

### E. Last Digit Frequency Analysis + Filter

Two components bundled as part of the Sprint 2 additions:

1. **Chart 9 in `lottery analyze`:** Frequency distribution by terminal digit (0–9). Shows which last digits appear most in winning draws.

2. **`no_same_last_digit` filter** (part of `--filters` above): Rejects tickets where 3 or more numbers share the same terminal digit.

```bash
# See last-digit chart
lottery analyze br/mega-sena --charts last_digit

# Apply filter on suggestions
lottery suggest br/mega-sena --filters no_same_last_digit
```

---

### F. 70% Sum Band — Explicit Display

Surface the historical sum distribution's P15–P85 band (the "70% zone") in:
1. The sum distribution chart in `lottery analyze`
2. The `sum_range` filter in `--filters`
3. The sum check line in `lottery check`
4. `lottery docs sum_formula` documentation page

```bash
lottery docs sum_formula   # explains the concept
lottery analyze br/mega-sena --charts sum   # shows the band visually
```

---

### G. `copairs` Strategy — Wire Up `correlation.py`

`correlation.py` already exists in `engine/modules/` but is never called by any strategy or CLI command. This item wires it up.

**New strategy: `copairs`**
- Builds a co-occurrence matrix across all historical draws
- Scores each number by its co-occurrence frequency with the current draw's most recent hot numbers
- Produces an evidence panel showing the top 10 hot pairs

```bash
lottery suggest br/mega-sena --strategy copairs
lottery suggest br/mega-sena --strategy copairs,weighted,bayesian
```

**Chart 12 in `lottery analyze`:** Top 20 co-occurring number pairs with occurrence counts.

**Implementation notes:**
- `correlation.py` likely already computes the co-occurrence matrix
- Verify its interface before wiring; may need a thin adapter
- Add `copairs` to all strategy presets in `_STRATEGY_PRESETS`
- Add `_STRATEGY_EXPLAINERS` entry for `compare` output

---

## Sprint 3 — Go Gateway (EXPANDED)

**Original scope:** HTTP proxy + rate limiting + auth skeleton.

**Added scope from Gail Howard analysis:**

### H. Lottery Wheeling Module (`lottery wheel`)

The most significant new module. Generates a minimal set of tickets with a mathematical coverage guarantee given a user-defined number pool.

```bash
# Abbreviated wheel: 12 numbers, pick-6, guarantee 4-if-4
lottery wheel br/mega-sena \
  --pool 3,7,12,24,31,45,9,18,22,36,41,47 \
  --guarantee 4if4

# Key number wheel: number 12 in every ticket
lottery wheel us/powerball \
  --pool 5,12,23,31,44,62 \
  --key 12 \
  --guarantee 3if3

# Full wheel (all combinations — use for small pools only)
lottery wheel br/mega-sena --pool 7,12,24,31 --type full

# List available pre-computed wheel templates
lottery wheels --game-type pick6
lottery wheels --pool-size 12 --guarantee 4if4
```

**Wheel types to implement:**
- **Full wheel** — all C(n,k) combinations from pool. Practical up to ~9-10 numbers.
- **Abbreviated wheel** — minimum cover design. Uses combinatorial covering algorithms.
- **Key number wheel** — one number forced into every ticket; reduces total ticket count.

**Implementation approach:**
1. Start with full wheels (trivial `itertools.combinations`)
2. For abbreviated wheels: implement a greedy covering algorithm or use pre-computed covering design tables (publicly available in combinatorics literature — these are not Howard's IP)
3. For pick-5 and pick-6 standard guarantees (3if3, 4if4, 4if5, 5if5), a small table of known minimum wheels can be hardcoded
4. Expose `wheel` as a new engine module: `engine/modules/wheel.py`

**Coverage guarantee definition:**
- `4if4` = if 4 of your pool numbers are in the winning draw, at least 1 of your tickets matches all 4
- `3if3` = if 3 of your pool numbers are in the winning draw, at least 1 ticket matches all 3
- The guarantee is a mathematical property of the covering design — it holds regardless of which numbers are drawn

**FastAPI endpoint:** `POST /wheel` — accepts pool, guarantee, game_id; returns ticket set + guarantee explanation

---

### I. Extended Game Registry (100+ games)

A YAML file encoding all major world lotteries with their parameters. Makes adding new adapters trivial and enables auto-parameterization of `lottery analyze`, `lottery wheel`, and `lottery check`.

**File:** `data/games/registry.yaml`

**Schema per game:**
```yaml
- id: br/mega-sena
  name: Mega-Sena
  country: Brazil
  pick_count: 6         # how many numbers drawn
  pool_size: 60         # total ball range
  bonus_pool: null      # null if no bonus ball
  bonus_pick: null
  draw_days: [Wednesday, Saturday]
  draw_city: "São Paulo"
  draw_city_lat: -23.5505
  draw_city_lon: -46.6333
  adapter: mega_sena    # maps to engine/adapters/mega_sena.py
  data_available: true

- id: us/powerball
  name: Powerball
  country: USA
  pick_count: 5
  pool_size: 69
  bonus_pool: 26
  bonus_pick: 1
  draw_days: [Monday, Wednesday, Saturday]
  draw_city: "Tallahassee, FL"
  draw_city_lat: 30.4383
  draw_city_lon: -84.2807
  adapter: powerball
  data_available: true
```

**Scope for Sprint 3:**
- Write the schema + populate all 150 games from the Howard dropdown (data entry, not code)
- Update engine to read game parameters from registry instead of hardcoding in adapter files
- Mark games as `data_available: false` until a fetcher is written — they'll appear in `lottery games` list but won't have data yet

**Community contribution path:**
- Each game with `data_available: false` is an open GitHub issue waiting for a contributor
- The registry + a clear fetcher template is how the engine grows to 100+ games organically

---

## Updated Full Sprint Plan

```
Sprint 1 — The Engine (OSS anchor)
  Python core: adapters + frequency + deviation modules + CLI
  GitHub first. [COMPLETE]

Sprint 2 — The Sidecar (EXPANDED)
  Original: Wrap engine in FastAPI. Internal, no auth.
  Added:
    A. lottery check <game> <numbers>      — ticket structural evaluator
    B. lottery analyze <game>              — 14-chart advantage report
    C. --pool and --key flags              — pool-constrained suggestions
    D. --filters system                    — composable structural rejection rules
    E. Last digit filter + analysis chart  — part of filters + analyze
    F. 70% sum band display                — surface the winning sum zone
    G. copairs strategy                    — wire up existing correlation.py

Sprint 3 — Go Gateway (EXPANDED)
  Original: HTTP proxy + rate limiting + auth skeleton.
  Added:
    H. lottery wheel module                — covering design ticket generation
    I. Extended game registry (YAML)       — 150 games parameterized

Sprint 4 — Expo App
  Nerd mode first, chaos mode second.
  Connect to Go gateway.
  lottery check → "Ticket Grader" UI card
  lottery analyze → "Game Dashboard" screen
  lottery wheel → "Wheel Builder" screen

Sprint 5 — Content + Deploy
  Write-up, hosted demo, monetization hooks.
  Each analyze chart → 1 blog post
  lottery check → SEO landing page: "Is my lottery ticket good?"
  lottery wheel → SEO landing page: "Lottery wheel generator"

Sprint 6 — Ecosystem
  Community adapters (new games via registry)
  Additional wheel types + larger guarantee tables
  Monetization layer on app
```

---

## What Was Skipped (and Why)

| Idea | Decision | Reason |
|---|---|---|
| Idea 5 — `group_balance` strategy | Not yet added | Decade analysis is already in `lottery analyze` chart 8; the strategy can be added later if users ask for it |
| Idea 9 — Birthday bias (standalone) | Folded into `--filters` | `no_calendar_cluster` filter covers it; no separate feature needed |
| Full wheel catalog (328 Howard systems) | Skipped | Howard's IP; engine builds the algorithm, not a catalog clone |
| Multilingual (Lotto Loteria) | Deferred | Sprint 5+ |

---

*Generated: 2026-04-25 | Based on: gail-howard-analysis.md*
