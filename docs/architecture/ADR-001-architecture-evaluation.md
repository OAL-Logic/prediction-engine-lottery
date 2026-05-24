# ADR-001: Architecture Evaluation — Lottery Prediction Engine

**Status:** Active Review  
**Date:** 2026-04-30  
**Deciders:** Operator D  
**Scope:** Full system — engine, API, gateway, frontend, strategy architecture, data layer

---

## Context

This document is a deep architectural evaluation of the Lottery Prediction Engine as it stands on 2026-04-30. The system is a solo-built, early-prototype Python engine for lottery analysis and ticket suggestion. It supports Brazilian lotteries (Mega-Sena, Lotofácil) and US Powerball, with a growing library of prediction strategies across statistical, ML, deep learning, and "fun" tiers.

The evaluation is based on a full read of the source: `engine/`, `gateway/`, `app/`, `data/registry.yaml`, `pyproject.toml`, and supporting docs.

---

## System Map (What Is Actually Built)

```
┌──────────────────────────────────────────────────────────┐
│    React Native / Expo (app/)       ← very early stage   │
│    Deployed bundle: app/dist/       ← web export exists   │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP (future)
                       ▼
┌──────────────────────────────────────────────────────────┐
│    Go Gateway  (gateway/main.go)    port :8080            │
│    chi router · API key auth · rate limit 100/min/IP      │
│    In-memory GET cache (10s TTL)                          │
└──────────────────────┬───────────────────────────────────┘
                       │ reverse proxy → :8000
                       ▼
┌──────────────────────────────────────────────────────────┐
│    FastAPI Sidecar  (engine/api/main.py)                  │
│    /games  /analysis  /suggest  /backtest  /check         │
│    /strategies                                            │
└──────────────────────┬───────────────────────────────────┘
                       │ direct Python import
                       ▼
┌──────────────────────────────────────────────────────────┐
│    Python Engine                                          │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Adapters   │  │  Strategies  │  │  Modules        │  │
│  │  registry   │  │  registry    │  │  frequency      │  │
│  │  caixa_base │  │  BaseStrategy│  │  deviation      │  │
│  │  mega_sena  │  │  statistical/│  │  correlation    │  │
│  │  lotofacil  │  │  ml/         │  │  patterns       │  │
│  │  powerball  │  │  deep/       │  │  filters        │  │
│  └──────┬──────┘  │  fun/        │  │  sum_range      │  │
│         │         └──────────────┘  │  geometry       │  │
│         ▼                           └─────────────────┘  │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Data layer: JSON file cache + model_cache/*.pt    │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                       │ also exposed as
                       ▼
┌──────────────────────────────────────────────────────────┐
│    Typer CLI  (engine/cli/main.py)                        │
│    lottery fetch · analyze · suggest · backtest           │
│    wizard · strategies · docs                             │
└──────────────────────────────────────────────────────────┘
```

---

## Architecture Assessment

### 1. Strategy Layer — Strong ✅

**Pattern:** Classic Strategy + Registry with a decorator-based auto-registration.

```python
# Every strategy self-registers at import time:
@register
class BayesianStrategy(BaseStrategy):
    name = "bayesian"
    tier = "statistical"
    
    def score(self, df, rules) -> dict[int, float]: ...
```

`BaseStrategy` provides a rich `suggest()` implementation for free — temperature-based sampling, K-of-N filter application, pool constraints, key number injection, seeded RNG, and even the cosmic-ray muon bit-flip easter egg. Subclasses only override `score()`.

**Trigger registration** happens via bare imports in `api/main.py`:
```python
import engine.strategies.statistical  # side-effect: fills _REGISTRY
import engine.strategies.fun
```
This is a common Python pattern and works, but it is fragile — if a new tier (e.g., `deep/`) is added without a matching import here, those strategies silently disappear from the API while remaining available in the CLI.

**Assumptions:**
- The CLI imports `_REGISTRY` indirectly through `get_strategy()` calls, so it sees all registered strategies at runtime without needing explicit trigger imports.
- `get_strategy(name, **kwargs)` uses `inspect.signature` to do surgical kwarg injection, avoiding `TypeError` on strategies with no custom `__init__`. This is well-designed.
- ~40+ strategies across 4 tiers. Deep strategies cache `.pt` model files to `data/model_cache/` with a deterministic hash-keyed filename (model type + lottery + draw count + data hash + hyperparams). This is a homegrown but effective pattern for avoiding re-training on unchanged data.

**Risk:** No `__init_subclass__` or plugin discovery — adding a new strategy file requires manually editing the `__init__.py` barrel or trigger-import. Easy to forget.

---

### 2. Adapter Layer — Well Designed ✅

**Pattern:** ABC with a concrete `CaixaBaseAdapter` providing a 3-tier data cascade:

