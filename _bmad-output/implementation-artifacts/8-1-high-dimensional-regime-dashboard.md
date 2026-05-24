# Story 8.1: High-Dimensional Regime Dashboard

Status: done

## Story

As an **Analyst**,
I want to visualize JS Divergence and Entropy trends over time,
so that I can detect when the "Mechanical Physics" of the draw are shifting.

## Acceptance Criteria

1. **Regime Analysis Support**: The `lottery analyze` command must support the `--regime` option. (AC: 8.1.1) [x]
2. **Topological Stability Metrics**: The system must calculate rolling **JS Divergence** and **Shannon Entropy** over a historical window (default=500 draws). (AC: 8.1.2) [x]
3. **Sparkline Visualization**: The CLI output must use `rich` sparklines to show the 100-draw trend of these metrics. (AC: 8.1.3) [x]
4. **Verdicts**: The system must output a "Regime Verdict" based on the stability: [STABLE, DRIFTING, DECOUPLED]. (AC: 8.1.4) [x]
5. **Obsidian Integration**: The regime trends must be included in the `--export-md` payload. (AC: 8.1.5) [x]

## Tasks / Subtasks

- [x] Implement `analyze_regime_stability` in `engine/modules/regime.py`. (AC: 8.1.2, 8.1.4)
  - [x] Implement rolling JS Divergence between adjacent windows.
  - [x] Implement rolling Shannon Entropy.
- [x] Update `engine/cli/commands/analyze.py` to add the `--regime` option. (AC: 8.1.1)
  - [x] Use `rich` sparklines for trend visualization. (AC: 8.1.3)
- [x] Add the regime data to the `AnalysisResult` and CLI output. (AC: 8.1.4)
- [x] Add a unit test to verify stability calculations. (AC: 8.1.2)

## Dev Notes

- **Metrics**: 
  - **JS Divergence**: Measures shift in number frequency between historical and recent windows.
  - **Shannon Entropy**: Measures the "Information Density" or randomness of the draw process.
- **Visualization**: High-fidelity sparklines integrated into the terminal output.

### Project Structure Notes

- **Module**: `engine/modules/regime.py`
- **Command**: `engine/cli/commands/analyze.py`

### References

- [Source: docs/architecture/technical-spec.md#The Chaos Temperature Governor]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 8.1: High-Dimensional Regime Dashboard]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Validated divergence calculation with synthetic distribution shifts in `tests/test_regime.py`.
- Verified sparkline rendering in `rich` console.

### Completion Notes List

- ✅ Implemented high-dimensional regime analytics.
- ✅ Added stability verdicts and trend sparklines.
- ✅ Verified sub-millisecond calculation for 500-draw windows.

### File List

- `engine/modules/regime.py` (MODIFIED)
- `engine/cli/commands/analyze.py` (MODIFIED)
- `tests/test_regime.py` (NEW)
