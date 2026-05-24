# Gail Howard × Prediction Engine — Ideas Analysis

> Three-expert review of every major idea from Gail Howard's SmartLuck material.
> Each idea is assessed against the current engine, classified by status, and given an effort score.
>
> **Experts:**
> - 🔬 **Statistics/Algorithm** — mathematical validity, implementation complexity
> - 🎯 **Product/UX** — user value, CLI/app experience, differentiation
> - 💼 **Business/OSS** — monetization, community appeal, OSS credibility

---

## What's Already Covered (No Action Needed)

| Howard Concept | Engine Module | Notes |
|---|---|---|
| Hot/cold number frequency | `frequency.py`, `streak`, `bayesian` | Fully covered |
| Overdue / gap tracking | `deviation.py`, `weighted (gap_score)` | Fully covered |
| Positional frequency | `weighted (pos_score)` | Covered |
| Sum totals distribution | `pattern`, `monte_carlo` | Covered |
| Odd/even balance | `pattern` | Covered |
| High/low split | `pattern` | Covered |
| Consecutive pair limit | `pattern (consec_pairs)` | Covered |
| Lucky cycles / timing | `moon_phase`, `biorhythm`, `zodiac`, `numerology` | Covered (Fun tier) |
| Crowd avoidance (prize split) | `crowd_avoidance` | Covered |
| Wheel-like combinatorics | `steiner_wheel` | Partial — see Idea 1 |

---

## Ideas NOT in the Engine — Full Analysis

---

### Idea 1 — Lottery Wheeling Module (`lottery wheel`)

**Source:** "Lotto How to Wheel a Fortune" (328 pick-6 systems), "Lotto Wheel Five to Win" (333 pick-5 systems), "Lotto Winning Wheels for Powerball" (190 systems)

**The concept:**
You select a "pool" of N numbers you believe in (e.g., 12 numbers from a 49-ball game). A wheeling system generates the minimum set of tickets needed to **guarantee** a specific prize tier if enough of your pool numbers are drawn. A 4-if-4 guarantee means: if 4 of your 12 chosen numbers are in the actual draw, at least one of your tickets will have all 4.

**Wheel types:**
- **Full wheel** — every possible combination of your pool (factorial growth, rarely practical)
- **Abbreviated wheel** — fewer tickets, reduced but still guaranteed coverage
- **Key number wheel** — one "key" number appears in every ticket

**Three-expert review:**

🔬 **Algorithm:** Well-defined combinatorics problem. For small pools (8–14 numbers), abbreviated wheels are computable. The guarantee condition (t-if-t) is a covering design problem. Libraries exist (Python `itertools`, combinatorial design databases). The engine already has `steiner_wheel` which is a mathematical Steiner system — this is the natural user-facing complement.

🎯 **Product:** This is the single most requested feature in lottery software. "I have 12 numbers — give me the tickets" is how most serious lottery players actually think. The engine currently outputs individual ticket suggestions; a wheeling module outputs a *set of tickets with mathematical coverage*. Completely different user workflow.

💼 **Business:** This is also the core of Howard's **premium product** — her books and software are essentially wheel catalogs. Building an open-source wheeling engine with a clean CLI would directly position the project as the OSS alternative to SmartLuck. High community value, strong GitHub star magnet.

**Status:** 🆕 New — `steiner_wheel` is a single internal strategy, not a user-facing wheel system
**Effort:** Medium (2–3 days for core + CLI; full library is ongoing)
**Priority:** ⭐⭐⭐⭐⭐ HIGHEST

**Proposed CLI:**
```bash
# Generate an abbreviated wheel: 12 numbers, pick-6, guarantee 4-if-4
lottery wheel br/mega-sena --pool 3,7,12,24,31,45,9,18,22,36,41,47 --guarantee 4if4
lottery wheel us/powerball --pool 5,12,23,31,44,62 --key 12 --guarantee 3if3

# List available wheel templates
lottery wheels --game-type pick6
```

---

### Idea 2 — Pool Pre-selection Flag (`--pool`)

**Source:** Implicit in all of Howard's wheeling books — the first step is always selecting a "pool" of numbers before generating tickets.

