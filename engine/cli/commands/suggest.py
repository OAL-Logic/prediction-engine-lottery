"""
Suggest Command 🎟️
==================
Generates lottery ticket suggestions using various prediction strategies.
"""

from __future__ import annotations

import logging
import math
import asyncio
from datetime import date, datetime
from typing import Annotated, Optional, List, Dict, Any

import typer
# import pandas as pd  # Moved inside functions
from rich import print as rprint
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel

from engine.cli.utils import get_adapter, print_command_summary, geocode, load_local_config
# from engine.strategies import get_strategy, list_strategies as list_strats_func, STRATEGY_PRESETS # Moved inside

console = Console()
logger = logging.getLogger(__name__)

# --- (v5.0) Chaos Temperature Governor helpers ---

async def _fetch_seismic(lat: float, lon: float, radius: int = 500) -> list[dict]:
    """Fetch recent seismic activity from USGS within radius km of location."""
    import httpx
    from datetime import datetime, timedelta
    
    end = datetime.now()
    start = end - timedelta(days=7)
    
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&starttime={start.strftime('%Y-%m-%d')}"
        f"&endtime={end.strftime('%Y-%m-%d')}&latitude={lat}&longitude={lon}"
        f"&maxradiuskm={radius}&minmagnitude=1.0"
    )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("features", [])
    except Exception:
        pass
    return []


