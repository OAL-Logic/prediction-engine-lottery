---
title: 'Story 3.3: The Swarm Equalizer (Weighting UI)'
type: 'feature'
created: '2026-11-08'
status: done
baseline_revision: eaa79b7e3732fe1c5d0a178c00cf75eb24cbbc0d
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: []
deferred:
  - summary: >-
      No producer calls setConsensusTickets, so consensusTickets is empty in the running app.
    evidence: |-
      The gateway suggest response carries number arrays without per-component scores; the swarm-to-ticket pipeline does not exist yet (same gap as 3.2 RewardSignals). Rescoring is implemented and tested on synthetic tickets only.
    location: >-
      app/stores/useResonanceStore.ts setConsensusTickets
    severity: medium
  - summary: >-
      SwarmEqualizer slider may read locationY relative to the wrong target during off-track drags (unverified).
    evidence: |-
      Needs a drag on react-native-web and on a device to see whether value jumps; gestureState.dy from the grant position would be the alternative.
    location: >-
      app/components/SwarmEqualizer.tsx PanResponder handlers
    severity: medium (unverified)
  - summary: >-
      zustand is imported by the store but not declared in app/package.json, and its node_modules copy has no package.json, so the store test falls back to a mock create.
    evidence: |-
      Pre-existing: the store imported zustand before this story. Declaring/installing it is a dependency change outside this spec.
    location: >-
      app/package.json
    severity: low
---

<intent-contract>

## Intent

**Problem:** The "Swarm Equalizer" in `App.tsx` is a row of tap segments that overwrite one weight (weights stop summing to 1), fire no visual ripple, and nothing rescores consensus tickets from the weights.

**Approach:** Replace it with a `SwarmEqualizer` component of tactile vertical sliders. Each adjustment rebalances the four weights to sum to 1, rescores the store's consensus tickets with a pure weighted-sum function (timed, budget 100ms), and fires a "Riemannian Ripple" color-wave in the SpatialRetina shader, modeled on the existing muon-strike wiring.

## Boundaries & Constraints

**Always:** Weight keys are `frequency, deviation, cosmic, ml`; weights always sum to 1 after a user edit (the adjusted key takes the clamped value, the others rescale proportionally; if the others are all 0 they share the remainder equally). Ticket score = Σ weight_k · component_k, components in [0, 1]. Rescoring is synchronous inside the same store update that sets the weights. Ripple is colour only (no vertex displacement), Forensic Neon palette.

**Never:** No hibernation (3.4), distillation (3.5), or Kelly consumption (4.3). No Go gateway, Python engine, or MANIFOLD_STATE protocol changes. No new dependencies. No writes to `sprint-status.yaml`. Do not remove the existing muon-strike shockwave.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Slider moved | `cosmic` -> 0.7 from equal weights | cosmic = 0.7, others 0.1 each, sum 1; ripple id increments; tickets rescored | — |
| Others all zero | `ml` -> 0.4 with others 0 | others share 0.6 equally | — |
| Out-of-range / NaN | value -0.5, 1.7, NaN | clamped to [0, 1]; NaN ignored (no state change, no ripple) | No exception |
| Rescore budget | 10,000 tickets | Scores sorted descending, computed under 100ms | `lastRescoreMs` recorded |
| Touch mapping | y at track top / bottom / outside | value 1 / 0 / clamped | — |
| Invalid ticket | Missing or non-finite component | Scored with that component as 0 | No exception |

</intent-contract>

## Code Map

- `app/App.tsx` (~L196-240) -- inline tap-bar equalizer using `setWeights`; replace with `<SwarmEqualizer />`; its `barContainer`/`equalizer*` styles can go.
- `app/stores/useResonanceStore.ts` -- Zustand store; `weights` already feeds the SpatialRetina uniforms; add ticket, ripple and rescore state plus `setEqualizerWeight`.
- `app/components/SpatialRetina.tsx` -- shader uniforms and the muon-strike time-ref pattern (`lastMuonStrike`, `strikeTimeRef`, `useFrame`); the ripple follows the same pattern.
- `app/utils/manifold-telemetry.ts` -- `SwarmWeights` consumer (telemetry may overwrite weights; unchanged).
- `app/utils/__tests__/*.test.ts` -- `bun:test` style for pure utils.

## Tasks & Acceptance

**Execution:**
- `app/utils/equalizer.ts` -- `rebalanceWeights`, `valueFromTouch`, `scoreTickets`, `RIPPLE_DURATION_S`, `rippleOrigin(key)` -- AC 3.3.1, 3.3.2
- `app/stores/useResonanceStore.ts` -- `consensusTickets`, `ripple`, `lastRescoreMs`, `setConsensusTickets`, `setEqualizerWeight` (rebalance, rescore, ripple atomically) -- AC 3.3.1, 3.3.2
- `app/components/SwarmEqualizer.tsx` -- vertical slider per key (PanResponder track, live value label) calling `setEqualizerWeight` -- AC 3.3.1
- `app/components/SpatialRetina.tsx` -- ripple uniforms and a fragment colour wave expanding from the origin, advanced in `useFrame` -- AC 3.3.1
- `app/App.tsx` -- mount `SwarmEqualizer` in place of the inline panel
- `app/utils/__tests__/equalizer.test.ts` -- cover every I/O matrix row, including the store action and the 100ms budget

**Acceptance Criteria:**
- Given a live session, when a slider is adjusted, then the store `ripple` token changes in the same update that sets the weights, and the SpatialRetina advances its ripple uniforms from it.
- Given 10,000 consensus tickets, when a weight changes, then rescoring completes in under 100ms and `lastRescoreMs` records the measured time.
- Given any slider edit, then the four weights sum to 1.

## Spec Change Log

## Review Triage Log