```
1. Community bulk mirror (Heroku) — fast, complete history, unreliable (Heroku sleep)
2. Caixa incremental API — official, authoritative, per-draw fetching
3. Local JSON cache — offline fallback, survives network outages
```

The incremental fetch uses `concurrent.futures.ThreadPoolExecutor(max_workers=10)` to parallelize per-draw HTTP requests — a practical choice for I/O-bound network calls. Given the Caixa API endpoints are per-draw, this cuts fetch time ~10× vs. sequential.

The cache merge logic deduplicates by draw ID using a dict keyed by concurso, which is correct but verbose. The multi-key normalization (`row.get("draw_id") or row.get("numero") or row.get("numeroConcurso") or row.get("concurso")`) handles format drift between the community mirror and official API — defensive but messy. This chain should be extracted to a `_normalize_draw_id(row)` helper.

**Assumption:** `load_data()` (called by the API) reads from the JSON cache file directly — it does **not** trigger a live fetch. The frontend/API must explicitly `POST /games/{name}/fetch` to refresh data. This is correct behavior but not documented in the API spec.

---

### 3. Lottery Registry — Simple and Correct ✅ (with one edge case)

`LotteryRegistry` is a singleton backed by `data/registry.yaml`. `GameDefinition` dataclasses map to `DrawRules` on demand via `.to_rules()`. The registry supports both full IDs (`br/mega-sena`) and short aliases (`mega-sena`).

**Assumption:** The alias lookup is registered at load time by slicing `id.split("/")[-1]`. Collision risk if two lotteries from different countries share the same short name (e.g., a hypothetical `eu/mega-sena`). Currently not a problem but worth noting as the registry expands.

`data_available: false` entries (`us/mega-millions`, `eu/euro-millions`) are placeholders for Sprint 2.4. The adapter field is absent, so any attempt to `get_adapter("mega-millions")` will fail with a `KeyError` — not a graceful 404.

---

### 4. Filter / Harmony System — Sophisticated but Overloaded ⚠️

`is_harmonious()` is a 200+ line method on `BaseStrategy` that evaluates up to 22 named structural filters:

```
sum_range · parity · breadth · no_consecutive · no_arithmetic
birthday_bias · no_calendar_cluster · no_same_last_digit
repeat_rate · parity_balance · high_low_balance · sum_harmonic
prime_count · ac_value · unit_sum · successive_groups · root_sum
hot_cold · no_historical_dupes · no_multiples_cluster
mixed_parity_digits · digit_space_123 · successive_end_units
pos_1_low · pos_last_high
```

The method supports `filters=None` (no checks), `filters=["balanced"]` (sum + parity + breadth), and `filters=["all"]` (full set). K-of-N fault tolerance allows a ticket to pass if it satisfies at least K of the active checks rather than all of them.

**Issues:**
- The entire filter set is inlined as a single method. It should be a `FilterRegistry` of callable validators, each independently testable. The current approach makes it nearly impossible to unit-test individual filters in isolation.
- `"balanced"` expands to 3 filters inside the method via string manipulation — this implicit expansion is a footgun.
- The `filters=None` vs `filters=[]` behavior is identical (pass-through) but the docstring says "default to balanced" — the code contradicts this. The actual default for the `suggest()` signature is `filters=None`, which means **no filters by default**, not balanced. This is a silent behavior change from prior versions (pre-v9.0).
- `from engine.modules import filters as f_mod` is imported inside the method body — not a problem functionally but indicates this code grew organically.

---

### 5. FastAPI Layer — Functional but Has Stubs ⚠️

The API is clean and idiomatic FastAPI. Routes follow REST conventions. Pydantic models in `api/models.py` provide request/response validation.

**Known stubs and issues:**

**a) Backtest endpoint is incomplete:**
```python
@app.post("/games/{name}/backtest")
async def backtest_strategy(name: str, request: BacktestRequest):
    from engine.cli.main import _run_backtest_internal  # ← doesn't exist as exported symbol
    ...
    return {"message": "Backtest started", "game": name, "strategy": request.strategy}
```
This endpoint always returns a placeholder. The backtest logic lives in the CLI (`engine/cli/main.py`) but has not been refactored into a shared service layer. The import `_run_backtest_internal` will fail at runtime if actually called.

**b) Ensemble strategy is a no-op:**
```python
strat_names = [s.strip() for s in request.strategy.split(",")]
if len(strat_names) > 1:
    pass  # TODO comment
strat = get_strategy(strat_names[0], **kwargs)  # only uses first
```
Multi-strategy ensemble (supported in the CLI) silently degrades to single-strategy in the API.

