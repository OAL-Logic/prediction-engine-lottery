---
id: "001"
type: research
status: closed
assignee: antigravity
blocked_by: []
map: strategy-pruning-meta-selection-map.md
created: 2026-07-11
---

# Roster data model

## Question

What is the persistent representation of a per-game strategy roster, where does it live on disk, and how does `lottery forecast` discover and consume it without breaking existing presets or explicit `--strategies` lists?

## Context

- `engine.strategies.STRATEGY_PRESETS` is global and in-memory; there is no per-game active list today.
- `data/calibration_cache.json` stores lifts per game, but it is overwritten per run and not a roster.
- `lottery forecast` accepts `--strategies default|fast|statistical|esoteric|<comma-list>`; we need an opt-in mechanism to use a persisted roster instead.
- The user has decided that "retirement" means runtime exclusion only: strategies must remain available when named explicitly.

## What to research

1. Compare candidate storage locations and formats:
   - `data/strategy_rosters.json` (analogous to `calibration_cache.json`)
   - `data/model_cache/<game>/roster.json`
   - A new table in `data/lottery.db`
   - A YAML file under `data/` or game-specific inspection directory
2. Define the schema: game id, list of active strategy names, version/timestamp, policy identifier, excluded strategies with reason, optional regime placeholder (future-proof but unused).
3. Decide how `forecast` consumes it:
   - New flag name (`--use-selected`, `--roster`, `--selected`, etc.)
   - Interaction with `--strategies` (does the flag override, complement, or conflict?)
   - Behavior when roster file is missing or empty
   - Behavior when a rostered strategy fails to load
4. Check how existing presets are resolved in `engine.cli.commands.forecast` and `engine.cli.commands.rank_numbers` so the roster can plug in at the same seam.

## Acceptance criteria

- [x] A recommended file path and schema are documented.
- [x] A note explains how the roster relates to `STRATEGY_PRESETS` and explicit `--strategies`.
- [x] Migration/rollback story is described (how a user abandons a roster).
- [x] No code is required; output is a markdown decision record linked from this ticket.

## Resolution

Resolved on 2026-08-11. See [MDR-001: Roster Data Model Design](../decisions/001-roster-data-model-decision.md) for full design and details.

### Key Decisions
- **Storage Location**: `data/strategy_roster.json`
- **CLI Integration**: Accessed via `--strategies roster` on both `forecast` and `rank-numbers`.
- **Fallback Policy**: Falls back to the `default` preset group if the roster is missing or contains no active strategies for the game.
- **Error Handling**: Missing/unresolved strategies inside a roster are skipped with a warning; if all strategies fail, execution aborts with exit code 1.
- **Seams**: Encapsulate strategy resolution logic in a unified `resolve_strategies()` utility function inside `engine/cli/utils.py`.
