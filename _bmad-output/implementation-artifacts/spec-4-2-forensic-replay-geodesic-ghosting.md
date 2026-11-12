---
title: 'Story 4.2: Forensic Replay & Geodesic Ghosting'
type: 'feature'
created: '2026-11-09'
status: 'done'
baseline_revision: '3fa3d7382a5220ff859771cb007bea8659d3cfb6'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
warnings: []
deferred:
  - summary: >-
      Nothing delivers a ledger replay payload to the app store, so the Forensic Replay button stays disabled at runtime.
    evidence: |-
      loadReplay/startReplay(payload) have no caller outside tests; build_replay is not exposed to the app. Closing it needs an engine-to-app channel (gateway or MANIFOLD_STATE change) and capture() wiring, both excluded by the intent's Never section.
    location: >-
      app/App.tsx:209
    severity: medium
  - summary: >-
      SpatialRetina fade and ghost wiring (uFade, ghost opacity, ring fade) is covered only by pure-helper tests.
    evidence: |-
      No R3F render test harness exists in the repo; the fade math is unit tested.
    location: >-
      app/components/SpatialRetina.tsx:386
    severity: low
---

<intent-contract>

## Intent

**Problem:** A ticket captured in the forensic ledger (Story 4.1) cannot be inspected visually: there is no replay of the historical state, and the 3D manifold has no way to show the original geodesic convergence point (FR13, UX-DR6).

**Approach:** Add `engine/modules/replay.py` that loads a ledger entry by seq, re-verifies the hash chain and returns a JSON-able replay payload. In the app, add pure helpers `app/utils/ghost.ts` (fade state machine, ghost geometry from a state vector), a replay slice in the store, a ghost wireframe in `SpatialRetina`, and a "Forensic Replay" trigger in `App.tsx`.

## Boundaries & Constraints

**Always:** Replay is read-only against the ledger. A payload is produced only if `verify()` is ok; otherwise `ReplayError`. The payload carries `seq`, `ticket`, `state_vector`, `agent_weights`, `qpu_fidelity`, `entry_hash`, `captured_at`. Ghost fade is time-based and clamped: current manifold alpha goes 1 -> 0 and ghost alpha 0 -> 1 over `GHOST_FADE_S`; exiting reverses it. Ghost is a transparent wireframe (low opacity, no depth write). Non-finite or empty state vectors are rejected by the helper, never rendered.

**Never:** No ledger writes or new ledger methods, no Go gateway, MANIFOLD_STATE protocol or new dependency changes, no wiring of `capture()` into ticket generation, no writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Replay | valid seq, intact chain | payload equal to the stored entry fields (floats bit-exact) | — |
| Unknown seq | seq not in ledger | `ReplayError` | no payload |
| Tampered | chain fails `verify()` | `ReplayError` naming first bad seq | no payload |
| Fade in | replay triggered, t = GHOST_FADE_S/2 | current alpha 0.5, ghost alpha 0.5 | — |
| Fade end | t >= GHOST_FADE_S | current 0, ghost 1 | clamped |
| Exit | replay cleared | fades back to current 1, ghost 0 | — |
| Bad vector | empty / NaN state vector | `ghostGeometry` returns null | ghost not shown |

</intent-contract>

## Code Map

- `engine/modules/ledger.py` -- `ForensicLedger.get/verify`, `LedgerError`; read-only reuse.
- `app/components/SpatialRetina.tsx` -- manifold shader (uniform `uResonating` pattern), ring geometries; add `uFade` and ghost `lineSegments`.
- `app/stores/useResonanceStore.ts` -- store with ripple slice pattern; add replay slice.
- `app/utils/equalizer.ts` -- pure-helper + test style; `app/utils/__tests__/equalizer.test.ts` uses `bun:test`.
- `app/App.tsx` -- Canvas at ~line 199; add trigger button.
- `tests/test_forensic_ledger.py` -- pytest style; run with `.venv/bin/python -m pytest`.

## Tasks & Acceptance

**Execution:**
- `engine/modules/replay.py` -- `ReplayError`, `build_replay(ledger, seq)` -- verify chain then return payload
- `tests/test_forensic_replay.py` -- Replay, Unknown seq, Tampered rows
- `app/utils/ghost.ts` -- `GHOST_FADE_S`, `fadeAlphas`, `ghostGeometry`, `parseReplayPayload` -- pure helpers
- `app/utils/__tests__/ghost.test.ts` -- Fade in/end/exit and Bad vector rows
- `app/stores/useResonanceStore.ts` -- `replay` slice: `startReplay`, `stopReplay`
- `app/components/SpatialRetina.tsx` -- fade current manifold, render ghost wireframe
- `app/App.tsx` -- "Forensic Replay" toggle, enabled when a replay payload is loaded

**Acceptance Criteria:**
- Given a ticket stored in the ledger, when the user triggers "Forensic Replay" in the 3D view, then the current manifold fades out and a transparent wireframe ghost of the original geodesic convergence point fades in.
- Given a tampered ledger, when replay is requested, then no payload is produced.

