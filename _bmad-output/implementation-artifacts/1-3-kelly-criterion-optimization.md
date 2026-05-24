# Story 1.3: Kelly Criterion Optimization CLI

Status: complete

## Story

As a **Strategic Player**,
I want my bet sizes to be mathematically optimized based on the system's signal confidence,
so that I can maximize long-term bankroll growth while minimizing risk.

## Acceptance Criteria

1. **Kelly Option Support**: The `lottery suggest` command must support a `--kelly [BANKROLL]` option. (AC: 1.3.1) [x]
2. **Confidence Integration**: The Kelly calculation must use the `confidence` score returned by the active strategy. (AC: 1.3.2) [x]
3. **Fractional Kelly Display**: The CLI must display the recommended "Fractional Kelly" bet amount and the corresponding number of tickets. (AC: 1.3.3) [x]
4. **Risk Warning**: The system must warn the user if the strategy confidence is below a safety threshold (default=0.2). (AC: 1.3.4) [x]
5. **Obsidian Metadata**: The Kelly recommendation must be included in the `--export-md` payload. (AC: 1.3.5) [x]

## Tasks / Subtasks

- [x] Implement `calculate_kelly_bet` in `engine/modules/risk.py`. (AC: 1.3.2, 1.3.3)
  - [x] Use the formula: $f^* = (p \times b - q) / b$ where $b$ is the odds decimal - 1.
- [x] Update `engine/cli/commands/suggest.py` to add the `--kelly` option. (AC: 1.3.1, 1.3.4)
  - [x] Integrate with the strategy confidence output.
  - [x] Format the output using `rich` panels.
- [x] Add the Kelly result to the `SuggestionResponse` and CLI output. (AC: 1.3.3)
- [x] Add a unit test for the Kelly calculation logic. (AC: 1.3.2)

## Dev Notes

- **Odds Decimal**: Jackpot odds are pulled from `DrawRules`.
- **Fractional Kelly**: Implemented as a Quarter Kelly (0.25) to manage extreme lottery variance.
- **Safety Threshold**: A 0.2 confidence floor triggers a red warning panel.

### Project Structure Notes

- **Module**: `engine/modules/risk.py`
- **Command**: `engine/cli/commands/suggest.py`

### References

- [Source: _bmad-output/planning-artifacts/prd.md#V. User-Driven Narrative & Optimization]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3: Kelly Criterion Optimization CLI]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Fixed `main.py` proxy logic to include the new `kelly` parameter.
- Integrated `risk.py` with `rich.panel` for high-fidelity output.

### Completion Notes List

- ✅ Created a dedicated `risk.py` module for bankroll management.
- ✅ Successfully integrated Kelly Criterion into the golden path `suggest` command.
- ✅ Verified with automated smoke and logic tests.

### File List

- `engine/modules/risk.py` (NEW)
- `engine/cli/commands/suggest.py` (MODIFIED)
- `engine/cli/main.py` (MODIFIED)
- `tests/test_risk.py` (NEW)
- `tests/test_cli_suggest_kelly.py` (NEW)
