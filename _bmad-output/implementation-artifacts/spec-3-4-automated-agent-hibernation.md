---
title: 'Story 3.4: Automated Agent Hibernation'
type: 'feature'
created: '2026-11-08'
status: done
baseline_revision: '1f6e1077545aded5c4b4fa4c6803bf1b8f33e433'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: []
deferred:
  - summary: >-
      No producer calls SwarmCluster.record_lifts, so no agent accumulates a 50-draw window in the running engine.
    evidence: |-
      Nothing in engine/ builds per-agent RewardSignals from out-of-sample draws; same gap as the 3.2 reward producer and DW-3. Hibernation is implemented and tested with synthetic signals only.
    location: >-
      engine/swarm/cluster.py record_lifts
    severity: medium
  - summary: >-
      The default hibernation ledger is a plain JSONL file (data/forensic_ledger.jsonl); Story 4.1's Forensic Ledger does not exist yet.
    evidence: |-
      Story 4.1 should adopt or wrap JsonlLedger and its agent_hibernated event shape so hibernation events land in the real immutable ledger.
    location: >-
      engine/swarm/hibernation.py JsonlLedger
    severity: low
---

<intent-contract>

## Intent

**Problem:** Every swarm agent runs every round regardless of quality, so noisy or underperforming agents dilute consensus. Nothing measures per-agent "Lift over Random" or removes bad agents, and no ledger records such decisions.

**Approach:** Add a `HibernationMonitor` that keeps a rolling 50-draw window of per-agent lift, hibernates an agent whose full-window mean lift falls below a threshold, and appends the event with its rationale to an append-only ledger sink. `SwarmCluster` feeds it lift observations and skips hibernated agents in rounds.

## Boundaries & Constraints

**Always:** Lift follows the `RewardSignal` convention (0.0 = random baseline, positive = better). Window is the last 50 observations per agent; an agent is judged only once its window is full. Hibernate when `mean(window) < threshold` (default threshold 0.0, constructor-configurable). Non-finite or non-numeric lifts are ignored. Each hibernation is logged exactly once, with `agent_id`, `window`, `mean_lift`, `threshold`, `observations`, ISO timestamp and a human-readable `rationale`. Ledger is append-only (JSONL, one event per line); the sink is injectable and a ledger write failure must not prevent hibernation. Hibernated agents are not run in rounds and are excluded from the active count; the agent object stays alive so state is kept.

**Never:** No wake/un-hibernate flow, no Forensic Ledger UI, no Epic 4 ledger schema (Story 4.1 will adopt this sink), no DuckDB/Qdrant, no frontend, Go gateway or MANIFOLD_STATE protocol changes, no new dependencies. No writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Underperformer | 50 lifts of -0.1 for agent 7 | Agent 7 hibernated on the 50th record; one ledger line with mean_lift -0.1 and rationale | — |
| Partial window | 49 lifts of -0.5 | Not hibernated | — |
| Good agent | 50 lifts of +0.2 | Stays active; no ledger line | — |
| Rolling window | 40 lifts of -0.1 then 60 of +0.3, judged on every record | Only the last 50 count; once the window is full the mean is evaluated on those; old values evicted | — |
| Already hibernated | More records for a hibernated agent | No second event | — |
| Invalid lift | NaN, inf, None, bool, "x" | Ignored, window unchanged | No exception |
| Ledger failure | Sink raises on write | Agent still hibernated; failure pulsed at WARN | No exception |
| Round with hibernation | 5 agents, 2 hibernated | `run_round` returns 3 envelopes; `health()` shows 3 active, 2 hibernated | — |

</intent-contract>

## Code Map

- `engine/swarm/agent.py` -- `ExpertAgent.agent_id`; local agents expose it, Ray handles do not.
- `engine/swarm/cluster.py` -- `SwarmCluster`: `_agents` list (local objects or Ray handles), `_spawn`, `scale_to` (pops the tail), `run_round` (gathers every agent), `health()`, `_pulse` helper. Track agent ids in a list parallel to `_agents`.
- `engine/swarm/manifold.py` -- `RewardSignal(lift, preference, agent_id)` and `_valid_lift`; reuse the lift convention and the validation idea.
- `engine/swarm/__init__.py` -- export the new public names.
- `engine/_paths.py` -- `PROJECT_ROOT` for the default ledger path `data/forensic_ledger.jsonl`.
- `tests/test_swarm_cluster.py`, `tests/test_swarm_manifold.py` -- pytest style (`pytest.mark.asyncio`, `FailingSidecar`, `_cluster()` helper); existing assertions on `health()["active_agents"]` must still hold.

## Tasks & Acceptance

**Execution:**
- `engine/swarm/hibernation.py` -- `JsonlLedger` (append-only sink with `append(event)`), `HibernationMonitor` (`record`, `record_signals`, `is_hibernated`, `hibernated_ids`, window/threshold config) -- AC 3.4.1, 3.4.2
- `engine/swarm/cluster.py` -- optional `hibernation` constructor arg (default monitor with the default ledger); `record_lifts(signals)` using `RewardSignal.agent_id`; `run_round` skips hibernated agents; `health()` adds `hibernated_agents` and reports active as non-hibernated; pulse each hibernation -- AC 3.4.1
- `engine/swarm/__init__.py` -- export `HibernationMonitor`, `JsonlLedger`
- `tests/test_swarm_hibernation.py` -- cover every I/O matrix row, using a tmp_path ledger, plus a cluster round test

