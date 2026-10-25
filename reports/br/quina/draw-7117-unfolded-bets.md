# Quina — Unfolded (Desdobrada) Multi-Number Bet Analysis & Optimization Architecture

**Target:** Quina concurso 7117, single unfolded ticket (6–15 numbers), played as a registered Caixa syndicate (bolão).
**Baseline invariant:** every 5-number combination from the 1–80 board has an identical theoretical draw probability of **1 in C(80,5) = 24,040,016**. Nothing in this document changes that fact. What follows filters a *candidate pool* against empirical macro-structural distributions and prices the payout structure of unfolded bets — it does not alter the odds of any individual 5-number line.

> **Data-freshness note.** This repo's cached Quina history (`data/inspections/br_quina/`, DuckDB `data/lottery.db`) currently runs through **draw 7076** (2026-07-27). Draw 7117 is ~41 draws ahead of the cache. All empirical figures below are computed from real history through 7076; before playing 7117, refresh with `python -m engine.cli.main fetch quina` (hits the Caixa API / community mirror) and re-run the pipeline in §3 — it will pick up the true prior draw and target id automatically.

---

## 1. Financial & Combinatorial Baseline

### 1.1 What "unfolded" (desdobrada) actually buys you

An N-number unfolded Quina ticket is **literally the set of all C(N,5) five-number sub-combinations** of your N chosen numbers. Caixa doesn't sell you "one ticket with a multiplier" — it sells you C(N,5) independent base-bet lines, priced accordingly:

```
cost(N) = C(N, 5) × R$ 2.50
```

This is exact and already implemented in this codebase (`DrawRules.calculate_bet_cost`, `engine/adapters/__init__.py:53`) — the only change made here was registering Quina's `max_picks = 15` (it previously allowed only the base 5-number bet; see `engine/adapters/br/quina.py`, mirroring the existing `mega_sena.py` / `lotofacil.py` convention).

### 1.2 Multiplier & cost matrix (N = 6…15)

| N  | Combinations C(N,5) | Cost multiplier vs. single bet | Cost (BRL) |
|----|---------------------|---------------------------------|------------|
| 5  | 1                   | 1×                              | R$ 2.50    |
| 6  | 6                   | 6×                              | R$ 15.00   |
| 7  | 21                  | 21×                             | R$ 52.50   |
| 8  | 56                  | 56×                             | R$ 140.00  |
| 9  | 126                 | 126×                            | R$ 315.00  |
| **10** | **252**         | **252×**                        | **R$ 630.00**  |
| 11 | 462                 | 462×                             | R$ 1,155.00 |
| 12 | 792                 | 792×                             | R$ 1,980.00 |
| 13 | 1,287               | 1,287×                           | R$ 3,217.50 |
| 14 | 2,002               | 2,002×                           | R$ 5,005.00 |
| **15** | **3,003**       | **3,003×**                      | **R$ 7,507.50** |

(`engine.modules.quina_financial.multiplier_matrix()` — computed, not looked up.)

### 1.3 Prize-tier line count — exact combinatorics, not an estimate

Every one of a ticket's C(N,5) lines scores **exactly** one tier based on `hits` (how many of the 5 officially-drawn numbers fall inside your N-number pool):

```
lines_at_tier(N, hits, tier) = C(hits, tier) × C(N − hits, 5 − tier)
```

This is the key structural difference from playing fragmented standard bets: **if your ticket has enough hits, you win multiple tiers simultaneously across different lines** (a single base 5-number bet can only ever land in one tier). Worked example, `hits = 4` (4 of the 5 drawn numbers are inside your pool):

| N  | Quina (5) lines | Quadra (4) lines | Terno (3) lines | Duque (2) lines |
|----|------------------|-------------------|-------------------|-------------------|
| 10 | 0                | 6                 | 60                | 120               |
| 12 | 0                | 8                 | 112               | 336               |
| 15 | 0                | 11                | 220               | 990               |

At `hits = 5` (jackpot inside your pool) a 10-number ticket simultaneously wins **1 Quina + 25 Quadra + 100 Terno + 100 Duque** lines; a 15-number ticket wins **1 + 50 + 450 + 1,200**. This multi-tier stacking — not a better jackpot probability — is the actual payoff structure an unfolded ticket buys.

### 1.4 Odds — hypergeometric, exact (not simulated)