## Spec Change Log

## Review Triage Log

### 2026-11-11 — Review pass
- verdicts: 24 findings — high 0, medium 2, low 12, false 7, maybe-false 0 (3 reviewer items merged into existing rows)
- findings:
  - `[medium]` `[defer]` Replay payload never reaches the store; button permanently disabled — real, but the fix needs gateway/protocol/capture wiring the intent's Never section excludes; recorded in deferred.
  - `[medium]` `[patch]` Store replay actions (startReplay/loadReplay/stopReplay) untested — added app/utils/__tests__/replay-store.test.ts (3 tests).
  - `[low]` `[defer]` SpatialRetina fade wiring untested beyond helpers — no render harness; recorded in deferred.
  - `[low]` `[reject]` Ghost uses only first 4 vector entries / formula may drift from shader — documented in Design Notes, no concrete harm.
  - `[low]` `[reject]` Ticket/weights/hash not displayed — not required by the intent.
  - `[low]` `[reject]` fadeAlphas exported but unused by the component — named in the spec's tasks and tested; harmless.
  - `[low]` `[reject]` Abrupt ghost swap when a new payload loads while active — cosmetic, no loader exists yet.
  - `[low]` `[reject]` No read-only UI lock during replay — negligible harm.
  - `[low]` `[reject]` seq <= 0 yields "unknown ledger seq" — message is accurate; fix adds a branch.
  - `[low]` `[reject]` Unbounded ghost radius for huge finite vectors — inf overflow already yields null; unlikely.
  - `[low]` `[reject]` Silent ignore of invalid loadReplay/startReplay — by spec design.
  - `[low]` `[reject]` Python/TS payload schema contract not pinned by a test; entry_hash/captured_at format unchecked — unlikely, adds complexity.
  - `[low]` `[reject]` Per-frame opacity write, button a11y/legend, inline style object — cosmetic, matches existing toggle pattern.
  - `[low]` `[reject]` Ghost is a sphere, not a convergence-point marker (intent reading) — Design Notes fixes the reading; single defensible reading in this repo.
  - `[false]` `[reject]` Delta stall/snap in stepFadeProgress — progress is clamped to [0,1]; zero dt correctly holds.
  - `[false]` `[reject]` replayActive true with null ghost shows EXIT with no ghost — replay is only set from parseReplayPayload, which requires renderable geometry, and is never cleared.
  - `[false]` `[reject]` Tamper blocks earlier entries — required by the spec (payload only if verify() ok).
  - `[false]` `[reject]` NaN/non-finite state_vector can reach payload — ledger capture rejects non-finite values (ledger.py:70-76).
  - `[false]` `[reject]` Non-LedgerError escapes build_replay — ledger wraps its errors in LedgerError.
  - `[false]` `[reject]` verify/get TOCTOU race — ledger is append-only and local; no demonstrated path.
  - `[false]` `[reject]` Executable file mode on replay.py/test — pre-existing in baseline, not this diff.
  - `[false]` `[reject]` Intent-alignment tamper guarantee not exercised through app path — engine test covers it; no app path exists (see deferred).

## Design Notes

The state vector is mapped to the same radial field as the shader: its first four entries (padded with 0) act as frequency/deviation/cosmic/ml amplitudes, giving a wireframe sphere whose radius is `7 + 1.8 * field`. The ghost is therefore the manifold shape at capture time, drawn as lines.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_forensic_replay.py tests/test_forensic_ledger.py -q` -- expected: all pass
- `cd app && bun test utils/__tests__/ghost.test.ts` -- expected: all pass

## Auto Run Result

Status: done

**Summary:** Story 4.2 adds the read-only `build_replay` (verifies the chain, then returns a payload), pure ghost helpers, a store replay slice, a fading ghost wireframe in `SpatialRetina`, and a "Forensic Replay" toggle in `App.tsx`.

**Files changed:**
- `engine/modules/replay.py` -- `ReplayError`, `build_replay`.
- `tests/test_forensic_replay.py` -- replay, unknown seq and tampered rows.
- `app/utils/ghost.ts` -- fade helpers, `ghostGeometry`, `parseReplayPayload`.
- `app/utils/__tests__/ghost.test.ts` -- helper tests.
- `app/utils/__tests__/replay-store.test.ts` -- store replay slice tests (review patch).
- `app/stores/useResonanceStore.ts` -- replay slice.
- `app/components/SpatialRetina.tsx` -- `uFade` uniform, ring fade, ghost lineSegments.
- `app/App.tsx` -- toggle button.

**Review:** 24 findings. Patched 1 (medium: store tests). Deferred 2 (medium: no engine-to-app delivery of payload; low: renderer wiring untested). Rejected 21, each with its reason in the triage log.

**Follow-up review recommended:** false (1 medium patched, no high).

**Verification:** `pytest tests/test_forensic_replay.py tests/test_forensic_ledger.py` passed (39). `bun test` on ghost, replay-store and equalizer tests passed (25).

**Residual risks:** The button is disabled at runtime until something loads a payload (deferred); the visual fade was not checked in a live render.
