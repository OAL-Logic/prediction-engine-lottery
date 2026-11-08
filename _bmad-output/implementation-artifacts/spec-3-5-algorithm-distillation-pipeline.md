---
title: 'Story 3.5: Algorithm Distillation Pipeline'
type: 'feature'
created: '2026-11-08'
status: 'done'
baseline_revision: '26c40aa5886fd1d2bf0d5a37c08dacf579e56b32'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: []
deferred:
  - summary: >-
      The default teacher path (teacher=None -> QuantumSidecar) and the real Amazon Braket QPU are never exercised.
    evidence: |-
      Every test injects a fake teacher. Here pennylane is not installed, so QuantumSidecar.distill_entropy raises and the pipeline would report DistillationError. A contract test with a stub mirroring the real return shape, and a run against a real Braket teacher, would settle it.
    location: >-
      engine/swarm/distillation.py _get_teacher
    severity: medium (unverified)
  - summary: >-
      The cached .npz carries no teacher provenance (source, fidelity, threshold, seed), and a fallback-sourced teacher is cached like a quantum one.
    evidence: |-
      save() writes only shape and weights under a fixed default file name; a VAE-fallback (uniform) teacher can pass the gate and overwrite a quantum-distilled policy. Matters once a consumer loads the cache.
    location: >-
      engine/swarm/distillation.py NumpyLSTMPolicy.save
    severity: low
---

<intent-contract>

## Intent

**Problem:** Quantum-grade sampling lives behind a QPU/cloud sidecar, so an edge or mobile user cannot get its "intuition" without a live QPU connection or sub-500ms latency. Nothing transfers the quantum model's behaviour into a classical policy or checks the transfer is faithful.

**Approach:** Add a `DistillationPipeline` that treats a quantum teacher (the `QuantumSidecar`-style `distill_entropy` interface, injectable) as the source of truth, trains a small classical LSTM policy on teacher samples, then verifies signal fidelity against the teacher's distribution (must be ≥ 0.90) and inference latency (P99 < 500ms) before accepting and caching the policy. Progress is pulsed to telemetry.

## Boundaries & Constraints

**Always:** The student is a pure-numpy LSTM (no torch/pennylane import, no new dependencies) that maps a sequence of past outcomes to a probability vector over the `2**qubits` outcomes. Signal fidelity is the classical (Bhattacharyya) fidelity `F = (sum sqrt(p*q))**2` between teacher and student distributions, averaged over probe contexts; threshold default 0.90, configurable. Training is deterministic for a given `seed`. The result reports `fidelity`, `passed`, `latency_p99_ms`, epochs, teacher source and cache path. Only a policy that passes the fidelity gate is written to `data/model_cache/` (`.npz`); a failing run returns `passed=False` and writes nothing. Training progress is emitted via `engine.modules.telemetry.pulse`. If the teacher call fails or returns an invalid distribution, raise `DistillationError`.

**Never:** No real Amazon Braket / QPU job submission or AWS credentials, no changes to `QuantumSidecar`, the Go gateway, frontend (`DistillationWaterfall`) or MANIFOLD_STATE protocol, no torch dependency, no ledger/DuckDB writes, no auto-registration as a strategy. No writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Teacher returns a skewed 16-outcome distribution (4 qubits) | `passed=True`, `fidelity >= 0.90`, `latency_p99_ms < 500`, `.npz` written | — |
| Uniform teacher | Teacher returns the uniform distribution | Student converges, `passed=True` | — |
| Under-trained | `epochs=0` on a skewed teacher | `passed=False`, nothing written | No exception |
| Teacher failure | `distill_entropy` raises | `DistillationError` | Message names the teacher failure |
| Bad distribution | Wrong length, negatives, NaN or sum far from 1 | `DistillationError` | Rejected before training |
| Determinism | Same seed and teacher twice | Identical fidelity and weights | — |
| Round trip | Save then `NumpyLSTMPolicy.load(path)` | Same `predict_probs` output | Missing/corrupt file raises `DistillationError` |
| Progress | Run with several epochs | At least one pulse per reporting interval and a final completion pulse | Pulse failure never aborts training |

</intent-contract>

## Code Map

- `engine/modules/cosmic.py` -- `QuantumSidecar.distill_entropy(qubits)` returns `{"entropy": [...2**qubits probs], "source", "fidelity"}`; the teacher interface the pipeline consumes (read-only).
- `engine/swarm/agent.py` -- shows how the sidecar result is used (`result["entropy"]`, `result.get("source")`) and the local fallback style.
- `engine/swarm/hibernation.py`, `engine/swarm/cluster.py` -- style reference: module layout, lazy `_pulse` helper, injectable collaborators.
- `engine/modules/telemetry.py` -- `pulse(message, level)` for progress.
- `engine/_paths.py` -- `PROJECT_ROOT` for default cache dir `data/model_cache/` (gitignored).
- `engine/swarm/__init__.py` -- export new public names.
- `tests/test_swarm_hibernation.py` -- pytest style; `.venv/bin/python` has numpy only.

