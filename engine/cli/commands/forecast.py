"""
Forecast Command 🔮
===================
Weighted ensemble consensus ticket — uses diagnostic composite scores
(stability × discrimination) as strategy weights so poor discriminators
contribute less to the final ticket.

Algorithm
---------
1. For each strategy in the group:
   a. Compute stability% on rolling windows (signal quality)
   b. Compute Δ confidence real vs random (discrimination)
   c. Derive composite weight = 0.5·stability + 0.5·clamp(Δ/0.05, 0, 1)
   d. Run strategy.suggest() → per-number score distribution
2. Aggregate: for each pool number sum(score × weight) across strategies
3. Normalize → consensus probability per number
4. Pick top pick_count by consensus score
5. Report per-number confidence band (across-strategy std-dev)

Output
------
  - Consensus ticket with confidence per number
  - Per-strategy contribution panel
  - Optional --export-md for Obsidian DataviewJS

Example
-------
  lottery forecast br/lotofacil
  lottery forecast br/lotofacil --strategies weighted,bayesian,markov
  lottery forecast br/lotofacil --strategies default --export-md forecast.md
"""

from __future__ import annotations

import json
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary, load_local_config
from engine.strategies import get_strategy

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_TICKET_LOG = _DATA_DIR / "ticket_log.jsonl"

_STRATEGY_GROUPS = {
    "statistical": ["markov", "bayesian", "weighted", "monte_carlo", "pattern",
                    "momentum", "spectral", "streak", "crowd_avoidance",
                    "cycle", "harmonic", "stability", "fisher"],
    "esoteric":    ["moon_phase", "solar", "noosphere", "numerology",
                    "fibonacci", "kabbalistic"],
    "deep":        ["transformer", "lstm_gru", "cnn_1d"],
    "default":     ["weighted", "markov", "bayesian", "monte_carlo",
                    "spectral", "cycle"],
    "fast":        ["bayesian", "weighted", "markov"],
}


def _stability_pct(df, adapter, name: str, window: int, step: int, personal_data: dict = None) -> float:
    n = len(df)
    confs = []
    personal_data = personal_data or {}
    for pos in range(0, n - window, step):
        try:
            s = get_strategy(name, **personal_data)
            r = s.suggest(df.iloc[pos: pos + window].copy(), adapter.rules,
                          count=1, temperature=1.0)
            confs.append(r.confidence)
        except Exception:
            continue
    if len(confs) < 3:
        return 0.3  # pessimistic default
    arr = np.array(confs)
    rolling_std = [float(np.std(arr[max(0, i - 2): i + 3])) for i in range(len(arr))]
    thr = float(np.percentile(rolling_std, 25))
    return float(sum(s <= thr for s in rolling_std) / len(rolling_std))


def _stress_delta(df, adapter, name: str, inject_ratio: float, trials: int, personal_data: dict = None) -> float:
    lo, hi = adapter.rules.number_range
    pick = adapter.rules.pick_count
    personal_data = personal_data or {}
    try:
        s = get_strategy(name, **personal_data)
        real_conf = s.suggest(df, adapter.rules, count=1, temperature=1.0).confidence
    except Exception:
        return 0.0

    rand_confs = []
    for _ in range(trials):
        rand_df = df.copy()
        n_inj = max(1, int(len(rand_df) * inject_ratio))
        idx = np.random.choice(len(rand_df), size=n_inj, replace=False)
        nums = rand_df["numbers"].tolist()
        for i in idx:
            nums[i] = sorted(
                np.random.choice(range(lo, hi + 1), size=pick, replace=False).tolist()
            )
        rand_df = rand_df.copy()
        rand_df["numbers"] = nums
        try:
            rs = get_strategy(name, **personal_data)
            rand_confs.append(rs.suggest(rand_df, adapter.rules, count=1, temperature=1.0).confidence)
        except Exception:
            continue

    return float(real_conf - np.mean(rand_confs)) if rand_confs else 0.0


def _composite_weight(stab: float, delta: float) -> float:
    return 0.5 * stab + 0.5 * max(0.0, min(1.0, delta / 0.05))


