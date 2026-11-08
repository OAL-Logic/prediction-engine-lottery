---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments: [
  '_bmad-output/planning-artifacts/prd.md',
  '_bmad-output/planning-artifacts/ux-design-specification.md',
  '_bmad-output/planning-artifacts/architecture.md',
  'mnt/c/ws/prj-lotto.LottoProphet'
]
version: '11.1'
---

# lottery-engine - Epic Breakdown v11.1

## Overview
This document provides the complete epic and story breakdown for the v11.1 Prophet Synthesis. We are integrating the analytical depth and desktop GUI capabilities of the LottoProphet project as a new alternative interface and intelligence tier.

## Requirements Inventory (v11.1 Additions)

### Functional Requirements
- **FR20 (Expected Value)**: Implement the game-theory based expected value model for combination scoring.
- **FR21 (LSTM-CRF)**: Implement sequence modeling for inter-number dependency detection.
- **FR22 (ML Ensemble)**: Integrate XGBoost, LightGBM, and CatBoost into a unified regressor tier.
- **FR23 (Desktop Client)**: Develop a multi-platform PySide6 interface with tabbed analysis.
- **FR24 (Feature Engineering)**: Implement sliding window time-series feature extraction.

### FR Coverage Map (v11.1 Additions)
- FR20: Epic 5 Story 5.1 - Game-Theoretic Expected Value Model
- FR21: Epic 5 Story 5.2 - Sequence Logic Brain (LSTM-CRF)
- FR22: Epic 5 Story 5.3 - Extended ML Hub (XGB/LGBM/CAT)
- FR23: Epic 5 Story 5.4 - Desktop Client Interface (PySide6)
- FR24: Epic 5 Story 5.3 - Extended ML Hub (Feature Engineering)

## Requirements Inventory (v11.0 Foundation — restored)

### Functional Requirements

FR1: Serialize planetary data (AC, MC, DC, IC) into agentic context via MCP.
FR2: Ingest real-time hardware-distilled entropy from physical QPUs.
FR3: Visualize "Resonance Intersection" point where planetary transits and quantum entropy converge.
FR4: Auto-adjust sampling temp based on real-time Solar (Kp-Index) and Seismic (USGS) jitter.
FR5: Simulate "Muon Strikes" (quantum bit-flips) during Riemannian projection.
FR6: Deploy distributed swarm of MARL agents to model lottery manifold.
FR7: Agents collaboratively evolve shared Riemannian state-vector based on collective lift.
FR8: Distill complex quantum models into classical-efficient policies (e.g., LSTMs) for edge inference.
FR9: Interactively weight "Expert Agent" priorities in TUI/App.
FR10: Automatically "hibernate" underperforming agents using recursive alpha-pruning.
FR11: Generate "Justified Number" backed by deterministic geodesic audit trail.
FR12: Maintain persistent, append-only Forensic Audit Ledger of all calculations.
FR13: Verify ticket against historical manifold state (Forensic Replay).
FR14: Calculate optimal bet sizes using Kelly Criterion based on swarm confidence.
FR15: Export narratives to Obsidian with deep-links to Geodesic Evidence Panel.
FR16: Terminate PQC-level TLS (Kyber) at gateway to protect agent tunnels.
FR17: Process sensitive hashing data (Name/Birth Date) on local device (Sovereignty).
FR18: Rotate crypto-algorithms without interrupting live predictive swarm.
FR19: Switch between Cloud QPU and Local VAE simulators based on latency/noise thresholds.

### NonFunctional Requirements

NFR1: Distilled inferences must complete in < 500ms (P99).
NFR2: Gateway PQC/MCP overhead must not exceed 20ms per request.
NFR3: 99.9% uptime for Astro-Quantum sidecar integration.
NFR4: 100% of agentic reasoning trajectories must be encrypted via PQC tunnels.
NFR5: Support up to 1,000 parallel MARL agents within a single Ray cluster.
NFR6: 3D visualization must handle 100k+ historical nodes with 60 FPS fluidity.
NFR7: 100% compatibility with Model Context Protocol 2.1 (JSON-RPC 2.0).

### Additional Requirements

