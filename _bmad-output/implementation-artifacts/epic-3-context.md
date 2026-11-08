# Epic 3 Context: Bio-Cosmic Intelligence Swarm (The Brain)

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Orchestrate a distributed swarm of Multi-Agent Reinforcement Learning (MARL) agents to model non-linear manifold curvature, collaborate on geodesic state-vector evolution, and distill complex quantum models into classical-efficient policies for edge inference.

## Stories

- Story 3.1: Distributed MARL Swarm Orchestrator
- Story 3.2: Collaborative Riemannian Evolution
- Story 3.3: The Swarm Equalizer (Weighting UI)
- Story 3.4: Automated Agent Hibernation
- Story 3.5: Algorithm Distillation Pipeline

## Requirements & Constraints

- FR6: Deploy distributed swarm of MARL agents to model lottery manifold.
- FR7: Agents collaboratively evolve shared Riemannian state-vector based on collective lift.
- FR8: Distill complex quantum models into classical-efficient policies (e.g., LSTMs) for edge inference.
- FR9: Interactively weight "Expert Agent" priorities in TUI/App.
- FR10: Automatically "hibernate" underperforming agents using recursive alpha-pruning.
- NFR5: Support up to 1,000 parallel MARL agents within a single Ray cluster.
- NFR1: Distilled inferences must complete in < 500ms (P99).
- NFR4: 100% of agentic reasoning trajectories must be encrypted via PQC tunnels.
- UX-DR4: SwarmEqualizer component for tactile vertical sliders for multi-agent weighting.

## Technical Decisions

- Initialize Ray RLlib Cluster v2.55.1 for decentralized swarm orchestration (`engine/swarm/cluster.py`).
- Inner-loop optimization uses Python/Rust with shared Riemannian state-vector in `engine/swarm/policy.py`.
- MAGRPO (Multi-Agent Group Relative Policy Optimization) for collective reward updates based on out-of-sample draws.
- Distillation transfers high-complexity QPU-sampled distributions to classical LSTMs in `engine/strategies/distilled/`.
- FastMCP / Model Context Protocol 2.1 JSON-RPC for agent-to-tool context exchange.
- DuckDB persistent Forensic Audit Ledger for logging agent hibernation events and alpha-pruning metrics.

## UX & Interaction Patterns

- SwarmEqualizer tactile vertical sliders allowing users to dynamically adjust agent tier priorities.
- Real-time "Riemannian Ripple" visual feedback in the 3D manifold when agent weights change (< 100ms response).
- Real-time visualization of distillation convergence via binary-stream waterfall.

## Cross-Story Dependencies

- Foundation relies on Epic 1 (Astro-Cartography MCP server & QPU sidecar).
- Visualizations hook into Epic 2 (Spatial Retina 3D Riemannian Manifold).
- Audit events feed into Epic 4 (Forensic Audit Ledger).
