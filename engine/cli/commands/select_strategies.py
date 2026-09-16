"""
Select-Strategies Command 🗳️
=============================
Computes and persists a per-game "active roster" of strategies from
empirical evidence (calibration lift, with a live pruning-audit fallback
for uncalibrated strategies), so that `lottery forecast --strategies roster`
and `lottery rank-numbers --strategies roster` can run ensembles that
automatically exclude strategies with no demonstrated edge over random.

Policy:      docs/wayfinder/decisions/003-policy-thresholds-decision.md (MDR-003)
Data model:  docs/wayfinder/decisions/001-roster-data-model-decision.md (MDR-001)

Example
-------
  lottery select-strategies br/lotofacil
  lottery select-strategies br/lotofacil --strategies all --min-lift 1.05
  lottery select-strategies br/lotofacil --pin moon_phase --exclude transformer
  lottery select-strategies br/lotofacil --dry-run
"""

from __future__ import annotations

from datetime import date as _date
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary
from engine.modules.strategy_roster import (
    DEFAULT_MIN_DRAWS,
    DEFAULT_MIN_LIFT,
    RosterResult,
    compute_roster,
    save_roster,
)

console = Console()


def select_strategies(
    lottery: str,
    strategies: str = "all",
    min_lift: float = DEFAULT_MIN_LIFT,
    window: int = DEFAULT_MIN_DRAWS,
    pin: Optional[str] = None,
    exclude: Optional[str] = None,
    dry_run: bool = False,
    export_md: Optional[str] = None,
) -> None:
    """🗳️ Build the empirically-active strategy roster for a game."""
    print_command_summary("select-strategies", lottery, strategies=strategies, min_lift=min_lift)

    adapter = get_adapter(lottery)

    if strategies.strip().lower() == "all":
        from engine.strategies import STRATEGY_REGISTRY
        candidate_names = list(STRATEGY_REGISTRY.keys())
    else:
        from engine.strategies import STRATEGY_PRESETS
        if strategies in STRATEGY_PRESETS:
            candidate_names = list(STRATEGY_PRESETS[strategies])
        else:
            candidate_names = [s.strip() for s in strategies.split(",") if s.strip()]

    pin_list = [s.strip() for s in pin.split(",") if s.strip()] if pin else []
    exclude_list = [s.strip() for s in exclude.split(",") if s.strip()] if exclude else []

    with console.status(f"[bold green]Evaluating {len(candidate_names)} strategies for {lottery}…"):
        result = compute_roster(
            adapter, lottery, candidate_names,
            min_lift=min_lift, window=window,
            pin=pin_list, exclude=exclude_list,
        )

    _print_report(result, min_lift)

    if dry_run:
        console.print("\n[dim]--dry-run: roster not saved.[/dim]")
        return

    save_roster(result)
    console.print(
        f"\n[green]✔[/green] Roster saved to data/strategy_roster.json "
        f"({len(result.active_strategies)} active / {len(result.entries)} evaluated)."
    )
    console.print(f"[dim]Use it with: lottery forecast {lottery} --strategies roster[/dim]")

    if export_md:
        _append_md(export_md, result, min_lift)
        console.print(f"[green]✔[/green] Report appended to {export_md}")


def _sort_key(e):
    return (not e.active, -(e.lift if e.lift is not None else -1.0))


def _print_report(result: RosterResult, min_lift: float) -> None:
    table = Table(title=f"Strategy Roster — {result.game_id}", box=None)
    table.add_column("Strategy", style="bold")
    table.add_column("Tier", style="dim")
    table.add_column("Lift", justify="right")
    table.add_column("Source", style="dim")
    table.add_column("Status")
    table.add_column("Reason", style="dim")

    for e in sorted(result.entries, key=_sort_key):
        lift_str = f"{e.lift:.3f}" if e.lift is not None else "—"
        status = "[green]✓ active[/green]" if e.active else "[red]✗ excluded[/red]"
        table.add_row(e.name, e.tier, lift_str, e.source, status, e.reason)

    console.print()
    console.print(table)
    console.print(Panel(
        f"Active: [bold green]{len(result.active_strategies)}[/bold green]  ·  "
        f"Excluded: [bold red]{len(result.entries) - len(result.active_strategies)}[/bold red]  ·  "
        f"Policy: [cyan]{result.policy_id}[/cyan] (min lift {min_lift:.3f})",
        border_style="cyan",
    ))


def _append_md(path: str, result: RosterResult, min_lift: float) -> None:
    lines = [
        "",
        "---",
        f"## Strategy Roster — {result.game_id} ({_date.today().isoformat()})",
        "",
        f"Policy: `{result.policy_id}` · min lift {min_lift:.3f}",
        "",
        "| Strategy | Tier | Lift | Source | Status | Reason |",
        "|---|---|---|---|---|---|",
    ]
    for e in sorted(result.entries, key=_sort_key):
        lift_str = f"{e.lift:.3f}" if e.lift is not None else "—"
        status = "active" if e.active else "excluded"
        lines.append(f"| {e.name} | {e.tier} | {lift_str} | {e.source} | {status} | {e.reason} |")
    with open(path, "a") as f:
        f.write("\n".join(lines) + "\n")