- Initialize Ray RLlib Cluster v2.55.1 for decentralized orchestration.
- Implement PennyLane + AS-SQD for active sampling quantum bridge.
- Implement FastMCP (Python SDK 2.1) for Astro-Cartography Hub.
- Use Hybrid Data Tier: DuckDB (Audit Ledger) + Qdrant (Agent Memory).
- Implement X25519MLKEM768 at Gateway for PQC security.
- Standardize on WebGPU via @react-three/fiber v9.6 for cross-platform 3D parity.
- Frontend State: Zustand for real-time low-latency reactive updates.

### UX Design Requirements

UX-DR1: SpatialRetina component for interactive 3D Riemannian manifold with Astro-Lines.
UX-DR2: ForensicLedger component for live-scrolling, bi-directional audit trail.
UX-DR3: ResonanceSigil component for visual lock-on confirmation (Scanning, Converging, Locked).
UX-DR4: SwarmEqualizer component for tactile vertical sliders for multi-agent weighting.
UX-DR5: DistillationWaterfall component for binary-stream visualization of training convergence.
UX-DR6: Geodesic Ghosting pattern showing historical state-vector overlay during replay.
UX-DR7: Adhere to "Forensic Neon" color palette across TUI and App.

### FR Coverage Map

- FR1: Epic 1 Story 1.2 - Astro-Cartography MCP Server
- FR2: Epic 1 Story 1.3 - Quantum Distillation Sidecar
- FR3: Epic 2 Story 2.1 - The Spatial Retina (Riemannian Manifold)
- FR4: Epic 1 Story 1.2 - Astro-Cartography MCP Server
- FR5: Epic 2 Story 2.4 - Muon Strike Simulation (Cosmic Ray)
- FR6: Epic 3 Story 3.1 - Distributed MARL Swarm Orchestrator
- FR7: Epic 3 Story 3.2 - Collaborative Riemannian Evolution
- FR8: Epic 3 Story 3.5 - Algorithm Distillation Pipeline
- FR9: Epic 3 Story 3.3 - The Swarm Equalizer (Weighting UI)
- FR10: Epic 3 Story 3.4 - Automated Agent Hibernation
- FR11: Epic 4 Story 4.1 - Immutable Forensic Audit Ledger
- FR12: Epic 4 Story 4.1 - Immutable Forensic Audit Ledger
- FR13: Epic 4 Story 4.2 - Forensic Replay & Geodesic Ghosting
- FR14: Epic 4 Story 4.3 - Swarm-based Kelly Optimizer
- FR15: Epic 4 Story 4.4 - Intelligence Narrative Obsidian Export
- FR16: Epic 1 Story 1.1 - Post-Quantum Gateway Middleware
- FR17: Epic 1 Story 1.4 - Sovereign Local Hashing
- FR18: Epic 4 Story 4.1 - Immutable Forensic Audit Ledger
- FR19: Epic 1 Story 1.3 - Quantum Distillation Sidecar

## Epic List

### Epic 1: The Resonance Bridge (Foundation)
**Goal**: Synchronize the engine with physical planetary and quantum entropy sources via a secure Go Gateway hub.
**FRs covered**: FR1, FR2, FR4, FR16, FR17, FR19.

### Epic 2: The Oracle’s Retina (Spatial Visualization)
**Goal**: Visually explore the "Resonance Intersection" in a 3D high-dimensional manifold across TUI and App.
**FRs covered**: FR3, FR5.

### Epic 3: Bio-Cosmic Intelligence Swarm (The Brain)
**Goal**: Orchestrate a distributed swarm of MARL agents to model non-linear manifold curvature and distill policies.
**FRs covered**: FR6, FR7, FR8, FR9, FR10.

### Epic 4: The Asset Class Factory (Forensic Integrity)
**Goal**: Manage "Justified Numbers" backed by a deterministic, immutable audit trail and optimized bet sizing.
**FRs covered**: FR11, FR12, FR13, FR14, FR15, FR18.

### Epic 5: Prophet Synthesis (Interface & Intelligence)
**Goal**: Integrate the full analytical depth and GUI capabilities of LottoProphet as a cross-platform desktop alternative.
**FRs covered**: FR20, FR21, FR22, FR23, FR24.

---

## Epic 1: The Resonance Bridge (Foundation)

Goal: Synchronize the engine with physical planetary and quantum entropy sources via a secure Go Gateway hub.

### Story 1.1: Post-Quantum Gateway Middleware

