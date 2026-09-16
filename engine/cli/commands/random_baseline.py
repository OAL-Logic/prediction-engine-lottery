"""
Random Baseline Command 🎲📏
============================
Generates a batch of PURE random (unweighted, no strategy) tickets and
reports their aggregate structural stats — sum, parity, prime count,
decade spread — as an honest empirical control group. Use it to check
whether a strategy's or a real ticket's structural profile (via
batch-grade/ticket-grade) actually differs from what plain randomness
already produces, in the spirit of this engine's chi²-gate honesty
philosophy.
"""

from __future__ import annotations

import random
import statistics
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, decade_spread
from engine.modules.filters import PRIMES

console = Console()
_PRIME_SET = set(int(p) for p in PRIMES)


def generate_random_tickets(pool_lo: int, pool_hi: int, pick_count: int, count: int, seed: Optional[int] = None) -> list[list[int]]:
    rng = random.Random(seed)
    pool = list(range(pool_lo, pool_hi + 1))
    return [sorted(rng.sample(pool, pick_count)) for _ in range(count)]


def summarize(tickets: list[list[int]], lo: int, hi: int) -> dict:
    sums = [sum(t) for t in tickets]
    odd_counts = [sum(1 for n in t if n % 2 == 1) for t in tickets]
    prime_counts = [sum(1 for n in t if n in _PRIME_SET) for t in tickets]
    spreads = [decade_spread(t, lo, hi) for t in tickets]
    return {
        "sum_mean": statistics.mean(sums), "sum_stdev": statistics.pstdev(sums),
        "odd_mean": statistics.mean(odd_counts),
        "prime_mean": statistics.mean(prime_counts),
        "spread_mean": statistics.mean(spreads),
    }


def random_baseline(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    count: Annotated[int, typer.Option("--count", "-n", help="How many random tickets to generate")] = 2000,
    seed: Annotated[Optional[int], typer.Option("--seed", help="RNG seed for a reproducible baseline")] = None,
) -> None:
    """🎲📏 Empirical structural baseline from pure-random tickets — no strategy involved."""

    adapter = get_adapter(lottery)
    rules = adapter.rules
    lo, hi = rules.number_range

    tickets = generate_random_tickets(lo, hi, rules.pick_count, count, seed)
    stats = summarize(tickets, lo, hi)

    ui_header("RANDOM BASELINE", f"{rules.name} · {count:,} pure-random tickets" + (f" · seed={seed}" if seed is not None else ""))

    table = ui_table(columns=["Metric", "Mean", "Notes"])
    table.add_row("Sum", f"{stats['sum_mean']:.1f} ± {stats['sum_stdev']:.1f}", f"theoretical midpoint ≈ {sum(rules.number_range) / 2 * rules.pick_count:.1f}")
    table.add_row("Odd count", f"{stats['odd_mean']:.2f} / {rules.pick_count}", "expect ≈ half")
    table.add_row("Prime count", f"{stats['prime_mean']:.2f} / {rules.pick_count}", "—")
    table.add_row("Decade spread", f"{stats['spread_mean']:.3f}", "0=concentrated, 1=fully spread")
    console.print(table)
    console.print(
        "\n[dim]This is what unweighted random chance produces. Compare a strategy's or a real ticket's "
        "batch-grade/ticket-grade numbers against these means — if they're not meaningfully different, "
        "the structure isn't doing anything a fair coin wouldn't.[/dim]"
    )
