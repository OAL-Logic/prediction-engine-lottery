# User Guide: Prophet Dashboard (Desktop) 🔮💻

The **Prophet Dashboard** is a professional-grade analytical cockpit (v11.1) built with PySide6. It provides a high-density, multi-tabbed interface for strategic custodians who require deep forensic deep-dives and real-time model training visualization.

---

## 🚀 1. Launching the Dashboard

Ensure you have the desktop dependencies installed:
```bash
pip install -e ".[desktop]"
```

Launch the client from the project root:
```bash
python3 desktop/src/main.py
```

---

## 🛠️ 2. Core Tab Modules

### 🎫 2.1 Prediction Center
The primary interface for generating **Justified Assets**.
- **Engine Configuration**: Select your target lottery, intelligence tier (e.g., Stacking AI, LSTM-CRF), and the desired number of tickets.
- **Hardware Acceleration**: Enable CUDA if a GPU is available to speed up deep learning inferences.
- **Actions**:
    - **Generate Justified Asset**: Triggers a resonance scan and produces tickets backed by deterministic proof.
    - **Retrain Swarm**: Refreshes the MARL agents with the latest historical data (monitored via the Telemetry Console).

### ⚖️ 2.2 Expected Value (Game Theory)
Visualizes the **Advantage Principle** for the current cycle.
- **Value Heatmap**: Identifies "Probability Resonance Clusters" in the number pool.
- **Advantage Scoring**: Shows which structural combinations (parity, high-low, sum) have the highest mathematical value based on game theory.

### 🔬 2.3 Forensic Analysis
Interactive high-fidelity statistical charting.
- **Forensic Views**: Switch between Frequency Distributions, Gap Statistics, and Structural Trends.
- **Diagnostic Summary**: View real-time metadata like Cycle Stability, Entropy Levels, and Dominant Clusters.

### 📓 2.4 Telemetry Console
The heart of the engine's real-time communication.
- **Live Stream**: Displays a monospaced log of every engine pulse, QPU distillation step, and learning update.
- **Semantic Highlighting**: 
    - [Glow Green]: Success/Capture
    - [Astro Violet]: Planetary Resonance detected
    - [Signal Red]: Decoherence Trap / System Error

---

## 🛡️ 3. Forensic Integrity

Every ticket generated via the dashboard is automatically logged in the **Forensic Audit Ledger** (DuckDB). You can verify any asset by right-clicking it in the result area to trigger a **Geodesic Ghosting** overlay in the manifold.

---

## 🌍 4. Multi-Platform Support

The Prophet Dashboard is fully compatible with:
- **Windows**: Native `.exe` packaging support via PyInstaller.
- **Linux**: High-performance rendering via WebGPU/Vulkan.
- **macOS**: Retina-display optimized fonts and high-DPI scaling.

---
_Demystifying complex numbers for the player who takes the game into another dimension._
