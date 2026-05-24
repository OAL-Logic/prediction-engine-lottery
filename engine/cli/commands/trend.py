"""
Trend Command 📈
================
Reads the persistent JSONL log built by `lottery log` and visualises
multi-week temporal trends in key diagnostic metrics.

Metrics tracked
---------------
  confidence   Strategy confidence over time
  entropy      Score entropy (lower = more concentrated)
  stable       Stability rate (1-week rolling %)
  chi2_p       Chi-squared fairness p-value
  moon_ratio   Lunar cycle position (0–1)
  solar_kp     NOAA K-index (when available)

Alerts (triggered when metric drifts from baseline)
------------------------------------------------------
  confidence_drop    confidence falls > 0.05 below its 7-day mean
  entropy_spike      entropy rises > 0.5 above its 7-day mean
  stability_collapse stable rate drops below 30% on 7-day rolling
  chi2_alarm         chi2_p drops below 0.05 (non-uniform distribution)

Output
------
  ASCII sparkline for each metric + alert panel + 7-day summary table

Example
-------
  lottery trend br/lotofacil
  lottery trend br/lotofacil --metric confidence --days 30
  lottery trend                (all games, all metrics)
"""

from __future__ import annotations

import json
from datetime import date as _date, timedelta
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import print_command_summary

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DEFAULT_LOG = _DATA_DIR / "draw_log.jsonl"

_SPARKS = "▁▂▃▄▅▆▇█"
_METRICS = ["confidence", "entropy", "chi2_p", "moon_ratio", "solar_kp"]


def _sparkline(values: list[float], width: int = 20) -> str:
    if not values:
        return "—" * width
    vals = [v for v in values if v is not None]
    if not vals:
        return "—" * width
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1e-9
    out = []
    for v in values[-width:]:
        if v is None:
            out.append("·")
        else:
            idx = int((v - lo) / span * (len(_SPARKS) - 1))
            out.append(_SPARKS[idx])
    return "".join(out)


def _rolling_mean(vals: list[float | None], window: int = 7) -> list[float | None]:
    result = []
    for i in range(len(vals)):
        window_vals = [v for v in vals[max(0, i - window + 1): i + 1] if v is not None]
        result.append(float(np.mean(window_vals)) if window_vals else None)
    return result


