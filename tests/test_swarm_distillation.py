import numpy as np
import pytest

from engine.swarm import (
    DistillationError,
    DistillationPipeline,
    NumpyLSTMPolicy,
    signal_fidelity,
)

N = 16
SKEWED = np.array([0.5, 0.2, 0.1, 0.05] + [0.15 / 12] * 12)


class Teacher:
    def __init__(self, dist=None, raw=None, source="fake"):
        self.raw = raw if raw is not None else list(dist)
        self.source = source

    async def distill_entropy(self, qubits=4, force_fallback=False):
        return {"entropy": self.raw, "source": self.source, "fidelity": 0.99}


class FailingTeacher:
    async def distill_entropy(self, qubits=4, force_fallback=False):
        raise RuntimeError("QPU offline")


def _pipe(tmp_path, teacher, **kw):
    return DistillationPipeline(teacher=teacher, cache_dir=tmp_path, **kw)


def test_signal_fidelity_basics():
    assert signal_fidelity(SKEWED, SKEWED) == pytest.approx(1.0)
    assert signal_fidelity([1, 0], [0, 1]) == 0.0


@pytest.mark.asyncio
async def test_happy_path(tmp_path):
    r = await _pipe(tmp_path, Teacher(SKEWED)).run()
    assert r.passed and r.fidelity >= 0.90 and r.latency_p99_ms < 500
    assert r.teacher_source == "fake" and r.epochs == 60
    assert r.cache_path and (tmp_path / "distilled_lstm.npz").exists()


@pytest.mark.asyncio
async def test_uniform_teacher(tmp_path):
    r = await _pipe(tmp_path, Teacher(np.full(N, 1 / N))).run()
    assert r.passed and r.fidelity >= 0.99


@pytest.mark.asyncio
async def test_under_trained_not_cached(tmp_path):
    r = await _pipe(tmp_path, Teacher(SKEWED), epochs=0).run()
    assert r.passed is False and r.fidelity < 0.90
    assert r.cache_path is None and list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
async def test_teacher_failure(tmp_path):
    with pytest.raises(DistillationError, match="teacher failed"):
        await _pipe(tmp_path, FailingTeacher()).run()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw",
    [
        [1.0] * 8,
        [-0.5, 1.5] + [0.0] * 14,
        [float("nan")] + [1 / 15] * 15,
        [0.5] * 16,
    ],
)
async def test_bad_distribution(tmp_path, raw):
    with pytest.raises(DistillationError):
        await _pipe(tmp_path, Teacher(raw=raw)).run()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
async def test_determinism(tmp_path):
    a = await _pipe(tmp_path / "a", Teacher(SKEWED), epochs=10).run()
    b = await _pipe(tmp_path / "b", Teacher(SKEWED), epochs=10).run()
    assert a.fidelity == b.fidelity
    for k in a.policy.params:
        assert np.array_equal(a.policy.params[k], b.policy.params[k])


@pytest.mark.asyncio
async def test_round_trip_and_corrupt(tmp_path):
    r = await _pipe(tmp_path, Teacher(SKEWED)).run()
    loaded = NumpyLSTMPolicy.load(r.cache_path)
    ctx = [1, 2, 3, 4]
    assert np.array_equal(loaded.predict_probs(ctx), r.policy.predict_probs(ctx))
    with pytest.raises(DistillationError):
        NumpyLSTMPolicy.load(tmp_path / "missing.npz")
    bad = tmp_path / "bad.npz"
    bad.write_bytes(b"garbage")
    with pytest.raises(DistillationError):
        NumpyLSTMPolicy.load(bad)


@pytest.mark.asyncio
async def test_progress_pulses(tmp_path, monkeypatch):
    msgs = []
    monkeypatch.setattr(
        "engine.swarm.distillation._pulse", lambda m, level="INFO": msgs.append(m)
    )
    await _pipe(tmp_path, Teacher(SKEWED), epochs=25, report_interval=5).run()
    epoch_msgs = [m for m in msgs if m.startswith("Distillation epoch")]
    assert len(epoch_msgs) == 4  # epochs 5, 10, 15, 20; epoch 25 is covered by the completion pulse
    assert "complete" in msgs[-1]


@pytest.mark.asyncio
async def test_pulse_failure_does_not_abort(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("telemetry down")

    monkeypatch.setattr("engine.modules.telemetry.pulse", boom)
    r = await _pipe(tmp_path, Teacher(SKEWED), epochs=5).run()
    assert r.epochs == 5


def test_gradient_check():
    pol = NumpyLSTMPolicy(4, hidden=5, window=3, seed=1)
    rng = np.random.default_rng(0)
    for k in ("b", "by"):  # non-zero so every gradient path is exercised
        pol.params[k] += rng.normal(0, 0.1, pol.params[k].shape)
    X = np.array([[0, 1, 2], [3, 3, 1], [2, 0, 0]])
    tgt = np.array([0.4, 0.3, 0.2, 0.1])
    _, grads = pol._grads(X, tgt)

    def loss():
        return pol._grads(X, tgt)[0]

    eps = 1e-6
    for name, p in pol.params.items():
        flat = p.reshape(-1)
        for idx in rng.choice(flat.size, size=min(8, flat.size), replace=False):
            orig = flat[idx]
            flat[idx] = orig + eps
            hi = loss()
            flat[idx] = orig - eps
            lo = loss()
            flat[idx] = orig
            num = (hi - lo) / (2 * eps)
            ana = grads[name].reshape(-1)[idx]
            assert abs(num - ana) / max(1e-8, abs(num) + abs(ana)) < 1e-4, (name, idx, num, ana)


@pytest.mark.asyncio
async def test_slow_policy_not_cached(tmp_path):
    r = await _pipe(tmp_path, Teacher(SKEWED), latency_limit_ms=1e-9).run()
    assert r.fidelity >= 0.90
    assert r.passed is False and r.cache_path is None
    assert list(tmp_path.iterdir()) == []