As a **Strategic Custodian**,
I want my predictive reasoning trajectories to be encrypted via post-quantum hybrid tunnels,
So that my high-value assets remain secure from future decryption attacks.

**Acceptance Criteria:**

**Given** the Go Gateway is running
**When** a client initiates a v11.0 session
**Then** the gateway must negotiate a `X25519MLKEM768` hybrid handshake
**And** all subsequent agent reasoning payloads must be 100% encrypted.

### Story 1.2: Astro-Cartography MCP Server

As a **Chaos Researcher**,
I want arcsecond-accurate planetary Great Circle data injected into the agentic context,
So that my predictions resonate with real-time cosmic geometry.

**Acceptance Criteria:**

**Given** the FastMCP server is active in `engine/modules/environment.py`
**When** a MARL agent requests `get_planetary_resonance`
**Then** the server must return coordinates for AC/MC/DC/IC lines using EAA standards.

### Story 1.3: Quantum Distillation Sidecar

As a **Data Alchemist**,
I want to ingest hardware-distilled entropy from physical QPUs,
So that my predictive swarm uses true quantum uncertainty instead of simulated noise.

**Acceptance Criteria:**

**Given** an active Amazon Braket session in `engine/modules/cosmic.py`
**When** a distillation job is triggered
**Then** the system must fetch hardware-distilled entropy
**And** automatically switch to the Local VAE simulator if latency exceeds 10s.

### Story 1.4: Sovereign Local Hashing

As a **Sovereign User**,
I want my intentional hashing data to be processed locally,
So that my private vibrational inputs (Name/Birth Date) never leave my device.

**Acceptance Criteria:**

**Given** user input in the Expo App
**When** the "Capture" button is triggered
**Then** the BLAKE2b hash must be calculated on-device
**And** only the resulting fingerprint is transmitted to the gateway.

## Epic 2: The Oracle’s Retina (Spatial Visualization)

Goal: Visually explore the "Resonance Intersection" in a 3D high-dimensional manifold across TUI and App.

### Story 2.1: The Spatial Retina (Riemannian Manifold)

As a **Data Alchemist**,
I want an intuitive 3D exploration of non-linear lottery clusters,
So that I can identify geodesic minima in the high-dimensional manifold.

**Acceptance Criteria:**

**Given** a historical dataset in QCSC Mode
**When** the user opens the manifold view
**Then** the system must render a fluid 3D Riemannian surface
**And** maintain a stable 60 FPS fluidity even with 100k+ historical nodes.

### Story 2.2: The Resonance Intersection Sigil

As a **Strategic Custodian**,
I want clear visual feedback when a high-confidence vector is identified,
So that I can confidently "capture" a justified ticket.

**Acceptance Criteria:**

**Given** an agentic swarm finding a geodesic minimum
**When** the vector aligns with a planetary Great Circle intersection
**Then** the `ResonanceSigil` component must transition to a high-luminescence Matrix Green glow
**And** provide a "Geodesic Lock" haptic pulse on mobile devices.

### Story 2.3: The Distillation Waterfall UI

As a **Chaos Researcher**,
I want to visualize the active learning progress of the quantum distillation,
So that I can monitor the convergence of the quantum signal in real-time.

**Acceptance Criteria:**

**Given** a long-running QPU job from the Gateway
**When** progress tokens are received by the UI
**Then** the system must render a cascading hex-bit waterfall
**And** the waterfall must "crystallize" into nodes in the 3D manifold as the job completes.

### Story 2.4: Muon Strike Simulation (Cosmic Ray)

As a **Nerd Mode User**,
I want quantum bit-flips injected into my ticket generation process,
So that I can account for cosmic noise and prevent deterministic traps.

**Acceptance Criteria:**

**Given** a ticket generation sequence in Chaos Mode
**When** a simulated muon strike occurs (~0.5% probability)
**Then** a single number in the ticket must undergo a bit-flip mutation
**And** the event must be logged with a "COSMIC_RAY_DETECTED" tag in the Evidence Panel.

## Epic 3: Bio-Cosmic Intelligence Swarm (The Brain)

Goal: Orchestrate a distributed swarm of MARL agents to model non-linear manifold curvature and distill policies.

### Story 3.1: Distributed MARL Swarm Orchestrator