**Baseline: standard single 5-number bet** (exact tier, matches Caixa's published figures):

| Tier   | Matches | 1 in X         |
|--------|---------|----------------|
| Quina  | 5/5     | 24,040,016.0   |
| Quadra | 4/5     | 64,106.7       |
| Terno  | 3/5     | 866.3          |
| Duque  | 2/5     | 35.6           |

**10-number and 15-number unfolded tickets** — probability of winning **at least** that tier somewhere in the ticket (`engine.modules.quina_financial.odds_table`, hypergeometric over 80-ball/5-drawn):

| Tier   | N=10 (1 in X) | N=12 (1 in X) | N=15 (1 in X) |
|--------|---------------|---------------|---------------|
| Quina  | 95,396.9      | 30,353.6      | 8,005.3       |
| Quadra | 1,607.8       | 697.8         | 262.1         |
| Terno  | 78.9          | 44.9          | 23.2          |
| Duque  | 8.7           | 6.3           | 4.3           |

Note the jackpot odds *do* improve with N (95,396.9 → 8,005.3 for the "at least 5 of my N are the winners" event at N=15) — this is expected: you're covering 3,003 lines instead of 1, at proportionally higher cost. It is **not** a distortion of the fixed-line 1-in-24,040,016 fact; it's the standard C(N,5)/C(80,5) coverage effect of buying more lines. The jackpot odds of *any single one* of those 3,003 lines remain 1-in-24,040,016 each.

### 1.5 Capital efficiency: unfolded ticket vs. fragmented standard bets

At equal budget, an N-number unfolded ticket and N-choose-5 independent fragmented single bets cost **identically** (`cost(N) = C(N,5) × R$2.50` either way) and cover the **same number of lines** — so raw jackpot EV is identical. The real trade-off is **correlation, not expected value**:

- **Unfolded ticket (this pipeline's output):** all C(N,5) lines share your N numbers. Outcomes are highly correlated — if 4 of your N numbers are drawn, you win *many* lines across 3 tiers at once (§1.3). If only 0–1 of your N numbers are drawn, you win *nothing at all*, across every line. High variance, "all-or-nothing" payout shape.
- **Fragmented bets (same budget, unrelated number sets):** C(N,5) independent lines drawn from disjoint or overlapping-but-uncorrelated pools. Outcomes decorrelate — you're far more likely to win *something small* on *some* ticket, and far less likely to sweep multiple tiers at once. Lower variance, smoother payout shape.

For a **syndicate**, the unfolded structure is usually preferred precisely *because* of this correlation: it produces fewer, larger, easier-to-split prize events (a Quadra hit pays out to the whole syndicate as one multi-line event) rather than many scattered R$3.50 Duque hits across unrelated tickets that are administratively annoying to reconcile among cotistas.

### 1.6 Syndicate (bolão) allocation guidelines

Caixa itself does not run bolões directly — they are organized informally or via a **registered lottery retailer (casa lotérica)** acting as the ticket-of-record holder. Because the exact minimum/maximum cota count and per-share cost ceiling are set by the retailer's own terms (and can change), treat the following as **standard market practice**, to be confirmed with the specific retailer registering ticket 7117, not as a fixed Caixa rule:

| Parameter | Typical practice |
|---|---|
| Minimum cotas | 2 |
| Typical cota range for a R$630–7,507.50 ticket | 10–100+, sized so each cota lands in a "round" price bracket (e.g. R$10, R$20, R$50) |
| Cost per cota | `ticket_cost(N) / n_cotas`, rounded up; retailer typically keeps the rounding remainder as an admin fee |
| Split threshold | Retailers commonly cap cotas at whatever count keeps `cost/cota` above a legibility floor (rarely below R$5–10) to avoid disputes over sub-R$1 shares on small prizes |
| Documentation | A registered bolão needs a written participant list + signed terms at purchase — required for any of the participants to legally claim a shared prize later |

Example at N=10 (R$630.00 total): 21 cotas at R$30/cota, or 63 cotas at R$10/cota, are both common round-number splits; confirm with the retailer before the draw, not after.

---

## 2. Statistical Feature Extraction & Heuristic Envelopes

Every bound below is computed from this repo's **actual 7,076-draw Quina history** (1994–2026-07-27), not textbook defaults, via `engine.quina_unfold.FeatureExtractor` and `engine.modules.{frequency,skips,sum_range}`.

### 2.1 Parity (odd/even)

Empirical odd-count distribution per draw (5 numbers, out of 80 where 40 are odd / 40 even):

| Odd count | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Frequency | 2.8% | 15.5% | **32.6%** | **31.4%** | 14.8% | 2.9% |

2–3 odd numbers (the "2:5–3:5" band) covers **64.0%** of all real draws — confirming the standard heuristic empirically rather than by assumption. **Filter used:** for an N-number pool, require the odd fraction to fall in **[0.40, 0.60]** (the same 2:5–3:5 band, scale-invariant).

### 2.2 Sum band

Analytical model (`engine.modules.sum_range`, k=5, N=80): `E[S] = 5·81/2 = 202.5`, `σ ≈ 50.0`. **Empirical mean over 7,076 real draws: 201.95** — the analytical model and reality agree to within 0.3%, so the same closed-form is safe to scale to any N via `pick_count=N` (validated in `engine/quina_unfold/filters.py::sum_rule`). Empirical 70%-coverage band: **149–256** (analytical: ~152–253 for k=5) — used directly, scaled proportionally to N by re-deriving `mean = N·81/2`, `σ = √(N·81·(80−N)/12)` for the pool size actually being built.

### 2.3 Decile / quadrant spread

80 numbers → 10 deciles of 8 numbers, or 4 quadrants of 20 numbers. Empirical quadrant coverage per real draw:

| Quadrants touched | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Frequency | 0.3% | 15.9% | **57.5%** | **26.4%** |

83.9% of real draws touch **3 or 4** quadrants — single- or double-quadrant concentration is rare (16.2% combined). **Filter used:** no decile/quadrant may hold more than its proportionate share (`round(N/10)` / `round(N/4)`) plus a small slack (+1 decile, +2 quadrant, to avoid over-constraining small N), and all 4 quadrants must be represented.

### 2.4 Prior-draw telemetry (dynamic — recomputed against the true 7117 prior draw at runtime)

- **Repeat filter:** fraction of the pool that repeats a number from the immediate prior draw ≤ 40%.
- **Adjacency filter:** fraction of the pool within ±1 of a prior-draw number ≤ 30%.

Both are evaluated live against `DrawRepository.get_prior_draw()` — for this report's snapshot (prior = draw 7076: `1, 18, 22, 35, 41`), the generated pool has **0 repeats and 0 adjacents** (§3), well inside both caps.

### 2.5 Frequency & cycles (rolling z-score, skip/delay classification)

Each number gets a frequency z-score (`engine.modules.frequency.analyze`, chi-squared-validated against the uniform null) and a delay ratio (`now_skip / average_skip`, via `engine.modules.skips.compute_skip_profile`):

- **hot**: `z ≥ +0.5`
- **cold**: `z ≤ −0.5`
- **overdue**: `delay_ratio ≥ 1.3` (currently on a longer gap than its own historical average — overrides hot/cold)
- **warm**: everything else

**Filter used:** at least 30% of the pool must be hot-or-overdue (the pool isn't allowed to be 100% inert "warm" numbers). Framed as data, not prediction — a truly fair lottery makes every draw independent; "overdue" is an observation about the historical record, not a claim about the next draw (same disclaimer already present in `engine/modules/deviation.py`).

---

## 3. Candidate Pool Generation — draw 7117 (snapshot on cached data through 7076)

Ran end-to-end via the pipeline in §4:

```python
repo = DrawRepository()
df = repo.load_history(source="cache")          # swap to source="auto" once cache is refreshed to 7117
prior = repo.get_prior_draw()
features = FeatureExtractor(repo.rules).compute(df, prior_draw=prior.numbers)
pipeline = FilterPipeline.default_envelope()
pool = PoolOptimizer(repo.rules, features, pipeline, pool_size=10).optimize()
```

### 3.1 Generated 10-number pool

**`04 · 10 · 26 · 31 · 37 · 44 · 45 · 49 · 52 · 62`** — cost R$630.00 (252 lines), backend: local-search (OR-Tools CP-SAT not installed in this environment; falls back automatically — see §4.1).

| Number | Historical count | Freq z-score | Now-skip | Avg skip | Delay ratio | Cycle | Decile | Quadrant |
|---|---|---|---|---|---|---|---|---|
| 04 | 507 | +3.10 | 1  | 13.0 | 0.08 | hot     | 1 | 1 |
| 10 | 459 | +0.80 | 33 | 14.3 | 2.30 | overdue | 2 | 1 |
| 26 | 492 | +2.38 | 18 | 13.4 | 1.35 | overdue | 4 | 2 |
| 31 | 476 | +1.62 | 6  | 13.8 | 0.43 | hot     | 4 | 2 |
| 37 | 458 | +0.75 | 30 | 14.4 | 2.08 | overdue | 5 | 2 |
| 44 | 482 | +1.90 | 27 | 13.6 | 1.98 | overdue | 6 | 3 |
| 45 | 443 | +0.04 | 65 | 14.9 | 4.37 | overdue | 6 | 3 |
| 49 | 482 | +1.90 | 15 | 13.7 | 1.10 | hot     | 7 | 3 |
| 52 | 488 | +2.19 | 36 | 13.4 | 2.68 | overdue | 7 | 3 |
| 62 | 434 | −0.39 | 57 | 15.2 | 3.75 | overdue | 8 | 4 |

### 3.2 Compliance against every structural envelope

| Envelope | Threshold | Pool result | Status |
|---|---|---|---|
| Parity | odd fraction ∈ [0.40, 0.60] | 4/10 odd = 0.40 | ✅ pass |
| Sum band | 334–476 (70% band, scaled to N=10) | 360 | ✅ pass |
| Decile spread | ≤2 per decile | max 2, 7/10 deciles occupied | ✅ pass |
| Quadrant spread | ≤4 per quadrant, all 4 touched | max 4, 4/4 touched | ✅ pass |
| Prior repeat rate | ≤40% | 0/10 (0%) | ✅ pass |
| Prior adjacency | ≤30% | 0/10 (0%) | ✅ pass |
| Cycle mix | ≥30% hot/overdue | 10/10 (100%) | ✅ pass |

All 7 rules pass simultaneously — `FilterReport.passed == True`.

### 3.3 Omission rationale (highest-scoring numbers excluded, i.e. the closest misses)

| Number | Composite score | Why excluded |
|---|---|---|
| 51 | 1.27 | Decile 7 already at its proportionate cap (49 and 52 already fill it) |
| 66 | 1.05 | Lower composite score than the 10 selected peers (rank 11/80) |
| 53 | 0.96 | Decile 7 already at its proportionate cap |
| 54 | 0.95 | Decile 7 already at its proportionate cap |
| 72 | 0.93 | Lower composite score than selected peers (rank 14/80) |
| 16 | 0.90 | Decile 2 already at its proportionate cap |

Every one of the remaining 70 excluded numbers has a machine-generated rationale attached (`PoolResult.omission_rationale`) — either it fails a structural cap already satisfied by a selected peer, it's cold/low-frequency, or it simply ranks below the cutoff on composite score. Full detail is reproducible by re-running §4's code.

### 3.4 12-number pool (for comparison)

**`04 · 10 · 26 · 31 · 37 · 44 · 45 · 49 · 52 · 62 · 66 · 75`** — R$1,980.00 (792 lines) — also passes all 7 rules (odd 5/12=0.42, sum 501 in band 409–563, decile max 2/cap 2, quadrant max 4/cap 5, 0 repeats, 0 adjacents, hot/overdue 11/12=92%).

---

## 4. Python Prediction Engine Architecture

### 4.1 Method comparison (runtime complexity vs. combinatorial optimality)

| Method | Optimality | Complexity for N≈10–15 pool from 80 | Verdict for this use case |
|---|---|---|---|
| **Vectorized brute-force (NumPy/Polars)** | Exact if pool space is enumerated | C(80,10) ≈ 1.6×10¹² — infeasible to fully enumerate; feasible only if pre-filtered to a shortlist (e.g. top-25 candidates by score → C(25,10) ≈ 3.3M, tractable) | Good as a *scoring/filtering* substrate (used throughout `FeatureExtractor`/`FilterPipeline` here), not as the search strategy itself at full scale |
| **Constraint Programming (OR-Tools CP-SAT)** | Exact optimum given linear/boolean constraints | Sub-second for this problem size (80 booleans, ~15 linear constraints) | **Best fit** — implemented as the primary backend in `PoolOptimizer._solve_cp_sat`; falls back automatically since `ortools` isn't installed in this environment (`pip install ortools` to activate it) |
| **MIP (PuLP)** | Exact, same class as CP-SAT | Comparable; CP-SAT's native boolean/AllDifferent modeling is a more natural fit for parity/decile-count constraints than PuLP's LP-oriented API | Redundant once CP-SAT is available; not implemented separately |
| **Genetic Algorithms (DEAP/PyGAD)** | Near-optimal, no guarantee | Overkill at this scale (80-bit search space, ~15 constraints) — GA shines when the objective/constraint surface is non-convex or too large to model exactly; that's not the case here | Not needed; the exact/greedy pair above already covers the space cheaply |
| **Simulated Annealing** | Near-optimal, no guarantee | This is effectively what the no-dependency fallback (`PoolOptimizer._solve_local_search`) implements — targeted swap hill-climbing driven directly by which FilterPipeline rule is failing, rather than blind random perturbation | **Implemented** as the zero-dependency fallback; converges in the 12-13 test run above without ever needing more than a few hundred iterations |
| **Markov chain state transitions** | N/A (descriptive, not optimizing) | Useful for *sequence*-dependent games; Quina draws are i.i.d. (same chi-squared-fairness assumption `sum_range.py` already documents) so a Markov model over "number states" adds complexity without a mechanism to add real signal | Not applicable to pool filtering; would belong in a separate strategy module (`engine/strategies/statistical/markov.py` already exists for single-ticket generation) |
| **Monte Carlo simulation** | Approximates exact odds | Every odds figure in §1.4 is available in closed form (hypergeometric) — Monte Carlo would only add sampling noise | Not needed; used exact combinatorics instead (`engine.modules.quina_financial`) |
| **Tree-based scoring (LightGBM)** | Learns from labeled outcomes | Already a dependency in this repo (`engine/strategies/ml/`) for single-ticket ranking; requires a supervised target (e.g., "did this number appear next draw") which is exactly the kind of pattern a fair lottery doesn't reliably contain — useful as one more *score* input, not as a pool-selection mechanism on its own | Out of scope for this deliverable; the composite score in `PoolOptimizer` is a natural place to blend in an ML-derived score later without changing the FilterPipeline/optimizer contract |

**Bottom line:** CP-SAT (exact, when installed) with a deterministic local-search fallback (zero extra dependency, same objective/constraints) gives exact-when-possible / good-enough-always behavior without forcing a new hard dependency onto the repo. Both are implemented behind the same `PoolOptimizer.optimize()` call.

### 4.2 Implementation

New code, all runnable today against this repo's real data:

```
engine/modules/quina_financial.py     — pure functions: cost(N), lines_at_tier(), odds_table(), multiplier_matrix()
engine/quina_unfold/
  ├── __init__.py                     — package exports
  ├── repository.py                   — DrawRepository
  ├── features.py                     — FeatureExtractor, NumberFeatures
  ├── filters.py                      — FilterPipeline, FilterRule, FilterReport
  └── optimizer.py                    — PoolOptimizer, PoolResult
tests/test_quina_unfold.py            — offline tests (financial combinatorics + full pipeline)
data/registry.yaml                    — added max_picks: 15 for br/quina (was single-bet only)
engine/adapters/br/quina.py           — added max_picks=15 to the adapter's hardcoded DrawRules
```

**`DrawRepository`** (`engine/quina_unfold/repository.py`) — wraps the existing `QuinaAdapter`/`storage` singleton (community mirror → Caixa incremental API → DuckDB/JSON cache, unchanged). `load_history(source="auto"|"cache")`, `get_prior_draw()`, `get_target_draw_id()`.

**`FeatureExtractor`** (`engine/quina_unfold/features.py`) — one `NumberFeatures` row per number 1–80: count, frequency, z-score (via `engine.modules.frequency`), skip/delay ratio (via `engine.modules.skips`), decile, quadrant, repeat/adjacency vs. the prior draw, and a hot/warm/cold/overdue `cycle_class`.

**`FilterPipeline`** (`engine/quina_unfold/filters.py`) — ordered `FilterRule`s, each a pure `(pool, features, rules) -> (passed, detail)` predicate. `FilterPipeline.default_envelope(...)` builds the §2 boundary filters with every threshold as an overridable constructor argument — nothing hard-coded inside a rule body.

**`PoolOptimizer`** (`engine/quina_unfold/optimizer.py`) — composite score = `0.4·freq_z + 0.5·min(delay_ratio,3) − 1.2·is_repeat − 0.5·is_adjacent`; `optimize()` tries CP-SAT first (if `ortools` is importable), otherwise runs the greedy-seed + targeted-swap local search. Returns a `PoolResult` with the pool, per-rule `FilterReport`, per-number scores, and a full omission rationale for every excluded number.

All four classes, the financial module, and the tests were executed against this repo's real 7,076-draw cache to produce every number in §1 and §3 above — nothing here is hypothetical output.

---

## Next steps

1. Run `python -m engine.cli.main fetch quina` to catch the cache up to draw 7117's actual immediate-prior draw, then re-run §3's snippet with `source="auto"` for the live pool.
2. If exact CP-SAT optimality is wanted over the local-search heuristic, `pip install ortools` — no code changes needed, `PoolOptimizer` picks it up automatically.
3. Confirm the syndicate's cota split and per-share cost with the registering lottery retailer before purchase (§1.6) — this repo doesn't (and shouldn't) automate that part.
