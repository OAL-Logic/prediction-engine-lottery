# Epic 4 Context: The Asset Class Factory (Forensic Integrity)

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Manage "Justified Numbers": every generated ticket is backed by a deterministic, immutable audit trail that can be replayed visually, sized with mathematically optimal bets, and exported as a research narrative. This lets the user defend and refine chosen assets by reproducing the exact conditions that produced them.

## Stories

- Story 4.1: Immutable Forensic Audit Ledger
- Story 4.2: Forensic Replay & Geodesic Ghosting
- Story 4.3: Swarm-based Kelly Optimizer
- Story 4.4: Intelligence Narrative Obsidian Export

## Requirements & Constraints

- Every "Justified Number" must have a deterministic geodesic audit trail; the ledger is persistent and append-only.
- Each captured entry stores the full geodesic state-vector, agentic weights, and QPU fidelity scores, and must be mathematically immutable once written.
- Ledger/crypto algorithms must be rotatable without interrupting the live predictive swarm.
- A ticket can be verified against the historical manifold state (Forensic Replay).
- Bet sizing uses the Kelly Criterion driven by swarm confidence; it applies only when confidence exceeds a baseline threshold, is fractional, and is based on the user's vault balance. It is surfaced as a "Confidence Leverage" signal in the dashboard.
- Exports are formatted Markdown narratives with functional deep-links to Geodesic Evidence Panel coordinates.
- Sensitive hashing data stays on the local device (sovereignty); agent reasoning trajectories travel over PQC-encrypted tunnels.

## Technical Decisions

- Hybrid data tier: DuckDB holds the audit ledger; Qdrant holds agent memory.
- Ledger logic lives in `engine/modules/ledger.py` (the "Capture" event).
- Frontend uses WebGPU via @react-three/fiber for the 3D view, with Zustand for low-latency reactive state.
- Engine is Python; the Go gateway handles PQC termination and the telemetry WebSocket.

## UX & Interaction Patterns

- ForensicLedger component: live-scrolling, bi-directional audit trail.
- Geodesic Ghosting: on "Forensic Replay", the current manifold fades out and a transparent ghost wireframe of the original geodesic convergence point fades in (historical state-vector overlay).
- Use the "Forensic Neon" palette consistently across TUI and apps.
- The Desktop client's journey ends with capturing a Justified Number and exporting the narrative to Obsidian.

## Cross-Story Dependencies

- Stories 4.2 and 4.4 depend on the ledger entries from 4.1 (replay reads stored state; export links to evidence coordinates).
- Story 4.3 consumes swarm consensus/confidence from Epic 3.
- Story 4.2 builds on the 3D Spatial Retina from Epic 2.
- Story 4.4 targets a finalized v11.0 intelligence session.
