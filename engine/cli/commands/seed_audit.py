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
from engine.i18n import resolve_locale, t

console = Console()


def seed_audit(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    date: Annotated[Optional[str], typer.Option("--date", help="Date to audit, YYYY-MM-DD (default: today)")] = None,
    target_time: Annotated[Optional[str], typer.Option("--time", "--target-time", help="Scheduled draw time HH:MM (e.g. 20:00) for diurnal/sidereal/orbital ephemeris")] = None,
    wind_kmh: Annotated[Optional[float], typer.Option("--wind-kmh", help="Atmospheric wind / vortex speed override (km/h)")] = None,
    pressure_hpa: Annotated[Optional[float], typer.Option("--pressure-hpa", help="Barometric pressure override (hPa, e.g. 1013.25)")] = None,
    locale: Annotated[Optional[str], typer.Option("--locale", "-l", help="Language/locale (en, pt_br)")] = None,
) -> None:
    """🌍🔍 Preview the deterministic --weather-seed for a given date, without running a generation."""
    active_loc = resolve_locale(cli_locale=locale, game_id=lottery)

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
        time_lbl = t("seed_audit.time_label", locale=active_loc)
        season_lbl = t("seed_audit.season_label", locale=active_loc)
        moon_lbl = t("seed_audit.moon_label", locale=active_loc)
        sun_lbl = t("seed_audit.sun_label", locale=active_loc)
        earth_lbl = t("seed_audit.earth_label", locale=active_loc)
        earth_sun_lbl = t("seed_audit.earth_sun_label", locale=active_loc)
        sidereal_lbl = t("seed_audit.sidereal_label", locale=active_loc)
        vortex_lbl = t("seed_audit.vortex_label", locale=active_loc)
        ephem_block = (
            f"{time_lbl} [bold]{eph['target_time']}[/bold] ({eph['diurnal_period']})   "
            f"{season_lbl} [bold]{eph['season']}[/bold] ({eph['season_progress']:.0%})   "
            f"{moon_lbl} [bold]{eph['lunar_phase_name']}[/bold] ({eph['moon_longitude_deg']}°)\n"
            f"{sun_lbl} {eph['sun_longitude_deg']}°   {earth_lbl} {eph['earth_heliocentric_lon_deg']}°   "
            f"{earth_sun_lbl} {eph['earth_sun_distance_au']} AU ({eph['earth_orbital_velocity_kms']} km/s)\n"
            f"{sidereal_lbl} {eph['local_sidereal_time_deg']}°   "
            f"{vortex_lbl} {eph['vortex_convective_index']:.2f} ({eph['vortex_regime']}, "
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
                hom_lbl = t("seed_audit.homologous_label", locale=active_loc)
                miss_lbl = t("seed_audit.cycle_missing_label", locale=active_loc)
                top_hom_lbl = t("seed_audit.top_homologous_label", locale=active_loc)
                top_sc_lbl = t("seed_audit.top_scored_label", locale=active_loc)
                ephem_block += (
                    f"{hom_lbl} Orbital={hom.get('orbital_homologues_count', 0)} · "
                    f"Lunar={hom.get('lunar_homologues_count', 0)} · "
                    f"Weekday={hom.get('weekday_homologues_count', 0)}\n"
                    f"{miss_lbl} [bold magenta]{hom.get('cycle_missing_numbers', [])}[/bold magenta]   "
                    f"{top_hom_lbl} [bold green]{hom.get('top_homologous_numbers', [])}[/bold green]\n"
                    f"{top_sc_lbl} [bold cyan]{top_scored}[/bold cyan]\n"
                )
        except Exception:
            pass

    date_lbl = t("seed_audit.date_label", locale=active_loc)
    coords_lbl = t("seed_audit.coords_label", locale=active_loc)
    temp_lbl = t("seed_audit.temp_label", locale=active_loc)
    precip_lbl = t("seed_audit.precip_label", locale=active_loc)
    solar_lbl = t("seed_audit.solar_label", locale=active_loc)
    lunar_lbl = t("seed_audit.lunar_label", locale=active_loc)
    seed_lbl = t("seed_audit.seed_label", locale=active_loc)
    title_lbl = t("seed_audit.panel_title", locale=active_loc)

    console.print(Panel(
        f"{date_lbl} [bold]{env_context['target_date']}[/bold]   {coords_lbl} {coords}\n"
        f"{temp_lbl} {env['temperature_c']}°C   {precip_lbl} {env['precip_mm']}mm   "
        f"{solar_lbl} {env['solar_kp']}   {lunar_lbl} {env['lunar_phase']:.0%}\n"
        f"{ephem_block}"
        f"→ {seed_lbl} [bold yellow]{seed}[/bold yellow]",
        title=f"{title_lbl} · {adapter.rules.name}",
        border_style="cyan",
    ))
    console.print(
        f"[dim]Reproduce with: lottery genetic-wheel {lottery} --seed {seed}  "
        f"or  lottery suggest {lottery} --seed {seed}[/dim]"
    )
    console.print("[dim]The seed changes WHICH valid combination a run lands on — it cannot change win probability.[/dim]")