As a **Swarm Reliability Engineer**,
I want to scale predictive modeling to include hundreds of independent "Expert" agents,
So that I can maximize the search space for non-linear lottery clusters.

**Acceptance Criteria:**

**Given** a high-performance compute environment (Ray RLlib)
**When** the swarm is initialized via `engine/swarm/cluster.py`
**Then** the system must support up to 1,000 parallel MARL agents
**And** each agent must be able to independently sample from the QPU sidecar.

### Story 3.2: Collaborative Riemannian Evolution

As a **Data Alchemist**,
I want agents to share intelligence to find the global "Geodesic Minimum" faster,
So that the manifold curvature reflects the collective learning of the entire swarm.

**Acceptance Criteria:**

**Given** a distributed swarm in a learning session
**When** agents receive reward signals from out-of-sample draws
**Then** they must collaboratively update a shared Riemannian state-vector
**And** this manifold evolution must be visible in real-time in the 3D Spatial Retina.

### Story 3.3: The Swarm Equalizer (Weighting UI)

As a **Strategic Custodian**,
I want to directly influence agentic consensus via a tactile interaction model,
So that I can align the swarm with my own intuition or specific analytical focus.

**Acceptance Criteria:**

**Given** a live v11.0 orchestration session
**When** a user adjusts an agent's weight slider in the `SwarmEqualizer`
**Then** the system must immediately trigger a "Riemannian Ripple" color-wave in the 3D manifold
**And** recalculate the consensus ticket scores in less than 100ms.

### Story 3.4: Automated Agent Hibernation

As a **System Architect**,
I want to automatically silence "noisy" or underperforming agents,
So that the system maintains a high signal-to-noise ratio during consensus.

**Acceptance Criteria:**

**Given** a rolling 50-draw audit window
**When** an agent's "Lift over Random" falls below the statistical threshold
**Then** the system must automatically hibernate that agent from the active swarm
**And** log the hibernation event and rationale in the Forensic Ledger.

### Story 3.5: Algorithm Distillation Pipeline

As a **Mobile User**,
I want "Quantum-grade intuition" at the edge without a constant QPU connection,
So that I can generate high-fidelity tickets with sub-500ms latency on my device.

**Acceptance Criteria:**

**Given** a trained quantum model in the Amazon Braket cloud
**When** the `DistillationWaterfall` completes the training-transfer loop
**Then** the system must produce a classical-efficient LSTM policy
**And** verify the distilled policy maintains ≥ 90% signal fidelity compared to the original QPU sampling.

## Epic 4: The Asset Class Factory (Forensic Integrity)

Goal: Manage "Justified Numbers" backed by a deterministic, immutable audit trail and optimized bet sizing.

### Story 4.1: Immutable Forensic Audit Ledger

As a **Strategic Custodian**,
I want guaranteed integrity and reproducibility of every "Justified Number,"
So that I can mathematically defend my chosen assets.

**Acceptance Criteria:**

**Given** a generated ticket vector
**When** the "Capture" event is logged in `engine/modules/ledger.py`
**Then** the system must store the complete geodesic state-vector, agentic weights, and QPU fidelity scores
**And** this entry must be mathematically immutable within the DuckDB ledger.

### Story 4.2: Forensic Replay & Geodesic Ghosting

As a **Data Alchemist**,
I want to visually verify the exact mathematical conditions of a past winning ticket,
So that I can refine my swarm orchestration based on historical resonance.

**Acceptance Criteria:**

**Given** a ticket stored in the Sovereign Vault
**When** the user triggers "Forensic Replay" in the 3D view
**Then** the manifold must fade out the current state
**And** fade in a transparent "ghost" wireframe of the original geodesic convergence point.

### Story 4.3: Swarm-based Kelly Optimizer

As a **Strategic Player**,
I want mathematically optimal bet sizing to maximize long-term wealth growth,
So that I can leverage the swarm's confidence without over-exposing my bankroll.

**Acceptance Criteria:**

**Given** a consensus prediction from the MARL swarm
**When** the swarm confidence exceeds the baseline threshold
**Then** the system must calculate the optimal fractional bet size based on the user's vault balance
**And** display this as a "Confidence Leverage" signal in the dashboard.

### Story 4.4: Intelligence Narrative Obsidian Export

As a **Chaos Researcher**,
I want to maintain a personal research journal of "justified" predictive assets,
So that I can track long-term resonance trends in my Obsidian vault.

