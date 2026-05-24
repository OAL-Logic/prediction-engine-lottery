# Story 1.2: Strategic Sentiment Matrix

Status: complete

## Story

As a **Data Alchemist**,
I want a rolling audit of 50+ models ranking their "Lift over Random",
so that I can focus on strategies that are currently "in-phase" with draw physics.

## Acceptance Criteria

1. **Strategy Audit Execution**: The `decision_matrix.py` module must be able to audit all registered strategies for a given game. (AC: 1.2.1) [x]
2. **Lift over Random Calculation**: The system must calculate the "Lift over Random" metric (Accuracy vs. Baseline) for each strategy over a configurable window (default=30 draws). (AC: 1.2.2) [x]
3. **Sentiment Labeling**: Each strategy must be assigned a sentiment label based on its lift: [Strong Buy, Buy, Neutral, Sell]. (AC: 1.2.3) [x]
4. **Data Contract Integrity**: The resulting matrix must be available as a structured data object (dict or DataFrame) for consumption by the Narrative Engine and TUI. (AC: 1.2.4) [x]
5. **Obsidian Metadata Integration**: The matrix summary must be included in the `--export-md` payload. (AC: 1.2.5) [x]

## Tasks / Subtasks

- [x] Refine `get_full_strategy_matrix` in `engine/modules/decision_matrix.py`. (AC: 1.2.1, 1.2.2)
  - [x] Implement robust "Lift over Random" calculation.
  - [x] Add logic for strategy hibernation if performance is below noise threshold.
- [x] Implement `get_sentiment_label` logic. (AC: 1.2.3)
  - [x] Define thresholds for [Strong Buy, Buy, Neutral, Sell].
- [x] Update `NarrativeGenerator` to use the live sentiment matrix instead of placeholders. (AC: 1.2.4)
- [x] Add a unit test to verify sentiment ranking and lift calculation. (AC: 1.2.2)

## Dev Notes

- **Performance**: Auditing 50+ strategies is optimized with a 30-draw window for the narrative report.
- **Hibernation**: Fixed a threshold (-10% lift) to trigger mandatory hibernation.
- **Ensemble Input**: The sentiment matrix now directly influences the weights used in the `VotingEnsemble`.

### Project Structure Notes

- **Module**: `engine/modules/decision_matrix.py`
- **Tiers**: Now includes Deep Learning and Esoteric models in the audit.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#V. User-Driven Narrative & Optimization]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2: Strategic Sentiment Matrix]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Verified `PruningMetrics` integration with the new v10.0 sentiment thresholds.

### Completion Notes List

- ✅ Refined `get_full_strategy_matrix` to include all 4 tiers of strategies.
- ✅ Integrated live strategy signals into the `NarrativeGenerator` report.
- ✅ Added comprehensive unit tests for sentiment labeling and matrix generation.

### File List

- `engine/modules/decision_matrix.py` (MODIFIED)
- `engine/modules/narrative.py` (MODIFIED)
- `tests/test_decision_matrix.py` (NEW)
