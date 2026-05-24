# Story 5.1: Game-Theoretic Expected Value Model

Status: done

## Story

As a **Strategic Custodian**,
I want to identify combinations that maximize the "Advantage Principle" based on historical structural ratios,
So that my ticket selections are grounded in game-theoretic value rather than just frequency.

## Acceptance Criteria

1. **Port EV Logic**: Port the core valuation logic from `LottoProphet/expected_value_model.py` into a new modular strategy: `engine/strategies/statistical/expected_value.py`. (AC: 5.1.1)
2. **Advantage Metrics**: The strategy must calculate and weight the following structural value patterns:
    - `even_odd_ratio`: Historical frequency of parity distributions.
    - `high_low_ratio`: Historical frequency of magnitude distributions.
    - `sum_range`: Probabilistic value of ticket sums (binned by 10).
    - `span_range`: Probabilistic value of the difference between highest and lowest numbers (binned by 5).
    - `sequence_pattern`: Value of consecutive number strings. (AC: 5.1.2)
3. **Adaptive Weighting**: Implement the `_calculate_combination_weights` logic to adjust number probabilities based on recent draw patterns (e.g., boosting odd numbers if they are currently under-represented). (AC: 5.1.3)
4. **Deterministic Normalization**: The final combination score must be normalized to a [0.0, 1.0] range to integrate with the multi-strategy ensemble. (AC: 5.1.4)
5. **V11 Parity**: Ensure the strategy respects `rules.number_range` and supports the `temperature` parameter for sampling randomness. (AC: 5.1.5)

## Tasks / Subtasks

- [x] Create `engine/strategies/statistical/expected_value.py`.
- [x] Implement the `ExpectedValueStrategy` class inheriting from `BaseStrategy`.
- [x] Port the `_calculate_combinations_value` logic to build the historical value dictionary.
- [x] Implement the `score()` method that blends individual number probabilities with the "Advantage Principle" weights.
- [x] Integrate recency bias weights from the last 5 draws (Story 5.1.3).
- [x] Add unit tests comparing results against the `expected_value_model.py` reference implementation.

## Dev Notes

- **Game Theory**: Successfully ported the "Advantage Principle" from LottoProphet. The strategy now evaluates Parity, Magnitude, Sum, Span, and Sequence patterns.
- **Normalization**: All scores are globally normalized to [0.0, 1.0] for v11.1 ensemble compatibility.
- **Adaptive Weighting**: Implemented recency bias and even/odd deficit checking to adjust number probabilities dynamically.
- **Verification**: Tests passed with 1e-5 precision approximations.

### Project Structure Notes

- **New Strategy**: `engine/strategies/statistical/expected_value.py` (NEW)
- **Registry**: `engine/strategies/__init__.py` (UPDATE)
- **Tests**: `tests/test_strategy_expected_value.py` (NEW)

### References

- [Source: LottoProphet/expected_value_model.py]
- [Source: docs/research/prophet-concepts.md#1. Expected Value Model]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Resolved `defaultdict` and `Counter` usage for historical distribution building.
- Verified WGS84 invariant compatibility with the new EV scoring.

### Completion Notes List

- ✅ Implemented v11.1 Expected Value Strategy.
- ✅ Verified Advantage Principle logic against historical patterns.
- ✅ Synchronized strategy registry for quad-architecture support.

### File List

- `engine/strategies/statistical/expected_value.py` (NEW)
- `engine/strategies/__init__.py` (MODIFIED)
- `tests/test_strategy_expected_value.py` (NEW)
