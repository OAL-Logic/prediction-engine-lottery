---
title: 'Story 4.2: Forensic Replay & Geodesic Ghosting'
type: 'feature'
created: '2026-11-09'
status: 'in-review'
baseline_revision: '3fa3d7382a5220ff859771cb007bea8659d3cfb6'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
warnings: []
deferred: []
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

## Design Notes

The state vector is mapped to the same radial field as the shader: its first four entries (padded with 0) act as frequency/deviation/cosmic/ml amplitudes, giving a wireframe sphere whose radius is `7 + 1.8 * field`. The ghost is therefore the manifold shape at capture time, drawn as lines.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_forensic_replay.py tests/test_forensic_ledger.py -q` -- expected: all pass
- `cd app && bun test utils/__tests__/ghost.test.ts` -- expected: all pass
