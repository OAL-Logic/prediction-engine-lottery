import dataclasses
import sys
import types

import pytest

from engine.swarm import MAX_AGENTS, PQCChannel, PQCChannelError, SwarmCluster
from engine.swarm.agent import ExpertAgent


class FailingSidecar:
    async def distill_entropy(self, qubits=4, force_fallback=False):
        raise ImportError("pennylane missing")


class OkSidecar:
    async def distill_entropy(self, qubits=4, force_fallback=False):
        return {"source": "braket_local", "entropy": [1.0 / 16] * 16}


def _cluster(**kw):
    kw.setdefault("use_ray", False)
    kw.setdefault("sidecar_factory", FailingSidecar)
    return SwarmCluster(**kw)


@pytest.mark.asyncio
async def test_local_spin_up_and_full_cap_round():
    c = _cluster()
    await c.start(MAX_AGENTS)
    assert c.backend == "local"
    envs = await c.run_round()
    assert len(envs) == 1000
    assert c.health()["active_agents"] == 1000
    await c.shutdown()
    assert c.health()["active_agents"] == 0


@pytest.mark.asyncio
async def test_over_cap_rejected():
    c = _cluster()
    with pytest.raises(ValueError):
        await c.start(1001)
    await c.start(5)
    with pytest.raises(ValueError):
        await c.scale_to(1001)
    await c.shutdown()


@pytest.mark.asyncio
async def test_scale_up_and_down():
    c = _cluster()
    await c.start(10)
    await c.scale_to(30)
    assert c.health()["active_agents"] == 30
    await c.scale_to(4)
    assert c.health()["active_agents"] == 4
    assert len(await c.run_round()) == 4
    await c.shutdown()


@pytest.mark.asyncio
async def test_round_distinct_seeds_and_fallback_flag():
    c = _cluster()
    await c.start(20)
    envs = await c.run_round()
    plain = [c.open(e) for e in envs]
    assert len({p["seed"] for p in plain}) == 20
    assert all(p["source"] == "local_simulator" for p in plain)
    await c.shutdown()


@pytest.mark.asyncio
async def test_sidecar_source_kept_when_healthy():
    c = _cluster(sidecar_factory=OkSidecar)
    await c.start(3)
    assert all(c.open(e)["source"] == "braket_local" for e in await c.run_round())
    await c.shutdown()


@pytest.mark.asyncio
async def test_default_sidecar_never_raises():
    c = SwarmCluster(use_ray=False)
    await c.start(3)
    plain = [c.open(e) for e in await c.run_round()]
    assert len(plain) == 3
    await c.shutdown()


class BoomAgent(ExpertAgent):
    async def run_round(self, round_id):
        if self.agent_id % 2 == 0:
            raise RuntimeError("boom")
        return await super().run_round(round_id)


@pytest.mark.asyncio
async def test_failed_agent_excluded_and_counted():
    c = _cluster(agent_cls=BoomAgent)
    await c.start(10)
    envs = await c.run_round()
    assert len(envs) == 5
    assert c.health()["last_round_failed_agents"] == 5
    await c.shutdown()


def test_channel_roundtrip_tamper_replay_inactive():
    ch = PQCChannel()
    env = ch.seal({"a": 1}, "s")
    assert env.headers() == {"X-PQC-Active": "true", "X-PQC-Key-Version": "v1"}
    assert ch.open(env) == {"a": 1}
    with pytest.raises(PQCChannelError):
        ch.open(env)  # replay
    env2 = ch.seal({"a": 2}, "s")
    bad = dataclasses.replace(env2, ciphertext=env2.ciphertext[:-1] + bytes([env2.ciphertext[-1] ^ 1]))
    with pytest.raises(PQCChannelError):
        ch.open(bad)
    assert ch.open(env2) == {"a": 2}  # failed tamper must not burn the counter
    env3 = ch.seal({"a": 3}, "s")
    with pytest.raises(PQCChannelError):
        ch.open(dataclasses.replace(env3, pqc_active=False))
    with pytest.raises(PQCChannelError):
        ch.open(dataclasses.replace(env3, counter=99))  # header tamper
    with pytest.raises(PQCChannelError):
        PQCChannel().open(env3)  # wrong session key


@pytest.mark.asyncio
async def test_health_zero_throughput_before_round():
    c = _cluster()
    await c.start(3)
    h = c.health()
    assert h["samples_per_sec"] == 0.0 and h["active_agents"] == 3
    assert h["worker_memory_mb"] > 0
    await c.run_round()
    assert c.health()["samples_per_sec"] > 0
    await c.shutdown()


@pytest.mark.asyncio
async def test_ray_path_with_fake_module(monkeypatch):
    killed = []
    state = {"init": False}

    class Handle:
        def __init__(self, actor):
            self._a = actor

        def __getattr__(self, name):
            fn = getattr(self._a, name)
            return types.SimpleNamespace(remote=lambda *a, **k: fn(*a, **k))

    class Wrapper:
        def __init__(self, cls):
            self._cls = cls

        def remote(self, *a, **k):
            return Handle(self._cls(*a, **k))

    fake = types.ModuleType("ray")
    fake.is_initialized = lambda: state["init"]
    fake.init = lambda **k: state.update(init=True)
    fake.remote = lambda cls: Wrapper(cls)
    fake.get = lambda ref: ref
    fake.kill = lambda h: killed.append(h)
    fake.shutdown = lambda: state.update(init=False)
    monkeypatch.setitem(sys.modules, "ray", fake)

    c = SwarmCluster(use_ray=True, sidecar_factory=FailingSidecar)
    await c.start(6)
    assert c.backend == "ray"
    envs = await c.run_round()
    assert len(envs) == 6
    await c.scale_to(2)
    assert len(killed) == 4
    await c.shutdown()
    assert state["init"] is False


@pytest.mark.asyncio
async def test_ray_disabled_or_missing_uses_local(monkeypatch):
    monkeypatch.setitem(sys.modules, "ray", None)  # import raises ImportError
    c = SwarmCluster(use_ray=True, sidecar_factory=FailingSidecar)
    await c.start(2)
    assert c.backend == "local"
    await c.shutdown()


def test_swarm_health_cli():
    from typer.testing import CliRunner
    from engine.cli.main import app

    r = CliRunner().invoke(app, ["swarm-health", "--agents", "8"])
    assert r.exit_code == 0, r.output
    assert "Active agents" in r.output and "Samples/sec" in r.output
    row = next(l for l in r.output.splitlines() if "Active agents" in l)
    assert "8" in row and "50" not in row

    bad = CliRunner().invoke(app, ["swarm-health", "--agents", "1001"])
    assert bad.exit_code == 2
    assert "Traceback" not in bad.output


def test_channel_is_picklable_for_ray_actors():
    import pickle

    ch = PQCChannel()
    clone = pickle.loads(pickle.dumps(ch))
    assert ch.open(clone.seal({"x": 1}, "a")) == {"x": 1}


@pytest.mark.asyncio
async def test_bool_agent_count_rejected():
    c = _cluster()
    with pytest.raises(ValueError):
        await c.start(True)


@pytest.mark.asyncio
async def test_malformed_sidecar_output_falls_back():
    class Bad:
        async def distill_entropy(self, qubits=4, force_fallback=False):
            return {"source": "x", "entropy": [0.0] * 16}

    a = ExpertAgent(1, 1, PQCChannel(), Bad)
    assert (await a.sample())["source"] == "local_simulator"
