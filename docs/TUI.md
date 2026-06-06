# 🏛️ High-Fidelity TUI: Design & Navigation

The Lottery Engine features a sophisticated Terminal User Interface (TUI) designed for maximum information density and diagnostic clarity.

## 1. The Command Center

Access the high-fidelity guide by running:
```bash
./lottery help
```

The interface is divided into six logical sectors:

### ⭐ Primary Golden Path
The essential workflow for most users.
- `wizard`: Interactive step-by-step guidance.
- `fetch`: Data ingestion and synchronization.
- `suggest`: The core prediction engine.
- `analyze`: The primary diagnostic dashboard.

### 🔬 Analytics & Diagnostics
Deep-dive statistical tools for pattern recognition.
- `trend`: Multi-day diagnostic trajectories.
- `signal`: Signal-to-noise stability analysis.
- `oracle`: Persona-based natural language insights.
- `board`: Grid-based visualizations (Heatmaps, Halves, Rows).

### 🎟️ Betting & Tactical Tools
Tools for ticket optimization and portfolio management.
- `wheel`: Combinatorial covering designs.
- `portfolio`: Multi-tier risk diversification.
- `hedge`: Prize-tier coverage optimization.
- `risk`: Kelly Criterion bet sizing.

### 📓 Monitoring & Logs
Passive data accumulation and pipeline tracking.
- `daily`: Automated morning digest.
- `weekly`: 7-day performance retrospectives.
- `report`: YAML-driven analysis pipelines.
- `watchlist`: Multi-game batch tracking.

### ⚙️ System & Optimization
Engine maintenance and AutoML tuning.
- `daemon`: Background AutoML optimization.
- `calibrate`: Empirical hit-rate verification.
- `audit-data`: Data integrity and physics audit.
- `tune`: Hyperparameter grid searching.

### ✅ Verification & Tools
Single-ticket evaluation and personal alignment.
- `check`: Structural harmony auditor.
- `ticket-grade`: A+ to F performance grading.
- `session`: All-in-one pre-draw decision session.
- `calendar`: Personal Kabbalistic alignment.

---

## 2. Global UI Standards

- **Color Semantics:**
    - `Green`: Statistical GO signals, high-confidence hits.
    - `Yellow`: Drift detected, cautionary thresholds.
    - `Red`: SHIFT regimes, high-risk conditions, or errors.
    - `Cyan/Gold`: Mystical/Chaos Mode indicators.
- **Rich Integration:** All outputs use the `Rich` library for tables, panels, and sparklines.
- **Markdown Export:** Every command supports `--export-md` for seamless Obsidian integration.

---

## 3. Help System

- **Summary Help:** `python3 -m engine.cli.main --help`
- **Detailed Manual:** `python3 -m engine.cli.main --detailed-help`
- **TUI Guide:** `python3 -m engine.cli.main help`
