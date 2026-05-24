"""
Report Command 📄
=================
Executes custom analysis pipelines defined in YAML/JSON configuration files.
Useful for scheduling via cron or systemd.

Two pipeline formats are supported:

Legacy format (backwards-compatible):
  reports:
    - name: Lotofacil Daily
      lottery: br/lotofacil
      strategies: [...]

New steps-based format:
  steps:
    - type: fetch
      lottery: br/lotofacil
    - type: daily
      lottery: br/lotofacil
      quiet: false
      export_md: data/digest.md
    - type: alert
      lottery: br/lotofacil
      condition: go-strong,regime-shift
    - type: scan
      lottery: br/lotofacil
    - type: forecast
      lottery: br/lotofacil
      strategies: fast
      export_md: data/forecast.md
    - type: watchlist-run
      mode: scan
    - type: suggest
      lottery: br/lotofacil
      strategy: bayesian
      count: 1
    - type: narrative
      lottery: br/lotofacil
      persona: "Synapse Architect"
"""

from __future__ import annotations

import os
import sys
import yaml
import json
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Optional

import typer
from rich.console import Console
from rich.rule import Rule

from engine.cli.utils import get_adapter, print_command_summary, load_local_config
from engine.strategies import get_strategy

console = Console()

# ── Step dispatch ─────────────────────────────────────────────────────────────

def _step_fetch(step: dict) -> None:
    lottery = step.get("lottery")
    if not lottery:
        console.print("[yellow]step fetch: missing 'lottery'[/yellow]")
        return
    from engine.cli.commands.fetch import fetch as _fetch
    try:
        _fetch(lottery=lottery)
    except (SystemExit, typer.Exit):
        pass


def _step_daily(step: dict) -> None:
    lottery = step.get("lottery")
    if not lottery:
        console.print("[yellow]step daily: missing 'lottery'[/yellow]")
        return
    from engine.cli.commands.daily import daily as _daily
    try:
        _daily(
            lottery=lottery,
            quiet=step.get("quiet", False),
            export_md=step.get("export_md") or step.get("export-md"),
            jackpot=step.get("jackpot"),
            persona=step.get("persona", "analyst"),
        )
    except (SystemExit, typer.Exit):
        pass


def _step_alert(step: dict) -> bool:
    """Returns True if alert was triggered (exit 0)."""
    lottery = step.get("lottery")
    if not lottery:
        console.print("[yellow]step alert: missing 'lottery'[/yellow]")
        return False
    from engine.cli.commands.alert import alert as _alert
    triggered = False
    try:
        _alert(
            lottery=lottery,
            condition=step.get("condition", "go-strong,regime-shift"),
            strategy=step.get("strategy", "bayesian"),
            output=step.get("output"),
            silent=step.get("silent", False),
        )
        triggered = True
    except typer.Exit as e:
        triggered = (e.exit_code == 0)
    except SystemExit as e:
        code = e.code if hasattr(e, "code") and isinstance(e.code, int) else 1
        triggered = code == 0
    return triggered


def _step_scan(step: dict) -> None:
    lottery = step.get("lottery")
    if not lottery:
        console.print("[yellow]step scan: missing 'lottery'[/yellow]")
        return
    from engine.cli.commands.scan import scan as _scan
    try:
        _scan(
            lottery=lottery,
            strategy=step.get("strategy", "bayesian"),
            window=step.get("window", 50),
            auto_suggest=step.get("suggest", False),
            export_md=step.get("export_md") or step.get("export-md"),
        )
    except (SystemExit, typer.Exit):
        pass


def _step_forecast(step: dict) -> None:
    lottery = step.get("lottery")
    if not lottery:
        console.print("[yellow]step forecast: missing 'lottery'[/yellow]")
        return
    from engine.cli.commands.forecast import forecast as _forecast
    try:
        _forecast(
            lottery=lottery,
            strategies=step.get("strategies", "default"),
            export_md=step.get("export_md") or step.get("export-md"),
        )
    except (SystemExit, typer.Exit):
        pass


def _step_watchlist_run(step: dict) -> None:
    from engine.cli.commands.watchlist import _run_daily, _run_alert, _run_scan, _load
    data = _load()
    games = data.get("games", [])
    if not games:
        console.print("[dim]step watchlist-run: watchlist is empty[/dim]")
        return
    mode = step.get("mode", "scan")
    if mode == "daily":
        _run_daily(games, export_md=step.get("export_md"), jackpot_map={})
    elif mode == "alert":
        try:
            _run_alert(games, condition=step.get("condition", "go-strong,regime-shift"), quiet=step.get("quiet", False))
        except (SystemExit, typer.Exit):
            pass
    else:
        _run_scan(games, quiet=step.get("quiet", False))


