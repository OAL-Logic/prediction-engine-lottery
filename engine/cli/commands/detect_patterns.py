"""
Detect-Patterns Command 🔭
==========================
Esoteric Overlay: cross-correlate statistical stability windows with
esoteric cycle markers (lunar phase, solar K-index, cyclical tensors).

The core question: do periods of low noise (STABLE windows in `lottery signal`)
cluster around specific esoteric marker values? If yes, you have found a
High-Probability Node — a point where traditional math and esoteric theory agree.

Supported overlays
------------------
  cyclical  — lunar cycle progress as 5 continuous quintile buckets (0–20%, …, 80–100%)
  lunar     — 8 discrete moon phases (New Moon, Full Moon, etc.)
  solar     — NOAA K-index bucket (quiet / unsettled / storm)
  all       — run all available overlays and report each

Statistics used
---------------
- For each esoteric bucket: stable_pct vs baseline_pct
- Chi-squared test of independence (bucket × stable/noise)
- Correlation coefficient (point-biserial for binary stable label vs continuous marker)
- Effect size flagged as HIGH-PROBABILITY-NODE when abs(Δ%) >= threshold
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, calculate_shannon_entropy, print_command_summary
from engine.strategies import get_strategy
from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name

console = Console()

_SPARK = "▁▂▃▄▅▆▇█"
_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    min_v, max_v = min(values), max(values)
    rng = max_v - min_v or 1.0
    return "".join(_SPARK[int((v - min_v) / rng * 7)] for v in values)


def _rolling_stability(df, adapter, strategy_name: str, window: int, step: int):
    """Return list of (draw_id, draw_date, confidence, entropy, rolling_std) per snapshot."""
    n = len(df)
    snapshots = []
    raw_confs = []

    positions = list(range(0, n - window, step))
    for pos in positions:
        win_df = df.iloc[pos : pos + window].copy()
        tail_row = win_df.iloc[-1]
        draw_id = int(tail_row["draw_id"])
        d = tail_row.get("date")
        try:
            import pandas as pd
            if pd.isna(d):
                d = None
            elif hasattr(d, "date"):
                d = d.date()
        except Exception:
            d = None

        try:
            strat = get_strategy(strategy_name)
            res = strat.suggest(win_df, adapter.rules, count=1, temperature=1.0)
            conf = res.confidence
            ent = calculate_shannon_entropy(res.scores)
            snapshots.append({"draw_id": draw_id, "date": d, "conf": conf, "entropy": ent})
            raw_confs.append(conf)
        except Exception:
            continue

    if not snapshots:
        return []

    conf_arr = np.array([s["conf"] for s in snapshots])
    for i, s in enumerate(snapshots):
        s["rolling_std"] = float(np.std(conf_arr[max(0, i - 2) : i + 3]))

    plateau_threshold = float(np.percentile([s["rolling_std"] for s in snapshots], 25))
    for s in snapshots:
        s["stable"] = s["rolling_std"] <= plateau_threshold

    return snapshots


# ── Lunar cycle markers ───────────────────────────────────────────────────────

def _lunar_quintile(d: _date | None) -> str | None:
    if d is None:
        return None
    ratio = moon_phase_ratio(d)   # 0.0 → 1.0
    bucket = int(ratio * 5)       # 0–4
    bucket = min(bucket, 4)
    labels = ["Q1 (0–20%)", "Q2 (20–40%)", "Q3 (40–60%)", "Q4 (60–80%)", "Q5 (80–100%)"]
    return labels[bucket]


def _lunar_phase_name(d: _date | None) -> str | None:
    if d is None:
        return None
    return phase_name(d)


# ── Solar K-index marker ──────────────────────────────────────────────────────

def _load_solar_cache() -> dict[str, float]:
    path = _DATA_DIR / "solar_k_index.json"
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def _solar_bucket(d: _date | None, cache: dict[str, float]) -> str | None:
    if d is None:
        return None
    key = d.isoformat()
    kp = cache.get(key)
    if kp is None:
        return None
    if kp < 3:
        return "quiet (Kp<3)"
    if kp < 5:
        return "unsettled (Kp 3–5)"
    return "storm (Kp≥5)"


# ── Correlation analysis ──────────────────────────────────────────────────────

def _analyze_overlay(snapshots: list[dict], label_fn, overlay_name: str, threshold: float) -> dict:
    """
    Group snapshots by esoteric marker value, compute stable% per bucket,
    compare vs baseline, and flag High-Probability Nodes.
    """
    labeled = [(s, label_fn(s["date"])) for s in snapshots]
    labeled = [(s, lbl) for s, lbl in labeled if lbl is not None]

    if len(labeled) < 5:
        return {"overlay": overlay_name, "skipped": True, "reason": "insufficient dated draws"}

    baseline_stable = sum(1 for s, _ in labeled if s["stable"]) / len(labeled)

    buckets: dict[str, list[bool]] = defaultdict(list)
    for s, lbl in labeled:
        buckets[lbl].append(s["stable"])

    rows = []
    nodes = []
    for bucket, stabilities in sorted(buckets.items()):
        n = len(stabilities)
        stable_pct = sum(stabilities) / n
        delta = stable_pct - baseline_stable
        is_node = abs(delta) >= threshold

        rows.append({
            "bucket": bucket,
            "n": n,
            "stable_pct": stable_pct,
            "delta": delta,
            "is_node": is_node,
        })
        if is_node:
            nodes.append({"bucket": bucket, "stable_pct": stable_pct, "delta": delta, "n": n})

    # Chi-squared test (stable vs bucket)
    try:
        from scipy import stats as _scipy_stats
        stable_counts = np.array([sum(v for v in b) for b in buckets.values()])
        noise_counts  = np.array([len(b) - sum(v for v in b) for b in buckets.values()])
        contingency   = np.column_stack([stable_counts, noise_counts])
        chi2, p_val, _, _ = _scipy_stats.chi2_contingency(contingency)
    except Exception:
        chi2, p_val = None, None

    return {
        "overlay":          overlay_name,
        "skipped":          False,
        "baseline_stable":  baseline_stable,
        "n_total":          len(labeled),
        "rows":             rows,
        "nodes":            nodes,
        "chi2":             chi2,
        "p_value":          p_val,
    }


# ── Main command ──────────────────────────────────────────────────────────────

def detect_patterns(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    esoteric: Annotated[str, typer.Option("--esoteric", "-e",
        help="Overlay type: cyclical | lunar | solar | all")] = "cyclical",
    strategy: Annotated[str, typer.Option("--strategy", "-s",
        help="Strategy whose stability windows are analysed")] = "weighted",
    threshold: Annotated[float, typer.Option("--threshold", "-t",
        help="Minimum |Δ stable%| vs baseline to flag a High-Probability Node")] = 0.15,
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Rolling window size in draws")] = 50,
    step: Annotated[int, typer.Option("--step",
        help="Step between windows")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Export pattern log to this .md file")] = None,
) -> None:
    """🔭 Esoteric Overlay: detect if esoteric cycle markers correlate with stable signal windows.

    Runs rolling stability analysis (like `lottery signal`) then cross-references
    each window's draw date with lunar phase, solar K-index, and other esoteric
    markers. Buckets with stable% significantly above baseline are flagged as
    High-Probability Nodes.

    Example: lottery detect-patterns br/lotofacil --esoteric cyclical --threshold 0.15
    """
    print_command_summary("detect-patterns", lottery,
                          esoteric=esoteric, strategy=strategy,
                          threshold=threshold, window=window)

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    n = len(df)
    if n < window + step:
        console.print(f"[red]Need at least {window + step} draws. Got {n}.[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold cyan]{adapter.rules.name}[/bold cyan]  "
        f"strategy=[bold]{strategy}[/bold]  esoteric=[bold]{esoteric}[/bold]\n"
        f"window={window}  step={step}  threshold=±{threshold:.0%}",
        title="🔭 Esoteric Pattern Detector",
    ))

    with console.status(f"[bold cyan]Computing {(n - window) // step} stability snapshots…"):
        snapshots = _rolling_stability(df, adapter, strategy, window, step)

    if not snapshots:
        console.print("[red]No snapshots produced — strategy may need more history.[/red]")
        raise typer.Exit(1)

    baseline = sum(1 for s in snapshots if s["stable"]) / len(snapshots)
    console.print(
        f"\n[bold]Baseline stability:[/bold] {len(snapshots)} windows  "
        f"→ {sum(s['stable'] for s in snapshots)} stable "
        f"({baseline:.0%})\n"
    )

    # ── Resolve overlays ──────────────────────────────────────────────────────
    solar_cache = _load_solar_cache()

    overlay_fns: list[tuple[str, object]] = []
    if esoteric in ("cyclical", "all"):
        overlay_fns.append(("Lunar Cycle Quintile", _lunar_quintile))
    if esoteric in ("lunar", "all"):
        overlay_fns.append(("Moon Phase", _lunar_phase_name))
    if esoteric in ("solar", "all"):
        overlay_fns.append(("Solar K-Index", lambda d: _solar_bucket(d, solar_cache)))
    if not overlay_fns:
        console.print(f"[red]Unknown --esoteric '{esoteric}'. Choose: cyclical | lunar | solar | all[/red]")
        raise typer.Exit(1)

    all_results = []
    all_nodes = []

    for overlay_name, label_fn in overlay_fns:
        result = _analyze_overlay(snapshots, label_fn, overlay_name, threshold)
        all_results.append(result)

        if result.get("skipped"):
            console.print(f"[yellow]⚠ {overlay_name}: {result['reason']}[/yellow]")
            continue

        # ── Print overlay table ───────────────────────────────────────────────
        console.rule(f"[bold cyan]{overlay_name}[/bold cyan]")

        if result["chi2"] is not None:
            sig = "[red]SIGNIFICANT[/red]" if result["p_value"] < 0.05 else "[dim]not significant[/dim]"
            console.print(
                f"  Chi-squared independence test: χ²={result['chi2']:.2f}  "
                f"p={result['p_value']:.4f}  → {sig}"
            )

        table = Table(header_style="bold cyan", box=None, padding=(0, 2))
        table.add_column(overlay_name,   style="cyan")
        table.add_column("n",            justify="right")
        table.add_column("Stable%",      justify="right")
        table.add_column("Δ vs baseline",justify="right")
        table.add_column("Signal",       justify="center")

        for row in result["rows"]:
            delta_str = f"{row['delta']:+.0%}"
            if row["is_node"] and row["delta"] > 0:
                signal_str = "[bold green]HIGH-PROB NODE ↑[/bold green]"
            elif row["is_node"] and row["delta"] < 0:
                signal_str = "[bold red]LOW-PROB ZONE ↓[/bold red]"
            else:
                signal_str = "[dim]—[/dim]"

            table.add_row(
                row["bucket"],
                str(row["n"]),
                f"{row['stable_pct']:.0%}",
                delta_str,
                signal_str,
            )

        console.print(table)

        if result["nodes"]:
            for node in result["nodes"]:
                direction = "↑ above" if node["delta"] > 0 else "↓ below"
                console.print(
                    f"\n  [bold green]★ High-Probability Node:[/bold green] "
                    f"[cyan]{node['bucket']}[/cyan]  "
                    f"stable={node['stable_pct']:.0%}  "
                    f"({node['delta']:+.0%} {direction} baseline)  n={node['n']}"
                )
                all_nodes.append({"overlay": overlay_name, **node})
        else:
            console.print(
                f"\n  [dim]No High-Probability Nodes found at threshold ±{threshold:.0%}. "
                f"Try --threshold 0.10 for a looser search.[/dim]"
            )

    # ── Summary ───────────────────────────────────────────────────────────────
    if all_nodes:
        console.print()
        console.rule("[bold magenta]CONVERGENCE SUMMARY — High-Probability Nodes[/bold magenta]")
        for node in all_nodes:
            console.print(
                f"  [magenta]{node['overlay']}[/magenta] → "
                f"[bold]{node['bucket']}[/bold]  "
                f"stable={node['stable_pct']:.0%}  Δ={node['delta']:+.0%}  n={node['n']}"
            )
        console.print(
            "\n  [dim]These windows show above-baseline predictive stability "
            "correlated with the esoteric marker. Cross-reference with your "
            "esoteric framework before acting on them.[/dim]"
        )
    else:
        console.print(
            "\n[yellow]No nodes found across all overlays. "
            "The esoteric markers tested show no significant correlation with "
            "strategy stability at this threshold.[/yellow]"
        )

    if export_md:
        _export_md(export_md, adapter.rules.name, strategy, esoteric,
                   threshold, window, step, baseline, all_results, all_nodes)
        console.print(f"\n[green]✔ Pattern log written to {export_md}[/green]")


# ── Markdown export ───────────────────────────────────────────────────────────

def _export_md(
    path: str,
    game: str,
    strategy: str,
    esoteric: str,
    threshold: float,
    window: int,
    step: int,
    baseline: float,
    results: list[dict],
    nodes: list[dict],
) -> None:
    node_rows = ""
    for node in nodes:
        node_rows += (
            f"| {node['overlay']} | {node['bucket']} | {node['stable_pct']:.0%} | "
            f"{node['delta']:+.0%} | {node['n']} |\n"
        )

    overlay_sections = ""
    for res in results:
        if res.get("skipped"):
            continue
        p_str = f"p={res['p_value']:.4f}" if res["p_value"] is not None else "n/a"
        rows_md = ""
        for row in res["rows"]:
            flag = " ★" if row["is_node"] else ""
            rows_md += f"| {row['bucket']} | {row['n']} | {row['stable_pct']:.0%} | {row['delta']:+.0%} |{flag}\n"
        overlay_sections += f"""