**The concept:**
A `--pool` CLI flag that constrains the engine to only suggest tickets from a user-defined set of numbers. Currently, suggestions come from the full number range. With `--pool 3,7,12,24,31,45`, the engine would only pick from those 6 numbers.

**Three-expert review:**

🔬 **Algorithm:** Trivial to implement — filter the score map to only pool members before sampling. Works transparently with every existing strategy.

🎯 **Product:** This is the missing link between "give me hot numbers" and "now build me tickets from those numbers." It's the workflow Howard users already follow manually. Makes the engine a complete tool rather than just an oracle.

💼 **Business:** Very low effort, very high perceived value. Users who pre-select their "lucky numbers" can now wheel within them.

**Status:** 🆕 New
**Effort:** Small (< 1 day)
**Priority:** ⭐⭐⭐⭐

**Proposed CLI:**
```bash
lottery suggest br/mega-sena --strategy weighted,bayesian --pool 3,7,12,24,31,45
```

---

### Idea 3 — Key Number Flag (`--key`)

**Source:** "Key number wheels" — Gail Howard's concept where one number the player is most confident about appears in every ticket.

**The concept:**
A `--key 7` flag guarantees that number 7 appears in every generated ticket. When combined with `--pool` and the wheeling module, this completes the full Howard workflow.

**Three-expert review:**

🔬 **Algorithm:** Post-processing step on any suggestion output. After sampling tickets, enforce key number inclusion.

🎯 **Product:** Very natural user request — "I'm sure 7 is coming up, make sure it's in every ticket." Paired with `--pool`, gives users full control.

💼 **Business:** Tiny effort, makes users feel like experts.

**Status:** 🆕 New
**Effort:** Small (< 1 day)
**Priority:** ⭐⭐⭐

---

### Idea 4 — Advantage Charts Command (`lottery analyze`)

**Source:** "Lottery Advantage Charts" — ~30 analysis charts per game, Howard's visual representation of historical patterns.

**The concept:**
A `lottery analyze <game>` command that outputs a comprehensive multi-chart report. Howard's charts are a dashboard of statistical lenses — all of which the engine already computes internally but never surfaces as a standalone report.

**Proposed charts:**
1. **Frequency Table** — every number's all-time frequency + rank
2. **Hot/Cold Rankings** — last 10, 30, 60 draws
3. **Gap (Skip) Table** — draws since each number last appeared
4. **Sum Distribution** — histogram of winning sums with 70% band marked
5. **Odd/Even Distribution** — % breakdown of all odd/even splits
6. **High/Low Distribution** — % breakdown of all high/low splits
7. **Positional Frequency** — which numbers prefer which sorted positions
8. **Consecutive Pair Frequency** — how often consecutive numbers appear together
9. **Decade/Group Frequency** — numbers per decade per draw distribution
10. **Last Digit Frequency** — frequency by terminal digit (0–9)
11. **Repeat Rate** — how many numbers from the last draw appeared again
12. **Hot Pairs Table** — which number pairs appear most often together
13. **Cycle Detection** — spectral summary of detected periodicities
14. **Moon Phase Correlation** — top numbers per phase
15. **Day-of-Week Bias** — whether draw day correlates with any numbers

**Three-expert review:**

🔬 **Algorithm:** All data is already computed by existing modules. This is an aggregation/display command — no new math, just new presentation.

🎯 **Product:** Transforms the engine from a "just give me tickets" tool to a "let me understand this game" tool. Huge educational value. The `lottery analyze` output is inherently shareable.

💼 **Business:** This is a content marketing goldmine. Every chart can be a blog post. Strong OSS community driver.

**Status:** 🆕 New (as a unified command — individual pieces exist inside modules)
**Effort:** Medium (2 days to build the rich terminal output)
**Priority:** ⭐⭐⭐⭐⭐ HIGHEST

---

### Idea 5 — Decade / Number Group Strategy (`group_balance`)

**Source:** Howard's "lotto number groups" — dividing the number pool into decades (1–10, 11–20, etc.) and tracking which groups most commonly appear together.

