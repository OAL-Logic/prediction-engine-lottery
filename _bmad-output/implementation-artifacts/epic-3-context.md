# Epic 3 Context: Bio-Cosmic Intelligence Swarm (The Brain)

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Orchestrate a distributed swarm of multi-agent reinforcement learning (MARL) expert agents that collectively model the non-linear curvature of the lottery manifold, let the user steer and prune the swarm, and distill the resulting quantum-grade policy into a lightweight classical model usable at the edge. This is the "brain" of the engine: it turns the quantum sampling and spatial visualization foundations into collective, auditable, tunable intelligence.

## Stories

- Story 3.1: Distributed MARL Swarm Orchestrator
- Story 3.2: Collaborative Riemannian Evolution
- Story 3.3: The Swarm Equalizer (Weighting UI)
- Story 3.4: Automated Agent Hibernation
- Story 3.5: Algorithm Distillation Pipeline

## Requirements & Constraints

- The swarm must scale to 1,000 parallel MARL agents in a single cluster, and each agent must be able to sample independently from the quantum (QPU) sidecar.
- Agents share reward signals from out-of-sample draws and collaboratively update one shared Riemannian state-vector; this evolution must be visible in real time in the 3D Spatial Retina.
- User weight adjustments on any agent must trigger an immediate visual ripple in the manifold and recompute consensus ticket scores in under 100ms.
- Agents are evaluated over a rolling 50-draw audit window; an agent whose "Lift over Random" falls below the statistical threshold is automatically hibernated, with the event and rationale logged in the forensic ledger.
- Distillation must yield a classical-efficient LSTM policy retaining at least 90% signal fidelity versus the original QPU sampling, with inference under 500ms (P99).
- Agentic reasoning trajectories must be encrypted via post-quantum tunnels; all service interfaces must stay compatible with Model Context Protocol 2.1 (JSON-RPC 2.0).

## Technical Decisions

- Orchestration runs on a Ray RLlib cluster (v2.55.1); the swarm is initialized from `engine/swarm/cluster.py`.
- Quantum sampling bridge uses PennyLane with active-sampling (AS-SQD); training of the quantum model happens in the cloud (Amazon Braket) before distillation.
- Hybrid data tier: DuckDB for the audit ledger, Qdrant for agent memory.
- Real-time telemetry (engine pulses, distillation progress, training logs) flows through the Go Gateway log-emitter WebSocket; long-running work must stay off UI threads.
- Python engine is the analytical core; strategies that train must expose a standardized `train()` interface reporting progress to the log emitter. Trained models serialize to `data/model_cache/`.
- Frontend state uses Zustand; 3D rendering uses WebGPU via @react-three/fiber and must hold 60 FPS at 100k+ nodes.

## UX & Interaction Patterns

- `SwarmEqualizer`: tactile vertical sliders for per-agent weighting, surfaced inside the Prediction Center alongside the Spatial Retina.
- Weight changes produce a "Riemannian Ripple" color-wave in the 3D manifold.
- `DistillationWaterfall`: binary-stream visualization of training convergence; distillation progress also appears in the telemetry console.
- Follow the "Forensic Neon" palette across TUI and app.

## Cross-Story Dependencies

- Builds on Epic 1 (quantum distillation sidecar, PQC gateway) and Epic 2 (Spatial Retina, DistillationWaterfall UI foundations).
- 3.2 depends on 3.1 (swarm exists); 3.3 depends on 3.1/3.2 (agents and live manifold); 3.4 depends on 3.1 and the forensic ledger from Epic 4 (Story 4.1) for event logging; 3.5 depends on the quantum sidecar and the DistillationWaterfall.
- Epic 4's swarm-based Kelly optimizer consumes swarm consensus from this epic.
