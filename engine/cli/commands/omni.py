"""
Lottery Omni Generator Command 🎱🌌
===================================
Production-grade, extensible, local-first combinatorial optimization command for
Brazilian lotteries (Mega-Sena, Lotofácil, etc.) and global lotteries.

Integrates:
1. Dual-Core Scoring Architecture (80% Statistical Pipeline + 20% Deterministic Context).
2. Budget-Constrained Combinatorial Wheels (Fechamentos):
   - reduce-coverage (Uniform Reduction)
   - reduce-pool (Universe Reduction)
3. Precomputed DuckDB/SQLite Wheel Cache Integration.
4. Historical Lunar, Orbital & Multi-Metric Correlation Analysis.
5. Surgical Multi-Force Variations (Celeste, Magnética, Quântica, Atrasão, Síntese).
6. Playwright Universal Betting Automation Integration.
7. Drumroll & Immersive Materialization Session.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date as _date, datetime
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.adapters import DrawRules
from engine.cli.utils import get_adapter
from engine.i18n import resolve_locale, t
from engine.modules.dual_core import (
    DEFAULT_TARGET_ISO,
    ContextEngine,
    DualCoreScorer,
    StatisticalPipeline,
)
from engine.modules.storage import storage
from engine.wheels.budget_wheel import CoverageAudit, WheelEngine, WheelResult, WheelTicket

console = Console()

CAIXA_DOWNLOAD_URL = "https://loterias.caixa.gov.br/Paginas/Download-Resultados.aspx"
CAIXA_API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/"


def display_ingestion_guide(game_id: str, active_loc: str = "pt_br") -> None:
    """Displays explicit instructions on how to download, stage, and index official Caixa draws."""
    title = t("omni.help_ingestion_title", locale=active_loc)
    step1 = t("omni.help_ingestion_step1", locale=active_loc)
    step2 = t("omni.help_ingestion_step2", locale=active_loc)
    step3 = t("omni.help_ingestion_step3", locale=active_loc, game=game_id)
    step4 = t("omni.help_ingestion_step4", locale=active_loc, game=game_id)

    guide_text = (
        f"[bold cyan]{title}[/bold cyan]\n\n"
        f"• {step1}\n"
        f"• {step2}\n"
        f"• {step3}\n"
        f"• {step4}\n\n"
        f"[dim]Cache Table: `draws` & `wheel_cache` in DuckDB ({storage.db_path or './data/lottery.db'})[/dim]"
    )
    console.print(Panel(guide_text, border_style="cyan", title="📥 Ingestion Guide"))


def omni(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required], e.g. br/mega-sena, br/lotofacil")],
    budget: Annotated[float, typer.Option("--budget", "-b", help="Total financial budget in BRL (default: 50.00, supports 80.00)")] = 50.0,
    reduction_strategy: Annotated[str, typer.Option("--reduction-strategy", "-r", help="Budget reduction mode: reduce-coverage (Uniform) | reduce-pool (Universe)")] = "reduce-coverage",
    target_date: Annotated[str, typer.Option("--target-date", "-d", help="Target draw date YYYY-MM-DD (default: 2026-10-29)")] = "2026-10-29",
    target_time: Annotated[str, typer.Option("--time", "--target-time", help="Target draw time HH:MM (default: 20:30)")] = "20:30",
    pool_size: Annotated[Optional[int], typer.Option("--pool-size", "-v", help="Candidate pool size v (auto-calculated if omitted)")] = None,
    guarantee: Annotated[Optional[int], typer.Option("--guarantee", "-g", "-t", help="Match guarantee t (e.g. 4 for Mega-Sena, 13 for Lotofácil)")] = None,
    export_json: Annotated[Optional[str], typer.Option("--export", "-o", help="Export combinations and coverage audit to a JSON file")] = None,
    variations: Annotated[bool, typer.Option("--variations", help="Generate the 5 surgical multi-force variations (Celeste, Magnética, Quântica, Atrasão, Síntese)")] = False,
    correlation: Annotated[bool, typer.Option("--correlation", help="Run deep historical 8-phase lunar, orbital and multi-metric correlation analysis")] = False,
    playwright: Annotated[bool, typer.Option("--playwright", help="Launch Playwright universal dispatcher to stage bets in Caixa cart")] = False,
    materialize: Annotated[bool, typer.Option("--materialize", "-m", help="Trigger drumroll & interactive/immersive materialization session")] = False,
    locale: Annotated[Optional[str], typer.Option("--locale", "-l", help="Language/locale (en, pt_br)")] = None,
) -> None:
    """
    🎱🌌 Lottery Omni Generator — Production Dual-Core 80/20 & Combinatorial Wheel Engine.

    Self-Documenting Ingestion Guide:
      1. Download official historical draw results (.csv / .xlsx / .json) directly from Caixa:
         https://loterias.caixa.gov.br/Paginas/Download-Resultados.aspx
      2. Place the downloaded file into the staging directory:
         ./data/history/ (e.g., ./data/history/megasena.csv or ./data/history/lotofacil.json)
      3. Import into high-performance local DuckDB / SQLite storage:
         ./p4lottery import-drawings br/mega-sena ./data/history/megasena.csv
      4. Live incremental fetch is also available:
         ./p4lottery fetch br/mega-sena
    """
    active_loc = resolve_locale(cli_locale=locale, game_id=lottery)

    # 1. Resolve Adapter & Rules
    try:
        adapter = get_adapter(lottery)
    except Exception as exc:
        console.print(f"[bold red]✗ Invalid lottery game '{lottery}': {exc}[/bold red]")
        raise typer.Exit(1)

    rules: DrawRules = adapter.rules

    # 2. Historical Data Validation & Graceful Diagnostics Halt
    try:
        df = adapter.fetch()
    except Exception as exc:
        console.print(f"[bold red]✗ Failed to access historical draw data for '{lottery}': {exc}[/bold red]")
        display_ingestion_guide(lottery, active_loc)
        raise typer.Exit(1)

    if df is None or len(df) == 0:
        err_msg = t("omni.err_no_data", locale=active_loc, game=lottery)
        console.print(f"[bold red]✗ {err_msg}[/bold red]\n")
        display_ingestion_guide(lottery, active_loc)
        raise typer.Exit(1)

    # 3. Context Engine & Deterministic Calculations (20% Weight)
    iso_target = f"{target_date}T{target_time}:00-03:00"
    ctx_engine = ContextEngine(target_iso=iso_target)
    s_ctx = ctx_engine.generate_context_scores(rules)
    astro = ctx_engine.astronomy

    phase_name = (
        "New Moon 🌑" if astro.lunar_phase < 0.125 or astro.lunar_phase >= 0.875
        else "First Quarter 🌓" if astro.lunar_phase < 0.375
        else "Full Moon 🌕" if astro.lunar_phase < 0.625
        else "Last Quarter 🌗"
    )

    ctx_panel = (
        f"[bold cyan]Target Date/Time:[/bold cyan]     {astro.target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"[bold cyan]Lunar Synodic Phase:[/bold cyan]  {astro.lunar_phase:.4f} ({phase_name}, Illumination: {astro.lunar_illumination * 100:.1f}%)\n"
        f"[bold cyan]Solar Declination:[/bold cyan]    {astro.solar_declination_deg:+.2f}° (Day of Year: {astro.day_of_year}/365)\n"
        f"[bold cyan]Seasonal Harmonics:[/bold cyan]   sin={astro.solar_harmonic_sin:+.4f}, cos={astro.solar_harmonic_cos:+.4f}\n"
        f"[bold cyan]Deterministic Mapping:[/bold cyan] SHA-256 Epoch Modulo (Zero PRNG Drift)"
    )
    console.print(Panel(ctx_panel, title=t("omni.context_title", locale=active_loc), border_style="magenta"))

    # 4. Optional: Deep Historical Correlation View
    if correlation:
        console.print(f"\n[bold yellow]{t('omni.correlation_header', locale=active_loc)}[/bold yellow]")
        from engine.modules.esoteric_pipeline import EsotericPipeline
        coords = adapter.get_draw_location() if hasattr(adapter, "get_draw_location") else (-23.5505, -46.6333)
        corr = EsotericPipeline.analyze_historical_correlations(
            df=df,
            rules=rules,
            target_date=target_date,
            target_time=target_time,
            coords=coords,
        )
        lunar_table = Table(title="🌕 8-Phase Historical Lunar Correlation", border_style="cyan")
        lunar_table.add_column("Phase", style="bold")
        lunar_table.add_column("Draws (n)", justify="right")
        lunar_table.add_column("Mean Sum (d)", justify="right")
        lunar_table.add_column("Odd %", justify="right")
        lunar_table.add_column("Primes", justify="right")
        lunar_table.add_column("Top Positive Z Numbers (Z-score / Lift%)")

        for row in corr.get("lunar_phase_table", []):
            top_str = ", ".join(f"{num:02d}(Z={z:+.2f},+{lift:.0f}%)" for num, _, z, lift in row["top_numbers"][:4])
            phase_display = f"★ {row['phase']}" if row.get("is_target") else f"  {row['phase']}"
            lunar_table.add_row(
                phase_display,
                str(row["n"]),
                f"{row['mean_sum']:.1f} ({row['sum_d']:+.2f})",
                f"{row['mean_odd_pct']:.1f}%",
                f"{row['mean_primes']:.2f}",
                top_str,
            )
        console.print(lunar_table)

    # 5. Statistical Pipeline & Dual-Core 80/20 Composite Scoring
    stat_pipe = StatisticalPipeline(history=df, rules=rules)
    s_stat = stat_pipe.compute_stat_scores()
    composite_scorer = DualCoreScorer(stat_scores=s_stat, ctx_scores=s_ctx)
    composite_scores = composite_scorer.compute_composite_scores()

    # 6. Combinatorial Wheel Generation
    wheel_engine = WheelEngine(rules=rules, cache=storage)

    try:
        result = wheel_engine.generate_wheel(
            scores=composite_scores,
            budget=budget,
            pool_size=pool_size,
            guarantee_t=guarantee,
            reduction_strategy=reduction_strategy,
            last_draw=stat_pipe.last_draw,
        )
    except ValueError as exc:
        console.print(f"[bold red]✗ Wheel Generation Error: {exc}[/bold red]")
        raise typer.Exit(1)

    # 7. Tabular Printout of Generated Games
    game_display_name = rules.name.upper()
    t_table = Table(title=t("omni.table_tickets_title", locale=active_loc, game=game_display_name), border_style="green")
    t_table.add_column("Tkt #", justify="center", style="bold cyan")
    t_table.add_column("Numbers", justify="left", style="bold white")
    t_table.add_column("Evens / Odds", justify="center")
    t_table.add_column("Sum", justify="right")
    t_table.add_column("Mean S(n)", justify="right", style="green")

    for tkt in result.tickets:
        nums_str = " ".join(f"{n:02d}" for n in tkt.numbers)
        parity_str = f"{tkt.even_count}E / {tkt.odd_count}O"
        t_table.add_row(
            f"#{tkt.ticket_id:02d}",
            nums_str,
            parity_str,
            str(tkt.total_sum),
            f"{tkt.mean_score:.4f}",
        )
    console.print(t_table)

    # 8. Combinatorial Coverage & Financial Audit Table
    audit: CoverageAudit = result.audit
    a_table = Table(title=t("omni.audit_title", locale=active_loc), border_style="blue")
    a_table.add_column("Metric", style="bold")
    a_table.add_column("Value")

    guar_str = "✅ YES" if audit.is_100_percent_guarantee else "❌ NO (Partial Coverage)"
    active_pool_str = " ".join(f"{n:02d}" for n in audit.pool_numbers)

    a_table.add_row(t("omni.metric_game", locale=active_loc), audit.game)
    a_table.add_row(t("omni.metric_strategy", locale=active_loc), audit.reduction_strategy_used)
    a_table.add_row(t("omni.metric_pool_v", locale=active_loc), f"{audit.total_pool_v} numbers")
    a_table.add_row(t("omni.metric_ticket_k", locale=active_loc), f"{audit.ticket_size_k} numbers")
    a_table.add_row(t("omni.metric_guarantee_t", locale=active_loc), f"Match {audit.guarantee_t} of {audit.drawn_m}")
    a_table.add_row(t("omni.metric_subsets_total", locale=active_loc), f"{audit.total_subsets_to_cover:,}")
    a_table.add_row(t("omni.metric_subsets_covered", locale=active_loc), f"{audit.subsets_covered:,}")
    a_table.add_row(t("omni.metric_coverage_pct", locale=active_loc), f"{audit.coverage_percentage:.2f}%")
    a_table.add_row(t("omni.metric_guarantee_100", locale=active_loc), guar_str)
    a_table.add_row(t("omni.metric_tickets_gen", locale=active_loc), f"{audit.tickets_generated} tickets")
    a_table.add_row(t("omni.metric_ticket_cost", locale=active_loc), f"{audit.currency} {audit.ticket_cost:.2f}")
    a_table.add_row(t("omni.metric_spend_total", locale=active_loc), f"{audit.currency} {audit.total_cost:.2f}")
    a_table.add_row(t("omni.metric_budget_allocated", locale=active_loc), f"{audit.currency} {audit.total_budget:.2f}")
    headroom = max(0.0, audit.total_budget - audit.total_cost)
    a_table.add_row(t("omni.metric_budget_headroom", locale=active_loc), f"{audit.currency} {headroom:.2f}")
    a_table.add_row(t("omni.metric_active_pool", locale=active_loc), active_pool_str)

    console.print(a_table)

    # 9. Optional: Multi-Force Surgical Variations
    if variations:
        console.print(f"\n[bold magenta]{t('omni.variations_header', locale=active_loc)}[/bold magenta]")
        from engine.modules.esoteric_pipeline import EsotericPipeline
        ep = EsotericPipeline()
        t_d = _date.fromisoformat(target_date[:10])
        surg = ep.generate_surgical_variations(
            df=df,
            rules=rules,
            target_date=t_d,
            target_time=target_time,
            locale=active_loc,
        )
        v_table = Table(title="🎯 Multi-Force Surgical Variations (1 Ticket Per Dimension)", border_style="magenta")
        v_table.add_column("Force / Variation", style="bold")
        v_table.add_column("Numbers", style="bold white")
        v_table.add_column("Sum", justify="right")
        v_table.add_column("Score", justify="right", style="green")

        for item in surg.get("variations", []):
            nums_fmt = " - ".join(f"{n:02d}" for n in item["numbers"])
            v_table.add_row(
                item["label"],
                nums_fmt,
                str(sum(item["numbers"])),
                f"{item.get('score', 0.0):.4f}",
            )
        console.print(v_table)

    # 10. JSON Export
    export_payload = {
        "engine": "lottery-omni-generator",
        "game": audit.game,
        "target_date": astro.target_time.isoformat(),
        "astronomical_context": {
            "lunar_phase": round(astro.lunar_phase, 4),
            "lunar_illumination": round(astro.lunar_illumination, 4),
            "solar_declination_deg": round(astro.solar_declination_deg, 2),
            "seasonal_harmonics": {
                "sin": round(astro.solar_harmonic_sin, 4),
                "cos": round(astro.solar_harmonic_cos, 4),
            },
        },
        "coverage_audit": {
            "reduction_strategy": audit.reduction_strategy_used,
            "total_pool_v": audit.total_pool_v,
            "ticket_size_k": audit.ticket_size_k,
            "guarantee_t": audit.guarantee_t,
            "drawn_m": audit.drawn_m,
            "total_subsets": audit.total_subsets_to_cover,
            "subsets_covered": audit.subsets_covered,
            "coverage_percentage": audit.coverage_percentage,
            "is_100_percent_guarantee": audit.is_100_percent_guarantee,
            "unit_cost": audit.ticket_cost,
            "total_cost": audit.total_cost,
            "allocated_budget": audit.total_budget,
            "headroom": headroom,
            "pool_numbers": audit.pool_numbers,
        },
        "tickets": [
            {
                "ticket_id": tkt.ticket_id,
                "numbers": tkt.numbers,
                "even_count": tkt.even_count,
                "odd_count": tkt.odd_count,
                "sum": tkt.total_sum,
                "mean_score": tkt.mean_score,
            }
            for tkt in result.tickets
        ],
    }

    if export_json:
        out_p = Path(export_json)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(export_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"\n[bold green]✓ {t('omni.export_success', locale=active_loc, path=str(out_p))}[/bold green]")

    # 11. Playwright Betting Automation
    if playwright:
        console.print(f"\n[bold cyan]🚀 {t('omni.playwright_dispatched', locale=active_loc, count=len(result.tickets))}[/bold cyan]")
        playwright_script = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "playwright_caixa_universal.py"
        tmp_json = Path(".scratch") / f"omni_{rules.name.lower()}_{target_date}.json"
        tmp_json.parent.mkdir(parents=True, exist_ok=True)
        pacote = [
            {
                "modalidade": "mega-sena" if "mega" in rules.name.lower() else "lotofacil",
                "descricao": f"Omni Generator ({audit.reduction_strategy_used} — Budget {audit.total_budget})",
                "jogos": [tkt.numbers for tkt in result.tickets],
            }
        ]
        tmp_json.write_text(json.dumps(pacote, indent=2, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, str(playwright_script), "--file", str(tmp_json), "--budget", str(budget)]
        if materialize:
            cmd.append("--materialize")
        console.print(f"[dim]Executing: {' '.join(cmd)}[/dim]")
        subprocess.run(cmd)
        return

    # 12. Drumroll & Materialization Session
    if materialize:
        console.print("\n🥁 [bold yellow]Launching Materialization Session...[/bold yellow]")
        from engine.cli.commands.materialize import run_materialize
        run_materialize(
            target_date=target_date,
            target_time=target_time,
            budget=budget,
            interactive=True,
            locale=active_loc,
        )


if __name__ == "__main__":
    app = typer.Typer(add_completion=False)
    app.command(name="omni")(omni)
    app()
