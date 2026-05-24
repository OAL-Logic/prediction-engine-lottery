"""
Leaderboard Command 🏆
=====================
Comparative diagnostic across multiple strategies:

  1. Signal quality  — rolling stability % (from signal analysis)
  2. Discrimination  — Δ confidence real vs random (from stress-test)
  3. Composite rank  — weighted combination of both metrics

This answers the question: "Which strategy is actually detecting structure,
and which is just pattern-matching noise?"

The composite score is:
  score = 0.5 × stability% + 0.5 × clamp(Δ_conf / 0.05, 0, 1)

A high composite score means the strategy is BOTH internally stable AND
responds differently to real vs random data — the two independent signals
that genuine pattern recognition requires.
"""

from __future__ import annotations

from typing import Annotated, Optional
from datetime import date as _date

import typer
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, calculate_shannon_entropy, print_command_summary
from engine.strategies import get_strategy, list_strategies

console = Console()

_STRATEGY_GROUPS = {
    "statistical": ["markov", "bayesian", "weighted", "monte_carlo", "pattern",
                    "momentum", "spectral", "streak", "crowd_avoidance",
                    "cycle", "harmonic", "stability", "fisher", "void"],
    "esoteric":    ["moon_phase", "solar", "noosphere", "numerology",
                    "fibonacci", "kabbalistic", "sefirot", "ley_lines"],
    "deep":        ["transformer", "lstm_gru", "cnn_1d"],
    "default":     ["weighted", "markov", "bayesian", "monte_carlo",
                    "spectral", "cycle", "moon_phase", "noosphere"],
}


def _stability_pct(df, adapter, strategy_name: str, window: int, step: int) -> float | None:
    """Return fraction of rolling windows that are STABLE for this strategy."""
    n = len(df)
    confs = []
    positions = list(range(0, n - window, step))
    if not positions:
        return None

    for pos in positions:
        win_df = df.iloc[pos : pos + window].copy()
        try:
            strat = get_strategy(strategy_name)
            res = strat.suggest(win_df, adapter.rules, count=1, temperature=1.0)
            confs.append(res.confidence)
        except Exception:
            continue

    if len(confs) < 3:
        return None

    conf_arr = np.array(confs)
    rolling_std = [
        float(np.std(conf_arr[max(0, i - 2) : i + 3]))
        for i in range(len(conf_arr))
    ]
    plateau_thr = float(np.percentile(rolling_std, 25))
    return float(sum(s <= plateau_thr for s in rolling_std) / len(rolling_std))


def _stress_delta(df, adapter, strategy_name: str, inject_ratio: float, trials: int) -> float | None:
    """Return (real_conf - avg_random_conf) for this strategy."""
    lo, hi = adapter.rules.number_range
    pick = adapter.rules.pick_count

    try:
        strat = get_strategy(strategy_name)
        real_res = strat.suggest(df, adapter.rules, count=1, temperature=1.0)
        real_conf = real_res.confidence
    except Exception:
        return None

    rand_confs = []
    for _ in range(trials):
        rand_df = df.copy()
        n_inject = max(1, int(len(rand_df) * inject_ratio))
        idx = np.random.choice(len(rand_df), size=n_inject, replace=False)
        nums = rand_df["numbers"].tolist()
        for i in idx:
            nums[i] = sorted(
                np.random.choice(range(lo, hi + 1), size=pick, replace=False).tolist()
            )
        rand_df = rand_df.copy()
        rand_df["numbers"] = nums
        try:
            rs = get_strategy(strategy_name)
            rr = rs.suggest(rand_df, adapter.rules, count=1, temperature=1.0)
            rand_confs.append(rr.confidence)
        except Exception:
            continue

    if not rand_confs:
        return None

    return float(real_conf - np.mean(rand_confs))


