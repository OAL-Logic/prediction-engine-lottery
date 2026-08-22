---
id: "002"
type: research
status: closed
assignee: antigravity
blocked_by: []
map: strategy-pruning-meta-selection-map.md
created: 2026-07-11
---

# Selection inputs survey

## Question

Which existing signals can and should feed the strategy selector, and what are their strengths, weaknesses, and readiness for runtime-exclusion decisions?

## Context

Several subsystems already compute strategy quality metrics but do not act on them:

- `lottery calibrate` → `data/calibration_cache.json` (out-of-sample lift, profit, ROI, precision)
- `lottery prune` → `engine.modules.pruning.run_pruning_audit()` (lift over random, `is_hibernated`, Jaccard redundancy matrix)
- `lottery tune` → `tuned/<lottery>.yaml` (best params per strategy, stacking meta-learner)
- `lottery forecast` internal diagnostics → stability%, discrimination Δ, composite weight
- Runtime cost is implicit: statistical ≈ ms, ML/deep ≈ seconds–minutes, fun strategies may hit HTTP APIs.

## What to research

1. For each signal above, document:
   - What it measures
   - Whether it is per-game
   - Whether it is already persisted and in what format
   - Computational cost to refresh
   - Whether it supports time-series history or only a snapshot
2. Identify gaps:
   - Is there a per-strategy runtime cost estimate or metadata?
   - Does the redundancy matrix from `prune --redundancy` have a stable output format?
   - How does `tune` output relate to selection (best config vs. best strategy)?
3. Recommend the minimum viable input set for a first selector and what can be deferred.

## Acceptance criteria

- [x] A markdown comparison table of candidate inputs exists.
- [x] A recommendation for MVP inputs is stated with rationale.
- [x] Gaps that need closing before policy design are listed.
- [x] No code is required; output is a markdown research summary linked from this ticket.

## Resolution

Resolved on 2026-08-11. See [Selection Inputs Survey Findings](../decisions/002-selection-inputs-survey-findings.md) for full details.

### Key Findings & Recommendations
- **Primary Selector Input**: Out-of-sample calibration lift (`data/calibration_cache.json`) is the most robust and ready metric for strategy selection.
- **Secondary Input**: Strategy tier (statistical/ML/deep/fun) from `STRATEGY_REGISTRY` to prevent high runtime latencies or system incompatibilities.
- **Critical Gaps to Close**: 
  1. `lottery prune` output is currently stdout-only; need to either run audits dynamically or cache pruning results to a JSON file.
  2. Calibration cache overwrites on each run, meaning historical trend of lift is not captured.
  3. No explicit latency metadata in strategy definitions.
  4. Redundancy Jaccard matrix is printed to console but not saved.
