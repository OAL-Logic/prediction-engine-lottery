# Story 5.2: Sequence Logic Brain (LSTM-CRF)

Status: done

## Story

As a **Data Alchemist**,
I want to use deep sequence modeling to predict lottery combinations,
So that the generated tickets follow realistic inter-number dependency patterns and global structural constraints.

## Acceptance Criteria

1. **Port LSTM-CRF Model**: Port the `LstmCRFModel` architecture from `LottoProphet/model.py` into a new modular strategy: `engine/strategies/deep/lstm_crf.py`. (AC: 5.2.1)
2. **Global Sequence Normalization**: The model must utilize a **Conditional Random Field (CRF)** layer to model the global dependencies between numbers in a ticket sequence, preventing invalid transitions. (AC: 5.2.2)
3. **Multi-layer Bi-LSTM**: Implement a multi-layer Bidirectional LSTM foundation for extracting high-dimensional temporal features from historical draws. (AC: 5.2.3)
4. **V11 Parity**: Integrate the model with the v11.0 `BaseStrategy` pattern, supporting `history_limit` and `temperature` parameters. (AC: 5.2.4)
5. **GPU Acceleration**: The implementation must support CUDA-based acceleration if a GPU is available, following the `Project Context` rules. (AC: 5.2.5)

## Tasks / Subtasks

- [x] Create `engine/strategies/deep/lstm_crf.py`.
- [x] Implement the `LstmCRFModel` class in PyTorch using `torchcrf`.
- [x] Implement the `LSTMCRFStrategy` class inheriting from `BaseStrategy`.
- [x] Develop the data loading and sequence preparation logic (sliding window of size 10).
- [x] Implement the `train()` method that serializes models to `data/model_cache/`.
- [x] Add unit tests verifying that the model produces valid, sorted sequences of unique numbers.

## Dev Notes

- **Implementation**: Successfully ported the `LstmCRFModel` from LottoProphet. The model uses a Bidirectional LSTM with a CRF layer for global sequence normalization.
- **Data Engineering**: Implemented a sliding-window data loader that converts historical draws into input/label pairs for supervised sequence learning.
- **Persistence**: Added `train()` and `load()` methods that handle model serialization to `data/model_cache/` using the game name as a key.
- **Verification**: Verified the model architecture, training loop, and persistence logic with 4 unit tests.
- **Dependencies**: Added `pytorch-crf` to `pyproject.toml`.

### Project Structure Notes

- **New Strategy**: `engine/strategies/deep/lstm_crf.py` (NEW)
- **Registry**: `engine/strategies/__init__.py` (UPDATED)
- **Tests**: `tests/test_strategy_lstm_crf.py` (NEW)
- **Model Cache**: `data/model_cache/` (NEW)

### References

- [Source: LottoProphet/model.py]
- [Source: docs/research/prophet-concepts.md#2. LSTM-CRF Sequence Modeling]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Handled `DrawRules` attribute mismatch (`lottery_id` vs `name`).
- Resolved `torchcrf` uint8 mask warnings.
- Verified CUDA fallback logic for CPU-only environments.

### Completion Notes List

- ✅ Implemented LSTM-CRF strategy for advanced sequence modeling.
- ✅ Verified model saving/loading lifecycle.
- ✅ Integrated with v11.1 strategy registry.

### File List

- `engine/strategies/deep/lstm_crf.py` (NEW)
- `engine/strategies/__init__.py` (MODIFIED)
- `pyproject.toml` (MODIFIED)
- `tests/test_strategy_lstm_crf.py` (NEW)
- `data/model_cache/` (NEW)