def suggest(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/mega-sena) [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s",
                     help="Strategy name or comma-separated list. Run 'lottery strategies' for available options.\n\n"
                          "Statistical: markov | bayesian | weighted | monte_carlo |\n"
                          "             pattern | momentum | spectral | streak\n"
                          "ML:          logistic | random_forest | gradient_boost | knn\n"
                          "Ensemble:    voting:s1,s2 | prob_weighted:s1,s2 | hybrid:s1,s2\n"
                          "Deep:        transformer | lstm_gru | cnn_1d\n"
                          "Fun:         numerology | moon_phase | weather |\n"
                          "             biorhythm | fibonacci | zodiac\n"
                          "Other:       chaos  (pure random)")] = "weighted",
    count:       Annotated[int,   typer.Option("--count",   "-c", help="Number of tickets")] = 1,
    temperature: Annotated[float, typer.Option("--temp",    "-t", help="Sampling temperature (0=deterministic, 1=default, >1=noisy)")] = 1.0,
    limit:           Annotated[int | None, typer.Option("--limit", "-L", help="Use only the N most recent draws")] = None,
    top_scored:      Annotated[int,        typer.Option("--top-scored",      help="How many top-scored numbers to show after each ticket suggestion")] = 5,
    recent_matches:  Annotated[int,        typer.Option("--recent-matches",  help="Max recent matched draws to show in correlation metadata (moon_phase, weather)")] = 5,
    top_numbers:     Annotated[int,        typer.Option("--top-numbers",     help="Max top numbers to show in correlation metadata (moon_phase, weather)")] = 5,
    full_name:       Annotated[Optional[str], typer.Option("--full-name",    help="User full name for personalized numerology strategies")] = None,
    birth_date:      Annotated[Optional[str], typer.Option("--birth-date",   help="User birth date (YYYY-MM-DD) for personalized strategies")] = None,
    topic:           Annotated[Optional[str], typer.Option("--topic",        help="Intentional topic string for seeding randomness")] = None,
    adaptive_window: Annotated[bool,          typer.Option("--adaptive-window", help="Automatically pick optimal history window for the strategy")] = False,
    pool:            Annotated[Optional[str], typer.Option("--pool",         help="Constrain selection to these numbers (comma-separated list)")] = None,
    key:             Annotated[Optional[str], typer.Option("--key",          help="Include these numbers in every ticket (comma-separated list)")] = None,
    filters:         Annotated[Optional[str], typer.Option("--filters",      help="Apply structural filters (comma-separated names or 'all')")] = None,
    k_of_n:          Annotated[int,           typer.Option("--k-of-n",       help="Tolerance for harmony checks (accept if K of N filters pass)")] = 0,
    pick:            Annotated[Optional[int], typer.Option("--pick",         help="Override default pick count (e.g. play 7 numbers in a pick-6 game)")] = None,
    explain:         Annotated[bool,          typer.Option("--explain",       help="Show top-3 contributing features for each prediction")] = False,
    window_check:    Annotated[bool,          typer.Option("--window-check",  help="Abort with a warning if the current signal window is NOISE")] = False,
    filter_anomalies: Annotated[bool, typer.Option("--filter-anomalies", help="Automatically restrict generation to correct statistical pattern anomalies")] = False,
    kelly: Annotated[Optional[float], typer.Option("--kelly", help="Calculate optimal bet size using Kelly Criterion for this bankroll")] = None,
    chaos: Annotated[bool, typer.Option("--chaos", help="Enable Real-time Environmental Jitter (Solar/Seismic)")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Append suggest report to this .md file")] = None,
) -> None:
    """
    🎟️ Generate ticket suggestions using a specific prediction strategy.
    """
    personal_data = load_local_config()
    # Merge CLI overrides
    if full_name: personal_data["full_name"] = full_name
    if birth_date: personal_data["birth_date"] = birth_date
    if topic: personal_data["topic"] = topic

    # ── Entropy gate: abort early when signal is noisy ────────────────────────
    if window_check:
        try:
            from engine.strategies import get_strategy as _gs
            _adapter = __import__("engine.cli.utils", fromlist=["get_adapter"]).get_adapter(lottery)
            _df = _adapter.fetch(limit=200)
            _w = 50
            _confs = []
            for _i in range(5):
                _pos = len(_df) - _w - _i * 15
                if _pos < 0:
                    break
                try:
                    # Pass personal data even to the gate-check strategy
                    _strat = _gs(strategy.split(",")[0].strip(), **personal_data)
                    _res = _strat.suggest(_df.iloc[_pos : _pos + _w], _adapter.rules, count=1, temperature=1.0)
                    _confs.append(_res.confidence)
                except Exception:
                    continue
            if len(_confs) >= 2:
                import numpy as _np
                _arr = _np.array(_confs)
                _std = float(_np.std(_arr))
                if _std > 0.08:
                    console.print(
                        f"\n[bold yellow]⚠ WINDOW-CHECK ABORT:[/bold yellow] "
                        f"Signal is NOISY (confidence σ={_std:.4f} > 0.08). "
                        f"Conditions are not favourable for prediction.\n"
                        f"  Run [cyan]lottery scan {lottery}[/cyan] for a full diagnostic.\n"
                        f"  Pass [dim]--no-window-check[/dim] to override."
                    )
                    raise typer.Exit(0)
        except SystemExit:
            raise
        except Exception:
            pass  # gate is best-effort — don't break suggest on gate errors

    _run_comparison(
        lottery=lottery,
        strategies=strategy,
        count=count,
        temperature=temperature,
        limit=limit,
        top=top_scored,
        learn=False, # suggest command is concise
        personal_data=personal_data,
        adaptive_window=adaptive_window,
        pool=pool,
        key=key,
        filters=filters,
        k_of_n=k_of_n,
        recent_matches=recent_matches,
        top_numbers=top_numbers,
        pick=pick,
        explain=explain,
        filter_anomalies=filter_anomalies,
        kelly=kelly,
        chaos=chaos,
        export_md=export_md,
    )

