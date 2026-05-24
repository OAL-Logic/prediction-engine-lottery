---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
inputDocuments: [
  '_bmad-output/planning-artifacts/prd.md',
  '_bmad-output/planning-artifacts/research/technical-quantum-astro-agentic-synthesis-for-v110-research-2026-05-14.md',
  '_bmad-output/project-context.md',
  'docs/user_guides/TUI.md',
  'mnt/c/ws/prj-lotto.LottoProphet'
]
version: '11.1'
---

# UX Design Specification v11.1: Prophet Dashboard

_This document defines the interface for the Desktop Prophet Client, synthesizing the high-density analytical patterns of LottoProphet with our v11.0 Quantum-Astro foundation._

---

## 1. The Prophet Dashboard (Desktop)

### 1.1 Interface Definition
The **Prophet Dashboard** is a multi-tabbed desktop environment (PySide6) designed for high-density forensic analysis. It serves as the primary interface for users who require real-time model training visualization and deep game-theoretic audits.

### 1.2 Dashboard Structure (Tabbed Cockpit)
- **Tab 1: Prediction Center**: Our signature 3D **Spatial Retina** integrated with the **Swarm Equalizer** and Model Selection (XGBoost, LSTM-CRF, Stacking AI).
- **Tab 2: Expected Value Model**: High-fidelity visualization of the **Advantage Principle**. Shows combination value distributions grounded in historical parity, magnitude, and span ratios.
- **Tab 3: Statistical Forensic**: Interactive charts (Trend, Frequency, Hot/Cold, Gap) using our high-contrast "Forensic Neon" palette.
- **Tab 4: Telemetry Console**: A real-time log emitter that displays agent reasoning loops, PQC handshake status, and algorithm distillation progress.

---

## 2. Key v11.1 Interactive Components

### 2.1 `ProphetTelemetryConsole`
- **Purpose**: Real-time feedback for long-running analytical jobs.
- **Visuals**: Scrolling monospaced log stream with semantic color coding (Green: Success, Violet: Astro-Pulse, Red: Decoherence).
- **Grounding**: Ported from the `LogEmitter` and `QTextEdit` pattern in `LottoProphet/lottery_predictor_app_new.py`.

### 2.2 `ExpectedValueHeatmap`
- **Purpose**: Visualizing the "Advantage Principle" for number pools.
- **Visuals**: A color-coded grid representing the expected value of number combinations, helping users identify "Value Clusters."
- **Grounding**: Driven by the `ExpectedValueLotteryModel` logic in `expected_value_model.py`.

### 2.3 `SequenceAuditViz`
- **Purpose**: Visualizing the output of the LSTM-CRF sequence model.
- **Visuals**: Probability bars showing the "Likelihood of Succession" between specific numbers in a predicted ticket.

---

## 3. Platform Strategy v11.1

- **Terminal (OpenTUI)**: High-speed, high-density analytical **Microscope**.
- **Mobile (Expo)**: Gestural, high-fidelity **Lens** for on-the-go generation.
- **Desktop (PySide6)**: Feature-rich, persistent **Cockpit** for strategic asset management.

---

## 4. Visual Language v11.1 (Synthesis)

We are blending the **LottoProphet** multi-tab organizational pattern with our **"Forensic Neon"** color tokens:
- **Tabs**: Sleek, borderless tab-bar with Obsidian Black background.
- **Charts**: High-fidelity line and scatter plots using `matplotlib` backend styled with Matrix Green and Astro Violet.
- **Logs**: High-contrast monospaced text on a deep-black viewport.

---

## 5. User Journey J4: The Prophet’s Audit

**Flow**:
1. User launches **Desktop Client**.
2. Retrains **ML Regressor** ensemble; monitors progress in the **Telemetry Console**.
3. Switches to **Expected Value** tab to identify high-advantage combination patterns.
4. Activates **3D Spatial Retina** to confirm resonance intersection.
5. Captures **Justified Number** and exports the Intelligence Narrative to Obsidian.
