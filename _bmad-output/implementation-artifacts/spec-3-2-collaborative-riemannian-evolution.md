---
title: 'Story 3.2: Collaborative Riemannian Evolution'
type: 'feature'
created: '2026-11-08'
status: done
baseline_revision: bb445c6d69920649ac9ab66588e1b36bbb27e07e
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** The Story 3.1 swarm samples independently; agents never share reward signals, so the manifold curvature reflects no collective learning, and the 3D Spatial Retina is driven only by static store weights.

**Approach:** Add a shared Riemannian state-vector (unit vector on the positive orthant of S^3, i.e. the sqrt-embedded 4-simplex with Fisher-Rao geometry) that the swarm evolves with geodesic (exp/log map) steps weighted by agent lift, publish each new state as a telemetry pulse, and have the app parse that pulse into the existing `weights` store so the SpatialRetina shader morphs live.

## Boundaries & Constraints

**Always:** State components are `frequency, deviation, cosmic, ml` (same keys as the store `SwarmWeights`); weights = squared components, always summing to 1. Updates use the sphere exp/log maps (never linear averaging then renormalising). Reward signals are out-of-sample per-agent `lift` plus a preference point on the simplex. Evolution is deterministic for identical inputs. Telemetry uses `engine.modules.telemetry.pulse` with message prefix `MANIFOLD_STATE ` + JSON.

**Never:** No weighting UI/ripple (3.3), hibernation (3.4), distillation (3.5). No edits to the Go gateway, `QuantumSidecar`, or the `SpatialRetina` shader. No new dependencies. No writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Collective update | Many signals with positive lift toward point P | State moves along the geodesic toward P; geodesic distance to P strictly decreases; weights sum to 1 | — |
| Negative lift | Signal with lift < 0 | Pushes state away from that agent's preference | — |
| No signals / zero total lift | `[]` or all lift 0 | State unchanged, epoch still advances only if signals applied | No exception |
| Invalid signal | Wrong dimension, negative/NaN preference, non-finite lift | Signal skipped and counted in `rejected` | No exception escapes |
| Antipodal/degenerate | Tangent of zero length | State unchanged | — |
| Telemetry | After a non-empty update | One pulse `MANIFOLD_STATE {"epoch","weights","distance_to_consensus"}` | Pulse failure never breaks evolution |
| App ingest | Telemetry message with the prefix | Store weights set from payload; other messages ignored | Malformed JSON/bad weights ignored |

</intent-contract>

## Code Map

- `engine/swarm/agent.py`, `engine/swarm/cluster.py` -- Story 3.1 agents/cluster; cluster `_pulse` helper reused; rounds return sealed envelopes (unchanged).
- `engine/modules/telemetry.py` -- `pulse(message, level)` UDP fire-and-forget; gateway relays the JSON message to the WebSocket as-is.
- `app/stores/useResonanceStore.ts` -- Zustand store; `weights` already bound to the SpatialRetina uniforms (`uFrequency` etc.), so `setWeights` makes evolution visible.
- `app/components/TelemetryWaterfall.tsx:98` -- `ws.onmessage` where telemetry JSON is ingested.
- `app/utils/__tests__/*.test.ts` -- `bun:test` style for pure utils.
- `tests/test_swarm_cluster.py` -- `pytest.mark.asyncio` style.

## Tasks & Acceptance

**Execution:**
- `engine/swarm/manifold.py` -- `RewardSignal`, `RiemannianState` (`evolve`, `weights`, `distance_to`, `snapshot`), sphere exp/log maps -- AC 3.2.1
- `engine/swarm/cluster.py` -- `SwarmCluster.evolve(signals)` owning one shared state, pulsing `MANIFOLD_STATE` -- AC 3.2.2, 3.2.3
- `engine/swarm/__init__.py` -- export new names
- `app/utils/manifold-telemetry.ts` -- `parseManifoldTelemetry(message)` returning weights or null -- AC 3.2.3
- `app/stores/useResonanceStore.ts` + `app/components/TelemetryWaterfall.tsx` -- apply parsed weights via `setWeights` (plus `manifoldEpoch`) in `onmessage` -- AC 3.2.3
- `tests/test_swarm_manifold.py`, `app/utils/__tests__/manifold-telemetry.test.ts` -- cover every I/O matrix row

**Acceptance Criteria:**
- Given 1,000 agents with signals toward a common point, when evolved over several rounds, then the geodesic distance to that point decreases monotonically and weights sum to 1.
- Given a cluster with signals, when `evolve` runs, then a `MANIFOLD_STATE` pulse with the new weights is emitted.
- Given the app receives that pulse over the telemetry socket, when parsed, then the store weights equal the pulse weights, which the SpatialRetina reads.

## Spec Change Log

## Review Triage Log