### 2026-11-08 — Review pass
- verdicts: 27 findings — high 0, medium 5, low 16, false 4, maybe-false 2 (the intent-alignment layer is descriptive and its divergences restate rows below)
- findings:
  - `[medium]` `[patch]` Blind: setWeights/setManifoldState bypass rescoring after telemetry — both now rescore and set lastRescoreMs without rippling; tests added
  - `[medium]` `[patch]` Edge: same telemetry-stale-ranking finding (grouped) — same fix
  - `[medium]` `[patch]` Gap: telemetry stale ranking (grouped) — same fix
  - `[medium]` `[defer]` Blind: nothing populates consensusTickets — no ticket source with components exists in the app/gateway; producer gap spans the epic
  - `[medium]` `[defer]` Gap: no producer for tickets (grouped) — same
  - `[maybe-false]` `[defer]` Blind: locationY unreliable off-track — needs device/web drag check; deferred unverified
  - `[maybe-false]` `[defer]` Edge: locationY off-track (grouped) — same
  - `[low]` `[defer]` Blind: zustand undeclared / test mock fallback — pre-existing undeclared dependency
  - `[low]` `[defer]` Gap: zustand mock fallback (grouped) — same
  - `[low]` `[patch]` Edge: lastRescoreMs > 0 flaky on coarse timers — changed to >= 0
  - `[low]` `[patch]` Gap: same assertion (grouped) — same fix
  - `[low]` `[reject]` Blind: rescore per drag event may exceed frame budget — spec budget is 100ms; measured test passes and the ticket list is empty in-app
  - `[low]` `[reject]` Blind: ripple restarts every drag event — continuous glow at origin while dragging, wave expands on release; throttling would contradict the AC that each edit changes the ripple token
  - `[low]` `[reject]` Edge: ripple restart (grouped) — same
  - `[low]` `[reject]` Blind: shader constants, delta clamp, sentinel, untested wave — mirrors the muon-strike pattern; cosmetic
  - `[low]` `[reject]` Blind: accessibility, 4-letter labels, 36px track — no requirement; cosmetic
  - `[low]` `[reject]` Blind: hygiene items (clamp silently alters, re-renders, unused numbers field) — negligible
  - `[low]` `[reject]` Edge: duplicate clamped value rescoring/ripple — negligible cost
  - `[low]` `[reject]` Edge: Infinity clamps to 1 while NaN is ignored — slider cannot produce Infinity
  - `[low]` `[reject]` Edge: 100ms wall-clock test flaky — spec AC requires the assertion; 10k sort runs far below budget
  - `[low]` `[reject]` Edge: non-array setConsensusTickets input — internal caller only
  - `[low]` `[reject]` Gap: ripple id-to-uniform wiring untested — extraction adds public surface for thin glue mirroring untested muon wiring
  - `[low]` `[reject]` Gap: slider touch-to-store untested — no RN render harness in repo
  - `[low]` `[reject]` Blind: float drift in weight sum — error ~1e-16, below any tolerance used
  - `[false]` `[reject]` Blind: ratios lost after slider hits 1 — spec explicitly defines equal split when others are 0
  - `[false]` `[reject]` Edge: ratios lost (grouped) — same
  - `[false]` `[reject]` Edge: unnormalized telemetry weights — parseManifoldTelemetry validates sum 1 and finiteness
  - `[false]` `[reject]` Edge: toFixed on undefined weight — store weights are always numbers; parser validates

## Design Notes

Rebalance: `others_k' = others_k · (1 − v) / Σ others` (equal split if Σ others = 0). Ripple origin is a fixed point on the manifold per key so the wave is visibly attributable to the slider moved. Ripple state is store-driven (`{ id, key }`); the Retina owns elapsed time in a ref, restarting whenever `id` changes.

## Verification

**Commands:**
- `cd app && bun test utils/__tests__/equalizer.test.ts` -- expected: all pass
- `cd app && bun test utils/__tests__/manifold-telemetry.test.ts` -- expected: still passes
- `cd app && npx tsc --noEmit -p .` -- expected: no new errors in touched files

**Manual checks (if no CLI):**
- Run the app and drag a slider: the manifold flashes a colour wave and the other sliders rebalance.

## Auto Run Result

Status: done

**Summary:** Replaced the tap-bar equalizer with a `SwarmEqualizer` of vertical PanResponder sliders. Each edit rebalances the four weights to sum 1, rescores consensus tickets (timed, `lastRescoreMs`) and bumps a ripple token that drives a colour-only "Riemannian Ripple" in the SpatialRetina shader.

**Files changed:**
- `app/utils/equalizer.ts` -- rebalance, touch mapping, ticket scoring, ripple origins
- `app/stores/useResonanceStore.ts` -- tickets, ripple, `setEqualizerWeight`; telemetry actions now rescore too
- `app/components/SwarmEqualizer.tsx` -- vertical sliders
- `app/components/SpatialRetina.tsx` -- ripple uniforms and fragment wave
- `app/App.tsx` -- mounts `SwarmEqualizer`
- `app/utils/__tests__/equalizer.test.ts` -- matrix rows, store actions, 100ms budget

**Review:** 3 patched entries (1 medium group, 1 low group; 0 high), 3 deferred groups, remainder rejected with reasons in the triage log.

**Follow-up review recommended:** false

**Verification:** `bun test utils/__tests__/equalizer.test.ts utils/__tests__/manifold-telemetry.test.ts` -- 19 pass, 0 fail. `tsc` not run (TypeScript not installed in `app/`). Shader and sliders were not rendered or driven on screen.

**Residual risks:** No producer feeds `consensusTickets` in the app; slider off-track drag behaviour unverified; zustand undeclared in `app/package.json` so the store test may run on a mock `create`.
