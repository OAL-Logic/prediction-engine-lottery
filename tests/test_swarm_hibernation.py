import json
import math

import pytest

from engine.swarm import HibernationMonitor, JsonlLedger, SwarmCluster
from engine.swarm.manifold import RewardSignal


class FailingSidecar:
    async def distill_entropy(self, qubits=4, force_fallback=False):
        raise ImportError("pennylane missing")


class RaisingLedger:
    def append(self, event):
        raise OSError("disk full")


def _monitor(tmp_path, **kw):
    path = tmp_path / "ledger.jsonl"
    return HibernationMonitor(ledger=JsonlLedger(path), **kw), path


def _lines(path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines()]


def test_underperformer_hibernated_on_50th(tmp_path):
    m, path = _monitor(tmp_path)
    for _ in range(49):
        assert m.record(7, -0.1) is False
    assert m.record(7, -0.1) is True
    assert m.is_hibernated(7) and m.hibernated_ids() == [7]
    lines = _lines(path)
    assert len(lines) == 1
    ev = lines[0]
    assert ev["event"] == "agent_hibernated" and ev["agent_id"] == 7
    assert ev["window"] == 50 and ev["observations"] == 50
    assert ev["mean_lift"] == pytest.approx(-0.1) and ev["threshold"] == 0.0
    assert ev["timestamp"] and "rationale" in ev and "-0.1000" in ev["rationale"]


def test_partial_window_not_hibernated(tmp_path):
    m, path = _monitor(tmp_path)
    for _ in range(49):
        m.record(1, -0.5)
    assert not m.is_hibernated(1) and _lines(path) == []


def test_good_agent_stays_active(tmp_path):
    m, path = _monitor(tmp_path)
    for _ in range(50):
        m.record(1, 0.2)
    assert not m.is_hibernated(1) and _lines(path) == []


def test_rolling_window_evicts_old_values(tmp_path):
    m, path = _monitor(tmp_path)
    for _ in range(40):
        m.record(1, -0.1)
    for _ in range(60):
        m.record(1, 0.3)
    # at record 50 the window is 40x-0.1 + 10x0.3 -> mean -0.02 < 0: hibernated once
    assert m.is_hibernated(1) and len(_lines(path)) == 1
    # recovery case: window of 60 good draws after bad ones never hibernates
    m2 = HibernationMonitor(ledger=JsonlLedger(tmp_path / "l2.jsonl"))
    for _ in range(30):
        m2.record(2, 0.3)
    for _ in range(10):
        m2.record(2, -0.1)
    for _ in range(60):
        m2.record(2, 0.3)
    assert not m2.is_hibernated(2)
    assert m2._windows[2].maxlen == 50 and len(m2._windows[2]) == 50
    assert all(v == 0.3 for v in m2._windows[2])


def test_already_hibernated_no_second_event(tmp_path):
    m, path = _monitor(tmp_path)
    for _ in range(80):
        m.record(3, -0.2)
    assert len(_lines(path)) == 1


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, None, True, "x", object()])
def test_invalid_lift_ignored(tmp_path, bad):
    m, _ = _monitor(tmp_path)
    assert m.record(1, bad) is False
    assert len(m._windows.get(1, [])) == 0


def test_ledger_failure_still_hibernates():
    m = HibernationMonitor(ledger=RaisingLedger())
    for _ in range(50):
        m.record(1, -1.0)
    assert m.is_hibernated(1)


def test_threshold_configurable(tmp_path):
    m, _ = _monitor(tmp_path, threshold=-0.5)
    for _ in range(50):
        m.record(1, -0.1)
    assert not m.is_hibernated(1)


@pytest.mark.asyncio
async def test_cluster_round_skips_hibernated(tmp_path):
    mon = HibernationMonitor(ledger=JsonlLedger(tmp_path / "l.jsonl"))
    c = SwarmCluster(
        use_ray=False, sidecar_factory=FailingSidecar, hibernation=mon
    )
    await c.start(5)
    pref = [0.0] * 4
    for _ in range(50):
        c.record_lifts(
            [RewardSignal(lift=-0.1, preference=pref, agent_id=a) for a in (1, 3)]
            + [RewardSignal(lift=0.2, preference=pref, agent_id=a) for a in (0, 2, 4)]
        )
    envs = await c.run_round()
    assert len(envs) == 3
    h = c.health()
    assert h["active_agents"] == 3 and h["hibernated_agents"] == 2
    assert len(_lines(tmp_path / "l.jsonl")) == 2
    await c.shutdown()


@pytest.mark.asyncio
async def test_scale_down_up_keeps_ids_aligned(tmp_path):
    mon = HibernationMonitor(ledger=JsonlLedger(tmp_path / "l.jsonl"))
    c = SwarmCluster(use_ray=False, sidecar_factory=FailingSidecar, hibernation=mon)
    await c.start(4)
    for _ in range(50):
        mon.record(1, -0.1)
    assert mon.is_hibernated(1)
    await c.scale_to(2)  # drops ids 3 and 2
    assert c.health()["active_agents"] == 1 and c.health()["hibernated_agents"] == 1
    await c.scale_to(3)  # new agent gets a fresh id (4)
    assert c._agent_ids == [0, 1, 4]
    assert len(await c.run_round()) == 2
    await c.shutdown()


@pytest.mark.asyncio
async def test_ray_path_skips_hibernated(monkeypatch, tmp_path):
    import sys
    import types

    called = []

    class Handle:
        def __init__(self, actor):
            self._a = actor

        def __getattr__(self, name):
            fn = getattr(self._a, name)

            def remote(*a, **k):
                called.append(self._a._agent.agent_id)
                return fn(*a, **k)

            return types.SimpleNamespace(remote=remote)

    class Wrapper:
        def __init__(self, cls):
            self._cls = cls

        def remote(self, *a, **k):
            return Handle(self._cls(*a, **k))

    fake = types.ModuleType("ray")
    fake.is_initialized = lambda: True
    fake.init = lambda **k: None
    fake.remote = lambda cls: Wrapper(cls)
    fake.get = lambda ref: ref
    fake.kill = lambda h: None
    fake.shutdown = lambda: None
    monkeypatch.setitem(sys.modules, "ray", fake)

    mon = HibernationMonitor(ledger=JsonlLedger(tmp_path / "l.jsonl"))
    c = SwarmCluster(use_ray=True, sidecar_factory=FailingSidecar, hibernation=mon)
    await c.start(4)
    assert c.backend == "ray"
    for _ in range(50):
        mon.record(2, -0.1)
    envs = await c.run_round()
    assert len(envs) == 3 and sorted(called) == [0, 1, 3]
    await c.shutdown()
