# MDR-004: `select-strategies` CLI UX

* **Status**: Accepted (Implemented)
* **Date**: 2026-09-16
* **Author**: Claude (Claude Code)
* **Decides**: The command surface for computing and consuming a strategy roster.

---

## 1. Selection command

**Name: `select-strategies`** (not `prune-roster` or `update-roster`) — it reads as "choose the active set," matches the destination map's own working name, and doesn't collide with the already-existing, semantically different `prune` command (which is a diagnostic, not a persistence step).

```
lottery select-strategies <lottery> [OPTIONS]

  -s, --strategies TEXT   Candidate pool to evaluate: 'all', a preset name,
                          or a comma list                        [default: all]
      --min-lift FLOAT    Minimum lift (1.0 = random baseline) to stay active
                                                                   [default: 1.0]
  -L, --limit INT         Backtest window for strategies with no calibration
                          cache entry                             [default: 20]
      --pin TEXT          Comma-separated strategies to force-include
      --exclude TEXT      Comma-separated strategies to force-exclude
      --dry-run           Preview the roster without saving it
      --export-md TEXT    Append the roster report to this .md file
```

**Default behavior with no flags**: evaluates *every* registered strategy (`--strategies all`) — unlike `prune`'s default of just the `default` preset. The entire point of this command is to be the one place that looks across the whole registry, so defaulting to a small preset would defeat its purpose; `--strategies <group>` narrows it for a faster run when that's wanted (`-L`/`--limit` reuses `prune`'s own flag name for the same concept, for muscle-memory consistency).

## 2. Forecast integration

**Opt-in value: the literal string `"roster"` passed to the existing `--strategies` option** on `forecast` and `rank-numbers` — not a new flag. Rationale: `--strategies` already accepts a preset name or a comma list; "roster" is just a third kind of value in that same slot, which is one new concept for the user (not two), and it means every place that already accepts `--strategies` gets roster support for free (this is also why `resolve_strategies()` was pulled into `engine/cli/utils.py` as a shared seam rather than copy-pasted).

- **Missing/stale roster**: `resolve_strategies()` warns to stderr-styled Rich output and transparently falls back to the `default` preset — the run still completes rather than erroring out. Exact behavior specified in MDR-001 §4 and implemented identically for both `forecast` and `rank-numbers`.
- **Interaction with `--strategies`**: no conflict — `roster` occupies the same option `--strategies` already uses, so there's nothing to reconcile. An explicit comma list in the same option always means exactly those strategies, same as before.

## 3. Output format

**Terminal**: Rich table, columns `Strategy | Tier | Lift | Source | Status | Reason`, sorted active-first then by lift descending, plus a summary `Panel` (active/excluded counts, policy id, effective threshold) — this is the same table+panel shape `prune`/`calibrate`/`forecast` already use, so it doesn't introduce a new visual language.

**`--export-md`**: appended Markdown table with the same columns, under a `## Strategy Roster — <game> (<date>)` heading — consistent with `--export-md` everywhere else in this CLI (append-only, human-readable, git-diffable).

**Exit codes**:
- `0` — normal completion, including the "every candidate excluded" case (an empty active roster is still a valid, saved result — see MDR-003 §8).
- `1` — reserved for `get_adapter()`'s existing behavior (unknown/unavailable lottery id) and any uncaught error; `select-strategies` itself doesn't introduce new failure exits, since even a fully-excluded roster is a successful run.

## 4. Examples

```console
$ lottery select-strategies br/lotofacil
# Evaluates all ~96 registered strategies against data/calibration_cache.json,
# live-audits anything uncalibrated, saves data/strategy_roster.json.

$ lottery select-strategies br/lotofacil --strategies fast --dry-run
                         Strategy Roster — br/lotofacil
 Strategy     Tier          Lift  Source   Status      Reason
 monte_carlo  statistical  1.039  pruning  ✓ active
 weighted     statistical  1.011  pruning  ✓ active
 copairs      statistical  1.011  pruning  ✓ active
 bayesian     statistical  0.994  pruning  ✗ excluded  live audit lift 0.994 < min 1.000 (...)
╭──────────────────────────────────────────────────────────────╮
│ Active: 3 · Excluded: 1 · Policy: calibration-lift-threshold-v1 (min lift 1.000) │
╰──────────────────────────────────────────────────────────────╯
--dry-run: roster not saved.

$ lottery forecast br/lotofacil --strategies roster
[dim]Using 3 strategies from the saved roster.[/dim]
... (normal forecast output using only weighted, monte_carlo, copairs)
```

(Both example runs above are real captured output from this implementation, not hypothetical.)

## Resolution

Resolved 2026-09-16, implemented directly (see [#003](003-policy-thresholds-decision.md) resolution note on why this map's tickets were carried through to code). `select-strategies` is registered under `PANEL_SYSTEM` in `engine/cli/main.py`, next to `prune`/`calibrate`/`tune`.
