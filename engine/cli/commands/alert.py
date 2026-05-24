"""
Alert Command 🚨
================
Condition monitor for cron/pipeline use — outputs NOTHING unless a
significant condition is met. Designed to run daily via cron and only
produce output (e.g., a desktop notification, email trigger, or log entry)
when action is warranted.

Alert conditions (any triggers output)
---------------------------------------
  GO_STRONG     scan verdict GO AND score >= 10/12
  GO_CAUTION    scan verdict GO (any score)
  REGIME_SHIFT  JS divergence >= 0.08 (regime change detected)
  CHI2_ALARM    chi-squared p < 0.05 (fairness anomaly)
  TREND_DROP    confidence fell > 0.05 vs 7-day log mean (from JSONL log)

Exit codes
----------
  0   — alert triggered (output produced)
  1   — no alert (silent)
  2   — error (data unavailable)

Usage
-----
  # Cron: run daily, send notification only if exit code is 0
  lottery alert br/lotofacil --condition go-strong && notify-send "Lottery GO"

  # Check multiple conditions
  lottery alert br/lotofacil --condition go,regime-shift

  # Write alert to file (for log-based notification systems)
  lottery alert br/lotofacil --output /tmp/lottery_alert.json
"""

from __future__ import annotations

import json
import sys
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel

from engine.cli.utils import get_adapter

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DEFAULT_LOG = _DATA_DIR / "draw_log.jsonl"

_ALL_CONDITIONS = {"go-strong", "go", "regime-shift", "chi2-alarm", "trend-drop"}


