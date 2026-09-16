# MDR-003: Strategy Selection Policy Thresholds

* **Status**: Accepted (Implemented)
* **Date**: 2026-09-16
* **Author**: Claude (Claude Code)
* **Decides**: The exact rules `lottery select-strategies` uses to promote, demote, and runtime-exclude strategies from a game's active roster.

---

## 1. Context

Blocked on [#002 Selection inputs survey](../tickets/002-selection-inputs-survey.md), which identified `data/calibration_cache.json` lift as the primary, most-ready signal, with strategy tier as a secondary guard. This ticket turns that survey into concrete, defensible numbers.

Unlike #001/#002, this ticket was carried through to a working implementation (`engine/modules/strategy_roster.py`, `lottery select-strategies`) rather than stopping at a design-only record — see "Scope note" at the bottom of the map for why.

## 2. Primary metric

**Decision: calibration lift, on the same 1.0-baseline scale `lottery calibrate` already uses** (1.0 = same as random; `calibrate.py`'s own help text: "Lift > 1.0 = above random").

Not ROI or precision, even though both are in the calibration cache: lift is the metric `calibrate.py` already treats as the headline number (its summary panel leads with lift), it is dimensionless across games with different ticket prices/payout tables, and it is the one both `select-strategies` and a human staring at `lottery calibrate`'s own output are already looking at — using a second metric here would mean the two commands could disagree about the same strategy for no visible reason.

A strategy with **no calibration entry** is evaluated live via `engine.modules.pruning.run_pruning_audit()`. That function's `lift_over_random` is a **different, 0-baseline** convention (`(actual − baseline) / baseline`, 0.0 = random). `select-strategies` converts it with `lift = 1.0 + lift_over_random` before doing anything else with it, so every entry in a roster — regardless of which signal produced it — sits on one axis and one threshold. This conversion, and which source produced each number, is recorded per-strategy (`source: "calibration" | "pruning"`) so the roster stays auditable.

## 3. Thresholds

| Threshold | Default | Rationale |
|---|---|---|
| `min_lift` (`--min-lift`) | **1.0** | Must beat random to be worth including at all. This is the strictest defensible floor — anything looser would let the roster include strategies indistinguishable from noise, defeating the point of the feature. Operators who want a stricter bar (e.g. 1.05) can pass `--min-lift` explicitly; `select-strategies` prints the effective threshold in its summary panel every run so this is never silent. |
| `window` / min sample (`--limit`/`-L`) | **20 draws** | Applies only to the live pruning-audit fallback. Reuses the sample-size floor already established elsewhere in this codebase (`esoteric_significance()` in `engine/cli/utils.py` uses the same `>= 20` rule for "enough matching draws to trust a test"), rather than inventing a second convention. Calibration-cache entries are **not** re-gated on sample size here — the user already chose their own window when they ran `lottery calibrate`, and second-guessing that window inside the selector would just create two silently-conflicting opinions about the same number. |
| Roster size | **No fixed count** | Threshold-based, not top-N or percentile: every strategy that clears `min_lift` is active. A fixed count would either arbitrarily exclude a strategy that legitimately beats random, or arbitrarily pad the roster with one that doesn't. Cost/latency control belongs to tier handling (below) and `--exclude`, not to a magic roster-size number. |

## 4. Tier handling

**Decision: one pool, not per-tier floors — with tier used only as a dependency/cost *label*, never as a diversity quota.**

Ticket #002's own framing for why tier matters was cost/compatibility ("to prevent high runtime latencies or system incompatibilities"), not representation. Forcing a weak `deep`-tier strategy to stay active just to guarantee "at least one deep strategy" would contradict the entire premise of evidence-based selection. So:

- Every candidate is checked for basic load-ability (`get_strategy(name)`) before any scoring; a strategy whose class can't even be instantiated is excluded immediately with `reason="failed to load (...)"`, tier attached for context.
- A strategy whose class loads but whose optional dependency fails at evaluation time (e.g. a `deep`-tier strategy without `torch` installed — the dependency is imported lazily inside `.suggest()`, not at construction) is excluded with a reason naming the tier and pointing at `lottery prune <game> --strategies <name>` to see the underlying error directly.
- No tier gets a guaranteed minimum seat. A user who wants deliberate diversity (e.g. "keep at least one `fun`-tier strategy regardless of lift") uses `--pin` — an explicit, visible override — rather than an implicit quota baked into the default policy.

## 5. New / untested strategies

**Decision: evaluate live, don't guess.**

A candidate with no calibration-cache entry is never silently included (would violate "evidence-based") or silently excluded forever (unfair to a genuinely new, genuinely good strategy — and every strategy is "new" until someone runs `calibrate`). Instead `select-strategies` runs `run_pruning_audit()` on it over the last `window` draws on the spot, so a first-time `select-strategies` run with no calibration cache at all still produces a real, evidence-based roster rather than an empty one. Two failure modes are told apart explicitly rather than collapsed into one generic reason:

- **Genuinely insufficient history** (`len(df) < window + 10`, mirroring `run_pruning_audit`'s own guard): `"insufficient history to evaluate (need more than N draws)"`.
- **Evaluation raised** (missing optional dependency, or any other runtime error): `"live audit failed to run (likely a missing optional dependency for the '<tier>' tier, or a transient error) — run 'lottery prune <game> --strategies <name>' directly to see the underlying error"`.

(Earlier in implementation these two were collapsed into one message, which mislabeled a missing-dependency failure as a history problem — caught and fixed during testing on this branch; see failure_scenario note in the test suite.)

## 6. Transparency

**Decision: the same report, three places.**

- **Terminal**: a Rich table — Strategy | Tier | Lift | Source | Status | Reason — sorted active-first, then by lift descending, plus a summary panel with active/excluded counts and the effective policy id + threshold.
- **Persisted roster** (`data/strategy_roster.json`): `active_strategies` is a plain name list (no reason needed — it's active); `exclusions` is a dict keyed by name with `{reason, metrics}` for every excluded or unevaluated strategy. `policy_id` (`"calibration-lift-threshold-v1"`) is stored on every write so a future policy change is itself visible in the file's history.
- **`--export-md`**: the same table, Markdown, appended to a file — consistent with every other report-producing command in this CLI (`forecast`, `prune`, `calibrate`, …).

## 7. Overrides

**Decision: `--pin` and `--exclude`, comma-separated names, exclude wins on conflict.**

- `--pin a,b` forces `a` and `b` active regardless of their computed lift (or even if they failed to load/evaluate) — the roster will simply list them; if a pinned strategy can't actually load at forecast time, `forecast`/`rank-numbers` already skip it with a warning per MDR-001 §4, so this can't crash a downstream run.
- `--exclude a,b` forces `a` and `b` excluded regardless of lift, with `reason="excluded by user (--exclude)"`.
- If the same name appears in both, **exclude wins** — it's the more deliberate, harder-to-undo-by-accident signal, and a deterministic tie-break beats a silent one.
- Both are recorded with their real reason string, never silently folded into the computed result, so a saved roster fully explains itself without needing the command that produced it.

## 8. Edge cases (acceptance criterion)

| Case | Behavior |
|---|---|
| No calibration cache exists at all | Every candidate falls through to the live pruning-audit path. First run is slower but still produces a real roster. |
| Every candidate ends up below `min_lift` | `active_strategies` is `[]`. `select-strategies` still saves this (a roster that says "nothing here beats random right now" is itself a valid, useful result) and prints `Active: 0`. Per MDR-001 §4, `resolve_strategies()` treats an empty `active_strategies` list as "no active roster" and falls back to the `default` preset with a warning — so a downstream `--strategies roster` run never silently executes zero strategies. |
| A named candidate doesn't exist in `STRATEGY_REGISTRY` at all (typo) | `get_strategy()` raises `KeyError`, caught by the same load-guard as a missing dependency; excluded with `reason="failed to load (KeyError: ...)"`. |
| `--pin`/`--exclude` name a strategy outside the evaluated candidate pool | Still appended to the roster (as pinned-active or excluded) — evaluating a strategy the operator didn't ask to consider would be surprising, but silently dropping an explicit override would be worse. |

## 9. Relationship to `lottery prune`

`lottery prune` remains a separate, on-demand diagnostic (prints Jaccard redundancy, hibernation flags, no persistence). `select-strategies` doesn't replace it — it *consumes* the same underlying audit function for the specific job of producing a persisted, forecast-consumable roster. They can disagree in edge cases (different default windows/thresholds) by design; `prune`'s threshold is an "is this worth keeping around at all" question (default 2% lift), while `select-strategies`'s is "should today's ensemble use it" (default: must beat random, i.e. 0% lift on the same delta scale). Both are printed with their policy/threshold on every run, so neither is a black box.

## Resolution

Resolved 2026-09-16. Implemented in `engine/modules/strategy_roster.py` (policy) and `engine/cli/commands/select_strategies.py` (`lottery select-strategies`), consumed via `resolve_strategies()` in `engine/cli/utils.py` from both `forecast` and `rank-numbers`. See [#004 CLI UX prototype](../tickets/004-cli-ux-prototype.md) for the command surface this policy is exposed through.
