"""
SwarmCluster: lifecycle for up to 1,000 ExpertAgents.

Backends: Ray actors when ``ray`` is importable and enabled, otherwise an
asyncio local pool. Both return only sealed envelopes.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import time
from typing import Any, Callable, Dict, List, Optional

from engine.swarm.agent import ExpertAgent
from engine.swarm.channel import PQCChannel, PQCChannelError, SealedEnvelope

MAX_AGENTS = 1000  # NFR5


def _import_ray():
    try:
        import ray  # type: ignore

        return ray
    except ImportError:
        return None


def _pulse(message: str, level: str = "INFO") -> None:
    from engine.modules.telemetry import pulse

    pulse(message, level)


class _RayAgentActor:
    """Sync wrapper so a Ray actor can drive the async agent."""

    def __init__(self, agent_id, seed, channel, sidecar_factory, agent_cls):
        self._agent = agent_cls(agent_id, seed, channel, sidecar_factory)

    def run_round(self, round_id: int) -> SealedEnvelope:
        return asyncio.run(self._agent.run_round(round_id))


class SwarmCluster:
    def __init__(
        self,
        use_ray: Optional[bool] = None,
        base_seed: Optional[int] = None,
        channel: Optional[PQCChannel] = None,
        sidecar_factory: Optional[Callable[[], Any]] = None,
        agent_cls: type = ExpertAgent,
    ):
        if use_ray is None:
            use_ray = os.environ.get("SWARM_DISABLE_RAY", "") not in ("1", "true", "True")
        self._want_ray = use_ray
        self._ray = None
        self._owns_ray = False
        self._remote_cls = None
        self.backend = "local"
        self._base_seed = base_seed if base_seed is not None else secrets.randbits(64)
        self._channel = channel or PQCChannel()
        self._sidecar_factory = sidecar_factory
        self._agent_cls = agent_cls
        self._agents: List[Any] = []  # local agents or Ray actor handles
        self._next_id = 0
        self._round = 0
        self._started = False
        self._last_samples = 0
        self._last_duration = 0.0
        self._last_failed = 0

    # ---- lifecycle -------------------------------------------------
    @staticmethod
    def _check(n: int) -> None:
        if isinstance(n, bool) or not isinstance(n, int) or n < 0 or n > MAX_AGENTS:
            raise ValueError(f"agent count must be between 0 and {MAX_AGENTS}, got {n}")

    def _seed_for(self, agent_id: int) -> int:
        digest = hashlib.sha256(f"{self._base_seed}:{agent_id}".encode()).digest()
        return int.from_bytes(digest[:8], "big")

    def _spawn(self):
        agent_id = self._next_id
        self._next_id += 1
        seed = self._seed_for(agent_id)
        if self._ray is not None:
            if self._remote_cls is None:
                self._remote_cls = self._ray.remote(_RayAgentActor)
            return self._remote_cls.remote(
                agent_id, seed, self._channel, self._sidecar_factory, self._agent_cls
            )
        return self._agent_cls(agent_id, seed, self._channel, self._sidecar_factory)

    async def start(self, n: int) -> None:
        self._check(n)
        if self._started:
            raise RuntimeError("cluster already started")
        ray = _import_ray() if self._want_ray else None
        if ray is not None:
            try:
                if not ray.is_initialized():
                    ray.init(ignore_reinit_error=True, include_dashboard=False)
                    self._owns_ray = True
                self._ray = ray
                self.backend = "ray"
            except Exception:
                self._ray = None
                self.backend = "local"
        self._started = True
        _pulse(f"Swarm starting: {n} agents on {self.backend} backend", "INFO")
        await self.scale_to(n)

    async def scale_to(self, n: int) -> None:
        self._check(n)
        while len(self._agents) < n:
            self._agents.append(self._spawn())
        while len(self._agents) > n:
            victim = self._agents.pop()
            if self._ray is not None:
                try:
                    self._ray.kill(victim)
                except Exception:
                    pass
        _pulse(f"Swarm scaled to {len(self._agents)} agents", "INFO")

    async def shutdown(self) -> None:
        await self.scale_to(0)
        if self._ray is not None:
            if self._owns_ray:
                try:
                    self._ray.shutdown()
                except Exception:
                    pass
            self._ray = None
            self._remote_cls = None
            self._owns_ray = False
        self._started = False
        _pulse("Swarm shut down", "INFO")

    # ---- rounds ----------------------------------------------------
    async def run_round(self) -> List[SealedEnvelope]:
        self._round += 1
        round_id = self._round
        start = time.perf_counter()
        if self._ray is not None:
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(None, self._ray_collect, round_id)
        else:
            raw = await asyncio.gather(
                *(a.run_round(round_id) for a in self._agents), return_exceptions=True
            )
        envelopes: List[SealedEnvelope] = []
        failed = 0
        for item in raw:
            if isinstance(item, SealedEnvelope):
                envelopes.append(item)
            else:
                failed += 1
        self._last_duration = time.perf_counter() - start
        self._last_samples = len(envelopes)
        self._last_failed = failed
        _pulse(
            f"Swarm round {round_id}: {len(envelopes)} trajectories, {failed} failed agents",
            "WARN" if failed else "SUCCESS",
        )
        return envelopes

    def _ray_collect(self, round_id: int) -> List[Any]:
        refs = [a.run_round.remote(round_id) for a in list(self._agents)]
        out: List[Any] = []
        for ref in refs:
            try:
                out.append(self._ray.get(ref))
            except Exception as exc:
                out.append(exc)
        return out

    def open(self, envelope: SealedEnvelope) -> Dict[str, Any]:
        """Open a sealed trajectory with the session channel (raises PQCChannelError)."""
        return self._channel.open(envelope)

    # ---- health ----------------------------------------------------
    def health(self) -> Dict[str, Any]:
        try:
            import psutil

            memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
        except Exception:
            memory_mb = 0.0
        throughput = (
            self._last_samples / self._last_duration
            if self._last_duration > 0 and self._last_samples
            else 0.0
        )
        snapshot = {
            "backend": self.backend,
            "active_agents": len(self._agents),
            "worker_memory_mb": round(memory_mb, 1),
            "samples_per_sec": round(throughput, 1),
            "rounds": self._round,
            "last_round_failed_agents": self._last_failed,
            "pqc_active": True,
            "pqc_key_version": self._channel.key_version,
        }
        _pulse(
            f"Swarm health: {snapshot['active_agents']} agents, "
            f"{snapshot['worker_memory_mb']} MB, {snapshot['samples_per_sec']} samples/s",
            "INFO",
        )
        return snapshot
