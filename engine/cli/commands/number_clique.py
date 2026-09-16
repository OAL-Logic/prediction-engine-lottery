"""
Number Clique Command 🔗🕸️
==========================
`pair-analysis` finds pairs; `number-clique` extends the same
co-occurrence graph to groups of size k (default 3) where EVERY pair
within the group co-occurred at least --min-pair-count times — a mutual
"clique," not just two numbers that individually pair well with a third.
"""

from __future__ import annotations

from itertools import combinations
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table
from engine.cli.commands.pair_graph_export import build_pair_counts

console = Console()

MAX_CANDIDATE_NODES = 40


def find_cliques(pair_counts, k: int, min_pair_count: int) -> list[tuple[tuple[int, ...], int]]:
    """Returns [(clique_tuple, min_pairwise_count), ...] sorted strongest-first."""
    adjacency: dict[int, set[int]] = {}
    for (a, b), c in pair_counts.items():
        if c >= min_pair_count:
            adjacency.setdefault(a, set()).add(b)
            adjacency.setdefault(b, set()).add(a)

    candidates = sorted(n for n, neighbors in adjacency.items() if len(neighbors) >= k - 1)
    if len(candidates) > MAX_CANDIDATE_NODES:
        raise ValueError(
            f"{len(candidates)} candidate numbers at min-pair-count={min_pair_count}, "
            f"above the safety cap of {MAX_CANDIDATE_NODES}. Raise --min-pair-count."
        )

    results = []
    for combo in combinations(candidates, k):
        pairs = list(combinations(combo, 2))
        if all(b in adjacency.get(a, ()) for a, b in pairs):
            strength = min(pair_counts.get((min(a, b), max(a, b)), 0) for a, b in pairs)
            results.append((combo, strength))

    results.sort(key=lambda r: r[1], reverse=True)
    return results


def number_clique(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    k: Annotated[int, typer.Option("--k", help="Clique size (group of k mutually co-occurring numbers)")] = 3,
    min_pair_count: Annotated[int, typer.Option("--min-pair-count", help="Minimum co-occurrence count required for every pair in the group")] = 5,
    draws: Annotated[Optional[int], typer.Option("--draws", "-n", help="Use only the N most recent draws (default: all)")] = None,
    max_results: Annotated[int, typer.Option("--max-results", help="How many cliques to show")] = 15,
) -> None:
    """🔗🕸️ Find groups of k numbers that ALL mutually co-occur at least --min-pair-count times."""

    if k < 2:
        console.print("[red]✗ --k must be at least 2.[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    pair_counts = build_pair_counts(df, draws)

    try:
        cliques = find_cliques(pair_counts, k, min_pair_count)
    except ValueError as exc:
        console.print(f"[red]✗ {exc}[/red]")
        raise typer.Exit(1)

    ui_header("NUMBER CLIQUE", f"{adapter.rules.name} · k={k} · min-pair-count={min_pair_count}")

    if not cliques:
        console.print(f"[yellow]No group of {k} numbers had every pair co-occur >= {min_pair_count} times.[/yellow]")
        return

    table = ui_table(title=f"{len(cliques)} clique(s) found (showing top {min(max_results, len(cliques))})", columns=["Numbers", "Weakest pair count"])
    for combo, strength in cliques[:max_results]:
        table.add_row(str(list(combo)), str(strength))
    console.print(table)
    console.print(f"\n[dim]A clique is a co-occurrence coincidence of this dataset, not a prediction of future draws.[/dim]")