**The concept:**
Most lottery draws spread across the number range. For a pick-6 game with numbers 1–49, you'd expect roughly 1–2 numbers per decade. The `group_balance` strategy scores candidates that fill underrepresented decades in the current partial ticket.

**Three-expert review:**

🔬 **Algorithm:** New strategy: compute decade of each number (floor((n-1)/10)). Score candidates that fill underrepresented decades. Can also be a post-sampling structural filter.

🎯 **Product:** Highly intuitive to explain — "pick at least one number from each zone." Great for educational content in `compare` output.

💼 **Business:** This is a strategy Howard popularized but didn't invent — observable statistical fact. Safe as open-source. Easy to visualize in the app layer.

**Status:** 🆕 New (distinct from `pattern` which only looks at sum/odd-even/high-low)
**Effort:** Small–Medium (1 day)
**Priority:** ⭐⭐⭐

---

### Idea 6 — Last Digit Frequency Analysis + Filter

**Source:** Howard's tip to avoid numbers sharing the same last digit (e.g., don't play 3, 13, 23, 33 together — statistically very rare).

**The concept:**
Two sub-components:
1. **Analysis:** Chart the frequency of terminal digits (0–9) across all winning draws (goes into `lottery analyze`)
2. **Filter:** Post-sampling filter that rejects tickets where 3+ numbers share the same last digit

**Three-expert review:**

🔬 **Algorithm:** Trivial — `number % 10`. Filter is a post-processing step on sampled tickets.

🎯 **Product:** One of Howard's most cited and actionable tips. Implementable in under an hour.

💼 **Business:** Good demo material — easy to show "before/after" of enabling the filter.

**Status:** 🆕 New
**Effort:** Small (< 1 day)
**Priority:** ⭐⭐⭐

---

### Idea 7 — Hard Structural Filters System (`--filters`)

**Source:** Howard's 9 basic tips on number avoidance from "Lottery Winning Strategies: & 70 Percent Win Formula."

**The concept:**
A set of **post-sampling hard filters** that reject structurally invalid tickets before returning suggestions. Unlike `pattern` (probabilistic scoring), these are binary rejection rules.

**Proposed filter set:**

| Filter | Rule |
|---|---|
| `no_all_odd` | Reject tickets with all odd numbers |
| `no_all_even` | Reject tickets with all even numbers |
| `no_all_high` | Reject tickets where all numbers > midpoint |
| `no_all_low` | Reject tickets where all numbers ≤ midpoint |
| `no_single_decade` | Reject if all numbers from same decade |
| `no_same_last_digit` | Reject if 3+ numbers share terminal digit |
| `no_arithmetic` | Reject arithmetic sequences (5,10,15,20,25,30) |
| `no_consecutive_run` | Reject if 4+ consecutive numbers appear |
| `sum_range` | Reject if sum falls outside the historical 70% band |
| `no_calendar_cluster` | Warn if 4+ numbers are ≤ 31 (birthday picker bias) |

**Three-expert review:**

🔬 **Algorithm:** All computable in O(k) per ticket. Should compose cleanly — any combination. The `monte_carlo` strategy already enforces some implicitly via simulation; exposing them as explicit flags is more transparent and user-controllable.

🎯 **Product:** Makes the engine "opinionated" in a good way. `--filters all` is a power-user feature that makes suggestions feel significantly smarter.

💼 **Business:** Howard's entire brand is built on these rules. Making them explicit and programmable is a strong OSS differentiator. Each filter is a documentation page.

**Status:** 🟡 Partial — `pattern` and `monte_carlo` encode some probabilistically; hard binary filters are new
**Effort:** Small (1 day)
**Priority:** ⭐⭐⭐⭐

**Proposed CLI:**
```bash
lottery suggest br/mega-sena --strategy weighted,bayesian --filters sum_range,no_all_even,no_same_last_digit
lottery suggest br/mega-sena --filters all   # apply all standard filters
```

---

### Idea 8 — Explicit "70% Sum Formula" Display

**Source:** Howard's "Secret Formulas that Win 70% of All Lotto Jackpots."