def trend(
    lottery: Annotated[Optional[str], typer.Argument(help="Lottery filter (e.g. br/lotofacil) — omit for all")] = None,
    log_file: Annotated[str, typer.Option("--log", "-l",
        help="JSONL log file path")] = "",
    days: Annotated[int, typer.Option("--days", "-d",
        help="Number of days to show")] = 14,
    metric: Annotated[Optional[str], typer.Option("--metric", "-m",
        help="Single metric to show (confidence|entropy|chi2_p|moon_ratio|solar_kp)")] = None,
    no_alerts: Annotated[bool, typer.Option("--no-alerts",
        help="Suppress alert panel")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append trend report to this .md file")] = None,
) -> None:
    """📈 Visualise multi-week diagnostic trends from the daily log.

    Reads the JSONL log built by `lottery log` and shows sparklines,
    rolling averages, and threshold alerts for key metrics.

    Example: lottery trend br/lotofacil
             lottery trend br/lotofacil --days 30
             lottery trend br/lotofacil --metric confidence
    """
    log_path = Path(log_file) if log_file else _DEFAULT_LOG

    if not log_path.exists():
        console.print(
            f"[yellow]No log at {log_path}.[/yellow] "
            "Run [bold]lottery log <game>[/bold] first to build the log."
        )
        raise typer.Exit(0)

    # Load records
    raw = [json.loads(l) for l in log_path.read_text().splitlines() if l.strip()]

    # Filter by game
    if lottery:
        raw = [r for r in raw if r.get("game") == lottery]

    if not raw:
        console.print(
            f"[yellow]No log entries for '{lottery}'.[/yellow] "
            "Run [bold]lottery log {lottery}[/bold] first."
        )
        raise typer.Exit(0)

    # Filter by date window
    cutoff = (_date.today() - timedelta(days=days)).isoformat()
    records = [r for r in raw if r.get("date", "") >= cutoff]

    if not records:
        console.print(
            f"[yellow]No entries in the last {days} days.[/yellow] "
            f"Showing oldest {min(7, len(raw))} available instead."
        )
        records = raw[-7:]

    game_label = lottery or "all games"
    console.print(Panel(
        f"[bold cyan]{game_label}[/bold cyan]  "
        f"[dim]{len(records)} entries  last {days} days[/dim]",
        title="📈 Diagnostic Trend",
    ))

    # Metrics to show
    show_metrics = [metric] if metric else _METRICS

    # Build series per metric
    dates     = [r.get("date", "?") for r in records]
    series: dict[str, list] = {m: [r.get(m) for r in records] for m in show_metrics}

    # ── Sparkline panel ───────────────────────────────────────────────────────
    spark_table = Table(box=None, padding=(0, 1), show_header=False)
    spark_table.add_column("Metric",    style="bold", width=14)
    spark_table.add_column("Trend",     width=22)
    spark_table.add_column("7d mean",   justify="right", width=9)
    spark_table.add_column("Last",      justify="right", width=9)
    spark_table.add_column("Direction", justify="center", width=8)

    for m in show_metrics:
        vals = series[m]
        numeric = [v for v in vals if v is not None]
        if not numeric:
            spark_table.add_row(m, "—", "—", "—", "—")
            continue

        roll  = _rolling_mean(vals, window=7)
        spark = _sparkline(vals, width=20)
        mean7 = roll[-1]
        last  = next((v for v in reversed(vals) if v is not None), None)

        if mean7 is not None and last is not None:
            diff = last - mean7
            if abs(diff) < 0.002:
                direction = "[dim]→[/dim]"
            elif diff > 0:
                direction = "[green]▲[/green]"
            else:
                direction = "[red]▼[/red]"
        else:
            direction = "—"

        mean_str = f"{mean7:.4f}" if mean7 is not None else "—"
        last_str = f"{last:.4f}" if last is not None else "—"

        spark_table.add_row(m, spark, mean_str, last_str, direction)

    console.print()
    console.print(spark_table)

    # ── Summary table (last 7 entries) ────────────────────────────────────────
    recent7 = records[-7:]
    summary = Table(title="Recent Entries", box=None, header_style="bold cyan", padding=(0, 1))
    summary.add_column("Date")
    summary.add_column("Conf",    justify="right")
    summary.add_column("Entropy", justify="right")
    summary.add_column("Stable",  justify="center")
    summary.add_column("Chi²p",   justify="right")
    summary.add_column("Moon",    justify="center")
    summary.add_column("Kp",      justify="right")

    for r in recent7:
        stab = r.get("stable")
        stab_str = "[green]✓[/green]" if stab else "[red]✗[/red]" if stab is not None else "—"
        summary.add_row(
            r.get("date", "?"),
            f"{r['confidence']:.4f}" if r.get("confidence") is not None else "—",
            f"{r['entropy']:.4f}"    if r.get("entropy")    is not None else "—",
            stab_str,
            f"{r['chi2_p']:.4f}"    if r.get("chi2_p")     is not None else "—",
            r.get("moon_phase", "—")[:10],
            str(r["solar_kp"])       if r.get("solar_kp")   is not None else "—",
        )

    console.print()
    console.print(summary)

    # ── Alert panel ───────────────────────────────────────────────────────────
    alerts: list[str] = []

    if not no_alerts and len(records) >= 3:
        conf_vals  = [r.get("confidence") for r in records]
        entr_vals  = [r.get("entropy")    for r in records]
        chi2_vals  = [r.get("chi2_p")     for r in records]
        stab_flags = [r.get("stable")     for r in records]

        conf_numeric = [v for v in conf_vals if v is not None]
        entr_numeric = [v for v in entr_vals if v is not None]

        if len(conf_numeric) >= 3:
            roll_conf = _rolling_mean(conf_vals, 7)
            last_conf = next((v for v in reversed(conf_vals) if v is not None), None)
            mean_conf = roll_conf[-1]
            if last_conf is not None and mean_conf is not None and (mean_conf - last_conf) > 0.05:
                alerts.append(
                    f"CONFIDENCE DROP — last={last_conf:.4f}  7d-mean={mean_conf:.4f}  "
                    f"Δ={last_conf - mean_conf:+.4f}  (strategy signal weakening)"
                )

        if len(entr_numeric) >= 3:
            roll_entr = _rolling_mean(entr_vals, 7)
            last_entr = next((v for v in reversed(entr_vals) if v is not None), None)
            mean_entr = roll_entr[-1]
            if last_entr is not None and mean_entr is not None and (last_entr - mean_entr) > 0.5:
                alerts.append(
                    f"ENTROPY SPIKE — last={last_entr:.4f}  7d-mean={mean_entr:.4f}  "
                    f"Δ={last_entr - mean_entr:+.4f}  (scores spreading out — less concentration)"
                )

        recent_stab = [v for v in stab_flags[-7:] if v is not None]
        if len(recent_stab) >= 3:
            stab_rate = sum(1 for v in recent_stab if v) / len(recent_stab)
            if stab_rate < 0.30:
                alerts.append(
                    f"STABILITY COLLAPSE — 7d stable rate={stab_rate:.0%}  "
                    "(< 30% of recent windows are stable)"
                )

        recent_chi2 = [v for v in chi2_vals[-3:] if v is not None]
        if recent_chi2 and min(recent_chi2) < 0.05:
            alerts.append(
                f"FAIRNESS ALARM — chi²p={min(recent_chi2):.4f}  "
                "(distribution non-uniform over last 3 log entries)"
            )

        if alerts:
            alert_body = "\n".join(f"  • {a}" for a in alerts)
            console.print()
            console.print(Panel(alert_body, title="⚠ Trend Alerts", border_style="red"))
        else:
            console.print(
                "\n[green]✓ No trend alerts — metrics within normal range.[/green]"
            )

    console.print(f"\n[dim]Log: {log_path}  |  {len(records)} entries shown[/dim]")

    if export_md:
        last_r = records[-1] if records else {}
        _append_md_trend(
            export_md, lottery or "all", days, len(records),
            last_r.get("confidence"), last_r.get("entropy"),
            last_r.get("chi2_p"), alerts,
        )
        console.print(f"[green]✔ Trend report appended to {export_md}[/green]")


def _append_md_trend(
    path: str, game: str, days: int, n_entries: int,
    last_conf: float | None, last_entropy: float | None,
    last_chi2: float | None, alerts: list[str],
) -> None:
    today = _date.today().isoformat()
    alert_lines = "\n".join(f"- {a}" for a in alerts) if alerts else "- none"
    content = f"""
---
type: diagnostic
subtype: trend
date: {today}
game: {game}
days: {days}
entries: {n_entries}
last_confidence: {f"{last_conf:.4f}" if last_conf is not None else "null"}
last_entropy: {f"{last_entropy:.4f}" if last_entropy is not None else "null"}
last_chi2_p: {f"{last_chi2:.4f}" if last_chi2 is not None else "null"}
alerts: {len(alerts)}
tags: [prediction-engine, trend, diagnostic, pattern-log]
---

## Trend Report: {game} ({today})

**Window:** last {days} days  ·  **Entries:** {n_entries}
**Last confidence:** {f"{last_conf:.4f}" if last_conf is not None else "—"}  ·  **Last entropy:** {f"{last_entropy:.4f}" if last_entropy is not None else "—"}

**Alerts ({len(alerts)}):**
{alert_lines}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
