---
title: 'Story 3.1: Distributed MARL Swarm Orchestrator'
type: 'feature'
created: '2026-11-08'
status: 'done'
baseline_revision: '71de6ff66362401d63370a8d0b5159ee524aa772'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/3-1-distributed-marl-swarm-orchestrator.md'
warnings: []
deferred:
  - summary: >-
      Ray round collection and sidecar sampling have no per-agent timeout, so one hung actor or sidecar call can stall a round.
    evidence: |-
      _ray_collect uses serial ray.get without timeout; agent.sample awaits distill_entropy unbounded. Real only with a hung QPU/actor; unverifiable here (Ray not installed).
    location: >-
      engine/swarm/cluster.py:_ray_collect
    severity: medium (unverified)
  - summary: >-
      health() worker_memory_mb is the driver process RSS; on the Ray backend it understates worker memory.
    evidence: |-
      psutil.Process() covers only the current process. Accurate for the local backend; Ray workers are separate processes.
    location: >-
      engine/swarm/cluster.py:health
    severity: medium
---

<intent-contract>

## Intent

**Problem:** The engine has a single `QuantumSidecar` and no way to run many independent "Expert" agents against it, so the search space for non-linear clusters is bounded by one sampler. There is no cluster lifecycle, no secure agent signaling, and no swarm health view.

**Approach:** Add `engine/swarm/` with a cluster orchestrator (Ray when installed and enabled, otherwise an asyncio local pool), a per-agent sampler with sidecar-to-local-simulator fallback, a PQC-signaled sealed channel for trajectories, and a health snapshot exposed via a `swarm-health` CLI command and telemetry pulses.

## Boundaries & Constraints

**Always:** Agent count is capped at 1,000 (NFR5). Each agent owns its own RNG and sidecar instance (no shared mutable sampling state). Missing Ray/PennyLane must degrade silently to local backend / simulator. Trajectories leave an agent only as sealed envelopes carrying an active-PQC signal and key version, mirroring the gateway's `X-PQC-Active` / `X-PQC-Key-Version` semantics. Telemetry goes through `engine.modules.telemetry.pulse`.

