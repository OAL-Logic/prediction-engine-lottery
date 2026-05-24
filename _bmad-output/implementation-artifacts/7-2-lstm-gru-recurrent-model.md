# Story 7.2: LSTM/GRU Recurrent Model

Status: done

## Story

As a **Chaos Researcher**,
I want to use recurrent units to capture the "Memory" of the lottery machine,
so that I can predict the next state based on temporal flow.

## Acceptance Criteria

1. **LSTM/GRU Strategy Support**: The `lottery suggest` command must support the `--strategy lstm` and `--strategy gru` options. (AC: 7.2.1) [x]
2. **Temporal Pattern Recognition**: The model must use LSTM or GRU architectures to capture dependencies over a sequence of historical draws. (AC: 7.2.2) [x]
3. **Forensic Caching**: The system must save and load trained models from `data/model_cache/` using a hash based on the draw history and hyperparameters. (AC: 7.2.3) [x]
4. **Strict Lazy Loading**: PyTorch (`torch`) must be imported only when the LSTM/GRU strategy is actually invoked. (AC: 7.2.4) [x]
5. **Hyperparameter Control**: Users can specify the architecture type (LSTM vs GRU) and hidden layer dimensions via strategy arguments. (AC: 7.2.5) [x]

## Tasks / Subtasks

- [x] Implement `LSTMStrategy` and `GRUStrategy` in `engine/strategies/deep/lstm_gru.py`. (AC: 7.2.2)
  - [x] Define the recurrent architecture (LSTM/GRU layers, Linear output head).
  - [x] Implement the `score()` method with sequence-to-one mapping.
- [x] Implement forensic caching for recurrent models. (AC: 7.2.3)
  - [x] Ensure cache keys distinguish between LSTM and GRU.
- [x] Ensure strict lazy loading of `torch` in the new module. (AC: 7.2.4)
- [x] Add unit tests for both LSTM and GRU scoring logic. (AC: 7.2.1)

## Dev Notes

- **Architecture**: Implemented a unified `_RecurrentModel` class supporting both `nn.LSTM` and `nn.GRU` cells.
- **Lazy Loading**: Leveraged the `_get_model_classes()` deferred definition pattern to ensure zero `torch` overhead on module import.
- **Caching**: Models are stored in `data/model_cache/` with prefixes `lstm_` and `gru_` respectively.

### Project Structure Notes

- **Module**: `engine/strategies/deep/lstm_gru.py`
- **Cache**: `data/model_cache/lstm_*.pt`, `data/model_cache/gru_*.pt`

### References

- [Source: docs/research/intelligence-hierarchy.md#3. Deep Learning (The Sequential)]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic 7: Deep Learning Predictive Tier (The Sequential)]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Verified `torch` isolation in `tests/test_strategy_recurrent.py`.
- Successfully validated both LSTM and GRU cell types in scoring tests.

### Completion Notes List

- ✅ Implemented dual Recurrent tiers (LSTM and GRU).
- ✅ Integrated with forensic caching and lazy loading invariants.
- ✅ Verified with comprehensive unit tests.

### File List

- `engine/strategies/deep/lstm_gru.py` (NEW/MODIFIED)
- `tests/test_strategy_recurrent.py` (NEW)
