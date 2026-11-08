"""Distributed MARL swarm (Epic 3). Story 3.1: orchestrator, agents, PQC channel."""

from engine.swarm.agent import ExpertAgent
from engine.swarm.channel import PQCChannel, PQCChannelError, SealedEnvelope
from engine.swarm.cluster import MAX_AGENTS, SwarmCluster
from engine.swarm.hibernation import HibernationMonitor, JsonlLedger
from engine.swarm.manifold import RewardSignal, RiemannianState

__all__ = [
    "ExpertAgent",
    "HibernationMonitor",
    "JsonlLedger",
    "MAX_AGENTS",
    "PQCChannel",
    "PQCChannelError",
    "RewardSignal",
    "RiemannianState",
    "SealedEnvelope",
    "SwarmCluster",
]