def leaderboard(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategies: Annotated[str, typer.Option("--strategies", "-s",
        help="Comma-separated list or group: default | statistical | esoteric | deep")] = "default",
    window: Annotated[int, typer.Option("--limit", "-L",
        help="Rolling window size for stability analysis")] = 50,
    step: Annotated[int, typer.Option("--step",
        help="Step between rolling windows")] = 20,
    inject_ratio: Annotated[float, typer.Option("--inject-ratio",
        help="Fraction of draws to randomise in stress-test")] = 0.5,
    trials: Annotated[int, typer.Option("--trials",
        help="Random injection trials per strategy")] = 3,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Export leaderboard to this .md file")] = None,
    seed: Annotated[Optional[int], typer.Option("--seed",
        help="Random seed for reproducible injection trials")] = None,
) -> None:
    """🏆 Comparative diagnostic leaderboard across multiple strategies.

    Measures two independent quality signals per strategy:
      1. Signal stability %  (rolling window variance analysis)
      2. Discrimination Δ    (real data vs injected random confidence delta)

    Then computes a composite rank. High composite = genuine pattern detector.
    Low composite = noise generator.

    Example: lottery leaderboard br/lotofacil --strategies default
             lottery leaderboard br/lotofacil --strategies weighted,markov,moon_phase
    """

    if seed is not None:
        np.random.seed(seed)

    print_command_summary("leaderboard", lottery,
                          strategies=strategies, window=window, trials=trials)

    # ── Resolve strategy list ─────────────────────────────────────────────────
    if strategies in _STRATEGY_GROUPS:
        names = _STRATEGY_GROUPS[strategies]
    else:
        names = [s.strip() for s in strategies.split(",") if s.strip()]

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    stress_window = min(100, len(df))
    stress_df = df.tail(stress_window)

    console.print(Panel(
        f"[bold cyan]{adapter.rules.name}[/bold cyan]  "
        f"{len(names)} strategies  "
        f"stability-window={window}  stress-trials={trials}\n"
        f"inject-ratio={inject_ratio:.0%}  stress-window last {stress_window} draws",
        title="🏆 Strategy Diagnostic Leaderboard",
    ))

    records = []
    failed  = []

    for name in names:
        console.print(f"  [dim]Analysing[/dim] [cyan]{name}[/cyan]…", end="")

        stab = _stability_pct(df, adapter, name, window, step)
        if stab is None:
            console.print(" [red]skip (insufficient history)[/red]")
            failed.append(name)
            continue

        delta = _stress_delta(stress_df, adapter, name, inject_ratio, trials)
        if delta is None:
            console.print(" [red]skip (stress-test failed)[/red]")
            failed.append(name)
            continue

        # Composite: 50% stability, 50% normalised discrimination
        norm_delta = max(0.0, min(1.0, delta / 0.05))
        composite  = 0.5 * stab + 0.5 * norm_delta

        records.append({
            "name":      name,
            "stability": stab,
            "delta":     delta,
            "composite": composite,
        })
        console.print(f" stability={stab:.0%}  Δ={delta:+.4f}  composite={composite:.3f}")

    if not records:
        console.print("[red]No strategies produced results.[/red]")
        raise typer.Exit(1)

    records.sort(key=lambda r: r["composite"], reverse=True)

    table = Table(title="Leaderboard", header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Rank",       justify="right",  style="dim")
    table.add_column("Strategy",   style="cyan")
    table.add_column("Stability%", justify="right")
    table.add_column("Δ real/rand",justify="right")
    table.add_column("Composite",  justify="right")
    table.add_column("Assessment", justify="center")

    for rank, r in enumerate(records, 1):
        if r["composite"] >= 0.5:
            assessment = "[green]DISCRIMINATES[/green]"
        elif r["delta"] < -0.005:
            assessment = "[red]INVERTED[/red]"
        elif r["stability"] < 0.15:
            assessment = "[yellow]UNSTABLE[/yellow]"
        else:
            assessment = "[dim]NOISE[/dim]"

        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        table.add_row(
            medal,
            r["name"],
            f"{r['stability']:.0%}",
            f"{r['delta']:+.4f}",
            f"{r['composite']:.3f}",
            assessment,
        )

    console.print()
    console.print(table)

    top = records[0]
    console.print(
        f"\n[bold]Top strategy:[/bold] [cyan]{top['name']}[/cyan]  "
        f"composite={top['composite']:.3f}  stability={top['stability']:.0%}  "
        f"Δ={top['delta']:+.4f}"
    )

    discriminators = [r for r in records if r["composite"] >= 0.5]
    if discriminators:
        console.print(
            f"[green]{len(discriminators)} strategies[/green] cross the 0.50 composite threshold "
            f"(genuine discriminators): "
            + ", ".join(r["name"] for r in discriminators)
        )
    else:
        console.print(
            "[yellow]No strategy crosses the 0.50 composite threshold. "
            "All show weak discrimination — consistent with uniform lottery data.[/yellow]"
        )

    if failed:
        console.print(f"\n[dim]Skipped: {', '.join(failed)}[/dim]")

    if export_md:
        _export_md(export_md, adapter.rules.name, strategies, window,
                   inject_ratio, trials, records, failed)
        console.print(f"\n[green]✔ Leaderboard written to {export_md}[/green]")


def _export_md(
    path: str,
    game: str,
    strategies: str,
    window: int,
    inject_ratio: float,
    trials: int,
    records: list[dict],
    failed: list[str],
) -> None:
    rows = ""
    for rank, r in enumerate(records, 1):
        rows += (
            f"| {rank} | {r['name']} | {r['stability']:.0%} | "
            f"{r['delta']:+.4f} | {r['composite']:.3f} |\n"
        )

    content = f"""---
type: pattern-log
game: {game}
strategies: "{strategies}"
window: {window}
inject_ratio: {inject_ratio}
trials: {trials}
date: {_date.today().isoformat()}
top_strategy: {records[0]['name'] if records else 'none'}
top_composite: {records[0]['composite']:.3f if records else 0}
tags: [prediction-engine, leaderboard, diagnostic, pattern-log]
---

# Strategy Diagnostic Leaderboard: {game}

**Strategies:** {strategies} | **Window:** {window} | **Inject ratio:** {inject_ratio:.0%} | **Trials:** {trials}

## Rankings

| Rank | Strategy | Stability% | Δ real/rand | Composite |
|------|----------|-----------|-------------|-----------|
{rows}

## Scoring

- **Stability%** — fraction of rolling windows classified as STABLE (low variance)
- **Δ real/rand** — real data confidence minus injected-random confidence
- **Composite** — `0.5 × stability + 0.5 × clamp(Δ / 0.05, 0, 1)`

Composite ≥ 0.50 → genuine discriminator | < 0.50 → noise-level performance

{"Skipped: " + ", ".join(failed) if failed else ""}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