### {res['overlay']}

Chi-squared: χ²={res['chi2']:.2f if res['chi2'] else 'n/a'}  {p_str}  |  n={res['n_total']}

| Bucket | n | Stable% | Δ baseline |
|--------|---|---------|------------|
{rows_md}
"""

    content = f"""---
type: pattern-log
game: {game}
strategy: {strategy}
esoteric: {esoteric}
threshold: {threshold}
window: {window}
step: {step}
date: {_date.today().isoformat()}
baseline_stability: {baseline:.2%}
high_probability_nodes: {len(nodes)}
tags: [prediction-engine, esoteric-overlay, pattern-log, detect-patterns]
---

# Esoteric Pattern Detection: {game}

**Strategy:** {strategy} | **Esoteric overlay:** {esoteric}
**Threshold:** ±{threshold:.0%} | **Window:** {window} draws | **Step:** {step}
**Baseline stability:** {baseline:.0%}

## High-Probability Nodes

{"No nodes found at this threshold." if not nodes else ""}
{"| Overlay | Bucket | Stable% | Δ baseline | n |" if nodes else ""}
{"|---------|--------|---------|------------|---|" if nodes else ""}
{node_rows}

{overlay_sections}

## Methodology

1. Rolling window analysis (window={window}, step={step}) labels each snapshot STABLE or NOISE
2. Each snapshot's draw date is tagged with esoteric marker values
3. Stable% per bucket is compared to baseline; |Δ| ≥ {threshold:.0%} → High-Probability Node
4. Chi-squared test checks independence between marker and stability

> A High-Probability Node is NOT a guarantee. It is a hypothesis: a period where
> traditional statistical patterns and esoteric cycle theory appear to align.
> Track these nodes over time with DataviewJS to validate or falsify the signal.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
