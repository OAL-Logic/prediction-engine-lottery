"""ExpertAgent: one swarm member with its own seed, RNG and sidecar."""

from __future__ import annotations

import random
from typing import Any, Callable, Dict, Optional

from engine.swarm.channel import PQCChannel, SealedEnvelope


def _default_sidecar():
    from engine.modules.cosmic import QuantumSidecar

    return QuantumSidecar()


class ExpertAgent:
    def __init__(
        self,
        agent_id: int,
        seed: int,
        channel: PQCChannel,
        sidecar_factory: Optional[Callable[[], Any]] = None,
        qubits: int = 4,
    ):
        self.agent_id = agent_id
        self.seed = seed
        self.qubits = qubits
        self._channel = channel
        self._rng = random.Random(seed)  # private RNG, never shared
        self._sidecar = (sidecar_factory or _default_sidecar)()  # private sidecar
        self.samples_taken = 0

    @property
    def sender(self) -> str:
        return f"agent-{self.agent_id}"

    def _draw(self, probs) -> int:
        return self._rng.choices(range(len(probs)), weights=probs, k=1)[0]

    async def sample(self) -> Dict[str, Any]:
        """Sample from the sidecar; on any failure fall back to a local simulator."""
        try:
            result = await self._sidecar.distill_entropy(qubits=self.qubits)
            probs = result["entropy"]
            source = result.get("source", "sidecar")
            outcome = self._draw(probs)
        except Exception:
            probs = [1.0 / (2**self.qubits)] * (2**self.qubits)
            source = "local_simulator"
            outcome = self._draw(probs)
        self.samples_taken += 1
        return {
            "agent_id": self.agent_id,
            "seed": self.seed,
            "source": source,
            "qubits": self.qubits,
            "outcome": outcome,
        }

    async def run_round(self, round_id: int) -> SealedEnvelope:
        """Sample and return the trajectory only as a sealed envelope."""
        sample = await self.sample()
        sample["round"] = round_id
        return self._channel.seal(sample, self.sender)
