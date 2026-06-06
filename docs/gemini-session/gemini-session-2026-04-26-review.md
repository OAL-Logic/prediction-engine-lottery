> ℹ️ **STATUS NOTE (2026-04-26)** — The roadmap section at the bottom of
> this file is partially out of date:
>
> - ✅ `lottery backtest` shipped (lines 772–1008 of `engine/cli/main.py`).
>   Now formalized as Sprint 1.2 in `../SPRINT_PLAN.md`.
> - ✅ `lottery optimize` shipped (lines 1009–1175). Also Sprint 1.2.
> - ⚠️ `lottery wizard` and `lottery compare` are referenced in CLI help
>   text and have data structures (`_STRATEGY_EXPLAINERS`,
>   `_STRATEGY_PRESETS`) staged, but neither is registered as
>   `@app.command()`. Decision pending: build them or strip references.
> - ⏳ Deep model caching, data-integrity audit (`lottery check` —
>   different scope than the Howard ticket evaluator), and parallel
>   fetching are still pending.
>
> Authoritative roadmap: `../SPRINT_PLAN.md` at the workspace root.

---

# Gemini CLI Session Review — 2026-04-25

## What Gemini Built

Gemini reviewed the project and implemented two features in `engine/cli/main.py`:

1. **`lottery wizard`** — Interactive step-by-step CLI prompt (lottery, strategy group, ticket count, temperature) that delegates to `compare`.
2. **`lottery compare`** — Runs multiple strategies at once: ticket, score bar chart, plain-English explainer per strategy, CONSENSUS panel, and a LEARN section.

**A bug was introduced** during the session: a duplicate `_print_suggestions` block caused an `IndentationError`. Gemini self-corrected by rewriting the entire file. A second typo (`correlation_mod` → `corr_mod`) was also fixed in the same session.

---

## What Was Already There (Pre-Session)

The existing code (from a prior Claude session) already had all of these features in a _more complete_ form:
- Full `inspect.signature` parameter-introspection in wizard
- `_run_comparison()` helper that accepts strategy objects (not just names)
- `crowd_avoidance` and `steiner_wheel` in the statistical preset
- Dynamic parameter display in compare output

Gemini's version was simpler in all these areas.

---

## Issues Fixed After This Review (2026-04-25)

### 1. Missing `_STRATEGY_EXPLAINERS` entries
Six strategies had no educational content in `compare` output:

| Strategy    | Tier        | Fixed |
|-------------|-------------|-------|
| `momentum`  | statistical | ✅    |
| `spectral`  | statistical | ✅    |
| `streak`    | statistical | ✅    |
| `fibonacci` | fun         | ✅    |
| `zodiac`    | fun         | ✅    |
| `biorhythm` | fun         | ✅    |

### 2. Incomplete `_STRATEGY_PRESETS`
Same six strategies were missing from the `compare --strategies` presets.

```python
# BEFORE
"statistical": ["markov", "bayesian", "monte_carlo", "weighted", "pattern", "crowd_avoidance", "steiner_wheel"],
"fun":         ["numerology", "moon_phase", "weather"],

# AFTER
"statistical": [
    "markov", "bayesian", "monte_carlo", "weighted", "pattern",
    "momentum", "spectral", "streak",
    "crowd_avoidance", "steiner_wheel",
],
"fun": ["numerology", "moon_phase", "weather", "fibonacci", "zodiac", "biorhythm"],
"all": [... all 16 strategies ...]
```

---

## How to Use the Compare Command

```bash
# Run all 10 statistical strategies — tickets + score bars + explanations
lottery compare mega-sena

# Run all 6 fun strategies
lottery compare mega-sena --strategies fun

# Full battery of 16 strategies
lottery compare mega-sena --strategies all

# Custom selection
lottery compare mega-sena --strategies markov,bayesian,momentum,spectral

# 3 tickets per strategy, sharper temperature
lottery compare mega-sena --count 3 --temp 0.5

# Skip the LEARN section
lottery compare mega-sena --no-learn

# Interactive wizard (guided selection + parameter customization)
lottery wizard
```

---

## Pending Improvements (Gemini's Suggestions — Not Yet Built)

### 1. 🔄 Backtesting Engine (`lottery backtest`)
Run a strategy against historical draws and report hit rates (≥N number matches).
The rolling-window infrastructure already exists inside `prob_weighted` — expose it as a CLI command.
**Effort**: Medium.

### 2. 💾 Deep Strategy Model Caching
`transformer`, `lstm_gru`, `cnn_1d` train from scratch each call (~30–60s on CPU).
Cache weights keyed on `(lottery, draw_count, last_draw_hash)` via `torch.save`.
**Effort**: Small.

### 3. 🔍 Data Integrity Audit (`lottery check`)
Validate cached JSON for missing draw IDs, duplicate dates, out-of-range numbers.
**Effort**: Small.

### 4. ⚡ Parallel Fetching
Parallelize the HTTP mirror chain in `caixa_base.py` with `ThreadPoolExecutor`.
**Effort**: Small.

---

## Recommended Priority

1. `lottery backtest` — highest user value
2. Deep model caching — quality-of-life
3. Data integrity check — robustness
4. Parallel fetching — minor speed gain
