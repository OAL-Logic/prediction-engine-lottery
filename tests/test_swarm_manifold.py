import json
import math

import pytest

from engine.swarm import RewardSignal, RiemannianState, SwarmCluster
from engine.swarm import cluster as cluster_mod

P = [0.7, 0.1, 0.1, 0.1]


def _sig(lift=1.0, pref=P):
    return RewardSignal(lift=lift, preference=pref)


def test_monotone_convergence_1000_agents():
    s = RiemannianState(lr=0.5)
    signals = [_sig(1.0 + (i % 5) * 0.1) for i in range(1000)]
    prev = s.distance_to(P)
    for _ in range(6):
        out = s.evolve(signals)
        d = s.distance_to(P)
        assert d < prev
        prev = d
        assert math.isclose(sum(out["weights"].values()), 1.0, abs_tol=1e-9)
        assert all(w >= 0 for w in out["weights"].values())
    assert s.epoch == 6


def test_negative_lift_pushes_away():
    s = RiemannianState()
    before = s.distance_to(P)
    s.evolve([_sig(-1.0)])
    assert s.distance_to(P) > before


def test_empty_and_zero_lift_unchanged():
    s = RiemannianState()
    w = s.weights()
    assert s.evolve([])["applied"] == 0
    assert s.evolve([_sig(0.0)])["applied"] == 0
    assert s.weights() == w and s.epoch == 0


def test_invalid_signals_rejected():
    s = RiemannianState()
    bad = [
        _sig(1.0, [0.5, 0.5, 0.0]),
        _sig(1.0, [-0.1, 0.5, 0.3, 0.3]),
        _sig(1.0, [float("nan"), 0.5, 0.3, 0.2]),
        _sig(float("inf")),
        _sig(float("nan")),
        _sig(1.0, [0, 0, 0, 0]),
        object(),
    ]
    out = s.evolve(bad + [_sig(1.0)])
    assert out["rejected"] == len(bad)
    assert out["applied"] == 1


def test_degenerate_tangent_unchanged():
    s = RiemannianState()
    w = s.weights()
    out = s.evolve([_sig(1.0, [0.25] * 4)])  # already at the point
    assert out["applied"] == 0 and s.weights() == w and s.epoch == 0


def test_deterministic():
    sigs = [_sig(1.0), _sig(-0.4, [0.1, 0.1, 0.1, 0.7])]
    a, b = RiemannianState(), RiemannianState()
    assert a.evolve(sigs) == b.evolve(sigs)


def test_cluster_pulses_manifold_state(monkeypatch):
    msgs = []
    monkeypatch.setattr(cluster_mod, "_pulse", lambda m, level="INFO": msgs.append(m))
    c = SwarmCluster(use_ray=False)
    c.evolve([_sig()])
    pulses = [m for m in msgs if m.startswith("MANIFOLD_STATE ")]
    assert len(pulses) == 1
    payload = json.loads(pulses[0][len("MANIFOLD_STATE "):])
    assert set(payload) == {"epoch", "weights", "distance_to_consensus"}
    assert payload["weights"] == c.manifold.weights()
    c.evolve([])
    assert len([m for m in msgs if m.startswith("MANIFOLD_STATE ")]) == 1


def test_pulse_failure_does_not_break_evolution(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(cluster_mod, "_pulse", boom)
    c = SwarmCluster(use_ray=False)
    assert c.evolve([_sig()])["applied"] == 1