## Tasks & Acceptance

**Execution:**
- `engine/swarm/distillation.py` -- `signal_fidelity`, `NumpyLSTMPolicy` (forward, `predict_probs`, BPTT step with Adam, `save`/`load`), `DistillationResult`, `DistillationError`, `DistillationPipeline.run()` (async; fetch teacher, train, verify fidelity + P99 latency, cache on pass) -- AC 3.5.1, 3.5.2
- `engine/swarm/__init__.py` -- export `DistillationPipeline`, `DistillationResult`, `DistillationError`, `NumpyLSTMPolicy`, `signal_fidelity`
- `tests/test_swarm_distillation.py` -- cover every matrix row with a fake teacher and `tmp_path` cache dir

**Acceptance Criteria:**
- Given a teacher distribution, when the pipeline completes, then it returns a classical LSTM policy and a fidelity score computed against the teacher.
- Given fidelity below the threshold, when the pipeline finishes, then the result is marked not passed and the policy is not cached.
- Given a passing policy, when it infers, then P99 latency is under 500ms.

## Spec Change Log

## Review Triage Log

### 2026-11-08 — Review pass
- verdicts: 32 findings — high 0, medium 5, low 26, false 1, maybe-false 0 (the intent-alignment layer is descriptive; its divergences restate rows below)
- findings:
  - `[low]` `[reject]` Blind: student ignores context, learns a constant vector — inherent to the context-free teacher interface; stated in Design Notes
  - `[low]` `[reject]` Blind: single teacher snapshot, teacher fidelity ignored — spec defines one call; no averaging asked for
  - `[low]` `[defer]` Blind: cached policy lacks teacher provenance — recorded in deferred
  - `[low]` `[reject]` Blind: non-atomic cache write — crash window negligible for a rare, rerunnable write
  - `[low]` `[reject]` Blind: latency check trivially loose, no warm-up — microsecond inference vs 500ms cannot flake
  - `[low]` `[reject]` Blind: run() blocks the event loop — no async caller drives it; fix adds threading complexity
  - `[low]` `[reject]` Blind: incomplete constructor validation, cache_name traversal — caller-controlled values
  - `[low]` `[reject]` Blind: sum tolerance renormalizes silently — deliberate, documented
  - `[low]` `[reject]` Blind: thin result metrics — outside spec
  - `[medium]` `[patch]` Blind: weak gradient test and test gaps — full finite-difference gradient test and latency-gate test added (grouped with the gap findings below)
  - `[low]` `[reject]` Blind: load NaN weights, no resume, bare except in `_pulse`, policy not wired into agents — outside spec or by design
  - `[low]` `[reject]` Edge: hidden/window/lr/limit not validated — same as the Blind validation row
  - `[low]` `[reject]` Edge: numpy ints rejected for qubits/epochs — callers pass Python ints
  - `[low]` `[reject]` Edge: no upper bound on qubits — callers are internal
  - `[low]` `[reject]` Edge: non-atomic save — same as above
  - `[low]` `[reject]` Edge: stale cache after a failing run — the earlier file was itself a verified policy
  - `[low]` `[reject]` Edge: raw OSError on cache write — raising on a failed write is correct
  - `[low]` `[reject]` Edge: short runs emit no epoch pulse — start and completion pulses still fire
  - `[low]` `[reject]` Edge: float contexts truncated — internal callers pass ints
  - `[low]` `[reject]` Edge: train_step input validation — internal API
  - `[low]` `[reject]` Edge: hostile .npz dims — local trusted cache
  - `[low]` `[reject]` Edge: no latency warm-up — see above
  - `[low]` `[reject]` Edge: mean fidelity can hide bad probes — spec defines the mean
  - `[medium]` `[patch]` Edge: gradient test sign-only — same patch as the Blind gradient row
  - `[low]` `[reject]` Edge: missing signal_fidelity shape and other tests — covered or negligible
  - `[false]` `[reject]` Edge claim: latency-failing policy withheld from cache is unstated — refuted: the spec says verify fidelity and P99 before accepting and caching
  - `[low]` `[reject]` Edge claim: per-interval pulse not guaranteed for last interval — the completion pulse covers it
  - `[medium]` `[patch]` Gap: latency gate untested — test_slow_policy_not_cached added
  - `[medium]` `[patch]` Gap: LSTM backprop unverified — finite-difference check over all five tensors added, found no bug; `train_step` split into `_grads` + Adam update
  - `[medium]` `[defer]` Gap: default QuantumSidecar teacher path unexercised — recorded in deferred
  - `[low]` `[reject]` Other: gradient test comment overstated — fixed by the patch
  - `[low]` `[reject]` Other: sum tolerance boundary untested — negligible