### 2026-11-08 — Review pass
- verdicts: 33 findings — high 0, medium 1, low 17, false 4, maybe-false 0 (11 further reviewer items are restatements of the rows below; Verification Gap items arrive pre-verified)
- findings:
  - `[medium]` `[patch]` Pulse-to-store wiring untested (setManifoldState/onmessage) — extracted `applyManifoldMessage` in `app/utils/manifold-telemetry.ts`, used by the component, with bun tests (valid pulse forwarded, other/invalid ignored)
  - `[low]` `[patch]` Missing/invalid epoch coerced to 0 (Blind, Edge) — parser now returns null; test added
  - `[low]` `[reject]` Stale/out-of-order epoch overwrites newer weights (Blind, Edge) — local UDP to WS is ordered in practice; a guard needs a restart-reset path, adding complexity
  - `[low]` `[reject]` Huge finite lifts overflow (Edge) — NaN tangent fails the `> EPS` check, state stays unchanged, nothing corrupted
  - `[low]` `[reject]` Non-iterable `signals` raises TypeError (Edge) — internal caller only; "no exception" applies to invalid signals
  - `[low]` `[reject]` No lock on concurrent evolve (Blind, Edge) — single driver per cluster
  - `[low]` `[reject]` NaN/Infinity in json.dumps (Edge, Gap) — state is finite by construction
  - `[low]` `[reject]` Orthant clamp is a projection, not an exact geodesic for negative lift (Blind, Edge x2) — documented as a numerical guard; matrix behavior ("pushes away") is tested
  - `[low]` `[reject]` `applied` is 0 when the step does not move (Blind, Edge) — documented snapshot semantics
  - `[low]` `[reject]` `distance_to_consensus` not forwarded to the store (Blind, Edge) — unused by the Retina
  - `[low]` `[reject]` Swallowed `_pulse` failure, lost UDP pulses, import order, `initial` semantics, wire-format drift test, extra TS test gaps (Blind, Edge, Gap) — fire-and-forget by design; next evolve resyncs; cosmetic or internal-only
  - `[false]` `[reject]` 1e-6 sum tolerance drops valid pulses — Python weights are normalized, sum error ~1e-15
  - `[false]` `[reject]` `setManifoldState` instead of `setWeights` (Edge) — functionally equivalent, merges weights and epoch atomically
  - `[false]` `[reject]` Store write after unmount (Edge) — `onmessage` returns early when `!isMounted`
  - `[false]` `[reject]` Operator-action reading D (Intent) — no AC requires a human-only external action
  - `[low]` `[reject]` Retina rendering / producer not integrated (Intent) — SpatialRetina already binds store `weights` to shader uniforms (verified in `SpatialRetina.tsx`); a draw-to-reward producer is residual risk, see below

## Auto Run Result

Status: done

**Summary:** Added a shared Riemannian state-vector (unit vector on the positive orthant of S^3) that the swarm evolves with lift-weighted geodesic steps; each update is pulsed as `MANIFOLD_STATE {json}` and the app parses it into the store `weights` that the SpatialRetina shader already reads.

**Files changed:**
- `engine/swarm/manifold.py` -- `RewardSignal`, `RiemannianState`, exp/log maps
- `engine/swarm/cluster.py` -- `SwarmCluster.evolve(signals)` with shared state and pulse
- `engine/swarm/__init__.py` -- exports
- `app/utils/manifold-telemetry.ts` -- pulse parser and `applyManifoldMessage`
- `app/stores/useResonanceStore.ts` -- `manifoldEpoch`, `setManifoldState`
- `app/components/TelemetryWaterfall.tsx` -- applies pulses in `onmessage`
- `tests/test_swarm_manifold.py`, `app/utils/__tests__/manifold-telemetry.test.ts` -- tests

**Review:** 2 patches applied (1 medium, 1 low), 0 deferred, rest rejected with reasons above.

**Follow-up review recommended:** false

**Verification:** `pytest tests/test_swarm_manifold.py tests/test_swarm_cluster.py` 23 passed; `bun test utils/__tests__/manifold-telemetry.test.ts` 6 passed. Store action and component were not type-checked or rendered (`zustand` is not installed in `app/node_modules`).

**Residual risks:** Nothing yet produces `RewardSignal`s from real out-of-sample draws; the API accepts them. Live Retina rendering was not observed.

## Design Notes

Exp/log on S^3: `log_x(p) = θ/sin θ · (p − cos θ · x)`, `θ = arccos(x·p)`; `exp_x(v) = cos|v|·x + sin|v|·v/|v|`. Step: `v = lr · Σ lift_i · log_x(p_i) / Σ|lift_i|`; positive-orthant preferences keep the state in the orthant for `lr ≤ 1`, and components are clipped at 0 and renormalised only as a numerical guard.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_swarm_manifold.py tests/test_swarm_cluster.py -q` -- expected: all pass
- `cd app && bun test utils/__tests__/manifold-telemetry.test.ts` -- expected: all pass
