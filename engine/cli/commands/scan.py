# --- High Fidelity ---
"""
Scan Command 🔬
===============
Unified pre-draw conditions scan — one command that tells you whether
today is a good time to play.

Runs six diagnostic layers in sequence and combines them into a single
GO / CAUTION / NO-GO recommendation:

  Layer 1  Chi-squared fairness test (is the distribution uniform?)
  Layer 2  Signal stability (recent windows: how many are STABLE?)
  Layer 3  Current cluster (which pattern group does the last draw belong to?)
  Layer 4  Esoteric conditions (moon phase, solar K-index)
  Layer 5  Adversarial discrimination (can the best strategy beat random?)
  Layer 6  Regime check (Jensen-Shannon drift vs full history)

Output: a compact condition card + a colour-coded recommendation.
Optional: auto-generate a ticket if the scan is GO.

Export: --export-md writes a timestamped YAML condition log for Obsidian.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date as _date
from typing import Annotated, Optional

import typer
import numpy as np
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from engine.cli.utils import get_adapter
from engine.strategies import  get_strategy
from engine.modules import frequency

console = Console()

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
        # Reduced timeout to 2.0s for snappy CLI response
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("features", [])
    except Exception:
        pass
    return []

def _solar_kp() -> Optional[float]:
    """Load latest solar Kp index from local cache."""
    from pathlib import Path
    import json
    p = Path("data/solar_k_index.json")
    if p.exists():
        try:
            data = json.loads(p.read_text())
            if isinstance(data, dict):
                # Legacy dict format: {"YYYY-MM-DD": kp}
                today = _date.today().isoformat()
                if today in data: return float(data[today])
                return float(data[sorted(data.keys())[-1]])
            elif isinstance(data, list) and data:
                # New list format: [{"kp": 1.0, ...}]
                return float(data[0].get("kp", 1.0))
        except Exception: pass
    return None

def _rolling_stable_pct(df, adapter, strategy, window, n_windows=6) -> Optional[float]:
    """Calculate what percentage of recent rolling windows were 'stable'."""
    try:
        from engine.cli.commands.signal import analyze_signal
        stable_count = 0
        for i in range(n_windows):
            offset = i * 5
            df_slice = df.iloc[:len(df)-offset]
            if len(df_slice) < window: break
            res = analyze_signal(df_slice, adapter, strategy, window=window, quiet=True)
            if res.get("verdict") == "STABLE":
                stable_count += 1
        return stable_count / n_windows
    except Exception:
        return None

def _current_cluster(df, adapter) -> Optional[tuple[int, str]]:
    """Determine the cluster of the most recent draw."""
    try:
        from engine.cli.commands.cluster import run_clustering
        res = run_clustering(df, adapter, n_clusters=5, quiet=True)
        return res.get("latest_cluster"), res.get("latest_desc")
    except Exception:
        return None

def _stress_delta(df, adapter, strategy, inject_ratio: float = 0.5, trials: int = 3) -> Optional[float]:
    """Calculate the discrimination delta (Real vs Random) for the strategy."""
    try:
        from engine.cli.commands.stress_test import run_stress_test
        res = run_stress_test(df, adapter, strategy, inject_ratio=inject_ratio, trials=trials, quiet=True)
        return res.get("discrimination_delta")
    except Exception:
        return None

def _regime_js(df, lo, pool_size, recent=50) -> tuple[float, str]:
    """Calculate Jensen-Shannon divergence between recent draws and full history."""
    try:
        from scipy.spatial.distance import jensenshannon
        all_nums = df["numbers"].explode().value_counts(normalize=True).reindex(range(lo, lo+pool_size), fill_value=0)
        recent_nums = df.tail(recent)["numbers"].explode().value_counts(normalize=True).reindex(range(lo, lo+pool_size), fill_value=0)
        
        # SciPy returns JS Distance (sqrt of divergence). 
        # Square it to maintain continuity with historical divergence logs.
        js_dist = float(jensenshannon(all_nums, recent_nums))
        js_div = js_dist ** 2
        
        if js_div < 0.02: return js_div, "STABLE"
        if js_div < 0.08: return js_div, "DRIFT"
        return js_div, "SHIFT"
    except Exception:
        return 0.0, "UNKNOWN"

def scan(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil) [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s",
        help="Primary strategy for signal and discrimination checks")] = "bayesian",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Rolling window size for stability check")] = 50,
    auto_suggest: Annotated[bool, typer.Option("--suggest/--no-suggest",
        help="Auto-generate a ticket if the scan verdict is GO")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append condition log to this .md file")] = None,
    quiet: Annotated[bool, typer.Option(hidden=True)] = False,
    offline: Annotated[bool, typer.Option("--offline", help="Skip network-dependent OSINT layers")] = False,
) -> str:
    """🔬 Unified pre-draw conditions scan — one command for GO/NO-GO.

    Runs five diagnostic layers (fairness, signal stability, cluster,
    esoteric conditions, adversarial discrimination) and combines them
    into a single recommendation.
    """
    
    from engine.cli.utils import ui_header, ui_panel, ui_table, ui_dummy_block, ui_section
    from engine.strategies.fun.moon_phase import phase_name, moon_phase_ratio

    # 1. Start concurrent fetches for performance
    async def fetch_all():
        from engine.cli.utils import get_cached_data_async
        adapter = get_adapter(lottery)
        
        # Run DB fetch (thread) and Seismic OSINT (async) in parallel
        tasks = [asyncio.to_thread(adapter.fetch)]
        
        if not offline:
            coords = adapter.get_draw_location() if hasattr(adapter, 'get_draw_location') else (-23.55, -46.63)
            cache_key = f"seismic_{coords[0]:.2f}_{coords[1]:.2f}"
            
            # Wrap the fetch in a lambda for the cache helper
            fetch_task = lambda: _fetch_seismic(coords[0], coords[1])
            tasks.append(get_cached_data_async(cache_key, fetch_task, ttl=3600))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return adapter, results[0], (results[1] if len(results) > 1 and not isinstance(results[1], Exception) else [])

    with (console.status(f"[bold green]Loading {lottery} data...") if not quiet else __import__('contextlib').nullcontext()):
        adapter, df, seismic_events = asyncio.run(fetch_all())

    if isinstance(df, Exception):
        rprint(f"[red]Error loading data: {df}[/red]")
        raise typer.Exit(1)

    rules = adapter.rules
    today = _date.today()

    if not quiet:
        ui_header("scan", f"{rules.name} | strategy={strategy}")

    scores: dict[str, int] = {}   # layer → 0/1/2
    details: dict[str, str] = {}  # layer → display text

    # ── Layer 1: Fairness / Chi-squared ─────────────────────────────────────────────
    with (console.status("") if not quiet else __import__('contextlib').nullcontext()):
        f_res = frequency.analyze(df.tail(100), rules, top_n=5)
    p = f_res.chi2_p_value
    if p < 0.05:
        scores["fairness"] = 0
        details["fairness"] = f"NON-UNIFORM (p={p:.4f}) — possible anomaly"
    elif p > 0.5:
        scores["fairness"] = 2
        details["fairness"] = f"UNIFORM (p={p:.4f}) — fair distribution"
    else:
        scores["fairness"] = 1
        details["fairness"] = f"BORDERLINE (p={p:.4f})"

    # ── Layer 2: Stability ────────────────────────────────────────────────────
    with (console.status("") if not quiet else __import__('contextlib').nullcontext()):
        stab = _rolling_stable_pct(df, adapter, strategy, window, n_windows=6)
    if stab is None:
        scores["stability"] = 1
        details["stability"] = "INSUFFICIENT DATA"
    elif stab >= 0.5:
        scores["stability"] = 2
        details["stability"] = f"STABLE — {stab:.0%} of windows consistent"
    elif stab >= 0.25:
        scores["stability"] = 1
        details["stability"] = f"MIXED — {stab:.0%} stability"
    else:
        scores["stability"] = 0
        details["stability"] = f"NOISY — {stab:.0%} stability (high entropy)"

    # ── Layer 3: Cluster ─────────────────────────────────────────────────────
    with (console.status("") if not quiet else __import__('contextlib').nullcontext()):
        cluster_result = _current_cluster(df, adapter)
    if cluster_result is None:
        scores["cluster"] = 1
        details["cluster"] = "UNAVAILABLE"
    else:
        c_id, c_desc = cluster_result
        scores["cluster"] = 1
        details["cluster"] = f"Cluster C{c_id}: {c_desc}"

    # ── Layer 4: Esoteric ─────────────────────────────────────────────────────
    m_name = phase_name(today)
    m_ratio = moon_phase_ratio(today)
    kp = _solar_kp()
    
    has_tremors = len(seismic_events) > 0
    
    esoteric_score = 1
    if m_name in ("New Moon", "Full Moon"): esoteric_score = 2
    if kp is not None and kp >= 5: esoteric_score = 0
    if has_tremors: esoteric_score = max(0, esoteric_score - 1)
    
    seismic_txt = f" | 🫨 Seismic Resonance active" if has_tremors else ""
    scores["esoteric"] = esoteric_score
    details["esoteric"] = f"{m_name} ({m_ratio*100:.0f}%) | Kp: {kp if kp else '—'}{seismic_txt}"

    # ── Layer 5: Discrimination ───────────────────────────────────────────────
    with (console.status("") if not quiet else __import__('contextlib').nullcontext()):
        delta = _stress_delta(df, adapter, strategy)
    if delta is None:
        scores["discrimination"] = 1
        details["discrimination"] = "UNAVAILABLE"
    elif delta > 0.02:
        scores["discrimination"] = 2
        details["discrimination"] = f"Strong Signal - REAL > RANDOM (Δ={delta:+.4f}) — strategy detects structure"
    elif delta < -0.005:
        scores["discrimination"] = 0
        details["discrimination"] = f"INVERTED (Δ={delta:+.4f}) — possible overfit"
    else:
        scores["discrimination"] = 1
        details["discrimination"] = f"Weak Signal - MARGINAL (Δ={delta:+.4f})"

    # ── Layer 6: Regime ───────────────────────────────────────────────────────
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    js_val, regime_verdict = _regime_js(df, lo, pool_size, recent=50)
    scores["regime"] = 2 if regime_verdict == "STABLE" else 1 if regime_verdict == "DRIFT" else 0
    
    regime_desc = "consistent with history" if regime_verdict == "STABLE" else "mild statistical drift" if regime_verdict == "DRIFT" else "regime shift detected"
    details["regime"] = f"{regime_verdict} — {regime_desc} (JS={js_val:.4f})"

    # ── Render Summary ────────────────────────────────────────────────────────
    total     = sum(scores.values())
    max_score = len(scores) * 2

    if not quiet:
        table = ui_table(columns=["Layer", "Status", "Insight"])
        for layer, score in scores.items():
            status = "●●" if score == 2 else "●○" if score == 1 else "○○"
            color = "green" if score == 2 else "yellow" if score == 1 else "red"
            table.add_row(layer.capitalize(), f"[{color}]{status}[/]", details[layer])
        
        console.print(ui_panel(table, title="Diagnostic Matrix"))

    pct = total / max_score
    if pct >= 0.7:
        verdict     = "GO"
        verdict_str = f"[bold green]✔ GO[/bold green]  ({total}/{max_score})"
    elif pct >= 0.4:
        verdict     = "CAUTION"
        verdict_str = f"[bold yellow]⚠ CAUTION[/bold yellow]  ({total}/{max_score})"
    else:
        verdict     = "NO-GO"
        verdict_str = f"[bold red]✘ NO-GO[/bold red]  ({total}/{max_score})"

    advice_map = {
        "GO": "Conditions are favourable! This is as good as it gets for a statistical approach.",
        "CAUTION": "Mixed signals. Think of it as a 'yellow light'—play for fun, but don't bet the farm.",
        "NO-GO": "Poor conditions. The math says 'not today.' Consider saving your tokens for a clearer signal."
    }
    
    advice = advice_map.get(verdict, "Proceed with your own judgment.")

    if not quiet:
        # 1. Entropy Alert
        is_high_entropy = False
        entropy_reasons = []
        if kp is not None and kp >= 5.0:
            is_high_entropy = True
            entropy_reasons.append("High Solar Activity (Solar Storm)")
        if m_name in ("Full Moon", "New Moon"):
            is_high_entropy = True
            entropy_reasons.append(f"Lunar Tide ({m_name})")
        if has_tremors:
            is_high_entropy = True
            entropy_reasons.append("Seismic Resonance")
            
        if is_high_entropy:
            console.print(ui_panel(
                f"Reasons: {', '.join(entropy_reasons)}\n\n"
                f"Perfect time for [bold cyan]VIX Jitter[/bold cyan] or [bold cyan]Hedge[/bold cyan] strategies.",
                title="🌀 HIGH ENTROPY REGIME",
                style="yellow"
            ))

        # 2. Recommendation
        style = "green" if verdict == "GO" else "yellow" if verdict == "CAUTION" else "red"
        console.print(ui_panel(
            f"{verdict_str}\n[dim]{advice}[/dim]",
            title="SYSTEM RECOMMENDATION",
            style=style
        ))
        
        # 3. Dummies Tip
        if verdict == "GO":
            ui_dummy_block("tip", "Since everything is aligned, try a [bold]Voting[/bold] ensemble to see where strategies converge.")
        elif verdict == "NO-GO":
            ui_dummy_block("tip", "On NO-GO days, [bold]Chaos[/bold] strategies are statistically just as likely as data-driven ones.")

    # ── Auto-suggest ──────────────────────────────────────────────────────────
    if auto_suggest and verdict == "GO":
        if not quiet:
            ui_section("Auto-Suggest")
        try:
            strat = get_strategy(strategy)
            result = strat.suggest(df, rules, count=1, temperature=0.8)
            if not quiet:
                t_str = ", ".join(map(str, sorted(result.tickets[0])))
                console.print(ui_panel(
                    f"→ [bold green]{t_str}[/]  (sum={sum(result.tickets[0])})",
                    title=f"{strategy.upper()} TARGET",
                    subtitle=f"confidence={result.confidence:.3f}"
                ))
        except Exception as exc:
            if not quiet:
                rprint(f"  [red]Auto-suggest failed: {exc}[/red]")
    elif auto_suggest and verdict != "GO" and not quiet:
        console.print(
            "\n[yellow]Auto-suggest skipped — conditions not GO.[/yellow] "
            "Use --no-suggest to suppress this message or run "
            "`lottery suggest` directly to override."
        )

    # ── Export ────────────────────────────────────────────────────────────────
    if export_md:
        _append_md(export_md, rules.name, strategy, today, scores, details, verdict, total, max_score,
                   m_name, m_ratio, kp, delta, stab, cluster_result,
                   js_val=js_val, regime_verdict=regime_verdict)
        if not quiet:
            console.print(f"\n[green]✔ Condition log appended to {export_md}[/green]")

    return verdict


def _append_md(
    path: str,
    game: str,
    strategy: str,
    today: _date,
    scores: dict,
    details: dict,
    verdict: str,
    total: int,
    max_score: int,
    moon_name: str,
    moon_ratio: float,
    kp: float | None,
    delta: float | None,
    stab: float | None,
    cluster_result,
    js_val: float = 0.0,
    regime_verdict: str = "UNKNOWN",
) -> None:
    """Append a dated condition block to the log file (creates file if absent)."""
    import re
    from pathlib import Path as _Path

    p = _Path(path)

    # Build entry
    cluster_id = cluster_result[0] if cluster_result else "n/a"
    entry = f"""
