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
