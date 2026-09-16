---
id: "003"
type: grilling
status: closed
assignee: claude-code
blocked_by: ["002"]
map: strategy-pruning-meta-selection-map.md
created: 2026-07-11
---

# Policy thresholds

## Question

What are the exact rules for promoting, demoting, and runtime-excluding strategies from a game's active roster, and how do we keep those rules transparent and defensible?

## Context

The user has decided:
- Runtime exclusion only (strategies remain available by explicit name).
- Global per-game selection first; regime-aware selection is future fog.
- Manual CLI trigger (`lottery select-strategies`).

This ticket is blocked until [#002 Selection inputs survey](002-selection-inputs-survey.md) identifies which signals are available.

## What to decide

1. **Primary metric**: lift, ROI, hit rate, precision, or a composite?
2. **Thresholds**:
   - What lift (if lift is used) demotes a strategy to excluded?
   - Is there a minimum number of test draws before a strategy is eligible?
   - How many strategies remain in the active roster (fixed count, percentile, or absolute threshold)?
3. **Tier handling**: do we select from all strategies as one pool, or enforce minimum representation per tier (statistical / ML / deep / fun)?
4. **New/untested strategies**: how are recently added strategies handled when no calibration exists?
5. **Transparency**: what does the command report so the user understands why each strategy was included or excluded?
6. **Overrides**: can the user pin a strategy always-in or always-out regardless of metrics?

## Acceptance criteria

- [x] A concrete policy is documented in plain language.
- [x] Threshold defaults and their rationale are recorded.
- [x] Edge cases (no calibration, all strategies below threshold, missing strategies) are addressed.
- [x] Output is a markdown policy decision record linked from this ticket.

## Resolution

Resolved 2026-09-16. See [MDR-003: Strategy Selection Policy Thresholds](../decisions/003-policy-thresholds-decision.md) for the full policy.

### Key decisions
- **Primary metric**: calibration lift (1.0-baseline scale, matching `lottery calibrate`), with a live `run_pruning_audit()` fallback (normalized onto the same scale) for strategies with no calibration entry.
- **Thresholds**: `min_lift = 1.0` (must beat random), `window = 20` draws for the live-audit fallback only (calibration-cache entries are trusted as-is). No fixed roster size — threshold-based inclusion.
- **Tier handling**: one pool, no per-tier quota; tier is only used to label dependency/cost-related exclusions. Diversity, if wanted, is opt-in via `--pin`.
- **New/untested strategies**: evaluated live rather than guessed; "insufficient history" and "evaluation raised" are reported as distinct, correctly-labelled reasons.
- **Transparency**: identical report in the terminal table, the persisted `data/strategy_roster.json`, and optional `--export-md`.
- **Overrides**: `--pin` / `--exclude`, comma-separated; exclude wins on conflict.

Unlike #001/#002, this ticket was carried through to a working implementation (not just a design record) — see the map's scope note.
