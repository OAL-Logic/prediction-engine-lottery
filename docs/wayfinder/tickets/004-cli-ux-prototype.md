---
id: "004"
type: prototype
status: open
blocked_by: ["001", "003"]
map: strategy-pruning-meta-selection-map.md
created: 2026-07-11
---

# CLI UX prototype

## Question

What is the exact command-line interface for selecting and consuming a strategy roster, and what does the output look like?

## Context

This ticket depends on:
- [#001 Roster data model](001-roster-data-model.md) for where the roster lives.
- [#003 Policy thresholds](003-policy-thresholds.md) for what the command computes and reports.

The user has decided the trigger is a manual CLI command and the forecast integration is opt-in.

## What to prototype

1. **Selection command**:
   - Command name (`select-strategies`, `prune-roster`, `update-roster`, etc.)
   - Arguments and options (lottery, strategy group to consider, metric, dry-run, force)
   - Default behavior when run without flags
2. **Forecast integration**:
   - Opt-in flag name (`--use-selected`, `--roster`, etc.)
   - Behavior when the roster is missing or stale
   - Interaction with `--strategies`
3. **Output format**:
   - Terminal table: active vs. excluded strategies with reason
   - `--export-md` format consistent with other commands
   - Exit codes (success, empty roster, error)
4. **Examples**: show at least two example invocations and their expected output.

## Acceptance criteria

- [ ] A markdown UX proposal with command signatures and sample output exists.
- [ ] The proposal is consistent with the roster data model from #001.
- [ ] The proposal reflects the policy from #003.
- [ ] No working code is required, but concrete command/output examples are.