def forecast(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Group or comma list: default | statistical | fast | esoteric | <names>")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="History window for each strategy")] = 50,
    step: Annotated[int, typer.Option("--step",
        help="Step between stability windows")] = 20,
    inject_ratio: Annotated[float, typer.Option("--inject-ratio",
        help="Fraction to randomise in stress-test")] = 0.5,
    trials: Annotated[int, typer.Option("--trials",
        help="Randomisation trials per strategy")] = 3,
    temperature: Annotated[float, typer.Option("--temperature",
        help="Suggestion temperature (0=deterministic)")] = 1.0,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append forecast to this .md file")] = None,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet")] = False,
    use_calibration: Annotated[bool, typer.Option("--use-calibration/--no-calibration",
        help="Weight strategies by calibrated empirical lift (from calibration cache)")] = False,
    seed: Annotated[Optional[int], typer.Option("--seed",
        help="Random seed for reproducible random injection trials")] = None,
    config: Annotated[Optional[Path], typer.Option("--config",
        help="YAML config from `lottery tune` — overrides --strategies and injects params")] = None,
) -> None:
    """🔮 Weighted ensemble consensus ticket.

    Scores each strategy by (stability × discrimination), uses those scores
    as weights to aggregate per-number confidence, then selects the top numbers.
    With --use-calibration, weights come from empirical out-of-sample lift scores
    (run 'lottery calibrate' first to populate the cache).

    Example: lottery forecast br/lotofacil
             lottery forecast br/lotofacil --strategies fast --quiet
             lottery forecast br/lotofacil --strategies default --export-md fc.md
    """
    personal_data = load_local_config()

    if seed is not None:
        np.random.seed(seed)

    # ── Config file overrides --strategies and injects per-strategy params ────
    _config_params: dict[str, dict] = {}  # strategy_name → {params, filters}
    if config is not None and Path(config).exists():
        import yaml as _yaml
        with open(config, "r") as _f:
            _raw = _yaml.safe_load(_f)
        # Support both bare list [{name, params}] and {strategies: [...]} wrapper
        _entries: list = (
            _raw if isinstance(_raw, list)
            else _raw.get("strategies", _raw.get("reports", [{}])[0].get("strategies", []))
            if isinstance(_raw, dict) else []
        )
        if _entries:
            strategies = ",".join(e["name"] for e in _entries if "name" in e)
            _config_params = {
                e["name"]: {
                    "params": e.get("params", {}),
                    "filters": e.get("filters", [])
                }
                for e in _entries if "name" in e
            }
            if not quiet:
                console.print(f"[dim]Config loaded: {config}  ({len(_entries)} strategy entries)[/dim]")

    if not quiet:
        print_command_summary("forecast", lottery, strategies=strategies, window=window)

    if strategies in _STRATEGY_GROUPS:
        names = _STRATEGY_GROUPS[strategies]
    else:
        names = [s.strip() for s in strategies.split(",") if s.strip()]

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    lo, hi = adapter.rules.number_range
    pick = adapter.rules.pick_count
    pool_size = hi - lo + 1
    win_df = df.tail(window)

    # Load calibration weights if requested
    cal_weights: dict[str, float] | None = None
    if use_calibration:
        from engine.cli.commands.calibrate import load_calibration_weights
        cal_weights = load_calibration_weights(lottery, names)
        if cal_weights and not quiet:
            console.print(f"[dim]Using calibration weights from cache.[/dim]")
        elif not quiet:
            console.print(f"[yellow]No calibration cache for {lottery}. "
                          f"Run [bold]lottery calibrate {lottery}[/bold] first.[/yellow]")

    # ── Per-strategy diagnostics ──────────────────────────────────────────────
    stress_df = df.tail(min(100, len(df)))
    contributions: list[dict] = []

    if not quiet:
        console.print()

    consensus_scores = np.zeros(pool_size, dtype=float)
    total_weight = 0.0

    per_num_scores: dict[str, np.ndarray] = {}  # for std-dev band

    for name in names:
        if not quiet:
            console.print(f"  [dim]→[/dim] [cyan]{name}[/cyan]", end="  ")

        stab  = _stability_pct(df, adapter, name, window, step, personal_data=personal_data)
        delta = _stress_delta(stress_df, adapter, name, inject_ratio, trials, personal_data=personal_data)
        if cal_weights is not None and name in cal_weights:
            weight = cal_weights[name]  # empirical lift from calibration cache
        else:
            weight = _composite_weight(stab, delta)

        try:
            _conf = _config_params.get(name, {})
            _strat_params = _conf.get("params", {})
            _strat_filters = _conf.get("filters", [])
            
            # Merge personal data
            combined_params = {**_strat_params, **personal_data}
            
            strat = get_strategy(name, **combined_params)
            res = strat.suggest(win_df, adapter.rules, count=1, temperature=temperature, filters=_strat_filters)
            scores = res.scores  # dict[int, float]
        except Exception:
            if not quiet:
                console.print("[red]skip[/red]")
            continue


        # Normalise strategy scores to [0, 1]
        arr = np.zeros(pool_size, dtype=float)
        for num, sc in scores.items():
            if lo <= num <= hi:
                arr[num - lo] = max(0.0, sc)
        arr_sum = arr.sum()
        if arr_sum > 0:
            arr /= arr_sum

        consensus_scores += arr * weight
        total_weight += weight
        per_num_scores[name] = arr

        contributions.append({
            "name": name,
            "stability": stab,
            "delta": delta,
            "weight": weight,
            "confidence": res.confidence,
        })

        if not quiet:
            console.print(
                f"stab={stab:.0%}  Δ={delta:+.4f}  w={weight:.3f}  "
                f"conf={res.confidence:.4f}"
            )

    if total_weight == 0:
        console.print("[red]No strategies produced scores.[/red]")
        raise typer.Exit(1)

    consensus_scores /= total_weight

    # ── Select ticket ─────────────────────────────────────────────────────────
    ranked = sorted(
        range(pool_size),
        key=lambda i: consensus_scores[i],
        reverse=True,
    )
    ticket_indices = sorted(ranked[:pick])
    ticket = [i + lo for i in ticket_indices]

    # Per-number std-dev across strategies (confidence band)
    if len(per_num_scores) > 1:
        stacked = np.stack(list(per_num_scores.values()), axis=0)  # (S, pool)
        band = np.std(stacked, axis=0)
    else:
        band = np.zeros(pool_size)

    # ── Display ───────────────────────────────────────────────────────────────
    if not quiet:
        contrib_table = Table(title="Strategy Contributions", box=None,
                              header_style="bold", padding=(0, 1))
        contrib_table.add_column("Strategy",   style="cyan")
        contrib_table.add_column("Stability%", justify="right")
        contrib_table.add_column("Δ disc",     justify="right")
        contrib_table.add_column("Weight",     justify="right")
        contrib_table.add_column("Confidence", justify="right")
        contributions.sort(key=lambda r: r["weight"], reverse=True)
        for c in contributions:
            contrib_table.add_row(
                c["name"],
                f"{c['stability']:.0%}",
                f"{c['delta']:+.4f}",
                f"{c['weight']:.3f}",
                f"{c['confidence']:.4f}",
            )
        console.print()
        console.print(contrib_table)

    # Ticket table
    ticket_table = Table(title="Consensus Ticket", box=None,
                         header_style="bold cyan", padding=(0, 2))
    ticket_table.add_column("Number",    justify="center", style="bold yellow")
    ticket_table.add_column("Consensus%", justify="right")
    ticket_table.add_column("±σ",        justify="right", style="dim")

    for idx in ticket_indices:
        num = idx + lo
        cs  = consensus_scores[idx]
        sd  = band[idx]
        ticket_table.add_row(str(num), f"{cs:.4f}", f"{sd:.4f}")

    console.print()
    console.print(ticket_table)

    ticket_str = "  ".join(str(n) for n in ticket)
    consensus_total = float(consensus_scores[ticket_indices].sum())

    console.print(Panel(
        f"[bold yellow]{ticket_str}[/bold yellow]\n"
        f"[dim]consensus_mass={consensus_total:.4f}  "
        f"strategies_used={len(contributions)}  "
        f"total_weight={total_weight:.3f}[/dim]",
        title="🔮 Forecast Ticket",
        border_style="yellow",
    ))

    _log_ticket(lottery, ticket, source="forecast", strategies=strategies)

    if export_md:
        _export_md(export_md, lottery, adapter.rules.name, strategies, window,
                   inject_ratio, trials, ticket, consensus_scores, band,
                   ticket_indices, lo, contributions, total_weight)
        console.print(f"[green]✔ Forecast appended to {export_md}[/green]")