def _run_comparison(
    lottery: str,
    strategies: str = "statistical",
    count: int = 1,
    temperature: float = 1.0,
    limit: int | None = None,
    top: int = 8,
    learn: bool = True,
    strategy_objects: list[Any] | None = None,
    strategy_configs: list[dict] | None = None,
    personal_data: dict | None = None,
    adaptive_window: bool = False,
    pool: str | None = None,
    key: str | None = None,
    filters: str | None = None,
    k_of_n: int = 0,
    recent_matches: int = 5,
    top_numbers: int = 5,
    pick: int | None = None,
    explain: bool = False,
    filter_anomalies: bool = False,
    kelly: float | None = None,
    chaos: bool = False,
    export_md: str | None = None,
) -> None:
    """Internal helper to run the actual comparison logic."""
    from engine.strategies import get_strategy, STRATEGY_PRESETS
    import pandas as pd # Local import for performance

    personal_data = personal_data or {}

    # Resolve strategy list
    if strategy_objects:
        strat_instances = strategy_objects
        strat_names = [s.name for s in strat_instances]
        # configs provided externally (e.g. from wizard)
        configs = strategy_configs or [{} for _ in strat_names]
    else:
        if strategies in STRATEGY_PRESETS:
            strat_names = STRATEGY_PRESETS[strategies]
        else:
            # (v10.0) Smart Split: Support ensembles with internal commas
            # We first try to split by ';' or '+' as high-priority separators.
            # If not found, we use a regex to split by ',' while respecting ':' scopes.
            if ";" in strategies:
                strat_names = [s.strip() for s in strategies.split(";") if s.strip()]
            elif "+" in strategies:
                strat_names = [s.strip() for s in strategies.split("+") if s.strip()]
            else:
                # REFINED: Split by comma, but merge parts that look like they belong to an ensemble.
                raw_parts = [s.strip() for s in strategies.split(",") if s.strip()]
                strat_names = []
                for p in raw_parts:
                    if ":" in p or not strat_names:
                        strat_names.append(p)
                    else:
                        prev = strat_names[-1]
                        if ":" in prev:
                            strat_names[-1] = f"{prev},{p}"
                        else:
                            strat_names.append(p)
        
        strat_instances = []
        configs = []
        for name in strat_names:
            try:
                # Merge personal data into instantiation
                params = personal_data.copy()
                params.pop("name", None) # Avoid clash with positional name
                strat = get_strategy(name, **params)
                strat_instances.append(strat)
                configs.append(params)
            except KeyError:
                console.print(f"[yellow]⚠ Strategy '{name}' not found. Skipping.[/yellow]")
                strat_instances.append(None)
                configs.append({})

    # Fail fast or Fallback if no valid strategies (Change 12)
    valid_count = sum(1 for s in strat_instances if s is not None)
    if valid_count == 0:
        console.print("[yellow]⚠ No valid strategies provided. Using 'weighted' as fallback.[/yellow]")
        strat_instances = [get_strategy("weighted", **personal_data)]
        configs = [personal_data]

    # Load data once
    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df_full = adapter.fetch()
        
        # Apply global recency limit
        df_sliced = df_full.tail(limit) if limit else df_full

    # Detect Anomaly Constraints (Phase 3)
    anomaly_constraints = {}
    if filter_anomalies:
        from engine.modules.tendency import analyze_pattern_tendency
        from engine.cli.commands.dashboard import PATTERN_CONFIG
        
        console.print("[bold cyan]⚗  Anomaly Filtering Active:[/bold cyan] Scanning for overdue patterns...")
        
        anomalies = []
        filter_map = {
            "primes": "prime_count",
            "fibonacci": "fibonacci_count",
            "magic": "magic_count",
            "multiples_3": "multiples_3_count",
            "repeated": "repeat_rate",
            "frame": "frame_count",
        }
        
        for pk, config in PATTERN_CONFIG.items():
            if pk not in filter_map: continue
            # Use full history for accurate statistical averages
            res = analyze_pattern_tendency(df_full, config["func"], config["name"])
            for s in res.stats:
                # Severity threshold: Delay >= 1.2x Average and Occurrence > 2%
                if s.delay >= (s.avg_frequency * 1.2) and s.avg_frequency > 0 and s.average_pct > 2:
                    anomalies.append((pk, filter_map[pk], s.qty, s.delay / s.avg_frequency))
        
        anomalies.sort(key=lambda x: x[3], reverse=True)
        for pk, filter_name, qty, score in anomalies[:3]:
            console.print(f"  [yellow]» Restricted:[/] {PATTERN_CONFIG[pk]['name']} must have QTY {qty} (Evidence: {score:.1f}x delay)")
            anomaly_constraints[filter_name] = qty

    lo, hi = adapter.rules.number_range
    pick_count = pick or adapter.rules.pick_count

    # Header
    from engine.cli.utils import ui_header, ui_panel, ui_dummy_block, ui_table
    ui_header("suggestion engine", f"{adapter.rules.name} | pick={pick_count} | temp={temperature}")

    all_results = []
    failed: list[str] = []

    for idx, (name, strat, config) in enumerate(zip(strat_names, strat_instances, configs)):
        if strat is None:
            rprint(f"  [red]Strategy '{name}' not found — skipping.[/red]")
            failed.append(name)
            continue

        strategy_label = name.upper()
        
        try:
            # 1. Inject UI settings into strategy object
            strat.recent_matches_count = recent_matches
            strat.top_numbers_count    = top_numbers

            # 2. Chaos Temperature Governor (Chaos Analyst)
            # Adjusts 'active_temp' based on Total Environmental Entropy
            # If multiple signals align (Solar Storm + Moon Tide + Arcano 78), 
            # we increase the temperature for high-reward exploration.
            
            entropy_boost = 0.0
            draw_date_obj = date.today() # Placeholder
            
            # (A) Esoteric signal (Kabbalistic Arcano)
            if name == "kabbalistic" and hasattr(strat, 'current_arcano') and getattr(strat, 'current_arcano') == 78:
                entropy_boost += 0.5
            
            # (B) Solar signal (Geomagnetic Storm)
            from engine.strategies.fun.solar import SolarStrategy
            solar_helper = SolarStrategy(draw_date=draw_date_obj)
            kp_val = solar_helper._get_target_kp(solar_helper._load_solar_data()) or 1.0
            if kp_val >= 5.0: # Storm G1+
                entropy_boost += 0.3
            
            # (C) Lunar signal (Proxigean Tides)
            from engine.strategies.fun.moon_phase import moon_phase_ratio, moon_distance_ratio, tidal_intensity
            p_ratio = moon_phase_ratio(draw_date_obj)
            d_ratio = moon_distance_ratio(draw_date_obj)
            tide = tidal_intensity(p_ratio, d_ratio)
            if tide > 0.8: # Very high tide
                entropy_boost += 0.2

            # (D) Seismic Resonance Layer
            coords = adapter.get_draw_location() if hasattr(adapter, 'get_draw_location') else (-23.55, -46.63)
            seismic_events = asyncio.run(_fetch_seismic(coords[0], coords[1]))
            
            if seismic_events:
                max_mag = max(e['properties']['mag'] for e in seismic_events)
                jitter_boost = min(0.5, max_mag * 0.1)
                entropy_boost += jitter_boost
            
            # (E) Noosphere Jitter
            import time
            import hashlib
            t_now = time.time()
            jitter_hash = hashlib.sha256(str(int(t_now // 3600)).encode()).hexdigest()
            noosphere_val = int(jitter_hash[:4], 16) / 65535.0
            if noosphere_val > 0.7:
                entropy_boost += 0.2
            
            # (F) Statistical Stability
            from scipy import stats
            flat_recent = [n for d in df_full.tail(20)["numbers"] for n in d]
            from collections import Counter
            counts_map = Counter(flat_recent)
            _, p_val = stats.chisquare(list(counts_map.values()))
            stability_boost = 0.0
            if p_val < 0.05:
                stability_boost = 0.3
            elif p_val > 0.8:
                stability_boost = -0.1
            
            active_temp = temperature + entropy_boost + stability_boost
            
            # --- (Howard Ideas) Constraints & Filters ---
            pool_list = [int(n) for n in pool.replace(",", " ").split()] if pool else None
            key_list  = [int(n) for n in key.replace(",", " ").split()] if key else None
            filter_list = [f.strip() for f in filters.split(",") if f.strip()] if filters else []
            
            # Inject anomaly filters
            if anomaly_constraints:
                filter_list.extend(anomaly_constraints.keys())

            strat.adaptive_window = adaptive_window
            
            with console.status(f"  Running {strategy_label}…"):
                result = strat.suggest(
                    df_sliced, 
                    adapter.rules, 
                    count=count, 
                    temperature=active_temp, 
                    history_limit=None,
                    pick=pick_count,
                    pool=pool_list,
                    key=key_list,
                    filters=filter_list,
                    filters_k_of_n=k_of_n,
                    chaos=chaos,
                    **anomaly_constraints # Pass the specific counts
                )
            
            # --- For Dummies Shortcut Tip ---
            if idx == 0 and len(strat_names) > 1:
                ui_dummy_block("tip", "Look at the [bold]Consensus Analysis[/] below to see where multiple strategies agree.")

            # 3. OSINT Injection
            if seismic_events:
                result.metadata["seismic_resonance"] = {
                    "count": len(seismic_events),
                    "max_mag": max(e['properties']['mag'] for e in seismic_events),
                    "latest": seismic_events[0]['properties']['place']
                }
            
            if "noosphere_intensity" not in result.metadata:
                result.metadata.update({
                    "noosphere_intensity": "Volatile" if noosphere_val > 0.7 else "Stable" if noosphere_val < 0.3 else "Coherent",
                    "jitter_score": round(noosphere_val, 3),
                    "regime": "High Focus" if noosphere_val > 0.7 else "Default Resonance"
                })
            
            if "phase_name" not in result.metadata:
                from engine.strategies.fun.moon_phase import phase_name
                result.metadata.update({
                    "phase_name": phase_name(draw_date_obj),
                    "phase_ratio": p_ratio,
                    "moon_distance": "Perigee" if d_ratio < 0.2 else "Apogee" if d_ratio > 0.8 else "Neutral",
                    "tidal_intensity": "high" if tide > 0.66 else "low" if tide < 0.33 else "normal"
                })
            
            if "kp" not in result.metadata:
                result.metadata.update({
                    "kp": round(kp_val, 1),
                    "intensity": "storm" if kp_val >= 5 else "unsettled" if kp_val >= 3 else "quiet"
                })

            if entropy_boost > 0:
                result.metadata["chaos_boost"] = round(entropy_boost, 2)
                
            all_results.append(result)
            _print_single_result(
                result, 
                strategy_label, 
                rules=adapter.rules, 
                df=df_full, 
                top_scored=top, 
                strat_obj=strat, 
                explain=explain,
                kelly_bankroll=kelly
            )

        except Exception as exc:
            console.print(f"[red]Strategy failed: {exc}[/red]")
            failed.append(name)
            continue

    if len(all_results) > 1:
        _print_consensus(all_results)

    if learn:
        _print_learn_section()

    if failed:
        console.print(f"\n[yellow]⚠  Skipped: {', '.join(failed)}[/yellow]")

    # STORY 3.2: Export to Markdown
    if export_md:
        from datetime import datetime
        import json
        import numpy as np
        
        # Calculate overall confidence
        avg_conf = np.mean([r.confidence for r in all_results]) if all_results else 0
        
        # Format tickets
        all_tickets = []
        for res in all_results:
            all_tickets.extend(res.tickets)
            
        _write_md(
            export_md,
            lottery,
            adapter.rules.name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            all_results,
            avg_conf,
            all_tickets
        )

def _write_md(path, lottery, game_name, timestamp, results, confidence, tickets):
    """Standardized Obsidian Metadata Contract implementation."""
    import json
    from pathlib import Path
    import numpy as np
    
    ticket_lines = "\n".join([f"- Ticket {i+1}: {', '.join(map(str, sorted(t)))}" for i, t in enumerate(tickets)])
    
    # JSON payload for DataviewJS
    serializable_results = []
    for r in results:
        serializable_results.append({
            "strategy": str(r.strategy_name),
            "confidence": float(r.confidence),
            "tickets": [[int(n) for n in t] for t in r.tickets]
        })

    content = f"""---
type: pattern-log
subtype: suggestion
game: "{game_name}"
lottery: "{lottery}"
date: {timestamp}
source-strategy: "multiple"
confidence-rating: {confidence:.2f}
tags: [prediction-engine, suggestion, #lottery/analysis]
data-payload: {json.dumps(serializable_results)}
---

# Suggestion Report: {game_name} — {timestamp}

**Average Confidence:** {confidence:.2%}

## Generated Tickets
{ticket_lines}

---
"""
    p = Path(path)
    # STORY 3.2: Create new file (isolated)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

    # STORY 3.2: Update central index (aggregate)
    index_path = p.parent.parent / "docs" / "analysis-index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# Lottery Analysis Index\n\n| Date | Game | Analysis File |\n| :--- | :--- | :--- |\n")
    
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | {game_name} | [[{p.name}]] |\n")

def _print_single_result(result, label, rules, df, top_scored, strat_obj, explain: bool = False, kelly_bankroll: float | None = None):
    """Prints formatted output for a single strategy suggestion."""
    from engine.cli.utils import ui_panel, ui_table, ui_dummy_block, Theme
    import numpy as np

    # 1. Metadata Summary Line

    meta = []
    if "phase_name" in result.metadata: meta.append(f"🌕 {result.metadata['phase_name']}")
    if "kp" in result.metadata: meta.append(f"☀️ Kp {result.metadata['kp']}")
    if "chaos_boost" in result.metadata: meta.append(f"🌀 Boost +{result.metadata['chaos_boost']}")
    subtitle = " | ".join(meta)

    # 2. Main Ticket Content
    content = []
    for i, ticket in enumerate(result.tickets):
        t_str = ", ".join(map(str, sorted(ticket)))
        t_sum = sum(ticket)
        
        # Historical win context
        win_counts = {tier: 0 for tier in rules.prize_tiers}
        for draw_nums in df["numbers"]:
            matches = len(set(ticket) & set(draw_nums))
            if matches in win_counts: win_counts[matches] += 1
        win_info = " | ".join(f"M{k}: {v}" for k, v in sorted(win_counts.items()) if v > 0)
        
        content.append(f"[bold {Theme.SECONDARY}]Ticket {i+1}:[/] {t_str} [dim](sum={t_sum})[/]")
        if win_info:
            content.append(f"   [dim]⌞ Hist Wins: {win_info}[/]")

    # 3. Top Scored Table (Evidence)
    evidence = None
    if explain:
        # Feature 5: score entropy (concentration)
        from engine.cli.utils import calculate_shannon_entropy
        ent = calculate_shannon_entropy(result.scores)
        
        # Max theoretical entropy for this pool size
        n_items = len(result.scores)
        max_ent = np.log(n_items)
        concentration = 1.0 - (ent / (max_ent or 1.0))
        
        conc_label = "diffuse" if concentration < 0.1 else "normal" if concentration < 0.25 else "concentrated"
        
        evidence = ui_table(columns=["Rank", "Number", "Score"])
        sorted_scores = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)[:top_scored]
        for i, (num, score) in enumerate(sorted_scores):
            evidence.add_row(str(i+1), f"[bold]{num}[/]", f"{score:.4f}")
        
        rprint(f" [dim]⌞ Score Entropy: {ent:.4f} ({conc_label})[/]")
    rprint(ui_panel(
        Group("\n".join(content), "\n", ui_panel(evidence, title="Statistical Evidence", style="bright_black") if evidence else ""),
        title=f"{label} PREDICTION",
        subtitle=subtitle,
        style=Theme.PRIMARY
    ))

    # Evidence Panel (from v7.0)
    _print_evidence_panel(result.metadata)

    # 4. Kelly Panel
    if kelly_bankroll:
        from engine.modules.risk import calculate_kelly_bet
        k_res = calculate_kelly_bet(
            bankroll=kelly_bankroll,
            ticket_price=rules.ticket_price,
            jackpot_odds=rules.jackpot_odds,
            confidence=result.confidence
        )
        
        k_color = "green" if k_res.is_safe else "yellow"
        k_lines = [
            f"Signal Confidence : [bold]{k_res.confidence:.2%}[/]",
            f"Optimal Risk (f*) : [bold]{k_res.fraction:.2%}[/] of bankroll",
            f"Recommended Bet   : [bold]{k_res.bet_amount:,.2f} {rules.currency}[/]",
            f"Ticket Count      : [bold yellow]{k_res.tickets}[/] tickets",
        ]
        if not k_res.is_safe:
            k_lines.append(f"\n[red]⚠ WARNING: Confidence below safety threshold (0.2).[/]")
            
        console.print(Panel("\n".join(k_lines), title="⚖️ Bankroll Optimization (Kelly)", border_style=k_color))

    # Explain Panel: top contributing features
    if explain:
        _print_explain_panel(result, rules, df)

def _print_evidence_panel(metadata: dict):
    """Draw the fancy 'OSINT' evidence panel."""
    from rich.panel import Panel
    evidence = []
    
    if "phase_name" in metadata:
        evidence.append(f"🌕 Moon phase: {metadata['phase_name']} ({metadata['phase_ratio']*100:.1f}% through cycle) | Distance: {metadata['moon_distance']} | Tide: {metadata['tidal_intensity']}")
        
    if "kp" in metadata:
        evidence.append(f"☀️ Solar Weather: {metadata['intensity']} (Planetary K-index: {metadata['kp']})")
        
    if "jitter_score" in metadata:
        evidence.append(f"🧠 Noosphere Jitter: {metadata['noosphere_intensity']} (Jitter Score: {metadata['jitter_score']}) | Regime: {metadata['regime']}")
        
    if "seismic_resonance" in metadata:
        s = metadata["seismic_resonance"]
        evidence.append(f"🫨 Seismic Resonance: {'Active' if s['count'] > 0 else 'Stable'} ({s['count']} recent tremors, max mag: {s['max_mag']})")

    if "env_jitter" in metadata:
        ej = metadata["env_jitter"]
        evidence.append(f"🌪️ Environmental Jitter: [bold yellow]+{ej['total_boost']}[/] (Solar: {ej['j_solar']}, Seismic: {ej['j_seismic']})")
        evidence.append(f"   [dim]⌞ Solar Kp: {ej['kp']} | Max Mag: {ej['seismic_mag']}[/]")

    if "chaos_boost" in metadata:
        evidence.append(f"🌀 Chaos Entropy Boost: +{metadata['chaos_boost']} applied to sampling temperature")

    if evidence:
        console.print(Panel("\n".join(evidence), title="Correlation Evidence", border_style="dim"))


def _print_explain_panel(result, rules, df) -> None:
    """Explain panel: show top-3 contributing features for the prediction."""
    import numpy as np
    from rich.panel import Panel
    from scipy import stats

    lines = []

    # Feature 1: top-scoring numbers and their score percentile
    sorted_scores = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)
    if sorted_scores:
        top3 = sorted_scores[:3]
        for rank, (num, score) in enumerate(top3, 1):
            pct = score / (sorted_scores[0][1] or 1.0) * 100
            lines.append(f"Feature {rank}: Number [bold]{num}[/bold]  score={score:.4f} ({pct:.0f}% of max)")

    # Feature 4: Chi² regime over last 30 draws
    try:
        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        flat = [n for d in df.tail(30)["numbers"] for n in d]
        from collections import Counter
        counts = Counter(flat)
        observed = np.array([counts.get(n, 0) for n in range(lo, hi + 1)], dtype=float)
        expected = np.full(pool_size, observed.sum() / pool_size)
        chi2, p_val = stats.chisquare(observed, expected)
        regime = "non-uniform [red](possible structure)[/red]" if p_val < 0.05 else "uniform [green](fair / random)[/green]"
        lines.append(f"Feature 4: 30-draw regime — χ²={chi2:.2f}  p={p_val:.4f}  → {regime}")
    except Exception:
        pass

    # Feature 5: score entropy (concentration)
    from engine.cli.utils import calculate_shannon_entropy
    ent = calculate_shannon_entropy(result.scores)
    max_ent = float(np.log(len(result.scores)) if result.scores else 1.0)
    concentration = 1.0 - ent / (max_ent or 1.0)
    conc_label = "focused" if concentration > 0.3 else "diffuse"
    lines.append(f"Feature 5: Score entropy={ent:.4f}  concentration={concentration:.2%} ({conc_label})")

    if lines:
        console.print(Panel("\n".join(lines), title="🔍 Explain — Top Contributing Features", border_style="blue"))


