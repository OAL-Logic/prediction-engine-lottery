"""
Cold Streak Alert Command 🥶
============================
Cron-safe alert that fires when numbers reach extreme cold streaks.

Exits 0 (ALERT) when at least one pool number has been absent for more
than `threshold` draws. Exits 1 (QUIET) when no number crosses the line.
Exits 2 on error (data unavailable).

This is intentionally minimal — designed for cron jobs or shell pipelines:
  lottery cold-streak-alert br/lotofacil && notify-send "Cold numbers ready!"

For richer output use --verbose; for Obsidian logging use --export-md.

Algorithm
---------
  For each pool number:
    cold_streak = draws since last appearance
    expected_gap = pool_size / pick_count
    alert if cold_streak >= threshold × expected_gap

  Default threshold = 2.5 (2.5× the expected gap = significant overdue)

Output (quiet by default)
------
  ALERT: #7 #14 #22 cold for 12+ draws  (exit 0)
  QUIET: no numbers exceed cold threshold  (exit 1)

Example
-------
  lottery cold-streak-alert br/lotofacil
  lottery cold-streak-alert br/lotofacil --threshold 3.0 --verbose
  lottery cold-streak-alert br/mega-sena --export-md alerts.md
"""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()


def cold_streak_alert(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    threshold: Annotated[float, typer.Option("--threshold", "-t",
        help="Alert when cold_streak ≥ threshold × expected_gap")] = 2.5,
    verbose: Annotated[bool, typer.Option("--verbose", "-v",
        help="Show detailed table of cold numbers")] = False,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append alert report to this .md file")] = None,
) -> None:
    """🥶 Cron-safe alert when pool numbers reach extreme cold streaks."""
    """🥶 Cron-safe alert when pool numbers reach extreme cold streaks.

    Exits 0 (ALERT) if any number is cold beyond threshold × expected gap.
    Exits 1 (QUIET) otherwise. Use with cron or shell pipelines.

    Example: lottery cold-streak-alert br/lotofacil
             lottery cold-streak-alert br/lotofacil --threshold 3.0 --verbose
    """
    try:
        adapter  = get_adapter(lottery)
        df       = adapter.fetch()
        rules    = adapter.rules
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise typer.Exit(2)

    lo, hi    = rules.number_range
    pool      = list(range(lo, hi + 1))
    pool_size = hi - lo + 1
    pick      = rules.pick_count
    all_rows  = list(df.itertuples())
    n_total   = len(all_rows)

    if n_total < 10:
        console.print("[dim]Insufficient data.[/dim]")
        raise typer.Exit(2)

    expected_gap = pool_size / pick
    alert_cutoff = threshold * expected_gap

    alerted: list[dict] = []

    for num in pool:
        # Find last appearance
        last_idx = None
        for i in range(n_total - 1, -1, -1):
            if num in all_rows[i].numbers:
                last_idx = i
                break

        cold_streak = n_total - last_idx - 1 if last_idx is not None else n_total

        if cold_streak >= alert_cutoff:
            alerted.append({
                "num":        num,
                "cold":       cold_streak,
                "expected":   expected_gap,
                "ratio":      cold_streak / expected_gap,
            })

    alerted.sort(key=lambda d: -d["cold"])

    today    = _date.today()
    fired    = len(alerted) > 0

    if fired:
        nums_str = "  ".join(f"#{d['num']} ({d['cold']} draws)" for d in alerted[:8])
        console.print(
            f"[bold red]🥶 ALERT:[/bold red]  {len(alerted)} number(s) cold ≥ "
            f"{threshold:.1f}× expected ({alert_cutoff:.0f} draws)"
        )
        console.print(f"  {nums_str}")

        if verbose:
            tbl = Table(title="Cold Streak Detail", box=None, padding=(0, 1), header_style="bold")
            tbl.add_column("Number",   justify="center", style="bold yellow")
            tbl.add_column("Cold",     justify="right")
            tbl.add_column("Expected", justify="right",  style="dim")
            tbl.add_column("Ratio",    justify="right")
            tbl.add_column("Status",   justify="center")
            for d in alerted:
                r = d["ratio"]
                status = (
                    "[bold red]EXTREME[/bold red]" if r >= threshold * 1.5 else
                    "[red]ALERT[/red]"
                )
                tbl.add_row(
                    str(d["num"]),
                    str(d["cold"]),
                    f"{d['expected']:.1f}",
                    f"{r:.2f}×",
                    status,
                )
            console.print()
            console.print(tbl)
    else:
        console.print(
            f"[dim]🥶 QUIET: no numbers cold ≥ {threshold:.1f}× expected "
            f"({alert_cutoff:.0f} draws). All within normal range.[/dim]"
        )

    if export_md:
        _append_md(
            export_md, lottery, rules.name, today,
            threshold, alert_cutoff, expected_gap, alerted, fired,
        )
        console.print(f"\n[green]✔ Alert report appended to {export_md}[/green]")

    raise typer.Exit(0 if fired else 1)


def _append_md(
    path: str, lottery: str, game_name: str, today: _date,
    threshold: float, alert_cutoff: float, expected_gap: float,
    alerted: list, fired: bool,
) -> None:
    nums_str = ", ".join(f"#{d['num']} ({d['cold']} draws)" for d in alerted[:10]) or "none"
    rows = ""
    for d in alerted[:10]:
        rows += f"| **{d['num']}** | {d['cold']} | {d['expected']:.1f} | {d['ratio']:.2f}× |\n"

    content = f"""
---
type: diagnostic
subtype: cold-streak-alert
date: {today.isoformat()}
game: {lottery}
game_name: {game_name}
threshold: {threshold}
alert_cutoff: {alert_cutoff:.1f}
expected_gap: {expected_gap:.2f}
alert_fired: {str(fired).lower()}
alerted_count: {len(alerted)}
---

## Cold Streak Alert: {game_name} ({today.isoformat()})

**Threshold:** {threshold}×  ·  **Cutoff:** {alert_cutoff:.0f} draws  ·  **Fired:** {fired}
**Alerted:** {nums_str}

| Number | Cold Streak | Expected Gap | Ratio |
|--------|-------------|--------------|-------|
{rows}
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