**Acceptance Criteria:**

**Given** a finalized v11.0 intelligence session
**When** the user triggers "Export to Obsidian"
**Then** the system must produce a formatted `.md` file containing the narrative
**And** include functional deep-links to the specific Geodesic Evidence Panel coordinates.

---

## Epic 5: Prophet Synthesis (Interface & Intelligence)

**Context Reference**: [Prophet Concepts: Game Theory & Sequence Modeling](docs/research/prophet-concepts.md)

### Story 5.1: Game-Theoretic Expected Value Model
**Technical Grounding**: Ported from `expected_value_model.py`.
```python
# LottoProphet Pattern: Feature Valuation
value_dict = {
    'even_odd_ratio': {},  # Parity logic
    'high_low_ratio': {},  # Magnitude logic
    'sum_range': {},       # Arithmetic logic
    'span_range': {},      # Spread logic
    'sequence_pattern': {} # Succession logic
}
```
**User Value**: Identify combinations that maximize the "Advantage Principle" based on historical structural ratios.

**Acceptance Criteria:**
- **Given** a historical dataset
- **When** the Expected Value strategy is invoked
- **Then** the system must calculate value scores for `even_odd_ratio`, `high_low_ratio`, and `sum_range`
- **And** output a normalized combination value score [0.0, 1.0].

### Story 5.2: Sequence Logic Brain (LSTM-CRF)
**Technical Grounding**: Ported from `model.py`.
```python
# LottoProphet Pattern: Deep Sequence Labeling
class LstmCRFModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, output_seq_length):
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim * output_seq_length)
        self.crf = CRF(output_dim, batch_first=True)
```
**User Value**: Deep sequence modeling to ensure predicted tickets follow realistic dependency patterns.

**Acceptance Criteria:**
- **Given** a PyTorch environment
- **When** the LSTM-CRF model is initialized
- **Then** it must utilize a Bi-LSTM layer followed by a Conditional Random Field (CRF)
- **And** achieve a sequence-labeling accuracy ≥ v10.0 baselines.

### Story 5.3: Extended ML Hub (XGBoost/LightGBM/CatBoost)
**Technical Grounding**: Ported from `ml_models.py`.
```python
# LottoProphet Pattern: Multi-Regressor Ensemble
MODEL_TYPES = {
    'random_forest': 'random forest',
    'xgboost': 'XGBoost',
    'gbdt': 'gradient boosted tree',
    'ensemble': 'integrated model'
}
# Supports optional: lightgbm, catboost
```
**User Value**: Superior predictive lift via high-performance gradient boosting ensembles.

**Acceptance Criteria:**
- **Given** sliding-window features (frequency, gap, trend)
- **When** the ML Regressor hub is trained
- **Then** it must optimize parameters for XGBoost, LightGBM, and CatBoost
- **And** store the serialized models in `data/model_cache/`.

### Story 5.4: Desktop Client Interface (PySide6)
**Technical Grounding**: Ported from `lottery_predictor_app_new.py`.
```python
# LottoProphet Pattern: Multi-Tab Dashboard
self.tab_widget = QTabWidget()
self.tab_widget.addTab(self.main_tab, "predict")
self.tab_widget.addTab(self.expectedvalue_tab, "Expected value model")
self.tab_widget.addTab(self.analysis_tab, "data analysis")
```
**User Value**: A feature-rich desktop alternative for professional deep-dives.

**Acceptance Criteria:**
- **Given** a PySide6 environment
- **When** the Desktop Client launches
- **Then** it must present a multi-tabbed dashboard (Predict | Expected Value | Analysis | Logs)
- **And** adhere to the "Forensic Neon" color palette.

### Story 5.5: Real-time Telemetry WebSocket
**Technical Grounding**: Ported from `thread_utils.py`.
```python
# LottoProphet Pattern: Non-blocking Log Emitting
class LogEmitter(QObject):
    new_log = pyqtSignal(str)
    def emit_log(self, message):
        self.new_log.emit(message)
```
**User Value**: Real-time feedback for long-running distillation and training jobs.

**Acceptance Criteria:**
- **Given** an active analytical job
- **When** the Go Gateway emits a signal
- **Then** the Desktop Client must render a live-scrolling monospaced log stream
- **And** provide semantic highlighting for critical events.