def _print_consensus(results: list[Any]) -> None:
    """Prints where multiple strategies agree on numbers (consensus across strategies)."""
    # Using TUI Design Language
    from engine.cli.utils import ui_panel, Theme
    from collections import Counter
    
    counter = Counter()
    for res in results:
        for ticket in res.tickets:
            for n in ticket:
                counter[n] += 1
                
    if not counter: return
    
    # 1. Consensus Content
    lines = []
    strategy_count = len(results)
    
    for num, votes in counter.most_common(15):
        # We'll just use a simple bar for now as per design language
        bar = "█" * int(votes) + "░" * (max(0, strategy_count - votes))
        lines.append(f"   [bold yellow]{num:>2}[/]  {bar}  [dim]{votes} votes[/]")
        
    high_conv = [n for n, v in counter.items() if v >= max(2, strategy_count // 2 + 1)]
    
    footer = ""
    if high_conv:
        footer = f"\n[bold green]⭐ High Conviction:[/] {sorted(high_conv)}"

    # 2. Final Render
    rprint(ui_panel(
        Group("\n".join(lines), footer),
        title="CONSENSUS ANALYSIS",
        style=Theme.SECONDARY
    ))


def _print_learn_section() -> None:
    """Prints educational take-away."""
    console.print()
    console.rule("[bold magenta]LEARN — How to use these results[/bold magenta]")
    console.print("  • Look for [bold yellow]Convergence[/bold yellow]: Numbers that multiple strategies agree on.")
    console.print("  • Respect [bold green]Harmony[/bold green]: The engine auto-filters for sum-range and parity balance.")
    console.print("  • Play [bold cyan]Diversified[/bold cyan]: Use different strategy tiers (Statistical, ML, Esoteric).")
