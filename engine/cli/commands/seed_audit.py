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
    target_time: Annotated[Optional[str], typer.Option("--time", "--target-time", help="Scheduled draw time HH:MM (e.g. 20:00) for diurnal/sidereal/orbital ephemeris")] = None,
    wind_kmh: Annotated[Optional[float], typer.Option("--wind-kmh", help="Atmospheric wind / vortex speed override (km/h)")] = None,
    pressure_hpa: Annotated[Optional[float], typer.Option("--pressure-hpa", help="Barometric pressure override (hPa, e.g. 1013.25)")] = None,
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
        seed, env_context = build_environmental_seed(
            coords,
            target_date=target_date,
            target_time=target_time,
            wind_kmh=wind_kmh,
            pressure_hpa=pressure_hpa,
        )
    except Exception as exc:
        console.print(f"[red]✗ Environmental seed unavailable: {exc}[/red]")
        raise typer.Exit(1)

    env = env_context["environmental"]
    ephem_block = ""
    if "celestial_ephemeris" in env_context:
        eph = env_context["celestial_ephemeris"]
        ephem_block = (
            f"Time: [bold]{eph['target_time']}[/bold] ({eph['diurnal_period']})   "
            f"Season: [bold]{eph['season']}[/bold] ({eph['season_progress']:.0%})   "
            f"Moon: [bold]{eph['lunar_phase_name']}[/bold] ({eph['moon_longitude_deg']}°)\n"
            f"Sun Lon: {eph['sun_longitude_deg']}°   Earth Helioc. Lon: {eph['earth_heliocentric_lon_deg']}°   "
            f"Earth-Sun: {eph['earth_sun_distance_au']} AU ({eph['earth_orbital_velocity_kms']} km/s)\n"
            f"Sidereal Time: {eph['local_sidereal_time_deg']}°   "
            f"Vortex/Tornado Index: {eph['vortex_convective_index']:.2f} ({eph['vortex_regime']}, "
            f"wind={eph.get('wind_speed_kmh', 12.0)} km/h, P={eph.get('pressure_hpa', 1013.25)} hPa)\n"
        )
        try:
            from engine.strategies.fun.esoteric_statistical import EsotericStatisticalStrategy
            df_hist = adapter.fetch()
            esot_strat = EsotericStatisticalStrategy(
                full_name="GEMINI ENGINE",
                birth_date="1990-01-01",
                coords_str=f"{coords[0]},{coords[1]}",
                target_date=env_context["target_date"],
                target_time=target_time,
                wind_kmh=wind_kmh,
                pressure_hpa=pressure_hpa,
            )
            scores = esot_strat.score(df_hist, adapter.rules)
            hom = esot_strat._last_context.get("homologous_resonance", {})
            top_scored = [n for n, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:10]]
            if hom:
                ephem_block += (
                    f"Homologous Draws: Orbital={hom.get('orbital_homologues_count', 0)} · "
                    f"Lunar={hom.get('lunar_homologues_count', 0)} · "
                    f"Weekday={hom.get('weekday_homologues_count', 0)}\n"
                    f"Cycle Missing: [bold magenta]{hom.get('cycle_missing_numbers', [])}[/bold magenta]   "
                    f"Top Homologous: [bold green]{hom.get('top_homologous_numbers', [])}[/bold green]\n"
                    f"Top Multi-Domain Scored: [bold cyan]{top_scored}[/bold cyan]\n"
                )
        except Exception:
            pass

    console.print(Panel(
        f"Date: [bold]{env_context['target_date']}[/bold]   Coords: {coords}\n"
        f"Temp: {env['temperature_c']}°C   Precip: {env['precip_mm']}mm   "
        f"Solar Kp: {env['solar_kp']}   Lunar phase: {env['lunar_phase']:.0%}\n"
        f"{ephem_block}"
        f"→ Deterministic seed: [bold yellow]{seed}[/bold yellow]",
        title=f"🌍 Seed Audit · {adapter.rules.name}",
        border_style="cyan",
    ))
    console.print(
        f"[dim]Reproduce with: lottery genetic-wheel {lottery} --seed {seed}  "
        f"or  lottery suggest {lottery} --seed {seed}[/dim]"
    )
    console.print("[dim]The seed changes WHICH valid combination a run lands on — it cannot change win probability.[/dim]")
