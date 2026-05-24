# Story 5.3: Extended ML Hub (XGBoost/LightGBM/CatBoost)

Status: done

## Story

As a **Data Alchemist**,
I want to use high-performance gradient boosting ensembles to predict lottery numbers,
So that I can achieve superior predictive lift through advanced feature interaction detection.

## Acceptance Criteria

1. **Port ML Hub Logic**: Port the multi-regressor hub from `LottoProphet/ml_models.py` into a new modular strategy: `engine/strategies/ml/regressor_hub.py`. (AC: 5.3.1)
2. **Regressor Integration**: Support the following gradient boosting frameworks with standardized parameter optimization:
    - **XGBoost**: Using the `WrappedXGBoostModel` pattern for DMatrix conversion.
    - **LightGBM**: Integrated with `LGBMRegressor`.
    - **CatBoost**: Optimized for categorical feature handling. (AC: 5.3.2)
3. **Sliding Window Feature Store**: Implement the `prepare_data` logic to extract rolling time-series features (e.g., window size of 10) including frequency, hot/cold status, and gap analysis. (AC: 5.3.3)
4. **V11 Parity**: Ensure the regressor hub integrates with the v11.0 `BaseStrategy` pattern and supports the `train()` interface for model serialization. (AC: 5.3.4)
5. **Model Checkpointing**: Serialize trained models to `data/model_cache/` using the `{model_type}_{timestamp}.pkl` format. (AC: 5.3.5)

## Tasks / Subtasks

- [x] Create `engine/strategies/ml/regressor_hub.py`.
- [x] Implement the `RegressorHubStrategy` class inheriting from `BaseStrategy`.
- [x] Port the feature engineering logic from `data_processing.py`.
- [x] Implement the ensemble voting/averaging logic for the `ensemble` mode.
- [x] Implement the `train()` method with `joblib` serialization.
- [x] Add unit tests verifying feature extraction and model prediction parity with LottoProphet.

## Dev Notes

- **Implementation**: Created the `ml_regressor` strategy which acts as a hub for XGBoost, LightGBM, and CatBoost.
- **Ensemble Logic**: Implemented a "consensus" mode that averages predictions from all three gradient boosting frameworks.
- **Feature Engineering**: Ported the sliding-window pattern to `engine/modules/feature_engineering.py`. Features include rolling frequencies, gaps, and structural stats (mean sum, span).
- **Persistence**: Models are serialized using `joblib` into `data/model_cache/`, following the v11.1 naming convention.
- **Verification**: All 4 unit tests (feature extraction, data preparation, save/load, and scoring) PASSED.

### Project Structure Notes

- **New Strategy**: `engine/strategies/ml/regressor_hub.py` (NEW)
- **Feature Logic**: `engine/modules/feature_engineering.py` (NEW)
- **Registry**: `engine/strategies/__init__.py` (UPDATED)
- **Tests**: `tests/test_strategy_ml_regressor.py` (NEW)

### References

- [Source: LottoProphet/ml_models.py]
- [Source: LottoProphet/data_processing.py]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Fixed `NameError` in `feature_engineering.py` list comprehension.
- Verified `MultiOutputRegressor` wrapper for handling multi-label ticket targets.
- Handled `X does not have valid feature names` warnings by ensuring consistent feature ordering.

### Completion Notes List

- ✅ Implemented Multi-Regressor ML Hub (XGB/LGBM/CAT).
- ✅ Developed sliding-window feature engineering pipeline.
- ✅ Verified ensemble consensus logic with high-performance gradient boosters.

### File List

- `engine/strategies/ml/regressor_hub.py` (NEW)
- `engine/modules/feature_engineering.py` (NEW)
- `engine/strategies/__init__.py` (MODIFIED)
- `pyproject.toml` (MODIFIED)
- `tests/test_strategy_ml_regressor.py` (NEW)