**The concept:**
For any pick-N game, compute the P15–P85 band of winning sums. Surface it as:
1. A visible stat in `lottery analyze` output
2. The `sum_range` filter in Idea 7
3. Documentation via `lottery docs sum_formula`

**Three-expert review:**

🔬 **Algorithm:** `np.percentile(historical_sums, [15, 85])` — one line. Already computed inside `pattern`; never shown to the user.

🎯 **Product:** "The 70% formula" is a great marketing hook. Showing users "your ticket sum of 240 is in the top 5% and almost never wins" is genuinely actionable.

💼 **Business:** Tiny effort, high content value. "Does your ticket pass the 70% test?" is a shareable, searchable concept.

**Status:** 🟡 Partial — computed internally, never surfaced to user
**Effort:** Tiny (< half day)
**Priority:** ⭐⭐⭐

---

### Idea 9 — Birthday Bias Awareness

**Source:** Howard's tip to avoid too many numbers ≤ 31, since most players use birth dates and prize splitting is likelier for those numbers.

**The concept:**
Extension of `crowd_avoidance`. The existing strategy estimates commonly played numbers. A specific sub-rule: 1–31 are overplayed due to birthday selection bias.
1. Show in `lottery analyze`: what % of winning draws had 4+ numbers ≤ 31
2. Filter `no_calendar_cluster`: warn/reject if 4+ numbers ≤ 31

**Three-expert review:**

🔬 **Algorithm:** Count numbers ≤ 31 in a ticket.

🎯 **Product:** "4 of your 6 numbers are ≤ 31 — you're competing with everyone who picks birthdays." Clear, memorable.

💼 **Business:** Explains prize-splitting in a relatable way. Good blog/content material.

**Status:** 🟡 Partial — `crowd_avoidance` exists but doesn't encode birthday bias specifically
**Effort:** Tiny (part of the Idea 7 filter set)
**Priority:** ⭐⭐

---

### Idea 10 — Extended Game Registry (100+ games)

**Source:** Howard's dropdown lists — USA (50+ states), Canada, and International (100+ unique games) with game-type codes like `5/39`, `6/49`, `5/70+1/25`.

**The concept:**
A structured YAML/JSON game registry encoding all major games with: pool size, pick count, bonus ball, draw frequency, draw city (for weather strategy), and country. Adapters would be auto-parameterized from the registry.

**Three-expert review:**

🔬 **Algorithm:** The registry is data, not code. The challenge is building history fetchers for each game. The current `mega_sena.py` and `powerball.py` adapters are manually written; the registry would generalize the pattern.

🎯 **Product:** "Supports 150 lotteries worldwide" is a massive differentiator. Even with 10 live fetchers, the registry makes future extension trivial.

💼 **Business:** International scope = international GitHub stars. Each new adapter is a community contribution opportunity.

**Status:** 🟡 Partial — 2 adapters exist; no formal registry
**Effort:** Medium–Large (registry: small; fetchers: ongoing community effort)
**Priority:** ⭐⭐⭐ (registry: high priority; fetchers: ongoing)

---

### Idea 11 — Ticket Evaluator (`lottery check`)

**Source:** Howard's concept of evaluating whether a player's own ticket "passes" her structural criteria.

**The concept:**
A `lottery check <game> <numbers>` command that evaluates a user-provided ticket against all structural rules and outputs a score card:

```
$ lottery check br/mega-sena 3,12,24,31,45,47

Ticket: 3 12 24 31 45 47

✅ Sum: 162 — within 70% band (135–195)
✅ Odd/Even: 3/3 — balanced
✅ High/Low: 3/3 — balanced
✅ Decades: 1-10(1), 11-20(1), 21-30(1), 31-40(1), 41-50(2) — well spread
✅ Last digits: 3,2,4,1,5,7 — all unique
⚠️  Calendar cluster: 4 of 6 numbers ≤ 31 — competing with birthday pickers
✅ No consecutive runs (4+)
✅ No arithmetic sequences

Structural score: 85/100 — Strong ticket
```

**Three-expert review:**

🔬 **Algorithm:** Applies all filter checks from Idea 7 and returns a structured report. One function, all filters.

