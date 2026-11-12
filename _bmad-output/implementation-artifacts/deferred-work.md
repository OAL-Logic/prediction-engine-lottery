### DW-1: Ray round collection and sidecar sampling have no per-agent timeout, so one hung actor or sidecar call can stall a round.
origin: spec-deferred 4266af213158
location: engine/swarm/cluster.py:_ray_collect
source_spec: `spec-3-1-distributed-marl-swarm-orchestrator.md`
severity: medium
reason: _ray_collect uses serial ray.get without timeout; agent.sample awaits distill_entropy unbounded. Real only with a hung QPU/actor; unverifiable here (Ray not installed). (declared severity: medium (unverified))
status: open

### DW-2: health() worker_memory_mb is the driver process RSS; on the Ray backend it understates worker memory.
origin: spec-deferred 0bce85c63c88
location: engine/swarm/cluster.py:health
source_spec: `spec-3-1-distributed-marl-swarm-orchestrator.md`
severity: medium
reason: psutil.Process() covers only the current process. Accurate for the local backend; Ray workers are separate processes.
status: open

### DW-3: No producer calls setConsensusTickets, so consensusTickets is empty in the running app.
origin: spec-deferred 011bdb1689e3
location: app/stores/useResonanceStore.ts setConsensusTickets
source_spec: `spec-3-3-the-swarm-equalizer-weighting-ui.md`
severity: medium
reason: The gateway suggest response carries number arrays without per-component scores; the swarm-to-ticket pipeline does not exist yet (same gap as 3.2 RewardSignals). Rescoring is implemented and tested on synthetic tickets only.
status: open

### DW-4: SwarmEqualizer slider may read locationY relative to the wrong target during off-track drags (unverified).
origin: spec-deferred 746dbfac38f5
location: app/components/SwarmEqualizer.tsx PanResponder handlers
source_spec: `spec-3-3-the-swarm-equalizer-weighting-ui.md`
severity: medium
reason: Needs a drag on react-native-web and on a device to see whether value jumps; gestureState.dy from the grant position would be the alternative. (declared severity: medium (unverified))
status: open

### DW-5: zustand is imported by the store but not declared in app/package.json, and its node_modules copy has no package.json, so the store test falls back to a mock create.
origin: spec-deferred c34456ee18c8
location: app/package.json
source_spec: `spec-3-3-the-swarm-equalizer-weighting-ui.md`
severity: low
reason: Pre-existing: the store imported zustand before this story. Declaring/installing it is a dependency change outside this spec.
status: open

### DW-6: No producer calls SwarmCluster.record_lifts, so no agent accumulates a 50-draw window in the running engine.
origin: spec-deferred 3dd9189826ca
location: engine/swarm/cluster.py record_lifts
source_spec: `spec-3-4-automated-agent-hibernation.md`
severity: medium
reason: Nothing in engine/ builds per-agent RewardSignals from out-of-sample draws; same gap as the 3.2 reward producer and DW-3. Hibernation is implemented and tested with synthetic signals only.
status: open

### DW-7: The default hibernation ledger is a plain JSONL file (data/forensic_ledger.jsonl); Story 4.1's Forensic Ledger does not exist yet.
origin: spec-deferred c5c7df675b04
location: engine/swarm/hibernation.py JsonlLedger
source_spec: `spec-3-4-automated-agent-hibernation.md`
severity: low
reason: Story 4.1 should adopt or wrap JsonlLedger and its agent_hibernated event shape so hibernation events land in the real immutable ledger.
status: open

### DW-8: The default teacher path (teacher=None -> QuantumSidecar) and the real Amazon Braket QPU are never exercised.
origin: spec-deferred 6bba4110f2a3
location: engine/swarm/distillation.py _get_teacher
source_spec: `spec-3-5-algorithm-distillation-pipeline.md`
severity: medium
reason: Every test injects a fake teacher. Here pennylane is not installed, so QuantumSidecar.distill_entropy raises and the pipeline would report DistillationError. A contract test with a stub mirroring the real return shape, and a run against a real Braket teacher, would settle it. (declared severity: medium (unverified))
status: open

### DW-9: The cached .npz carries no teacher provenance (source, fidelity, threshold, seed), and a fallback-sourced teacher is cached like a quantum one.
origin: spec-deferred cbb3c12cddf3
location: engine/swarm/distillation.py NumpyLSTMPolicy.save
source_spec: `spec-3-5-algorithm-distillation-pipeline.md`
severity: low
reason: save() writes only shape and weights under a fixed default file name; a VAE-fallback (uniform) teacher can pass the gate and overwrite a quantum-distilled policy. Matters once a consumer loads the cache.
status: open

### DW-10: Tail truncation or a fully re-sealed chain is not detectable by verify() alone, and nothing is wired to call capture() yet.
origin: spec-deferred ef0bf9da4a1e
location: engine/modules/ledger.py ForensicLedger.verify
source_spec: `spec-4-1-immutable-forensic-audit-ledger.md`
severity: medium
reason: The hash chain is unkeyed SHA-256 on a local DuckDB file; deleting the last rows leaves a valid chain. Documented in the module docstring and pinned by a test. Needs an external anchor of latest().entry_hash (or an HMAC key), and a Capture call site in ticket generation. (declared severity: medium (design limit))
status: open

### DW-11: Nothing delivers a ledger replay payload to the app store, so the Forensic Replay button stays disabled at runtime.
origin: spec-deferred 6cd0cdf19bda
location: app/App.tsx:209
source_spec: `spec-4-2-forensic-replay-geodesic-ghosting.md`
severity: medium
reason: loadReplay/startReplay(payload) have no caller outside tests; build_replay is not exposed to the app. Closing it needs an engine-to-app channel (gateway or MANIFOLD_STATE change) and capture() wiring, both excluded by the intent's Never section.
status: open

### DW-12: SpatialRetina fade and ghost wiring (uFade, ghost opacity, ring fade) is covered only by pure-helper tests.
origin: spec-deferred 171e25c5cddc
location: app/components/SpatialRetina.tsx:386
source_spec: `spec-4-2-forensic-replay-geodesic-ghosting.md`
severity: low
reason: No R3F render test harness exists in the repo; the fade math is unit tested.
status: open