### 2026-11-08 — Review pass (follow-up)
- verdicts: 22 findings — high 0, medium 1, low 21, false 0, maybe-false 0 (the intent-alignment layer is descriptive; its divergences restate rows below)
- findings:
  - `[low]` `[reject]` Blind: student learns a constant vector, fidelity shows only the marginal — carried: inherent to the context-free teacher interface; stated in Design Notes
  - `[low]` `[reject]` Blind: probes not independent of training, drawn uniformly — carried: with a context-free teacher the probe distribution cannot change the result
  - `[low]` `[reject]` Blind: latency check optimistic, no warm-up, 64 samples — carried: microsecond inference vs 500ms cannot flake
  - `[low]` `[reject]` Blind: sum tolerance renormalizes silently — carried: deliberate, documented
  - `[low]` `[reject]` Blind: hyperparameters/qubits not validated — carried: caller-controlled values
  - `[low]` `[reject]` Blind: non-atomic save, stale cache after a failing run, no metadata — carried: negligible crash window; provenance already deferred
  - `[low]` `[reject]` Blind: load drops Adam state and does not check NaN — carried: no resume asked; local trusted cache
  - `[low]` `[reject]` Blind: remaining test gaps (margin, constructor validation, shape mismatch) — carried: negligible
  - `[low]` `[reject]` Blind: run() blocks the event loop — carried: no async caller drives it
  - `[low]` `[reject]` Blind: not wired to SwarmCluster/ExpertAgent, no docs — the intent's Never list excludes auto-registration; consumers are a later story
  - `[low]` `[reject]` Edge: hidden/window/lr/latency_limit_ms unvalidated — carried: same as the Blind validation row
  - `[low]` `[reject]` Edge: ValueError from NumpyLSTMPolicy leaks after the teacher fetch — same root as the validation row; fails loudly on a caller bug
  - `[low]` `[reject]` Edge: stale .npz after a failing run — carried: the earlier file was itself a verified policy
  - `[low]` `[reject]` Edge: non-atomic cache write — carried: negligible window
  - `[low]` `[reject]` Edge: hostile or NaN .npz on load — carried: local trusted cache
  - `[low]` `[reject]` Edge: no upper bound on qubits — carried: callers are internal
  - `[low]` `[reject]` Edge: latency cold start, no warm-up — carried
  - `[low]` `[patch]` Edge: test_progress_pulses counted the start pulse ("epochs" contains "epoch") and asserted >= 4, so one lost interval pulse would pass — verified in the test; tightened to match "Distillation epoch" and assert == 4 (patched directly, tests pass)
  - `[low]` `[reject]` Edge claim: last interval gets only the completion pulse — carried: the completion pulse covers it
  - `[medium]` `[defer]` Gap: default QuantumSidecar teacher path and DEFAULT_CACHE_DIR unexercised — carried: already in deferred
  - `[low]` `[reject]` Other: the real teacher only ever returns a uniform distribution — an observation, no defect in this diff
  - `[low]` `[reject]` Other: hidden/window/lr unvalidated — carried: same as the validation row

## Design Notes

Teacher shots are i.i.d. draws from the teacher distribution, so the student learns next-outcome probabilities from a sliding window of past outcomes; with a context-free teacher the LSTM's learned prior is the distilled distribution, and with a context-dependent teacher the same code applies. Probe contexts for verification are fresh random outcome windows.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_swarm_distillation.py tests/test_swarm_hibernation.py tests/test_swarm_cluster.py -q` -- expected: all pass


## Auto Run Result

Status: done

- **Summary:** `DistillationPipeline` trains a pure-numpy LSTM student on samples from an injectable quantum teacher, gates on Bhattacharyya fidelity (>= 0.90) and P99 latency (< 500ms), caches only passing policies as `.npz`, and pulses progress to telemetry.
- **Files changed:** `engine/swarm/distillation.py` (pipeline, policy, result and error types), `engine/swarm/__init__.py` (exports), `tests/test_swarm_distillation.py` (matrix coverage, gradient check, latency gate; the progress-pulse assertion was tightened in this follow-up pass).
- **Review findings (follow-up pass):** 22 findings; patches applied 1 (low), deferred 1 (medium, carried: default teacher path unexercised), rejected 20 (reasons recorded per row in the Review Triage Log; most carried from the earlier pass).
- **Follow-up review recommended:** false. This was a follow-up pass and it patched no high finding. Patched counts: high 0, medium 0, low 1.
- **Verification:** `.venv/bin/python -m pytest tests/test_swarm_distillation.py tests/test_swarm_hibernation.py tests/test_swarm_cluster.py -q` gave 47 passed.
- **Residual risks:** the default `QuantumSidecar` teacher and the real Braket path are never run in tests, and the cache carries no teacher provenance (both in `deferred`).
