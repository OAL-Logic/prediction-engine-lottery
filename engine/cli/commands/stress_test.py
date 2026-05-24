"""
Stress-Test Command ⚡
=====================
Adversarial CLI: inject true randomness into the dataset and test whether
a strategy can tell the difference from real draw history.

If your RL/DL/statistical model gives similar confidence for real data
and shuffled random data, the patterns it detects are likely a hallucination.
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
from engine.strategies import get_strategy

console = Console()


def stress_test(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy name or comma-separated list")] = "weighted",
    inject_ratio: Annotated[float, typer.Option("--inject-ratio", help="Fraction of draws to replace with true random (0.0–1.0)")] = 0.5,
    trials: Annotated[int, typer.Option("--trials", help="Number of random injection trials to average over")] = 5,
    window: Annotated[Optional[int], typer.Option("--limit", "-L", help="Use only the N most recent draws")] = 100,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export adversarial report to this .md file")] = None,
    seed: Annotated[Optional[int], typer.Option("--seed", help="Random seed for reproducible injection trials")] = None,
) -> None:
    """⚡ Adversarial stress-test: inject true randomness and compare strategy response.

    Baseline: run the strategy on real historical draws → measure confidence + entropy.
    Adversarial: replace inject-ratio% of draws with uniformly random draws, repeat
    for `trials` runs, and compare.

    If the strategy cannot distinguish real from random, its patterns may be noise.

    Example: lottery stress-test br/lotofacil --strategy weighted --inject-ratio 0.5 --trials 5
    """

    if seed is not None:
        np.random.seed(seed)

    print_command_summary("stress-test", lottery, strategy=strategy,
                          inject_ratio=inject_ratio, trials=trials, window=window)

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter  = get_adapter(lottery)
        df       = adapter.fetch(limit=window)

    lo, hi  = adapter.rules.number_range
    pick    = adapter.rules.pick_count
    names   = [s.strip() for s in strategy.split(",")]

    console.print(Panel(
        f"[bold cyan]{adapter.rules.name}[/bold cyan]  strategy=[bold]{strategy}[/bold]\n"
        f"inject_ratio=[yellow]{inject_ratio:.0%}[/yellow]  trials={trials}  window={len(df)} draws",
        title="⚡ Adversarial Stress-Test",
    ))

    header = Table(header_style="bold cyan", box=None, padding=(0, 2))
    header.add_column("Strategy",          style="cyan")
    header.add_column("Real conf",         justify="right")
    header.add_column("Random conf",       justify="right")
    header.add_column("Δ conf",            justify="right")
    header.add_column("Real entropy",      justify="right")
    header.add_column("Random entropy",    justify="right")
    header.add_column("Verdict",           justify="center")

    report_rows: list[dict] = []

    for s_name in names:
        # ── Baseline: real data ───────────────────────────────────────────────
        try:
            strat      = get_strategy(s_name)
            real_res   = strat.suggest(df, adapter.rules, count=1, temperature=1.0)
            real_conf  = real_res.confidence
            real_ent   = calculate_shannon_entropy(real_res.scores)
        except Exception as exc:
            console.print(f"[red]{s_name}: baseline failed — {exc}[/red]")
            continue

        # ── Adversarial: inject random draws ─────────────────────────────────
        rand_confs: list[float] = []
        rand_ents:  list[float] = []

        for _ in range(trials):
            rand_df     = df.copy()
            n_inject    = max(1, int(len(rand_df) * inject_ratio))
            inject_idx  = np.random.choice(len(rand_df), size=n_inject, replace=False)

            nums_col = rand_df["numbers"].tolist()
            for idx in inject_idx:
                nums_col[idx] = sorted(
                    np.random.choice(range(lo, hi + 1), size=pick, replace=False).tolist()
                )
            rand_df = rand_df.copy()
            rand_df["numbers"] = nums_col

            try:
                rand_strat = get_strategy(s_name)
                rand_res = strat.suggest(rand_df, adapter.rules, count=1, temperature=1.0)
                rand_confs.append(rand_res.confidence)
                rand_ents.append(calculate_shannon_entropy(rand_res.scores))

            except Exception:
                continue

        if not rand_confs:
            continue

        avg_rand_conf = float(np.mean(rand_confs))
        avg_rand_ent  = float(np.mean(rand_ents))
        delta         = real_conf - avg_rand_conf

        if abs(delta) < 0.005:
            verdict     = "[red]CANNOT DISTINGUISH[/red]"
            verdict_txt = "CANNOT DISTINGUISH"
        elif delta > 0.01:
            verdict     = "[green]REAL > RANDOM ✔[/green]"
            verdict_txt = "REAL > RANDOM"
        elif delta < -0.01:
            verdict     = "[yellow]RANDOM > REAL (!)[/yellow]"
            verdict_txt = "RANDOM > REAL"
        else:
            verdict     = "[dim]MARGINAL[/dim]"
            verdict_txt = "MARGINAL"

        header.add_row(
            s_name,
            f"{real_conf:.4f}",
            f"{avg_rand_conf:.4f}",
            f"{delta:+.4f}",
            f"{real_ent:.4f}",
            f"{avg_rand_ent:.4f}",
            verdict,
        )
        report_rows.append({
            "strategy":    s_name,
            "real_conf":   real_conf,
            "rand_conf":   avg_rand_conf,
            "delta":       delta,
            "real_ent":    real_ent,
            "rand_ent":    avg_rand_ent,
            "verdict":     verdict_txt,
        })

    console.print(header)
    console.print(
        "\n[dim]Verdict guide: "
        "REAL > RANDOM = strategy detects structure in data | "
        "CANNOT DISTINGUISH = patterns may be hallucinated | "
        "RANDOM > REAL = check for inverted logic[/dim]"
    )

    if export_md:
        _export_md(export_md, adapter.rules.name, inject_ratio, trials, window or len(df), report_rows)
        console.print(f"\n[green]✔ Adversarial report written to {export_md}[/green]")


def _export_md(
    path: str,
    game: str,
    inject_ratio: float,
    trials: int,
    window: int,
    rows: list[dict],
) -> None:
    table_rows = "\n".join(
        f"| {r['strategy']} | {r['real_conf']:.4f} | {r['rand_conf']:.4f} | "
        f"{r['delta']:+.4f} | {r['real_ent']:.4f} | {r['rand_ent']:.4f} | {r['verdict']} |"
        for r in rows
    )

    content = f"""---
type: pattern-log
game: {game}
inject_ratio: {inject_ratio}
trials: {trials}
window: {window}
date: {_date.today().isoformat()}
tags: [prediction-engine, stress-test, adversarial, pattern-log]
---

# Adversarial Stress-Test: {game}

**Inject ratio:** {inject_ratio:.0%} of draws replaced with true uniform random
**Trials:** {trials} | **Window:** {window} draws

## Results

| Strategy | Real conf | Random conf | Δ conf | Real entropy | Random entropy | Verdict |
|----------|-----------|-------------|--------|--------------|----------------|---------|
{table_rows}

## Interpretation

| Verdict | Meaning |
|---------|---------|
| REAL > RANDOM | Strategy detects genuine structure. Patterns may be real. |
| CANNOT DISTINGUISH | Strategy responds equally to real and random data. Patterns are likely noise. |
| RANDOM > REAL | Strategy prefers injected random data — investigate for overfitting or inverted logic. |
| MARGINAL | Weak signal. Not conclusive either way. |

> A strategy that cannot distinguish real lottery draws from uniformly random draws
> is not finding patterns — it is finding confirmation of noise.
> Cross-reference these results against the `signal` command's stability windows.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
