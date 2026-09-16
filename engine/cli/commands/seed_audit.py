"""
Seed Audit Command 🌍🔍
=======================
Inspect what `--weather-seed` would produce for a given date WITHOUT
running a full `suggest`/`genetic-wheel` generation — useful to preview
tomorrow's seed, or to independently re-verify the seed/environmental
readings behind a past `--weather-seed` run for a specific date.
"""

from __future__ import annotations

from datetime import date as _date
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from engine.cli.utils import get_adapter

console = Console()


def seed_audit(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    date: Annotated[Optional[str], typer.Option("--date", help="Date to audit, YYYY-MM-DD (default: today)")] = None,
) -> None:
    """🌍🔍 Preview the deterministic --weather-seed for a given date, without running a generation."""

    adapter = get_adapter(lottery)
    coords = adapter.get_draw_location() if hasattr(adapter, "get_draw_location") else (-23.5505, -46.6333)

    target_date = None
    if date:
        try:
            target_date = _date.fromisoformat(date)
        except ValueError:
            console.print(f"[red]✗ Invalid --date '{date}'. Expected YYYY-MM-DD.[/red]")
            raise typer.Exit(1)

    from engine.modules.esoteric_pipeline import build_environmental_seed

    try:
        seed, env_context = build_environmental_seed(coords, target_date=target_date)
    except Exception as exc:
        console.print(f"[red]✗ Environmental seed unavailable: {exc}[/red]")
        raise typer.Exit(1)

    env = env_context["environmental"]
    console.print(Panel(
        f"Date: [bold]{env_context['target_date']}[/bold]   Coords: {coords}\n"
        f"Temp: {env['temperature_c']}°C   Precip: {env['precip_mm']}mm   "
        f"Solar Kp: {env['solar_kp']}   Lunar phase: {env['lunar_phase']:.0%}\n"
        f"→ Deterministic seed: [bold yellow]{seed}[/bold yellow]",
        title=f"🌍 Seed Audit · {adapter.rules.name}",
        border_style="cyan",
    ))
    console.print(
        f"[dim]Reproduce with: lottery genetic-wheel {lottery} --seed {seed}  "
        f"or  lottery suggest {lottery} --seed {seed}[/dim]"
    )
    console.print("[dim]The seed changes WHICH valid combination a run lands on — it cannot change win probability.[/dim]")