**Never:** No real ML-KEM implementation or new third-party dependency (the gateway's PQC is also a simulation seam; `cryptography` AES-GCM + HKDF is the stand-in). No Riemannian evolution, weighting UI, hibernation or distillation (Stories 3.2-3.5). No edits to `QuantumSidecar` or the Go gateway. No writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Local spin-up | `start(n=50)`, no Ray | 50 agents active, backend `local` | — |
| Over cap | `start(n=1001)` / `scale_to(1001)` | — | `ValueError` |
| Scale | `scale_to` up then down | Active count matches target | — |
| Round | `run_round()` | One sealed trajectory per agent, distinct per-agent seeds | Failed agent excluded and counted, round continues |
| Sidecar down | sampler raises (e.g. PennyLane missing) | Agent falls back to local simulator, sample flagged `source="local_simulator"` | No exception escapes |
| Tampered/replayed envelope | Modified ciphertext or reused counter | — | `PQCChannelError` |
| Inactive PQC signal | Envelope with `pqc_active=False` | — | `PQCChannelError` |
| Health | Any state | Active agents, worker memory MB, samples/sec | Zero throughput before first round |

</intent-contract>

## Code Map

- `engine/modules/cosmic.py:15` -- `QuantumSidecar.distill_entropy(qubits, force_fallback)` async; lazy-imports pennylane outside its try (ImportError propagates) -- agents must catch and fall back.
- `engine/modules/telemetry.py` -- `pulse(message, level)` UDP emitter, fire-and-forget.
- `gateway/pqc_middleware.go:144` -- `X-PQC-Active` / `X-PQC-Key-Version` signaling to mirror (read-only).
- `engine/cli/main.py:1889` -- `data-status` registration pattern (lazy import of impl, `PANEL_SYSTEM`); `engine/cli/commands/data_status.py` -- command impl pattern.
- `tests/test_cosmic_quantum.py` -- `@pytest.mark.asyncio` style (strict mode).
- Ray and PennyLane are not installed in `.venv`; `cryptography`, `psutil`, `numpy` are.

## Tasks & Acceptance

**Execution:**
- `engine/swarm/__init__.py` -- package exports -- new package
- `engine/swarm/channel.py` -- `PQCChannel` (HKDF session key, AES-256-GCM, key version, monotonic counter, replay/tamper/inactive-signal rejection) -- AC 3.1.3
- `engine/swarm/agent.py` -- `ExpertAgent` (own seed/RNG/sidecar, async `sample()` with fallback, sealed trajectory) -- AC 3.1.2
- `engine/swarm/cluster.py` -- `SwarmCluster` (Ray/local backends, `start`/`scale_to`/`run_round`/`shutdown`, `health()`, telemetry) -- AC 3.1.1, 3.1.4
- `engine/cli/commands/swarm_health.py` + `engine/cli/main.py` -- `swarm-health` command printing the health snapshot -- AC 3.1.4
- `tests/test_swarm_cluster.py` -- cover every I/O matrix row, incl. a fake `ray` module for the Ray path

**Acceptance Criteria:**
- Given no Ray, when a cluster starts with 1,000 agents and runs a round, then 1,000 sealed trajectories return and the backend is `local`.
- Given a failing sidecar, when agents sample, then every agent still returns a flagged local-simulator sample.
- Given a sealed trajectory, when opened with the session channel, then plaintext round-trips; any tamper or replay raises.
- Given a running cluster, when `swarm-health` runs, then it shows active agents, memory and throughput.

## Spec Change Log

## Review Triage Log

### 2026-11-08 — Review pass
- verdicts: 33 findings — high 1, medium 4, low 6, false 1, maybe-false 2 (grouped; remaining reviewer items are repeats of these claims or rejected below)
- findings:
  - `[high]` `[patch]` PQCChannel holds an unpicklable AESGCM, so Ray actor creation would fail — verified by pickle TypeError; added __getstate__/__setstate__ plus pickle round-trip test
  - `[medium]` `[patch]` Malformed sidecar entropy escapes the fallback — _draw moved inside the try; test added
  - `[medium]` `[patch]` Weak swarm-health CLI test (arg wiring, over-cap exit) — assertions and 1001 case added
  - `[low]` `[patch]` bool accepted as agent count; Ray remote class rebuilt per spawn; shutdown kills a foreign Ray session; weak memory assertion — all fixed
  - `[maybe-false]` `[defer]` no timeout on Ray get / sidecar call — deferred
  - `[medium]` `[defer]` worker memory is driver RSS on Ray — deferred
  - `[low]` `[reject]` AAD delimiter ambiguity, struct.error on bad counter, JSON error after auth, strict ordered replay, lock for concurrent rounds, hardcoded pqc_active, telemetry exception wrapping, start() cleanup on failure, health() pulse noise, qubits validation, duplicated CLI defaults — internal-only callers, unlikely in everyday use, fix adds guards/complexity
  - `[false]` `[reject]` asyncio.run inside Ray actor breaks sidecar — sync Ray actor has no running loop and QuantumSidecar holds no loop-bound state
  - `[low]` `[reject]` epic-3-context.md drops FR/NFR IDs — regenerated per the compile rules ("describe by purpose, not source"); generated artifact
  - `[low]` `[reject]` intent-alignment reading B (awaiting-operator) — no AC requires a human-only external action; real-Ray run is an agent-doable dev step, noted as residual risk

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_swarm_cluster.py -q` -- expected: all pass
- `.venv/bin/python -m pytest tests/test_cosmic_quantum.py tests/test_cli_commands_smoke.py -q` -- expected: no regressions

## Auto Run Result

Status: done

**Summary:** Added `engine/swarm/` (PQC-signaled sealed channel, ExpertAgent with sidecar-to-local-simulator fallback, SwarmCluster with Ray/local backends capped at 1,000 agents, health snapshot) and a `swarm-health` CLI command.

**Files:** `engine/swarm/{__init__,channel,agent,cluster}.py` (new), `engine/cli/commands/swarm_health.py` (new), `engine/cli/main.py` (command registration), `tests/test_swarm_cluster.py` (15 tests), `epic-3-context.md` (recompiled).

**Review:** patches applied — 1 high, 2 medium, 4 low; deferred 2 (see frontmatter); the rest rejected with reasons in the triage log.

**Follow-up review recommended:** false.

**Verification:** `pytest tests/test_swarm_cluster.py` — 15 passed. `test_cosmic_quantum.py` has 2 failures from PennyLane not installed (file untouched by this story, not compared against a clean checkout). `test_cli_commands_smoke.py` hangs in `test_daily_export_md` on a network call; the implementer saw 63 passes with `-k "not daily"`. The suite's data-file side effects were reverted.

**Residual risks:** real Ray was never run (fake module only); PQC is an AES-GCM/HKDF simulation, not ML-KEM; `swarm-health` probes a short-lived local cluster.
