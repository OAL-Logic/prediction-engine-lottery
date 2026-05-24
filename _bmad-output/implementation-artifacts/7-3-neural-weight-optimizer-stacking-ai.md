# Story 7.3: Neural Weight Optimizer (Stacking AI)

Status: in-progress

## Story

As a **Strategic Player**,
I want a meta-learner that automatically tunes the weights of my sub-models,
so that I can maximize my rolling lift over random.

## Acceptance Criteria

1. **Stacking AI Strategy Support**: The `lottery suggest` command must support the `--strategy stacking_ai` option. (AC: 7.3.1)
2. **Meta-Learning Logic**: The system must implement a meta-learner (e.g., Logistic Regression or a small Neural Net) that learns the optimal combination of sub-model scores. (AC: 7.3.2)
3. **Automated Tuning**: Running `lottery tune` must trigger the stacking optimizer and save the new weight vector. (AC: 7.3.3)
4. **Performance Parity**: The stacking AI must demonstrate a higher rolling capture rate than simple weighted averaging in backtests. (AC: 7.3.4)
5. **Lazy Loading**: Scikit-Learn or PyTorch dependencies must be loaded only when the optimizer is invoked. (AC: 7.3.5)

## Tasks / Subtasks

- [ ] Implement `StackingAIStrategy` in `engine/strategies/ml/stacking_ai.py`. (AC: 7.3.2)
  - [ ] Implement `train_meta_learner` using recent backtest performance data.
  - [ ] Implement `score()` using the trained meta-model.
- [ ] Integrate stacking weights with the `synapse` ensemble. (AC: 7.3.1)
- [ ] Implement `lottery tune` command interface. (AC: 7.3.3)
- [ ] Add a backtest benchmark to compare Stacking vs. Weighted. (AC: 7.3.4)

## Dev Notes

- **Meta-Data**: The trainer requires a "X" matrix of sub-model predictions and a "y" vector of actual hits.
- **Overfitting Guard**: Use strong regularization (L1/L2) for the meta-learner to avoid chasing noise.
- **Architecture**: A simple Ridge regression or shallow MLP is often sufficient for stacking weights.

### Project Structure Notes

- **Module**: `engine/strategies/ml/stacking_ai.py`
- **Weights**: `data/model_cache/stacking_weights.joblib`

### References

- [Source: docs/research/intelligence-hierarchy.md#2. Machine Learning (The Consensus)]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 7.3: Neural Weight Optimizer (Stacking AI)]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

### File List