**c) Background task fetch has no status feedback:**
`POST /games/{name}/fetch` dispatches to `background_tasks.add_task(adapter.fetch_data)` but there is no polling endpoint or WebSocket to report progress. A slow fetch (200 draws × HTTP calls) completes silently with no observable state change until the caller hits `/analysis` again.

**d) No authentication on `check` and `strategies` endpoints** (only guarded by the Go gateway's API key). If the Python sidecar port `:8000` is ever exposed directly, these are open.

---

### 6. Go Gateway — Correct but Minimal ⚠️

The gateway is a well-structured chi-based reverse proxy with three middlewares:
- Request ID, Real IP, Logger, Recoverer (standard chi stack)
- `httprate.LimitByIP(100, 1*time.Minute)`
- `CacheMiddleware(10 * time.Second)` — **in-memory only**

**Issues:**
- The in-memory cache does not survive restarts, won't work behind multiple gateway replicas, and could grow unbounded without an eviction policy. For a solo-deployed product this is fine now, but it should be swapped for Redis-backed caching before any load testing.
- A single static `API_KEY` environment variable authenticates all requests. There's no per-user token, no JWT, no expiry. Fine for a private beta but not for a public SaaS.
- The `AuthMiddleware` correctly returns 401 on missing/wrong key, but the response format is not checked — it may return plain text while the sidecar returns JSON, creating inconsistent error shapes to clients.

---

### 7. Data Layer — No Database, by Design ✅ (with caveats)

The entire persistent state is:
- `data/*.json` — historical draw data per lottery (flat file cache)
- `data/model_cache/*.pt` / `.joblib` — trained ML/deep model files
- `data/registry.yaml` — lottery metadata

This is the right call for a solo developer at early prototype stage. The absence of a database eliminates ops overhead, and historical draw data is append-only and small (Mega-Sena has ~202 draws in cache, Lotofácil ~3,672).

**Assumptions:**
- Concurrent writes are not handled. If two API requests trigger `fetch_data` simultaneously, both will write to the same JSON cache file. Python's GIL partially protects here but `json.dumps` + `write_text` is not atomic.
- The model cache filenames encode draw count in the hash: `cnn_1d_mega-sena_202_...`. Fetching 1 new draw technically invalidates all cached models for that lottery. Consider separating model invalidation from draw count.

---

### 8. Frontend (React Native / Expo) — Early Stage 🔜

`app/` contains a bare Expo project with `App.tsx` and a pre-built web export at `app/dist/`. The mobile app is not yet wired to the API. The web export exists (`dist/index.html`) suggesting a web deployment was attempted. No routing, no API calls, no UI components are in the source yet beyond the Expo default template.

**Assessment:** The frontend is a placeholder. The primary interface today is the CLI, with the API as a secondary delivery mechanism. This is appropriate prioritization for an early prototype.

---

## Structural Patterns Summary

| Pattern | Where Used | Quality |
|---|---|---|
| Strategy + Registry (decorator) | `engine/strategies/` | Excellent |
| Abstract Base Class | `BaseStrategy`, `LotteryAdapter`, `CaixaBaseAdapter` | Excellent |
| Singleton | `LotteryRegistry` | Good |
| Template Method | `CaixaBaseAdapter._load_live_or_cache()` | Good |
| Reverse Proxy + Gateway | Go `main.go` | Good |
| Parallel I/O | `ThreadPoolExecutor` in fetch | Good |
| Seeded randomness | `random.Random(seed)` per suggestion | Good |
| Side-effect registration | `import engine.strategies.*` in API | Fragile |
| God method | `is_harmonious()` | Needs refactor |
| Incomplete stub | `POST /backtest` | Must fix before launch |

---

## Risks by Priority

### 🔴 High — Fix Before Public Launch

**R1: Backtest API is a dead stub.**  
`_run_backtest_internal` does not exist as an exported symbol. A user hitting `POST /games/{name}/backtest` will either get a 500 or a misleading success message. The backtest logic in the CLI must be extracted to `engine/services/backtest.py` and called from both the CLI and API routes.

**R2: Ensemble strategy silently drops to single strategy in API.**  
A user who passes `strategy=markov,bayesian` via the API gets only `markov` results with no indication the second strategy was ignored. Either implement the ensemble in the API or return a 400 with a clear error message until it is supported.

**R3: No user model — single API key for all.**  
The current auth model can't distinguish between users, can't rate-limit per user, and can't support paid tiers. The key needs to be rotated or replaced with per-user JWT tokens before any monetization attempt. Supabase Auth (already planned in the design doc) would handle this.

### 🟡 Medium — Fix Before Beta

**R4: Strategy trigger-import is implicit and fragile.**  
Deep learning strategies (`engine/strategies/deep/`) are not trigger-imported in `api/main.py`. Requesting a deep strategy via the API (`strategy=transformer`) will raise `KeyError: unknown strategy 'transformer'`. Add `import engine.strategies.deep` with an appropriate try/except for the optional `torch` dependency, or implement an `__init_subclass__` auto-discovery pattern.

**R5: `is_harmonious()` is untestable in isolation.**  
The 22 filter checks are inlined in one method with no seams. Any change to one filter risks silently breaking others. This should be refactored into a `FilterRegistry` before the filter system is exposed in user-facing UI.

**R6: Model invalidation on every fetch.**  
Every new draw fetch technically invalidates all model caches (draw count changes the hash). For the deep learning models (which take minutes to re-train), this is a usability problem. The cache key should use the data hash (already in the filename) rather than draw count.

**R7: Concurrent fetch race condition.**  
Two simultaneous calls to `fetch_data` will both write the JSON cache file. Add a file lock (`threading.Lock` keyed by cache filename) around cache writes.

### 🟢 Low — Nice to Have

**R8: `adaptive_window` sweep in `suggest()` is a no-op.**  
The implementation tests three window sizes but never actually computes precision — it just sets `best_limit = len(df)` for every iteration, defaulting to full history always. Either implement the evaluation or remove the sweep.

**R9: `_last_muon_strike` instance mutation is a bad pattern.**  
The muon bit-flip easter egg sets `self._last_muon_strike = True` on the strategy instance. Strategy instances are freshly instantiated per API call today, so it's not a real bug, but if strategies were ever cached as singletons it would cause request cross-contamination. Use the `metadata` dict on `SuggestionResult` to pass this flag instead.

**R10: Registry alias collision risk.**  
Adding `eu/mega-sena` would shadow the alias `mega-sena` for `br/mega-sena`. The alias registration in `LotteryRegistry._load()` uses a first-write-wins policy silently. Add a warning log if an alias collision is detected.

---

## What Is Working Really Well

**The `score()` / `suggest()` split is the best design decision in the codebase.** It gives 40+ strategy authors a simple, well-defined contract: "tell me how likely each number is, and I'll handle the rest." Temperature-based sampling, structural filters, key numbers, pool constraints, seeded RNG — none of that complexity bleeds into individual strategy implementations. New strategies are ~50 lines each.

**The 3-tier data cascade is robust for the use case.** Community mirror for bulk history, incremental Caixa fetch for recency, local JSON for offline resilience. This is resilient to third-party API downtime without adding infrastructure.

**The YAML-backed registry is the right call at this scale.** Adding a new lottery is a 12-line YAML entry. No migrations, no admin UI needed.

**The Go gateway is appropriately thin.** Auth, rate limiting, caching — it does exactly what a gateway should do and nothing more. Python handles all business logic.

---

## Recommended Action Plan

Ordered by impact-to-effort for a solo developer:

1. **[1 day] Extract backtest service layer.** Create `engine/services/backtest.py`, move the CLI backtest logic there, call it from both the CLI and `POST /backtest` API route.

2. **[2 hours] Fix API trigger-import for deep strategies.** Add `import engine.strategies.deep` with a graceful fallback when `torch` is not installed.

3. **[1 day] Introduce Supabase Auth.** Replace the single API key with per-user JWT tokens. Required before any public beta.

4. **[0.5 days] Fix model cache key.** Replace draw count with data hash in the cache filename key so new draws don't trigger full re-training.

5. **[1 day] Refactor `is_harmonious()` into a FilterRegistry.** Extract each named check into its own function with a `@filter_registry.register("sum_range")` decorator. This unblocks independent unit testing and makes the filter list self-documenting.

6. **[2 hours] Add file lock around JSON cache writes.** Use `threading.Lock` keyed by cache filename to prevent concurrent write corruption.

7. **[0.5 days] Connect the Expo frontend to the API.** Wire `/games`, `/suggest`, and `/analysis` endpoints to React Native screens. The backend is ready; the frontend is waiting.

---

## Consequences

**What becomes easier after these fixes:**
- Adding new strategies remains a 1-file, 50-line operation
- The filter system becomes independently testable and extensible
- The API becomes feature-equivalent to the CLI
- A public beta is safe to launch

**What remains hard:**
- No user management means A/B testing strategies per user is impossible until auth is added
- File-based data storage won't scale past ~10K concurrent requests (but this is far ahead of current needs)
- The `fun/` strategy tier (noosphere, ley lines, kabbalistic, reincarnation) will require careful UX framing if exposed publicly — users should clearly understand these are entertainment, not predictions

**What to revisit at 1,000 users:**
- Replace in-memory Go cache with Redis
- Move draw data to PostgreSQL (keep JSON as seed)
- Add WebSocket support for real-time fetch progress
- Consider strategy result caching (same strategy + same data = deterministic output at temperature=0)