def _step_suggest(step: dict, adapter_cache: dict, global_config: dict) -> str:
    """Legacy suggest step — returns output text."""
    lottery = step.get("lottery")
    if not lottery:
        return ""
    
    limit = step.get("limit", 100)
    count = step.get("count", 1)
    temp  = step.get("temperature", step.get("temp", 1.0))
    
    # Howard / Tactical params
    pool = step.get("pool")
    key  = step.get("key")
    filters = step.get("filters")
    k_of_n  = step.get("k-of-n", step.get("k_of_n", 0))
    
    strat_configs = step.get("strategies", [])
    ensemble_type = step.get("ensemble")

    if lottery not in adapter_cache:
        adapter_cache[lottery] = get_adapter(lottery)
    adapter = adapter_cache[lottery]
    df = adapter.fetch(limit=limit)

    strat_names = []
    strat_instances = []
    for sc in strat_configs:
        s_name = sc.get("name") if isinstance(sc, dict) else sc
        # Merge global config with step-specific params
        params = global_config.copy()
        if isinstance(sc, dict) and "params" in sc:
            params.update(sc["params"])
        
        # Avoid clashing with get_strategy(name=...)
        params.pop("name", None)
            
        try:
            strat = get_strategy(s_name, **params)
            strat_names.append(s_name)
            strat_instances.append(strat)
        except Exception as e:
            console.print(f"  [red]Failed to load strategy {s_name}: {e}[/red]")

    if not strat_instances:
        return ""

    name = step.get("name", lottery)
    
    # Resolve tactical lists
    pool_list = [int(n) for n in pool.replace(",", " ").split()] if isinstance(pool, str) else pool
    key_list  = [int(n) for n in key.replace(",", " ").split()] if isinstance(key, str) else key
    filter_list = [f.strip() for f in filters.split(",") if f.strip()] if isinstance(filters, str) else filters

    suggest_kwargs = {
        "count": count,
        "temperature": temp,
        "pool": pool_list,
        "key": key_list,
        "filters": filter_list,
        "filters_k_of_n": k_of_n
    }

    if ensemble_type:
        try:
            if ensemble_type == "voting":
                from engine.strategies.ml.ensemble import VotingEnsemble
                master_strat = VotingEnsemble(members=strat_names)
            elif ensemble_type == "hybrid":
                from engine.strategies.ml.ensemble import HybridEnsemble
                master_strat = HybridEnsemble(members=strat_names)
            else:
                master_strat = strat_instances[0]
        except Exception:
            master_strat = strat_instances[0]

        res = master_strat.suggest(df, adapter.rules, **suggest_kwargs)
        out = f"# {name}\n\nLottery: {lottery}\nStrategies: {strat_names}\nEnsemble: {ensemble_type}\n\n"
        for i, t in enumerate(res.tickets):
            out += f"Ticket {i+1}: {t} (Confidence: {res.confidence:.2f})\n"
    else:
        out = f"# {name}\n\nLottery: {lottery}\n\n"
        for s_name, strat in zip(strat_names, strat_instances):
            res = strat.suggest(df, adapter.rules, **suggest_kwargs)
            out += f"## Strategy: {s_name}\n"
            for i, t in enumerate(res.tickets):
                out += f"Ticket {i+1}: {t} (Confidence: {res.confidence:.2f})\n"
            out += "\n"

    return out


def _step_narrative(step: dict, adapter_cache: dict) -> str:
    """Generates a v11 story narrative for the lottery."""
    lottery = step.get("lottery")
    if not lottery:
        console.print("[yellow]step narrative: missing 'lottery'[/yellow]")
        return ""
    
    if lottery not in adapter_cache:
        adapter_cache[lottery] = get_adapter(lottery)
    adapter = adapter_cache[lottery]
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pool_size = hi - lo + 1

    # 1. Run required scans for results
    from engine.cli.commands.scan import _regime_js, _rolling_stable_pct, _stress_delta, _solar_kp
    from engine.strategies.fun.moon_phase import moon_phase_ratio
    from engine.modules import frequency

    js_val, regime_verdict = _regime_js(df, lo, pool_size, recent=50)
    
    scan_scores: dict[str, int] = {}
    
    # Simple score mapping
    f_res = frequency.analyze(df.tail(100), rules)
    p = f_res.chi2_p_value
    scan_scores["fairness"] = 2 if p > 0.5 else 1 if p >= 0.05 else 0
    
    stab = _rolling_stable_pct(df, adapter, "bayesian", 50, n_windows=4)
    scan_scores["stability"] = 2 if (stab or 0) >= 0.5 else 1
    
    stress = _stress_delta(df, rules, "bayesian")
    if stress is not None:
        scan_scores["stress"] = 2 if abs(stress) < 0.1 else 1 if abs(stress) < 0.2 else 0
    else:
        scan_scores["stress"] = 1
    
    moon_r = moon_phase_ratio(date.today())
    scan_scores["lunar"] = 2 if 0.4 <= moon_r <= 0.6 else 1
    
    kp = _solar_kp()
    scan_scores["solar"] = 2 if kp < 4 else 1 if kp < 6 else 0
    
    total = sum(scan_scores.values())
    max_s = len(scan_scores) * 2
    verdict = "GO" if total >= 8 else "CAUTION" if total >= 5 else "NO-GO"

    scan_results = {
        "regime": {"js": js_val, "verdict": regime_verdict},
        "scan": {"score": total, "max": max_s, "verdict": verdict}
    }

    # 2. Generate Narrative
    from engine.modules.narrative import NarrativeGenerator
    gen = NarrativeGenerator(adapter, df, scan_results)
    
    persona = step.get("persona", "Synapse Architect")
    return gen.generate_story_v11(persona=persona)