**Acceptance Criteria:**
- Given a rolling 50-draw window, when an agent's mean lift is below the threshold, then it is hibernated and excluded from subsequent rounds.
- Given a hibernation, then exactly one ledger line records the event and its rationale.
- Given no hibernation, then existing swarm behaviour and tests are unchanged.

## Spec Change Log

## Review Triage Log

### 2026-11-08 — Review pass
- verdicts: 25 findings — high 0, medium 2, low 20, false 1, maybe-false 0 (the intent-alignment layer is descriptive; its divergences restate rows below)
- findings:
  - `[low]` `[patch]` Blind: agent id taken from `_next_id` before `_spawn` is order-fragile — scale_to now spawns first, then appends agent and id
  - `[low]` `[reject]` Blind: no wake path — spec Never excludes it
  - `[low]` `[reject]` Blind: all agents can hibernate — by design at threshold 0.0; a floor adds policy the spec did not ask for
  - `[low]` `[reject]` Blind: state not persisted across restart — agent ids and seeds restart per session, so replaying old ids would hibernate the wrong agents
  - `[low]` `[reject]` Blind: ledger fsync, rotation, blocking write — negligible for rare events
  - `[low]` `[reject]` Blind: record_signals swallows errors, invalid lifts uncounted — negligible
  - `[medium]` `[patch]` Blind: missing tests for Ray path, scale alignment — two tests added (grouped with gap findings)
  - `[low]` `[reject]` Blind: import order, duplicated `_pulse` helper, `active_agents` meaning change — cosmetic; the new meaning is the spec's
  - `[medium]` `[patch]` Edge: `_spawn` raising leaves `_agent_ids` longer than `_agents` — same fix as the first row
  - `[low]` `[reject]` Edge: scale-down pops the tail even if hibernated — ids never reused; capacity effect negligible
  - `[low]` `[reject]` Edge: unknown agent ids get windows — callers are internal
  - `[low]` `[reject]` Edge: unhashable agent_id in record() — RewardSignal ids are ints and record_signals guards
  - `[low]` `[reject]` Edge: concurrent record() calls — cluster calls it synchronously
  - `[low]` `[reject]` Edge: sum overflow on huge finite lifts — unreachable with real lifts
  - `[false]` `[reject]` Edge: restart forgets hibernation and duplicates event — refuted above: ids do not carry across sessions
  - `[low]` `[reject]` Edge: no fsync across processes — single-process writer, lock held
  - `[low]` `[reject]` Edge: default monitor writes the real ledger path — that is the intended production path; no existing test hibernates
  - `[low]` `[reject]` Edge: direct monitor use skips the WARN pulse — pulse is a convenience of record_lifts
  - `[low]` `[reject]` Edge: failed ledger write not retried — spec says failure must not block hibernation
  - `[medium]` `[patch]` Gap: Ray path never exercised with a hibernated agent — test_ray_path_skips_hibernated added
  - `[medium]` `[patch]` Gap: scale-down/up alignment untested — test_scale_down_up_keeps_ids_aligned added
  - `[medium]` `[defer]` Gap: nothing feeds lift into record_lifts in engine/ — producer gap spans the epic; recorded in deferred
  - `[low]` `[reject]` Gap: swarm-health CLI does not show hibernated_agents — outside spec scope, row stays accurate
  - `[low]` `[reject]` Gap: spawn-raises alignment — duplicate of the patched finding
  - `[low]` `[reject]` Gap: default ledger path unexercised — same as the edge row above

## Design Notes

Ledger line example:
`{"event":"agent_hibernated","agent_id":7,"window":50,"observations":50,"mean_lift":-0.1,"threshold":0.0,"timestamp":"2026-11-08T12:00:00+00:00","rationale":"mean lift over last 50 draws -0.1000 < threshold 0.0000"}`

The Forensic Ledger of Story 4.1 does not exist yet, so this story defines the minimal sink and its event shape; 4.1 can wrap or replace the sink. A plain mean against a configurable threshold keeps "statistical threshold" deterministic and testable.

## Verification

**Commands:**
- `python -m pytest tests/test_swarm_hibernation.py tests/test_swarm_cluster.py tests/test_swarm_manifold.py -q` -- expected: all pass

## Auto Run Result

Status: done

**Summary:** Added `HibernationMonitor` with a rolling 50-draw per-agent lift window. An agent whose full-window mean lift is below the threshold (default 0.0) is hibernated, and the event with its rationale is appended to an append-only JSONL ledger. `SwarmCluster` takes lift observations via `record_lifts`, skips hibernated agents in rounds (local and Ray) and reports `hibernated_agents` in `health()`.

**Files changed:**
- `engine/swarm/hibernation.py` -- `JsonlLedger`, `HibernationMonitor`
- `engine/swarm/cluster.py` -- hibernation wiring, id tracking, round filtering, health fields
- `engine/swarm/__init__.py` -- exports
- `tests/test_swarm_hibernation.py` -- matrix rows, cluster round, scale alignment, Ray path

**Review:** 4 patched entries (0 high, 2 medium groups), 1 deferred group plus 1 deferred note, remainder rejected with reasons in the triage log.

**Follow-up review recommended:** false

**Verification:** `python3 -m pytest tests/test_swarm_hibernation.py tests/test_swarm_cluster.py tests/test_swarm_manifold.py tests/test_fringe_swarm.py -q` -- 44 passed. The Ray path was tested only with a fake `ray` module.

**Residual risks:** No producer feeds per-agent lift in the running engine; the ledger is a plain JSONL file until Story 4.1 provides the real Forensic Ledger. No human-only actions are owed, so the status is `done`, not `awaiting-operator`.
