"""
Pair Graph Export Command 🕸️
============================
Export the number co-occurrence network as a standard graph interchange
file (GraphML or DOT) for external tools (Gephi, Cytoscape, Graphviz).
`pair-analysis`/`synergy-map` print rankings; this hands the whole graph
to something built for graphs.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli.utils import get_adapter

console = Console()


def build_pair_counts(df, draws: Optional[int] = None) -> Counter:
    if draws:
        df = df.tail(draws)
    counts: Counter = Counter()
    for nums in df["numbers"]:
        for a, b in combinations(sorted(nums), 2):
            counts[(a, b)] += 1
    return counts


def to_graphml(counts: Counter, min_count: int) -> str:
    edges = [(a, b, c) for (a, b), c in counts.items() if c >= min_count]
    nodes = sorted({n for a, b, _ in edges for n in (a, b)})
    lines = [
        "<?xml version='1.0' encoding='utf-8'?>",
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="weight" for="edge" attr.name="weight" attr.type="int"/>',
        '  <graph id="G" edgedefault="undirected">',
    ]
    for n in nodes:
        lines.append(f'    <node id="n{n}"/>')
    for a, b, c in edges:
        lines.append(f'    <edge source="n{a}" target="n{b}"><data key="weight">{c}</data></edge>')
    lines += ["  </graph>", "</graphml>"]
    return "\n".join(lines) + "\n"


def to_dot(counts: Counter, min_count: int) -> str:
    edges = [(a, b, c) for (a, b), c in counts.items() if c >= min_count]
    nodes = sorted({n for a, b, _ in edges for n in (a, b)})
    lines = ["graph G {"]
    for n in nodes:
        lines.append(f"  {n};")
    for a, b, c in edges:
        lines.append(f"  {a} -- {b} [weight={c}];")
    lines.append("}")
    return "\n".join(lines) + "\n"


def pair_graph_export(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    draws: Annotated[Optional[int], typer.Option("--draws", "-n", help="Use only the N most recent draws (default: all)")] = None,
    min_count: Annotated[int, typer.Option("--min-count", help="Only include pairs that co-occurred at least this many times")] = 3,
    format: Annotated[str, typer.Option("--format", "-f", help="graphml | dot")] = "graphml",
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Write to this file instead of printing")] = None,
) -> None:
    """🕸️ Export the number co-occurrence network as GraphML or DOT for external graph tools."""

    if format not in ("graphml", "dot"):
        console.print(f"[red]✗ --format must be 'graphml' or 'dot' (got '{format}').[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    counts = build_pair_counts(df, draws)
    text = to_graphml(counts, min_count) if format == "graphml" else to_dot(counts, min_count)

    n_edges = sum(1 for (a, b), c in counts.items() if c >= min_count)
    if output:
        Path(output).write_text(text)
        console.print(f"[green]✓[/green] Wrote {n_edges} edges (min_count={min_count}) to [bold]{output}[/bold] ({format})")
    else:
        console.print(text)