def _log_ticket(lottery: str, ticket: list[int], *, source: str = "forecast", **meta) -> None:
    """Silently append generated ticket to data/ticket_log.jsonl."""
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "date": _date.today().isoformat(),
            "game": lottery,
            "ticket": ticket,
            "source": source,
            **{k: v for k, v in meta.items() if v is not None},
        }
        with open(_TICKET_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def _export_md(
    path: str,
    lottery: str,
    game_name: str,
    strategies: str,
    window: int,
    inject_ratio: float,
    trials: int,
    ticket: list[int],
    consensus_scores: np.ndarray,
    band: np.ndarray,
    ticket_indices: list[int],
    lo: int,
    contributions: list[dict],
    total_weight: float,
) -> None:
    today = _date.today().isoformat()
    ticket_str = ", ".join(str(n) for n in ticket)
    consensus_total = float(consensus_scores[ticket_indices].sum())

    rows = ""
    for idx in ticket_indices:
        rows += f"| {idx + lo} | {consensus_scores[idx]:.4f} | {band[idx]:.4f} |\n"

    contrib_rows = ""
    for c in sorted(contributions, key=lambda r: r["weight"], reverse=True):
        contrib_rows += (
            f"| {c['name']} | {c['stability']:.0%} | "
            f"{c['delta']:+.4f} | {c['weight']:.3f} | {c['confidence']:.4f} |\n"
        )

    content = f"""---
type: pattern-log
subtype: forecast
game: "{game_name}"
lottery: "{lottery}"
strategies: "{strategies}"
window: {window}
inject_ratio: {inject_ratio}
trials: {trials}
date: {today}
ticket: [{ticket_str}]
consensus_mass: {consensus_total:.4f}
strategies_used: {len(contributions)}
total_weight: {total_weight:.3f}
tags: [prediction-engine, forecast, consensus, pattern-log]
---

# Forecast: {game_name} — {today}

**Strategies:** {strategies} | **Window:** {window} | **Total weight:** {total_weight:.3f}

## Consensus Ticket

**`{ticket_str}`**

| Number | Consensus% | ±σ |
|--------|-----------|-----|
{rows}

## Strategy Contributions

| Strategy | Stability% | Δ disc | Weight | Confidence |
|----------|-----------|--------|--------|-----------|
{contrib_rows}

---
*consensus_mass={consensus_total:.4f} — higher = more concentrated agreement*
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
