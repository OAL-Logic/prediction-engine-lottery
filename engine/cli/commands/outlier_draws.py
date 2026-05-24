"""
Outlier Draws Command 🚨
========================
Z-score flagger for structurally anomalous historical draws.

A lottery draw is "structurally anomalous" when one or more of its
fundamental properties (sum, parity ratio, consecutive pairs, spread,
decade coverage) deviates significantly from the historical norm.

This command computes a per-draw composite z-score and flags the
most extreme draws — useful for asking:
  • Are weird draws becoming more frequent?
  • Does the distribution of draw properties drift over time?
  • Should anomalous draws be modelled separately?

Algorithm
---------
For each draw, compute a 5-dim structural vector:
  [sum, parity_ratio, consecutive_count, spread, decade_coverage]

Compute mean and std for each dimension over the full analysis window.
Per-draw z-score for dimension k:
  z_k = (val_k − mean_k) / std_k

Composite score = mean(|z_k|)  — average absolute deviation in σ units.

Draws with composite score ≥ threshold (default 2.0) are flagged.

Output
------
  Outlier table  ranked draws with composite z, individual z per dim
  Timeline bar   sparkline of composite z over time (rising = more weird)
  Summary panel  count flagged, mean/max z, trend

Example
-------
  lottery outlier-draws br/lotofacil
  lottery outlier-draws br/mega-sena --threshold 1.5 --top 20
  lottery outlier-draws br/lotofacil --draws 500 --export-md outliers.md
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, decade_spread as _decade_spread

console = Console()

_DIM_NAMES = ["Sum", "Parity", "Consec", "Spread", "Decade"]

_SPARK = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float], width: int = 40) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span   = hi - lo or 1.0
    sample_step = max(1, len(values) // width)
    sampled     = values[::sample_step][:width]
    return "".join(_SPARK[min(7, int((v - lo) / span * 7))] for v in sampled)


def outlier_draws(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g. br/lotofacil)")],
    threshold: Annotated[float, typer.Option("--threshold", "-t",
        help="Composite z-score threshold for flagging")] = 2.0,
    draws: Annotated[int, typer.Option("--draws", "-n",
        help="Historical draws to analyse")] = 300,
    top: Annotated[int, typer.Option("--top", "-N",
        help="Number of top outliers to display")] = 15,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append outlier report to this .md file")] = None,
) -> None:
    """🚨 Z-score flagger for structurally anomalous historical draws.

    Computes a composite z-score across 5 structural dimensions and flags
    draws that deviate most from the historical norm. Useful for detecting
    structural drift or regime breaks in the draw distribution.

    Example: lottery outlier-draws br/lotofacil
             lottery outlier-draws br/mega-sena --threshold 1.5 --top 20
    """
    adapter  = get_adapter(lottery)
    df       = adapter.fetch()
    rules    = adapter.rules
    lo, hi   = rules.number_range
    n_draws  = min(draws, len(df))
    window   = df.tail(n_draws)
    all_rows = [r for r in window.itertuples() if r.numbers is not None and len(r.numbers) > 0]

    if len(all_rows) < 10:
        console.print("[dim]Not enough draw data.[/dim]")
        raise typer.Exit(0)

    # ── Build feature matrix ────────────────────────────────────────────
    def _features(nums: list[int]) -> list[float]:
        s = sorted(nums)
        return [
            float(sum(s)),
            sum(1 for n in s if n % 2 == 0) / len(s),
            float(sum(1 for a, b in zip(s, s[1:]) if b == a + 1)),
            float(s[-1] - s[0]),
            _decade_spread(s, lo, hi),
        ]

    feats = [_features(list(row.numbers)) for row in all_rows]
    n_dim = len(_DIM_NAMES)

    # Per-dimension mean and std
    means: list[float] = []
    stds:  list[float] = []
    for d in range(n_dim):
        vals = [feats[i][d] for i in range(len(feats))]
        mu   = sum(vals) / len(vals)
        var  = sum((v - mu) ** 2 for v in vals) / len(vals)
        std  = var ** 0.5
        means.append(mu)
        stds.append(std if std > 0 else 1.0)

    # Per-draw z-vectors and composite z
    draw_scores: list[tuple] = []
    for i, row in enumerate(all_rows):
        z_vec   = [(feats[i][d] - means[d]) / stds[d] for d in range(n_dim)]
        comp_z  = sum(abs(z) for z in z_vec) / n_dim
        date_str = str(row.date)[:10] if hasattr(row, "date") and row.date is not None else "—"
        draw_scores.append((row.draw_id, date_str, list(row.numbers), z_vec, comp_z))

    # Sort by composite z descending
    draw_scores.sort(key=lambda x: -x[4])
    flagged = [x for x in draw_scores if x[4] >= threshold]

    # Timeline (original order) for sparkline
    by_order = sorted(draw_scores, key=lambda x: x[0])
    z_vals_ordered = [x[4] for x in by_order]

    # ── Table ─────────────────────────────────────────────────────────────
    tbl = Table(
        title=f"🚨 Outlier Draws — {rules.name}  (window={n_draws}, threshold={threshold}σ)",
        box=None, padding=(0, 1), header_style="bold",
    )
    tbl.add_column("Draw",   justify="right",  style="dim")
    tbl.add_column("Date",   justify="center", style="dim")
    tbl.add_column("CompZ",  justify="right")
    for name in _DIM_NAMES:
        tbl.add_column(f"z({name[:3]})", justify="right", style="dim")
    tbl.add_column("Numbers", justify="left")

    shown = 0
    for draw_id, date_str, nums, z_vec, comp_z in draw_scores[: top]:
        colour = "bold red" if comp_z >= threshold else "yellow" if comp_z >= threshold * 0.7 else "dim"
        nums_str = " ".join(f"{n:2}" for n in sorted(nums)[:8])
        if len(nums) > 8:
            nums_str += " …"
        z_cells = [f"{z:+.1f}" for z in z_vec]
        tbl.add_row(
            str(draw_id),
            date_str,
            f"[{colour}]{comp_z:.2f}σ[/{colour}]",
            *z_cells,
            nums_str,
        )
        shown += 1

    console.print()
    console.print(tbl)

    # ── Sparkline ──────────────────────────────────────────────────────────
    spark = _sparkline(z_vals_ordered)
    console.print(f"\n  [dim]Composite z over time (oldest→newest):  {spark}[/dim]")

    # ── Summary panel ──────────────────────────────────────────────────────
    n_flagged = len(flagged)
    mean_z    = sum(x[4] for x in draw_scores) / len(draw_scores)
    max_z     = draw_scores[0][4]
    max_draw  = draw_scores[0][0]

    # Trend: compare first half vs second half mean z
    half = len(z_vals_ordered) // 2
    first_half_z  = sum(z_vals_ordered[:half]) / half if half else 0.0
    second_half_z = sum(z_vals_ordered[half:]) / (len(z_vals_ordered) - half) if (len(z_vals_ordered) - half) else 0.0
    trend_str = (
        "[red]↑ increasing anomalies[/red]" if second_half_z > first_half_z * 1.1
        else "[green]↓ decreasing anomalies[/green]" if second_half_z < first_half_z * 0.9
        else "[dim]→ stable[/dim]"
    )

    console.print()
    console.print(Panel(
        f"Flagged: [bold red]{n_flagged}[/bold red]/{len(draw_scores)} draws ≥ {threshold}σ  ·  "
        f"Trend: {trend_str}\n"
        f"[dim]Mean composite z: {mean_z:.2f}  ·  Max: {max_z:.2f}σ (draw #{max_draw})\n"
        f"Dims: {', '.join(_DIM_NAMES)}  ·  Window: {n_draws} draws[/dim]",
        title="🚨 Outlier Summary",
        border_style="yellow",
    ))

    if export_md:
        _append_md(
            export_md, lottery, rules.name, _date.today(),
            n_draws, threshold, n_flagged, len(draw_scores), mean_z, max_z, max_draw,
            draw_scores[:top],
        )
        console.print(f"\n[green]✔ Outlier report appended to {export_md}[/green]")


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    n_draws: int, threshold: float, n_flagged: int, total: int,
    mean_z: float, max_z: float, max_draw_id: int,
    top_draws: list,
) -> None:
    rows_md = ""
    for draw_id, date_str, nums, z_vec, comp_z in top_draws:
        nums_str = " ".join(str(n) for n in sorted(nums))
        rows_md += f"| {draw_id} | {date_str} | {comp_z:.2f} | {nums_str} |\n"

    content = f"""
---
type: diagnostic
subtype: outlier-draws
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
draws_window: {n_draws}
threshold: {threshold}
flagged: {n_flagged}
total_draws: {total}
mean_z: {mean_z:.4f}
max_z: {max_z:.4f}
max_z_draw: {max_draw_id}
---

## Outlier Draws: {game_name} ({today.isoformat()})

**Window:** {n_draws}  ·  **Threshold:** {threshold}σ
**Flagged:** {n_flagged}/{total} draws  ·  **Mean z:** {mean_z:.2f}  ·  **Max z:** {max_z:.2f}

| Draw | Date | CompZ | Numbers |
|------|------|-------|---------|
{rows_md}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
