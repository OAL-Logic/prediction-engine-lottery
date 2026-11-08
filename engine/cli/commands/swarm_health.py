"""Swarm Health Command: spin up a short-lived swarm, run rounds, show health."""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import ui_header, ui_table
from engine.swarm.cluster import MAX_AGENTS, SwarmCluster

console = Console()


async def _probe(agents: int, rounds: int) -> dict:
    cluster = SwarmCluster()
    await cluster.start(agents)
    try:
        for _ in range(rounds):
            await cluster.run_round()
        return cluster.health()
    finally:
        await cluster.shutdown()


def swarm_health(
    agents: Annotated[int, typer.Option("--agents", "-n", help=f"Agents to spin up (max {MAX_AGENTS})")] = 50,
    rounds: Annotated[int, typer.Option("--rounds", help="Sampling rounds before reading health")] = 1,
) -> None:
    """Swarm cluster health: active agents, worker memory, sampling throughput."""
    if agents < 0 or agents > MAX_AGENTS:
        console.print(f"[red]--agents must be between 0 and {MAX_AGENTS}[/red]")
        raise typer.Exit(code=2)
    ui_header("SWARM HEALTH", f"{agents} agents")
    snap = asyncio.run(_probe(agents, max(rounds, 0)))
    table = ui_table(columns=["Metric", "Value"])
    table.add_row("Backend", snap["backend"])
    table.add_row("Active agents", str(snap["active_agents"]))
    table.add_row("Worker memory (MB)", str(snap["worker_memory_mb"]))
    table.add_row("Samples/sec", str(snap["samples_per_sec"]))
    table.add_row("Rounds", str(snap["rounds"]))
    table.add_row("Failed agents (last round)", str(snap["last_round_failed_agents"]))
    table.add_row("PQC", f"active, key {snap['pqc_key_version']}")
    console.print(table)
