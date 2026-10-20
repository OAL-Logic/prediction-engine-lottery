"""
Filter Assistant Command 🧙‍♂️
=============================
Lottery Studio's "Assistant Filter" wizard equivalent: a guided, tier-by-tier
walk through the filter registry (rather than requiring you to already
know unique_ids), ending in the same elimination-funnel report as
`filter-funnel` — and an offer to save the resulting recipe as a
`profile` for instant replay later.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from engine.cli.utils import get_adapter, ui_header, ui_table
from engine.modules.filters import registry

console = Console()


def filter_assistant(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
) -> None:
    """🧙‍♂️ Guided, tier-by-tier filter picker ending in an elimination-funnel report."""

    adapter = get_adapter(lottery)
    rules = adapter.rules

    ui_header("FILTER ASSISTANT", f"{rules.name} · pick filters tier by tier")
    console.print("[dim]For each tier, enter the IDs you want (comma-separated), or leave blank to skip the tier.[/dim]\n")

    chosen: list[str] = []
    for t in range(1, 6):
        entries = sorted(registry.list_by_tier(t), key=lambda f: f.unique_id)
        if not entries:
            continue
        table = ui_table(title=f"Tier {t} ({len(entries)} filters)", columns=["ID", "Name"])
        for f in entries:
            table.add_row(f.unique_id, f.display_name)
        console.print(table)

        picked = Prompt.ask(f"Tier {t} — filter IDs to include", default="")
        for uid in [x.strip() for x in picked.split(",") if x.strip()]:
            if registry.get(uid) is not None:
                chosen.append(uid)
            else:
                console.print(f"[yellow]⚠ Unknown filter id '{uid}', skipping.[/yellow]")

    if not chosen:
        console.print("[yellow]No filters selected — nothing to run.[/yellow]")
        raise typer.Exit(0)

    lo, hi = rules.number_range
    pool_str = Prompt.ask(f"\nCandidate pool (comma-separated numbers, within {rules.number_range})")
    pool = sorted({int(x.strip()) for x in pool_str.split(",") if x.strip()})
    if any(not (lo <= n <= hi) for n in pool) or len(pool) < rules.pick_count:
        console.print(f"[red]✗ Pool must have at least {rules.pick_count} numbers, all within {rules.number_range}.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Selected filters:[/bold] {chosen}")

    from engine.cli.commands.filter_funnel import filter_funnel as run_funnel
    run_funnel(lottery, pool=",".join(map(str, pool)), filters=",".join(chosen), list_filters=False, tier=None)

    if Confirm.ask("\nSave this filter set as a named profile for later?", default=False):
        name = Prompt.ask("Profile name")
        from engine.cli.commands.profile import save as save_profile
        command = f"filter-funnel {lottery} --pool {','.join(map(str, pool))} --filters {','.join(chosen)}"
        save_profile(name, command, description="Saved from filter-assistant")
