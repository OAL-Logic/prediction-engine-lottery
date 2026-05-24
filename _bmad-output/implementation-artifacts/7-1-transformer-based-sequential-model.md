# Story 7.1: Transformer-based Sequential Model

Status: done

## Story

As a **Data Alchemist**,
I want to use attention mechanisms to analyze draw sequences,
so that I can identify non-obvious long-range patterns that statistical models miss.

## Acceptance Criteria

1. **Transformer Strategy Support**: The `lottery suggest` command must support the `--strategy transformer` option. (AC: 7.1.1) [x]
2. **Sequential Pattern Recognition**: The model must use a GPT-style decoder-only Transformer to analyze the last $N$ draws (default=32). (AC: 7.1.2) [x]
3. **Model Caching**: The system must save and load trained models from `data/model_cache/` using a hash based on the draw history and hyperparameters. (AC: 7.1.3) [x]
4. **Sub-Second Inference**: Loading a cached model and generating a score vector must complete in less than 500ms (excluding training). (AC: 7.1.4) [x]
5. **Lazy Loading**: PyTorch (`torch`) must be imported only when the transformer strategy is actually invoked. (AC: 7.1.5) [x]

## Tasks / Subtasks

- [x] Implement `TransformerStrategy` in `engine/strategies/deep/transformer.py`. (AC: 7.1.2)
  - [x] Define `_LotteryTransformer` architecture (Embedding, Causal Masking, Attention layers).
  - [x] Implement the `score()` method with `torch` inference logic.
- [x] Implement the `data/model_cache/` lifecycle management. (AC: 7.1.3)
  - [x] Generate unique cache keys based on `md5(draw_id_sequence)`.
  - [x] Save `.pt` state dicts after training.
- [x] Enforce Lazy Loading patterns in `engine/strategies/deep/__init__.py`. (AC: 7.1.5)
- [x] Add a smoke test to verify inference from a dummy `.pt` file. (AC: 7.1.4)

## Dev Notes

- **Architecture**: GPT-style decoder-only Transformer with causal masking.
- **Lazy Loading**: Implemented via deferred model class definitions and method-scoped imports. Module loading does not trigger `torch` import.
- **Inference Performance**: Sub-second inference verified on local CPU environment.

### Project Structure Notes

- **Module**: `engine/strategies/deep/transformer.py`
- **Cache**: `data/model_cache/*.pt`

### References

- [Source: docs/research/intelligence-hierarchy.md#3. Deep Learning (The Sequential)]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 7.1: Transformer-based Sequential Model]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Fixed `ImportError` by installing `torch` under YOLO mandate.
- Verified lazy loading returns `False` for `torch` in `sys.modules` on module load.
- Validated caching logic with identical score output on re-runs.

### Completion Notes List

- ✅ Implemented state-of-the-art Transformer strategy.
- ✅ Integrated with forensic model cache.
- ✅ Preserved sub-second CLI startup invariants.

### File List

- `engine/strategies/deep/transformer.py` (MODIFIED)
- `tests/test_strategy_transformer.py` (NEW)
