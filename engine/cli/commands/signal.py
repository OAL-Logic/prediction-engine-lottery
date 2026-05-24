"""
Signal Command 📡
================
Signal-to-Noise rolling window stability dashboard.

Runs a strategy across rolling historical windows and measures confidence stability.
Stable windows (low variance, plateau) indicate detectable structure.
Oscillating windows indicate noise dominance.
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

_SPARK = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    min_v, max_v = min(values), max(values)
    rng = max_v - min_v or 1.0
    return "".join(_SPARK[int((v - min_v) / rng * 7)] for v in values)


def signal(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Strategy name")] = "weighted",
    window: Annotated[int, typer.Option("--limit", "-L", help="Rolling window size in draws")] = 50,
    step: Annotated[int, typer.Option("--step", help="Step between windows")] = 10,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export pattern log to this .md file")] = None,
) -> None:
    """📡 Signal-to-Noise rolling window stability analysis.

    Runs the strategy across overlapping historical windows and tracks
    confidence and score entropy over time. Stable plateaus = detectable
    structure. Wild oscillations = noise dominance.

    Example: lottery signal br/lotofacil --strategy weighted --window 50
    """
    print_command_summary("signal", lottery, strategy=strategy, window=window, step=step)

    with console.status(f"[bold green]Loading {lottery} data…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    n = len(df)
    if n < window + step:
        console.print(f"[red]Need at least {window + step} draws. Got {n}.[/red]")
        raise typer.Exit(1)

    confidences: list[float] = []
    entropies: list[float] = []
    labels: list[str] = []

    positions = list(range(0, n - window, step))
    with console.status(f"[bold cyan]Running {len(positions)} windows for '{strategy}'…"):
        for pos in positions:
            win_df = df.iloc[pos : pos + window].copy()
            label = f"#{int(win_df.iloc[-1]['draw_id'])}"
            try:
                strat = get_strategy(strategy)
                res = strat.suggest(win_df, adapter.rules, count=1, temperature=1.0)
                confidences.append(res.confidence)
                entropies.append(calculate_shannon_entropy(res.scores))
                labels.append(label)
            except Exception:
                continue

    if not confidences:
        console.print("[red]No results generated — strategy may require more history.[/red]")
        raise typer.Exit(1)

    conf_arr = np.array(confidences)
    ent_arr = np.array(entropies)

    # Plateau detection: rolling std over ±2 neighbours
    rolling_std = [
        float(np.std(conf_arr[max(0, i - 2) : i + 3]))
        for i in range(len(conf_arr))
    ]
    plateau_threshold = float(np.percentile(rolling_std, 25))

    # ── Display ──────────────────────────────────────────────────────────────
    console.print(Panel(
        f"[bold cyan]{adapter.rules.name}[/bold cyan]  strategy=[bold]{strategy}[/bold]  "
        f"window={window} draws  step={step}  snapshots={len(labels)}",
        title="📡 Signal-to-Noise Dashboard",
    ))

    conf_spark = _sparkline(confidences)
    ent_spark  = _sparkline(entropies)

    console.print(f"\n[bold]Confidence:[/bold] {conf_spark}")
    console.print(
        f"  [dim]min={min(confidences):.3f}  max={max(confidences):.3f}  "
        f"mean={float(conf_arr.mean()):.3f}  σ={float(conf_arr.std()):.4f}[/dim]"
    )
    console.print(f"\n[bold]Entropy:   [/bold] {ent_spark}")
    console.print(
        f"  [dim]min={min(entropies):.3f}  max={max(entropies):.3f}  "
        f"mean={float(ent_arr.mean()):.3f}[/dim]"
    )

    table = Table(title="Rolling Window Details", header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Window end", style="dim")
    table.add_column("Confidence", justify="right")
    table.add_column("Entropy",    justify="right")
    table.add_column("Signal",     justify="center")

    for lbl, conf, ent, std_v in zip(labels, confidences, entropies, rolling_std):
        sig = "[green]STABLE[/green]" if std_v <= plateau_threshold else "[yellow]NOISE[/yellow]"
        table.add_row(lbl, f"{conf:.4f}", f"{ent:.4f}", sig)

    console.print(table)

    stable_count = sum(1 for s in rolling_std if s <= plateau_threshold)
    peak_idx = int(np.argmax(confidences))
    low_ent_idx = int(np.argmin(entropies))

    console.print(
        f"\n[bold]Stability score:[/bold] {stable_count}/{len(labels)} windows stable "
        f"({stable_count / len(labels) * 100:.0f}%)"
    )
    console.print(f"[bold]Peak confidence:[/bold] {confidences[peak_idx]:.4f} at {labels[peak_idx]}")
    console.print(
        f"[bold]Lowest entropy: [/bold] {entropies[low_ent_idx]:.4f} at {labels[low_ent_idx]} "
        f"[dim](most concentrated scoring)[/dim]"
    )

    if export_md:
        _export_md(export_md, adapter.rules.name, strategy, window, step,
                   labels, confidences, entropies, rolling_std, plateau_threshold)
        console.print(f"\n[green]✔ Pattern log written to {export_md}[/green]")


def _export_md(
    path: str,
    game: str,
    strategy: str,
    window: int,
    step: int,
    labels: list[str],
    confidences: list[float],
    entropies: list[float],
    rolling_std: list[float],
    plateau_threshold: float,
) -> None:
    stable_count = sum(1 for s in rolling_std if s <= plateau_threshold)
    mean_conf = float(sum(confidences) / len(confidences))
    mean_ent  = float(sum(entropies) / len(entropies))

    rows = "\n".join(
        f"| {lbl} | {conf:.4f} | {ent:.4f} | {'stable' if s <= plateau_threshold else 'noise'} |"
        for lbl, conf, ent, s in zip(labels, confidences, entropies, rolling_std)
    )

    content = f"""---
type: pattern-log
game: {game}
strategy: {strategy}
window: {window}
step: {step}
date: {_date.today().isoformat()}
stability_score: {stable_count / len(labels):.2%}
mean_confidence: {mean_conf:.4f}
mean_entropy: {mean_ent:.4f}
tags: [prediction-engine, signal-noise, pattern-log]
---

# Signal-to-Noise Log: {game} / {strategy}

## Sparklines

**Confidence:** `{_sparkline(confidences)}`

**Entropy:**    `{_sparkline(entropies)}`

## Rolling Window Data

| Window End | Confidence | Entropy | Signal |
|-----------|-----------|---------|--------|
{rows}

## Summary

- **Stability score:** {stable_count}/{len(labels)} windows stable ({stable_count / len(labels):.0%})
- **Strategy:** {strategy}
- **Window size:** {window} draws | Step: {step}
- **Mean confidence:** {mean_conf:.4f}
- **Mean entropy:** {mean_ent:.4f}

> Cross-reference stable windows with esoteric markers using DataviewJS to test alignment.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
