"""
Filter Funnel Command 🕳️
========================
Lottery Studio's "Elimination Tracking" equivalent: apply a chain of structural
filters (from the 100+ filter registry in engine.modules.filters — tiers
1-5) to every combination of a candidate number pool, and report how many
combinations survive after each filter, in order. Also doubles as a
catalog browser (`--list-filters`) since nothing else currently surfaces
that registry to a user.
"""

from __future__ import annotations

import itertools
from math import comb
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console

from engine.cli.utils import get_adapter, ui_header, ui_table, Theme
from engine.modules.filters import registry

console = Console()

MAX_COMBINATIONS = 3_000_000


def _parse_numbers(raw: str) -> list[int]:
    return sorted({int(x.strip()) for x in raw.split(",") if x.strip()})


def filter_funnel(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    pool: Annotated[Optional[str], typer.Option("--pool", help="Comma-separated candidate number pool to sweep")] = None,
    filters: Annotated[Optional[str], typer.Option("--filters", help="Comma-separated filter unique_ids, applied in order")] = None,
    list_filters: Annotated[bool, typer.Option("--list-filters", help="List every available filter (tier, id, name) and exit")] = False,
    tier: Annotated[Optional[int], typer.Option("--tier", help="With --list-filters, restrict to a single tier (1-5)")] = None,
) -> None:
    """🕳️ Track how many combinations survive each filter in a chain, tier by tier."""

    if list_filters:
        ui_header("FILTER CATALOG", "engine.modules.filters registry")
        tiers = [tier] if tier else [1, 2, 3, 4, 5]
        for t in tiers:
            entries = sorted(registry.list_by_tier(t), key=lambda f: f.unique_id)
            if not entries:
                continue
            table = ui_table(title=f"Tier {t} ({len(entries)} filters)", columns=["ID", "Name"])
            for f in entries:
                table.add_row(f.unique_id, f.display_name)
            console.print(table)
        return

    if not pool or not filters:
        console.print("[red]✗ --pool and --filters are required (or pass --list-filters to browse the catalog).[/red]")
        raise typer.Exit(1)

    adapter = get_adapter(lottery)
    rules = adapter.rules
    lo, hi = rules.number_range
    pool_numbers = _parse_numbers(pool)
    filter_ids = [f.strip() for f in filters.split(",") if f.strip()]

    if any(not (lo <= n <= hi) for n in pool_numbers):
        console.print(f"[red]✗ Pool numbers must be within {rules.number_range} for {rules.name}.[/red]")
        raise typer.Exit(1)
    if len(pool_numbers) < rules.pick_count:
        console.print(f"[red]✗ Pool needs at least {rules.pick_count} numbers for {rules.name} (got {len(pool_numbers)}).[/red]")
        raise typer.Exit(1)

    total = comb(len(pool_numbers), rules.pick_count)
    if total > MAX_COMBINATIONS:
        console.print(
            f"[red]✗ Pool of {len(pool_numbers)} numbers yields C({len(pool_numbers)},{rules.pick_count}) = "
            f"{total:,} combinations, above the {MAX_COMBINATIONS:,} safety cap. Use a smaller pool.[/red]"
        )
        raise typer.Exit(1)

    combos = np.array(list(itertools.combinations(pool_numbers, rules.pick_count)))

    ui_header("FILTER FUNNEL", f"{rules.name} · pool={len(pool_numbers)} numbers · {total:,} starting combinations")

    survivors = np.ones(combos.shape[0], dtype=bool)
    table = ui_table(title="Elimination funnel", columns=["Stage", "Filter", "Before", "After", "Eliminated", "Eliminated %"])
    table.add_row("0", "[dim](starting pool)[/dim]", "—", f"{total:,}", "—", "—")

    for i, uid in enumerate(filter_ids, start=1):
        f = registry.get(uid)
        before = int(survivors.sum())
        if f is None:
            table.add_row(str(i), f"[red]{uid} (not found)[/red]", f"{before:,}", f"{before:,}", "0", "0.0%")
            continue
        mask = f.apply(combos, rules)
        survivors &= mask
        after = int(survivors.sum())
        eliminated = before - after
        pct = (eliminated / before * 100) if before else 0.0
        style = Theme.WARNING if after == 0 else ""
        table.add_row(str(i), f.display_name, f"{before:,}", f"[{style}]{after:,}[/{style}]" if style else f"{after:,}", f"{eliminated:,}", f"{pct:.1f}%")
        if after == 0:
            break

    console.print(table)
    final = int(survivors.sum())
    console.print(
        f"\n[bold {Theme.SUCCESS if final else Theme.DANGER}]{final:,} / {total:,} combinations "
        f"({final / total * 100:.4f}%) survive the full chain.[/bold {Theme.SUCCESS if final else Theme.DANGER}]"
    )
