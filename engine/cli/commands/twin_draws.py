"""
Twin Draws Command 👯
=====================
Finds the historical draws that most closely resemble EACH OTHER (as
opposed to `pattern-search`, which compares history against a ticket you
supply). A curiosity report: "which two draws in this game's history were
the most alike?"
"""

from __future__ import annotations

import heapq
from typing import Annotated

import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, Theme

console = Console()


def _bitmask(numbers) -> int:
    m = 0
    for n in numbers:
        m |= 1 << int(n)
    return m


def find_twin_draws(rows: list[tuple], top: int) -> list[tuple[int, int, int]]:
    """
    rows: list of (draw_id, bitmask) tuples, most-recent-last or any order.
    Returns up to `top` (overlap, i, j) triples, largest overlap first,
    using row *indices* into `rows` for i/j.
    """
    n = len(rows)
    heap: list[tuple[int, int, int]] = []  # (overlap, i, j) min-heap of size `top`
    for i in range(n):
        mi = rows[i][1]
        for j in range(i + 1, n):
            overlap = (mi & rows[j][1]).bit_count()
            if len(heap) < top:
                heapq.heappush(heap, (overlap, i, j))
            elif overlap > heap[0][0]:
                heapq.heapreplace(heap, (overlap, i, j))
    heap.sort(reverse=True)
    return heap


def twin_draws(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    top: Annotated[int, typer.Option("--top", help="How many twin pairs to show")] = 10,
    limit: Annotated[int, typer.Option("--limit", help="Scan only the N most recent draws (0 = all history)")] = 1500,
) -> None:
    """👯 Find the pairs of historical draws with the highest number overlap."""

    adapter = get_adapter(lottery)
    df = adapter.fetch()
    if df.empty:
        console.print(f"[red]✗ No cached history for {lottery}. Run `lottery fetch {lottery}` first.[/red]")
        raise typer.Exit(1)

    if limit and len(df) > limit:
        df = df.tail(limit)

    rows = [(int(r["draw_id"]), _bitmask(r["numbers"])) for _, r in df.iterrows()]
    if len(rows) < 2:
        console.print("[yellow]Need at least 2 draws to compare.[/yellow]")
        raise typer.Exit(1)

    with console.status(f"[bold green]Comparing {len(rows)} draws pairwise…"):
        top_pairs = find_twin_draws(rows, top)

    date_by_id = {int(r["draw_id"]): str(r["date"])[:10] for _, r in df.iterrows()}
    numbers_by_id = {int(r["draw_id"]): list(r["numbers"]) for _, r in df.iterrows()}

    ui_header("TWIN DRAWS", f"{adapter.rules.name} · {len(rows)} draws compared pairwise")

    table = ui_table(title=f"Top {len(top_pairs)} most similar draw pairs", columns=["Draw A", "Draw B", "Overlap", "Shared numbers"])
    for overlap, i, j in top_pairs:
        id_a, id_b = rows[i][0], rows[j][0]
        shared = sorted(set(numbers_by_id[id_a]) & set(numbers_by_id[id_b]))
        table.add_row(
            f"{id_a} ({date_by_id[id_a]})",
            f"{id_b} ({date_by_id[id_b]})",
            f"[bold {Theme.SUCCESS}]{overlap}[/bold {Theme.SUCCESS}]",
            str(shared),
        )
    console.print(table)
    console.print("\n[dim]A high historical overlap between two past draws is a coincidence of the dataset, not a pattern that predicts future ones.[/dim]")
