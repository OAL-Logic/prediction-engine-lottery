import numpy as np
import pytest
from engine.strategies import _calibrate_temperature_for_entropy, _weighted_sample


def test_temperature_calibration_reaches_target_entropy():
    # Synthetic logits
    logits = np.array([1.0, 0.8, 0.5, 0.2, 0.1, 0.05, 0.01, 0.0])
    target_h = 1.5

    tau = _calibrate_temperature_for_entropy(logits, target_h, tol=1e-3)
    assert tau > 0

    # Calculate actual Shannon entropy under tau
    scaled = (logits - np.max(logits)) / tau
    exp_s = np.exp(scaled)
    p = exp_s / np.sum(exp_s)
    actual_h = -float(np.sum(p * np.log(np.maximum(p, 1e-12))))

    assert abs(actual_h - target_h) < 1e-2


def test_weighted_sample_with_entropy_target():
    numbers = list(range(1, 11))
    scores = {n: float(n) / 10.0 for n in numbers}

    sampled = _weighted_sample(numbers, scores, k=5, target_entropy=1.8)
    assert len(sampled) == 5
    assert len(set(sampled)) == 5
    assert all(n in numbers for n in sampled)
