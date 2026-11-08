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
