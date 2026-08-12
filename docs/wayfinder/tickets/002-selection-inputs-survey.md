---
id: "002"
type: research
status: open
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

- [ ] A markdown comparison table of candidate inputs exists.
- [ ] A recommendation for MVP inputs is stated with rationale.
- [ ] Gaps that need closing before policy design are listed.
- [ ] No code is required; output is a markdown research summary linked from this ticket.