# ── Main pipeline runner ──────────────────────────────────────────────────────

def _load_report_state() -> dict:
    from engine.cli.utils import DATA_DIR
    path = DATA_DIR / "report_state.json"
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_report_state(state: dict) -> None:
    from engine.cli.utils import DATA_DIR
    path = DATA_DIR / "report_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def run_report(config_path: str, force: bool = False, overrides: dict | None = None):
    path = Path(config_path)
    if not path.exists():
        console.print(f"[red]Error: Configuration file not found at {path}[/red]")
        raise typer.Exit(1)

    # ── Configuration & State ────────────────────────────────────────────────
    global_config = load_local_config()
    if overrides:
        global_config.update(overrides)

    state = _load_report_state()
    config_id = str(path.absolute())
    today = date.today().isoformat()
    
    if not force and state.get(config_id) == today:
        console.print(f"[green]✓ Pipeline '{path.name}' already executed today. Use --force to re-run.[/green]")
        return

    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error parsing {path}: {e}[/red]")
        raise typer.Exit(1)

    state[config_id] = today
    _save_report_state(state)
    
    if "params" in config:
        global_config.update(config["params"])

    steps = config.get("steps", [])
    if steps:
        pipeline_name = config.get("name", path.stem)
        console.print(Rule(f"[bold cyan]Pipeline: {pipeline_name}[/bold cyan]"))

        _STEP_TYPES = {"fetch", "daily", "alert", "scan", "forecast", "watchlist-run", "suggest", "narrative"}
        adapter_cache: dict = {}

        for i, step in enumerate(steps, 1):
            step_type = step.get("type", "suggest")
            step_name = step.get("name") or step.get("lottery") or step_type
            if step_type not in _STEP_TYPES:
                console.print(f"[yellow]Step {i}: Unknown type '{step_type}' — skipping.[/yellow]")
                continue

            console.print(Rule(f"[dim]Step {i}/{len(steps)}: {step_type} — {step_name}[/dim]"))

            if step_type == "fetch":
                _step_fetch(step)
            elif step_type == "daily":
                _step_daily(step)
            elif step_type == "alert":
                triggered = _step_alert(step)
                if triggered:
                    console.print(f"[green]✓ Alert triggered for {step.get('lottery', '?')}[/green]")
                else:
                    console.print(f"[dim]No alert for {step.get('lottery', '?')}[/dim]")
            elif step_type == "scan":
                _step_scan(step)
            elif step_type == "forecast":
                _step_forecast(step)
            elif step_type == "watchlist-run":
                _step_watchlist_run(step)
            elif step_type == "suggest":
                output_text = _step_suggest(step, adapter_cache, global_config)
                output_file = step.get("output")
                if output_file:
                    out_path = Path(output_file)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_text(output_text)
                    console.print(f"[green]✓ Saved to {output_file}[/green]")
                else:
                    console.print(output_text)
            elif step_type == "narrative":
                output_text = _step_narrative(step, adapter_cache)
                output_file = step.get("output")
                if output_file:
                    out_path = Path(output_file)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_text(output_text)
                    console.print(f"[green]✓ Narrative saved to {output_file}[/green]")
                else:
                    console.print(output_text)

        console.print(Rule(f"[bold green]Pipeline complete[/bold green]"))
        return

    # ── Legacy reports format ─────────────────────────────────────────────────
    reports = config.get("reports", [])
    if not reports:
        console.print("[yellow]No reports or steps defined in configuration.[/yellow]")
        return

    adapter_cache: dict = {}
    for r in reports:
        name = r.get("name", "Unnamed Report")
        console.rule(f"[bold cyan]Executing Report: {name}[/bold cyan]")
        output_text = _step_suggest(r, adapter_cache, global_config)
        output_file = r.get("output")
        if output_file:
            out_path = Path(output_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output_text)
            console.print(f"[green]✓ Report saved to {output_file}[/green]")
        else:
            console.print(output_text)


def report(
    config_path: Annotated[Path, typer.Argument(help="Path to report configuration (YAML)")],
    force: Annotated[bool, typer.Option("--force", help="Run even if already updated today")] = False,
) -> None:
    """📋 Execute a scheduled report or diagnostic pipeline from a config file.

    Supports two formats:

    Legacy (strategy suggestions):
      reports: [{name: ..., lottery: ..., strategies: [...]}]

    New steps-based pipeline:
      steps:
        - {type: fetch, lottery: br/lotofacil}
        - {type: daily, lottery: br/lotofacil, export_md: digest.md}
        - {type: alert, lottery: br/lotofacil, condition: go-strong}
        - {type: scan, lottery: br/lotofacil}
        - {type: forecast, lottery: br/lotofacil, strategies: fast}
        - {type: watchlist-run, mode: scan}
        - {type: narrative, lottery: br/lotofacil, persona: "Synapse Architect"}

    Example: lottery report config.yaml
    """
    run_report(str(config_path), force=force)