---
## {today} — {game}

```yaml
date: {today}
game: {game}
strategy: {strategy}
verdict: {verdict}
score: {total}/{max_score}
stability: {f"{stab:.2%}" if stab is not None else "n/a"}
cluster: {cluster_id}
moon_phase: "{moon_name}"
moon_ratio: {moon_ratio:.2f}
solar_kp: {kp if kp is not None else "null"}
discrimination_delta: {f"{delta:.4f}" if delta is not None else "null"}
js_divergence: {js_val:.5f}
regime: {regime_verdict}
fairness_p: {details.get("fairness", "").split("p=")[-1].split()[0] if "p=" in details.get("fairness", "") else "null"}
```

| Layer | Signal |
|-------|--------|
"""
    # Strip rich markup for md
    _markup_re = re.compile(r"\[/?[^\]]*\]")
    for layer, detail in details.items():
        clean = _markup_re.sub("", detail)
        entry += f"| {layer.capitalize()} | {clean} |\n"

    entry += f"\n**Verdict: {verdict}** ({total}/{max_score})\n"

    # Prepend frontmatter if new file
    if not p.exists():
        header = (
            "---\n"
            f"type: condition-log\n"
            f"game: {game}\n"
            f"strategy: {strategy}\n"
            "tags: [prediction-engine, condition-log, scan]\n"
            "---\n\n"
            f"# Condition Log: {game}\n"
        )
        p.write_text(header, encoding="utf-8")

    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)