def alert(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    condition: Annotated[str, typer.Option("--condition", "-c",
        help="Comma-separated: go-strong | go | regime-shift | chi2-alarm | trend-drop | all")] = "go-strong,regime-shift",
    strategy: Annotated[str, typer.Option("--strategy", "-s",
        help="Strategy for scan layers")] = "bayesian",
    output: Annotated[Optional[str], typer.Option("--output", "-o",
        help="Write alert JSON to this file (for pipeline use)")] = None,
    silent: Annotated[bool, typer.Option("--silent/--no-silent",
        help="Suppress terminal output (exit code still set)")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append triggered alerts to this .md file (only written when alerts fire)")] = None,
) -> None:
    """🚨 Condition monitor — outputs only when an alert condition is met.

    Exit code 0 = alert triggered, 1 = no alert, 2 = error.
    Designed for cron: chain with && to act only when conditions are met.

    Example: lottery alert br/lotofacil
             lottery alert br/lotofacil --condition go,regime-shift
             lottery alert br/lotofacil --condition all --silent --output alert.json
             lottery alert br/lotofacil && notify-send "Play today!"
    """

    # Resolve condition set
    if condition.strip().lower() == "all":
        watch = set(_ALL_CONDITIONS)
    else:
        watch = {c.strip().lower() for c in condition.split(",") if c.strip()}
        unknown = watch - _ALL_CONDITIONS
        if unknown:
            console.print(f"[red]Unknown condition(s): {', '.join(unknown)}[/red]")
            console.print(f"Valid: {', '.join(sorted(_ALL_CONDITIONS))} | all")
            raise typer.Exit(2)

    try:
        adapter = get_adapter(lottery)
        df = adapter.fetch()
    except Exception as exc:
        if not silent:
            console.print(f"[red]Error loading {lottery}: {exc}[/red]")
        raise typer.Exit(2)

    rules = adapter.rules
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    triggered: list[dict] = []

    # ── Evaluate conditions ───────────────────────────────────────────────────

    # Regime check (cheap — always compute)
    from engine.cli.commands.scan import _regime_js
    js_val, regime_verdict = _regime_js(df, lo, pool_size, recent=50)

    if "regime-shift" in watch and regime_verdict == "SHIFT":
        triggered.append({
            "condition": "regime-shift",
            "message": f"Regime SHIFT detected — JS={js_val:.5f}. Strategy signals may be mis-calibrated.",
            "js": js_val,
            "verdict": regime_verdict,
        })

    # Chi-squared (cheap)
    if "chi2-alarm" in watch:
        try:
            from engine.modules import frequency
            f_res = frequency.analyze(df.tail(100), rules, top_n=1)
            p = f_res.chi2_p_value
            if p < 0.05:
                triggered.append({
                    "condition": "chi2-alarm",
                    "message": f"Fairness ALARM — chi²p={p:.4f} (distribution non-uniform).",
                    "chi2_p": p,
                })
        except Exception:
            pass

    # GO / GO-STRONG (full scan)
    if "go" in watch or "go-strong" in watch:
        from engine.cli.commands.scan import (
            _rolling_stable_pct, _stress_delta, _solar_kp,
        )
        from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name
        from engine.modules import frequency

        scores: dict[str, int] = {}

        try:
            f_res = frequency.analyze(df.tail(100), rules, top_n=1)
            p = f_res.chi2_p_value
            scores["fairness"] = 2 if p > 0.5 else 1 if p >= 0.05 else 0
        except Exception:
            scores["fairness"] = 1

        stab = _rolling_stable_pct(df, adapter, strategy, 50, n_windows=4)
        scores["stability"] = (2 if stab and stab >= 0.5 else 1 if stab and stab >= 0.25 else
                               0 if stab is not None else 1)

        scores["cluster"] = 1

        today = _date.today()
        moon_name = phase_name(today)
        kp = _solar_kp()
        es = 2 if moon_name in ("New Moon", "Full Moon") else 1
        if kp is not None:
            es = max(0, es - 1) if kp >= 5 else min(2, es + 1) if kp < 3 else es
        scores["esoteric"] = es

        delta = _stress_delta(df, adapter, strategy)
        scores["discrimination"] = (2 if delta and delta > 0.02 else
                                    0 if delta and delta < -0.005 else 1)

        scores["regime"] = 2 if regime_verdict == "STABLE" else 1 if regime_verdict == "DRIFT" else 0

        total = sum(scores.values())
        max_score = len(scores) * 2
        pct = total / max_score

        if pct >= 0.70:
            scan_verdict = "GO"
        elif pct >= 0.40:
            scan_verdict = "CAUTION"
        else:
            scan_verdict = "NO-GO"

        if "go-strong" in watch and scan_verdict == "GO" and total >= 10:
            triggered.append({
                "condition": "go-strong",
                "message": f"GO STRONG — conditions score {total}/{max_score}. High-confidence play opportunity.",
                "scan_score": total,
                "scan_max": max_score,
                "scan_verdict": scan_verdict,
            })
        elif "go" in watch and scan_verdict == "GO" and "go-strong" not in triggered:
            triggered.append({
                "condition": "go",
                "message": f"GO — conditions score {total}/{max_score}.",
                "scan_score": total,
                "scan_max": max_score,
                "scan_verdict": scan_verdict,
            })

    # Trend drop (requires JSONL log)
    if "trend-drop" in watch and _DEFAULT_LOG.exists():
        try:
            records = [
                json.loads(l) for l in _DEFAULT_LOG.read_text().splitlines()
                if l.strip()
            ]
            game_records = [r for r in records if r.get("game") == lottery][-14:]
            conf_vals = [r.get("confidence") for r in game_records if r.get("confidence") is not None]
            if len(conf_vals) >= 4:
                mean7 = float(np.mean(conf_vals[-7:])) if len(conf_vals) >= 7 else float(np.mean(conf_vals))
                last_conf = conf_vals[-1]
                if (mean7 - last_conf) > 0.05:
                    triggered.append({
                        "condition": "trend-drop",
                        "message": f"TREND DROP — confidence fell to {last_conf:.4f} vs 7d-mean {mean7:.4f} (Δ={last_conf - mean7:+.4f}).",
                        "last_confidence": last_conf,
                        "mean7_confidence": mean7,
                        "delta": last_conf - mean7,
                    })
        except Exception:
            pass

    # ── Output ────────────────────────────────────────────────────────────────
    today = _date.today().isoformat()

    if not triggered:
        # No alert — silent exit with code 1
        if not silent:
            console.print(f"[dim]{today} {lottery}: no alert conditions met (watching: {condition})[/dim]")
        raise typer.Exit(1)

    # Alert(s) triggered
    alert_data = {
        "date": today,
        "lottery": lottery,
        "game": rules.name,
        "alerts": triggered,
    }

    if output:
        p = Path(output)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(alert_data, f, indent=2)

    if not silent:
        for t in triggered:
            color = {
                "go-strong": "green",
                "go": "green",
                "regime-shift": "red",
                "chi2-alarm": "red",
                "trend-drop": "yellow",
            }.get(t["condition"], "cyan")

            console.print(Panel(
                f"[bold]{t['message']}[/bold]",
                title=f"🚨 Alert: {t['condition'].upper()} — {rules.name} {today}",
                border_style=color,
            ))

    if export_md:
        _append_md_alert(export_md, lottery, rules.name, today, triggered)
        if not silent:
            console.print(f"[green]✔ Alert appended to {export_md}[/green]")

    # Exit 0 = alert triggered
    raise typer.Exit(0)


def _append_md_alert(
    path: str, lottery: str, game_name: str,
    today: str, triggered: list[dict],
) -> None:
    conditions = ", ".join(t["condition"] for t in triggered)
    rows = ""
    for t in triggered:
        rows += f"| {t['condition']} | {t['message']} |\n"

    content = f"""
---
type: diagnostic
subtype: alert
date: {today}
game: {lottery}
game_name: {game_name}
alerts_count: {len(triggered)}
conditions_triggered: "{conditions}"
tags: [prediction-engine, alert, go-no-go, pattern-log]
---

## Alert: {game_name} ({today})

**{len(triggered)} condition(s) triggered:** {conditions}

| Condition | Message |
|-----------|---------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