🎯 **Product:** The killer user-facing feature. Users can evaluate their own tickets before buying. Completes the "advisor" UX loop.

💼 **Business:** "Check my lottery ticket" is a search query. High monetization potential in the app layer. This feature alone could be the reason someone stars the repo.

**Status:** 🆕 New — no `lottery check` command exists
**Effort:** Small–Medium (1–2 days)
**Priority:** ⭐⭐⭐⭐⭐ HIGHEST

---

### Idea 12 — Hot Pairs / Co-occurrence Strategy (`copairs`)

**Source:** Implicit in Howard's correlation work — numbers that tend to appear together more than chance would predict.

**The concept:**
A co-occurrence matrix across all historical draws, surfaced as:
1. A chart in `lottery analyze` (top 20 hot pairs)
2. A new strategy `copairs` that scores numbers by co-occurrence with recently hot numbers

**Three-expert review:**

🔬 **Algorithm:** O(n²) over all draws — fine for typical histories. The `correlation.py` module **already exists** in the engine but is never called by any strategy or CLI command.

🎯 **Product:** "Numbers that like each other" is intuitive and educational. Great app layer visualization.

💼 **Business:** `correlation.py` is already written — exposing it closes an existing gap with near-zero additional code.

**Status:** 🟡 Partial — `correlation.py` exists, no strategy uses it
**Effort:** Small (< 1 day to wire up the existing module)
**Priority:** ⭐⭐⭐⭐

---

## Ideas to Deprioritize

| Idea | Why Skip / Delay |
|---|---|
| Full wheel catalogs (replicating all 328 systems) | Howard's competitive moat; better to build the *algorithm* than replicate her data |
| Multilingual support (Lotto Loteria in Spanish) | Good long-term, premature now |
| "Strategies for Attracting Good Luck" (mystical content) | Already covered by the Fun tier |

---

## Recommended Additions to Sprint Plan

### Quick Wins (Sprint 2 or 3 additions — small effort, high value)
- **Idea 2** — `--pool` flag
- **Idea 3** — `--key` flag
- **Idea 6** — last digit frequency + filter
- **Idea 8** — expose 70% sum band explicitly
- **Idea 12** — wire up `correlation.py` as hot-pairs strategy

### Medium Features (Sprint 4 or own sprint)
- **Idea 7** — `--filters` system (all hard structural filters)
- **Idea 5** — `group_balance` strategy (decade analysis)
- **Idea 11** — `lottery check` ticket evaluator
- **Idea 4** — `lottery analyze` comprehensive chart report

### Major Features (Sprint 6+)
- **Idea 1** — Lottery Wheeling Module (`lottery wheel`)
- **Idea 10** — Extended game registry (100+ games)

---

## Implementation Priority Matrix

| Priority | Idea | Effort | User Value | OSS Value |
|---|---|---|---|---|
| 🔴 P1 | Idea 11 — `lottery check` evaluator | Small | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🔴 P1 | Idea 1 — Wheeling module | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🔴 P1 | Idea 4 — `lottery analyze` charts | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🟠 P2 | Idea 7 — Hard structural filters | Small | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🟠 P2 | Idea 12 — Hot pairs / correlation | Small | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 🟠 P2 | Idea 2 — `--pool` flag | Tiny | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 🟡 P3 | Idea 5 — Decade/group balance | Small | ⭐⭐⭐ | ⭐⭐⭐ |
| 🟡 P3 | Idea 6 — Last digit frequency | Tiny | ⭐⭐⭐ | ⭐⭐ |
| 🟡 P3 | Idea 3 — `--key` flag | Tiny | ⭐⭐⭐ | ⭐⭐ |
| 🟡 P3 | Idea 8 — Expose 70% sum band | Tiny | ⭐⭐⭐ | ⭐⭐ |
| 🔵 P4 | Idea 10 — Game registry (100+) | Large | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🔵 P4 | Idea 9 — Birthday bias | Tiny | ⭐⭐ | ⭐⭐ |

---

*Analysis date: 2026-04-25 | Source: smartluck.com (Gail Howard) | Engine version: Sprint 1+2 build*
