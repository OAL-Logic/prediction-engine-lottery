---
title: Spec — Next-Gen Lottery Engine Desktop Cockpit (cockpit/)
status: ready-for-agent
labels:
  - ready-for-agent
  - cockpit-v2
  - pyside6
  - Lottery Studio-parity
---

# Specification: Next-Gen Lottery Engine Desktop Cockpit (`cockpit/`)

## 1. Problem Statement & Mission
The legacy desktop interface in `desktop/` carries technical debt and mixed conventions. The user requires a completely greenfield, decoupled PySide6 desktop suite in a dedicated root directory (`cockpit/`).
The cockpit must achieve **100% functional parity and functional superiority over Lottery Studio Free and Registered/Pro Editions**:
- Full 105+ combinatorial filter engine + Fault Tolerance Engine (Error Allowance $N$-of-$M$).
- Complete Wheeling Subsystem (Covering designs $t$-if-$m$ of $v$, Positional Wheels, Banker/Key numbers, Hamming redundancy pruning, reduction zones).
- Physical Betslip Layout Calibrator & Printer for Caixa Econômica Federal slips (Lotofácil, Mega-Sena, Quina, Lotomania, Dupla Sena).
- Hybrid 2D/3D Esoteric & Deterministic Chaos Observatory (`pyqtgraph.opengl` 60fps GPU acceleration + Matplotlib 3D fallback).
- Multi-Monitor Docking Workspace layout with perspective persistence.
- Strict compliance with `pyqt6-ui-designer` design tokens (4px grid, dual light/dark themes, complete interactive widget states).
- Headless synchronization with `engine/` algorithms and CLI (`lottery cockpit` / `lottery desktop`).

## 2. Phased Implementation Architecture

### Phase 1: Architecture Core, Design Tokens & Shell
- Clean directory scaffolding under `cockpit/src/`.
- Domain models (`GameSchema`, `FilterNode`, `ToleranceRule`, `WheelingConfig`, `ProfileBundle`).
- Strict 4px grid design tokens, typography, and palette presets (`ThemeManager`).
- Multi-monitor docking manager (`DockingManager`) and perspective manager (`PerspectiveManager`).
- Headless `EngineBridge` dynamically binding games from `engine/adapters/registry.py`.
- Custom high-DPI `QPainter` widgets (`BallMatrixWidget`, `TicketReceiptWidget`).
- Perspectives: Express Mode (1-click generation, 6-layer diagnostic HUD) and Studio Mode foundation.
- Standalone launcher: `cockpit/src/app.py`.
- Phase 1 test suite (`cockpit/tests/test_phase1.py`).

### Phase 2: Complete Lottery Studio Combinatorial Filter & Wheeling Engine
- Full 105+ filter catalog across 7 categories.
- High-performance vectorized chunked streaming worker (`StreamingCombinatorialWorker`).
- Fault Tolerance Engine ($N$-of-$M$ Error Allowance).
- Full & Abbreviated Wheeling Studio ($t$-if-$m$ of $v$, Banker Keys, Hamming pruning).
- Auto-Fit historical condition scanner and Batch Condition Optimizer.

### Phase 3: Esoteric & Deterministic Chaos Observatory (2D & 3D)
- Primary 60fps GPU 3D visualizer using `pyqtgraph.opengl.GLViewWidget`.
- Secondary Matplotlib 3D vector export.
- Strange Attractors (Lorenz, Rössler, Clifford) & 3D kinetic drum bounce simulation.
- Celestial Ephemeris orbit map, 2D Biorhythm multi-track waveforms, Gematria/Kabbalistic tree graphs.

### Phase 4: Physical Betslip Calibrator, File I/O & CLI Subcommands
- Caixa betslip layout calibrator & printer (Lotofácil, Mega-Sena, Quina, Lotomania).
- File format support: `.slk`, `.csv`, `.txt`, and Lottery Studio space-delimited text.
- CLI subcommands `lottery cockpit` and `lottery desktop`.

### Phase 5: Verification, Test Automation & Visual Audits
- Comprehensive automated test suite in `cockpit/tests/`.
- High-resolution visual screenshots for Light and Dark modes across all perspectives.
