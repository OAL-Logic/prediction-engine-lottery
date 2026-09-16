---
label: wayfinder:map
destination: Strategy pruning and meta-selection system
status: shipped
created: 2026-07-11
updated: 2026-09-16
---

# Strategy Pruning & Meta-Selection Map

## Destination

A decision-ready design for a **per-game strategy roster** system: a manual CLI command (`lottery select-strategies`) that runtime-excludes poorly performing strategies from a game's active forecast roster using calibrated out-of-sample evidence and a documented policy. The roster is persisted and consumed by an opt-in forecast flag. Regime-aware selection is recognized as a follow-on effort, not part of this map.

## Notes

- **Domain**: Lottery Engine strategy lifecycle — registration (`engine.strategies`), calibration (`lottery calibrate`), pruning (`lottery prune` / `engine.modules.pruning`), tuning (`lottery tune`), and ensemble forecast (`lottery forecast`).
- **Skills to consult**: `bmad-domain-modeling` for policy vocabulary; `bmad-grilling` for threshold trade-offs; `lottery-backtest` for empirical validation questions.
- **Standing preferences from 2026-07-11**:
  - "Retirement" = runtime exclusion only (strategies remain available by explicit name).
  - Selection starts as global per game; regime-aware is future fog.
  - Trigger is a manual CLI command, not an automatic daemon.
- **Map scope**: this effort stops at a spec/design that can be handed off for implementation. It does not build the feature in place unless a later ticket explicitly overrides that.

## Decisions so far

<!-- Index of closed tickets. One line per ticket: gist + link. -->

- [#001 Roster data model](tickets/001-roster-data-model.md) — Roster stored in central `data/strategy_roster.json` and consumed via `--strategies roster` with a default-preset fallback.
- [#002 Selection inputs survey](tickets/002-selection-inputs-survey.md) — Identified out-of-sample calibration lift as primary signal and tier metadata as secondary, detailing 4 key gaps.
- [#003 Policy thresholds](tickets/003-policy-thresholds.md) — Calibration lift (1.0-baseline) as primary metric with a live pruning-audit fallback for uncalibrated strategies; `min_lift=1.0`, `window=20` (fallback path only); one pool, no per-tier quota; `--pin`/`--exclude` overrides, exclude wins on conflict.
- [#004 CLI UX prototype](tickets/004-cli-ux-prototype.md) — `lottery select-strategies <game>`, roster consumed via the existing `--strategies roster` value on `forecast`/`rank-numbers` (no new flag).

## Tickets (frontier)

None open — #003 and #004 are closed. This map's original destination (a decision-ready design) is reached; see "Scope note" below for why it was then also implemented.

## Scope note: design carried through to implementation

This map's own text originally said: *"this effort stops at a spec/design that can be handed off for implementation... It does not build the feature in place unless a later ticket explicitly overrides that."* #003 and #004 are recorded as that override: both were resolved directly against a working implementation rather than a plan for one, because the session's goal was explicitly to ship modular engine features, not just design them, and the design was already unambiguous enough (thanks to #001/#002) to implement without further back-and-forth. Shipped as:

- `engine/modules/strategy_roster.py` — policy (`compute_roster`, `load_roster`, `save_roster`).
- `engine/cli/commands/select_strategies.py` + `lottery select-strategies` in `engine/cli/main.py`.
- `resolve_strategies()` in `engine/cli/utils.py` — the unified seam from MDR-001 §5, consumed by both `forecast.py` and `rank_numbers.py`.
- Tests: `tests/test_strategy_roster.py`.
- Bugfix found via this work: `load_local_config()` was leaking arbitrary keys from unrelated `*.local.yaml` files (e.g. a `report`-pipeline template's `name`/`steps`) into `get_strategy(**personal_data)` calls, crashing `forecast`/`suggest`/`tune` for every strategy whenever such a file was present. Narrowed to only extract the two keys it actually documents (`full_name`, `birth_date`) — see `engine/cli/utils.py` docstring and CHANGELOG.

## Not yet specified

Fog that is in scope but not sharp enough to ticket yet:

- **Regime-aware selection.** The `compare-draws` command already detects STABLE / DRIFT / SHIFT via JS divergence. Whether the roster should differ per regime is deferred until the global selector is designed.
- **Ensemble interactions.** How `select-strategies` relates to ensemble strategies (`voting`, `synapse`, `stacking`) that themselves bundle members. Does the selector prune ensemble members or top-level strategies?
- **Historical calibration cache.** Current `calibration_cache.json` is overwritten per run. Whether to keep time-series calibration history is fog until #002 surveys the inputs.
- **Auto-calibration trigger.** Whether `select-strategies` should invoke `calibrate` automatically or require a fresh cache is a UX/policy question tied to #003.
- **Per-tier vs. pooled selection.** Whether the selector treats all strategies as one pool or enforces minimum representation per tier (statistical / ML / deep / fun).

## Out of scope

- Hard deletion or deprecation of strategy files/entries.
- Background daemon or automatic periodic re-selection.
- Mobile / desktop UI surfaces.
- Changing the default behavior of `lottery forecast`; this design is opt-in only.
- Building the implementation itself (this map produces a spec).
